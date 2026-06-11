---
title: blogs - GraphQL Admin
description: >-
  Returns a paginated list of the shop's
  [`Blog`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Blog)
  objects. Blogs serve as containers for
  [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article)
  objects and provide content management capabilities for the store's editorial
  content.


  Supports [cursor-based
  pagination](https://shopify.dev/docs/api/usage/pagination-graphql) to control
  the number of blogs returned and their order. Use the
  [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/blogs#arguments-query)
  argument to filter results by specific criteria.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/blogs'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/blogs.md'
---

# blogs

query

Returns a paginated list of the shop's [`Blog`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Blog) objects. Blogs serve as containers for [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article) objects and provide content management capabilities for the store's editorial content.

Supports [cursor-based pagination](https://shopify.dev/docs/api/usage/pagination-graphql) to control the number of blogs returned and their order. Use the [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/blogs#arguments-query) argument to filter results by specific criteria.

## BlogConnection arguments

[BlogConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/BlogConnection)

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

  * handle

    string

  * * id

      id

    * title

      string

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * updated\_at

    time

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Blog​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/BlogSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Blog​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BlogEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Blog!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Blog)

  non-null

  A list of nodes that are contained in BlogEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve a list of all blogs

  #### Query

  ```graphql
  query BlogList {
    blogs(first: 50) {
      nodes {
        id
        handle
        title
        updatedAt
        commentPolicy
        feed {
          path
          location
        }
        createdAt
        templateSuffix
        tags
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
  "query": "query BlogList { blogs(first: 50) { nodes { id handle title updatedAt commentPolicy feed { path location } createdAt templateSuffix tags } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query BlogList {
      blogs(first: 50) {
        nodes {
          id
          handle
          title
          updatedAt
          commentPolicy
          feed {
            path
            location
          }
          createdAt
          templateSuffix
          tags
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
    query BlogList {
      blogs(first: 50) {
        nodes {
          id
          handle
          title
          updatedAt
          commentPolicy
          feed {
            path
            location
          }
          createdAt
          templateSuffix
          tags
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
    data: `query BlogList {
      blogs(first: 50) {
        nodes {
          id
          handle
          title
          updatedAt
          commentPolicy
          feed {
            path
            location
          }
          createdAt
          templateSuffix
          tags
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query BlogList {
    blogs(first: 50) {
      nodes {
        id
        handle
        title
        updatedAt
        commentPolicy
        feed {
          path
          location
        }
        createdAt
        templateSuffix
        tags
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "blogs": {
      "nodes": [
        {
          "id": "gid://shopify/Blog/389767568",
          "handle": "bluecheese-blog",
          "title": "The Blog",
          "updatedAt": "2024-02-02T00:00:00Z",
          "commentPolicy": "CLOSED",
          "feed": null,
          "createdAt": "2023-02-01T00:00:00Z",
          "templateSuffix": null,
          "tags": []
        },
        {
          "id": "gid://shopify/Blog/397675442",
          "handle": "smallcheese-blog",
          "title": "Yo Blog",
          "updatedAt": "2011-11-02T00:00:00Z",
          "commentPolicy": "CLOSED",
          "feed": null,
          "createdAt": "2024-10-29T22:38:08Z",
          "templateSuffix": null,
          "tags": [
            "not_alpha"
          ]
        },
        {
          "id": "gid://shopify/Blog/854997985",
          "handle": "bigcheese-blog",
          "title": "Mah Blog",
          "updatedAt": "2006-02-02T00:00:00Z",
          "commentPolicy": "CLOSED",
          "feed": null,
          "createdAt": "2006-02-01T00:00:00Z",
          "templateSuffix": null,
          "tags": [
            "alpha",
            "important"
          ]
        }
      ]
    }
  }
  ```
