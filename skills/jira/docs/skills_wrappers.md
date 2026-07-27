# Jira agent skill wrapper

The source checkout keeps the tracked wrapper at `skills/jira/SKILL.md`. The published `jira` skill places the same wrapper at top-level `SKILL.md`. It tells an agent to use this tool for Jira Cloud Platform and Jira Software work, begin with a read, inspect the fixed command, and keep writes at the plan stage until the user approves.

It also tells the agent not to use this tool for Jira Service Management, Assets, Operations, Confluence, Jira Data Center or Server, organization administration outside the selected APIs, or arbitrary HTTP requests.

The wrapper is intentionally short. Exact syntax lives in the [command guide](command_reference.md), safety details live in the [safety model](safety_model.md), and all 721 operations live in [API coverage](api_coverage.md).
