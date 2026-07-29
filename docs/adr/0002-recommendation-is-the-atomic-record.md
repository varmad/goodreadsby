# Recommendation is the atomic record; lists are views

The site is organised around curated lists, so the obvious schema is a table of lists
with ordered entries. We store the opposite. The atomic record is a Recommendation — one
named person spoke positively about one Work, at a knowable moment, evidenced by a
Source. Lists are queries over those facts, not documents anyone authors.

This is what makes the work compound. Establishing once that a person recommended a book
on a particular episode then feeds that person's page, the Work's page ("recommended by
seven people"), every topical list the Work belongs to, and every ranking of
most-recommended books. Authored lists would make each of those pages separate manual
work.

A Recommendation points at a Work, not an Edition. A Work is the book as people discuss
it; an Edition is one purchasable form of it. Deduplication and counting operate on
Works, so seven people recommending Sapiens is one book and not seven. Affiliate links
and format choice operate on Editions, because only an Edition has an ASIN to link to.
Collapsing the two breaks either counting or purchasing.

## Consequences

- There is no lists table. A "list" is a named query, and adding one is a config change.
- Every Recommendation must resolve to a Work before it can be published, which makes
  Work resolution a required pipeline step rather than an enrichment.
- Ordering within a list is derived (by date, by recommendation count) rather than
  hand-set. Editorial ordering would need a deliberate extension.
