# What we tested

## November 23, 2026 local checks

Fresh installs of the source and local catalog copy loaded 62 commands and passed 108 offline tests. The tests used simulated replies to check account changes, price changes and missing prices, pending orders and their lookup, a lost reply, a second attempt, and account moves that did or did not appear in the queue.

Both copies passed Ruff and mypy. I checked the guide links, all four JSON examples, the wheels, and the source archives. The public archive now includes its top-level skill instructions.

## July 31, 2026

Version `0.1.0` passed 103 tests with Python 3.12.13 in both the original source and the unpacked archive. Ruff and mypy passed across 21 source files. The source archive held 77 files and the wheel held 26. The installed wheel loaded 61 named commands across 11 groups (23 GET, 18 POST, eight PUT and 12 DELETE). The tests used simulated NameBright replies.

The tests checked the fixed host, OAuth, redaction, all 37 write plans, approvals, and before-and-after reads. Contact tests showed that the tool catches changed contact details even when their redacted display looks the same. Plans and receipts kept the field names and fingerprints used for checking.

A separate July correction brought the guides into line with the actual flags, including `--domain-name`, the approval flags, and `/auth/token`. It removed starter examples from the instructions. The [July operation hashes](official_operation_pages.sha256) preserve the source list.

## Repeat the checks

```bash
python -m unittest discover -s tests -q
ruff check src tests
mypy src
```

The [version](examples/outputs/version.json), [connection](examples/outputs/auth_check.json), [plan](examples/plan.example.json), and [receipt](examples/receipt.example.json) are examples with fake values. The example plan can't be applied. Tests use simulated requests. Account access and live results need separate checks with an authorized NameBright account.
