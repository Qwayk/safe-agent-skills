# Engineering notes

- Source slice: `qwayk-sav-safe-agent-cli`
- Source build: pinned to `https://documenter.gw.postman.com/api/collections/9688716/TzzANHFJ?segregateAuth=true&versionTag=latest`
- Safety model: fixed command set, write plans by default, explicit approvals on apply
- Host boundary: fixed `https://api.sav.com/domains_api_v1`; redirects are disabled and only 2xx responses succeed.
- State writes: `0700` private directories under `.state`, files at `0600` with atomic replace (`mkstemp` + rename).
- Plan authentication: per-env random HMAC key stored in `.state/keys/plan-hmac.key`, plans are `schema_version: 2`.
- Apply persistence: an honest unknown-outcome receipt is written before transport; provider-response receipts replace it after a response. If the final write fails, output keeps the provider status visible and warns against a blind retry.
- Receipt fields: `receipt_written` is local file persistence only; `durable_state_verified` is always false without independent SAV readback; `provider_response_only` matches `provider_response_received`; and a 2xx outcome is `provider_accepted`.
- Transfer input: one regular mode-`0600` file in a non-symlink mode-`0700` parent is opened without following symlinks and checked/read through the same descriptor.
- No raw command bridge is exposed
- No hidden path translation outside official collection operations
- No restore/rollback flow for writes; no independent readback contract
- WHOIS and auth-like values are redacted in displayed output and receipts

Current gaps to track:
- No apply-time readback verification assertions are shipped in this slice.
- Write recovery is intentionally non-reversible from this runtime shape.
