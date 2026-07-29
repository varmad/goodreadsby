# 03 — Deploy the skeleton

**What to build:** The walking skeleton running on real infrastructure at a real URL,
rather than only on a developer machine. Both runtimes from ADR-0004 are deployed — the
public Next.js site and the FastAPI service — with a managed Postgres attached and
incremental static regeneration actually enabled rather than merely configured.

This is the ticket that makes ticket 10's freshness promise measurable, so ISR must be
demonstrably working, not assumed.

**Blocked by:** 02 — Walking skeleton.

**Status:** needs-info

> Held: hosting has not been decided. This ticket cannot be specified for an agent until
> someone chooses the target platform for the two runtimes and the Postgres instance.
> Everything else about it is settled.

- [ ] Public site reachable at a real URL, serving server-rendered pages
- [ ] FastAPI service deployed, with the public site reading from it
- [ ] Managed Postgres attached, with backups configured
- [ ] A page can be revalidated on demand and the change is visible without a full rebuild
- [ ] Secrets held in the platform's secret store, never in the repository
- [ ] Deploys are repeatable from a command or a push, not assembled by hand
