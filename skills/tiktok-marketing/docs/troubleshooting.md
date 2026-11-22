# Fix a TikTok Marketing problem

Start with `tiktok-marketing-api-tool --output json auth check`. Use the same `--env-file` as your report or planned change. Keep secrets out of anything you share.

| What you see | What to check |
| --- | --- |
| Missing app ID, secret, or token | Run [onboarding](onboarding.md) and fill the missing values. If you saved a token file, check that it is beside the settings file you chose. |
| Empty list of ad accounts | Check which accounts authorized the app. Use an account ID from the list before trying a report. |
| TikTok returned an error code | Read the message. Check the token, the account permissions, and the [inputs that the command accepts](command_reference.md). |
| No report rows | Check the account and dates. If the report has more pages, read each page before drawing a conclusion. |
| The tool returned a plan | Add `--live` before `api` to send a read. For a write, follow the [approval steps](safety_model.md). |
| `refused: true` or plan mismatch | Read the reason. If the request or credentials changed, save and review a new plan. |
| A write timed out | Read the campaign or other affected item first so you know whether the change took effect. |

Use `--verbose` to see request timing on stderr. Use `--debug` for local debugging when the normal error lacks detail.
