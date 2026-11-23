# Repeat Google Cloud work

Run one generated command at a time. For each write, specify the exact resource in the input, save a plan with `--bind-adc`, and get approval before running it. The CLI has no CSV batch runner. [Approval steps](safety_model.md)

If a batch runner is added later, each row must name an operation from `src/gcp_safe_agent_cli/gcp_discovery_inventory.json` and a clear target. Save a plan entry for each operation and keep the same approval requirements. Stop on missing targets or required values. Use the listed operations for every row.
