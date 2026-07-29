# 09 — Approval queue

**What to build:** The human gate that ADR-0003 makes mandatory, and the core working
surface of the whole product. A reviewer opens a queue of Candidates and, for each one,
plays the audio at the cited moment, reads the quote in context, and either approves it —
creating a published Recommendation — or rejects it.

Review time is the throughput ceiling of the entire business, so ergonomics are the
feature, not a polish pass. A reviewer should be able to work through a queue at pace
using the keyboard, without waiting on page loads between decisions.

Only positive judgements become Recommendations. Neutral, negative and self-promotional
Candidates are discarded at this gate rather than stored. Confidence from the extractor
may order the queue; it may never bypass it.

Every approval must record who made it and when, because ticket 12 depends on being able
to answer "how did this get published?" months later.

**Blocked by:** 08 — Candidate extraction.

**Status:** ready-for-agent

- [ ] A reviewer sees a queue of pending Candidates with the highest-value ones first
- [ ] Each Candidate shows the quote, the speaker, the resolved Work and the surrounding
      transcript context
- [ ] Audio can be played from the cited moment without leaving the queue
- [ ] Approving publishes a Recommendation; rejecting discards the Candidate
- [ ] A reviewer can correct the speaker or the resolved Work before approving
- [ ] Approval records the reviewer's identity and the time
- [ ] The queue is reachable only by authenticated staff and is never indexed
- [ ] A reviewer can move through consecutive decisions by keyboard alone
- [ ] No path exists that publishes a Recommendation without an explicit human approval
