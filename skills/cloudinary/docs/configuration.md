# Configuration

## `.env` values

This tool reads a simple `.env` file.
OS environment variables override the file.

Required for product APIs:
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

Required for account APIs:
- `CLOUDINARY_ACCOUNT_ID`
- `CLOUDINARY_ACCOUNT_API_KEY`
- `CLOUDINARY_ACCOUNT_API_SECRET`

Optional:
- `CLOUDINARY_PRODUCT_API_HOST`
  - default: `api.cloudinary.com`
- `CLOUDINARY_ACCOUNT_API_HOST`
  - default: `api.cloudinary.com`
- `CLOUDINARY_TIMEOUT_S`
  - default: `30`

Unsigned upload commands still need `CLOUDINARY_CLOUD_NAME`.
They do not need the product key or secret, but Cloudinary still needs a valid unsigned upload preset in the request.

## `--env-file`

Use a different env file like this:

```bash
cloudinary-safe-agent-cli --env-file envs/client-a.env --output json auth check
```

Run history is stored next to that env file under `.state/runs/`.

## `--project-dir`

`--project-dir` sets the safe root for files written by `--out`.
Relative `--out` paths are resolved under this folder.
The tool refuses to write outside it.

## `--config`

You can pass a non-secret JSON config file:

```json
{
  "notes_file": "notes/cloudinary.md",
  "exports_dir": "artifacts/exports"
}
```

Current built-in commands do not read named keys from this JSON.
It is there so wrappers can keep non-secret defaults near the tool.
Relative paths inside the JSON are resolved from the config file folder.
