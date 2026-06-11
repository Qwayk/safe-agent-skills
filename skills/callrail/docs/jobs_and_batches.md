# Jobs and batches

This tool intentionally does not ship a generic batch runner.
It uses explicit named commands only, so each action is a direct API family command like `calls list`, `text-messages send`, or `trackers disable`.

Use your shell or a small script to run repeated calls when you need batching.
For every write call, run in dry-run mode first and then apply with `--apply --yes --ack-no-snapshot` (and `--ack-irreversible` when required).
