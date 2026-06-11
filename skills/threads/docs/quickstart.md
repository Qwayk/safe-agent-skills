# Quickstart

If you want the simplest setup steps, read `docs/onboarding.md`.

This page is the short technical path.

1. Install in a virtual environment.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Create `.env` from `.env.example`, then fill the Threads app settings.

3. Build the OAuth URL and review the token exchange plan.

```bash
threads-api-tool --output json auth authorize-url --scope threads_basic
threads-api-tool --output json --plan-out /tmp/threads-auth.plan.json auth code exchange --code <authorization_code>
```

The current apply attempt requires explicit no-snapshot approval before token exchange or local token-file writes. Use a manually configured `THREADS_API_TOKEN` for reads when no saved snapshot is available for auth writes.

4. Confirm the CLI works.

```bash
threads-api-tool --output json --version
threads-api-tool --output json auth token status
threads-api-tool --output json auth check
threads-api-tool --output json profiles me
```

5. For writes, review a dry-run plan first.

```bash
threads-api-tool --output json --plan-out /tmp/threads.plan.json posts create-text --threads-user-id <id> --text "Draft"
```
