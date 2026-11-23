# Amazon Creators command guide

Start with [account setup](onboarding.md) or [your first search](quickstart.md).

## Account setup

```bash
amazon-creators-api-tool onboarding
amazon-creators-api-tool onboarding --apply
amazon-creators-api-tool auth token fetch
amazon-creators-api-tool auth token fetch --apply
amazon-creators-api-tool auth check
amazon-creators-api-tool auth token status
```

- `--env-file <file>` selects a settings file for the command. Without this option, shell settings take priority over the default `.env`.
- `onboarding --no-write-env` shows settings without writing a file, even with `--apply`.
- `auth token fetch --force --apply` gets a new token even when the account has a usable one.
- `auth check` checks the saved token locally. `auth token status` shows saved token metadata. A catalog read checks account access at Amazon.
- `auth token set --file <file>` is a preview-only helper. Use `auth token fetch` for setup.

## Catalog commands

| What you need | Command and options |
| --- | --- |
| Find a product | `search --keywords <query>`. Use `--item-count` or `--max-results` for 1 to 10 items and `--item-page` or `--page` for pages 1 to 10. |
| Look up item details | `items get --item-id <Amazon item ID>`. Repeat the flag for several items. The default ID type is `ASIN`. |
| See product variations | `variations get --asin <parent ASIN>`. Use `--variation-count` and `--variation-page` to choose a page. `--item-id` is an alias for `--asin`. |
| Describe a category | `browse-nodes describe --browse-node-id <id>`. Repeat the flag for several categories. |

Use `--locale <code>` to select a marketplace for a request. Use `locales list` or `locales show --locale <code>` to see the settings for a locale.

Use `--resource <name>` to add fields for an operation. It accepts repeated flags and comma-separated values. Use `--resource-preset <name>` for a set of fields. Search defaults to `search-lens`, item and variation lookups to `book-media`, and category lookups to `browse-basic`. Other sets include `inventory-view` and `full`, where supported. See [API coverage](api_coverage.md) for resource names.

## Preview, run, and check an Amazon request

- `--plan-out <path>` saves the preview. Run again with `--apply` after approval. If you include `--plan-in <path>`, the command checks the selected account, endpoint, and request against that preview before sending anything.
- `--receipt-out <path>` saves the result of a complete or partial catalog read. A partial result includes the products and errors. An error-only reply has no successful receipt.
- `--include-raw` includes the API response alongside the simpler results. `--output json` is the default. Use `--output text` for text setup instructions.
- `--timeout-s <seconds>` changes the timeout. `--verbose` shows requests and status codes on stderr. `--debug` is for troubleshooting Python errors locally.
- `--no-artifacts` skips the default files in `.state/runs/`. `--run-id`, `--artifacts-dir`, and `--log-file` let you choose how to find a run again. Use `runs list --limit <count>` or `runs show --run-id <id>` to read saved run information.

The CLI still accepts `--yes` and `--ack-irreversible`. Catalog reads and the approved setup actions don’t need them.
