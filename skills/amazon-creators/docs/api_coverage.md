# API coverage

This tool provides four catalog reads through `https://creatorsapi.amazon/catalog/v1`. The original Issue #404 check was on June 4, 2026. The November 23 local audit checked the current [setup and search definitions](references.md).

## Coverage

| API operation | CLI command | Key resource/locale flags |
|---------------|-------------|--------------------------|
| `GetBrowseNodes` | `amazon-creators-api-tool browse-nodes describe --browse-node-id <id> [--apply] [--resource | --resource-preset]` | `--resource` ▸ BrowseNodeInfo, BrowseNodes; presets: `browse-basic`, `full` |
| `GetItems` | `amazon-creators-api-tool items get --item-id <id> [--apply] [--item-id-type ASIN] [--resource | --resource-preset | --locale]` | default preset: `book-media` (the simplified `items` output surfaces `asin`, `title`, `binding`, `product_group`, `classifications`, `content_info`, `technical_info`, `parent_asin`, and `variation_summary`); additional resource names can be added |
| `GetVariations` | `amazon-creators-api-tool variations get --asin <parent> [--apply] [--variation-count] [--variation-page] [--resource | --resource-preset]` | preset bundles + explicit resources cover the simplified variation `items`, which share the same fields as `items get` plus any available variation metadata (`--item-id` is accepted as an alias) |
| `SearchItems` | `amazon-creators-api-tool search --keywords "<query>" [--apply] [--item-count] [--item-page] [--resource | --resource-preset]` | `book-media`, `search-lens`, or `inventory-view` presets plus any of the eight resources; includes locale override and simplified `items` output (`--max-results` and `--page` are accepted as aliases) |

Every command supports `--include-raw` to surface the raw API payload and `--locale` to override `AMAZON_CREATORS_LOCALE`.

Each command previews the read by default. `--apply` sends it after approval. With `--plan-in`, the current account, endpoint, and request must match the saved preview. Results include errors when Amazon reports them. Search returns product links and the number of matches when Amazon supplies those fields.

High-level resource vocabulary (all supported by the `--resource` flag):

- `BrowseNodeInfo`
- `BrowseNodes`
- `Images`
- `ItemInfo`
- `OffersV2`
- `ParentAsin`
- `SearchRefinements`
- `VariationSummary`
