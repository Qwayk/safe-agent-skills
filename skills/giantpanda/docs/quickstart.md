# Quickstart

Use this path to get one useful result quickly: a date-range stats result.

## 1) Check setup readiness (local only)

```bash
giantpanda --output json auth check
```

What this means:

- `ready: true` means a non-placeholder token is available in `.env` or process env.
- `ready: false` means token is missing or still a placeholder.
- This command never sends a request to GiantPanda.

If this is false, run onboarding:

```bash
giantpanda onboarding
```

## 2) Get the first useful date-range result

```bash
giantpanda --output json domains stats --start-date 2026-08-01 --end-date 2026-08-07
```

Optional pagination:

```bash
giantpanda --output json domains stats --start-date 2026-08-01 --end-date 2026-08-07 --page 1 --page-size 50
```

If this succeeds, ask your agent to summarize what it found and whether another date window or page would help.

## 3) Prepare a safe write plan

```bash
giantpanda --output json domains add --domain example.com --domain shop.example.com
```

This is the plan-only mode by default. It stays local and writes a private plan file.
