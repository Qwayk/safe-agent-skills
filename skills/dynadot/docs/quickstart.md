# Quickstart

If you downloaded the source, open its folder and install it:

```bash
python3 -m venv .venv
. .venv/bin/activate
.venv/bin/python -m pip install -e .
```

Follow [Onboarding](onboarding.md) to connect your account. These examples use `dynadot.env`.

## Check domains, prices, or orders

```bash
dynadot-api-tool --output json --env-file dynadot.env domains list --page 1
dynadot-api-tool --output json --env-file dynadot.env account balance
dynadot-api-tool --output json --env-file dynadot.env pricing tld-price --currency USD
```

For a long list of names, put one name per line in `domains.txt` and run:

```bash
dynadot-api-tool --output json --env-file dynadot.env domains availability \
  --domains-file domains.txt --show-price --currency USD --out availability.json
```

The command reports how many names were available, unavailable, or still unresolved. Keep the default one name per request on a Regular Account. If a registry or connection error remains after retries, the command exits with an error and the file still shows which names need another check.

## Review a purchase

For example, to prepare a one-year registration with a maximum of $15:

```bash
dynadot-api-tool --output json --env-file dynadot.env --plan-out register.json \
  api3 register --domain example.com --duration 1 --currency USD --max-price 15.00
```

Check the account, domain, term, currency, and price. The same inputs must be used when applying a reviewed plan. See the [approval and price rules](safety_model.md).

## Compare and change nameservers

```bash
dynadot-api-tool --output json --env-file dynadot.env domains list --all --out domains.list.json
dynadot-api-tool --output json --env-file dynadot.env domains name-servers export \
  --domains-export-in domains.list.json --out name_servers.current.json
dynadot-api-tool --output json --env-file dynadot.env domains name-servers diff \
  --current-in name_servers.current.json --desired-ns ns1.example.net \
  --desired-ns ns2.example.net --out name_servers.diff.json
dynadot-api-tool --output json --env-file dynadot.env --plan-out name_servers.plan.json \
  domains name-servers set --diff-in name_servers.diff.json
```

Check the domains and intended nameservers before approving. For two-account moves, bids, contact changes, and other requests, see the [command reference](command_reference.md).
