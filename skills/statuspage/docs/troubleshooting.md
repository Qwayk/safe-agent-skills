# Troubleshooting

## Common issues

### Missing base URL

- Make sure your `.env` contains `STATUSPAGE_BASE_URL=https://status.somevendor.com`.

### HTTP errors / invalid JSON

- Use `--verbose` for HTTP logs (to stderr).
- Use `--debug` for stack traces.
