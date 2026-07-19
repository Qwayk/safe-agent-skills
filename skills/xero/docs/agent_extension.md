# Extending the Xero tool

Change the boundary only from an official Xero contract. Do not add one-off commands by guessing a URL or copying an SDK method.

## Before changing commands

1. Read the root, `api-tools/`, and tool-local `AGENTS.md` chain.
2. Confirm the official OpenAPI release or exact official docs page.
3. Decide whether the operation is current, regional, partner-gated, paid, preview, superseded, duplicate, callback-only, or unavailable.
4. Add a failing inventory or behavior test before changing the generator or runtime.

## OpenAPI changes

Update the pin deliberately, then regenerate both:

- `src/xero_safe_agent_cli/generated/operations.json`
- `docs/api_coverage.md`

Review the complete count diff, commands added or removed, scopes, auth flow, request shape, risk, sensitive output, snapshot pairing, and verification. Never hand-edit the generated files.

## Official docs-only changes

Add a manual row only when the official docs provide a fixed method, URL, parameters, auth, and enough request detail to implement it safely. If the contract is incomplete, record the family as unavailable or access-gated instead of adding a loose command.

## Runtime changes

Keep these invariants:

- one fixed command per callable row
- no arbitrary host, path, method, or request bridge
- exact tenant and auth profile checks
- protected sensitive reads
- all non-GET operations plan-first
- separate normal, high-risk, and no-snapshot approvals
- saved-plan integrity and changed-target refusal
- verification and protected receipt when applicable
- exactly one JSON object on stdout

Run tests, Ruff, mypy, deterministic generation, package build, and a clean installed-artifact check. Then manually read the README, onboarding, command, safety, proof, coverage, examples, and `skills/xero/SKILL.md` as one set.
