# What was tested

## November 23, 2026

The audit installed the source and GitHub copies and used simulated Unsplash replies. Search and connection checks worked. The old download path recorded tracking before it reached the missing import. A separate test of the file-writing step showed that an interrupted overwrite left a partial file in place of the original.

The updated tests cover matching previews, old previews, changed settings, refusal before tracking, tracking without a local copy, and saving approved files with their hash and photographer details. A simulated lost reply sends one tracking request and leaves the outcome marked unclear. An interrupted transfer keeps the original file. Collection lookups and exports accept IDs with letters.

Both local copies passed 33 offline tests. I built a wheel from each copy, installed it in a clean Python environment, and ran 10 checks against the installed command code. Setup created the selected settings file and kept its path in the next command. Both skill files passed validation and the Python source passed the type check. The tests used simulated replies.

## Earlier checks

The local test and proof baseline is from June 4, 2026. The docs and example results were checked again on June 11, 2026. That June cleanup also removed a leftover `TEMPLATE_GUIDE.md`. The earlier evidence covers Access Key reads, pagination limits, the one-object JSON output, and the original no-snapshot approval.

The saved [plan](examples/plan.example.json), [refusal example](examples/receipt.example.json), and [command outputs](examples/outputs/) show earlier formats. Save a new preview with `--plan-out` before applying a download. The older plan example predates the matching connection check.

## Repeat the checks

Use these commands from the package folder.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m unittest -q
.venv/bin/unsplash-api-tool --output json --version
.venv/bin/unsplash-api-tool --output json onboarding --no-write-env
```

Use a valid Access Key for an authorized live `auth check`. The offline tests use simulated replies, including success, decline, lost replies and file errors.
