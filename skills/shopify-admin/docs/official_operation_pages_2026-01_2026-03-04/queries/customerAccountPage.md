---
title: customerAccountPage - GraphQL Admin
description: Returns a `CustomerAccountPage` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/customerAccountPage
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/customerAccountPage.md
---

# customer​Account​Page

query

Returns a `CustomerAccountPage` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `CustomerAccountPage` to return.

***

## Possible returns

* Customer​Account​Page

  [Customer​Account​Page](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/CustomerAccountPage)

  A customer account page.

  * default​Cursor

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A default [cursor](https://shopify.dev/api/usage/pagination-graphql) that returns the single next record, sorted ascending by ID.

  * handle

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A unique, human-friendly string for the customer account page.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    The unique ID for the customer account page.

  * title

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The title of the customer account page.

***

## Examples

* ### customerAccountPage reference
