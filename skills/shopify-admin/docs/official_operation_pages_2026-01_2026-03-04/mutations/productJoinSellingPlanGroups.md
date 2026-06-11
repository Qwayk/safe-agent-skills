---
title: productJoinSellingPlanGroups - GraphQL Admin
description: Adds multiple selling plan groups to a product.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productJoinSellingPlanGroups
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/productJoinSellingPlanGroups.md
---

# product​Join​Selling​Plan​Groups

mutation

Requires `write_products` access scope as well as any of `write_own_subscription_contracts`, `write_purchase_options` access scopes. Also: The user must have `manage_orders_information` permissions.

Adds multiple selling plan groups to a product.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the product.

* selling​Plan​Group​Ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The IDs of the selling plan groups to add.

***

## Product​Join​Selling​Plan​Groups​Payload returns

* product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The product object.

* user​Errors

  [\[Selling​Plan​Group​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroupUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### productJoinSellingPlanGroups reference
