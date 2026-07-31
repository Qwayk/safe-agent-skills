# Jobs and batches

This tool does not ship a jobs runner.

Use one command at a time and run write commands in plan-apply mode.

- Read commands are safe and can run directly.
- Write commands need `--plan-out` then `--apply --yes --plan-in` with the command's acknowledgements.

The two CSV files in `examples/` are docs-only refusal examples.
They are not action templates and should not be interpreted as runnable input.
