---
title: segments - GraphQL Admin
description: >-
  Returns a paginated list of
  [`Segment`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Segment)
  objects for the shop. Segments are dynamic groups of customers that meet
  specific criteria defined through [ShopifyQL
  queries](https://shopify.dev/docs/api/shopifyql/segment-query-language-reference).
  You can filter segments by search query and sort them by creation date or
  other criteria.


  The query supports standard
  [pagination](https://shopify.dev/docs/api/usage/pagination-graphql) arguments
  and returns a
  [`SegmentConnection`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SegmentConnection)
  containing segment details including names, creation dates, and the query
  definitions that determine segment membership.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/segments'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/segments.md'
---

# segments

query

Returns a paginated list of [`Segment`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Segment) objects for the shop. Segments are dynamic groups of customers that meet specific criteria defined through [ShopifyQL queries](https://shopify.dev/docs/api/shopifyql/segment-query-language-reference). You can filter segments by search query and sort them by creation date or other criteria.

The query supports standard [pagination](https://shopify.dev/docs/api/usage/pagination-graphql) arguments and returns a [`SegmentConnection`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SegmentConnection) containing segment details including names, creation dates, and the query definitions that determine segment membership.

## SegmentConnection arguments

[SegmentConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SegmentConnection)

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

    * id

      id

    * name

      string

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Segment​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/SegmentSortKeys)

  Default:CREATION\_DATE

  Sort the underlying list by the given key.

***

## Possible returns

* edges

  [\[Segment​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SegmentEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Segment!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Segment)

  non-null

  A list of nodes that are contained in SegmentEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieves the first three segments from a shop

  #### Description

  The following query retrieves the first three segments from a shop.

  #### Query

  ```graphql
  query {
    segments(first: 3) {
      edges {
        node {
          id
        }
      }
    }
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query { segments(first: 3) { edges { node { id } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      segments(first: 3) {
        edges {
          node {
            id
          }
        }
      }
    }`,
    );
    const json = await response.json();
    return json.data;
  }
  ```

  #### Ruby

  ```ruby
  session = ShopifyAPI::Auth::Session.new(
    shop: "your-development-store.myshopify.com",
    access_token: access_token
  )
  client = ShopifyAPI::Clients::Graphql::Admin.new(
    session: session
  )

  query = <<~QUERY
    query {
      segments(first: 3) {
        edges {
          node {
            id
          }
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      segments(first: 3) {
        edges {
          node {
            id
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    segments(first: 3) {
      edges {
        node {
          id
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "segments": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Segment/210588551"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Segment/250599805"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Segment/631221407"
          }
        }
      ]
    }
  }
  ```
