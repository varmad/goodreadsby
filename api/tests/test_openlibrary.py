import json
import unittest

from app.openlibrary import (
    MalformedRecord,
    ol_id,
    parse_author,
    parse_dump_line,
    parse_edition,
    parse_work,
    slugify,
)


def _line(type_: str, key: str, record: dict) -> str:
    # A dump row: type, key, revision, last_modified, JSON — tab separated.
    return "\t".join([type_, key, "1", "2024-01-01T00:00:00", json.dumps(record)])


class OlIdTests(unittest.TestCase):
    def test_extracts_the_bare_id(self):
        self.assertEqual(ol_id("/works/OL1W"), "OL1W")
        self.assertEqual(ol_id("/authors/OL2A"), "OL2A")
        self.assertEqual(ol_id("/books/OL3M/"), "OL3M")

    def test_rejects_a_non_key(self):
        with self.assertRaises(MalformedRecord):
            ol_id("OL1W")


class SlugifyTests(unittest.TestCase):
    def test_lowercases_and_hyphenates(self):
        self.assertEqual(
            slugify("Sapiens: A Brief History of Humankind"),
            "sapiens-a-brief-history-of-humankind",
        )

    def test_empty_becomes_untitled(self):
        self.assertEqual(slugify("   "), "untitled")

    def test_is_bounded_in_length(self):
        self.assertLessEqual(len(slugify("word " * 100)), 80)


class ParseDumpLineTests(unittest.TestCase):
    def test_parses_a_well_formed_row(self):
        record = parse_dump_line(_line("/type/work", "/works/OL1W", {"title": "A"}))
        self.assertEqual(record.type, "/type/work")
        self.assertEqual(record.key, "/works/OL1W")
        self.assertEqual(record.data["title"], "A")

    def test_short_row_is_malformed(self):
        with self.assertRaises(MalformedRecord):
            parse_dump_line("/type/work\t/works/OL1W\t1")

    def test_invalid_json_is_malformed(self):
        with self.assertRaises(MalformedRecord):
            parse_dump_line("/type/work\t/works/OL1W\t1\t2024\t{not json}")

    def test_non_object_json_is_malformed(self):
        with self.assertRaises(MalformedRecord):
            parse_dump_line("/type/work\t/works/OL1W\t1\t2024\t[1, 2, 3]")


class ParseWorkTests(unittest.TestCase):
    def test_extracts_title_slug_and_author_ids(self):
        record = parse_dump_line(
            _line(
                "/type/work",
                "/works/OL1W",
                {
                    "title": "Sapiens",
                    "authors": [{"author": {"key": "/authors/OL7A"}}],
                },
            )
        )
        work = parse_work(record)
        self.assertEqual(work.id, "OL1W")
        self.assertEqual(work.title, "Sapiens")
        self.assertEqual(work.author_ids, ["OL7A"])
        # Slug carries the id so distinct works never collide on it.
        self.assertEqual(work.slug, "sapiens-ol1w")

    def test_accepts_legacy_author_shapes(self):
        record = parse_dump_line(
            _line(
                "/type/work",
                "/works/OL1W",
                {"title": "T", "authors": [{"author": "/authors/OL9A"}]},
            )
        )
        self.assertEqual(parse_work(record).author_ids, ["OL9A"])

    def test_missing_title_is_malformed(self):
        record = parse_dump_line(_line("/type/work", "/works/OL1W", {"subtitle": "x"}))
        with self.assertRaises(MalformedRecord):
            parse_work(record)


class ParseEditionTests(unittest.TestCase):
    def test_extracts_work_identifiers_and_format(self):
        record = parse_dump_line(
            _line(
                "/type/edition",
                "/books/OL5M",
                {
                    "works": [{"key": "/works/OL1W"}],
                    "isbn_10": ["0062316117"],
                    "isbn_13": ["9780062316110"],
                    "physical_format": "Paperback",
                },
            )
        )
        edition = parse_edition(record)
        self.assertEqual(edition.id, "OL5M")
        self.assertEqual(edition.work_id, "OL1W")
        self.assertEqual(edition.isbn_10, "0062316117")
        self.assertEqual(edition.isbn_13, "9780062316110")
        self.assertEqual(edition.format, "paperback")

    def test_missing_format_defaults_to_unknown(self):
        record = parse_dump_line(
            _line("/type/edition", "/books/OL5M", {"works": [{"key": "/works/OL1W"}]})
        )
        edition = parse_edition(record)
        self.assertEqual(edition.format, "unknown")
        self.assertIsNone(edition.isbn_10)

    def test_edition_without_a_work_has_no_work_id(self):
        record = parse_dump_line(
            _line("/type/edition", "/books/OL5M", {"physical_format": "hardcover"})
        )
        self.assertIsNone(parse_edition(record).work_id)


class ParseAuthorTests(unittest.TestCase):
    def test_extracts_name(self):
        record = parse_dump_line(
            _line("/type/author", "/authors/OL7A", {"name": "Yuval Noah Harari"})
        )
        author = parse_author(record)
        self.assertEqual(author.id, "OL7A")
        self.assertEqual(author.name, "Yuval Noah Harari")

    def test_missing_name_is_malformed(self):
        record = parse_dump_line(_line("/type/author", "/authors/OL7A", {"bio": "x"}))
        with self.assertRaises(MalformedRecord):
            parse_author(record)


if __name__ == "__main__":
    unittest.main()
