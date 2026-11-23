# What we tested

## November 23, 2026 local checks

Fresh installs of both local copies loaded all 12 SAV commands and passed 56 tests with simulated replies. The tests checked that a saved plan uses the same SAV key, that a receipt cannot overwrite the plan or settings, and that a second apply stops even if it names a different receipt. They also checked that unclear replies tell the user to check SAV and that known keys and transfer codes stay out of the output and receipt.

Both copies built a wheel and source archive, passed Ruff and mypy, and matched the generated command list. The archives include the right skill file. The local guide links and all three JSON examples passed.

## July 31, 2026

The source and public layouts of version `0.1.4` each passed 50 offline tests. The archive and wheel built successfully. Lint and type checks passed, all three redacted JSON examples parsed, and the clean wheel loaded 12 commands (four reads and eight writes).

The simulated replies checked routing, the fixed host and `APIKEY` header, refusal to follow redirects, offline plans, private file permissions, the signed plan, transfer-code handling, redaction, and write receipts. The skill passed in both layouts. The tests also reject a package with either no skill file or two copies.

## Provider source

The [official SAV collection](references.md) is pinned by SHA-256 `d330b3df8f1b1962fcae295b0dc47b831c15f68d0d90db73c4dcb151968e33fe`. It generates the same [12 commands](api_coverage.md) every time. The host is `https://api.sav.com/domains_api_v1/`.

## Run the checks

```bash
python tools/generate_inventory.py --check
python -m unittest -q
ruff check src tests tools
mypy src
```

The [domain read](examples/read-active.example.json), [plan](examples/plan.example.json), and [receipt](examples/receipt.example.json) are redacted examples. The tests use simulated replies. Check actual account results in SAV after an approved live change.
