# Connect Figma

Run `figma-safe-agent-cli onboarding` from the folder where you want to keep the settings. It creates `.env` if needed. Use `--env-file PATH` before `onboarding` to choose another file, and pass the same option to later commands. Add `--no-write-env` after `onboarding` to see the setup steps without creating the file.

## Choose a token

| Token | Local setup |
| --- | --- |
| Personal | Set `FIGMA_ACCESS_TOKEN` in the settings file. This is the default mode. |
| OAuth | Set `FIGMA_AUTH_MODE=oauth`. Set `FIGMA_ACCESS_TOKEN` or save the token JSON with `figma-safe-agent-cli auth token set --file token.json`. |
| Plan | Set `FIGMA_AUTH_MODE=plan` and `FIGMA_ACCESS_TOKEN`. Figma limits plan tokens to supported organization or enterprise actions. Comment writes need a supported personal or OAuth token. |

Keep settings and tokens out of Git and chat. Values set in your shell take priority over the settings file. The API address defaults to `https://api.figma.com`, and the timeout defaults to 30 seconds. Use `FIGMA_BASE_URL` or `FIGMA_TIMEOUT_S` if you need to change either. For OAuth, a configured token takes priority over the saved token JSON under `.state/token.json` beside the settings file.

## Check that you can open the file

Start with a file you can open in Figma. These commands check different permissions.

- `figma-safe-agent-cli operations files get-file-meta --file-key YOUR_FILE_KEY` needs `file_metadata:read`.
- `figma-safe-agent-cli operations files get-file --file-key YOUR_FILE_KEY` and image renders need `file_content:read`.
- `figma-safe-agent-cli operations comments get-comments --file-key YOUR_FILE_KEY` needs `file_comments:read`. Posting and deleting comments use `file_comments:write`.

`figma-safe-agent-cli auth check` tries the Figma profile endpoint with a personal or OAuth token. That endpoint needs `current_user:read`. If the check fails for that permission, try the read you actually need. Plan mode and `auth check --skip-live` report local setup only.

## If a command fails

- Check that you used the same settings file and that the token is current. `figma-safe-agent-cli auth token status` shows saved OAuth token details without showing the token.
- If Figma refuses a request, check the file key, whether the account can open the file, and whether the token has the permission for that command. Team or plan limits can also apply.
- Use `operations show AREA COMMAND` to check the required options. The flag for Figma's version ID is `--version-id`.
- Keep the error details for troubleshooting. `--verbose` shows request timing on stderr. `--debug` shows more details for developers. Before you share an error, remove any private account details or secrets.
- If a write failed after it was sent, check Figma before retrying. See [Approve and check changes](safety_model.md).

[Figma token setup](https://developers.figma.com/docs/rest-api/authentication/) · [Figma permissions](https://developers.figma.com/docs/rest-api/scopes/) · [Plan token limits](https://developers.figma.com/docs/rest-api/plan-access-tokens/#supported-endpoints)
