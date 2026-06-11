---
title: nodes - GraphQL Admin
description: >-
  Returns the list of nodes (any objects that implement the

  [Node](https://shopify.dev/api/admin-graphql/latest/interfaces/Node)

  interface) with the given IDs, in accordance with the

  [Relay
  specification](https://relay.dev/docs/guides/graphql-server-specification/#object-identification).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/nodes'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/nodes.md'
---

# nodes

query

Returns the list of nodes (any objects that implement the [Node](https://shopify.dev/api/admin-graphql/latest/interfaces/Node) interface) with the given IDs, in accordance with the [Relay specification](https://relay.dev/docs/guides/graphql-server-specification/#object-identification).

## Arguments

* ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The IDs of the Nodes to return.

***

## Possible returns

* Node

  [\[Node\]!](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Node)

  An object with an ID field to support global identification, in accordance with the [Relay specification](https://relay.dev/graphql/objectidentification.htm#sec-Node-Interface). This interface is used by the [node](https://shopify.dev/api/admin-graphql/unstable/queries/node) and [nodes](https://shopify.dev/api/admin-graphql/unstable/queries/nodes) queries.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

***

## Examples

* ### Retrieve a list of objects using a nodes query

  #### Description

  The following query retrieves a list of objects using their IDs.

  #### Query

  ```graphql
  query {
    nodes(ids: ["gid://shopify/Product/108828309", "gid://shopify/GiftCard/924862292", "gid://shopify/Collection/142458073"]) {
      id
      ... on Product {
        title
      }
      ... on GiftCard {
        balance {
          amount
          currencyCode
        }
      }
      ... on Collection {
        sortOrder
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
  "query": "query { nodes(ids: [\"gid://shopify/Product/108828309\", \"gid://shopify/GiftCard/924862292\", \"gid://shopify/Collection/142458073\"]) { id ... on Product { title } ... on GiftCard { balance { amount currencyCode } } ... on Collection { sortOrder } } }"
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
      nodes(ids: ["gid://shopify/Product/108828309", "gid://shopify/GiftCard/924862292", "gid://shopify/Collection/142458073"]) {
        id
        ... on Product {
          title
        }
        ... on GiftCard {
          balance {
            amount
            currencyCode
          }
        }
        ... on Collection {
          sortOrder
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
      nodes(ids: ["gid://shopify/Product/108828309", "gid://shopify/GiftCard/924862292", "gid://shopify/Collection/142458073"]) {
        id
        ... on Product {
          title
        }
        ... on GiftCard {
          balance {
            amount
            currencyCode
          }
        }
        ... on Collection {
          sortOrder
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
      nodes(ids: ["gid://shopify/Product/108828309", "gid://shopify/GiftCard/924862292", "gid://shopify/Collection/142458073"]) {
        id
        ... on Product {
          title
        }
        ... on GiftCard {
          balance {
            amount
            currencyCode
          }
        }
        ... on Collection {
          sortOrder
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
    nodes(ids: ["gid://shopify/Product/108828309", "gid://shopify/GiftCard/924862292", "gid://shopify/Collection/142458073"]) {
      id
      ... on Product {
        title
      }
      ... on GiftCard {
        balance {
          amount
          currencyCode
        }
      }
      ... on Collection {
        sortOrder
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "nodes": [
      {
        "id": "gid://shopify/Product/108828309",
        "title": "Draft"
      },
      {
        "id": "gid://shopify/GiftCard/924862292",
        "balance": {
          "amount": "75.0",
          "currencyCode": "USD"
        }
      },
      {
        "id": "gid://shopify/Collection/142458073",
        "sortOrder": "MANUAL"
      }
    ]
  }
  ```
