# Troubleshooting

When Hacker News does not return what you expected, start by checking the target, the API response, and the exact JSON error. For this public read tool, most fixes are about the request itself: a missing ID, an empty result, a changed public record, a timeout, or an API root override.

Do not guess from an empty list or a `null` result. Ask the agent to fetch the actual record, show the error type, and explain whether the data is missing or the request needs to change.

A good first troubleshooting ask is: "Read the Hacker News error, explain what failed in plain English, and tell me the safest next check without inventing missing data."

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
