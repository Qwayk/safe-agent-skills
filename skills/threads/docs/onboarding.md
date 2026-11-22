# Connect your Threads account

Run `threads-api-tool onboarding` to create a local `.env` file. Add `--no-write-env` after `onboarding` to see the setup instructions without creating the file. Keep tokens, app secrets and sign-in codes off chat and out of Git.

## If you already have a user token

Put it in `THREADS_API_TOKEN` and run `threads-api-tool auth check`. The command returns the account ID and username. The default server and API version work without any app settings. An explicit token in the settings takes priority over a saved token file.

## If you need a token

1. Create or open a Meta app with the Threads use case. Set `THREADS_APP_ID`, `THREADS_APP_SECRET` and `THREADS_REDIRECT_URI` in your local settings. Use the exact redirect URL registered with Meta.
2. Run `threads-api-tool auth authorize-url --scope threads_basic` and open the returned URL yourself. For publishing, use `threads_basic,threads_content_publish`. Add other permissions only for the commands you need. [Access by command](api_coverage.md)
3. After approving access in the browser, use the returned code locally. Preview `threads-api-tool auth code exchange --code AUTHORIZATION_CODE` and review it. To exchange the code and save the token, rerun with `--apply --ack-no-snapshot` before `auth`.
4. Run `threads-api-tool auth check` to confirm the account and `threads-api-tool auth token status` to check the saved file.

Use `auth token exchange-long` for a longer-lived token and `auth token refresh` to renew it. These commands preview by default and save a token only after approval. If you keep an old `THREADS_API_TOKEN` value, it still takes priority over a newly saved token. [Meta’s token guide](https://www.postman.com/meta/threads/documentation/dht3nzz/threads-api)

## Settings and separate accounts

Use `--env-file /path/to/account/.env` before the command to choose a settings file. The tool stores tokens in `.state/token.json` beside that file. Settings files in the same directory share the saved token. Use a separate directory for each account. Shell environment values take priority over values in the settings file.

| Setting | Default |
| --- | --- |
| `THREADS_API_BASE_URL` | `https://graph.threads.net` |
| `THREADS_API_VERSION` | `v1.0` |
| `THREADS_DEFAULT_USER_ID` | Optional account ID for commands that accept it |
| `THREADS_TIMEOUT_S` | 30 seconds |

The permission to read a profile is separate from permission to publish, view insights, manage replies or use discovery. The [command list](api_coverage.md) shows the permissions for those jobs.
