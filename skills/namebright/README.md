# NameBright

The NameBright API tool for agents helps you review and manage the domains in your NameBright account. It can check availability, show your account and domain details, and help you keep domain settings current.

You can ask your agent to review contacts, nameservers, DNS records, locks, auto-renew, privacy, verification status, purchases, renewals, and NameBright account pushes.

For example: "List the first five domains in my account," "Check the DNS records for example.com," "Tell me whether this domain is available," or "Prepare a plan to update these nameservers."

The safest first ask is: "Check my NameBright connection and list the first page of domains without changing anything." The agent reads first and explains what it found. If you ask for a live change, it prepares the exact change and waits for your approval.

## Start here first

After you connect the account, start with this:

```text
Check my NameBright connection, list the first page of domains, and do not change anything.
```

Need help connecting it? [Set up NameBright API access](docs/onboarding.md). Want examples? [See what you can ask your agent](docs/use_cases.md).

## What your agent can do

Your agent can:

- check domain availability, account balance, and domain inventory
- review contacts, nameservers, DNS records, WHOIS accuracy, and verification status
- prepare domain registration and renewal requests with exact domain and duration read-back
- prepare updates to lock/autorenew/privacy, contacts, nameservers, and host records
- prepare inbound and outbound NameBright account pushes
- prepare external verification send and code verification actions

The full command boundary is in [API coverage](docs/api_coverage.md).

## What happens before live changes

Every write starts as a saved plan. Applying is not possible without the reviewed plan file.

The tool asks for extra confirmation before:
- spending money (`--ack-spend`)
- high-risk settings and verification actions (`--ack-high-risk`)
- ownership and no-snapshot/irreversible flows (`--ack-ownership`, `--ack-no-snapshot`, `--ack-irreversible`)
- destructive actions (`--ack-destructive`)
- external messages (`--ack-external-message`)
- creating a recipient account during force-push (`--ack-account-creation`)

Results are never printed in ways that reveal secrets. Read-back verification is attempted where NameBright supports it.

## What access this tool needs

You need:

- a NameBright account with Domain API access
- an approved source IP on the NameBright API whitelist
- a NameBright client ID and client secret

The tool obtains a short-lived OAuth2 bearer token in memory from `https://api.namebright.com/auth/token` and sends it only to `https://api.namebright.com/rest`.
Keep `NAMEBRIGHT_CLIENT_ID` and `NAMEBRIGHT_CLIENT_SECRET` in your local `.env` file.
Never paste credentials, bearer tokens, authorization codes, or verification codes into chat.

## Install and first run

Install the `namebright` skill from `Qwayk/safe-agent-skills`.
Then follow the [quickstart](docs/quickstart.md) to create your local `.env`, run `auth check`, and get a safe first read.

## What it covers today

The tool covers 60 Domain API + 1 OAuth operations from NameBright API help pages retrieved on July 31, 2026.
Each query-style and path-style push variant has its own named command.
The operation mapping and hashes are pinned in [the source references](docs/references.md).

## Limits

- Live NameBright behavior is not verified yet because no credential or live API request was authorized for the source build.
- The tool does not manage account funding, payment methods, API-access applications, IP whitelists, or undocumented endpoints.
- It does not promise rollback or restore where NameBright does not provide a reliable path.

## Helpful docs

- [Choose the right guide](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [What you can ask](docs/use_cases.md)
- [Command guide](docs/command_reference.md)
- [Safety before live changes](docs/safety_model.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
