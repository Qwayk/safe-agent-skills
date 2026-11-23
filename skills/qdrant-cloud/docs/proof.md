# Qdrant Cloud test results

## November 23, 2026 local checks

The source and local public copy each passed 27 offline tests. I built a wheel and source archive from each copy, installed each wheel outside the repo, and checked all 118 command names.

The installed checks covered a private settings file at the chosen path, the first account read, a changed backup ID and a restore that sent once when Qdrant returned a simulated error. The test suites also covered changed keys and request bodies, destructive and spending approvals, and price estimates. The example generator produced a review plan and a restore receipt using a local test server. Both skill files passed validation. The public copy contains 90 files.

These checks used fake keys and simulated replies. Live Qdrant behavior was outside this check.

## June 2026 checks

The local suite and committed examples date to June 4, 2026 UTC. The docs and runtime rules were checked again June 11, 2026 UTC. The tool version was `0.1.0` with inventory `v1`.

The June checks covered the named commands, `--live`, the no-snapshot flag for ordinary changes, and Qdrant’s separate backup and restore workflow. The [committed June examples](examples/) preserve the old result and approval fields. Generate a new plan for current use.

## Run the checks

From the tool folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
qdrant-cloud-api-tool --output json --version
qdrant-cloud-api-tool --output json auth check
python3 scripts/generate_example_outputs.py
```
