"""Turns domain records into the public JSON a reader is allowed to see.

This is the single seam through which anything reaches the public site, so it is
where the "only the date said is ever shown" rule is enforced: ``ingested_at``
exists on the domain record but never appears in a presented payload.
"""

from __future__ import annotations

from typing import Iterable

from .models import Edition, Recommendation, Work
from .sources import format_timestamp, source_deep_link


def present_recommendation(rec: Recommendation) -> dict:
    """Public shape of a single Recommendation. Never includes ``ingested_at``."""
    return {
        "recommender": {
            "name": rec.recommender.name,
            "slug": rec.recommender.slug,
        },
        "said_on": rec.said_on.isoformat(),
        "source": {
            "title": rec.source.title,
            "url": source_deep_link(rec.source.url, rec.source.position_seconds),
            "position_label": format_timestamp(rec.source.position_seconds),
        },
    }


def present_work(
    work: Work,
    recommendations: Iterable[Recommendation],
    editions: Iterable[Edition] = (),
) -> dict:
    """Public shape of a Work page: the book, its Recommendations and its formats.

    Recommendations are ordered most-recent-first by the date they were said.
    ``formats`` is the sorted, de-duplicated set of Edition formats — the available
    forms of the Work, drawn from the Open Library ingest (SCRUM-4).
    """
    ordered = sorted(recommendations, key=lambda r: r.said_on, reverse=True)
    formats = sorted({e.format for e in editions})
    return {
        "id": work.id,
        "slug": work.slug,
        "title": work.title,
        "author": work.author,
        "formats": formats,
        "recommendations": [present_recommendation(r) for r in ordered],
    }
