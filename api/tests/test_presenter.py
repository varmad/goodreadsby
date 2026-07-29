import json
import unittest
from datetime import date, datetime, timezone

from app.domain.models import Edition, Recommendation, Recommender, Source, Work
from app.domain.presenter import present_recommendation, present_work


def _recommendation(rec_id: str, said_on: date) -> Recommendation:
    return Recommendation(
        id=rec_id,
        work_id="work-1",
        recommender=Recommender(id="r1", name="Ada Lovelace", slug="ada-lovelace"),
        source=Source(
            id="s1",
            title="Some Podcast, Ep. 1",
            url="https://ex.com/ep/1",
            position_seconds=90,
        ),
        said_on=said_on,
        ingested_at=datetime(2026, 7, 1, tzinfo=timezone.utc),
    )


class PresentRecommendationTests(unittest.TestCase):
    def test_shows_recommender_date_said_and_source_position(self):
        payload = present_recommendation(_recommendation("rmd-1", date(2026, 6, 1)))
        self.assertEqual(payload["recommender"]["name"], "Ada Lovelace")
        self.assertEqual(payload["said_on"], "2026-06-01")
        self.assertEqual(payload["source"]["url"], "https://ex.com/ep/1#t=90")
        self.assertEqual(payload["source"]["position_label"], "1:30")

    def test_ingested_at_is_never_exposed(self):
        payload = present_recommendation(_recommendation("rmd-1", date(2026, 6, 1)))
        # The internal ingestion instant must not leak — not by key, not by value.
        self.assertNotIn("ingested_at", json.dumps(payload))
        self.assertNotIn("2026-07-01", json.dumps(payload))


class PresentWorkTests(unittest.TestCase):
    def test_shows_every_recommendation_for_the_work(self):
        work = Work(id="work-1", title="A Book", author="An Author", slug="a-book")
        recs = [
            _recommendation("rmd-1", date(2026, 6, 1)),
            _recommendation("rmd-2", date(2026, 6, 20)),
            _recommendation("rmd-3", date(2026, 5, 15)),
        ]
        payload = present_work(work, recs)
        self.assertEqual(len(payload["recommendations"]), 3)

    def test_recommendations_are_most_recent_first(self):
        work = Work(id="work-1", title="A Book", author="An Author", slug="a-book")
        recs = [
            _recommendation("rmd-1", date(2026, 6, 1)),
            _recommendation("rmd-2", date(2026, 6, 20)),
            _recommendation("rmd-3", date(2026, 5, 15)),
        ]
        payload = present_work(work, recs)
        said = [r["said_on"] for r in payload["recommendations"]]
        self.assertEqual(said, ["2026-06-20", "2026-06-01", "2026-05-15"])

    def test_lists_available_formats_deduplicated_and_sorted(self):
        work = Work(id="work-1", title="A Book", author="An Author", slug="a-book")
        editions = [
            Edition(id="e1", work_id="work-1", format="paperback"),
            Edition(id="e2", work_id="work-1", format="hardcover"),
            Edition(id="e3", work_id="work-1", format="paperback"),
        ]
        payload = present_work(work, [], editions)
        self.assertEqual(payload["formats"], ["hardcover", "paperback"])

    def test_formats_default_to_empty_without_editions(self):
        work = Work(id="work-1", title="A Book", author="An Author", slug="a-book")
        payload = present_work(work, [_recommendation("rmd-1", date(2026, 6, 1))])
        self.assertEqual(payload["formats"], [])

    def test_work_payload_never_leaks_ingestion_data(self):
        work = Work(id="work-1", title="A Book", author="An Author", slug="a-book")
        payload = present_work(work, [_recommendation("rmd-1", date(2026, 6, 1))])
        self.assertNotIn("ingested_at", json.dumps(payload))


if __name__ == "__main__":
    unittest.main()
