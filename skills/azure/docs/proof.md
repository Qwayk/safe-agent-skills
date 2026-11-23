# Azure test results

## November 23, 2026 local checks

Fresh installs from the source folder and the local release folder each passed 34 tests with network access blocked. Both installed packages loaded 339 service commands and registered all 26,337 operations in the pinned inventory. The inventory has 340 service entries. The IoT Spaces entry has no operations.

The tests used simulated Azure replies to check sign-in and token selection, saved approvals, resource and location limits, and private values in replies. They checked that the tool keeps a receipt when a change is pending, Azure reports a failure, or a reply is lost. They also checked that the tool keeps the token on the approved host and avoids sending a write again after a lost reply. A separate install check created a private settings file and prepared an offline resource group change without sending it.

Azure sign-in and service calls still need a check on a real account. Start with the [first read](quickstart.md) after you have permission to use that subscription.

## Repeat the offline checks

From the tool folder, after installing it, run:

```bash
qwayk-azure-safe-agent-cli --output json --version
qwayk-azure-safe-agent-cli onboarding --no-write-env
qwayk-azure-safe-agent-cli inventory summary
python -m unittest -q
```

## Earlier examples

The June 28, 2026 inventory still uses Azure REST spec commit `ada8601c3b75c15f06f21e50f9368d9476229305`. The [coverage guide](api_coverage.md) lists the services and [the package inventory](../src/azure_safe_agent_cli/official_inventory.json) holds the exact operation names.

These examples show the earlier output format. The [approval guide](safety_model.md) explains the current plan and receipt fields.

- [Version](examples/outputs/version.json)
- [Access check](examples/outputs/auth_check.json)
- [Plan](examples/plan.example.json)
- [Receipt](examples/receipt.example.json)

Use `qwayk-azure-safe-agent-cli --output json auth check` to check the current connection. This may ask the local Azure CLI for a token. By default, the tool stores run records under `.state/runs/` when it writes them.
