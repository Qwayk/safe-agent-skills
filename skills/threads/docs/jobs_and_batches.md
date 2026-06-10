# Jobs and batches

This tool exposes a small demo jobs runner in the current slice.

Rows with write actions now require explicit no-snapshot approval before demo/job writes or receipt output when no saved snapshot is available.

Read-safe runs history is still available:

Run history can still be reviewed with:
- `threads-api-tool runs list`
- `threads-api-tool runs show --run-id <id>`
