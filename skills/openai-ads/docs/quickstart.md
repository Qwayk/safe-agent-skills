# Check your first campaign

Open the downloaded tool folder, make a Python environment, and install the CLI:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/openai-ads-safe-agent-cli onboarding
```

Add your Ads Manager key to the file onboarding shows. Then confirm it is the right account and list up to ten campaigns:

```bash
.venv/bin/openai-ads-safe-agent-cli auth check
.venv/bin/openai-ads-safe-agent-cli api campaigns list-campaigns --query limit=10
```

Ask the agent to point out which campaigns are paused and which are active. For spend and campaign results, use the matching Insights command. See the [command guide](command_reference.md).

## Preview a paused campaign

If you want to try planning, this command saves an example with a lifetime budget of 10,000,000 micros, which is 10 units of the account currency. Change the name and budget to match what you actually intend. This command prepares a plan without creating a campaign.

```bash
.venv/bin/openai-ads-safe-agent-cli --plan-out plan.json api campaigns create-campaign --body-json '{"name":"West Coast test","status":"paused","budget":{"lifetime_spend_limit_micros":10000000}}'
```

Read the [approval guide](safety_model.md) before using a saved plan to create the campaign. If you use a separate settings file, keep the same file for the read, plan, and apply.
