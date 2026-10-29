# CustomerService (Google Ads API v25)

Command shape:
- `google-ads-api-tool customer-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `create-customer-client` — `CustomerService.CreateCustomerClient` (write; plan-first; unary_unary) — request: `CreateCustomerClientRequest` → response: `CreateCustomerClientResponse`
- `list-accessible-customers` — `CustomerService.ListAccessibleCustomers` (read; unary_unary) — request: `ListAccessibleCustomersRequest` → response: `ListAccessibleCustomersResponse`
- `mutate-customer` — `CustomerService.MutateCustomer` (write; plan-first; unary_unary) — request: `MutateCustomerRequest` → response: `MutateCustomerResponse`
