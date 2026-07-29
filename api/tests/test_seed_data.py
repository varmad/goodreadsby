import unittest

from app.domain.presenter import present_work
from app import seed_data


class SeedDataTests(unittest.TestCase):
    def test_every_recommendation_resolves_to_a_seeded_work(self):
        work_ids = {w.id for w in seed_data.WORKS}
        for rec in seed_data.RECOMMENDATIONS:
            self.assertIn(rec.work_id, work_ids)

    def test_every_edition_belongs_to_a_seeded_work(self):
        work_ids = {w.id for w in seed_data.WORKS}
        for edition in seed_data.EDITIONS:
            self.assertIn(edition.work_id, work_ids)

    def test_every_recommendation_has_a_source_position(self):
        for rec in seed_data.RECOMMENDATIONS:
            self.assertGreaterEqual(rec.source.position_seconds, 0)

    def test_at_least_one_work_has_several_recommendations(self):
        counts: dict[str, int] = {}
        for rec in seed_data.RECOMMENDATIONS:
            counts[rec.work_id] = counts.get(rec.work_id, 0) + 1
        self.assertTrue(
            any(n >= 2 for n in counts.values()),
            "seed must include a Work with several Recommendations",
        )

    def test_seed_renders_through_the_public_presenter(self):
        # Prove the seeded records survive the public seam without leaking ingest data.
        for work in seed_data.WORKS:
            recs = [r for r in seed_data.RECOMMENDATIONS if r.work_id == work.id]
            payload = present_work(work, recs)
            self.assertEqual(payload["id"], work.id)
            self.assertEqual(len(payload["recommendations"]), len(recs))


if __name__ == "__main__":
    unittest.main()
