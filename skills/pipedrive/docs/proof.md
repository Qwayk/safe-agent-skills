# Pipedrive verification

## November 22, 2026

All 31 tests passed in both local copies with Python 3.12. Each built package contained all 161 route entries and opened help after a fresh install outside the checkout. Both skill files passed validation.

Using fake Pipedrive replies on this computer, the installed tool created the selected settings file, read the current user, returned an empty list, reported a failed read, used the supplied offset for the second page, and returned file headers. These checks made zero live Pipedrive calls.

Run the checkout tests with:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

They cover account setup, read-only command coverage, pagination, failed and empty reads, the file header check, and token handling. Check the installed tool from outside the source directory as well. It needs the bundled command list even when you only ask for help:

```bash
qwayk-pipedrive-safe-agent-cli --version
qwayk-pipedrive-safe-agent-cli --help
```

## May 22, 2026 verification

The earlier checks covered imports, the command list, redaction, read-only behavior, and one sample read for each command group. They also checked that the file command reported the HTTP method it actually used. The saved commands were:

```bash
python3 -m venv .venv
.venv/bin/python -m ensurepip --upgrade
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --output json --version
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env onboarding
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env auth check
PYTHONPATH=src python3 -m qwayk_pipedrive_safe_agent_cli --env-file .env --debug --log-file proof_runs.jsonl auth check
```

## Saved output

- [Version](examples/outputs/version.json)
- [Connection check](examples/outputs/auth_check.json)
- [File details](examples/outputs/files_download_metadata.json)
