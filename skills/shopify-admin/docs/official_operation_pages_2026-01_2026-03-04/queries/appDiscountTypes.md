---
title: appDiscountTypes - GraphQL Admin
description: A list of app discount types installed by apps.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/appDiscountTypes'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/appDiscountTypes.md
---

# app​Discount​Types

query

Requires Apps must have `read_discounts` access scope.

A list of app discount types installed by apps.

## Possible returns

* App​Discount​Type

  [\[App​Discount​Type!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppDiscountType)

  The details about the app extension that's providing the [discount type](https://help.shopify.com/manual/discounts/discount-types). This information includes the app extension's name and [client ID](https://shopify.dev/docs/apps/build/authentication-authorization/client-secrets), [App Bridge configuration](https://shopify.dev/docs/api/app-bridge), [discount class](https://help.shopify.com/manual/discounts/combining-discounts/discount-combinations), [function ID](https://shopify.dev/docs/apps/build/functions/input-output/metafields-for-input-queries), and other metadata about the discount type, including the discount type's name and description.

  * app

    [App!](https://shopify.dev/docs/api/admin-graphql/latest/objects/App)

    non-null

    The name of the app extension that's providing the [discount type](https://help.shopify.com/manual/discounts/discount-types).

  * app​Bridge

    [Functions​App​Bridge!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FunctionsAppBridge)

    non-null

    The [App Bridge configuration](https://shopify.dev/docs/api/app-bridge) for the [discount type](https://help.shopify.com/manual/discounts/discount-types).

  * app​Key

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The [client ID](https://shopify.dev/docs/apps/build/authentication-authorization/client-secrets) of the app extension that's providing the [discount type](https://help.shopify.com/manual/discounts/discount-types).

  * description

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    A description of the [discount type](https://help.shopify.com/manual/discounts/discount-types) provided by the app extension.

  * discount​Classes

    [\[Discount​Class!\]!](https://shopify.dev/docs/api/admin-graphql/latest/enums/DiscountClass)

    non-null

    The list of [discount classes](https://help.shopify.com/manual/discounts/combining-discounts/discount-combinations) that this app extension supports.

  * function​Id

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The [function ID](https://shopify.dev/docs/apps/build/functions/input-output/metafields-for-input-queries) associated with the app extension providing the [discount type](https://help.shopify.com/manual/discounts/discount-types).

  * title

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of the [discount type](https://help.shopify.com/manual/discounts/discount-types) that the app extension is providing.

  * discount​Class

    [Discount​Class!](https://shopify.dev/docs/api/admin-graphql/latest/enums/DiscountClass)

    non-nullDeprecated

  * target​Type

    [Discount​Application​Target​Type!](https://shopify.dev/docs/api/admin-graphql/latest/enums/DiscountApplicationTargetType)

    non-nullDeprecated

***

## Examples

* ### appDiscountTypes reference
