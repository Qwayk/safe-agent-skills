# Safety model

This tool uses a simple safety model.

## Live calls

- No live Reddit API call happens unless you pass `--live`.
- This includes `auth exchange-code`, `auth refresh`, `auth check --live`, and all live `api` calls.
- `auth exchange-code` and `auth refresh` are live, token-writing steps.

## Reads

- Reads can run with `--live` only.
- Without `--live`, the tool returns a dry-run plan.

## API writes

- Pinned API writes stay dry-run by default.
- To attempt an API write apply, use `--live --apply`.
- Risky or irreversible writes still require their extra gates, but approved write applies require explicit no-snapshot approval after the gates pass and must record the recovery limit.
- A successful Reddit write receipt must not be emitted until the command can save real endpoint-specific before-state or provider backup data first.

## Plan checks

- Plans include an environment fingerprint from public Reddit setup fields (host, auth URLs, redirect URI, OAuth scopes, client id, and user-agent).
- A plan with a different fingerprint is refused on apply, even if the command is otherwise valid.

## Local setup files

- `auth login` can save local OAuth setup state without calling Reddit.
- `auth exchange-code` and `auth refresh` call Reddit and can save tokens locally. Both require `--live`.
- `auth token set`, `auth exchange-code`, and `auth refresh` overwrite local token state without an automatic restore path in this tool.

## Risky writes

- Risky writes also need `--plan-in --yes`.
- This makes you reuse a reviewed plan instead of applying a fresh unchecked command.

## Irreversible writes

- Irreversible writes also need `--ack-irreversible`.

## Rollback model

- Current Reddit write families should be treated as `irreversible_and_clearly_labeled`.
- This includes live API writes plus the local template write helpers such as `jobs run` and `demo write`.
- The tool saves plans and local run history for review, but it does not create provider restore flows, rollback helpers, or before-state snapshots.
- If a write apply is refused, confirm `before_state.status` is `no_snapshot_available` and the receipt records no-snapshot approval, or missing approval refused before provider HTTP.

## Proof

- Write-capable commands save local run folders under `.state/runs/`.
- Plans and refusal outputs can be reviewed later.
