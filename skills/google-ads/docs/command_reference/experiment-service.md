# ExperimentService (Google Ads API v22)

Command shape:
- `google-ads-api-tool experiment-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `end-experiment` — `ExperimentService.EndExperiment` (read; unary) — request: `EndExperimentRequest` → response: `Empty`
- `graduate-experiment` — `ExperimentService.GraduateExperiment` (read; unary) — request: `GraduateExperimentRequest` → response: `Empty`
- `list-experiment-async-errors` — `ExperimentService.ListExperimentAsyncErrors` (read; unary) — request: `ListExperimentAsyncErrorsRequest` → response: `ListExperimentAsyncErrorsResponse`
- `mutate-experiments` — `ExperimentService.MutateExperiments` (write; unary) — request: `MutateExperimentsRequest` → response: `MutateExperimentsResponse` (plan-first; snapshot-backed live applies save before-state when possible; other write shapes need explicit no-snapshot approval support or a true blocker reason; allowlist required)
- `promote-experiment` — `ExperimentService.PromoteExperiment` (read; unary) — request: `PromoteExperimentRequest` → response: `Operation`
- `schedule-experiment` — `ExperimentService.ScheduleExperiment` (read; unary) — request: `ScheduleExperimentRequest` → response: `Operation`
