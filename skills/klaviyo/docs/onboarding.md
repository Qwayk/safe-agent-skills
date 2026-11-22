# Connect your Klaviyo account

Install the tool using the [main guide](../README.md#install). Run onboarding where you want to keep the settings file.

```bash
klaviyo-safe-agent-cli --env-file 'my klaviyo.env' onboarding
```

Onboarding creates the file when it’s missing and gives you the next command with that same filename. The new file is private to its owner. The default filename is `.env`. Use `onboarding --no-write-env` if you only want to check the setup.

## Choose a key for the job

Save your private API key as `KLAVIYO_API_KEY` in the settings file. A key with `lists:read` can list audiences. `auth check` without `--live` checks local settings. `--live auth check` calls Get Accounts and needs `accounts:read`. You can run the list command directly with a lists-only key. Keep private keys in the settings file and out of chat and Git. [Klaviyo account permissions](https://developers.klaviyo.com/en/v2026-04-15/reference/get_accounts)

Client commands such as `api get_client_geofences` use the public `KLAVIYO_COMPANY_ID` without the private key. The company ID is optional for server commands.

## Other settings

- `KLAVIYO_API_BASE_URL` defaults to `https://a.klaviyo.com`.
- `KLAVIYO_API_REVISION` defaults to `2026-04-15`, the revision used to build the included command list.
- `KLAVIYO_TIMEOUT_S` defaults to 30 seconds.
- Shell settings take priority over values in the file.

If Klaviyo rejects the key, check that you selected the intended settings file and that the key has the permission for that command. If a write times out or the result is uncertain, check Klaviyo before you try again. [Plans and receipts](safety_model.md)
