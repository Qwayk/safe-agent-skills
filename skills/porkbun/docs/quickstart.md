# Quickstart

If you downloaded the package and want to run it from source, open its folder and run:

```bash
python3 -m venv .venv
. .venv/bin/activate
.venv/bin/python -m pip install -e '.[dev]'
```

[Connect your Porkbun account](onboarding.md) before using commands that need keys. The examples use `porkbun.env`. Change the path if you chose a different file.

## Check prices or list domains

```bash
porkbun --output json pricing get-pricing-get
porkbun --output json --env-file porkbun.env domain get-domains
```

For the POST version, save the JSON in a file and run `porkbun --output json pricing get-pricing --input pricing.json`. Wherever a command uses `--input`, give it the path to a JSON object file.

You can also ask your agent which domains expire soon, which webhook deliveries failed, or what a transfer costs. For a specific domain, use `porkbun --output json --env-file porkbun.env domain domain-check-domain --domain example.com` to see whether it is available to register and what registration, renewal and transfer cost.

## Change the cache time on one DNS record

First, check the DNS records and identify the record ID.

```bash
porkbun --output json --env-file porkbun.env dns get-dns-records --domain example.com
```

Put `{"ttl": 900}` in `dns.json`. This sets the cache time to 900 seconds. The following example uses record ID `42`.

```bash
porkbun --output json --env-file porkbun.env --plan-out dns-plan.json \
  dns dns-edit --domain example.com --id 42 --input dns.json
```

Check the record, its current value and the planned change. After approval, use the same keys, directory and input file.

```bash
porkbun --output json --env-file porkbun.env --plan-in dns-plan.json --yes \
  dns dns-edit --domain example.com --id 42 --input dns.json --apply
```

Read the receipt to see whether Porkbun returned the expected record. The [approval guide](safety_model.md) explains what to do if the record changed or the result is unclear.

## Check a private account invite

Save `{"token":"INVITE_TOKEN"}` in a private file first.

```bash
chmod 600 invite-status.json
porkbun --output json --env-file porkbun.env account get-account-invite-status --input invite-status.json
```

For more commands, see the [command reference](command_reference.md).
