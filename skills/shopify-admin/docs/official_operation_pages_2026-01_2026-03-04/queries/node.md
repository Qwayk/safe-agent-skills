---
title: node - GraphQL Admin
description: >-
  Returns a specific node (any object that implements the

  [Node](https://shopify.dev/api/admin-graphql/latest/interfaces/Node)

  interface) by ID, in accordance with the

  [Relay
  specification](https://relay.dev/docs/guides/graphql-server-specification/#object-identification).

  This field is commonly used for refetching an object.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/node'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/node.md'
---

# node

query

Returns a specific node (any object that implements the [Node](https://shopify.dev/api/admin-graphql/latest/interfaces/Node) interface) by ID, in accordance with the [Relay specification](https://relay.dev/docs/guides/graphql-server-specification/#object-identification). This field is commonly used for refetching an object.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `Node` to return.

***

## Possible returns

* Node

  [Node](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Node)

  An object with an ID field to support global identification, in accordance with the [Relay specification](https://relay.dev/graphql/objectidentification.htm#sec-Node-Interface). This interface is used by the [node](https://shopify.dev/api/admin-graphql/unstable/queries/node) and [nodes](https://shopify.dev/api/admin-graphql/unstable/queries/nodes) queries.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

***

## Examples

* ### Retrieve a product using a node query

  #### Description

  The following query retrieves a product using its ID.

  #### Query

  ```graphql
  query {
    node(id: "gid://shopify/Product/108828309") {
      id
      ... on Product {
        title
        handle
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
  "query": "query { node(id: \"gid://shopify/Product/108828309\") { id ... on Product { title handle } } }"
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
      node(id: "gid://shopify/Product/108828309") {
        id
        ... on Product {
          title
          handle
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
      node(id: "gid://shopify/Product/108828309") {
        id
        ... on Product {
          title
          handle
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
      node(id: "gid://shopify/Product/108828309") {
        id
        ... on Product {
          title
          handle
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
    node(id: "gid://shopify/Product/108828309") {
      id
      ... on Product {
        title
        handle
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "node": {
      "id": "gid://shopify/Product/108828309",
      "title": "Draft",
      "handle": "draft"
    }
  }
  ```
