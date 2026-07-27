# List the Jira projects you can browse

Your first result is a read-only list of projects available to the connected Jira user. This proves the site URL, credential, Jira permissions, and Platform API path before you prepare any change.

## 1. Install the source package

Use Python 3.12 or newer:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
```

## 2. Create the local setup file

```bash
.venv/bin/jira-safe onboarding
```

Open `.env` and set `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN`. Keep the token in that local file and out of chat.
For Basic auth, the URL must be the root `https://your-domain.atlassian.net` site. OAuth uses `https://api.atlassian.com/ex/jira/<cloudId>` instead.

## 3. Check the connected user

```bash
.venv/bin/jira-safe --env-file .env auth check
```

A successful result includes `"ok": true`, the Jira site, `"auth_mode": "basic"`, and the current account returned by `/rest/api/3/myself`.

## 4. List available projects

```bash
.venv/bin/jira-safe --env-file .env platform get-all-projects
```

The command only reads Jira. It does not create a plan because there is no live change to approve.

Next, ask your agent to [find issues or review a board and sprint](use_cases.md). Before asking for a change, read [what happens before live writes](safety_model.md).
