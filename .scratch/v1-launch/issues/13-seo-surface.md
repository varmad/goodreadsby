# 13 — SEO surface

**What to build:** The machinery that lets search engines find, understand and correctly
attribute the site — the only acquisition channel the product has.

A sitemap that reflects the live corpus rather than a stale snapshot, structured data
describing Works and Lists so results can render richly, canonical URLs so the same Work
reachable by several paths is not treated as duplicate content, and social preview
metadata so shared links render properly.

Structured data must describe only what we actually assert: that a named person
recommended a book, evidenced by a source. It must not be shaped to imply ratings or
reviews we do not have.

**Blocked by:** 11 — Lists as named views.

**Status:** ready-for-agent

- [ ] A dynamic sitemap covers Works, Recommenders, Feeds and Lists, and excludes anything
      retracted or unapproved
- [ ] Work and List pages emit valid structured data that passes Google's Rich Results Test
- [ ] Every page declares a canonical URL
- [ ] Social preview metadata renders correctly when a page is shared
- [ ] Admin surfaces and the Candidate queue are excluded from crawling
- [ ] Structured data claims nothing beyond attributed recommendations — no invented
      ratings or review counts
- [ ] Sitemap stays current as new Recommendations are approved, without a manual step
