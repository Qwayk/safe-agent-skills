# How an agent should use the Twilio skill

The tracked `twilio` skill wrapper tells an agent when to choose this CLI and how to keep Twilio work inside its fixed command and approval rules.

For credential-free checks, route to the fixed local commands in [local voice and webhook checks](local_contracts.md). Keep their strict `wss://`/TwiML and documented WebSocket limits intact; webhook signature checks use an environment-only Auth Token and raw request body, and Agent Connect is local SDK/middleware metadata only.

## Use it for

Use the skill when the user wants to read, review, prepare, or change supported Twilio communications resources. Examples include message and call status, usage, phone numbers, messaging services, Verify configuration, Conversations, Studio, Serverless, TaskRouter, routing, identity, and account resources.

The safest first action is a local auth check followed by the fixed account read:

```bash
qwayk-twilio-safe-agent-cli auth check
qwayk-twilio-safe-agent-cli api-v2010 fetch-account \
  --input-json examples/inputs/fetch-account.json
```

## Do not use it for

Do not use this skill for SendGrid, Segment, Console browser automation, webhook hosting, client-SDK setup, or TwiML as an arbitrary execution language. Do not replace a missing command with `curl`, a raw URL, an arbitrary method, custom headers, or a Twilio SDK pass-through.

If an operation is not in [the coverage ledger](api_coverage.md), the agent should stop and report the missing boundary instead of inventing access.

## Agent behavior

The agent should:

1. Check auth locally and read the target before proposing a change.
2. Inspect the command locally when its fields or restrictions are not already clear, then use the exact `<spec-id> <operation-kebab>` command and a command-specific JSON input file.
3. Keep normal read output private-data-safe; use `--sensitive-out` only for a protected local file the user needs.
4. Treat paid reads and every write as plan-first.
5. Apply only from the reviewed plan with `--apply --yes` and every acknowledgement the plan names.
6. Never retry a write automatically.
7. Report the Twilio status literally. Queued is not delivered.
8. Require a new protected receipt path before apply; refuse an existing or unwritable destination and report `succeeded`, `failed`, or `uncertain` without automatic retry.
9. For bulk work, verify the exact derived target list locally, show only its private-data-safe preview and count, and refuse a missing list, a count mismatch, or more than 25 targets.
10. Put flexible JSON only in the exact documented field for that command. Never add an undocumented optional branch or turn the field into a generic body.

The public install slug is `twilio`:

```bash
npx skills add Qwayk/safe-agent-skills@twilio -g -y
```
