# CustomerService (Google Ads API v22)

Command shape:
- `google-ads-api-tool customer-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `create-customer-client` — `CustomerService.CreateCustomerClient` (write; unary) — request: `CreateCustomerClientRequest` → response: `CreateCustomerClientResponse` (plan-first; snapshot-backed live applies save before-state when possible; other write shapes need explicit no-snapshot approval support or a true blocker reason; allowlist required)
- `list-accessible-customers` — `CustomerService.ListAccessibleCustomers` (read; unary) — request: `ListAccessibleCustomersRequest` → response: `ListAccessibleCustomersResponse`
- `mutate-customer` — `CustomerService.MutateCustomer` (write; unary) — request: `MutateCustomerRequest` → response: `MutateCustomerResponse` (plan-first; snapshot-backed live applies save before-state when possible; other write shapes need explicit no-snapshot approval support or a true blocker reason; allowlist required)
