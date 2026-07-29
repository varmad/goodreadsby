# Issue tracker: Jira (draft-only, except inside the Sandcastle sandbox)

Issues for this repo are tracked in **Jira** (project `SCRUM` on
`srinivasavarmad.atlassian.net`). Interactive agents do **not** have write access.

## The rule

Never call a Jira CLI, MCP server, or REST API. Never claim an issue was created,
updated, commented on, or transitioned. Agents produce **drafts**; the human creates
the real Jira issues.

## The one exception: the Sandcastle loop

The autonomous loop in `.sandcastle/` **does** write to Jira, via the `jira-task`
helper baked into its sandbox image. It is the only agent context allowed to:

- `jira-task list` — open tasks (status in `JIRA_WORK_STATUSES`) as JSON
- `jira-task view <KEY>` — one task, with comments and `blocks` links
- `jira-task comment <KEY> <msg>` — record a blocker without changing status
- `jira-task review <KEY> [msg]` — comment, then transition to `JIRA_REVIEW_STATUS`
- `jira-task close <KEY> [msg]` — comment, then transition to Done

The loop **never closes an issue**. Its implement agent only comments; the publish step
runs `jira-task review` once the pull request exists, moving the issue to **In Review**
with the PR link attached. Closing is a human decision, made after the PR merges — see
`github.md`. `jira-task close` remains available for a human driving the helper by hand.

The review status must not appear in `JIRA_WORK_STATUSES`, or `jira-task list` will hand
the same issue back on the next iteration.

The helper lives at `.sandcastle/jira-task` and reads `JIRA_*` credentials from
`.sandcastle/.env`. Nothing outside that sandbox may use it. If you are reading this
in an interactive session, the draft-only rule above still applies to you.

## When a skill says "publish to the issue tracker"

Do both of these:

1. Write the issue as a markdown file at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`,
   numbered from `01` — one file per ticket, never a single combined tickets file.
2. Print the drafted issue(s) in the conversation in Jira-ready form: a one-line
   **Summary**, then a **Description** body, then the triage role as a label line.

The human copies them into Jira. Report it as "drafted N issues" — not "created N issues".

## When a skill says "fetch the relevant ticket"

Read the file under `.scratch/`. If the user references a Jira key (e.g. `GBY-123`)
that has no local file, ask them to paste the issue text — do not guess at its contents
and do not try to fetch it.

## Where specs live

Specs (you may know a spec as a PRD) live in this repo, not in Jira or Confluence:
`.scratch/<feature-slug>/spec.md`.

## Triage state

Recorded as a `Status:` line near the top of each `.scratch/` issue file, using the
role strings in `triage-labels.md`. When drafting for Jira, surface the same string as
a label so the human can apply it.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.scratch/<effort>/map.md` — the Notes / Decisions-so-far / Fog body.
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the
  question in the body. A `Type:` line records the ticket type
  (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every
  file it lists is `resolved`.
- **Frontier**: scan `.scratch/<effort>/issues/` for files that are open, unblocked, and
  unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then
  append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.

## Changing this later

Once Jira tooling is available (a `jira`/`acli` CLI, a Jira MCP server, or an API token),
edit this file to describe the write path — the Jira instance URL, the project key, and the
exact command agents should run. The skills read this file, so no re-setup is needed.
