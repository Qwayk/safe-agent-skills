# Skimlinks Safe CLI

This page is the agent-facing rule sheet for the public Skimlinks skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use this skill when a user wants an agent to work with the customer-ready Skimlinks safe API CLI in this repo.

## Reference points

- CLI command: `skimlinks-safe-cli`
- Command reference: `docs/command_reference.md`
- API coverage ledger: `docs/api_coverage.md`
- Proof pack: `docs/proof.md`

## Safety Rules

- Never ask the user to paste Skimlinks client secrets, access tokens, or `.env` contents into chat.
- Start with `skimlinks-safe-cli onboarding` when setup is missing.
- Use `skimlinks-safe-cli auth check` before live Merchant or Reporting requests.
- Use `skimlinks-safe-cli auth check --scope product` before Product Key requests.
- Treat Product Key as separately gated unless the account has enabled Product Key credentials.
- Require `SKIMLINKS_PUBLISHER_DOMAIN_ID` or `--publisher-domain-id` for Product Key commands.
- Use only explicit named commands from the command reference.
- Do not invent raw HTTP requests or generic bridge commands.
- Link Wrapper is a local URL builder. It must not open the URL or follow redirects.
- Data Pipe and Skimlinks JavaScript are documented surfaces, but they are not shipped HTTP API command families in this CLI.

## Normal Flow

1. Check setup with onboarding or auth.
2. Run the smallest explicit read command that answers the request.
3. Report the useful result in plain English.
4. Mention any Product Key, Data Pipe, JavaScript, or Link Wrapper limitation when it affects the answer.

## Install Note

To expose this skill in a runtime that reads local skills, copy or symlink this folder into that runtime's skills folder, such as `.codex/skills/skimlinks-safe-cli/`.
