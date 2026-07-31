# Agent extension guide

Use this page when editing source behavior.

## Repo map

- `src/qwayk_porkbun_safe_agent_cli/cli.py`: command definitions and operation dispatch
- `src/qwayk_porkbun_safe_agent_cli/config.py`: `.env` and host mode
- `src/qwayk_porkbun_safe_agent_cli/http.py`: request execution and transport checks
- `src/qwayk_porkbun_safe_agent_cli/output.py`: JSON/text output formatting
- `src/qwayk_porkbun_safe_agent_cli/errors.py`: typed errors and safety exceptions
- `src/qwayk_porkbun_safe_agent_cli/__main__.py`: entry point
- `scripts/generate_inventory.py` and `scripts/porkbun_inventory_policy.json`: source coverage generation
- `tests/test_cli.py`: runtime behavior and safety tests
- `tests/test_api_inventory.py`: boundary, generation, coverage, and packaged-resource parity tests

## Adding a read command

1. Add/adjust the operation inventory JSON and test schema expectations.
2. Register any new command in `cli.py` parser.
3. Add request schema handling and output shape checks.
4. Add a unit test in `tests/test_cli.py`.
5. Keep output as one object in `--output json`.

## Adding a write command

1. Add parser and operation mapping with `--apply`.
2. Add plan structure and precondition checks.
3. Add confirmation flags (if required) and optional snapshot handling.
4. Add no-snapshot behavior when before-state is unavailable.
5. Add verification logic with explicit comparison and readback contract.
6. Add tests for:
   - no-apply refusal
   - required ack flags
   - plan/retrieved state behavior
   - receipt shape and no secret leakage

## Safety constraints

- No raw endpoints.
- No hidden bridge modes.
- No unreviewed direct apply.
- Do not promise rollback without implemented recovery plan.
