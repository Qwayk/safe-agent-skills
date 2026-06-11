---
title: publicationUpdate - GraphQL Admin
description: >-
  Updates a
  [`Publication`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication).


  You can add or remove
  [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)
  from the publication, with a maximum of 50 items per operation. The
  [`autoPublish`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/publicationUpdate#arguments-input.fields.autoPublish)
  field determines whether new products automatically display in this
  publication.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/publicationUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/publicationUpdate.md
---

# publication​Update

mutation

Requires `write_publications` access scope. Also: The user must have a permission to create and edit catalogs.

Updates a [`Publication`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication).

You can add or remove [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) from the publication, with a maximum of 50 items per operation. The [`autoPublish`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/publicationUpdate#arguments-input.fields.autoPublish) field determines whether new products automatically display in this publication.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the publication to update.

* input

  [Publication​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PublicationUpdateInput)

  required

  The input fields to use when updating the publication.

***

## Publication​Update​Payload returns

* publication

  [Publication](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication)

  The publication that's been updated.

* user​Errors

  [\[Publication​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PublicationUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### publicationUpdate reference
