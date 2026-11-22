# Troubleshooting

- **Wrong account or expired token.** Use `auth check` to see the signed-in user and `auth token status` to check the selected settings file. For an old token file or a new browser sign-in, follow [account setup](onboarding.md).
- **Some boards or pins are missing.** Confirm the account and permissions. Secret boards and protected pins depend on Pinterest access. Use the returned bookmark to continue a list. [Board and pin commands](command_reference.md#inventory)
- **Analytics fails.** Use `--skip-analytics` to save boards and pins without analytics. Ads and catalogs can need an ad account ID and additional permissions.
- **A pin edit returns `restricted feature: pin_edit`.** Check Pinterest’s app access for pin edits. Another local approval or token with the same app access may give the same response. [Pinterest’s access guide](https://developers.pinterest.com/docs/getting-started/set-up-authentication-and-authorization/)
- **A saved plan is refused.** Confirm the account and compare the exact change with the preview. If the target or change differs, save a fresh preview for approval. If Pinterest might already have created the item, look it up before trying again.
- **You need more detail.** Use `--verbose` for request details or `--debug` for a local error trace. Check output for secrets before sharing it.
