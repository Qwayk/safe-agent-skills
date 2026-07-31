# Troubleshooting

## Auth and config

- `ValidationError: Missing configuration: PORKBUN_API_KEY`
  → Fill `.env` with the key and secret.
- Wrong host mode:
  `PORKBUN_API_HOST` must be `default` or `ipv4`.
- `403` or permission errors:
  confirm the API key has the matching Porkbun permission.

## Command usage

- Use exact commands from `docs/command_reference.md`.
- Commands with `--input` require a path to a JSON object file. Inline JSON is rejected.
- Use `--output json` while validating.

## Write flow blocks

- If write returns "approval required", include:
  - `--plan-out` (first run) or `--plan-in` (apply)
  - `--apply` for execution
  - required `--ack-*` flags
  - `--yes` for apply paths
- If a before-state check fails, use `--ack-no-snapshot` with a clear reason.
- If apply says the plan signature or signing key is invalid, return to the same working directory and `.state` used to create the plan. Do not edit and rehash the plan; create a fresh plan if needed.
- If billable apply reports cost drift, stop and review the fresh quote before creating a new plan.
- If the CLI reports a file role collision, give every active plan, receipt, and secret output its own path. None may point to the environment file, JSON `--input`, or `--plan-in`, even through a relative, absolute, `..`, symbolic-link, or existing-file alias.

## Secret output

- If a command says secret-bearing, use:
  `--ack-secret --secret-out ./secrets/result.json`
- Do not request or display the full secret output in normal text.
- A directory, symbolic link, unwritable path, or unsafe target is refused before Porkbun is called.

## Invite status

Do not pass the invite token as `--token`. Save `{"token":"..."}` in a private JSON file and use:
`porkbun account get-account-invite-status --input ./invite-status.json`

## Redirect error

`HTTP_REDIRECT` means Porkbun returned `3xx`. The tool does not follow it because custom API headers must never be forwarded to another location.
