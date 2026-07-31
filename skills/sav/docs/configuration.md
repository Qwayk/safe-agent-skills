# Configuration

## Environment inputs

```text
SAV_API_KEY=
SAV_TIMEOUT_S=30
```

- `SAV_API_KEY` is required for reads and all apply writes.
- `SAV_TIMEOUT_S` defaults to `30` seconds when omitted or empty.

## CLI-level overrides

You can always override timeout per command with:

```bash
sav --output json --timeout-s 60 domains active
```

Timeout values must be finite and greater than `0` in both env and CLI mode.

## Files and permissions

Default state is written under `<env-file parent>/.state`:

- `.state/plans/` for plan JSON (mode `0600`, atomic write)
- `.state/receipts/` for receipt JSON (mode `0600`, atomic write)
- `.state/keys/` for plan signing key (mode `0600`, random)
- `.state/secrets/` is safe to use for temporary transfer secrets as a local helper location.

All state directories must be `0700`.
Custom `--plan-out` and `--receipt-out` paths must remain under the env-file parent and use a private mode-`0700` parent directory.
Transfer-code input must be a regular mode-`0600` file in a non-symlink mode-`0700` parent. The CLI opens it without following a file symlink, checks that same open descriptor, reads one non-empty line, and does not read the secret again during apply.
