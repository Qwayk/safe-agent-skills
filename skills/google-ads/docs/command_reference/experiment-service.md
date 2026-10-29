# ExperimentService (Google Ads API v25)

Command shape:
- `google-ads-api-tool experiment-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `end-experiment` — `ExperimentService.EndExperiment` (write; plan-first; unary_unary) — request: `EndExperimentRequest` → response: `Empty`
- `graduate-experiment` — `ExperimentService.GraduateExperiment` (write; plan-first; unary_unary) — request: `GraduateExperimentRequest` → response: `Empty`
- `list-experiment-async-errors` — `ExperimentService.ListExperimentAsyncErrors` (read; unary_unary) — request: `ListExperimentAsyncErrorsRequest` → response: `ListExperimentAsyncErrorsResponse`
- `mutate-experiments` — `ExperimentService.MutateExperiments` (write; plan-first; unary_unary) — request: `MutateExperimentsRequest` → response: `MutateExperimentsResponse`
- `promote-experiment` — `ExperimentService.PromoteExperiment` (write; plan-first; unary_unary) — request: `PromoteExperimentRequest` → response: `Operation`
- `schedule-experiment` — `ExperimentService.ScheduleExperiment` (write; plan-first; unary_unary) — request: `ScheduleExperimentRequest` → response: `Operation`
