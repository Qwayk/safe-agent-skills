---
title: carrierServices - GraphQL Admin
description: >-
  A paginated list of carrier services configured for the shop. Carrier services
  provide real-time shipping rates from external providers like FedEx, UPS, or
  custom shipping solutions. Use the `query` parameter to filter results by
  attributes such as active status.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/carrierServices'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/carrierServices.md'
---

# carrier​Services

query

Requires `read_shipping` access scope.

A paginated list of carrier services configured for the shop. Carrier services provide real-time shipping rates from external providers like FedEx, UPS, or custom shipping solutions. Use the `query` parameter to filter results by attributes such as active status.

## DeliveryCarrierServiceConnection arguments

[DeliveryCarrierServiceConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/DeliveryCarrierServiceConnection)

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

  * active

    boolean

  * id

    id

    Filter by `id` range.

    Example:

    * `id:1234`
    * `id:>=1234`
    * `id:<=1234`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Carrier​Service​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/CarrierServiceSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Delivery​Carrier​Service​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryCarrierServiceEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Delivery​Carrier​Service!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryCarrierService)

  non-null

  A list of nodes that are contained in DeliveryCarrierServiceEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve a list of CarrierServices

  #### Query

  ```graphql
  query CarrierServiceList {
    carrierServices(first: 10, query: "active:true") {
      edges {
        node {
          id
          name
          callbackUrl
          active
          supportsServiceDiscovery
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
  "query": "query CarrierServiceList { carrierServices(first: 10, query: \"active:true\") { edges { node { id name callbackUrl active supportsServiceDiscovery } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query CarrierServiceList {
      carrierServices(first: 10, query: "active:true") {
        edges {
          node {
            id
            name
            callbackUrl
            active
            supportsServiceDiscovery
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
    query CarrierServiceList {
      carrierServices(first: 10, query: "active:true") {
        edges {
          node {
            id
            name
            callbackUrl
            active
            supportsServiceDiscovery
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
    data: `query CarrierServiceList {
      carrierServices(first: 10, query: "active:true") {
        edges {
          node {
            id
            name
            callbackUrl
            active
            supportsServiceDiscovery
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
  'query CarrierServiceList {
    carrierServices(first: 10, query: "active:true") {
      edges {
        node {
          id
          name
          callbackUrl
          active
          supportsServiceDiscovery
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "carrierServices": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/DeliveryCarrierService/1036895101",
            "name": "test name",
            "callbackUrl": null,
            "active": true,
            "supportsServiceDiscovery": false
          }
        }
      ]
    }
  }
  ```
