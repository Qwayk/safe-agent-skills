# Quickstart

If you want the human path first, start with [What you can do with Threads](use_cases.md), [Connect your Threads account](onboarding.md), and [How this skill stays safe](safety_model.md).

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

Token exchange and local token-file writes need explicit no-snapshot approval when no saved snapshot exists. If you only need reads first, you can use a manually configured `THREADS_API_TOKEN`.

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

If you later choose to apply a write, review the plan first and expect extra approval for no-snapshot actions. Delete actions also need `--yes --ack-irreversible`.
