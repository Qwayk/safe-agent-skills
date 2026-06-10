# Safety model

This tool is built to stay safe by default.

## What happens before a risky change

- Read commands do not change the Awin account.
- Write commands start in dry-run mode unless you explicitly ask to apply.
- Risky writes need extra confirmation flags before the tool will continue.
- Batch and file-based writes can use a saved plan file so apply only happens against the exact reviewed input.

## What this means in normal language

- Nothing changes just because you asked for a preview.
- The tool is designed to stop when the setup is missing, the input changed, or the action is not safe enough to apply yet.
- After a real write, the tool can save a receipt so you have a record of what happened.

## Two layers of safety

- Tool safety: the CLI keeps write steps explicit and deterministic.
- Review safety: your human reviewer or AI agent decides whether the change is actually the right business move.

## What to expect from your AI agent

- A short plain-English summary first.
- A clear note about whether anything changed.
- Proof-file paths when the action produced a plan, receipt, or audit log.
- A refusal or block message when setup, safety gates, or validation are not ready yet.
