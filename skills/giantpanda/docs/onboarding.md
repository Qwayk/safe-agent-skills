# Set up GiantPanda

Run `giantpanda onboarding` in the folder where you want to keep your settings. It creates a private `.env` file if the file is missing. For a different file, run `giantpanda --env-file account.env onboarding`. Existing settings stay in place.

Copy your token from the Authentication tab in the [GiantPanda API docs](https://account.giantpanda.com/docs/client-api/) and set `GIANTPANDA_API_TOKEN` in that private file. Keep the token out of chat, logs, and shared files. Run the `auth check` command printed by setup. It uses the same settings file. A token set in the shell takes priority over the file.

`auth check` tells you whether the tool found a token on your machine. The first stats request checks whether GiantPanda accepts it. If that request fails, check that the token is for the right account and that the account has access to stats. A redirect stops the request. Keep the token on the official GiantPanda host.

`GIANTPANDA_TIMEOUT_S` is optional and defaults to 30 seconds. Use a positive number. The [README](../README.md#get-your-first-report) shows how to ask for your first report.
