# Jobs and batches

The current official Sovrn surface in this tool is read-only, so a customer-facing batch runner is not shipped yet.

Why this page still exists:

- the repo standard expects us to document how batching will be handled if official write-capable Sovrn endpoints are added later
- the local codebase still keeps some internal scaffold helpers while the real API surface is being finished

Current rule:

- Do not treat any internal batch scaffold as shipped customer surface.
- If a future official write-capable command lands, update this page together with `docs/api_coverage.md`, `docs/safety_model.md`, and the CLI help.
