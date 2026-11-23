# Engineering notes

## Where the code lives

| File | What it does |
| --- | --- |
| `src/gemini_api_tool/operation_registry.py` | Lists the 82 shipped operations and their API versions. |
| `src/gemini_api_tool/cli.py` and `gemini_commands.py` | Parse commands and pass them to the Gemini code. |
| `src/gemini_api_tool/gemini_runtime.py` | Builds the request, checks spending approval and saved plans, sends the request, and returns a receipt. |
| `src/gemini_api_tool/config.py` | Reads the key, API address and timeout. |
| `src/gemini_api_tool/audit_log.py`, `runs.py` and `json_files.py` | Write audit events, run history, plans and receipts. |

## Review and send

The plan records the request target and hashes of the JSON body and any upload. The tool signs the plan details with the API key and ties them to the folder that tracks sent plans. It reads the upload bytes once per apply, so the same bytes it checks are the ones it sends. Before sending, it creates a folder for the plan ID under `.state/runs/sent-plans/` in one filesystem operation. Simultaneous applies of the same plan use the same folder. If the send was interrupted, check Google before making another plan.

## June 28, 2026 build

Google’s `v1beta` and `v1` discovery files both reported revision `20260626`. Those files supplied the named commands. At that point reads and compute calls ran directly, state changes required a reviewed plan, and `python3 -m unittest -q` passed 23 tests. See [proof](proof.md) for later checks.
