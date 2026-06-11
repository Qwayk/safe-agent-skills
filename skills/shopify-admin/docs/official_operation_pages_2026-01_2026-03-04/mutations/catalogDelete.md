---
title: catalogDelete - GraphQL Admin
description: Delete a catalog.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogDelete'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogDelete.md'
---

# catalog​Delete

mutation

Requires `write_products` access scope. Also: The user must have permission to delete catalogs.

Delete a catalog.

## Arguments

* delete​Dependent​Resources

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Whether to also delete the price list and the publication owned by the catalog.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the catalog to delete.

***

## Catalog​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted catalog.

* user​Errors

  [\[Catalog​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CatalogUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### catalogDelete reference
