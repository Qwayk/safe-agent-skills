# Onboarding

This command gives you a fast path from a fresh clone to a working config.

```bash
make-com-safe onboarding
```

`onboarding` will:

- create `.env` from `.env.example` when `.env` is missing,
- check for missing values,
- print next command steps.

## Required values

Set these in `.env` (or exported environment variables):

- `MAKE_BASE_URL`
  - Use one zone base URL. Example: `https://eu1.make.com`
  - The CLI normalizes this to include `/api/v2`.
- `MAKE_API_TOKEN`
- `MAKE_TIMEOUT_S` (optional, seconds)

The tool also accepts the legacy alias `MAKE_ZONE_URL` for base URL.

## Recommended flow

```bash
make-com-safe --output text onboarding
make-com-safe --output json auth check
make-com-safe --output json api list
```

## Flag

`--no-write-env` only prints setup guidance without touching `.env`:

```bash
make-com-safe onboarding --no-write-env
```

## Safety notes

- Secrets are never printed.
- `.env` is local-only and should not be committed.
- `onboarding` itself does not call write endpoints.
