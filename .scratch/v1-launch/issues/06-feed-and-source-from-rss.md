# 06 — Feed and Source from RSS

**What to build:** The monitoring surface that the freshness wedge depends on. An
operator registers a Feed — a podcast, channel or interview series — and the system polls
it, creating a Source for each newly published episode. A Feed page lists the Sources
we've seen from it.

Feed is a first-class entity, deliberately orthogonal to Recommender: one Feed hosts many
Recommenders, and one Recommender appears across many Feeds. Nothing here attributes
anything to a person yet; that begins in ticket 08.

No transcripts and no extraction in this slice. The deliverable is that new episodes
reliably become Sources shortly after they are published.

**Blocked by:** 02 — Walking skeleton.

**Status:** ready-for-agent

- [ ] An operator can register a Feed and see it begin producing Sources
- [ ] Polling runs on a schedule without manual intervention
- [ ] Re-polling an unchanged Feed creates no duplicate Sources
- [ ] A Source records its publication date, its title, and where its audio lives
- [ ] A Feed page lists its Sources, most recent first
- [ ] A malformed or unreachable Feed is reported and retried, and does not stall other Feeds
- [ ] Time from episode publication to Source existing is observable
