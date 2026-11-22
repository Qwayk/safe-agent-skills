# Quickstart

Run `pinterest-api-tool --output json --version` first. If you are working from a checkout, install the tool from its folder.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Use `.venv/bin/pinterest-api-tool` from that folder, or activate `.venv` before running the commands below. See [account setup](onboarding.md) for the settings file.

## Read one board

```bash
pinterest-api-tool auth check
pinterest-api-tool boards list --limit 1
pinterest-api-tool board-pins list --board-id BOARD_ID --limit 5
```

Use the board ID from the list. To continue, pass the returned value with `--bookmark`. To save the account’s boards and pins locally, run `pinterest-api-tool audit snapshot --out-dir OUT_DIR --skip-analytics`.

## Preview a pin edit

This command shows the request without sending it. Use an actual pin ID only after you have checked the account.

```bash
pinterest-api-tool pins update --id PIN_ID --title "New title"
```

To save a preview for approval, add `--plan-out plan.json` before `pins`. The tool reads the signed-in account and records it in the file. After you approve the exact change, run the same command with `--apply --yes --ack-no-snapshot --plan-in plan.json` in place of `--plan-out plan.json`. [Approval and recovery](safety_model.md)
