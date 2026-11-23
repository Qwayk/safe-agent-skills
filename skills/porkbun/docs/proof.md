# What we tested

The offline checks use sample Porkbun replies. They check what the CLI sends, what it refuses and what it records. Live account permissions, real charges and real DNS changes need separate verification.

## November 23, 2026 local checks

Fresh installs from the source and local catalog copy each loaded all 66 commands and passed 56 tests with the network blocked. Both passed the lint, type and skill checks. Regenerating the inventory produced the same files and checksum.

The tests checked that a saved plan stops if either key changes or if the plan is too old to carry the account check. For DNS, they checked that the tool stops before a write if the records changed or cannot be confirmed, and that the receipt only confirms the expected result. They also checked a cache-time-only edit, a failed purchase preview with the same price, and onboarding with a chosen file that has spaces in its path.

## July 31, 2026

The source checks covered version `0.1.0` and the pinned v3.9 spec, with 53 paths and 66 commands. See the [spec and checksum](references.md).

- Replaced the starter docs and examples with Porkbun setup, commands and approval rules.
- Checked that edited or unsigned plans stop, including changes to expiry, before-state and idempotency fields. Checked that acknowledgement requirements come from the current command and that missing or changed cost stops a billable write.
- Checked file permissions, atomic replacement and private destinations. Tested collisions between outputs and inputs through relative paths, `..`, links and existing files. Concurrent first plans shared one signing key.
- Checked both allowed provider URLs, redirect refusal, and redaction of keys and sensitive values in results and errors. Kept invite tokens in JSON input files.
- Checked source packaging, types and repeatable inventory generation. No live Porkbun account or real keys were used.

## Run the source checks

In a clean environment with the project installed, run:

```bash
python -m unittest discover -s tests -q
ruff check .
mypy src
python scripts/generate_inventory.py
```

Check that generating the inventory leaves the tracked files unchanged when the command list stays the same.

## Sample output

The redacted examples show the earlier output format. Create a fresh plan with the installed tool.

- [Version](examples/outputs/version.json)
- [Connection check](examples/outputs/auth_check.json)
- [Plan](examples/plan.example.json)
- [Receipt](examples/receipt.example.json)
