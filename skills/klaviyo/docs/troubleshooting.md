# Troubleshooting

When Klaviyo stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing profiles, lists, segments, campaigns, flows, and email performance, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Klaviyo error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## `Missing KLAVIYO_API_BASE_URL`

- Check `.env` has `KLAVIYO_API_BASE_URL`.
- Run `klaviyo-safe-agent-cli onboarding` to rebuild `.env` from `.env.example`.

## `auth check` says API key is missing

- Add `KLAVIYO_API_KEY=<your private key>` to `.env`.
- Re-run: `klaviyo-safe-agent-cli auth check`.

## HTTP 401 / 403 during live calls

- Check the API key in `.env`.
- Confirm the key has access to the requested method and account.

## Safety refusal before apply

- Add `--live` for real HTTP calls.
- Add `--plan-in` for high-impact operations.
- Add `--yes` for high-impact operations with destructive risk.
- If the refusal says before-state support is missing, that is expected in the current Wave 2 safety state; no Klaviyo write was sent.
- For missing required inputs, pass values with `--path`, `--query`, or JSON flags.

## Run history and artifact paths

- If a command is write-capable, it writes artifacts in `.state/runs/<run_id>/`.
- Use `runs list` and `runs show --run-id <id>` to review history.
- Keep `.state/` private in local use.
