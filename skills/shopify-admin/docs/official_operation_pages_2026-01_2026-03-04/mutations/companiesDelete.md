---
title: companiesDelete - GraphQL Admin
description: Deletes a list of companies.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/companiesDelete'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/companiesDelete.md
---

# companies​Delete

mutation

Requires `write_customers` access scope or `write_companies` access scope. Also: The API client must be installed on a Shopify Plus store.

Deletes a list of companies.

## Arguments

* company​Ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  A list of IDs of companies to delete.

***

## Companies​Delete​Payload returns

* deleted​Company​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  A list of IDs of the deleted companies.

* user​Errors

  [\[Business​Customer​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessCustomerUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### companiesDelete reference
