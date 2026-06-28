# Architecture

The Azure skill is built as a small command-line tool that an agent can run from a normal shell while keeping plans, receipts, and local settings in predictable files. It turns the pinned Azure REST API inventory into explicit service commands, then routes each command through shared config, redaction, safety, HTTP, and run-history code. This matters when an agent is using the skill for real work. The user can see which layer picked the operation, which layer checked the risk, and which layer wrote the run record. A good architecture check is: ask the agent to explain which generated command it would use, what input file it needs, and where the plan or receipt would be saved before it prepares any change.

Read this after the user-facing docs, not before them.

## Runtime

The entry point is a local CLI command. It reads a JSON input file, loads Azure settings from the local environment, builds the REST request, and writes structured output. Read operations can return a result directly. Write operations first create a plan, then require a separate apply step before anything is sent live.

## Request flow

1. The generated command selects one Azure operation from the pinned inventory.
2. The input reader loads path, query, header, and body values from JSON.
3. The safety layer classifies the operation and decides whether a plan, acknowledgement, or refusal is needed.
4. The HTTP layer sends the request when the action is allowed.
5. The run-history layer writes the plan, receipt, or refusal record.

## Main parts

- `cli.py`: argument parsing + shared flags
- `commands/*`: user-facing verbs
- `config.py`: `.env` parsing and validation
- `http.py`: HTTP client wrapper around `requests`
- `audit_log.py`: optional JSONL audit events (secrets redacted)
- `runs.py`: local run artifacts + history index (`.state/runs/`)
- `errors.py`: consistent error taxonomy (`ValidationError`, `SafetyError`, `NotSupportedError`)
- `json_files.py`: safe JSON read/write helpers for plan/receipt files

## Generated inventory

The command set is generated from a pinned Azure REST API spec snapshot. That makes the public skill predictable: the agent should use the inventory and command guide to choose commands, not memory of old Azure examples.
