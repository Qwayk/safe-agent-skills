---
title: fulfillmentTrackingInfoUpdateV2 - GraphQL Admin
description: Updates tracking information for a fulfillment.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentTrackingInfoUpdateV2
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentTrackingInfoUpdateV2.md
---

# fulfillment​Tracking​Info​Update​V2

mutation

Requires `write_assigned_fulfillment_orders` access scope, `write_merchant_managed_fulfillment_orders` access scope or `write_third_party_fulfillment_orders` access scope. Also: The user must have fulfill\_and\_ship\_orders permission.

Deprecated. Use [fulfillmentTrackingInfoUpdate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentTrackingInfoUpdate) instead.

Updates tracking information for a fulfillment.

## Arguments

* fulfillment​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the fulfillment.

* notify​Customer

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Whether the customer will be notified of this update and future updates for the fulfillment. If this field is left blank, then notifications won't be sent to the customer when the fulfillment is updated.

* tracking​Info​Input

  [Fulfillment​Tracking​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/FulfillmentTrackingInput)

  required

  The tracking input for the mutation, including tracking URL, number, and company.

***

## Fulfillment​Tracking​Info​Update​V2Payload returns

* fulfillment

  [Fulfillment](https://shopify.dev/docs/api/admin-graphql/latest/objects/Fulfillment)

  The updated fulfillment with tracking information.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### fulfillmentTrackingInfoUpdateV2 reference
