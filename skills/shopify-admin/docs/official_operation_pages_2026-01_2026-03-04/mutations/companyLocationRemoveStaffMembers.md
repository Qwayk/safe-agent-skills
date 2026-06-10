---
title: companyLocationRemoveStaffMembers - GraphQL Admin
description: >-
  Deletes one or more existing mappings between a staff member at a shop and a
  company location.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyLocationRemoveStaffMembers
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyLocationRemoveStaffMembers.md
---

# company​Location​Remove​Staff​Members

mutation

Requires `write_customers` access scope or `write_companies` access scope. Also: The API client must be installed on a Shopify Plus store.

Deletes one or more existing mappings between a staff member at a shop and a company location.

## Arguments

* company​Location​Staff​Member​Assignment​Ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The list of IDs of the company location staff member assignment to delete.

***

## Company​Location​Remove​Staff​Members​Payload returns

* deleted​Company​Location​Staff​Member​Assignment​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The list of IDs of the deleted staff member assignment.

* user​Errors

  [\[Business​Customer​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessCustomerUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### companyLocationRemoveStaffMembers reference
