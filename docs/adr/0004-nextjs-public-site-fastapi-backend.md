# Next.js renders the public site; FastAPI owns the API and pipeline

Running two language runtimes for one product needs justifying, since a single FastAPI
service with server-rendered templates, or a plain React SPA against the API, would each
be simpler to build and deploy.

The business is entirely dependent on organic search, and its differentiator is that
pages change constantly. That combination rules out both simpler options. A
client-rendered SPA leaves our List and Work pages to be rendered by the crawler, which
indexes slowly and unreliably — a poor bet when search is the only acquisition channel.
Full static generation rules itself out on the other side: once the corpus is large,
rebuilding everything on each new Recommendation takes longer than the freshness we sell.

Next.js with incremental static regeneration resolves both. Pages are server-rendered
HTML, and a new Recommendation revalidates only the pages it touches, within seconds and
without a rebuild. FastAPI keeps the API, the admin surface, the ingestion pipeline and
the approval queue, none of which need to be crawlable and all of which are better served
by Python's data tooling.

## Consequences

- Two runtimes to deploy, monitor and keep in dependency sync. Accepted deliberately.
- The public site is read-only against the API, so the boundary between them stays a
  cache boundary rather than a coupling.
- Revalidation must be triggered on approval, making the approval action the moment
  content goes live. Freshness is measured from that action.
