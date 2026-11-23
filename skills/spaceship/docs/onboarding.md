# Connect your Spaceship account

Create a key and secret in [Spaceship API Manager](https://www.spaceship.com/application/api-manager/). Give the key the permissions needed for your task. For example, the exact-domain price lookup needs `domains:read`, and requesting a renewal or transfer needs `domains:billing`. [Spaceship API permissions](https://docs.spaceship.dev/)

Run onboarding from the tool folder:

```bash
qwayk-spaceship-safe-agent-cli --output json onboarding
```

Open the private settings file it creates and fill in `SPACESHIP_API_KEY` and `SPACESHIP_API_SECRET`. Keep keys out of chat and Git. If you already have a settings file, you can check or set its permissions with `chmod 600 .env`. Use your own filename if it differs.

Run the connection command that onboarding prints. If you use `--env-file`, keep using that file on later commands. Without that flag the tool uses `.env`. Matching variables already set in your shell take priority. The timeout defaults to 30 seconds and can be set with `SPACESHIP_TIMEOUT_S` or the command flag `--timeout-s`.

`auth check` checks your local settings. To check account access and permissions, run the first read in the [quickstart](quickstart.md). If Spaceship refuses a request, check the selected file, key, and permissions. Use `--verbose` to see the request and reply status when needed.
