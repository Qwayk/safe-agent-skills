---
title: companies - GraphQL Admin
description: >-
  A paginated list of companies in the shop.
  [`Company`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Company)
  objects are business entities that purchase from the merchant.


  Use the
  [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/companies#arguments-query)
  argument to filter companies by attributes like name or externalId. Sort and
  paginate results to handle large datasets efficiently. Learn more about
  [Shopify API search syntax](https://shopify.dev/docs/api/usage/search-syntax).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/companies'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/companies.md'
---

# companies

query

A paginated list of companies in the shop. [`Company`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Company) objects are business entities that purchase from the merchant.

Use the [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/companies#arguments-query) argument to filter companies by attributes like name or externalId. Sort and paginate results to handle large datasets efficiently. Learn more about [Shopify API search syntax](https://shopify.dev/docs/api/usage/search-syntax).

## CompanyConnection arguments

[CompanyConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CompanyConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * default

      string

    * active\_customers\_count

      integer

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:
      * `query=Bob Norman`
      * `query=title:green hoodie`

  * created\_at

    time

  * external\_id

    id

  * * id

      id

    * metafields.{namespace}.{key}

      mixed

    * name

      string

    - Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filters resources by metafield value. Format: `metafields.{namespace}.{key}:{value}`. Learn more about [querying by metafield value](https://shopify.dev/apps/build/custom-data/metafields/query-by-metafield-value).

    - Example:
      * `metafields.custom.on_sale:true`
      * `metafields.product.material:"gid://shopify/Metaobject/43458085"`

  * since\_date

    time

  * updated\_at

    time

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Company​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/CompanySortKeys)

  Default:ID

  Sort the underlying list by the given key.

***

## Possible returns

* edges

  [\[Company​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Company!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Company)

  non-null

  A list of nodes that are contained in CompanyEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### companies reference
