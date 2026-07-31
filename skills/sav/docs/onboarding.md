# Connect SAV Domain APIs v1

You need a valid SAV API key and a whitelisted request source before running this CLI.
This tool does not perform logins, OAuth flow, API onboarding, or whitelist requests.

## 1) Prepare the local environment file

```bash
cp .env.example .env
```

## 2) Add required access values

In `.env`, set only values you were given by SAV:

```text
SAV_API_KEY=
SAV_TIMEOUT_S=30
```

Enter the key SAV issued after `SAV_API_KEY=`. It is required for read commands and write apply commands.

The process environment takes precedence over values in `--env-file`.

`SAV_TIMEOUT_S` is optional. If omitted, runtime defaults to `30`.

## 3) Confirm runtime and command surface

```bash
sav --output json --env-file .env --version
```

## 4) Confirm a read call works

```bash
sav --output json --env-file .env domains active
```

If this returns valid JSON, the tool can reach the fixed SAV API host.

## 5) Create one safe write plan

```bash
sav --output json --env-file .env --plan-out .state/plans/sale-price-example.json domains set-sale-price --domain-name example.com --sale-price 42
```

Stop here and review the output before any apply step.

For transfer submission, create a private secret file under `.state/secrets` and pass it through `--auth-code-file`:

```bash
mkdir -p .state/secrets
chmod 700 .state/secrets
AUTH_FILE="$(mktemp ".state/secrets/sav-transfer.XXXXXX")"
read -r -s SAV_TRANSFER_CODE
printf '%s\n' "$SAV_TRANSFER_CODE" > "$AUTH_FILE"
chmod 600 "$AUTH_FILE"
unset SAV_TRANSFER_CODE

sav --output json --env-file .env --plan-out .state/plans/submit-transfer-code.example.json domains submit-transfer-code --domain-name example.com --auth-code-file "$AUTH_FILE"

rm -f "$AUTH_FILE"
```

The file must be a regular mode-`0600` file with exactly one non-empty line. The value is never placed in command arguments or env vars.

## Important setup expectations

- IP whitelisting and account-level access are account prerequisites handled by SAV.
- The transfer authorization code has no environment fallback. It is read only from `--auth-code-file` during dry-run creation.
- Keep plan and receipt files out of shared directories; mode `0600` is used automatically.
