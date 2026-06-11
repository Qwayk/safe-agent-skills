---
title: fulfillmentCreateV2 - GraphQL Admin
description: >-
  Creates a fulfillment for one or many fulfillment orders.

  The fulfillment orders are associated with the same order and are assigned to
  the same location.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentCreateV2
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentCreateV2.md
---

# fulfillment​Create​V2

mutation

Requires `write_assigned_fulfillment_orders` access scope, `write_merchant_managed_fulfillment_orders` access scope or `write_third_party_fulfillment_orders` access scope. Also: The user must have fulfill\_and\_ship\_orders permission.

Deprecated. Use [fulfillmentCreate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentCreate) instead.

Creates a fulfillment for one or many fulfillment orders. The fulfillment orders are associated with the same order and are assigned to the same location.

## Arguments

* fulfillment

  [Fulfillment​V2Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/FulfillmentV2Input)

  required

  The input fields used to create a fulfillment from fulfillment orders.

* message

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  An optional message for the fulfillment request.

***

## Fulfillment​Create​V2Payload returns

* fulfillment

  [Fulfillment](https://shopify.dev/docs/api/admin-graphql/latest/objects/Fulfillment)

  The created fulfillment.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### fulfillmentCreateV2 reference
