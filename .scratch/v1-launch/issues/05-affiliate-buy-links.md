# 05 — Affiliate buy links on Editions

**What to build:** The first revenue-capable surface. A Work page offers its Editions by
format — paperback, hardcover, Kindle, audiobook — and each one links out to Amazon with
our Associates tag attached, so a purchase is attributed to us.

Links are constructed from identifiers we already store, never fetched from Amazon, per
ADR-0001. Ticket 01's findings determine which formats can be linked this way and which
cannot; formats that fail validation must degrade gracefully rather than emitting a
broken link.

Per the affiliate-locale decision, Amazon US is the only enrolled programme for now, but
link construction should treat locale as a parameter rather than hardcoding the domain
and tag, so adding OneLink later is configuration and not a rewrite.

**Blocked by:** 01 — Validate ISBN-10 to ASIN; 04 — Open Library ingest.

**Status:** ready-for-agent

- [ ] A Work page lists its available Editions grouped by format
- [ ] Each linkable Edition produces a working Amazon URL carrying the Associates tag
- [ ] Locale and tag are configuration, not literals embedded at each call site
- [ ] Formats that ticket 01 showed cannot be linked from a stored identifier are either
      omitted or shown without a buy link — never rendered as a dead link
- [ ] Outbound links carry the disclosure and link attributes the Associates programme
      requires
- [ ] A Work with no linkable Edition still renders as a valid page
