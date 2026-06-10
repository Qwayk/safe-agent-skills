---
title: sellingPlanGroup - GraphQL Admin
description: Returns a `SellingPlanGroup` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/sellingPlanGroup'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/sellingPlanGroup.md
---

# selling​Plan​Group

query

Returns a `SellingPlanGroup` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `SellingPlanGroup` to return.

***

## Possible returns

* Selling​Plan​Group

  [Selling​Plan​Group](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroup)

  A selling method that defines how products can be sold through purchase options like subscriptions, pre-orders, or try-before-you-buy. Groups one or more [`SellingPlan`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlan) objects that share the same selling method and options.

  The group provides buyer-facing labels and merchant-facing descriptions for the selling method. Associates [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) and [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) objects with selling plan groups to offer them through these purchase options.

  ***

  **Caution:** Selling plan groups and their associated records are automatically deleted 48 hours after a merchant uninstalls the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/objects/App">\<code>App\</code>\</a> that created them. Back up these records if you need to restore them later.

  ***

  * app​Id

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The ID for app, exposed in Liquid and product JSON.

  * applies​To​Product

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the given product is directly associated to the selling plan group.

    * product​Id

      [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      required

      ### Arguments

      The ID of the product.

    ***

  * applies​To​Product​Variant

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the given product variant is directly associated to the selling plan group.

    * product​Variant​Id

      [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      required

      ### Arguments

      The ID of the product.

    ***

  * applies​To​Product​Variants

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether any of the product variants of the given product are associated to the selling plan group.

    * product​Id

      [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      required

      ### Arguments

      The ID of the product.

    ***

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the selling plan group was created.

  * description

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The merchant-facing description of the selling plan group.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * merchant​Code

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The merchant-facing label of the selling plan group.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The buyer-facing label of the selling plan group.

  * options

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The values of all options available on the selling plan group. Selling plans are grouped together in Liquid when they're created by the same app, and have the same `selling_plan_group.name` and `selling_plan_group.options` values.

  * position

    [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    The relative position of the selling plan group for display.

  * products

    [Product​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductConnection)

    non-null

    Products associated to the selling plan group.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * products​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    A count of products associated to the selling plan group.

  * product​Variants

    [Product​Variant​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductVariantConnection)

    non-null

    Product variants associated to the selling plan group.

    * product​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      ### Arguments

      Filters the product variants by a product ID.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * product​Variants​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    A count of product variants associated to the selling plan group.

    * product​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      ### Arguments

      The ID of the product to scope the count to.

    ***

  * selling​Plans

    [Selling​Plan​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SellingPlanConnection)

    non-null

    Selling plans associated to the selling plan group.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * summary

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    A summary of the policies associated to the selling plan group.

  * translations

    [\[Translation!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Translation)

    non-null

    The published translations associated with the resource.

    * locale

      [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      required

      ### Arguments

      Filters translations locale.

    * market​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      Filters translations by market ID. Use this argument to retrieve content specific to a market.

    ***

***

## Examples

* ### sellingPlanGroup reference
