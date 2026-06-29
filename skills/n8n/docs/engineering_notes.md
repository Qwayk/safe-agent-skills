# Engineering Notes

- Built from the repo template on 2026-06-29.
- Pinned the official public API spec folder from `n8n-io/n8n` commit `0c92df794a07404d22cbc85a3c4ed6b332e442ab`.
- Generated 80 official operations across 15 command families.
- Kept command execution inventory-based and explicit; no raw request or arbitrary endpoint command was added.
- Writes use dry-run plans, plan matching, no-snapshot acknowledgement, high-risk acknowledgement, receipts, and redaction.
