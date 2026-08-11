# Configuration

This tool uses one local token and one optional timeout setting.

## Files

- `.env`: local-only settings file.
- `.env.example`: placeholder version to copy from.

The onboarding command creates a missing `.env` with file mode `0600`.

## Environment variables

- `GIANTPANDA_API_TOKEN`
  - Required for read and write commands.
  - Must be a real token value, not a placeholder.
- `GIANTPANDA_TIMEOUT_S`
  - Optional.
  - Default is `30`.
  - Must be a positive number.

## Precedence

Environment variables from the process override values in `--env-file`.

## Private outputs

Plan and receipt files are written using mode `0600`.
