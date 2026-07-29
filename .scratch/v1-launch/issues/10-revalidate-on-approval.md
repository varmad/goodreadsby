# 10 — Freshness: revalidate on approval

**What to build:** The wedge, made real and measurable. When a reviewer approves a
Candidate, every public page affected by that new Recommendation is live within seconds —
the Work page, the Recommender's page, the Feed's page and any List the Work now belongs
to — without rebuilding the site.

Per ADR-0004, approval is the moment content goes live, and freshness is measured from
that action. This ticket is what distinguishes the product from a competitor whose corpus
was assembled once and left to age, so the latency needs to be observed rather than
assumed.

**Blocked by:** 03 — Deploy the skeleton; 09 — Approval queue.

**Status:** ready-for-agent

- [ ] Approving a Candidate makes the new Recommendation visible on every affected page
      without a full rebuild
- [ ] The set of pages to refresh is derived from the Recommendation, not hardcoded
- [ ] Time from approval to public visibility is recorded and can be charted over time
- [ ] A failed revalidation is retried and surfaced, and never leaves a page permanently stale
- [ ] Revalidation cost does not grow unacceptably as the corpus grows
- [ ] Demonstrated end to end: approve a Candidate, load the public page, see it there
