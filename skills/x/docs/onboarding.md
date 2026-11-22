# Connect your X account

Use your approved X app. Keep its tokens and the local `.state` folder out of chat and Git. Use a different folder for each account because the tool keeps token files next to the chosen `.env` file.

## Set up the app

Create a private `.env` file in the folder where you will work. You can use `x-api-tool onboarding` to create it, or `x-api-tool onboarding --no-write-env` to check for missing settings without writing the file. Add `X_API_BASE_URL=https://api.x.com/2`.

For app-level reads, add `X_API_BEARER_TOKEN` from your X app. For account reads and writes, add the OAuth settings below. Get the client ID from the app and use the exact same redirect URI in X and in this file.

~~~dotenv
X_API_BASE_URL=https://api.x.com/2
X_API_OAUTH2_CLIENT_ID=YOUR_CLIENT_ID
X_API_OAUTH2_REDIRECT_URI=http://127.0.0.1:8080/callback
X_API_OAUTH2_SCOPES=users.read tweet.read
~~~

Add `tweet.write` if you have approval to post. Add `dm.read dm.write` if you have approval to read and send messages. X controls which actions the app can use and which people can receive messages from your account. [X OAuth setup](https://docs.x.com/fundamentals/authentication/oauth-2-0/authorization-code)

Use `--env-file` to choose another settings file. Environment variables override file values. `X_API_TIMEOUT_S` is optional and defaults to 30 seconds.

## Sign in as the account

First preview both commands without the approval flags. With approval, start sign-in:

~~~bash
x-api-tool --apply --yes --ack-no-snapshot auth pkce start
~~~

Open the returned URL and sign in as the intended account. Copy the final redirect URL from the browser address bar even if the loopback page fails to load. Run the finish command locally. The URL contains a short-lived code, so keep it out of chat.

~~~bash
x-api-tool --apply --yes --ack-no-snapshot auth pkce finish --redirect-url 'YOUR_REDIRECT_URL'
~~~

The first command saves sign-in state in `.state/pkce.json`. The second exchanges the code and saves the token in `.state/token.json`. If you already have a token file, preview `x-api-tool auth token set --file token.json`, then add `--apply --yes --ack-no-snapshot` after review. Use `x-api-tool auth token status` to check whether the token file exists.

Run `x-api-tool auth check` for a local check. When a credit-using read is approved, run `x-api-tool --live auth check` to see the username and ID for the OAuth token. [X API pricing](https://docs.x.com/x-api/getting-started/pricing)
