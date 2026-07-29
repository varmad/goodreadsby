"""End-to-end ingest through the real SQLAlchemy store.

Unlike the pure ``test_ingest`` (which drives a fake store), this exercises the
actual persistence: ``SqlAlchemyStore`` merging into real tables, the repository
reading them back, and the presenter shaping the public payload. It runs against a
temporary SQLite database so no Postgres is needed.

SQLAlchemy is a declared dependency but may not be installed in every environment
(the unit tests above need only the standard library). When it is absent this whole
module is skipped rather than failing, so ``make api-test`` stays green either way.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest

try:  # pragma: no cover - exercised by presence/absence of the dependency
    import sqlalchemy  # noqa: F401

    HAVE_SQLALCHEMY = True
except ImportError:  # pragma: no cover
    HAVE_SQLALCHEMY = False

_DB_FD, _DB_PATH = (None, None)


def setUpModule() -> None:
    global _DB_FD, _DB_PATH
    if not HAVE_SQLALCHEMY:
        return
    # Point the engine at a throwaway SQLite file before app.db.session imports.
    _DB_FD, _DB_PATH = tempfile.mkstemp(suffix=".db")
    os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{_DB_PATH}"


def tearDownModule() -> None:
    if _DB_PATH:
        os.close(_DB_FD)
        os.unlink(_DB_PATH)


def _line(type_: str, key: str, record: dict) -> str:
    return "\t".join([type_, key, "1", "2024-01-01", json.dumps(record)])


DUMP = [
    _line("/type/author", "/authors/OL7A", {"name": "Yuval Noah Harari"}),
    _line(
        "/type/work",
        "/works/OL1W",
        {"title": "Sapiens", "authors": [{"author": {"key": "/authors/OL7A"}}]},
    ),
    _line(
        "/type/edition",
        "/books/OL5M",
        {
            "works": [{"key": "/works/OL1W"}],
            "isbn_10": ["0062316117"],
            "physical_format": "Paperback",
        },
    ),
    _line(
        "/type/edition",
        "/books/OL6M",
        {"works": [{"key": "/works/OL1W"}], "physical_format": "Hardcover"},
    ),
]


@unittest.skipUnless(HAVE_SQLALCHEMY, "SQLAlchemy not installed")
class IngestStoreEndToEndTests(unittest.TestCase):
    def setUp(self):
        from app.db.base import Base
        from app.db.session import engine
        from app.ingest_store import create_schema

        # Fresh schema per test for isolation.
        Base.metadata.drop_all(bind=engine)
        create_schema()

    def _ingest(self, lines, source="dump"):
        from app.ingest import run_ingest
        from app.ingest_store import SqlAlchemyStore

        with SqlAlchemyStore() as store:
            return run_ingest(store, source, lines, log=lambda _m: None)

    def _present_work(self, slug):
        from app.db.session import SessionLocal
        from app.db.repository import get_work_by_slug
        from app.domain.presenter import present_work

        with SessionLocal() as session:
            result = get_work_by_slug(session, slug)
            if result is None:
                return None
            work, recs, editions = result
            return present_work(work, recs, editions)

    def test_a_work_page_renders_real_catalogue_data_end_to_end(self):
        self._ingest(DUMP)
        payload = self._present_work("sapiens-ol1w")
        self.assertIsNotNone(payload)
        self.assertEqual(payload["title"], "Sapiens")
        self.assertEqual(payload["author"], "Yuval Noah Harari")
        # Both Editions' formats surface as the Work's available formats.
        self.assertEqual(payload["formats"], ["hardcover", "paperback"])

    def test_re_running_the_ingest_is_idempotent(self):
        self._ingest(DUMP)
        # Re-run from scratch (new source name avoids the resume checkpoint).
        self._ingest(DUMP, source="dump-again")

        from sqlalchemy import func, select
        from app.db import models as orm
        from app.db.session import SessionLocal

        with SessionLocal() as session:
            works = session.scalar(select(func.count()).select_from(orm.Work))
            editions = session.scalar(select(func.count()).select_from(orm.Edition))
        self.assertEqual(works, 1)
        self.assertEqual(editions, 2)

    def test_an_interrupted_ingest_resumes_from_its_checkpoint(self):
        # First pass stops after the checkpoint would be at line 2 (author + work).
        self._ingest(DUMP[:2])
        # A crash leaves checkpoint at 2; resuming the same source picks up line 3+.
        stats = self._ingest(DUMP)
        self.assertEqual(stats.stored, 2)  # only the two editions, not the whole file

        payload = self._present_work("sapiens-ol1w")
        self.assertEqual(payload["formats"], ["hardcover", "paperback"])


if __name__ == "__main__":
    unittest.main()
