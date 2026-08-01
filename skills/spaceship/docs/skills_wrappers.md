# Spaceship skill wrapper

The public skill slug is `spaceship`. The wrapper is tracked at `skills/spaceship-safe-cli/SKILL.md` in source and promoted to top-level `SKILL.md` in the public skill folder. The Python executable it calls is `qwayk-spaceship-safe-agent-cli`.

The wrapper tells an agent to use the tool only for the 40 documented Spaceship External API operations. The safest first action is a read, such as listing domains or checking one domain's availability, before preparing any change.

For a write, the wrapper requires a saved plan, exact target review, `--apply --yes --plan-in`, every operation-specific acknowledgement, a fresh preflight read where Spaceship exposes one, and a redacted receipt. Spend, ownership, DNS, financial, destructive, and private-data actions receive stronger acknowledgement. When no reliable snapshot or complete financial recheck exists, the plan must say so and require `--ack-no-snapshot`.

Plans and receipts use the automatic `.state/runs/<run_id>/` paths unless the agent supplies an explicit output path. Run IDs must be non-empty single path segments; never use an absolute path, slash, backslash, `.` or `..`. Persisted command displays must digest contact and SafePay transaction identifiers, and billing contacts or opaque private errors must never be repeated. The wrapper must preserve the official sold-domain `cursor`, date filters, and per-command `take` limits.

The wrapper must refuse generic API requests, undocumented endpoints, vague targets, secret disclosure, unsafe hosts, changed plans, missing acknowledgements, and any write that cannot follow the review-first flow. It must also refuse `domains delete` and `domains personal-nameservers get-host` locally because Spaceship documents those operations as under development with HTTP 501.

Credentials come only from `SPACESHIP_API_KEY` and `SPACESHIP_API_SECRET`. They are sent only to `https://spaceship.dev/api` and must not appear in prompts, output, plans, receipts, logs, or examples.

Redirects are refused rather than followed, so those custom headers are never resent to another host.

This source build has no live-account proof. The wrapper must describe provider behavior as live-unverified until a separately authorized credentialed check exists.
