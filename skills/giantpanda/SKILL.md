---
name: giantpanda
description: Read traffic and earnings for GiantPanda parked domains and review a plan before adding domains.
---

# GiantPanda

Use this skill for parked-domain stats or to prepare a plan to add names to a GiantPanda account. Registration, DNS, transfers, payouts, and billing are separate work.

For stats, use `giantpanda domains stats --start-date YYYY-MM-DD --end-date YYYY-MM-DD`. Read every page before totaling the results. Use `giantpanda onboarding` when settings are missing. Use the same `--env-file` for later commands. `auth check` checks for a token locally. The stats request checks account access.

For a domain add, run `giantpanda domains add --domain example.com` to save a local plan. Show the exact names and explain that the tool cannot undo the add. Wait for approval. Apply with `--apply --plan-in <path> --approve-plan <id> --ack-no-snapshot` and the same domain names and settings. A changed token or an old plan needs a fresh review.

After apply, read the saved receipt. Report the names GiantPanda says it added and the names that were already there. If the reply is lost or leaves names unconfirmed, check those names in the dashboard before asking for another approval. Keep tokens and account data private.
