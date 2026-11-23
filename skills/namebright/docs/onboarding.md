# Connect your NameBright account

Request API access in NameBright under My Account → API Management. Add the IP address that will send requests. If your agent runs on another machine, use that machine's IP. NameBright's examples use an IPv4 address and a client ID in the form `account name:application name`. [NameBright help](https://help.namebright.com/faqs/portfolio-category-management/) · [NameBright client examples](https://github.com/NameBright/DomainApiClientExamples/tree/128b70a2b7348742b4a3b94a1d2e9d26251de199)

From the tool folder, run:

```bash
namebright-safe-cli --output json onboarding
```

Open the private `.env` file and fill in `NAMEBRIGHT_CLIENT_ID` and `NAMEBRIGHT_CLIENT_SECRET`. The timeout is 30 seconds by default. Use `NAMEBRIGHT_TIMEOUT_S` or the command flag `--timeout-s` if you need a different timeout. Keep credentials in the settings file or environment, away from chat and Git.

Follow the command onboarding prints. With the default file, it is:

```bash
namebright-safe-cli --output json auth check
```

If you choose another filename with `--env-file`, use it on each command. The tool uses the same variables from your shell first if they are set. It keeps the short-lived token in memory. Run `auth token` if you need to see the token's status.

If the connection fails, check the settings file, the client ID, API access, and the IP NameBright has on file. Use `--verbose` to see which request failed. After the connection works, follow the [quickstart](quickstart.md).
