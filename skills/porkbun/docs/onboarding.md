# Connect your Porkbun account

Set up a private env file, then run a read to check your connection.

```bash
porkbun --version
porkbun --output json --env-file porkbun.env onboarding
```

Open `porkbun.env` and fill in `PORKBUN_API_KEY` and `PORKBUN_SECRET_API_KEY`. Use the same `--env-file` path on later commands. By default, the tool looks for `.env`. You can also start from [the example env file](../.env.example). Keep the file out of Git and the keys out of chat and shell arguments. Environment variables with the same names take priority over the file.

Onboarding creates a file only you can read and write (`0600`). It stops if the path points to a directory or symbolic link. The tool uses Porkbun's key pair and does not need an OAuth token.

```bash
porkbun --output json --env-file porkbun.env auth check
porkbun --output json --env-file porkbun.env domain get-domains
```

The first command checks whether Porkbun accepts the keys. Without keys it reports `authenticated: false` without contacting Porkbun. If you get a permission error, check that the key pair is correct and you enabled API access for the domain you want to manage. Use IP restrictions in Porkbun if they fit your setup. [Porkbun's API setup guide](https://kb.porkbun.com/article/307-getting-started-porkbun-api)

The default timeout is 30 seconds. Set `PORKBUN_TIMEOUT_S` or pass `--timeout-s` if needed. `PORKBUN_API_HOST` accepts `default` (`https://api.porkbun.com/api/json/v3`) or `ipv4` (`https://api-ipv4.porkbun.com/api/json/v3`).

For your first commands, see [Quickstart](quickstart.md).
