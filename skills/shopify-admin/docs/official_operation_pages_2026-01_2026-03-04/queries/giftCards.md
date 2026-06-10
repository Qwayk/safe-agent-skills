---
title: giftCards - GraphQL Admin
description: >-
  Returns a paginated list of
  [`GiftCard`](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCard)
  objects issued for the shop.


  You can filter gift cards by attributes such as status, last characters of the
  code, balance status, and other values using the
  [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/giftCards#arguments-query)
  parameter. You can also apply
  [`SavedSearch`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SavedSearch)
  objects to filter results.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/giftCards'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/giftCards.md'
---

# gift​Cards

query

Requires `read_gift_cards` access scope.

Returns a paginated list of [`GiftCard`](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCard) objects issued for the shop.

You can filter gift cards by attributes such as status, last characters of the code, balance status, and other values using the [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/giftCards#arguments-query) parameter. You can also apply [`SavedSearch`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SavedSearch) objects to filter results.

## GiftCardConnection arguments

[GiftCardConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/GiftCardConnection)

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

    * balance\_status

      string

    * created\_at

      time

    * expires\_on

      date

    * id

      id

    * initial\_value

      string

    * source

      string

    * status

      string

    - Filter by a case-insensitive search of multiple fields in a document, including gift card codes.

    - Example:
      * `query=a5bh6h64b329j4k7`
      * `query=Bob Norman`

    - Valid values:
      * `full`
      * `partial`
      * `empty`
      * `full_or_partial`
      Example:
      * `balance_status:full`

    - Example:
      * `created_at:>=2020-01-01T12:00:00Z`

    - Example:

      * `expires_on:>=2020-01-01`

      Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

    - Example:
      * `initial_value:>=100`

    - Valid values:
      * `manual`
      * `purchased`
      * `api_client`
      Example:
      * `source:manual`
      Valid values:
      * `disabled`
      * `enabled`
      * `expired`
      * `expiring`
      Example:
      * `status:disabled OR status:expired`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

* sort​Key

  [Gift​Card​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/GiftCardSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Gift​Card​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCardEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Gift​Card!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCard)

  non-null

  A list of nodes that are contained in GiftCardEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Get the first 5 enabled gift cards

  #### Description

  The following query retrieves the first five enabled gift cards for a shop, and returns the ID and enabled status of each gift card.

  #### Query

  ```graphql
  query {
    giftCards(first: 5, query: "status:enabled") {
      edges {
        node {
          id
          enabled
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
  "query": "query { giftCards(first: 5, query: \"status:enabled\") { edges { node { id enabled } } } }"
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
      giftCards(first: 5, query: "status:enabled") {
        edges {
          node {
            id
            enabled
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
      giftCards(first: 5, query: "status:enabled") {
        edges {
          node {
            id
            enabled
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
      giftCards(first: 5, query: "status:enabled") {
        edges {
          node {
            id
            enabled
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
    giftCards(first: 5, query: "status:enabled") {
      edges {
        node {
          id
          enabled
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCards": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/GiftCard/63396415",
            "enabled": true
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/292935194",
            "enabled": true
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/411106674",
            "enabled": true
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/566141102",
            "enabled": true
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/636946744",
            "enabled": true
          }
        }
      ]
    }
  }
  ```

* ### Get up to 5 gift cards with the last characters "1234"

  #### Description

  The following query retrieves up to five gift cards with the last characters "1234" for a shop, and returns the ID and last characters of each gift card.

  #### Query

  ```graphql
  query {
    giftCards(first: 5, query: "1234") {
      edges {
        node {
          id
          lastCharacters
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
  "query": "query { giftCards(first: 5, query: \"1234\") { edges { node { id lastCharacters } } } }"
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
      giftCards(first: 5, query: "1234") {
        edges {
          node {
            id
            lastCharacters
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
      giftCards(first: 5, query: "1234") {
        edges {
          node {
            id
            lastCharacters
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
      giftCards(first: 5, query: "1234") {
        edges {
          node {
            id
            lastCharacters
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
    giftCards(first: 5, query: "1234") {
      edges {
        node {
          id
          lastCharacters
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCards": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/GiftCard/411106674",
            "lastCharacters": "1234"
          }
        }
      ]
    }
  }
  ```

* ### Retrieves a list of gift cards

  #### Description

  The following query retrieves the first ten gift cards for a shop, and returns the ID of each gift card.

  #### Query

  ```graphql
  query {
    giftCards(first: 10) {
      edges {
        node {
          id
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
  "query": "query { giftCards(first: 10) { edges { node { id } } } }"
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
      giftCards(first: 10) {
        edges {
          node {
            id
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
      giftCards(first: 10) {
        edges {
          node {
            id
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
      giftCards(first: 10) {
        edges {
          node {
            id
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
    giftCards(first: 10) {
      edges {
        node {
          id
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCards": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/GiftCard/63396415"
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/83783397"
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/292935194"
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/411106674"
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/566141102"
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/636946744"
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/638517611"
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/665558842"
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/746346263"
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/842921201"
          }
        }
      ]
    }
  }
  ```

* ### Searches for gift cards

  #### Query

  ```graphql
  query GiftCardList($first: Int, $query: String) {
    giftCards(first: $first, query: $query) {
      edges {
        node {
          id
          balance {
            amount
            currencyCode
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "first": 5,
    "query": "status:enabled"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query GiftCardList($first: Int, $query: String) { giftCards(first: $first, query: $query) { edges { node { id balance { amount currencyCode } } } } }",
   "variables": {
      "first": 5,
      "query": "status:enabled"
    }
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query GiftCardList($first: Int, $query: String) {
      giftCards(first: $first, query: $query) {
        edges {
          node {
            id
            balance {
              amount
              currencyCode
            }
          }
        }
      }
    }`,
    {
      variables: {
          "first": 5,
          "query": "status:enabled"
      },
    },
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
    query GiftCardList($first: Int, $query: String) {
      giftCards(first: $first, query: $query) {
        edges {
          node {
            id
            balance {
              amount
              currencyCode
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "first": 5,
    "query": "status:enabled"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query GiftCardList($first: Int, $query: String) {
        giftCards(first: $first, query: $query) {
          edges {
            node {
              id
              balance {
                amount
                currencyCode
              }
            }
          }
        }
      }`,
      "variables": {
          "first": 5,
          "query": "status:enabled"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query GiftCardList($first: Int, $query: String) {
    giftCards(first: $first, query: $query) {
      edges {
        node {
          id
          balance {
            amount
            currencyCode
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "first": 5,
    "query": "status:enabled"
  }'
  ```

  #### Response

  ```json
  {
    "giftCards": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/GiftCard/63396415",
            "balance": {
              "amount": "10.0",
              "currencyCode": "USD"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/292935194",
            "balance": {
              "amount": "75.0",
              "currencyCode": "EUR"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/411106674",
            "balance": {
              "amount": "25.0",
              "currencyCode": "USD"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/566141102",
            "balance": {
              "amount": "0.23",
              "currencyCode": "USD"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/GiftCard/636946744",
            "balance": {
              "amount": "75.0",
              "currencyCode": "USD"
            }
          }
        }
      ]
    }
  }
  ```
