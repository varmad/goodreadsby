# 01 — Validate the ISBN-10 to ASIN assumption

**What to build:** No code. Establish whether an Amazon product URL built from an
Edition's ISBN-10 reliably resolves to that Edition's Amazon listing. ADR-0001 commits us
to constructing affiliate links from stored identifiers rather than calling Amazon's
Product Advertising API, and that decision rests entirely on this holding true.

Sample roughly 50 real books deliberately spread across formats (hardcover, paperback,
mass-market), publishers (large trade, academic, small press), publication decades, and
at least two Amazon locales. Record the hit rate and characterise the failures — whether
they cluster by format, age, region or publisher.

Write up the finding and, if the assumption does not hold broadly, amend ADR-0001 with
what actually works instead.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] At least 50 ISBN-10s sampled across formats, publishers, decades and 2+ locales
- [ ] Hit rate recorded, with failures characterised by category rather than just counted
- [ ] Behaviour for Kindle and audiobook editions specifically documented, since these are
      the formats least likely to carry an ISBN-derived identifier
- [ ] A clear verdict: the assumption holds, holds with stated exceptions, or fails
- [ ] ADR-0001 amended if the verdict is anything other than "holds"
