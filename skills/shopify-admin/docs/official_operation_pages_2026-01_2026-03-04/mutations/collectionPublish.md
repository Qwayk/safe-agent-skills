---
title: collectionPublish - GraphQL Admin
description: Publishes a collection to a channel.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionPublish
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionPublish.md
---

# collection​Publish

mutation

Requires `write_publications` access scope. Also: The user must have a permission to publish a collection.

Deprecated. Use [publishablePublish](https://shopify.dev/docs/api/admin-graphql/latest/mutations/publishablePublish) instead.

Publishes a collection to a channel.

## Arguments

* input

  [Collection​Publish​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CollectionPublishInput)

  required

  Specify a collection to publish and the sales channels to publish it to.

***

## Collection​Publish​Payload returns

* collection

  [Collection](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection)

  The published collection.

* collection​Publications

  [\[Collection​Publication!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/CollectionPublication)

  The channels where the collection has been published.

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

* ### collectionPublish reference
