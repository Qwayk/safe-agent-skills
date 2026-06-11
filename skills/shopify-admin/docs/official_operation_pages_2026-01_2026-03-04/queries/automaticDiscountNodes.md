---
title: automaticDiscountNodes - GraphQL Admin
description: >-
  Returns a list of [automatic
  discounts](https://help.shopify.com/manual/discounts/discount-types#automatic-discounts).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/automaticDiscountNodes
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/automaticDiscountNodes.md
---

# automatic​Discount​Nodes

query

Requires Apps must have `read_discounts` access scope.

Deprecated. Use [discountNodes](https://shopify.dev/docs/api/admin-graphql/latest/queries/discountNodes) instead.

Returns a list of [automatic discounts](https://help.shopify.com/manual/discounts/discount-types#automatic-discounts).

## DiscountAutomaticNodeConnection arguments

[DiscountAutomaticNodeConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/DiscountAutomaticNodeConnection)

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

    * status

      string

    * type

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

      Filter by the discount status.

    - Valid values:

      * `active`
      * `expired`
      * `scheduled`

      Example:

      * `status:scheduled`

      Filter by the [discount type](https://help.shopify.com/manual/discounts/discount-types).

      Valid values:

      * `all`
      * `all_with_app`
      * `app`
      * `bxgy`
      * `fixed_amount`
      * `percentage`

      Example:

      * `type:bxgy`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

* sort​Key

  [Automatic​Discount​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/AutomaticDiscountSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Discount​Automatic​Node​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomaticNodeEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Discount​Automatic​Node!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomaticNode)

  non-null

  A list of nodes that are contained in DiscountAutomaticNodeEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Query a list of automatic discounts

  #### Description

  Retrieve \[automatic discounts]\(https://help.shopify.com/manual/discounts/discount-types#automatic-discounts) that are applied on a cart and at checkout when an order meets specific criteria.

  #### Query

  ```graphql
  query {
    automaticDiscountNodes(first: 2) {
      edges {
        node {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
              title
              status
            }
            ... on DiscountAutomaticBxgy {
              title
              status
            }
          }
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
  "query": "query { automaticDiscountNodes(first: 2) { edges { node { id automaticDiscount { ... on DiscountAutomaticBasic { title status } ... on DiscountAutomaticBxgy { title status } } } } } }"
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
      automaticDiscountNodes(first: 2) {
        edges {
          node {
            id
            automaticDiscount {
              ... on DiscountAutomaticBasic {
                title
                status
              }
              ... on DiscountAutomaticBxgy {
                title
                status
              }
            }
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
      automaticDiscountNodes(first: 2) {
        edges {
          node {
            id
            automaticDiscount {
              ... on DiscountAutomaticBasic {
                title
                status
              }
              ... on DiscountAutomaticBxgy {
                title
                status
              }
            }
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
      automaticDiscountNodes(first: 2) {
        edges {
          node {
            id
            automaticDiscount {
              ... on DiscountAutomaticBasic {
                title
                status
              }
              ... on DiscountAutomaticBxgy {
                title
                status
              }
            }
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
    automaticDiscountNodes(first: 2) {
      edges {
        node {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
              title
              status
            }
            ... on DiscountAutomaticBxgy {
              title
              status
            }
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "automaticDiscountNodes": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/DiscountAutomaticNode/1057371287",
            "automaticDiscount": {
              "title": "Automatic BXGY",
              "status": "ACTIVE"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/DiscountAutomaticNode/1057371288",
            "automaticDiscount": {
              "title": "Basic Discount",
              "status": "ACTIVE"
            }
          }
        }
      ]
    }
  }
  ```

* ### Query automatic discounts with pagination and filtering

  #### Description

  This example shows how to query automatic discounts with pagination and status filtering. The query returns the first active discount and includes a cursor for pagination.

  #### Query

  ```graphql
  query {
    automaticDiscountNodes(first: 1, query: "status:active") {
      nodes {
        id
        automaticDiscount {
          ... on DiscountAutomaticBxgy {
            title
            status
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
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
  "query": "query { automaticDiscountNodes(first: 1, query: \"status:active\") { nodes { id automaticDiscount { ... on DiscountAutomaticBxgy { title status } } } pageInfo { hasNextPage endCursor } } }"
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
      automaticDiscountNodes(first: 1, query: "status:active") {
        nodes {
          id
          automaticDiscount {
            ... on DiscountAutomaticBxgy {
              title
              status
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
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
      automaticDiscountNodes(first: 1, query: "status:active") {
        nodes {
          id
          automaticDiscount {
            ... on DiscountAutomaticBxgy {
              title
              status
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
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
      automaticDiscountNodes(first: 1, query: "status:active") {
        nodes {
          id
          automaticDiscount {
            ... on DiscountAutomaticBxgy {
              title
              status
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
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
    automaticDiscountNodes(first: 1, query: "status:active") {
      nodes {
        id
        automaticDiscount {
          ... on DiscountAutomaticBxgy {
            title
            status
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "automaticDiscountNodes": {
      "nodes": [
        {
          "id": "gid://shopify/DiscountAutomaticNode/1057371286",
          "automaticDiscount": {
            "title": "Active BXGY",
            "status": "ACTIVE"
          }
        }
      ],
      "pageInfo": {
        "hasNextPage": false,
        "endCursor": "eyJsYXN0X2lkIjoxMDU3MzcxMjg2LCJsYXN0X3ZhbHVlIjoiMTA1NzM3MTI4NiJ9"
      }
    }
  }
  ```
