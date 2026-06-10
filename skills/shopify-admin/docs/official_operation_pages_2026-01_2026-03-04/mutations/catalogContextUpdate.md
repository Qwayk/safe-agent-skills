---
title: catalogContextUpdate - GraphQL Admin
description: >-
  Modifies which contexts, like
  [markets](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market) or
  B2B [company
  locations](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation),
  can access a
  [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog).
  You can add or remove contexts to control where the catalog's products and
  prices are available.


  Learn more about [managing catalog
  contexts](https://shopify.dev/docs/apps/build/markets/new-markets/catalogs)
  and [managing B2B
  catalogs](https://shopify.dev/docs/apps/build/b2b/manage-catalogs).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogContextUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/catalogContextUpdate.md
---

# catalog​Context​Update

mutation

Requires `write_products` access scope. Also: The user must have permission to create and edit catalogs.

Modifies which contexts, like [markets](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market) or B2B [company locations](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation), can access a [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog). You can add or remove contexts to control where the catalog's products and prices are available.

Learn more about [managing catalog contexts](https://shopify.dev/docs/apps/build/markets/new-markets/catalogs) and [managing B2B catalogs](https://shopify.dev/docs/apps/build/b2b/manage-catalogs).

## Arguments

* catalog​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the catalog for which to update the context.

* contexts​To​Add

  [Catalog​Context​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CatalogContextInput)

  The contexts to add to the catalog.

* contexts​To​Remove

  [Catalog​Context​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CatalogContextInput)

  The contexts to remove from the catalog.

***

## Catalog​Context​Update​Payload returns

* catalog

  [Catalog](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog)

  The updated catalog.

* user​Errors

  [\[Catalog​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CatalogUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### catalogContextUpdate reference
