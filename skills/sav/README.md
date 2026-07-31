# SAV Domain APIs v1

The SAV Domain APIs v1 tool for agents helps you review domains in your SAV account, check recent auction and premium sales, see current transaction pricing, and prepare documented domain changes.

You can ask your agent to show your active domains, review recent sales, check SAV's current pricing, or prepare an update to a sale listing, renewal setting, nameservers, privacy, WHOIS contacts, or a pending transfer.

For example: "Show my active SAV domains," "Check my recent premium sales," "What is SAV's current domain pricing?" or "Prepare a plan to change the nameservers for example.com."

The agent starts by reading your account and explaining the result. If you ask it to change a domain, it builds a private plan for review first and keeps sensitive values redacted from output.

## Start here first

- Need use-case ideas first? [Use cases](docs/use_cases.md)
- Need onboarding and setup? [Onboarding and env file](docs/onboarding.md)
- Need safety details? [Safety model](docs/safety_model.md)
- Need exact syntax? [Command reference](docs/command_reference.md)
- Want proof and limits? [Proof and verification](docs/proof.md)

## What your agent can do

- Review active domains in the account.
- Check recent auction sales, premium sales, and current SAV transaction pricing.
- Prepare changes to auto-renewal, nameservers, privacy, and WHOIS contacts.
- Prepare transfer authorization, sale-price, sale-listing, and remove-from-sale actions.

Reads go only to SAV's documented domain API host. Write plans are private mode-`0600` files that keep the minimum exact values needed for apply, while displayed output and receipts hide transfer codes and WHOIS contact data.

The private state layout is under the env-file directory and guarded by `0700` directories:

- `.state/plans/` for plans
- `.state/receipts/` for receipts
- `.state/keys/` for signing key material

## What happens before live changes

Every write command is review-first by default:

- `--plan-out` builds the plan file.
- dry-run write does not call SAV HTTP.
- apply requires `--plan-in`, `--apply`, `--yes`, `--ack-no-snapshot`, and `--ack-high-risk` in the same command.
- apply output is redacted and indicates receipt status.
- Plan files are schema `2` and signed with HMAC-SHA256.
- Plan signing keys live at `.state/keys/plan-hmac.key`.

## What access this tool needs

- `SAV_API_KEY` is required for reads and apply writes.
- `SAV_API_KEY` may come from the process environment or the selected env file; the process environment takes precedence.
- SAV asks for account IP whitelisting through `support@sav.com`.
- This is a user prerequisite; the tool only uses the provided access.
- Provider host is fixed to `https://api.sav.com/domains_api_v1/`.
- `SAV_TIMEOUT_S` controls request timeout when set.
- The tool does not accept a literal transfer code flag or retry prompt during apply.

## Install and first run

Install slug: `sav`.

Ask your agent to install the `sav` skill from `Qwayk/safe-agent-skills`. If your host does not install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@sav -g -y
```

Then confirm the command is available:

```bash
sav --output json --env-file .env --version
```

Then run:

```bash
sav --output json --env-file .env domains active
```

## What it covers today

The tool covers the complete official SAV Domain APIs v1 collection: account domains, recent sales, transaction pricing, and the documented domain, transfer, privacy, contact, renewal, and sale changes.

See [API coverage](docs/api_coverage.md) for all 12 operation and command mappings.

## Limits

- No hidden raw-request bridge.
- No rollback, backup, or restore workflow is currently shipped.
- No independent readback guarantee for write commands.
- Receipts report provider response and explicit safety state, not restoreability.
- For writes, only `provider_accepted` can be reported from 2xx provider responses; it reflects provider response only and does not verify durable account state.
- Source proof uses mocked provider behavior only. No SAV credential or live SAV request was used.
- No claim of live proof from examples; signatures in examples are placeholders.

## Helpful docs

- [Use cases](docs/use_cases.md)
- [Safe change flow](docs/safety_model.md)
- [Coverage map](docs/api_coverage.md)
- [Authentication rules](docs/authentication.md)
- [Command reference](docs/command_reference.md)
