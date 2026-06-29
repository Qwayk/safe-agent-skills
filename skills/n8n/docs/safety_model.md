# n8n Safety Model

n8n workflows can trigger connected apps and internal systems, so this tool treats reads and writes differently.

## Reads

Read commands can run directly. They use named operations from the official public API inventory and send the API key only in the `X-N8N-API-KEY` header.

## Writes

Write commands start with a dry-run plan. The plan records:

- official operation and n8n scope
- target path parameters and query
- redacted request body
- API key fingerprint, not the API key
- snapshot status
- risk reasons
- verification notes

Live apply requires:

```bash
--apply --yes --plan-in plan.json
```

If the plan has no verified before-state snapshot, apply also requires:

```bash
--ack-no-snapshot
```

High-risk changes also require:

```bash
--ack-irreversible
```

High-risk includes destructive actions, workflow activation changes, execution stop/retry/delete, user or role changes, credential work, project moves, source-control pull, and package install/update/uninstall/import.

## Plan matching

The CLI refuses apply when the reviewed plan no longer matches:

- command family and operation
- base URL
- API key fingerprint
- path and query target
- request body hash

## Secret handling

The tool redacts API keys, tokens, credential data, webhook secrets, password-like fields, and authorization values from normal output, plans, receipts, and audit logs.

## Rollback

The tool does not promise generic rollback. n8n write operations affect different resources in different ways, and some connected systems may already have seen a workflow change. If rollback is needed, create a separate reviewed plan for the exact resource and action.
