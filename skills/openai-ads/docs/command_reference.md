# Command Reference

Use `--output json` for agent runs.

## Local commands

```bash
openai-ads-safe-agent-cli onboarding
openai-ads-safe-agent-cli --version
openai-ads-safe-agent-cli runs list
openai-ads-safe-agent-cli runs show --run-id <run-id>
```

## Auth

```bash
openai-ads-safe-agent-cli auth check
```

## Generated Advertiser API commands

List the 41 generated operation commands:

```bash
openai-ads-safe-agent-cli api list
```

Command shape:

```bash
openai-ads-safe-agent-cli api <family> <command> \
  --path-param name=value \
  --query name=value \
  --header Idempotency-Key=value \
  --body-json '{...}'
```

Families: `ad-account`, `ad-groups`, `ads`, `campaigns`, `conversions`, `custom-audiences`, `files`, `insights`, and `targeting`.

Examples:

```bash
openai-ads-safe-agent-cli api campaigns list-campaigns --query limit=10
openai-ads-safe-agent-cli api targeting get-geo-lookup --query q="San Francisco" --query limit=5
openai-ads-safe-agent-cli --plan-out plan.json api campaigns create-campaign --body-json '{"name":"Test","status":"paused"}'
```

Apply shape for writes:

```bash
openai-ads-safe-agent-cli --apply --yes --plan-in plan.json --ack-no-snapshot --ack-irreversible api campaigns create-campaign --body-json '{"name":"Test","status":"paused"}'
```

## Measurement

```bash
openai-ads-safe-agent-cli measurement events-list
openai-ads-safe-agent-cli measurement pixel-guide
openai-ads-safe-agent-cli measurement image-tag-build --event order_created --data-type contents --data amount=2599 --data currency=USD
openai-ads-safe-agent-cli --plan-out conversion-plan.json measurement conversions-send --events-json '[{"id":"evt_1","type":"order_created"}]'
```

## Product feeds and targeting guides

```bash
openai-ads-safe-agent-cli product-feeds guide
openai-ads-safe-agent-cli targeting guide
```
