# goodreadsby

## Agent skills

### Issue tracker

Jira, draft-only — agents never write to Jira; they draft issues into `.scratch/<feature>/` and print Jira-ready text for a human to create. The one exception is the autonomous Sandcastle loop, which lists real Jira issues via the `jira-task` helper in its sandbox and moves each one to In Review once its PR is open — it never closes an issue. See `docs/agents/issue-tracker.md`.

### GitHub

Pull requests only — agents commit locally and never push. The one exception is the autonomous Sandcastle loop, which pushes each iteration's branch and opens a PR via the `gh-pr` helper in its sandbox. See `docs/agents/github.md`.

### Triage labels

The five canonical roles, unchanged: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
