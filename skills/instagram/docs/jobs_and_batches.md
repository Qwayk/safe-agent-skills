# Instagram Login Tool Jobs and batches

The shipped CLI does not include the scaffold `jobs` runner.

That is intentional. The old template batch surface was demo-only, so it was removed from the supported command set instead of pretending it was a real Instagram feature.

## Safe batch pattern

If you need bulk work:

1. have your agent read the target items first
2. generate one dry-run command per item
3. review the plans
4. rerun only the approved commands with `--apply` to confirm the explicit no-snapshot approval
5. keep the saved plans, refusal outputs, and summaries under `.state/runs/`

## Why this tool does not ship a CSV runner yet

- Instagram writes are not all equally safe
- some commands need extra flags like `--yes` or `--ack-irreversible`
- the removed scaffold batch runner only had fake demo actions

If a real batch runner is added later, it must use the same explicit command families listed in `docs/command_reference.md`.
