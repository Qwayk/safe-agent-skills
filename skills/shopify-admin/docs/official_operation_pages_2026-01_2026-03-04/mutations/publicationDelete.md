---
title: publicationDelete - GraphQL Admin
description: Deletes a publication.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/publicationDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/publicationDelete.md
---

# publication​Delete

mutation

Requires `write_publications` access scope. Also: The user must have a permission to create and edit catalogs.

Deletes a publication.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the publication to delete.

***

## Publication​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the publication that was deleted.

* user​Errors

  [\[Publication​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PublicationUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### publicationDelete reference
