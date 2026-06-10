---
title: collectionDuplicate - GraphQL Admin
description: >-
  Duplicates a
  [collection](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection).


  An existing collection ID and new title are required.


  ## Publication Duplication


  Publications may be excluded by passing `copyPublications: false` in the
  input.


  ## Metafields

  Metafield values are not duplicated if the unique values capability is
  enabled.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionDuplicate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionDuplicate.md
---

# collection​Duplicate

mutation

Requires `write_products` access scope. Also: The store must not be on the Starter or Retail plans and user must have permission to create collections. If also copying publications, user must have permission to manage publications.

Duplicates a [collection](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection).

An existing collection ID and new title are required.

## Publication Duplication

Publications may be excluded by passing `copyPublications: false` in the input.

## Metafields

Metafield values are not duplicated if the unique values capability is enabled.

## Arguments

* input

  [Collection​Duplicate​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CollectionDuplicateInput)

  required

  The input for duplicating a collection.

***

## Collection​Duplicate​Payload returns

* collection

  [Collection](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection)

  The newly created duplicate collection. Will contain all data if duplication completed synchronously. If async processing is required, the collection will be created but products will be added in the background and can be tracked via the job field or the collection's active\_operations field.

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The background job copying manually included products onto the target collection. Only returned if async processing is required, otherwise products will be copied synchronously when the collection is created.

* user​Errors

  [\[Collection​Duplicate​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CollectionDuplicateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### collectionDuplicate reference
