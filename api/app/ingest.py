"""Ingest Open Library dumps into our own Works and Editions (SCRUM-4).

    python -m app.ingest AUTHORS.txt WORKS.txt EDITIONS.txt

One command loads any number of dump files. Each line is dispatched by its Open
Library type, so the same command handles author, work and edition dumps — pass
authors before works so a work can resolve its author's name. Files may be plain
text or gzipped (``.gz``).

The orchestration here is deliberately free of any database import: it drives an
abstract :class:`Store`, so the resume, batching, idempotency and error-reporting
logic is unit-testable with an in-memory fake. The concrete SQLAlchemy binding
lives in ``app.ingest_store`` and is imported lazily by :func:`main`.

How each acceptance criterion is met:

* **Single command** — :func:`main` loads every file passed to it.
* **Idempotent** — records carry deterministic ids derived from their Open Library
  key, and the store upserts, so a re-run overwrites in place with no duplicates.
* **Resumable** — a per-file checkpoint of the last committed line is stored in the
  same transaction as the batch; a re-run skips lines at or before it.
* **Work/Edition preserved** — works and editions are stored as distinct records,
  the edition carrying its own identifiers and format and pointing at its work.
* **Observable** — progress and running counts are logged as the job runs.
* **Never silently dropped** — a record that fails to parse is counted and reported.
"""

from __future__ import annotations

import gzip
import os
import sys
from dataclasses import dataclass
from typing import Callable, Iterable, Protocol

from . import openlibrary as ol
from .openlibrary import MalformedRecord


class Store(Protocol):
    """The persistence operations the ingest needs, kept minimal and upsert-based.

    Every ``upsert_*`` is keyed by the record's deterministic id, which is what
    makes a re-run idempotent. The checkpoint methods make a run resumable.
    """

    def get_checkpoint(self, source: str) -> int: ...
    def set_checkpoint(self, source: str, line_no: int) -> None: ...
    def upsert_author(self, author_id: str, name: str) -> None: ...
    def upsert_work(self, work_id: str, title: str, author: str, slug: str) -> None: ...
    def upsert_edition(
        self,
        edition_id: str,
        work_id: str,
        fmt: str,
        isbn_10: str | None,
        isbn_13: str | None,
    ) -> None: ...
    def get_author_name(self, author_id: str) -> str | None: ...
    def commit(self) -> None: ...


UNKNOWN_AUTHOR = "Unknown author"


@dataclass
class Stats:
    """Running tally for one file, reported as the job goes and at the end."""

    stored: int = 0
    skipped: int = 0
    failed: int = 0

    def __add__(self, other: "Stats") -> "Stats":
        return Stats(
            stored=self.stored + other.stored,
            skipped=self.skipped + other.skipped,
            failed=self.failed + other.failed,
        )

    def __str__(self) -> str:
        return (
            f"{self.stored} stored, {self.skipped} skipped, {self.failed} failed"
        )


def _resolve_author(store: Store, work: ol.ParsedWork) -> str:
    """Join the names of every author we already ingested for this work.

    Falls back to a placeholder when none resolve — a work whose author dump has
    not been loaded yet still renders, rather than violating the not-null column.
    """
    names = [
        name
        for name in (store.get_author_name(aid) for aid in work.author_ids)
        if name
    ]
    return ", ".join(names) if names else UNKNOWN_AUTHOR


def apply_record(store: Store, record: ol.DumpRecord) -> str | None:
    """Persist one record. Returns ``None`` when stored, or a reason when skipped.

    Raises :class:`MalformedRecord` when the record is too broken to store; the
    caller counts and reports it.
    """
    if record.type == ol.TYPE_AUTHOR:
        author = ol.parse_author(record)
        store.upsert_author(author.id, author.name)
        return None
    if record.type == ol.TYPE_WORK:
        work = ol.parse_work(record)
        store.upsert_work(work.id, work.title, _resolve_author(store, work), work.slug)
        return None
    if record.type == ol.TYPE_EDITION:
        edition = ol.parse_edition(record)
        if edition.work_id is None:
            # Our schema requires an Edition to belong to a Work (ADR-0002); an
            # edition with no work reference is valid Open Library data we cannot
            # place, so we skip and report rather than store an orphan.
            return "edition has no work reference"
        store.upsert_edition(
            edition.id,
            edition.work_id,
            edition.format,
            edition.isbn_10,
            edition.isbn_13,
        )
        return None
    return f"unhandled record type {record.type}"


def run_ingest(
    store: Store,
    source: str,
    lines: Iterable[str],
    log: Callable[[str], None] = print,
    batch_size: int = 1000,
    progress_every: int = 10000,
) -> Stats:
    """Ingest one dump's ``lines`` into ``store``, resuming and committing in batches.

    ``source`` names the file for checkpointing. Lines at or before the stored
    checkpoint are skipped so an interrupted run resumes instead of restarting.
    """
    start_line = store.get_checkpoint(source)
    if start_line:
        log(f"[{source}] resuming after line {start_line}")
    stats = Stats()
    line_no = 0
    for line_no, line in enumerate(lines, start=1):
        if line_no <= start_line:
            continue
        if not line.strip():
            continue
        try:
            record = ol.parse_dump_line(line)
            reason = apply_record(store, record)
        except MalformedRecord as exc:
            stats.failed += 1
            log(f"[{source}] line {line_no}: skipped unparseable record — {exc}")
            continue
        if reason is None:
            stats.stored += 1
        else:
            stats.skipped += 1
            log(f"[{source}] line {line_no}: skipped — {reason}")
        if line_no % batch_size == 0:
            store.set_checkpoint(source, line_no)
            store.commit()
        if line_no % progress_every == 0:
            log(f"[{source}] {line_no} lines — {stats}")
    # Final checkpoint + commit for the trailing partial batch.
    store.set_checkpoint(source, line_no)
    store.commit()
    log(f"[{source}] done: {line_no} lines — {stats}")
    return stats


def _usage() -> str:
    return "usage: python -m app.ingest DUMP_FILE [DUMP_FILE ...]"


def main(argv: list[str]) -> int:
    if not argv:
        print(_usage(), file=sys.stderr)
        return 2

    # Imported here, not at module top, so the pure orchestration above (and its
    # tests) never require SQLAlchemy to be installed.
    from .ingest_store import SqlAlchemyStore, create_schema

    create_schema()
    total = Stats()
    for path in argv:
        opener = gzip.open if path.endswith(".gz") else open
        source = os.path.basename(path)
        with opener(path, "rt", encoding="utf-8", errors="replace") as handle:
            with SqlAlchemyStore() as store:
                total += run_ingest(store, source, handle)
    print(f"ingest complete: {total}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
