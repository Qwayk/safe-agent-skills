---
title: publications - GraphQL Admin
description: >-
  Returns a paginated list of
  [`Publication`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication).


  Filter publications by
  [`CatalogType`](https://shopify.dev/docs/api/admin-graphql/latest/enums/CatalogType).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/publications'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/publications.md'
---

# publications

query

Requires `read_publications` access scope.

Returns a paginated list of [`Publication`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication).

Filter publications by [`CatalogType`](https://shopify.dev/docs/api/admin-graphql/latest/enums/CatalogType).

## PublicationConnection arguments

[PublicationConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/PublicationConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* catalog​Type

  [Catalog​Type](https://shopify.dev/docs/api/admin-graphql/latest/enums/CatalogType)

  Filter publications by catalog type.

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Publication​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PublicationEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Publication!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication)

  non-null

  A list of nodes that are contained in PublicationEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### List the first three publications

  #### Query

  ```graphql
  query publications {
    publications(first: 3) {
      edges {
        node {
          id
          autoPublish
          supportsFuturePublishing
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
  "query": "query publications { publications(first: 3) { edges { node { id autoPublish supportsFuturePublishing } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query publications {
      publications(first: 3) {
        edges {
          node {
            id
            autoPublish
            supportsFuturePublishing
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
    query publications {
      publications(first: 3) {
        edges {
          node {
            id
            autoPublish
            supportsFuturePublishing
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
    data: `query publications {
      publications(first: 3) {
        edges {
          node {
            id
            autoPublish
            supportsFuturePublishing
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
  'query publications {
    publications(first: 3) {
      edges {
        node {
          id
          autoPublish
          supportsFuturePublishing
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "publications": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Publication/224761294",
            "autoPublish": false,
            "supportsFuturePublishing": false
          }
        },
        {
          "node": {
            "id": "gid://shopify/Publication/244171671",
            "autoPublish": false,
            "supportsFuturePublishing": true
          }
        },
        {
          "node": {
            "id": "gid://shopify/Publication/347532733",
            "autoPublish": false,
            "supportsFuturePublishing": false
          }
        }
      ]
    }
  }
  ```
