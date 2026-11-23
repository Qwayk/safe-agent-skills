# Connect your Awin Publisher account

Create a private settings file, add the token for the job, then check which publisher accounts it can access.

```bash
awin-publisher-safe-cli --env-file .env onboarding
```

Open the file locally and fill in `AWIN_API_TOKEN`. Use the next command that onboarding prints. For `.env`, it is:

```bash
awin-publisher-safe-cli --env-file .env --output json auth check
```

Check the publisher account in the reply before running a report or downloading a feed. When you pass `--env-file`, the CLI uses that file’s Awin settings. Without the flag, shell settings can override the default `.env` file, which is useful in CI. Keep tokens and settings files out of chat and Git.

## Which key to use

- `AWIN_API_TOKEN` covers accounts, programs, offers, transactions, reports, tracking links, and enhanced feeds. The enhanced feed sends the bearer token in the authorization header. Other publisher commands may also send it in the query as documented in [API coverage](api_coverage.md).
- `AWIN_FEED_API_KEY` is for `feeds legacy-list` and looking up a legacy download by feed ID. Awin puts this key in legacy download URLs. Keep those URLs private.
- `AWIN_PROOF_OF_PURCHASE_API_KEY` is for order submission and uses the `x-api-key` header. Awin and the advertiser must first enable the publisher for that program. [Order approval steps](safety_model.md)
- `AWIN_TIMEOUT_S` sets the request timeout in seconds. The default is 30. Use `--timeout-s` to change it for one run.

## If a command stops

- If a settings file is missing, check the path or run onboarding with that path. If the account is wrong, check the file and the publisher ID before continuing.
- If an enhanced feed is unavailable, check the publisher, advertiser, and locale against [Awin’s current feed list guide](https://help.awin.com/developers/docs/downloading-a-list-of-your-product-feeds). Awin’s guide uses the publisher ID and separate feed key to open the current list. The CLI still ships the earlier legacy list command.
- Use `--verbose` to see request and response details with credentials hidden. Use `--debug` if you need a Python stack trace for an unexpected error.
- If a submission may have reached Awin, check the orders before trying again. If a key appeared in an output, rotate it before using that key again.
