import unittest

from app.domain.sources import format_timestamp, source_deep_link


class FormatTimestampTests(unittest.TestCase):
    def test_under_an_hour_is_minutes_and_seconds(self):
        self.assertEqual(format_timestamp(0), "0:00")
        self.assertEqual(format_timestamp(75), "1:15")
        self.assertEqual(format_timestamp(245), "4:05")

    def test_over_an_hour_includes_hours(self):
        self.assertEqual(format_timestamp(3725), "1:02:05")

    def test_negative_is_rejected(self):
        with self.assertRaises(ValueError):
            format_timestamp(-1)


class SourceDeepLinkTests(unittest.TestCase):
    def test_appends_media_fragment(self):
        self.assertEqual(
            source_deep_link("https://ex.com/ep/1", 90),
            "https://ex.com/ep/1#t=90",
        )

    def test_replaces_existing_fragment_so_relinking_is_idempotent(self):
        once = source_deep_link("https://ex.com/ep/1", 90)
        twice = source_deep_link(once, 90)
        self.assertEqual(once, twice)

    def test_negative_is_rejected(self):
        with self.assertRaises(ValueError):
            source_deep_link("https://ex.com/ep/1", -1)


if __name__ == "__main__":
    unittest.main()
