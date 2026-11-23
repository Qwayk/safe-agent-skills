# Connect Cloudinary

Run `cloudinary-safe-agent-cli onboarding` from the folder where you want to keep your settings. It creates `.env` if needed. To use a different file, put `--env-file PATH` before `onboarding` and before later commands. Use `onboarding --no-write-env` to get the setup steps without creating a file.

## Pick the connection you need

| Work | Settings |
| --- | --- |
| Images, videos, folders, uploads, analysis, and streaming | `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` from your Cloudinary media library |
| Product environments, users, roles, and account keys | `CLOUDINARY_ACCOUNT_ID`, `CLOUDINARY_ACCOUNT_API_KEY`, `CLOUDINARY_ACCOUNT_API_SECRET` from your Cloudinary account |
| Unsigned uploads | `CLOUDINARY_CLOUD_NAME` and a valid unsigned upload preset in the request |

Some permissions commands, such as validating a policy, are public. Use `operations show` to see which connection a command uses. Keep credentials in the local settings file or your shell environment. Shell values take priority. Keep them out of chat and Git.

The hosts default to `api.cloudinary.com`. Set `CLOUDINARY_PRODUCT_API_HOST` or `CLOUDINARY_ACCOUNT_API_HOST` if Cloudinary gave you a different host. Requests default to 30 seconds. Set `CLOUDINARY_TIMEOUT_S` or use `--timeout-s` for a different request timeout.

## Check access

Use the media read shown by onboarding. It needs your media credentials. If you want a connection report, run `cloudinary-safe-agent-cli auth check` and check `checks.product.ready` or `checks.account.ready` for the part you need. The media check calls `GET /ping`. The account check tries to list product environments when account credentials are present.

If access fails, check the selected file, cloud name or account ID, regional host, and permission for the actual command. Use `operations show --area AREA --op COMMAND` to look up the command's parameters. Use `--verbose` for request timing and `--debug` for a stack trace when troubleshooting locally.

Set `--project-dir PATH` to choose where `--out` files may go. The optional `--config PATH` accepts non-secret JSON settings for wrappers. See [Approve and check changes](safety_model.md) for private output and run history.

[Find your media credentials](https://cloudinary.com/documentation/finding_your_credentials_tutorial) · [Account API credentials](https://cloudinary.com/documentation/provisioning_api)
