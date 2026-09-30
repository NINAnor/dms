- ALWAYS use docker and docker compose to run any command
- ALWAYS source the `helpers.sh` script, check out the commands in there
- ALWAYS use the development profile
- ALWAYS use `pnmp` to install and handle javascript dependencies
- ALWAYS run `pre-commit`
- ALWAYS make sure the javascript/react code follows eslint/prettier configuration
- PREFER backward compatible changes to APIs
- PREFER adding readonly fields for related fields in the REST API
- PREFER fat models over logic in the views
- ALWAYS use Conventional Commits for commit messages, kept short and meaningful (concise subject line, no filler)

## Agent skills

### Issue tracker

Issues are tracked in ClickUp (Space "IT Utvikling" → Folder "DMS" → List "DMS"). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (root CONTEXT.md + docs/adr/). See `docs/agents/domain.md`.
