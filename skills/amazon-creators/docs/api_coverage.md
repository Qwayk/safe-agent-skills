# API coverage

Last audited (UTC): 2026-06-04
Last verified (UTC): 2026-06-04

The tool targets the Amazon Creators Catalog API at `https://creatorsapi.amazon/catalog/v1`.
The four supported operations are mapped to explicit catalog commands with first-class resource controls.
The Issue #404 inventory is test-locked: the coverage suite now fails if any of the four operations or eight high-level resources drift out of the ledger.

| API operation | CLI command | Key resource/locale flags |
|---------------|-------------|--------------------------|
| `GetBrowseNodes` | `amazon-creators-api-tool browse-nodes describe --browse-node-id <id> [--apply] [--resource | --resource-preset]` | `--resource` ▸ BrowseNodeInfo, BrowseNodes; presets: `browse-basic`, `full` |
| `GetItems` | `amazon-creators-api-tool items get --item-id <id> [--apply] [--item-id-type ASIN] [--resource | --resource-preset | --locale]` | default preset: `book-media` (the simplified `items` output surfaces `asin`, `title`, `binding`, `product_group`, `classifications`, `content_info`, `technical_info`, `parent_asin`, and `variation_summary`); additional resource names can be added |
| `GetVariations` | `amazon-creators-api-tool variations get --asin <parent> [--apply] [--variation-count] [--variation-page] [--resource | --resource-preset]` | preset bundles + explicit resources cover the simplified variation `items`, which share the same fields as `items get` plus any available variation metadata (`--item-id` is accepted as an alias) |
| `SearchItems` | `amazon-creators-api-tool search --keywords "<query>" [--apply] [--item-count] [--item-page] [--resource | --resource-preset]` | `book-media`, `search-lens`, or `inventory-view` presets plus any of the eight resources; includes locale override and simplified `items` output (`--max-results` and `--page` are accepted as aliases) |

Every command supports `--include-raw` to surface the raw API payload and `--locale` to override `AMAZON_CREATORS_LOCALE`.

Each table entry describes the live flow: running without `--apply` produces a dry-run `plan`, while rerunning with `--apply` emits the simplified `items` data (under the `items` key for catalog calls) and records a `receipt` (and optional `receipt_out`) in `.state/runs/`.

High-level resource vocabulary (all supported by the `--resource` flag):

- `BrowseNodeInfo`
- `BrowseNodes`
- `Images`
- `ItemInfo`
- `OffersV2`
- `ParentAsin`
- `SearchRefinements`
- `VariationSummary`
