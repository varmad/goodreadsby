import json
import unittest

from app.ingest import UNKNOWN_AUTHOR, Stats, run_ingest


def _line(type_: str, key: str, record: dict) -> str:
    return "\t".join([type_, key, "1", "2024-01-01T00:00:00", json.dumps(record)])


def _author(ol_key: str, name: str) -> str:
    return _line("/type/author", ol_key, {"name": name})


def _work(ol_key: str, title: str, author_keys: list[str] | None = None) -> str:
    record: dict = {"title": title}
    if author_keys:
        record["authors"] = [{"author": {"key": k}} for k in author_keys]
    return _line("/type/work", ol_key, record)


def _edition(ol_key: str, work_key: str | None, fmt: str = "paperback") -> str:
    record: dict = {"physical_format": fmt, "isbn_10": ["0062316117"]}
    if work_key is not None:
        record["works"] = [{"key": work_key}]
    return _line("/type/edition", ol_key, record)


class FakeStore:
    """An in-memory :class:`app.ingest.Store` — no database, no SQLAlchemy.

    Upserts are keyed by id (dicts), mirroring the real store's merge-by-primary-key,
    so idempotency and the Work/Edition relationship can be asserted directly.
    """

    def __init__(self, checkpoints: dict[str, int] | None = None) -> None:
        self.authors: dict[str, str] = {}
        self.works: dict[str, dict] = {}
        self.editions: dict[str, dict] = {}
        self.checkpoints: dict[str, int] = dict(checkpoints or {})
        self.commits = 0

    def get_checkpoint(self, source: str) -> int:
        return self.checkpoints.get(source, 0)

    def set_checkpoint(self, source: str, line_no: int) -> None:
        self.checkpoints[source] = line_no

    def upsert_author(self, author_id: str, name: str) -> None:
        self.authors[author_id] = name

    def upsert_work(self, work_id: str, title: str, author: str, slug: str) -> None:
        self.works[work_id] = {"title": title, "author": author, "slug": slug}

    def upsert_edition(self, edition_id, work_id, fmt, isbn_10, isbn_13) -> None:
        self.editions[edition_id] = {
            "work_id": work_id,
            "format": fmt,
            "isbn_10": isbn_10,
            "isbn_13": isbn_13,
        }

    def get_author_name(self, author_id: str):
        return self.authors.get(author_id)

    def commit(self) -> None:
        self.commits += 1


class RunIngestTests(unittest.TestCase):
    def test_stores_works_and_editions_preserving_the_relationship(self):
        store = FakeStore()
        lines = [
            _author("/authors/OL7A", "Yuval Noah Harari"),
            _work("/works/OL1W", "Sapiens", ["/authors/OL7A"]),
            _edition("/books/OL5M", "/works/OL1W"),
        ]
        stats = run_ingest(store, "dump", lines, log=lambda _m: None)

        self.assertEqual(stats, Stats(stored=3))
        self.assertEqual(store.works["OL1W"]["author"], "Yuval Noah Harari")
        self.assertEqual(store.works["OL1W"]["slug"], "sapiens-ol1w")
        # The Edition carries its own identifiers and points at its Work.
        self.assertEqual(store.editions["OL5M"]["work_id"], "OL1W")
        self.assertEqual(store.editions["OL5M"]["isbn_10"], "0062316117")

    def test_re_running_is_idempotent(self):
        lines = [
            _author("/authors/OL7A", "Harari"),
            _work("/works/OL1W", "Sapiens", ["/authors/OL7A"]),
            _edition("/books/OL5M", "/works/OL1W"),
        ]
        store = FakeStore()
        run_ingest(store, "dump", lines, log=lambda _m: None)
        # A second pass over the same records must not duplicate anything.
        store.checkpoints.clear()  # force a full re-read, not a resume
        run_ingest(store, "dump", lines, log=lambda _m: None)

        self.assertEqual(len(store.works), 1)
        self.assertEqual(len(store.editions), 1)
        self.assertEqual(len(store.authors), 1)

    def test_resumes_after_the_checkpoint_instead_of_restarting(self):
        lines = [
            _work("/works/OL1W", "First"),
            _work("/works/OL2W", "Second"),
            _work("/works/OL3W", "Third"),
            _work("/works/OL4W", "Fourth"),
        ]
        # Pretend the first two lines were already committed before a crash.
        store = FakeStore(checkpoints={"dump": 2})
        stats = run_ingest(store, "dump", lines, log=lambda _m: None)

        self.assertEqual(stats.stored, 2)
        self.assertNotIn("OL1W", store.works)
        self.assertNotIn("OL2W", store.works)
        self.assertIn("OL3W", store.works)
        self.assertIn("OL4W", store.works)
        self.assertEqual(store.checkpoints["dump"], 4)

    def test_unparseable_records_are_skipped_and_reported_not_dropped(self):
        reports: list[str] = []
        lines = [
            _work("/works/OL1W", "Good"),
            "this is not a valid dump row",
            _line("/type/work", "/works/OL2W", {"no_title": True}),
            _work("/works/OL3W", "Also good"),
        ]
        stats = run_ingest(store := FakeStore(), "dump", lines, log=reports.append)

        self.assertEqual(stats.stored, 2)
        self.assertEqual(stats.failed, 2)
        self.assertEqual(len(store.works), 2)
        # Every failure was surfaced, never silently dropped.
        self.assertEqual(sum("skipped unparseable" in m for m in reports), 2)

    def test_edition_without_a_work_is_skipped_and_reported(self):
        reports: list[str] = []
        stats = run_ingest(
            store := FakeStore(),
            "dump",
            [_edition("/books/OL5M", None)],
            log=reports.append,
        )
        self.assertEqual(stats, Stats(skipped=1))
        self.assertEqual(store.editions, {})
        self.assertTrue(any("no work reference" in m for m in reports))

    def test_unresolved_author_falls_back_to_placeholder(self):
        store = FakeStore()
        run_ingest(
            store,
            "dump",
            [_work("/works/OL1W", "Orphan", ["/authors/OLMISSING"])],
            log=lambda _m: None,
        )
        self.assertEqual(store.works["OL1W"]["author"], UNKNOWN_AUTHOR)

    def test_blank_lines_are_ignored(self):
        stats = run_ingest(
            FakeStore(), "dump", ["", "   ", _work("/works/OL1W", "T")],
            log=lambda _m: None,
        )
        self.assertEqual(stats, Stats(stored=1))

    def test_progress_and_completion_are_logged(self):
        reports: list[str] = []
        run_ingest(
            FakeStore(),
            "dump",
            [_work("/works/OL1W", "T")],
            log=reports.append,
            progress_every=1,
        )
        self.assertTrue(any("1 lines" in m for m in reports))
        self.assertTrue(any(m.endswith("stored, 0 skipped, 0 failed") for m in reports))

    def test_commits_in_batches_and_at_the_end(self):
        store = FakeStore()
        lines = [_work(f"/works/OL{i}W", f"T{i}") for i in range(1, 6)]
        run_ingest(store, "dump", lines, log=lambda _m: None, batch_size=2)
        # Two full batches (lines 2 and 4) plus a final commit for the remainder.
        self.assertEqual(store.commits, 3)
        self.assertEqual(store.checkpoints["dump"], 5)


if __name__ == "__main__":
    unittest.main()
