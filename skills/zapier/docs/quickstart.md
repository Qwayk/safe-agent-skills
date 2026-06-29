# Quickstart

Get a first safe Zapier result by checking credentials and listing apps before asking for any live change.

```bash
cp .env.example .env
qwayk-zapier-safe-agent-cli --output json onboarding
qwayk-zapier-safe-agent-cli --output json auth check
```

Then run one safe read:

```bash
qwayk-zapier-safe-agent-cli --output json partner apps-list
```

If you are deciding what an agent can do next, ask it to inspect:

- `qwayk-zapier-safe-agent-cli partner apps-list`
- `qwayk-zapier-safe-agent-cli partner zaps-list`
- `qwayk-zapier-safe-agent-cli trigger-inbox listTriggerInboxes`
- `qwayk-zapier-safe-agent-cli ai-actions ai-actions-list-ai-actions`

## Prepare a Zap change without applying it

```bash
qwayk-zapier-safe-agent-cli \
  --output json \
  --plan-out zap-plan.json \
  partner post-zaps \
  --body-json '{"title":"Review-only Zap plan","steps":[]}'
```

That command writes a plan and does not create the Zap. After a person reviews the plan, live apply must include the same operation, `--apply`, `--plan-in zap-plan.json`, and the required approval flag.

```bash
qwayk-zapier-safe-agent-cli \
  --output json \
  --apply \
  --plan-in zap-plan.json \
  --ack-no-snapshot \
  --receipt-out zap-receipt.json \
  partner post-zaps \
  --body-json '{"title":"Review-only Zap plan","steps":[]}'
```

Use live apply only with real Zapier credentials, the right scopes, and a body you have reviewed.
