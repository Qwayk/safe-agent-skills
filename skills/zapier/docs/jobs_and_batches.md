# Jobs and batches

Zapier source-ready v0.1.0 does not ship a batch runner.

Use the explicit operation commands in `docs/command_reference.md` one at a time. For live changes, create one plan per Zapier operation, review it, then apply it with `--plan-in` and the required approval flag.

This is intentional. Zapier writes can run actions, create workflows, change inbox state, or acknowledge messages, so batching them before the single-operation safety model is proven would make review weaker.
