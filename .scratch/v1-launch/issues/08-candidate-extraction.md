# 08 — Candidate extraction

**What to build:** Turning transcripts into reviewable claims. A model reads a Source's
transcript and emits Candidates: a speaker, a Work, the quote that constitutes the
recommendation, its timestamp, and a judgement of what kind of remark it was.

Candidates are never public in any form — no unverified badge, no staging surface a
crawler can reach — per ADR-0003. They exist only to be reviewed in ticket 09.

The extractor must resolve the spoken title to a real Work from the catalogue, which is
the hard part: people say "Sapiens", not a full title and author. A Candidate that cannot
be resolved to a Work is still worth surfacing to a reviewer, but flagged as unresolved
rather than guessed at.

Judgement matters as much as detection. Only positive remarks become Recommendations; the
extractor must distinguish genuine praise from a neutral mention, a criticism, and an
author promoting their own book — the last being the case most likely to be mistaken for
a recommendation.

**Blocked by:** 04 — Open Library ingest; 07 — Transcript acquisition.

**Status:** ready-for-agent

- [ ] Running extraction over a Source produces Candidates with speaker, Work, quote and
      timestamp
- [ ] Each Candidate carries a judgement: positive, neutral, negative or self-promotional
- [ ] Speaker attribution comes from the transcript's speaker labels, not inferred from
      context alone
- [ ] Titles are resolved against catalogue Works; unresolved Candidates are flagged, not dropped
- [ ] Candidates are unreachable from the public site and excluded from sitemaps
- [ ] Re-running extraction on the same Source does not duplicate Candidates
- [ ] Extraction is evaluated against a hand-labelled set of transcripts, with the
      false-positive rate on self-promotional remarks reported specifically
