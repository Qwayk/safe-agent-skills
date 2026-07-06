# Engineering Notes

The CLI uses a pinned generated inventory from the official OpenAI Ads OpenAPI spec. The parser creates explicit `api <family> <command>` subcommands from that inventory at startup.

Manual command families cover official measurement docs that sit outside the Advertiser API spec:

- `measurement events-list`
- `measurement pixel-guide`
- `measurement image-tag-build`
- `measurement conversions-send`
- `product-feeds guide`
- `targeting guide`

There is no raw request bridge.
