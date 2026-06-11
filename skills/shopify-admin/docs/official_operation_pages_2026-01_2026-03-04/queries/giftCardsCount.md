---
title: giftCardsCount - GraphQL Admin
description: >-
  The total number of gift cards issued for the shop. Limited to a maximum of
  10000 by default.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/giftCardsCount'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/giftCardsCount.md'
---

# gift​Cards​Count

query

Requires `read_gift_cards` access scope.

The total number of gift cards issued for the shop. Limited to a maximum of 10000 by default.

## Arguments

* limit

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  Default:10000

  The upper bound on count value before returning a result. Use `null` to have no limit.

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

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of an existing saved search. The search’s query string is used as the query argument. Refer to the [`SavedSearch`](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch) object.

***

## Possible returns

* Count

  [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

  A numeric count with precision information indicating whether the count is exact or an estimate.

  * count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The count of elements.

  * precision

    [Count​Precision!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CountPrecision)

    non-null

    The count's precision, or the exactness of the value.

***

## Examples

* ### Get the total number of enabled gift cards that are issued for the shop

  #### Description

  The following query retrieves a count for the total number of enabled gift cards that are issued for the shop.

  #### Query

  ```graphql
  query {
    giftCardsCount(query: "status:enabled") {
      count
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
  "query": "query { giftCardsCount(query: \"status:enabled\") { count } }"
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
      giftCardsCount(query: "status:enabled") {
        count
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
      giftCardsCount(query: "status:enabled") {
        count
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
      giftCardsCount(query: "status:enabled") {
        count
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    giftCardsCount(query: "status:enabled") {
      count
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCardsCount": {
      "count": 10
    }
  }
  ```

* ### Retrieves a count of gift cards

  #### Description

  The following query retrieves a count for the total number of all gift cards that are issued for the shop.

  #### Query

  ```graphql
  query {
    giftCardsCount {
      count
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
  "query": "query { giftCardsCount { count } }"
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
      giftCardsCount {
        count
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
      giftCardsCount {
        count
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
      giftCardsCount {
        count
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    giftCardsCount {
      count
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCardsCount": {
      "count": 11
    }
  }
  ```
