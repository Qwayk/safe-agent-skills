# Jobs and batches

Google Cloud batch work is easy to get wrong because one repeated command can touch many resources. This source build does not ship a CSV batch runner yet, so repeat work should stay one reviewed generated command at a time.

A CSV file is a simple spreadsheet-style file. A safe GCP batch runner must expand each row into an explicit generated `service operation` command and keep the same plan and apply gates.

## What to do today

- Use one generated command at a time.
- Save a dry-run plan for every write.
- Review the plan before apply.
- Keep the target project, region, billing account, or resource name explicit in the input JSON.

## Future batch rule

When a batch runner is added later, it must not become one command that can call any Google URL.

It should:

- accept only operations that exist in `docs/_generated/gcp_discovery_inventory.json`
- create one plan entry per generated operation
- require reviewed `--plan-in --apply --yes` for writes
- keep `--ack-no-snapshot` and `--ack-irreversible` gates
- stop when a row has an unclear target or unsafe missing value
