---
title: collectionUnpublish - GraphQL Admin
description: Unpublishes a collection.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionUnpublish
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionUnpublish.md
---

# collection​Unpublish

mutation

Requires `write_publications` access scope. Also: The user must have a permission to unpublish a collection.

Deprecated. Use [publishableUnpublish](https://shopify.dev/docs/api/admin-graphql/latest/mutations/publishableUnpublish) instead.

Unpublishes a collection.

## Arguments

* input

  [Collection​Unpublish​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CollectionUnpublishInput)

  required

  Specify a collection to unpublish and the sales channels to remove it from.

***

## Collection​Unpublish​Payload returns

* collection

  [Collection](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection)

  The collection that has been unpublished.

* shop

  [Shop!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Shop)

  non-null

  The shop associated with the collection.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### collectionUnpublish reference
