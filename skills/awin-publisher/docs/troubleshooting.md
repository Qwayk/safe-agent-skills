# Troubleshooting

## Debug HTTP

- Use `--verbose` to print request and response status lines to stderr.
- Confirm `AWIN_API_TOKEN` is set and not expired.

## Debug JSON errors

- `--output json` gives structured errors without stack traces.
- Add `--debug` to print Python stack traces for unexpected runtime errors.

## Secrets

- Do not paste tokens or secret output.
- If you suspect a leaked secret, rotate immediately and update `.env`.
