# Safety model

This tool supports live reads and write planning. Current write-capable commands require explicit no-snapshot approval before live write execution when no saved snapshot is available.

Core rules:
- Write-capable commands are dry-run by default.
- Dry-run plans include `before_state.required: true`, `before_state.supported: false`, and `before_state.status: "blocked"`.
- Apply attempts still require the normal flags.
- High-risk deletes require `--apply`, `--yes`, and `--ack-irreversible`.
- After the gates pass, apply attempts require explicit no-snapshot approval before Threads provider writes, local token writes, demo/job writes, or receipt output.
- No built-in rollback, provider backup, or restore path exists in this runtime.

Local outputs:
- Dry-run plans may be written with `--plan-out`.
- Run history may write `.state/runs/<run_id>/` and `.state/runs/index.jsonl`.
- Missing-approval refusal summaries are allowed; successful write receipts must record either saved before-state or explicit no-snapshot approval.

Write families covered by the refusal:
- Auth local token writes: `auth code exchange`, `auth token exchange-long`, and `auth token refresh`.
- Posts: create text/image/video/carousel item/carousel, publish, repost, and delete.
- Replies: hide/unhide and pending reply decisions.
- Demo write and jobs rows with write actions.

What must be added before live apply can be allowed:
- Command-specific before-state capture or provider backup.
- A verification plan tied to saved before-state.
- A clear rollback status. It may remain `automatic_rollback: false`, but that must be explicit before any live write is allowed.
