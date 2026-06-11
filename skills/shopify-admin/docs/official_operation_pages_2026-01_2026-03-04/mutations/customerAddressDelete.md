---
title: customerAddressDelete - GraphQL Admin
description: Deletes a customer's address.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerAddressDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerAddressDelete.md
---

# customer​Address​Delete

mutation

Requires `write_customers` access scope.

Deletes a customer's address.

## Arguments

* address​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the address to be deleted from the customer.

* customer​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the customer whose address is being deleted.

***

## Customer​Address​Delete​Payload returns

* deleted​Address​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the address deleted from the customer.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### customerAddressDelete reference
