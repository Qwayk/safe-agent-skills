# Agent Extension Notes

The n8n CLI is inventory-backed. To add or refresh operations, update the pinned official spec copy, regenerate `docs/official_inventory.json`, copy the same inventory to `src/n8n_safe_agent_cli/data/official_inventory.json`, and regenerate `docs/api_coverage.md` plus `docs/command_reference.md`.

Do not add raw-request, private `/rest`, n8n CLI, node-doc, MCP, template, or webhook-runner commands.

When changing write behavior, keep these tests true:

- writes dry-run by default
- apply requires `--apply --yes --plan-in`
- no-snapshot apply requires `--ack-no-snapshot`
- high-risk apply requires `--ack-irreversible`
- plans redact secrets and include target/body hashes
- apply refuses if the reviewed plan no longer matches
