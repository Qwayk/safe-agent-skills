# Safety Model

v0.1.0 ships read commands, read-like Product Key POST lookups, and a local Link Wrapper URL builder.

There are no live mutation commands in this release.

Safety rules:
- No raw request bridge.
- No hidden endpoints.
- No credentials or access tokens in stdout, stderr, logs, examples, or docs.
- Product Key access is not flattened into the shared auth model.
- Link Wrapper does not click or follow redirects.
- Data Pipe and Skimlinks JavaScript are documented as official non-API areas, not counted as shipped API commands.

If write commands are ever added, they must use the repo-standard plan -> review -> apply -> verify -> receipt flow.
