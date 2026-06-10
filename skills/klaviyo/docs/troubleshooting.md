# Troubleshooting

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
