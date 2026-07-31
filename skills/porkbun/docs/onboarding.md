# Onboarding

Set up Porkbun access first, then do one safe read before any live write.

## Step 1: Create `.env`

1. Run `porkbun onboarding --env-file .env`, or copy `.env.example` to `.env`.
2. Fill:
   - `PORKBUN_API_KEY`
   - `PORKBUN_SECRET_API_KEY`
   - `PORKBUN_API_HOST` (`default` or `ipv4`)
   - `PORKBUN_TIMEOUT_S` (optional)

The onboarding command creates the env file atomically with `0600` permissions. It refuses directory and symbolic-link targets.

## Step 2: Validate the local install

```bash
cd api-tools/qwayk-porkbun-safe-agent-cli
porkbun --version
```

## Step 3: Check the connection

```bash
porkbun --output json auth check
```

This call is read-only. With configured keys, it asks Porkbun whether the pair is valid. Without keys, it reports `authenticated: false` without making a provider request.

## Step 4: Start with one real read

```bash
porkbun --output json domain get-domains
```

## Step 5: Ask the first live-capable command only after a plan

For any write command:
- review the plan
- confirm intent
- run with `--apply` and required acknowledgement flags

## Host and safety limits

- Default host: `https://api.porkbun.com/api/json/v3`
- IPv4 host: `https://api-ipv4.porkbun.com/api/json/v3`
- Redirects are not followed; any `3xx` response fails.
- No raw endpoint calls, no dashboard automation, no webhook receiver hosting.
- Source and package checks use no credentials and make no live Porkbun request.

## Common onboarding mistakes

- wrong key pair for environment
- missing or stale `.env`
- `PORKBUN_API_HOST` set to anything other than `default` or `ipv4`

If you want to continue after setup, open [Quickstart](quickstart.md).
