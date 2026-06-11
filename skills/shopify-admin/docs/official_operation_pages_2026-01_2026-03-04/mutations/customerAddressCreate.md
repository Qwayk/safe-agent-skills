---
title: customerAddressCreate - GraphQL Admin
description: >-
  Creates a new
  [`MailingAddress`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress)
  for a
  [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer).
  You can optionally set the address as the customer's default address.


  You can only add addresses to existing customers. Each customer can have
  multiple addresses.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerAddressCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerAddressCreate.md
---

# customer​Address​Create

mutation

Requires `write_customers` access scope.

Creates a new [`MailingAddress`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress) for a [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer). You can optionally set the address as the customer's default address.

You can only add addresses to existing customers. Each customer can have multiple addresses.

## Arguments

* address

  [Mailing​Address​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MailingAddressInput)

  required

  Specifies the fields to use when creating the address.

* customer​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the customer.

* set​As​Default

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Whether to set the address as the customer's default address.

***

## Customer​Address​Create​Payload returns

* address

  [Mailing​Address](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress)

  The created address.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### customerAddressCreate reference
