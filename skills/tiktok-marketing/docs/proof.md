# What has been checked

## November 23, 2026 local checks

Both local copies passed 29 tests from source and 29 tests after a fresh install. I built a Python source archive and wheel for each copy and checked that both packages included the [list of 240 commands](../src/tiktok_marketing_safe_agent_cli/data/official_operations_v1_2026-05-24.json). The installed CLI loaded all 240 commands from outside the checkout.

I ran the [quickstart](quickstart.md) with simulated TikTok replies. Onboarding created the chosen settings file. The account check returned a name and ID. The report returned two pages for the same account and dates, and the tool reported a TikTok error when the provider returned an error code with an HTTP success status.

A campaign pause made no request before approval. The tool stopped when the approval to proceed without a saved copy was missing. It also stopped when the submitted campaign ID differed from the saved plan. With the matching plan and all approvals, it sent one request and recorded the simulated provider reply. A separate read showed the new campaign status. Unchanged plans made by the earlier GitHub version also passed simulated checks for a campaign pause, an upload, and a token exchange.

Both skill files and the Python type check passed. Seven existing code style warnings remain. These checks used simulated replies and made no attempts to contact TikTok.

## Earlier checks and examples

The June 4, 2026 local baseline checked command registration, authentication, write refusals, multipart plans, and run history. The June 11, 2026 check reviewed the docs against the local tool. The tool version was `0.1.0` and it used the same TikTok operation list dated May 24, 2026.

These files preserve earlier sample output:

- [Version response](examples/outputs/version.json)
- [Account check response](examples/outputs/auth_check.json)
- [Saved plan](examples/plan.example.json)
- [Write refusal](examples/receipt.example.json)

## Live checks

Live account access depends on the app, token, ad account, and requested feature. See [API coverage](api_coverage.md) for the available commands and which calls still need live checks. The [approval guide](safety_model.md) explains what the tool can confirm after a write.
