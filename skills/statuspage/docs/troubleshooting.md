# Troubleshooting

When Statuspage stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing pages, components, incidents, subscribers, and status updates, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Statuspage error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Common issues

### Missing base URL

- Make sure your `.env` contains `STATUSPAGE_BASE_URL=https://status.somevendor.com`.

### HTTP errors / invalid JSON

- Use `--verbose` for HTTP logs (to stderr).
- Use `--debug` for stack traces.
