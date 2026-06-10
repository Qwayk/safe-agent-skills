---
title: reverseDeliveryShippingUpdate - GraphQL Admin
description: Updates a reverse delivery with associated external shipping information.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/reverseDeliveryShippingUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/reverseDeliveryShippingUpdate.md
---

# reverse​Delivery​Shipping​Update

mutation

Requires `write_returns` access scope.

Updates a reverse delivery with associated external shipping information.

## Arguments

* label​Input

  [Reverse​Delivery​Label​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ReverseDeliveryLabelInput)

  Default:null

  The return label file information for the reverse delivery.

* notify​Customer

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:true

  If `true` and an email address exists on the `ReverseFulfillmentOrder.order`, then the customer is notified with the updated delivery instructions.

* reverse​Delivery​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the reverse delivery to update.

* tracking​Input

  [Reverse​Delivery​Tracking​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ReverseDeliveryTrackingInput)

  Default:null

  The tracking information for the reverse delivery.

***

## Reverse​Delivery​Shipping​Update​Payload returns

* reverse​Delivery

  [Reverse​Delivery](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReverseDelivery)

  The updated reverse delivery.

* user​Errors

  [\[Return​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### reverseDeliveryShippingUpdate reference
