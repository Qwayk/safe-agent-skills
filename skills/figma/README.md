# figma-safe-agent-cli

`figma-safe-agent-cli` is a safe CLI for explicit Figma REST API operations.
It uses a source-of-truth operation inventory, runs reads directly, and keeps provider writes on a plan-first path where live apply needs operation-specific before-state capture or explicit no-snapshot approval.

## For non-technical users: Start here (no coding)

- Start with `docs/use_cases.md` for plain-English examples of what this tool can do.
- Use `docs/onboarding.md` for step-by-step setup.
- Read `docs/safety_model.md` to understand preview, approval, and proof behavior before any write.

Plain-English example requests:
- “Check which parts of the Figma REST API this account can safely use.”
- “Prepare a preview for posting one comment to a file, but do not send it yet.”
- “Tell me which endpoints are enterprise-only or team-gated before I try them.”
- “Show me local proof for what this tool can do today.”

## For technical users: Start here (CLI)

- Use `docs/quickstart.md` for install and first-run commands.
- Use `docs/command_reference.md` for the full CLI surface and flags.

Minimal CLI examples:

```bash
figma-safe-agent-cli auth check
figma-safe-agent-cli operations list --area files
```

## What is live

This tool is customer-ready on the current command and runtime slice:
- `onboarding`
- `auth check`
- `auth token set`
- `auth token status`
- `runs list`
- `runs show`
- `operations list`
- `operations show`
- `operations <area> <op_key>`

The operation set is limited to the official Figma REST API areas and endpoints defined in `src/figma_safe_agent_cli/operation_specs.py`.
Current write applies require explicit no-snapshot approval before Figma token use or provider HTTP when operation-specific before-state capture is not available. Write plans include `before_state.status: no_snapshot_available`, and successful write receipts must record the no-snapshot approval and recovery limit.

## Reality check

Live calls still require real Figma credentials and team/project-level access.
When you do not have a valid token or correct permissions, the tool will return a clear blocked status rather than pretending success.

## Local install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```
