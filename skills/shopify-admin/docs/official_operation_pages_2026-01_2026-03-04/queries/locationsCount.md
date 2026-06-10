---
title: locationsCount - GraphQL Admin
description: >-
  Returns the count of locations for the given shop. Limited to a maximum of
  10000 by default.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/locationsCount'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/locationsCount.md'
---

# locations​Count

query

Returns the count of locations for the given shop. Limited to a maximum of 10000 by default.

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

* ### Retrieve a count of locations

  #### Description

  Count the number of locations in a shop

  #### Query

  ```graphql
  query {
    locationsCount {
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
  "query": "query { locationsCount { count } }"
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
      locationsCount {
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
      locationsCount {
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
      locationsCount {
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
    locationsCount {
      count
    }
  }'
  ```

  #### Response

  ```json
  {
    "locationsCount": {
      "count": 10
    }
  }
  ```
