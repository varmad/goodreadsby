"""SQLAlchemy ORM models — the core entities persisted to Postgres.

Kept deliberately minimal for the walking skeleton; later tickets extend it. The
one rule this schema enforces structurally is ADR-0002: a Recommendation references
a Work, not an Edition. Editions hang off Works and carry the identifiers.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Recommender(Base):
    __tablename__ = "recommenders"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)


class Author(Base):
    """A catalogue author from Open Library, keyed by its Open Library id.

    Denormalised onto ``Work.author`` at ingest time (SCRUM-4); the site reads the
    name off the Work, so this table only exists to resolve a work's author keys.
    """

    __tablename__ = "authors"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class IngestCheckpoint(Base):
    """The last committed dump line per source file, so an ingest can resume.

    Written in the same transaction as each batch (SCRUM-4): after a crash the
    checkpoint and the rows it accounts for advance together, never apart.
    """

    __tablename__ = "ingest_checkpoints"

    source: Mapped[str] = mapped_column(String, primary_key=True)
    line_no: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    # Exact position within the Source where the recommendation was said.
    position_seconds: Mapped[int] = mapped_column(Integer, nullable=False)


class Work(Base):
    __tablename__ = "works"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    editions: Mapped[list["Edition"]] = relationship(back_populates="work")
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="work"
    )


class Edition(Base):
    __tablename__ = "editions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    work_id: Mapped[str] = mapped_column(ForeignKey("works.id"), nullable=False)
    format: Mapped[str] = mapped_column(String, nullable=False)
    isbn_10: Mapped[str | None] = mapped_column(String, nullable=True)
    isbn_13: Mapped[str | None] = mapped_column(String, nullable=True)

    work: Mapped[Work] = relationship(back_populates="editions")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    # ADR-0002: a Recommendation points at a Work, never an Edition.
    work_id: Mapped[str] = mapped_column(ForeignKey("works.id"), nullable=False)
    recommender_id: Mapped[str] = mapped_column(
        ForeignKey("recommenders.id"), nullable=False
    )
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), nullable=False)
    # When it was said — the only date a reader ever sees.
    said_on: Mapped[date] = mapped_column(Date, nullable=False)
    # When we recorded it — internal, never shown to a reader.
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    work: Mapped[Work] = relationship(back_populates="recommendations")
    recommender: Mapped[Recommender] = relationship()
    source: Mapped[Source] = relationship()
