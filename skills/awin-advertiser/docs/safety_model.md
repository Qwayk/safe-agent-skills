# Safety model

This skill is built to stay safe by default.

## What happens before live changes

- Read commands do not change the Awin account.
- Write commands start in dry-run mode unless you explicitly ask to apply.
- Live writes need `--apply --yes --ack-irreversible --plan-in`.
- Batch and file-based writes can use a saved plan file so apply only happens against the exact reviewed input.

## What this means in normal language

- Nothing changes just because you asked for a preview.
- The skill is designed to stop when setup is missing, the plan changed, or the action is not ready to apply yet.
- After a real write, the tool can save a receipt so you have a record of what happened.
- Current write families leave a review trail, but they do not promise a broad saved before-state or automatic restore path.

## Two layers of safety

- Tool safety: the CLI keeps write steps explicit and deterministic.
- Review safety: your human reviewer or agent decides whether the change is actually the right business move.

## What to expect from your agent

- A short plain-English summary first.
- A clear note about whether anything changed.
- Proof-file paths when the action produced a plan, receipt, or audit log.
- A refusal or block message when setup, safety gates, or validation are not ready yet.
