---
title: urlRedirects - GraphQL Admin
description: A list of redirects for a shop.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/urlRedirects'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/urlRedirects.md'
---

# url​Redirects

query

A list of redirects for a shop.

## UrlRedirectConnection arguments

[UrlRedirectConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/UrlRedirectConnection)

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

    * created\_at

      time

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:
      * `query=Bob Norman`
      * `query=title:green hoodie`

  * * id

      id

    * path

      string

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * target

    string

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

* sort​Key

  [Url​Redirect​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/UrlRedirectSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Url​Redirect​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UrlRedirectEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Url​Redirect!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UrlRedirect)

  non-null

  A list of nodes that are contained in UrlRedirectEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieves a list of URL redirects

  #### Query

  ```graphql
  query UrlRedirects {
    urlRedirects(first: 100) {
      edges {
        node {
          id
          path
          target
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
  "query": "query UrlRedirects { urlRedirects(first: 100) { edges { node { id path target } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query UrlRedirects {
      urlRedirects(first: 100) {
        edges {
          node {
            id
            path
            target
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
    query UrlRedirects {
      urlRedirects(first: 100) {
        edges {
          node {
            id
            path
            target
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
    data: `query UrlRedirects {
      urlRedirects(first: 100) {
        edges {
          node {
            id
            path
            target
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
  'query UrlRedirects {
    urlRedirects(first: 100) {
      edges {
        node {
          id
          path
          target
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "urlRedirects": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/UrlRedirect/510765931",
            "path": "/page%20with%20many%20spaces",
            "target": "/products/element"
          }
        },
        {
          "node": {
            "id": "gid://shopify/UrlRedirect/891487173",
            "path": "/about-us",
            "target": "/pages/aboutus"
          }
        },
        {
          "node": {
            "id": "gid://shopify/UrlRedirect/905192165",
            "path": "/about",
            "target": "/pages/aboutus"
          }
        },
        {
          "node": {
            "id": "gid://shopify/UrlRedirect/979034143",
            "path": "/2008/01/01/look-at-my-cool-new-snowboard",
            "target": "/products/draft"
          }
        },
        {
          "node": {
            "id": "gid://shopify/UrlRedirect/984542198",
            "path": "/aboutus",
            "target": "/pages/aboutus"
          }
        }
      ]
    }
  }
  ```
