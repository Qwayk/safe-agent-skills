# Check a Jobber account

Ask your agent:

> Check which Jobber account is connected, then show me a few clients so I can confirm it's the right one.

Follow [Connect Jobber](onboarding.md) if you need to add a token. For an existing connection, start here:

```bash
qwayk-jobber-safe-agent-cli --env-file account.env --output json auth check
qwayk-jobber-safe-agent-cli --env-file account.env --output json read account --selection "id name"
```

Confirm the account name and ID. Then try one small read:

```bash
qwayk-jobber-safe-agent-cli --env-file account.env --output json read clients --selection "nodes { id name } totalCount" --limit 10
```

Use `schema summary` to check which commands are installed. For any proposed change, see [approval flags and receipts](safety_model.md).
