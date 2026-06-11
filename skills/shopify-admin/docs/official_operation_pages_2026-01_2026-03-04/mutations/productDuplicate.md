---
title: productDuplicate - GraphQL Admin
description: >-
  Duplicates a product.


  If you need to duplicate a large product, such as one that has many

  [variants](https://shopify.dev/api/admin-graphql/latest/input-objects/ProductVariantInput)

  that are active at several

  [locations](https://shopify.dev/api/admin-graphql/latest/input-objects/InventoryLevelInput),

  you might encounter timeout errors.


  To avoid these timeout errors, you can instead duplicate the product
  asynchronously.


  In API version 2024-10 and higher, include `synchronous: false` argument in
  this mutation to perform the duplication asynchronously.


  In API version 2024-07 and lower, use the asynchronous
  [`ProductDuplicateAsyncV2`](https://shopify.dev/api/admin-graphql/2024-07/mutations/productDuplicateAsyncV2).


  Metafield values are not duplicated if the unique values capability is
  enabled.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/productDuplicate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productDuplicate.md
---

# product​Duplicate

mutation

Requires `write_products` access scope. Also: The user must have a permission to duplicate a product.

Duplicates a product.

If you need to duplicate a large product, such as one that has many [variants](https://shopify.dev/api/admin-graphql/latest/input-objects/ProductVariantInput) that are active at several [locations](https://shopify.dev/api/admin-graphql/latest/input-objects/InventoryLevelInput), you might encounter timeout errors.

To avoid these timeout errors, you can instead duplicate the product asynchronously.

In API version 2024-10 and higher, include `synchronous: false` argument in this mutation to perform the duplication asynchronously.

In API version 2024-07 and lower, use the asynchronous [`ProductDuplicateAsyncV2`](https://shopify.dev/api/admin-graphql/2024-07/mutations/productDuplicateAsyncV2).

Metafield values are not duplicated if the unique values capability is enabled.

## Arguments

* include​Images

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Specifies whether or not to duplicate images.

* include​Translations

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Specifies whether or not to duplicate translations.

* new​Status

  [Product​Status](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductStatus)

  The new status of the product. If no value is provided the status will be inherited from the original product.

* new​Title

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The new title of the product.

* product​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the product to be duplicated.

* synchronous

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:true

  Specifies whether or not to run the mutation synchronously.

***

## Product​Duplicate​Payload returns

* image​Job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job that duplicates the product images.

* new​Product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The duplicated product.

* product​Duplicate​Operation

  [Product​Duplicate​Operation](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductDuplicateOperation)

  The product duplicate operation, returned when run in asynchronous mode.

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

* ### productDuplicate reference
