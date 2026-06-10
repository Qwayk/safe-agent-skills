---
title: collectionAddProductsV2 - GraphQL Admin
description: >-
  Adds products to a
  [`Collection`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection)
  asynchronously and returns a
  [`Job`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job) to
  track the operation's progress. This mutation handles large product sets
  efficiently by processing them in the background.


  You can poll the returned job using the
  [`job`](https://shopify.dev/docs/api/admin-graphql/latest/queries/job) query
  to monitor completion status.


  > Note:

  > This mutation adds products in the order specified in the
  [`productIds`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionAddProducts#arguments-productIds)
  argument.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionAddProductsV2
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionAddProductsV2.md
---

# collection​Add​Products​V2

mutation

Requires `write_products` access scope. Also: The user must have a permission to add products to a collection.

Adds products to a [`Collection`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection) asynchronously and returns a [`Job`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job) to track the operation's progress. This mutation handles large product sets efficiently by processing them in the background.

You can poll the returned job using the [`job`](https://shopify.dev/docs/api/admin-graphql/latest/queries/job) query to monitor completion status.

***

**Note:** This mutation adds products in the order specified in the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionAddProducts#arguments-productIds">\<code>\<span class="PreventFireFoxApplyingGapToWBR">product\<wbr/>Ids\</span>\</code>\</a> argument.

***

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the collection that's being updated.

* product​Ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The IDs of the products that are being added to the collection. If the collection's sort order is manual, the products will be added in the order in which they are provided.

***

## Collection​Add​Products​V2Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job adding the products.

* user​Errors

  [\[Collection​Add​Products​V2User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CollectionAddProductsV2UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### collectionAddProductsV2 reference
