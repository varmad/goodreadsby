"""SQLAlchemy binding for the ingest (SCRUM-4).

This is the concrete :class:`app.ingest.Store`. It is kept in its own module so
that ``app.ingest`` — the orchestration and its tests — never imports SQLAlchemy.
Every write is a ``session.merge``: an upsert keyed by primary key, which is what
makes re-running the ingest idempotent regardless of database dialect.
"""

from __future__ import annotations

from .db import models as orm
from .db.base import Base
from .db.session import SessionLocal, engine


def create_schema() -> None:
    """Create any missing tables so the ingest runs against a fresh database."""
    Base.metadata.create_all(bind=engine)


class SqlAlchemyStore:
    """One database session for the span of a single dump file."""

    def __init__(self) -> None:
        self.session = SessionLocal()

    def __enter__(self) -> "SqlAlchemyStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            self.session.rollback()
        self.session.close()

    def get_checkpoint(self, source: str) -> int:
        row = self.session.get(orm.IngestCheckpoint, source)
        return row.line_no if row else 0

    def set_checkpoint(self, source: str, line_no: int) -> None:
        self.session.merge(orm.IngestCheckpoint(source=source, line_no=line_no))

    def upsert_author(self, author_id: str, name: str) -> None:
        self.session.merge(orm.Author(id=author_id, name=name))

    def upsert_work(
        self, work_id: str, title: str, author: str, slug: str
    ) -> None:
        self.session.merge(
            orm.Work(id=work_id, title=title, author=author, slug=slug)
        )

    def upsert_edition(
        self,
        edition_id: str,
        work_id: str,
        fmt: str,
        isbn_10: str | None,
        isbn_13: str | None,
    ) -> None:
        self.session.merge(
            orm.Edition(
                id=edition_id,
                work_id=work_id,
                format=fmt,
                isbn_10=isbn_10,
                isbn_13=isbn_13,
            )
        )

    def get_author_name(self, author_id: str) -> str | None:
        row = self.session.get(orm.Author, author_id)
        return row.name if row else None

    def commit(self) -> None:
        self.session.commit()
