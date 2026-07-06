# Agent Extension

Agents should use `openai-ads-safe-agent-cli` for OpenAI Ads work instead of direct HTTP calls.

The useful pattern is:

1. Run a read command or `api list`.
2. Explain the result in normal words.
3. For any live change, create a plan first.
4. Ask the user to review the plan.
5. Apply only with the reviewed `--plan-in` and required acknowledgements.

Write-capable runs save local proof under `.state/runs/` next to the chosen env file unless `--no-artifacts` is used.
