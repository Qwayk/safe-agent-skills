# Connect your Freepik account

Create an API key in your Freepik or Magnific account. Create a private `.env` file in the folder you run the tool from and add `FREEPIK_API_KEY=your-key`. Keep the real key out of chat and Git. Use `--env-file /path/to/your.env` before the command to choose a different file.

```bash
freepik-api-tool --output json auth check
```

This runs one small search to check the key. Freepik may charge for API reads. Check your account before planning a large search.

## Settings you can change

Environment variables take priority over values for the same name in the file.

| Setting | Default or purpose |
| --- | --- |
| `FREEPIK_API_KEY` | Required. `FREEPIK_KEY` also works. |
| `FREEPIK_API_BASE_URL` | `https://api.freepik.com/v1`. `FREEPIK_BASE_URL` also works. |
| `FREEPIK_AUTH_HEADER` | `x-freepik-api-key` |
| `FREEPIK_AUTH_PREFIX` | Empty |
| `FREEPIK_TIMEOUT_S` | 30 seconds |
| `FREEPIK_ACCEPT_LANGUAGE` | Optional language such as `en-US` |
| `FREEPIK_IMAGE_SIZE` | Optional size such as `2000px` |
| `FREEPIK_DOWNLOAD_URL_JSONPATH` | Optional path to the download URL in the API reply |
| `FREEPIK_LICENSE_URL_JSONPATH` | Optional path to the license URL in the API reply or asset details |

Use `--config project.json` to set `downloads_dir` and `inventory_csv` for a project. Relative paths inside that file start at the file's folder. The defaults are `downloads/` and `licensed-downloads-ledger.csv` under `--project-dir`, the config file's folder, or the current folder, in that order. Keep keys in the env file.

## If a command fails

- **401 or 403 on the connection check.** Check the key, API host and header settings. A premium asset can also return 403 when your plan lacks access. Use `--param 'filters[license][freemium]=1'` to look for free assets.
- **400 on a photo search.** Pass `--param 'filters[content_type][]=photo'` with the brackets, or use `search photos`. If a large search times out, try a smaller page of up to 100 results.
- **Missing AI fields.** Choose another asset. The tool needs both `is_ai_generated=false` and `has_prompt=false`.
- **A download stops or gives an unclear reply.** Read the result and [check what Freepik recorded](safety_model.md#when-a-download-stops) before trying again. If Freepik changed where it puts a URL, set the relevant JSONPath and save a fresh preview before any new attempt.
- **Need more detail about a read error.** `--verbose` shows request lines. `--debug` shows a Python traceback. Keep any private URLs out of shared logs.
