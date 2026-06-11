# Troubleshooting

## Common checks

- Missing config
  - Error text shows required fields are missing.
  - Fix by filling `.env` and rerunning `auth check`.
- Auth check fails
  - Confirm token and domain are correct.
  - Confirm the token can call read endpoints in your Pipedrive account.
- API call errors
  - Use the `--output json` response and check `error_type` and `error`.

## Error output

The tool should always print one JSON object in JSON mode.

## Keep secrets safe

- Do not share token values.
- Use a copy of your `.env` without real tokens for support.
