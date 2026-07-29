"""Pure domain records for the walking skeleton.

These dataclasses are the framework-independent shape of the domain. They import
only the standard library so the domain rules that matter for this ticket — what a
reader is allowed to see, and how a Source is deep-linked — can be unit-tested
without a database or a web framework in the loop.

The SQLAlchemy models in ``app.db.models`` persist these to Postgres; the repository
maps rows back into these records; the presenter turns them into public JSON.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class Recommender:
    """A real, identifiable person whose public book recommendations we record."""

    id: str
    name: str
    slug: str


@dataclass(frozen=True)
class Source:
    """A single published artifact that evidences a Recommendation.

    ``position_seconds`` is the exact position within the Source where the
    recommendation was said — the thing the reader clicks through to.
    """

    id: str
    title: str
    url: str
    position_seconds: int


@dataclass(frozen=True)
class Edition:
    """One purchasable form of a Work. Editions carry identifiers; Works do not."""

    id: str
    work_id: str
    format: str
    isbn_10: str | None = None
    isbn_13: str | None = None


@dataclass(frozen=True)
class Work:
    """A book as a thing people talk about, independent of how it is printed."""

    id: str
    title: str
    author: str
    slug: str


@dataclass(frozen=True)
class Recommendation:
    """A named person spoke positively about one Work, at a knowable moment.

    ``said_on`` is when it was said — the only date a reader ever sees.
    ``ingested_at`` is when we recorded it — internal, never shown.
    """

    id: str
    work_id: str
    recommender: Recommender
    source: Source
    said_on: date
    ingested_at: datetime
