---
title: productVariantsBulkReorder - GraphQL Admin
description: >-
  Reorders multiple variants in a single product. This mutation can be called
  directly or via the bulkOperation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkReorder
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkReorder.md
---

# product​Variants​Bulk​Reorder

mutation

Requires `write_products` access scope. Also: The user must have a permission to reorder product variants.

Reorders multiple variants in a single product. This mutation can be called directly or via the bulkOperation.

## Arguments

* positions

  [\[Product​Variant​Position​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductVariantPositionInput)

  required

  An array of variant positions.

* product​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The product ID of the variants to be reordered.

***

## Product​Variants​Bulk​Reorder​Payload returns

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The updated product.

* user​Errors

  [\[Product​Variants​Bulk​Reorder​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariantsBulkReorderUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### productVariantsBulkReorder reference
