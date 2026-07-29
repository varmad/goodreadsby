# Amazon is a link target, not a data source

Our revenue comes from Amazon affiliate links, so the obvious move is to build the
catalogue on Amazon's Product Advertising API. We deliberately do not. PA-API requires
three qualifying sales within 180 days to gain access, and revokes access after a
consecutive 30-day period without qualified sales — so a new site cannot get in, and an
established one loses its catalogue precisely when sales dip. Depending on it would
couple our ability to render pages to our recent revenue.

Instead the catalogue comes from Open Library's free monthly bulk dumps, ingested into
our own database. Open Library natively distinguishes Works from Editions, which is the
split we already need (see ADR-0002), and self-hosting means no rate limits, no caching
restrictions, and no third-party uptime in our critical path. Amazon appears only at the
moment we construct a purchase URL.

## Consequences

- Affiliate links are built from stored identifiers rather than fetched, so we never call
  Amazon to render a page. The assumption that a print Edition's ASIN equals its ISBN-10
  was validated against a real sample and **holds** — see
  `docs/research/isbn10-to-asin-validation.md` (SCRUM-1): 36/36 resolvable print editions
  hit, across three locales, all print formats, large-trade/academic/small-press
  publishers, and every decade from the 1920s to 2021. Build links as
  `https://{locale-host}/dp/{ISBN-10}?tag={tag}`, converting a stored `978…` ISBN-13 to its
  ISBN-10 when needed.
- The assumption holds **only for print Editions**, with three exceptions where no
  ISBN-derived link exists — gate link construction accordingly:
  - **Kindle/ebook** and **audiobook/Audible** Editions use `B0…` ASINs, not ISBNs. Never
    build a link from an ebook or audiobook Edition; only print Editions get a buy link.
  - **979-prefix ISBN-13s have no ISBN-10** (the 10-digit form only ever encoded `978`
    titles); Amazon assigns those a `B0…` ASIN. If a print Edition's only identifier is a
    `979…` ISBN-13, render no buy link (or a non-ISBN fallback). This category grows as
    `979-8` becomes the KDP/self-published default.
- A given ISBN-10 is only guaranteed to resolve on the Amazon locale that carried that
  Edition; the `/dp/{isbn10}` path itself is locale-portable but availability is not.
- We cannot show live Amazon prices or stock. This is a deliberate loss.
- Open Library coverage is patchy for very new and niche titles. Those gaps are filled by
  hand or from a secondary source, not by adopting PA-API.
- Do not "fix" this by adding PA-API when someone notices the missing prices.
