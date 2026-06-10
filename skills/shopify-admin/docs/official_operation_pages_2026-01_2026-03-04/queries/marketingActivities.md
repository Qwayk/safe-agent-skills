---
title: marketingActivities - GraphQL Admin
description: A list of marketing activities associated with the marketing app.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/marketingActivities
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/marketingActivities.md
---

# marketing​Activities

query

A list of marketing activities associated with the marketing app.

## MarketingActivityConnection arguments

[MarketingActivityConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MarketingActivityConnection)

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

* marketing​Activity​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  Default:\[]

  The list of marketing activity IDs to filter by.

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * default

      string

    * app\_id

      id

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:
      * `query=Bob Norman`
      * `query=title:green hoodie`

  * app\_name

    string

    A comma-separated list of app names.

  * created\_at

    time

  * * id

      id

    * marketing\_campaign\_id

      id

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * scheduled\_to\_end\_at

    time

  * scheduled\_to\_start\_at

    time

  * tactic

    string

  * title

    string

  * updated\_at

    time

* remote​Ids

  [\[String!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  Default:\[]

  The list of remote IDs associated with marketing activities to filter by.

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

* sort​Key

  [Marketing​Activity​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/MarketingActivitySortKeys)

  Default:CREATED\_AT

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

* utm

  [UTMInput](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/UTMInput)

  The UTM parameters associated with marketing activities to filter by.

***

## Possible returns

* edges

  [\[Marketing​Activity​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketingActivityEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Marketing​Activity!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketingActivity)

  non-null

  A list of nodes that are contained in MarketingActivityEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### marketingActivities reference
