# Jobs and batches

Batch operations are run from a CSV file:

```bash
amazon-pa-api-tool jobs run --file jobs.csv
```

## Safety rules

- Jobs are strict by default.
- The runner stops on the first error and exits non-zero.
- Output is exactly one JSON summary object.

## CSV format

The CSV must include an `action` column.

Supported actions:
- `product.search` (requires `query`; optional: `search_index`, `limit`, `item_page`)
- `product.get` (requires `asin` or `asins`)
- `product.variations` (requires `asin`; optional: `variation_page`, `variation_count`)
- `browse.get` (requires `browse_node_id` or `browse_node_ids`)

Tip: add `--include-raw` to include raw PA-API responses in each job result.

Example:

```csv
action,query,search_index,limit,item_page
product.search,cast iron skillet,All,3,1
```

## Multi-ID batching + `--yes` guard

Some PA-API operations only allow up to 10 IDs per request (example: `GetItems`, `GetBrowseNodes`).

- If a row expands to more than one PA-API request, the tool errors unless you pass `--yes`.
- In `jobs run`, batching is fixed to the PA-API max per request (10 IDs) with a hard cap of 10 requests per row.
- To control `--batch-size` / `--max-requests`, run `product get` / `browse get` directly (not via jobs).

### `product.get` CSV columns

- `asin`: single ASIN
- `asins`: multiple ASINs in one cell, pipe-separated (example: `B000000000|B000000001|B000000002`)

### `browse.get` CSV columns

- `browse_node_id`: single browse node id
- `browse_node_ids`: multiple browse node ids in one cell, pipe-separated (example: `3040|3045`)
