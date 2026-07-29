# ISBN-10 → Amazon ASIN validation (SCRUM-1)

**Question.** ADR-0001 commits us to building Amazon affiliate links from stored
identifiers instead of calling the Product Advertising API. That rests on one assumption:
_an Amazon product URL built from a print Edition's ISBN-10 reliably resolves to that
Edition's Amazon listing_ (i.e. Amazon's ASIN for a print book equals its ISBN-10). This
document tests that assumption against a real sample.

**Verdict: the assumption holds for print Editions, with stated exceptions** for Kindle,
audiobook, and 979-prefix editions. ADR-0001 has been amended accordingly.

## Method

Each sample is a real edition drawn from Open Library — our only catalogue source
(ADR-0001) — so a failure means "Amazon does not map this real ISBN-10", not "we invented
an ISBN". For each ISBN-10 we requested `https://{locale}/dp/{isbn10}` and recorded, from
the returned page:

- whether it is a valid **Books** product page (vs. a 404 / robot page);
- the **canonical URL** and **ASIN**;
- the **ISBN-13** shown in the page title, checked against `convert(isbn10)`.

A sample is a **HIT** when the page is a real book, `ASIN == isbn10`, the canonical URL is
`/dp/{isbn10}`, and (where shown) the title's ISBN-13 equals the converted ISBN-10 — i.e.
the link an affiliate URL would use lands on the intended Edition. The rule is
identity-based, so it does not depend on us guessing which book an ISBN belongs to: a
matching ASIN + ISBN-13 on a real Books page _is_ the proof.

Sample design deliberately spread across the dimensions the ticket named:

- **Locales:** `amazon.com` (US), `amazon.co.uk` (UK), `amazon.de` (DE).
- **Formats:** mass-market, trade paperback, hardcover (plus Kindle & audiobook, below).
- **Publisher tiers:** large trade (Penguin RH, HarperCollins, Scribner, Scholastic,
  Putnam, Bloomsbury, Faber, Signet, Diogenes…), academic (MIT Press ×2, University of
  Chicago Press, Oxford UP), small press (Graywolf).
- **Decades:** first-publication years from the 1920s through 2021.

**Sample size.** 43 distinct print ISBN-10s were queried plus the Kindle / 979 / audiobook
cases (~46 editions examined, "roughly 50" per the ticket). 36 print fetches returned a
usable page; **all 36 were hits (100%)**. 7 print fetches failed as HTTP 500 from the
fetch proxy itself — not Amazon 404s. Each of those 7 is a real, in-print edition with a
valid ISBN-10 check digit (e.g. _The Road_ 0307476316, _Klara and the Sun_ US 0593318188,
_The Kite Runner_ 1594631840), so they are recorded as **inconclusive (tooling)** and
excluded from the denominator rather than counted as misses. No fetch returned an Amazon
"page not found" or a wrong-book page.

## Results — print Editions

100% hit across every cell. Representative confirmed hits:

