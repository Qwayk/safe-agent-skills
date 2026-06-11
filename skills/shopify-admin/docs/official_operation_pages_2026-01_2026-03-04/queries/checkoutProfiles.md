---
title: checkoutProfiles - GraphQL Admin
description: List of checkout profiles on a shop.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/checkoutProfiles'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/checkoutProfiles.md
---

# checkout​Profiles

query

Requires access to the checkout and accounts editor.

List of checkout profiles on a shop.

## CheckoutProfileConnection arguments

[CheckoutProfileConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CheckoutProfileConnection)

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

  * * id

      id

    * is\_published

      boolean

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Checkout​Profile​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/CheckoutProfileSortKeys)

  Default:UPDATED\_AT

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Checkout​Profile​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutProfileEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Checkout​Profile!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CheckoutProfile)

  non-null

  A list of nodes that are contained in CheckoutProfileEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Reference checkout profiles

  #### Query

  ```graphql
  query checkoutProfiles {
    checkoutProfiles(first: 10) {
      nodes {
        id
        isPublished
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
  "query": "query checkoutProfiles { checkoutProfiles(first: 10) { nodes { id isPublished } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query checkoutProfiles {
      checkoutProfiles(first: 10) {
        nodes {
          id
          isPublished
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
    query checkoutProfiles {
      checkoutProfiles(first: 10) {
        nodes {
          id
          isPublished
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
    data: `query checkoutProfiles {
      checkoutProfiles(first: 10) {
        nodes {
          id
          isPublished
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query checkoutProfiles {
    checkoutProfiles(first: 10) {
      nodes {
        id
        isPublished
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "checkoutProfiles": {
      "nodes": [
        {
          "id": "gid://shopify/CheckoutProfile/890967685",
          "isPublished": true
        }
      ]
    }
  }
  ```
