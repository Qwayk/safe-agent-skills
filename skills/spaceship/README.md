# Spaceship

The Spaceship API tool for agents helps you manage domains, DNS, contacts, transfers, personal nameservers, and SellerHub from one clear workflow.

You can ask your agent to check whether a domain is available, review the domains in your account, inspect DNS or transfer settings, prepare a renewal, or review SellerHub and SafePay activity.

For example: "Which domains need attention?", "Check whether this domain is available", "Show me the DNS records before we change them", or "Prepare a renewal plan for this domain."

The agent looks first and explains what it found. If you ask for a live change, it saves a plan, shows the exact target and risks, and waits for your approval. Spend, ownership, DNS, private-data, financial, and destructive actions require stronger acknowledgement before the tool sends one write.

## Start here first

Ask your agent:

```text
Connect Spaceship, list my domains, and tell me what needs attention. Do not change anything.
```

If the tool is not connected yet, the agent will guide you through [onboarding](docs/onboarding.md). The [quickstart](docs/quickstart.md) shows the same first check from the command line.

## What your agent can do

- Check domain availability and review domain details.
- Read contacts, DNS records, privacy settings, nameservers, transfer state, and async operation status.
- Review SellerHub listings, sold-domain reports, verification records, checkout activity, and SafePay transactions while masking private values.
- Prepare and apply supported domain, DNS, contact, transfer, nameserver, SellerHub, checkout-link, and SafePay changes through saved plans.

## What happens before live changes

Read commands can run directly after credentials are configured. Write commands only create a local plan unless you provide the saved plan again with `--apply --yes` and every acknowledgement named in that plan.

Without `--plan-out` or `--receipt-out`, the tool saves writes under `.state/runs/<run_id>/plan.json` and `.state/runs/<run_id>/receipt.json`. An explicit path always wins.

The tool reads current state again when the official API offers a reliable check. If Spaceship does not expose a reliable snapshot or full financial recheck, the plan says so and requires `--ack-no-snapshot`. HTTP 202 means Spaceship accepted the work for processing; it does not mean the work is finished.

## What access this tool needs

Use a Spaceship API key and secret in a local `.env` file:

- `SPACESHIP_API_KEY`
- `SPACESHIP_API_SECRET`

Credentials are sent only to the fixed HTTPS API host `https://spaceship.dev/api`. The tool does not expose a general base-URL setting and never prints the credentials.

Redirects are disabled. Any HTTP 3xx response is returned as a failure, so the custom credential headers are never resent to another host.

## Install and first run

The public skill slug is `spaceship`. The command installed by the Python package is `qwayk-spaceship-safe-agent-cli`; they are different names for the skill and its executable.

```bash
npx skills add Qwayk/safe-agent-skills --skill spaceship
qwayk-spaceship-safe-agent-cli --output json --version
```

## What it covers today

The official boundary contains 40 documented operations across 10 families. The tool implements the 38 stable operations as fixed named commands. Two documented operations remain local refusals because Spaceship says they are under development and return HTTP 501.

See the [full API coverage](docs/api_coverage.md) and [command reference](docs/command_reference.md).

## Limits

- `domains delete` is unavailable and refuses locally.
- `domains personal-nameservers get-host` is unavailable and refuses locally.
- Live account behavior has not been tested because this source build used no Spaceship credentials and made no provider requests.
- The tool does not create API keys, manage payment methods, accept legal terms, automate the Spaceship website, host callbacks, or expose undocumented endpoints.

## Helpful docs

- [Choose the right guide](docs/README.md)
- [Get the first safe result](docs/quickstart.md)
- [Understand approvals and refusals](docs/safety_model.md)
- [See realistic asks](docs/use_cases.md)
- [Review tested behavior and limits](docs/proof.md)
