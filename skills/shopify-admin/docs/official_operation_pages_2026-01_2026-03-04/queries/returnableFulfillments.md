---
title: returnableFulfillments - GraphQL Admin
description: List of returnable fulfillments.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/returnableFulfillments
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/returnableFulfillments.md
---

# returnable​Fulfillments

query

List of returnable fulfillments.

## ReturnableFulfillmentConnection arguments

[ReturnableFulfillmentConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ReturnableFulfillmentConnection)

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

* order​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Order ID that will scope all returnable fulfillments.

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Returnable​Fulfillment​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnableFulfillmentEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Returnable​Fulfillment!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnableFulfillment)

  non-null

  A list of nodes that are contained in ReturnableFulfillmentEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Get fulfillment information for returnable fulfillments

  #### Description

  The following query shows how to retrieve the \`id\`, \`status\`, and \`location\` from the first 5 returnable fulfillments of an order.

  #### Query

  ```graphql
  query {
    returnableFulfillments(orderId: "gid://shopify/Order/215577410", first: 5) {
      edges {
        node {
          id
          fulfillment {
            id
            displayStatus
            location {
              address {
                address1
              }
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
  "query": "query { returnableFulfillments(orderId: \"gid://shopify/Order/215577410\", first: 5) { edges { node { id fulfillment { id displayStatus location { address { address1 } } } } } } }"
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
      returnableFulfillments(orderId: "gid://shopify/Order/215577410", first: 5) {
        edges {
          node {
            id
            fulfillment {
              id
              displayStatus
              location {
                address {
                  address1
                }
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
      returnableFulfillments(orderId: "gid://shopify/Order/215577410", first: 5) {
        edges {
          node {
            id
            fulfillment {
              id
              displayStatus
              location {
                address {
                  address1
                }
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
      returnableFulfillments(orderId: "gid://shopify/Order/215577410", first: 5) {
        edges {
          node {
            id
            fulfillment {
              id
              displayStatus
              location {
                address {
                  address1
                }
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
    returnableFulfillments(orderId: "gid://shopify/Order/215577410", first: 5) {
      edges {
        node {
          id
          fulfillment {
            id
            displayStatus
            location {
              address {
                address1
              }
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
    "returnableFulfillments": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/ReturnableFulfillment/607470790",
            "fulfillment": {
              "id": "gid://shopify/Fulfillment/607470790",
              "displayStatus": "MARKED_AS_FULFILLED",
              "location": {
                "address": {
                  "address1": "126 york street"
                }
              }
            }
          }
        }
      ]
    }
  }
  ```
