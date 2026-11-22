# OpenAI Ads commands

Put shared flags, such as `--env-file`, `--output json`, `--plan-out`, and `--plan-in`, before the command. Use [Onboarding](onboarding.md) to choose the account and [Quickstart](quickstart.md) for a full worked example.

| What you want | Command |
| --- | --- |
| Set up a local settings file | `openai-ads-safe-agent-cli onboarding` |
| Check the connected Ads account | `openai-ads-safe-agent-cli auth check` |
| List the 40 Advertiser API commands | `openai-ads-safe-agent-cli api list` |
| List ten campaigns | `openai-ads-safe-agent-cli api campaigns list-campaigns --query limit=10` |
| Read conversion settings | `openai-ads-safe-agent-cli api conversions list-conversion-event-settings` |
| Look up a location | `openai-ads-safe-agent-cli api targeting get-geo-lookup --query q=Seattle --query limit=5` |
| List conversion event types | `openai-ads-safe-agent-cli measurement events-list` |
| Get Pixel setup steps | `openai-ads-safe-agent-cli measurement pixel-guide` |
| Build an example image tag with the Pixel ID hidden | `openai-ads-safe-agent-cli measurement image-tag-build --event order_created --data-type contents --data amount=2599 --data currency=USD` |
| Review product-feed setup | `openai-ads-safe-agent-cli product-feeds guide` |
| Review campaign targeting | `openai-ads-safe-agent-cli targeting guide` |
| Find a saved run | `openai-ads-safe-agent-cli runs list` |
| Open a saved run | `openai-ads-safe-agent-cli runs show --run-id example-run` |

Use `--path-param name=value` for an ID in the URL, `--query name=value` for a filter, and `--body-file` or `--body-json` for the payload. See the [API coverage table](api_coverage.md) for route names.

For server-side events, use `measurement conversions-send --events-file` with a file that follows the [Conversions API guide](https://developers.openai.com/ads/conversions-api). The default plan is for validation only. For account changes or real conversion sends, read [Approvals and receipts](safety_model.md).
