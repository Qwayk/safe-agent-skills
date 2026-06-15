# Troubleshooting

When OpenAI stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent inspecting organization, project, model, file, and usage-related data available to the key, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the OpenAI error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Debug HTTP

Use `--verbose` to log HTTP start/end lines to stderr. Hidden secrets are never printed (no Authorization headers, no tokens).

## Debug errors

By default the CLI prints a single JSON error object. Add `--debug` to show Python stack traces when you need extra detail.
