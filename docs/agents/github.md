# GitHub: one branch, one pull request, per issue

Code reaches GitHub through **pull requests only**. Nothing pushes to `main` directly.

## The rule

Interactive agents do not push and do not open pull requests. Commit locally, and let
the human push. This mirrors the draft-only rule in `issue-tracker.md`: never claim a
branch was pushed or a PR opened.

## The one exception: the Sandcastle loop

The autonomous loop in `.sandcastle/` publishes its own work. Each iteration is:

1. **Implement** — one issue, on branch `sandcastle/sequential-reviewer/<timestamp>`.
2. **Review** — a second agent refines the same branch.
3. **Publish** — `main.mts` runs the `gh-pr` helper in the sandbox, which pushes the
   branch and opens a PR against `PR_BASE_BRANCH` (default `main`).

Publish is a plain command, not an agent, so the PR always contains the reviewed code
and each issue gets exactly one PR. Both prompt files forbid the agents from pushing
themselves.

If the branch's commit messages name a `SCRUM-<n>` key, `gh-pr` links the Jira issue in
the PR body, comments the PR URL onto the issue, and moves it to `JIRA_REVIEW_STATUS`
(default **In Review**). The issue is never closed by the loop — that happens when a
human merges the PR. This is also what stops the next iteration from picking the same
issue up, so the commit messages must carry the key; the implement prompt requires it.

A failed publish aborts the whole run rather than continuing — the usual cause is a bad
token or a missing remote, which would repeat every iteration. The commits are safe on
their local branch; fix the cause and re-run to publish them.

## Configuration

Set in `.sandcastle/.env` (see `.env.example`):

| Variable | Required | Meaning |
| --- | --- | --- |
| `GH_TOKEN` | yes | PAT with Contents and Pull requests read/write on this repo |
| `GITHUB_REPO` | no | `owner/name`; defaults to the `origin` remote |
| `PR_BASE_BRANCH` | no | PR target branch; defaults to `main` |
| `PR_DRAFT` | no | `1` opens PRs as drafts |
| `JIRA_REVIEW_STATUS` | no | status the issue moves to; defaults to `In Review` |

The token is passed to `git push` through a one-shot credential helper, so it never
lands in a remote URL, the process list, or `.git/config`.

## Prerequisites

The loop cannot publish until the repo has a GitHub `origin` and a `main` branch on it.
`gh-pr` fails loudly if either is missing.
