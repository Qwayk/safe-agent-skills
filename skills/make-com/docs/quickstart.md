# Quickstart

## 1) Prepare local config

```bash
cp .env.example .env
make-com-safe onboarding --output text
```

Set:

- `MAKE_BASE_URL` (example `https://eu1.make.com`)
- `MAKE_API_TOKEN` (Make API token)

## 2) Verify credentials

```bash
make-com-safe --output json auth check
```

Expect either a live response from `/users/me` or a clear auth failure message.

## 3) Read safely first

```bash
make-com-safe --output json api list
make-com-safe --output json api schema scenarios list-scenarios
make-com-safe --output json api scenarios list-scenarios --query "teamId=123"
```

The `api list` command shows what operations are available in this install.

## 4) Run a write with plan-first review

```bash
make-com-safe \
  --plan-out /tmp/make-scenario-plan.json \
  --output json \
  api scenarios update-scenario \
  --path-param scenarioId=123456 \
  --body-file /tmp/scenario-update.json
```

This returns a plan and does not change anything.

## 5) Apply the plan after review

```bash
make-com-safe \
  --plan-in /tmp/make-scenario-plan.json \
  --apply \
  --yes \
  --ack-no-snapshot \
  --output json \
  api scenarios update-scenario \
  --path-param scenarioId=123456 \
  --body-file /tmp/scenario-update.json
```

Use `--ack-no-snapshot` when the operation's write plan says no snapshot is available. Most Make writes in the pinned inventory need it.

## 6) Optional: include a receipt

```bash
make-com-safe \
  --plan-in /tmp/make-scenario-plan.json \
  --apply \
  --yes \
  --ack-no-snapshot \
  --receipt-out /tmp/make-receipt.json \
  --output json \
  api scenarios run-scenario \
  --path-param scenarioId=123456
```

## 7) Check run history

```bash
make-com-safe runs list
make-com-safe runs show --run-id <RUN_ID>
```

## If you need help

- `docs/use_cases.md` for real requests your agent can make.
- `docs/command_reference.md` for all flags, including destructive checks.
