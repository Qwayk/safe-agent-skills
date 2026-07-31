# Authentication

This slice uses one environment key for both read and apply:

- `SAV_API_KEY` (required for all reads and required on apply)
- `SAV_TIMEOUT_S` (optional HTTP timeout in seconds)

## Configuration source

The CLI reads values from the process environment and the file selected by `--env-file`.
The process environment takes precedence.

## Read behavior

- Without `SAV_API_KEY`, reads return a validation error.
- `SAV_API_KEY` is validated only when required by command mode.
- Read operations do not need a signing key and still require the fixed host and API key.
- The `APIKEY` header is sent only to the fixed SAV operation URL. Redirects are disabled, so the key is never forwarded to a redirect target.
- Every response outside 2xx is treated as a provider failure.
- Malformed/invalid env input fails command parsing before any network request.
- Timeout values must be a finite positive number from either `SAV_TIMEOUT_S` or `--timeout-s`.
