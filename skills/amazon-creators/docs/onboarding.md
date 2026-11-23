# Connect your Amazon Creators account

## Create your settings file

Run `amazon-creators-api-tool onboarding` to see the fields. Run `amazon-creators-api-tool onboarding --apply` to create a private `.env` file. The command leaves an existing file in place.

Fill in these values locally. Keep them out of chat and Git.

| Setting | What to enter |
| --- | --- |
| `AMAZON_CREATORS_CREDENTIAL_ID` | The Credential ID from Associates Central |
| `AMAZON_CREATORS_CREDENTIAL_SECRET` | The Credential Secret from Associates Central |
| `AMAZON_CREATORS_CREDENTIAL_VERSION` | The exact version Amazon issued, such as `3.1` |
| `AMAZON_CREATORS_LOCALE` | The marketplace locale, such as `en_US` or `en_GB` |
| `AMAZON_CREATORS_PARTNER_TAG` | Your Associates tracking tag for that marketplace |

[Register for Creators API](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/onboarding/register-for-creators-api) if you need credentials. Amazon uses the credential version to pick the sign-in endpoint. Your marketplace and tracking tag determine which catalog you ask for. Review [Amazon's account requirements](https://affiliate-program.amazon.com/creatorsapi/docs/) if you can sign in but cannot read the catalog.

For more than one account, keep a private settings file for each one. Put `--env-file /path/to/account.env` on each command. The named file supplies the settings. Without that option, shell settings take priority over the default `.env`.

## Get a token

Preview the token request, then use `--apply` after approval:

```bash
amazon-creators-api-tool auth token fetch
amazon-creators-api-tool auth token fetch --apply
amazon-creators-api-tool auth check
```

The tool gets a token from Amazon and saves it in a private file under `.state/` next to your settings. A token is reused only when it matches the credentials and has time left. Earlier caches without the account check need a fresh fetch. A failed refresh leaves the previous file in place. Use `auth check` to check the saved token without reaching Amazon. Use [a small search](quickstart.md) to check that Amazon lets the account read the catalog.

For version 3 credentials the tool uses Login with Amazon and the `creatorsapi::default` scope. For version 2 credentials the tool uses the Cognito endpoint and the `creatorsapi/default` scope.

## If a command fails

- **Settings are missing.** Run onboarding with the same settings file and fill the listed fields.
- **The token is missing, expired, or belongs to another set of credentials.** Check which settings file you selected, then preview and approve a token fetch for that account.
- **Amazon issued a token but denied the search.** Check catalog access in Associates Central and make sure the tracking tag belongs to the marketplace in the preview.
- **Amazon rejects a request field.** Check the identifier, marketplace, and resources in [the command guide](command_reference.md). Use a smaller request to identify the field it rejected.
- **You need to find a failed request.** Keep the HTTP status and any Amazon request ID. Keep credentials and tokens private.

The default catalog address is `https://creatorsapi.amazon/catalog/v1`. `AMAZON_CREATORS_API_BASE_URL`, `AMAZON_CREATORS_TOKEN_URL`, and `AMAZON_CREATORS_TIMEOUT_S` are optional overrides. The default timeout is 30 seconds.
