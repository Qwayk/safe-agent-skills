# Quickstart

Start by asking the agent to list Azure resource groups and flag anything that looks public, expensive, or security-sensitive before it prepares any change.

A good first ask is:

```text
Use the Azure skill to list the resource groups in this subscription, summarize anything that looks risky, and stop before making any change.
```

If you want examples before commands, start with [What this skill can help you do](use_cases.md). If setup is not finished yet, use [Set up your account step by step](onboarding.md).

## What you will do first

You will make one small read against Azure, confirm the token can see the expected subscription or resource group, and keep the result read-only. This is the safest first check because it proves the connection and target before any plan or live change exists.

## 1) Check local setup

```bash
# Create .env locally and fill AZURE_API_TOKEN and endpoints, then run:
qwayk-azure-safe-agent-cli auth check
```

This does not change Azure. It only tells you whether the local settings file has the fields the tool needs.

## 2) Verify command coverage

```bash
qwayk-azure-safe-agent-cli inventory summary
```

This confirms the command catalog is built from the pinned Azure REST API spec snapshot. It helps the agent choose a real service command instead of guessing from memory.

## 3. Run one small first read

Create `read.json` with the real subscription or resource group you want to inspect:

```json
{
  "path": {
    "subscriptionId": "<subscription-id>",
    "resourceGroupName": "<resource-group>"
  },
  "query": {
    "api-version": "2024-01-01"
  }
}
```

Then ask the agent to pick the matching read operation from the catalog and run it:

```bash
qwayk-azure-safe-agent-cli <service-command> <operation-name> \
  --input-json read.json
```

Use `<service-command>` and `<operation-name>` from the generated Azure command list. If the exact operation name is not obvious, ask the agent to inspect the inventory summary and command guide first, then run only the read.

## 4. Stop before anything risky

Do not move from a read into a change in the same step. For Azure, risky work can affect access, public networking, spend, secrets, compute, databases, or deletion behavior. Ask the agent to summarize what it found, what it would change, and what record it would leave before it prepares a write plan.

When you are ready to prepare a change, keep it as a reviewed plan first:

```bash
qwayk-azure-safe-agent-cli <service-command> <write-operation-name> \
  --input-json write.json \
  --plan-out plan.json
```

Live writes need `--plan-in --apply --yes` before the tool sends a change. Higher-risk operations can also need `--ack-no-snapshot` or `--ack-irreversible`.

## What a useful first result includes

A useful first result should tell you which subscription or resource group was checked, whether the command was read-only, what resources or settings were returned, and whether anything looks risky enough to review. Sensitive read results should hide secret-like values instead of printing them.

## Where to go next

- For plain-English examples, open [What this skill can help you do](use_cases.md).
- For setup help, open [Set up your account step by step](onboarding.md).
- For exact commands, open [Command guide](command_reference.md).
- For safety details, open [Safety model](safety_model.md).
