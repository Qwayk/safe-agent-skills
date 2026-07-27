# Jobs, asynchronous work, and the batch exclusion

This CLI does not have a generic CSV job runner or arbitrary batch command. Each request uses one fixed Asana operation so the method, path, parameters, body type, risk, and approval behavior stay known.

Asana itself returns job-backed or asynchronous results for some exports, duplication, and template operations. The CLI reports the returned state and can use `--wait` when the result includes a job GID. Polling stops on `succeeded`, `failed`, or the chosen timeout. A timeout means queued or running, not failed and not complete.

The pinned specification also includes `POST /batch`. It accepts arbitrary relative API paths, so exposing it would recreate a raw-request bridge. The operation remains visible as `intentionally_excluded` in `docs/api_coverage.md`; every supported underlying operation has its own fixed command.
