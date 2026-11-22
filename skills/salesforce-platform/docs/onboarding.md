# Connect your Salesforce org

You need a Salesforce org address and a REST API access token. Get the token from your approved Salesforce app. Salesforce recommends an External Client App for new setups. An existing Connected App can also issue a token. [Salesforce app setup](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_oauth_and_connected_apps.htm)

## Set your local settings

```bash
qwayk-salesforce-platform-safe-agent-cli onboarding
```

Set `SALESFORCE_INSTANCE_URL` to your org address, such as `https://your-domain.my.salesforce.com`. Onboarding creates a local settings file if needed. Use `--env-file` before the command to choose another file.

Set `SALESFORCE_ACCESS_TOKEN` in the settings file or shell, or save a token file you already have:

```bash
qwayk-salesforce-platform-safe-agent-cli auth token set --file token.json
qwayk-salesforce-platform-safe-agent-cli auth token status
```

Keep the access token and token file out of chat and Git. The tool stores the token under `.state/token.json` next to the selected settings file. It can also read the org address from that token file. Shell values take precedence over values in the settings file. The default API version is `67.0` and the timeout is 60 seconds. Set `SALESFORCE_API_VERSION` or `SALESFORCE_TIMEOUT_S` if you need a different value.

## Check the connection

Run the command printed by onboarding. It carries the settings file you chose. The default check is:

```bash
qwayk-salesforce-platform-safe-agent-cli --output json auth check
```

The check reads the limits for your org. Confirm the org address before you move on to [your first read](quickstart.md).

## If a command fails

- Check the selected settings file, org address, access token, and Salesforce permissions.
- For Knowledge articles, check that Salesforce Knowledge is enabled. Supply a language with `--header Accept-Language=en-US` and any required filters.
- Save large CSV or binary responses with `--download-to`. For supported blob uploads, pass a manifest with `--multipart-file`.
- Read the error before retrying a change. Use `--verbose` for HTTP messages or `--debug` for a stack trace. Keep private details in those logs on your computer.
