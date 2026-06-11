---
title: productFeedDelete - GraphQL Admin
description: Deletes a product feed for a specific publication.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productFeedDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productFeedDelete.md
---

# product​Feed​Delete

mutation

Requires Access allowed for apps with `read_product_listings` scope.

Deletes a product feed for a specific publication.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the product feed to be deleted.

***

## Product​Feed​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the product feed that was deleted.

* user​Errors

  [\[Product​Feed​Delete​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductFeedDeleteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### productFeedDelete reference
