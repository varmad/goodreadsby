"""Parsing Open Library bulk dumps — pure, stdlib-only, no database.

Per ADR-0001 Open Library is our only catalogue source. Its monthly bulk dumps
are tab-separated files whose columns are::

    type  key  revision  last_modified  json

The last column is the record itself as JSON. This module turns one physical line
into a typed record and extracts the few fields our schema needs, preserving Open
Library's Work/Edition split (see ADR-0002). It imports only the standard library
so the whole parse layer is unit-testable without SQLAlchemy or Postgres in the
loop — the ingest orchestration (``app.ingest``) and its database binding
(``app.ingest_store``) sit on top of it.

A record that cannot be parsed raises :class:`MalformedRecord`; the ingest catches
it, counts it, and reports it, so a bad line is skipped and surfaced rather than
silently dropped (SCRUM-4).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field


class MalformedRecord(ValueError):
    """A dump line or record that cannot be parsed into what our schema needs."""


# Open Library type keys we understand. Anything else is a record we don't store.
TYPE_AUTHOR = "/type/author"
TYPE_WORK = "/type/work"
TYPE_EDITION = "/type/edition"


@dataclass(frozen=True)
class DumpRecord:
    """One parsed dump line: its Open Library type, its key and the JSON body."""

    type: str
    key: str
    data: dict


@dataclass(frozen=True)
class ParsedAuthor:
    id: str
    name: str


@dataclass(frozen=True)
class ParsedWork:
    id: str
    title: str
    slug: str
    author_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ParsedEdition:
    id: str
    work_id: str | None
    format: str
    isbn_10: str | None
    isbn_13: str | None


def ol_id(key: str) -> str:
    """The bare Open Library id from a key: ``/works/OL1W`` -> ``OL1W``.

    >>> ol_id("/works/OL1W")
    'OL1W'
    >>> ol_id("/authors/OL2A")
    'OL2A'
    """
    trimmed = key.strip().rstrip("/")
    if not trimmed or "/" not in trimmed:
        raise MalformedRecord(f"not an Open Library key: {key!r}")
    return trimmed.rsplit("/", 1)[-1]


def slugify(text: str) -> str:
    """A URL-safe slug fragment from a title. Never empty.

    >>> slugify("Sapiens: A Brief History of Humankind")
    'sapiens-a-brief-history-of-humankind'
    >>> slugify("   ")
    'untitled'
    """
    lowered = text.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    # Keep slugs bounded; real titles run very long. Trim on a word boundary.
    if len(cleaned) > 80:
        cleaned = cleaned[:80].rstrip("-")
    return cleaned or "untitled"


def parse_dump_line(line: str) -> DumpRecord:
    """Turn one raw dump line into a :class:`DumpRecord`.

    Open Library dump rows have five tab-separated columns; the fifth is the JSON
    record. Raises :class:`MalformedRecord` on a short row or unparseable JSON.
    """
    columns = line.rstrip("\n").split("\t")
    if len(columns) < 5:
        raise MalformedRecord(f"expected 5 tab-separated columns, got {len(columns)}")
    type_, key, _revision, _last_modified, body = columns[:5]
    if not type_ or not key:
        raise MalformedRecord("row is missing its type or key")
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise MalformedRecord(f"record JSON is invalid: {exc}") from exc
    if not isinstance(data, dict):
        raise MalformedRecord("record JSON is not an object")
    return DumpRecord(type=type_, key=key, data=data)


def _author_ids(data: dict) -> list[str]:
    """Extract author Open Library ids from a work record, defensively.

    Open Library has used several shapes for a work's authors over the years:
    ``[{"author": {"key": "/authors/OL1A"}}]``, ``[{"author": "/authors/OL1A"}]``
    and, rarely, ``[{"key": "/authors/OL1A"}]``. We accept all of them and skip
    entries we cannot read rather than failing the whole work.
    """
    ids: list[str] = []
    for entry in data.get("authors", []) or []:
        key = None
        if isinstance(entry, dict):
            author = entry.get("author", entry)
            if isinstance(author, dict):
                key = author.get("key")
            elif isinstance(author, str):
                key = author
        elif isinstance(entry, str):
            key = entry
        if isinstance(key, str) and key.startswith("/authors/"):
            try:
                ids.append(ol_id(key))
            except MalformedRecord:
                continue
    return ids


def parse_author(record: DumpRecord) -> ParsedAuthor:
    name = record.data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise MalformedRecord("author record has no usable name")
    return ParsedAuthor(id=ol_id(record.key), name=name.strip())


def parse_work(record: DumpRecord) -> ParsedWork:
    title = record.data.get("title")
    if not isinstance(title, str) or not title.strip():
        raise MalformedRecord("work record has no usable title")
    title = title.strip()
    work_id = ol_id(record.key)
    # Append the Open Library id so the slug is unique and stable across re-ingest:
    # two distinct works can share a title, and merging on a colliding slug would
    # fail the unique constraint. The title fragment keeps the URL search-friendly.
    slug = f"{slugify(title)}-{work_id.lower()}"
    return ParsedWork(
        id=work_id, title=title, slug=slug, author_ids=_author_ids(record.data)
    )


def _first_str(data: dict, key: str) -> str | None:
    value = data.get(key)
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str) and item.strip():
                return item.strip()
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def parse_edition(record: DumpRecord) -> ParsedEdition:
    edition_id = ol_id(record.key)
    work_id: str | None = None
    works = record.data.get("works") or []
    if works and isinstance(works[0], dict):
        work_key = works[0].get("key")
        if isinstance(work_key, str) and work_key.startswith("/works/"):
            work_id = ol_id(work_key)
    # ``physical_format`` is absent on digital-only editions; default rather than
    # fail, since a null format would break the not-null column.
    fmt = _first_str(record.data, "physical_format") or "unknown"
    return ParsedEdition(
        id=edition_id,
        work_id=work_id,
        format=fmt.lower(),
        isbn_10=_first_str(record.data, "isbn_10"),
        isbn_13=_first_str(record.data, "isbn_13"),
    )
