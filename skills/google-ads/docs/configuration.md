# Configuration

This tool uses a `.env` file for configuration.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)

## Environment variables

- `GOOGLE_ADS_DEVELOPER_TOKEN` (required)
- `GOOGLE_ADS_CLIENT_ID` (required)
- `GOOGLE_ADS_CLIENT_SECRET` (required)
- `GOOGLE_ADS_REFRESH_TOKEN` (required)
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID` (optional; manager/MCC context)
- `GOOGLE_ADS_TIMEOUT_S` (optional; default: 30)
- `GOOGLE_ADS_EXTERNAL_WRITES_DISABLED` (optional; default: unset/false; set to `1` to refuse all external writes)
- `GOOGLE_ADS_WRITE_CUSTOMER_ID_ALLOWLIST` (optional; default: empty; comma-separated customer IDs allowed for writes)
- `GOOGLE_ADS_MAX_MUTATE_OPERATIONS_PER_REQUEST` (optional; default: 100; hard cap for batch operations)
- `GOOGLE_ADS_MAX_MUTATE_OPERATIONS_PER_RUN` (optional; default: 1000; hard cap per run)
- `GOOGLE_ADS_RETRY_MAX_ATTEMPTS` (optional; default: 3; bounded retries for retryable RPC errors)
- `GOOGLE_ADS_RETRY_BASE_DELAY_S` (optional; default: 1.0; deterministic exponential backoff base delay)

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.
