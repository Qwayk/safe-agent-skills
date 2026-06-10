---
title: shopifyFunction - GraphQL Admin
description: >-
  Returns a Shopify Function by its ID.

  [Functions](https://shopify.dev/apps/build/functions)

  enable you to customize Shopify's backend logic at defined parts of the
  commerce loop.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/shopifyFunction'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/shopifyFunction.md'
---

# shopify​Function

query

Returns a Shopify Function by its ID. [Functions](https://shopify.dev/apps/build/functions) enable you to customize Shopify's backend logic at defined parts of the commerce loop.

## Arguments

* id

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The ID of the Shopify Function.

***

## Possible returns

* Shopify​Function

  [Shopify​Function](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyFunction)

  A Shopify Function.

  * api​Type

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The API type of the Shopify Function.

  * api​Version

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The API version of the Shopify Function.

  * app

    [App!](https://shopify.dev/docs/api/admin-graphql/latest/objects/App)

    non-null

    The app that owns the Shopify Function.

  * app​Bridge

    [Functions​App​Bridge!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FunctionsAppBridge)

    non-null

    The App Bridge information for the Shopify Function.

  * app​Key

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The client ID of the app that owns the Shopify Function.

  * description

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The description of the Shopify Function.

  * handle

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The handle of the Shopify Function.

  * id

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The ID of the Shopify Function.

  * input​Query

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The input query of the Shopify Function.

  * title

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The title of the Shopify Function.

  * use​Creation​Ui

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    If the Shopify Function uses the creation UI in the Admin.

***

## Examples

* ### shopifyFunction reference
