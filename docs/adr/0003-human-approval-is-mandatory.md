# Every Candidate requires human approval before publication

Recommendations are extracted from transcripts by a model, which makes full automation
tempting: the corpus is the product, volume is the wedge, and the extractor is the only
thing standing between us and thousands of pages. We still require a human to approve
every Candidate before it becomes a published Recommendation.

The reason is asymmetric risk. A published Recommendation is a factual claim that a real,
named person endorsed a real book. Getting it wrong means we have fabricated an
endorsement and attributed it to someone who can object — and the extractor's most likely
errors are exactly the ones that produce this: attributing a host's line to the guest,
reading a neutral mention as praise, or treating an author promoting their own book as a
recommendation. No confidence threshold makes that class of error acceptable, because the
cost is not a bad page but a false statement about a person.

## Consequences

- Human review time is the throughput ceiling of the entire business. Pipeline capacity
  beyond that ceiling is wasted, so invest in review tooling (clip playback, keyboard
  approval) before extraction volume.
- Candidates are never public in any form — no "unverified" badge, no staging surface
  that search engines can reach.
- Confidence scores may order the review queue. They may not bypass it.
- Only positive judgements are stored; neutral, negative and self-promotional Candidates
  are discarded at this gate rather than recorded.
