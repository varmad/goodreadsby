# 12 — Retraction

**What to build:** The response path for a published Recommendation that turns out to be
wrong or is disputed — the case where a named person's representative says they never
said it.

A reviewer retracts the Recommendation. It disappears from every public view immediately
and its page returns 410 Gone rather than 404, signalling deliberate removal. The record
itself survives, along with why it was withdrawn, who requested the withdrawal, and who
approved it in the first place.

Retaining the record is the point. Hard-deleting makes the complaint disappear but
destroys the only evidence that we acted in good faith, and hides whether the extractor
has a systematic fault producing the same class of error elsewhere.

**Blocked by:** 09 — Approval queue.

**Status:** ready-for-agent

- [ ] A reviewer can retract a published Recommendation, recording a reason and who requested it
- [ ] The Recommendation vanishes from every public view, including Lists and counts
- [ ] Its page returns 410 Gone
- [ ] The record survives with its original approver and approval time intact
- [ ] Retracted Recommendations are removed from the sitemap
- [ ] Retracted items are excluded from cached and revalidated pages, not merely hidden in
      the template
- [ ] Retractions are reviewable as a set, so a pattern of extractor error is visible
- [ ] The same Candidate cannot be silently re-published by a later extraction run
