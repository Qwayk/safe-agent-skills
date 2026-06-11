---
title: reverseDeliveryCreateWithShipping - GraphQL Admin
description: Creates a new reverse delivery with associated external shipping information.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/reverseDeliveryCreateWithShipping
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/reverseDeliveryCreateWithShipping.md
---

# reverse​Delivery​Create​With​Shipping

mutation

Requires `write_returns` access scope or `write_marketplace_returns` access scope.

Creates a new reverse delivery with associated external shipping information.

## Arguments

* label​Input

  [Reverse​Delivery​Label​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ReverseDeliveryLabelInput)

  Default:null

  The return label file information for the reverse delivery.

* notify​Customer

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:true

  When `true` the customer is notified with delivery instructions if the `ReverseFulfillmentOrder.order.email` is present.

* reverse​Delivery​Line​Items

  [\[Reverse​Delivery​Line​Item​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ReverseDeliveryLineItemInput)

  required

  The reverse delivery line items to be created. If an empty array is provided, then this mutation will create a reverse delivery line item for each reverse fulfillment order line item, with its quantity equal to the reverse fulfillment order line item total quantity.

* reverse​Fulfillment​Order​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the reverse fulfillment order that's associated to the reverse delivery.

* tracking​Input

  [Reverse​Delivery​Tracking​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ReverseDeliveryTrackingInput)

  Default:null

  The tracking information for the reverse delivery.

***

## Reverse​Delivery​Create​With​Shipping​Payload returns

* reverse​Delivery

  [Reverse​Delivery](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReverseDelivery)

  The created reverse delivery.

* user​Errors

  [\[Return​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### reverseDeliveryCreateWithShipping reference
