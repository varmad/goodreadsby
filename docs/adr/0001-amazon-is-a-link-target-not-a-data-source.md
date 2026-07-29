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
  Amazon to render a page. Validate the assumption that a print Edition's ASIN equals its
  ISBN-10 against a real sample before relying on it.
- We cannot show live Amazon prices or stock. This is a deliberate loss.
- Open Library coverage is patchy for very new and niche titles. Those gaps are filled by
  hand or from a secondary source, not by adopting PA-API.
- Do not "fix" this by adding PA-API when someone notices the missing prices.
