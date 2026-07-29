# 14 — Newsletter capture

**What to build:** The retention layer, and the only audience the product owns. A visitor
gives their email address on any public page and confirms it, joining a list that will
receive what's been recommended recently.

This is the counterweight to depending entirely on search: an algorithm change can take
the traffic, but not the list. There are no user accounts in v1 — an email address is the
whole of the relationship.

This ticket delivers capture and confirmation only. Composing and sending the weekly
edition is out of scope.

**Blocked by:** 02 — Walking skeleton.

**Status:** ready-for-agent

- [ ] A signup form appears on public pages and submits without a full page reload
- [ ] Subscription requires confirming the address before it is considered active
- [ ] Every email carries a working one-click unsubscribe
- [ ] Duplicate signups are handled without error and without re-sending confirmation endlessly
- [ ] The form resists automated submission
- [ ] Consent, its timestamp and its source page are recorded
- [ ] Stored addresses are treated as personal data, with a documented deletion path
