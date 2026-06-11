---
title: productFeedCreate - GraphQL Admin
description: Creates a product feed for a specific publication.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productFeedCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productFeedCreate.md
---

# product​Feed​Create

mutation

Requires Access allowed for apps with `read_product_listings` scope.

Creates a product feed for a specific publication.

## Arguments

* input

  [Product​Feed​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductFeedInput)

  The properties of the new product feed.

***

## Product​Feed​Create​Payload returns

* product​Feed

  [Product​Feed](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductFeed)

  The newly created product feed.

* user​Errors

  [\[Product​Feed​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductFeedCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### productFeedCreate reference
