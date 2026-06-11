---
title: companyContactRole - GraphQL Admin
description: Returns a `CompanyContactRole` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/companyContactRole'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/companyContactRole.md
---

# company​Contact​Role

query

Returns a `CompanyContactRole` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `CompanyContactRole` to return.

***

## Possible returns

* Company​Contact​Role

  [Company​Contact​Role](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyContactRole)

  The role for a [company contact](https://shopify.dev/api/admin-graphql/latest/objects/companycontact).

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of a role. For example, `admin` or `buyer`.

  * note

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    A note for the role.

***

## Examples

* ### companyContactRole reference
