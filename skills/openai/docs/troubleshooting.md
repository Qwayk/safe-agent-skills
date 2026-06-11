# Troubleshooting

## Debug HTTP

Use `--verbose` to log HTTP start/end lines to stderr. Hidden secrets are never printed (no Authorization headers, no tokens).

## Debug errors

By default the CLI prints a single JSON error object. Add `--debug` to show Python stack traces when you need extra detail.
