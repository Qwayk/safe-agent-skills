---
title: locations - GraphQL Admin
description: >-
  A paginated list of inventory locations where merchants can stock
  [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)
  items and fulfill
  [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)
  items.


  Returns only active locations by default. Use the
  [`includeInactive`](https://shopify.dev/docs/api/admin-graphql/latest/queries/locations#arguments-includeInactive)
  argument to retrieve deactivated locations that can no longer stock inventory
  or fulfill orders. Use the
  [`includeLegacy`](https://shopify.dev/docs/api/admin-graphql/latest/queries/locations#arguments-includeLegacy)
  argument to include locations that
  [`FulfillmentService`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentService)
  apps manage. Use the
  [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/locations#arguments-query)
  argument to filter by location attributes like name, address, and whether
  local pickup is enabled.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/locations'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/locations.md'
---

# locations

query

A paginated list of inventory locations where merchants can stock [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) items and fulfill [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) items.

Returns only active locations by default. Use the [`includeInactive`](https://shopify.dev/docs/api/admin-graphql/latest/queries/locations#arguments-includeInactive) argument to retrieve deactivated locations that can no longer stock inventory or fulfill orders. Use the [`includeLegacy`](https://shopify.dev/docs/api/admin-graphql/latest/queries/locations#arguments-includeLegacy) argument to include locations that [`FulfillmentService`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentService) apps manage. Use the [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/locations#arguments-query) argument to filter by location attributes like name, address, and whether local pickup is enabled.

## LocationConnection arguments

[LocationConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/LocationConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* include​Inactive

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Whether to include the locations that are deactivated.

* include​Legacy

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Whether to include the legacy locations of fulfillment services.

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * default

      string

    * active

      string

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:
      * `query=Bob Norman`
      * `query=title:green hoodie`

  * address1

    string

  * address2

    string

  * city

    string

  * country

    string

  * created\_at

    time

  * geolocated

    boolean

  * * id

      id

    * legacy

      boolean

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * location\_id

    id

  * name

    string

  * * pickup\_in\_store

      string

    * province

      string

    -
    - Valid values:
      * `enabled`
      * `disabled`

  * zip

    string

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Location​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/LocationSortKeys)

  Default:NAME

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Location​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/LocationEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Location!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)

  non-null

  A list of nodes that are contained in LocationEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve a list of locations

  #### Description

  Retrieves the first 5 locations.

  #### Query

  ```graphql
  query {
    locations(first: 5) {
      edges {
        node {
          id
          name
          address {
            formatted
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
  "query": "query { locations(first: 5) { edges { node { id name address { formatted } } } } }"
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
      locations(first: 5) {
        edges {
          node {
            id
            name
            address {
              formatted
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
      locations(first: 5) {
        edges {
          node {
            id
            name
            address {
              formatted
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
      locations(first: 5) {
        edges {
          node {
            id
            name
            address {
              formatted
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
    locations(first: 5) {
      edges {
        node {
          id
          name
          address {
            formatted
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "locations": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Location/346779380",
            "name": "Ottawa Store",
            "address": {
              "formatted": [
                "126 york street",
                "second and third floor",
                "ottawa ON k1n5t5",
                "Canada"
              ]
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/Location/648019273",
            "name": "Ottawa Store geo located",
            "address": {
              "formatted": [
                "126 york street",
                "second and third floor",
                "ottawa ON k1n5t5",
                "Canada"
              ]
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/Location/884687543",
            "name": "Ottawa Warehouse",
            "address": {
              "formatted": [
                "Canada"
              ]
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/Location/124656943",
            "name": "Shipping Origin",
            "address": {
              "formatted": [
                "190 MacLaren Street",
                "Ottawa ON K2P 0L6",
                "Canada"
              ]
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/Location/750123840",
            "name": "Toronto Store",
            "address": {
              "formatted": [
                "620 King St. W",
                "toronto ON m5v1m5",
                "Canada"
              ]
            }
          }
        }
      ]
    }
  }
  ```
