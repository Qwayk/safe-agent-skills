---
name: figma-safe-cli
description: Execute explicit Figma API operations with safe defaults (preview first, explicit apply, and verification notes).
---

This page is the agent-facing rule sheet for the public Figma skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.


You are a safe wrapper for `figma-safe-agent-cli`.

## Core rules

- Always call commands with `--output json`.
- Never include raw secrets (`FIGMA_ACCESS_TOKEN`, OAuth secrets, headers).
- Validate auth before write operations: `figma-safe-agent-cli auth check`.
- Use explicit operation commands only:
  - `operations list`
  - `operations show`
  - `operations <area> <op_key>`
- For writes:
  1) run `operations <area> <op_key>` without `--apply` first
  2) review returned plan
  3) apply with required flags (`--apply` and `--yes`, plus `--ack-irreversible` where required) only after approval
  4) report the receipt or exact tool limitation instead of claiming a provider write happened without proof
- Use `--plan-out` and `--plan-in` for repeatable approvals.
- Do not claim stronger verification than the tool provides; current provider writes need required approval before Figma token use or HTTP when no before-state can be saved.

## Typical safe flow

1. `figma-safe-agent-cli auth check`
2. `figma-safe-agent-cli operations list --area ...`
3. `figma-safe-agent-cli operations show ...`
4. `figma-safe-agent-cli operations <area> <op_key> ...` (preview)
5. `figma-safe-agent-cli --apply --yes operations <area> <op_key> ...` (after approval; verify the receipt or exact tool limitation)
