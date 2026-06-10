---
title: companyLocations - GraphQL Admin
description: >-
  A paginated list of
  [`CompanyLocation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation)
  objects for B2B customers. Company locations represent individual branches or
  offices of a
  [`Company`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Company)
  where B2B orders can be placed.


  Each location can have its own billing and shipping addresses, tax settings,
  [`PaymentTerms`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTerms),
  and
  [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog)
  assignments with custom pricing. Use the query parameter to search locations
  by name or other attributes.


  Learn more about [managing company
  locations](https://shopify.dev/docs/apps/build/b2b/manage-client-company-locations).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/companyLocations'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/companyLocations.md
---

# company​Locations

query

A paginated list of [`CompanyLocation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation) objects for B2B customers. Company locations represent individual branches or offices of a [`Company`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Company) where B2B orders can be placed.

Each location can have its own billing and shipping addresses, tax settings, [`PaymentTerms`](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTerms), and [`Catalog`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog) assignments with custom pricing. Use the query parameter to search locations by name or other attributes.

Learn more about [managing company locations](https://shopify.dev/docs/apps/build/b2b/manage-client-company-locations).

## CompanyLocationConnection arguments

[CompanyLocationConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CompanyLocationConnection)

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

    * company\_id

      id

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:
      * `query=Bob Norman`
      * `query=title:green hoodie`

  * created\_at

    time

  * external\_id

    string

  * * id

      id

    * ids

      string

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * * metafields.{namespace}.{key}

      mixed

    * name

      string

    - Filters resources by metafield value. Format: `metafields.{namespace}.{key}:{value}`. Learn more about [querying by metafield value](https://shopify.dev/apps/build/custom-data/metafields/query-by-metafield-value).

    - Example:
      * `metafields.custom.on_sale:true`
      * `metafields.product.material:"gid://shopify/Metaobject/43458085"`

  * updated\_at

    time

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Company​Location​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/CompanyLocationSortKeys)

  Default:ID

  Sort the underlying list by the given key.

***

## Possible returns

* edges

  [\[Company​Location​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocationEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Company​Location!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation)

  non-null

  A list of nodes that are contained in CompanyLocationEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### companyLocations reference
