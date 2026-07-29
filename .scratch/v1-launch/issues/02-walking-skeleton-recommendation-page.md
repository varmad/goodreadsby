# 02 — Walking skeleton: a hand-entered Recommendation renders publicly

**What to build:** The thinnest complete path through every layer of the system. A
visitor opens a Work page and sees the book, who recommended it, when they said it, and
a link that takes them to the exact moment in the Source where it was said.

The data for this first slice is seeded by hand — no ingestion, no extraction, no
approval queue. The point is to prove the whole vertical exists and holds together
before any of those are built.

Establish the core entities from the glossary: Recommender, Source, Work, Edition and
Recommendation, with a Recommendation pointing at a Work rather than an Edition per
ADR-0002. Keep the schema minimal; later tickets extend it.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Core entities exist in Postgres, with Recommendation referencing a Work
- [ ] A Recommendation records both when it was said and when it was ingested, and only
      the former is ever shown to a reader
- [ ] The public site serves a server-rendered Work page — not client-rendered — per ADR-0004
- [ ] The page shows the Recommender, the date said, and a link into the Source at its
      exact position
- [ ] A Work with several Recommendations shows all of them
- [ ] Seed data is reproducible from a command, so the skeleton can be rebuilt from empty
