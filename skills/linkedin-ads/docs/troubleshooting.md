# Fix a LinkedIn Ads problem

Start with `linkedin-ads-api-tool --output json auth check`. Check the result for the account you want to use before trying a report or a change.

| What you see | What to check |
| --- | --- |
| Missing token | Use [account setup](onboarding.md) to add a token to the settings file or save one with `auth token set`. If you used `--env-file`, pass the same path on your next command. |
| `401` | Check whether the token expired or belongs to the wrong LinkedIn app. Get a new token through the approved app flow and save it locally. |
| `403` | Check the approved LinkedIn product, the token permissions, and the member's role on this ad account. Reports need `r_ads_reporting`. |
| Empty report | Check account access and the report dates. LinkedIn can return an empty report when there is no activity or when the token lacks access to the data. |
| `404` or `410` | Check the account or item ID, the LinkedIn API version, and whether LinkedIn offers that endpoint for your app. |
| Rejected API version | Check the [LinkedIn version schedule](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/migrations). The tool defaults to `202605` and Rest.li `2.0.0`. See [optional settings](onboarding.md#optional-settings) for how to change them. |
| `refused: true` | Read the exact reason and check the [approval guide](safety_model.md). A refusal stops the request before it goes to LinkedIn. |
| Lost reply after a write | Read the affected item first. Use its current state to decide what to do next. |

Use `--verbose` for the request line and timing. Keep credentials and private account data out of anything you share.
