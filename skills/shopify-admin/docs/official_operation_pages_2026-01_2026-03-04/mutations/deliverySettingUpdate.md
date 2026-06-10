---
title: deliverySettingUpdate - GraphQL Admin
description: Set the delivery settings for a shop.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliverySettingUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliverySettingUpdate.md
---

# delivery​Setting​Update

mutation

Set the delivery settings for a shop.

## Arguments

* setting

  [Delivery​Setting​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DeliverySettingInput)

  required

  Specifies the input fields for the delivery shop level settings.

***

## Delivery​Setting​Update​Payload returns

* setting

  [Delivery​Setting](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliverySetting)

  The updated delivery shop level settings.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### deliverySettingUpdate reference
