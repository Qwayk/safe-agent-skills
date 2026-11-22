# Old sign-in and settings

This page explains an existing setup. Reddit requires its approval before Data API access. The old setup used `auth login` to open Reddit’s consent page and `auth exchange-code` to save the returned token. The tool can record the temporary sign-in code in a local log and can save a failed reply as if it were a token. Use the [offline quickstart](quickstart.md) for this retired tool. [Reddit’s access rules](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy)

## Where settings were saved

The tool reads `.env` or the file given with `--env-file`. Environment variables take priority. Keep both settings and token files private.

| Setting | What it was for |
| --- | --- |
| `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_REDIRECT_URI` | The approved app’s sign-in details. A client secret was needed for apps that have one. |
| `REDDIT_CONTACT_USERNAME`, `REDDIT_USER_AGENT` | Reddit expects a descriptive User-Agent with the app and contact. The tool builds one from the contact username unless you set your own. |
| `REDDIT_OAUTH_SCOPES` | The permissions requested from Reddit. |
| `REDDIT_ACCESS_TOKEN` | An optional token that takes priority over the saved file. |
| `REDDIT_API_BASE_URL` | Defaults to `https://oauth.reddit.com`. |
| `REDDIT_OAUTH_AUTHORIZE_URL`, `REDDIT_OAUTH_TOKEN_URL` | Default to `https://www.reddit.com/api/v1/authorize` and `https://www.reddit.com/api/v1/access_token`. |
| `REDDIT_TIMEOUT_S` | Defaults to 30 seconds. |

`.state/token.json` sits next to the settings file. The tool uses a saved token with a future expiry or tries to refresh it if a refresh token is present. `auth token status` shows what is saved without showing token values. `auth token set`, `auth exchange-code`, and `auth refresh` can replace the saved file. See [approval and recovery](safety_model.md) for how settings affected old plans.
