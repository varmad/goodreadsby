# 04 — Open Library ingest

**What to build:** Real catalogue data behind the site. An operator runs a command that
loads Open Library's monthly bulk dumps into our own Works and Editions, and Work pages
stop showing seeded placeholders and start showing genuine titles, authors, covers and
available formats.

Per ADR-0001 this is the only catalogue source; Amazon is never queried. Open Library's
own Work/Edition split maps directly onto ours, so the ingest preserves that distinction
rather than flattening it.

The dumps are large and the job is long-running, so it must survive interruption and be
safe to re-run — a monthly refresh will overwrite the same records repeatedly for the
rest of the project's life.

**Blocked by:** 02 — Walking skeleton.

**Status:** ready-for-agent

- [ ] An operator can ingest a dump with a single command
- [ ] Re-running the ingest is idempotent — no duplicated Works or Editions
- [ ] An interrupted ingest resumes rather than restarting from the beginning
- [ ] Open Library's Work/Edition relationship is preserved, with Editions carrying their
      own identifiers and format
- [ ] A Work page renders real catalogue data end to end
- [ ] Progress and failures are observable while the job runs, not only at the end
- [ ] Records that fail to parse are skipped and reported, never silently dropped
