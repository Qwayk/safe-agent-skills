# Where the code lives

- `cli.py` reads arguments and starts the command. `config.py` reads the settings.
- `operations_v1.py` lists the commands from Qdrant’s pinned API definitions.
- `commands/operations.py` builds plans, checks approvals and records results.
- `cloud_http.py` and `http.py` send requests and check replies.
- `runs.py` and `audit_log.py` write local run history. `json_files.py` reads and writes plans and receipts.

[Command list](official_commands_v1.txt) · [What the tests cover](proof.md)