| Book | ISBN-10 | Locale | Format / publisher | ~Decade | ASIN==ISBN-10 |
|---|---|---|---|---|---|
| Nineteen Eighty-Four | 0451524934 | .com | mass-market / Signet | 1949 | ✓ |
| The Great Gatsby | 0743273567 | .com | trade pb / Scribner | 1925 | ✓ |
| The Catcher in the Rye | 0316769177 | .com | pb / Little, Brown | 1951 | ✓ |
| Dune | 0441172717 | .com | mass-market / Ace | 1965 | ✓ |
| The Hitchhiker's Guide | 0345391802 | .com | mass-market / Del Rey | 1979 | ✓ |
| The Handmaid's Tale | 038549081X | .com | trade pb / Anchor | 1985 | ✓ |
| Beloved | 1400033411 | .com | trade pb / Vintage | 1987 | ✓ |
| SICP (paperback) | 0262510871 | .com | pb / MIT Press (academic) | 1996 | ✓ |
| SICP (hardcover) | 0262011530 | .com | hc / MIT Press (academic) | 1996 | ✓ |
| Structure of Scientific Revolutions | 0226458121 | .com | pb / U. Chicago (academic) | 1962 | ✓ |
| Marx: A Very Short Introduction | 0198821077 | .com | pb / Oxford UP (academic) | 1980 | ✓ |
| Citizen: An American Lyric | 1555976905 | .com | pb / Graywolf (small press) | 2014 | ✓ |
| The Hunger Games | 0439023483 | .com | pb / Scholastic | 2008 | ✓ |
| Gone Girl | 030758836X | .com | trade pb / Broadway | 2012 | ✓ |
| Where the Crawdads Sing | 0735219095 | .com | hc / Putnam | 2018 | ✓ |
| Project Hail Mary | 0593135202 | .com | hc / Ballantine | 2021 | ✓ |
| Thinking, Fast and Slow | 0374533555 | .com | pb / FSG (nonfiction) | 2011 | ✓ |
| Harry Potter (Philosopher's Stone) | 0747532699 | .co.uk | hc / Bloomsbury | 1997 | ✓ |
| Harry Potter (Philosopher's Stone) | 1408855658 | .co.uk | pb / Bloomsbury | 2014 | ✓ |
| Normal People | 0571334652 | .co.uk | hc / Faber | 2018 | ✓ |
| Klara and the Sun | 057136487X | .co.uk | hc / Faber | 2021 | ✓ |
| Project Hail Mary | 1529157463 | .co.uk | pb / Del Rey UK | 2021 | ✓ |
| Citizen: An American Lyric | 0141981776 | .co.uk | pb / Penguin | 2014 | ✓ |
| Pride and Prejudice | 0141439513 | .co.uk | pb / Penguin Classics | 1813 | ✓ |
| Meet the Oceans | 1526603632 | .co.uk | hc / Bloomsbury (children's) | 2020 | ✓ |
| Der Vorleser | 3257229534 | .de | pb / Diogenes | 1995 | ✓ |

(Plus: Don Quixote 0060934344, Educated 0399590501, Brave New World 0060850523, Ender's
Game 0812550706, To Kill a Mockingbird 0446310786, The Da Vinci Code 0307474275, Twilight
0316015849, The Alchemist 0061122416, The Fault in Our Stars 0525478817, The Grapes of
Wrath 0143039431 — all `.com`, all hits.)

**No failures by format, decade, publisher tier, or locale.** The mapping worked
identically for a 1925 Scribner classic, a 1962 university-press monograph, a 2014
small-press poetry collection, and a 2021 trade hardcover, and on all three locales tested.

### Two harmless metadata quirks (still hits)

- **EAN instead of ISBN-13 in the title.** _The Structure of Scientific Revolutions_
  (0226458121) shows `8601404381294` (an Amazon EAN) in its title rather than
  `9780226458120`. The ASIN still equals the ISBN-10 and `/dp/0226458121` resolves, so the
  affiliate link works. Do **not** rely on scraping the title's number to confirm a link;
  rely on the ISBN-10 you already store.
- **ISBN-10 (not ISBN-13) in the title.** The 2014 Bloomsbury Harry Potter (1408855658)
  and _Meet the Oceans_ (1526603632) show the ISBN-10 in the title. Again ASIN == ISBN-10,
  link resolves. Both quirks are display-only; neither affects link construction.

## Failure categories (the "exceptions")

These are the cases where an ISBN-derived URL does **not** reach the right listing. All are
about the _kind_ of Edition, not the book:

1. **Kindle / ebook Editions.** Amazon identifies ebooks by a `B0…` ASIN, not an ISBN, and
   the Kindle page carries no ISBN at all. Confirmed: _Project Hail Mary_ Kindle is
   `B08FHBV4ZX` (valid product, no ISBN shown). A stored print ISBN-10 will never resolve
   to the Kindle listing — it resolves to the _print_ listing (from which Amazon's own
   format switcher offers the Kindle edition).

2. **Audiobook / Audible Editions.** Same mechanism — Audible titles use `B0…` ASINs on a
   separate catalogue. Open Library's audiobook Editions almost never carry the Amazon /
   Audible ASIN, so there is nothing to build a link from.

3. **979-prefix editions (growing).** An ISBN-13 beginning `979` has **no ISBN-10
   equivalent** — the 10-digit form only ever encoded `978` titles. Amazon assigns such a
   print book a `B0…` ASIN instead. Example: the independently-published paperback
   _Stupidhead_ (ISBN 979-8336233988) has ASIN `B0DDKC8FXC`. `979` blocks (`979-8` in
   particular) are now the default for KDP / self-published print, so this category grows
   over time. There is no ISBN-10 to convert; `/dp/{isbn10}` cannot be constructed.

### One behaviour to watch (not observed here)

Amazon sometimes **redirects an out-of-print ISBN-10 to a different in-print Edition of the
same Work**. None of the 36 hits did this, but at ingest scale it can send a user to a
different Edition than the one recommended. It degrades link _precision_, not link
validity, and is acceptable for affiliate purposes; worth monitoring, not blocking on.

## Implications for the build

- **Build links only for print Editions.** Gate link construction on
  `physical_format ∈ {hardcover, paperback, mass-market, …}`. Never derive an Amazon link
  from an ebook or audiobook Edition's identifier.
- **Link shape:** `https://{locale-host}/dp/{ISBN-10}?tag={affiliate-tag}`. When only an
  ISBN-13 is stored, convert `978…` → ISBN-10; if the ISBN-13 is `979…`, **there is no
  ISBN-10** → render no buy link for that Edition (or fall back to a non-ISBN search link).
- **Locale:** the `/dp/{isbn10}` path is locale-portable (verified on .com/.co.uk/.de), but
  a given ISBN-10 is only guaranteed to resolve on the locale that carried that Edition.
  Default to the locale matching the Edition's market and/or the visitor; do not assume one
  ISBN-10 resolves everywhere.
- **Trust the stored ISBN-10, not scraped page metadata** — Amazon's title field sometimes
  shows an EAN or the ISBN-10 rather than the ISBN-13.

## Limitations

- 3 locales, ~46 editions — enough to establish the pattern and its exceptions, not a
  census. The failure categories (Kindle / audiobook / 979) are structural, not
  sample-size dependent.
- 7 print fetches were lost to fetch-proxy HTTP 500s (a tooling limit of this run, not an
  Amazon result); all were real in-print editions and are excluded rather than scored.
- Not tested: extreme long-tail / non-Latin-market editions, and Amazon's out-of-print
  redirect behaviour at scale (flagged above as a monitor-only item).
