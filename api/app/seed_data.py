"""The hand-entered first slice.

Pure data — no database, no framework — so it can be validated in tests and
consumed by ``app.seed`` to rebuild the skeleton from empty. Later tickets replace
this with the Open Library ingest (SCRUM-4) and the approval queue.

It deliberately includes one Work recommended by several people, to prove a Work
page shows all of its Recommendations.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from .domain.models import (
    Edition,
    Recommender,
    Recommendation,
    Source,
    Work,
)

# A fixed ingestion instant keeps the seed reproducible byte-for-byte. It is
# internal bookkeeping and, per the presenter, is never shown to a reader.
_INGESTED_AT = datetime(2026, 7, 1, 9, 0, tzinfo=timezone.utc)


RECOMMENDERS: list[Recommender] = [
    Recommender(id="rec-naval", name="Naval Ravikant", slug="naval-ravikant"),
    Recommender(id="rec-ryan", name="Ryan Holiday", slug="ryan-holiday"),
    Recommender(id="rec-cal", name="Cal Newport", slug="cal-newport"),
]

WORKS: list[Work] = [
    Work(
        id="work-sapiens",
        title="Sapiens: A Brief History of Humankind",
        author="Yuval Noah Harari",
        slug="sapiens",
    ),
    Work(
        id="work-meditations",
        title="Meditations",
        author="Marcus Aurelius",
        slug="meditations",
    ),
]

EDITIONS: list[Edition] = [
    Edition(
        id="ed-sapiens-pb",
        work_id="work-sapiens",
        format="paperback",
        isbn_10="0062316117",
        isbn_13="9780062316110",
    ),
    Edition(
        id="ed-meditations-pb",
        work_id="work-meditations",
        format="paperback",
        isbn_10="0812968255",
        isbn_13="9780812968255",
    ),
]

SOURCES: list[Source] = [
    Source(
        id="src-naval-tim",
        title="Naval Ravikant on The Tim Ferriss Show",
        url="https://example.com/podcasts/tim-ferriss/naval",
        position_seconds=1830,
    ),
    Source(
        id="src-ryan-daily",
        title="Ryan Holiday — The Daily Stoic Podcast, Ep. 412",
        url="https://example.com/podcasts/daily-stoic/412",
        position_seconds=245,
    ),
    Source(
        id="src-cal-deep",
        title="Cal Newport — Deep Questions, Ep. 88",
        url="https://example.com/podcasts/deep-questions/88",
        position_seconds=3725,
    ),
]

_SOURCES_BY_ID = {s.id: s for s in SOURCES}
_RECOMMENDERS_BY_ID = {r.id: r for r in RECOMMENDERS}

RECOMMENDATIONS: list[Recommendation] = [
    # Sapiens — recommended by two people, on two different Sources.
    Recommendation(
        id="rmd-1",
        work_id="work-sapiens",
        recommender=_RECOMMENDERS_BY_ID["rec-naval"],
        source=_SOURCES_BY_ID["src-naval-tim"],
        said_on=date(2026, 6, 12),
        ingested_at=_INGESTED_AT,
    ),
    Recommendation(
        id="rmd-2",
        work_id="work-sapiens",
        recommender=_RECOMMENDERS_BY_ID["rec-cal"],
        source=_SOURCES_BY_ID["src-cal-deep"],
        said_on=date(2026, 6, 28),
        ingested_at=_INGESTED_AT,
    ),
    # Meditations — a single Recommendation.
    Recommendation(
        id="rmd-3",
        work_id="work-meditations",
        recommender=_RECOMMENDERS_BY_ID["rec-ryan"],
        source=_SOURCES_BY_ID["src-ryan-daily"],
        said_on=date(2026, 5, 3),
        ingested_at=_INGESTED_AT,
    ),
]
