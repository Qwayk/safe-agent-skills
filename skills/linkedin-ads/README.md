# LinkedIn Ads

**Capability:** Reads + careful changes

LinkedIn Ads is where B2B campaign work often depends on the right account access, product approval, targeting rules, lead forms, and tracking setup.

This skill helps an agent check LinkedIn Ads access, review accounts, campaigns, creatives, leads, conversions, targeting, analytics, previews, and tracking tags, and prepare careful changes before they go live.

Use it for questions like: "Which ad accounts can this token see?", "What campaign groups and creatives should we review?", "Can you pull one analytics report?", "Are lead forms or conversions accessible?", or "What LinkedIn approval gate is blocking this job?"

LinkedIn Ads access can fail even when the command is correct, because product approval and account permissions matter. Reads can run live when the token allows them, create and update flows start as dry-run plans, higher-risk changes need stronger approval, and write applies still need explicit no-snapshot approval because this runtime does not save provider-side before-state first.

A good first ask is: "Check the LinkedIn Ads connection, list the ad accounts I can see, show one campaign report, and stop before any writes."

## Start here first

- Want ideas for real LinkedIn Ads work? [What you can do with LinkedIn Ads](docs/use_cases.md)
- Need setup? [Connect your LinkedIn Ads account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check token health, product approval, and ad-account access before you try real LinkedIn work.
- Review ad accounts, account users, campaign groups, campaigns, creatives, analytics, previews, leads, conversions, targeting, and tracking tags.
- Plan careful create, update, delete, batch, and permission-changing actions across supported LinkedIn Ads families.
- Surface private, access-gated, tier-gated, and live-unverified areas clearly instead of hiding them behind guesswork.
- Reach the documented LinkedIn Ads families through explicit commands instead of hidden generic calls.

## What access this skill needs

- A valid LinkedIn Ads access token.
- The right LinkedIn product approvals and scopes for the families you want to use.
- Ad account IDs, URNs, or other LinkedIn resource IDs for many jobs.
- Extra approval from LinkedIn for restricted areas like Matched Audiences, Audience Insights, Media Planning, or Company Intelligence.

## Install and first run

Install slug: `linkedin-ads`

Ask your agent to install the `linkedin-ads` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@linkedin-ads -g -y
```

Then try a safe first ask like:

```text
Check the LinkedIn Ads connection, list the ad accounts I can see, show one campaign report, and stop before any writes.
```

## How this skill stays safe

- Operations marked as reads run live, including LinkedIn actions that are read-like even when they use `POST`.
- Non-read operations start as plans first and do not hit LinkedIn live unless you pass the required apply flags.
- Every live LinkedIn write needs `--apply --ack-irreversible`, and delete, batch-write, or permission-changing actions also need `--yes`.
- Write applies still need explicit no-snapshot approval because this runtime does not save provider-side before-state or restore points first.
- Gate labels like `access-gated`, `private-api-gated`, `tier-gated`, and `live-unverified` stay visible in the coverage docs and command outputs.
- Plans, local run history, docs, tests, and the API coverage ledger all live in this repo.

## What it covers today

This skill covers:

- ad account, campaign group, campaign, creative, analytics, preview, conversion, lead, targeting, tracking, and insight-tag families
- explicit support for many restricted LinkedIn Ads areas when the app and token already have the needed approval
- dry-run write planning plus local run-artifact proof for write-capable operations

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the account, URNs, payload, and approval-gate labels before apply.
- Reads can run live immediately when the token and LinkedIn product approval allow them.
- Standard writes need `--apply --ack-irreversible`.
- Delete, batch-write, and permission-changing actions also need `--yes`.
- Some higher-risk apply flows also need a saved-plan recheck with `--plan-in`.
- The live write path still needs explicit no-snapshot approval because no provider-side snapshot is saved first.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Saved plans can be rechecked with `--plan-in`.
- Local run history lives under `.state/runs/`.
- Redacted example outputs, docs, tests, and the API coverage ledger are all in this repo.

## Limits

- LinkedIn product approvals and scopes can block live access even when the CLI wiring is already present.
- Some supported families are still marked `live-unverified` because this repo does not store approved customer credentials.
- This runtime does not save provider-side before-state or automatic restore points for LinkedIn writes.
- Restricted LinkedIn private APIs can still deny live calls even when they appear in the command catalog.

## Helpful docs

- [Browse all LinkedIn Ads docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
