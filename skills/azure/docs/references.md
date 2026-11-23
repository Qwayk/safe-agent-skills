# References

## Source-of-truth documents

- Azure REST API specs: `https://github.com/Azure/azure-rest-api-specs`
- Pinned spec commit: `ada8601c3b75c15f06f21e50f9368d9476229305`
- Pinned commit URL: `https://github.com/Azure/azure-rest-api-specs/tree/ada8601c3b75c15f06f21e50f9368d9476229305`
- Azure ARM docs: `https://learn.microsoft.com/azure/azure-resource-manager/`
- Microsoft Entra identity token flow: `https://learn.microsoft.com/entra/identity-platform/access-tokens`

- [Azure CLI accounts and token selection](https://learn.microsoft.com/cli/azure/account)
- [Azure Resource Manager status checks](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/async-operations)
- [Azure resource IDs and scope](https://learn.microsoft.com/en-us/azure/role-based-access-control/scope-overview)
- [Key Vault authentication](https://learn.microsoft.com/azure/key-vault/authentication-requests-and-responses)

## Tool behavior mapping

- Scope boundary: official Azure `resource-manager` and `data-plane` JSON specs.
- Service coverage: 339 commands across 340 service entries. The IoT Spaces entry has no operations.
- Operation selection: `26,337` generated operations from `214,231` candidate operations.
- Exclusions: non-Azure Microsoft products and non-spec folders used by Azure boundary filtering.
- Last inventory generation date in this repo: `2026-06-28T08:19:50Z`.
