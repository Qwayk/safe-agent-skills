# Troubleshooting

## Common issues

### Wrong API root

- Use the default public root unless you have a specific mirror.
- Verify with `hacker-news-api-tool --output json auth check`.

### Missing item or user

- The Hacker News API returns `null` for missing records.
- The CLI turns that into a clear JSON error so downstream agents do not treat `null` as a good result.

### HTTP or JSON errors

- Use `--verbose` for HTTP logs to stderr.
- Use `--debug` for stack traces.
