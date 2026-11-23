# Run your first Awin Publisher read

Install from the tool folder with Python 3.12 or later:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
awin-publisher-safe-cli --version
```

Use the [setup guide](onboarding.md) to add your token. Check the account and then list joined programs. Replace `PUBLISHER_ID` with the publisher you chose.

```bash
awin-publisher-safe-cli --env-file .env --output json auth check
awin-publisher-safe-cli --env-file .env --output json accounts list
awin-publisher-safe-cli --env-file .env --output json programs list --publisher-id PUBLISHER_ID --relationship joined
```

Check the account name and publisher ID before trusting the program list. From there, you can [find offers, run reports, or download a feed](command_reference.md). For order submissions, [prepare a plan and wait for approval](safety_model.md).
