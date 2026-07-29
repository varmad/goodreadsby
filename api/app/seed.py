"""Rebuild the skeleton's data from empty.

    python -m app.seed

Drops and recreates every table, then inserts the hand-entered first slice from
``app.seed_data``. Dropping first makes it reproducible and idempotent: running it
against a fresh database or a seeded one both leave exactly the seed contents.
"""

from __future__ import annotations

from .db import models as orm
from .db.base import Base
from .db.session import SessionLocal, engine
from . import seed_data


def reset_schema() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def load_seed() -> None:
    with SessionLocal() as session:
        for r in seed_data.RECOMMENDERS:
            session.add(orm.Recommender(id=r.id, name=r.name, slug=r.slug))
        for w in seed_data.WORKS:
            session.add(
                orm.Work(id=w.id, title=w.title, author=w.author, slug=w.slug)
            )
        for e in seed_data.EDITIONS:
            session.add(
                orm.Edition(
                    id=e.id,
                    work_id=e.work_id,
                    format=e.format,
                    isbn_10=e.isbn_10,
                    isbn_13=e.isbn_13,
                )
            )
        for s in seed_data.SOURCES:
            session.add(
                orm.Source(
                    id=s.id,
                    title=s.title,
                    url=s.url,
                    position_seconds=s.position_seconds,
                )
            )
        for rec in seed_data.RECOMMENDATIONS:
            session.add(
                orm.Recommendation(
                    id=rec.id,
                    work_id=rec.work_id,
                    recommender_id=rec.recommender.id,
                    source_id=rec.source.id,
                    said_on=rec.said_on,
                    ingested_at=rec.ingested_at,
                )
            )
        session.commit()


def main() -> None:
    reset_schema()
    load_seed()
    print(
        f"Seeded {len(seed_data.WORKS)} works and "
        f"{len(seed_data.RECOMMENDATIONS)} recommendations."
    )


if __name__ == "__main__":
    main()
