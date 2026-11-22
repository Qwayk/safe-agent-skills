# Approval and recovery

Use this retired tool to inspect old runs and preview requests offline. A dry run shows what the tool would send. Reddit’s response is unknown until a request reaches it.

## How to read a plan

Check the action, target account and subreddit, the exact fields you expected to change, and whether the tool could save the old data. The tool compares settings such as its URLs, client ID, permissions, and User-Agent when checking a saved plan. Check the signed-in account separately.

The old live commands required `--live`. A change also required `--apply`. Risky changes required `--plan-in` and `--yes`. Irreversible changes required `--ack-irreversible`. When the tool could not save the old data, it required `--ack-no-snapshot`.

## How to read a result

- A refusal means the tool stopped. The plan can still be useful for seeing what it would have tried.
- `before_state.status="no_snapshot_available"` means the tool has no saved copy to restore. An approved receipt should record that limit and the approval to proceed.
- Treat a success value in the output as unverified. The tool marked a simulated Reddit error as successful. Check the actual post or moderation result.
- If the reply was lost, check Reddit for the result before repeating a request that could make the same change twice.

See the [saved examples and test results](proof.md).
