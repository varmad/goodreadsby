"""Reads that map ORM rows back into pure domain records.

The public site only reads, so the repository only needs to load a Work and all of
its Recommendations. Everything the presenter needs is eager-loaded in one go.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..domain import models as domain
from . import models as orm


def _to_domain_recommendation(row: orm.Recommendation) -> domain.Recommendation:
    return domain.Recommendation(
        id=row.id,
        work_id=row.work_id,
        recommender=domain.Recommender(
            id=row.recommender.id,
            name=row.recommender.name,
            slug=row.recommender.slug,
        ),
        source=domain.Source(
            id=row.source.id,
            title=row.source.title,
            url=row.source.url,
            position_seconds=row.source.position_seconds,
        ),
        said_on=row.said_on,
        ingested_at=row.ingested_at,
    )


def _to_domain_work(row: orm.Work) -> domain.Work:
    return domain.Work(id=row.id, title=row.title, author=row.author, slug=row.slug)


def get_work_by_slug(
    session: Session, slug: str
) -> tuple[domain.Work, list[domain.Recommendation]] | None:
    """Return the Work and all its Recommendations, or None if unknown."""
    stmt = (
        select(orm.Work)
        .where(orm.Work.slug == slug)
        .options(
            joinedload(orm.Work.recommendations).joinedload(
                orm.Recommendation.recommender
            ),
            joinedload(orm.Work.recommendations).joinedload(orm.Recommendation.source),
        )
    )
    work_row = session.scalars(stmt).unique().one_or_none()
    if work_row is None:
        return None
    work = _to_domain_work(work_row)
    recs = [_to_domain_recommendation(r) for r in work_row.recommendations]
    return work, recs
