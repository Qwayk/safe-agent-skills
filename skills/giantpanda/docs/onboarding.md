# Onboarding

Use when local setup is missing or incomplete.

## 1) Create config

```bash
giantpanda onboarding
```

This creates `.env` from `.env.example` if `.env` does not exist and reports placeholder fields.

## 2) Fill required value

Edit `.env` and set `GIANTPANDA_API_TOKEN`.

## 3) Check local readiness

```bash
giantpanda --output json auth check
```

This command never sends a request to GiantPanda and can be used any time to confirm readiness.

## 4) Run your first safe read

```bash
giantpanda --output json domains stats --start-date 2026-08-01 --end-date 2026-08-07
```

If this succeeds, ask for a plan before any domain-add apply.
