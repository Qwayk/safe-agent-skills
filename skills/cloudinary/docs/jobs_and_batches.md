# Jobs and batches

This shipped Cloudinary CLI does not expose a generic `jobs` command.

That is intentional.
Cloudinary operations in this tool are explicit, per-operation commands so an agent can discover the exact allowlisted action first.

## Current safe batch pattern

If you need bulk work:
1. use `operations list` and `operations show` to find the exact command
2. build your own small wrapper that loops over explicit `cloudinary-safe-agent-cli operations ...` calls
3. keep write steps in dry-run first
4. expect current write apply attempts to require explicit no-snapshot approval before Cloudinary HTTP
5. keep each apply attempt with its own local run artifacts

## Why there is no shipped batch runner yet

- the official Cloudinary REST surface is large and mixed across product, account, public, binary, and sensitive endpoints
- a generic batch runner would need more command-specific review rules before it would be safe for non-technical users
- explicit commands plus local run history are the safer current release
