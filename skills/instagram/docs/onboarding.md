# Connect your Instagram account

Run `instagram-api-tool onboarding` to create a local `.env` file. Add `--no-write-env` after `onboarding` to see setup instructions without creating a file. Keep settings, access tokens and sign-in codes private.

## If you already have a user token

Put the Instagram Login user token in `INSTAGRAM_ACCESS_TOKEN` and run `instagram-api-tool auth check`. It shows the professional account ID and username. You can also preview `auth token set --file token.json` and use `--apply --ack-no-snapshot` to save an approved local token file.

## If you need to sign in through your Meta app

1. Set `INSTAGRAM_APP_ID`, `INSTAGRAM_APP_SECRET` and `INSTAGRAM_REDIRECT_URI` locally. Use the exact redirect URL registered with Meta.
2. Run `instagram-api-tool auth login-url --scope instagram_business_basic` and open the returned link. Sign in to the professional account you want to work with.
3. Use the code from the redirect locally. Preview `auth code exchange --code YOUR_CODE`. After approval, rerun with `--apply --ack-no-snapshot` before `auth` to exchange the code and save the token.
4. Run `auth check` to confirm the account, and `auth token status` to check where the token is saved.

Use `auth token exchange-long` to exchange a short-lived token and `auth token refresh` to renew a valid long-lived token. These commands preview first and need approval to save a token. [Meta’s sign-in guide](https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login/business-login)

## Permissions

Request the permissions you need for the work.

| Permission | What it lets you do |
| --- | --- |
| `instagram_business_basic` | Read the professional account and posts |
| `instagram_business_content_publish` | Prepare and publish posts |
| `instagram_business_manage_comments` | Read and manage comments |
| `instagram_business_manage_messages` | Work with eligible messages |

Meta lists different insights permissions for its login methods. Check the [listed insights references](references.md) for the permission that applies to your app.

## Settings and separate accounts

Use `--env-file /path/to/account/.env` before the command to choose an account settings file. Token commands save `.state/token.json` in that file’s directory. Use separate directories if you want separate saved tokens. Shell environment values take priority over the settings file. `INSTAGRAM_ACCESS_TOKEN` takes priority over the saved token file, including after a refresh.

| Optional setting | Default |
| --- | --- |
| `INSTAGRAM_GRAPH_BASE_URL` | `https://graph.instagram.com` |
| `INSTAGRAM_AUTH_API_BASE_URL` | `https://api.instagram.com` |
| `INSTAGRAM_AUTH_WEB_BASE_URL` | `https://www.instagram.com` |
| `INSTAGRAM_GRAPH_VERSION` | `v25.0` |
| `INSTAGRAM_IG_USER_ID` | Accounts resolve from the token for `media list` if you leave this blank |
| `INSTAGRAM_TIMEOUT_S` | 30 seconds |
