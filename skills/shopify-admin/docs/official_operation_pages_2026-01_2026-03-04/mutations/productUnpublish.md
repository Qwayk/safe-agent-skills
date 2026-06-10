---
title: productUnpublish - GraphQL Admin
description: Unpublishes a product.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUnpublish'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUnpublish.md
---

# product​Unpublish

mutation

Requires `write_publications` access scope. Also: The user must have a permission to unpublish a product.

Deprecated. Use [publishableUnpublish](https://shopify.dev/docs/api/admin-graphql/latest/mutations/publishableUnpublish) instead.

Unpublishes a product.

## Arguments

* input

  [Product​Unpublish​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductUnpublishInput)

  required

  Specifies the product to unpublish and the channel to unpublish it from.

***

## Product​Unpublish​Payload returns

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The product that has been unpublished.

* shop

  [Shop!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Shop)

  non-null

  The user's shop.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### productUnpublish reference
