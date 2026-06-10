---
title: pages - GraphQL Admin
description: >-
  A paginated list of pages from the online store.
  [`Page`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page)
  objects are content pages that merchants create to provide information to
  customers, such as "About Us", "Contact", or policy pages.


  The query supports filtering with a [search
  query](https://shopify.dev/docs/api/usage/search-syntax) and sorting by
  various criteria. Advanced filtering is available through saved searches using
  the
  [`savedSearchId`](https://shopify.dev/docs/api/admin-graphql/latest/queries/pages#arguments-savedSearchId)
  argument.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/pages'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/pages.md'
---

# pages

query

A paginated list of pages from the online store. [`Page`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page) objects are content pages that merchants create to provide information to customers, such as "About Us", "Contact", or policy pages.

The query supports filtering with a [search query](https://shopify.dev/docs/api/usage/search-syntax) and sorting by various criteria. Advanced filtering is available through saved searches using the [`savedSearchId`](https://shopify.dev/docs/api/admin-graphql/latest/queries/pages#arguments-savedSearchId) argument.

## PageConnection arguments

[PageConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/PageConnection)

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

    * handle

      string

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      Filter by the date and time when the page was created.

    - Example:

      * `created_at:>'2020-10-21T23:39:20Z'`
      * `created_at:<now`
      * `created_at:<=2024`

      Filter by the handle of the page.

  * * id

      id

    * published\_at

      time

    * published\_status

      string

    - Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by the date and time when the page was published.

    - Example:

      * `published_at:>'2020-10-21T23:39:20Z'`
      * `published_at:<now`
      * `published_at:<=2024`

      Filter by published status

  * title

    string

    Filter by the title of the page.

  * updated\_at

    time

    Filter by the date and time when the page was last updated.

    Example:

    * `updated_at:>'2020-10-21T23:39:20Z'`
    * `updated_at:<now`
    * `updated_at:<=2024`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

* sort​Key

  [Page​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/PageSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Page​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Page!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Page)

  non-null

  A list of nodes that are contained in PageEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieves a list of pages

  #### Query

  ```graphql
  query PageList {
    pages(first: 10) {
      edges {
        node {
          id
        }
      }
      pageInfo {
        endCursor
        hasNextPage
        hasPreviousPage
        startCursor
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
  "query": "query PageList { pages(first: 10) { edges { node { id } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query PageList {
      pages(first: 10) {
        edges {
          node {
            id
          }
        }
        pageInfo {
          endCursor
          hasNextPage
          hasPreviousPage
          startCursor
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
    query PageList {
      pages(first: 10) {
        edges {
          node {
            id
          }
        }
        pageInfo {
          endCursor
          hasNextPage
          hasPreviousPage
          startCursor
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
    data: `query PageList {
      pages(first: 10) {
        edges {
          node {
            id
          }
        }
        pageInfo {
          endCursor
          hasNextPage
          hasPreviousPage
          startCursor
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query PageList {
    pages(first: 10) {
      edges {
        node {
          id
        }
      }
      pageInfo {
        endCursor
        hasNextPage
        hasPreviousPage
        startCursor
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "pages": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Page/602767277"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Page/905192165"
          }
        }
      ],
      "pageInfo": {
        "endCursor": "eyJsYXN0X2lkIjo5MDUxOTIxNjUsImxhc3RfdmFsdWUiOiI5MDUxOTIxNjUifQ==",
        "hasNextPage": false,
        "hasPreviousPage": false,
        "startCursor": "eyJsYXN0X2lkIjo2MDI3NjcyNzcsImxhc3RfdmFsdWUiOiI2MDI3NjcyNzcifQ=="
      }
    }
  }
  ```
