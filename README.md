# goodreadsby

Who recommended what, when they said it, and always the evidence. See
[`CONTEXT.md`](CONTEXT.md) for the domain language and [`docs/adr/`](docs/adr) for
the decisions.

## Walking skeleton (SCRUM-2)

The thinnest complete path through every layer: a visitor opens a Work page and
sees the book, who recommended it, when they said it, and a link to the exact
moment in the Source. Data is seeded by hand — no ingestion, extraction or
approval queue yet.

### Layout

- `api/` — FastAPI service + SQLAlchemy models on Postgres, and the seed command
  (ADR-0004). Domain rules live in pure, framework-free modules under
  `api/app/domain/` so they are unit-testable without a database.
- `web/` — Next.js public site. Work pages are **server-rendered** (ADR-0004).
- `docker-compose.yml` — local Postgres.

A Recommendation references a **Work**, not an Edition (ADR-0002). It records both
`said_on` (when it was said) and `ingested_at` (when we recorded it); the presenter
only ever exposes `said_on` to a reader.

### Run it

```sh
cp .env.example .env
make db-up                 # start Postgres
cd api && pip install -e '.[dev]' && cd ..
make seed                  # rebuild data from empty (idempotent)
make api                   # FastAPI on :8000
make web                   # Next.js on :3000  (needs: cd web && npm install)
```

Then open <http://localhost:3000/works/sapiens> — a Work with two Recommendations.

### Test

```sh
make api-test              # domain unit tests (stdlib only, no DB needed)
cd web && npm run typecheck && npm run build
```

### Verified in this change

- `api`: 16 domain unit tests pass; all modules byte-compile. The tests cover the
  rules that carry the acceptance criteria — `ingested_at` never reaches a reader,
  Source deep-linking, and that a Work shows all of its Recommendations.
- `web`: `tsc --noEmit` passes and `next build` succeeds, with `/works/[id]`
  reported as dynamic (server-rendered on demand).
- Not run in this sandbox (no Postgres/pip available here): the live FastAPI +
  Postgres integration and the seed command against a real database. Provisioning
  real infrastructure is SCRUM-3.
