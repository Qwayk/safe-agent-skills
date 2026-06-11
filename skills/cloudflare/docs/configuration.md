# Configuration

This tool uses a `.env` file for configuration (local-only; do not commit it).

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/`: local tool state next to your `--env-file` (gitignored)
- `--project-dir`: base directory for safe file outputs (sensitive reads only write under this directory)

## Environment variables

Required / common:
- `CLOUDFLARE_API_TOKEN`: Cloudflare API Token (preferred auth)

Optional:
- `CLOUDFLARE_API_BASE_URL`: default is `https://api.cloudflare.com/client/v4/`
- `CLOUDFLARE_TIMEOUT_S`: request timeout seconds (default: `30`)
- `CLOUDFLARE_CONNECT_TIMEOUT_S`: connect timeout seconds (defaults to `CLOUDFLARE_TIMEOUT_S`)
- `CLOUDFLARE_READ_TIMEOUT_S`: read timeout seconds (defaults to `CLOUDFLARE_TIMEOUT_S`)

Notes:
- OS environment variables override the env file (useful in CI).
- This tool never prints your token and never logs `Authorization` headers.
- For vendor-slow endpoints (commonly in Zero Trust), use `--timeout-profile slow` or increase `--read-timeout-s`.
- The tool has an optional short-TTL cache for explicitly allowlisted safe GET reads (enabled by default; see `--cache-ttl-s` / `--no-cache`).

## Example `.env`

```bash
CLOUDFLARE_API_BASE_URL=https://api.cloudflare.com/client/v4
CLOUDFLARE_API_TOKEN=your_token_here
CLOUDFLARE_TIMEOUT_S=30
# Optional: split timeouts (recommended when some endpoints are very slow)
# CLOUDFLARE_CONNECT_TIMEOUT_S=10
# CLOUDFLARE_READ_TIMEOUT_S=240
```
