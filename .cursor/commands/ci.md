# ci

Use GitHub CLI (`gh`) to check CI status, view failing CI runs, and examine build error messages.

## Behavior

1. Use `gh` CLI commands to check CI status and view failing runs
2. Examine build error messages from failed CI runs
3. Analyze the errors to understand what's failing
4. Help diagnose and fix issues based on CI error messages
5. If needed, provide guidance on how to fix the issues

## Common Commands

- `gh run list` - List recent workflow runs
- `gh run view <run-id>` - View details of a specific run
- `gh run view <run-id> --log` - View logs from a specific run
- `gh run list --status failure` - List only failed runs
- `gh run watch` - Watch the latest run in real-time

## Workflow

1. Check recent CI runs: `gh run list`
2. Identify failing runs (look for ❌ or failed status)
3. View details of failing runs: `gh run view <run-id>`
4. Examine logs: `gh run view <run-id> --log` or `gh run view <run-id> --log-failed`
5. Analyze error messages to identify the root cause
6. Provide recommendations or fix the issues locally

## Important Notes

- Always check the most recent failing run first
- Look for error messages in the logs, especially from test failures or linting errors
- Compare with local `poetry run poe check:fix` results if available
- If the error is unclear, examine the full log output for context
- Consider checking multiple failed runs if the issue persists across commits

