# 11 — Lists as named views

**What to build:** The pages that carry the site's traffic. A List is a named query over
Recommendations — most-recommended, recommended this week, by category, everything from a
given Feed, everything from a given Recommender — rendered as a browsable page.

Per ADR-0002 there is no lists table and nobody authors a list. Adding a new List is
configuration, and ordering is derived rather than hand-set. Counting and deduplication
operate on Works, so a book recommended by seven people is one entry showing seven
recommenders, not seven entries.

This can be built against seeded data and does not wait on the extraction pipeline.

**Blocked by:** 04 — Open Library ingest.

**Status:** ready-for-agent

- [ ] A List renders as a server-rendered page of Works with their recommenders and counts
- [ ] Adding a new List is a configuration change, requiring no new page code
- [ ] Works are deduplicated across Editions — one entry per Work regardless of format
- [ ] A time-bounded List such as "this week" reflects when recommendations were *said*,
      not when they were ingested
- [ ] Recommender and Feed pages are Lists, not bespoke page types
- [ ] An empty List renders as a valid page rather than an error
- [ ] List pages remain responsive as the corpus grows to hundreds of thousands of
      Recommendations
