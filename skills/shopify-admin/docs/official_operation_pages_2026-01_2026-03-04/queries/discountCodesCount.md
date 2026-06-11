---
title: discountCodesCount - GraphQL Admin
description: >-
  The total number of discount codes for the shop. Limited to a maximum of 10000
  by default.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/discountCodesCount'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/discountCodesCount.md
---

# discount​Codes​Count

query

Requires `read_discounts` access scope.

The total number of discount codes for the shop. Limited to a maximum of 10000 by default.

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

    * id

      id

    * times\_used

      integer

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

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

* ### Retrieve the number of discount codes used more than once

  #### Description

  Returns the number of discount codes that were used more than once.

  #### Query

  ```graphql
  query discountCodesCount($query: String!) {
    discountCodesCount(query: $query) {
      count
    }
  }
  ```

  #### Variables

  ```json
  {
    "query": "times_used:>1"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query discountCodesCount($query: String!) { discountCodesCount(query: $query) { count } }",
   "variables": {
      "query": "times_used:>1"
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
    query discountCodesCount($query: String!) {
      discountCodesCount(query: $query) {
        count
      }
    }`,
    {
      variables: {
          "query": "times_used:>1"
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
    query discountCodesCount($query: String!) {
      discountCodesCount(query: $query) {
        count
      }
    }
  QUERY

  variables = {
    "query": "times_used:>1"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query discountCodesCount($query: String!) {
        discountCodesCount(query: $query) {
          count
        }
      }`,
      "variables": {
          "query": "times_used:>1"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query discountCodesCount($query: String!) {
    discountCodesCount(query: $query) {
      count
    }
  }' \
  --variables \
  '{
    "query": "times_used:>1"
  }'
  ```

  #### Response

  ```json
  {
    "discountCodesCount": {
      "count": 3
    }
  }
  ```

* ### Retrieve the number of discount codes used within a range

  #### Description

  Returns the number of discount codes that were used more than onceand less than four times.

  #### Query

  ```graphql
  query discountCodesCount($query: String!) {
    discountCodesCount(query: $query) {
      count
    }
  }
  ```

  #### Variables

  ```json
  {
    "query": "times_used:>1 AND times_used:<4"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query discountCodesCount($query: String!) { discountCodesCount(query: $query) { count } }",
   "variables": {
      "query": "times_used:>1 AND times_used:<4"
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
    query discountCodesCount($query: String!) {
      discountCodesCount(query: $query) {
        count
      }
    }`,
    {
      variables: {
          "query": "times_used:>1 AND times_used:<4"
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
    query discountCodesCount($query: String!) {
      discountCodesCount(query: $query) {
        count
      }
    }
  QUERY

  variables = {
    "query": "times_used:>1 AND times_used:<4"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query discountCodesCount($query: String!) {
        discountCodesCount(query: $query) {
          count
        }
      }`,
      "variables": {
          "query": "times_used:>1 AND times_used:<4"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query discountCodesCount($query: String!) {
    discountCodesCount(query: $query) {
      count
    }
  }' \
  --variables \
  '{
    "query": "times_used:>1 AND times_used:<4"
  }'
  ```

  #### Response

  ```json
  {
    "discountCodesCount": {
      "count": 2
    }
  }
  ```

* ### Retrieve the number of unused discount codes

  #### Description

  Returns the number of discount codes that were never used.

  #### Query

  ```graphql
  query discountCodesCount($query: String!) {
    discountCodesCount(query: $query) {
      count
    }
  }
  ```

  #### Variables

  ```json
  {
    "query": "times_used:0"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query discountCodesCount($query: String!) { discountCodesCount(query: $query) { count } }",
   "variables": {
      "query": "times_used:0"
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
    query discountCodesCount($query: String!) {
      discountCodesCount(query: $query) {
        count
      }
    }`,
    {
      variables: {
          "query": "times_used:0"
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
    query discountCodesCount($query: String!) {
      discountCodesCount(query: $query) {
        count
      }
    }
  QUERY

  variables = {
    "query": "times_used:0"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query discountCodesCount($query: String!) {
        discountCodesCount(query: $query) {
          count
        }
      }`,
      "variables": {
          "query": "times_used:0"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query discountCodesCount($query: String!) {
    discountCodesCount(query: $query) {
      count
    }
  }' \
  --variables \
  '{
    "query": "times_used:0"
  }'
  ```

  #### Response

  ```json
  {
    "discountCodesCount": {
      "count": 25
    }
  }
  ```

* ### Retrieve the total number of discount codes

  #### Description

  Returns the total number of discount codes.

  #### Query

  ```graphql
  query discountCodesCount {
    discountCodesCount {
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
  "query": "query discountCodesCount { discountCodesCount { count } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query discountCodesCount {
      discountCodesCount {
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
    query discountCodesCount {
      discountCodesCount {
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
    data: `query discountCodesCount {
      discountCodesCount {
        count
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query discountCodesCount {
    discountCodesCount {
      count
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodesCount": {
      "count": 29
    }
  }
  ```

* ### Retrieves a count of discount codes for a shop

  #### Query

  ```graphql
  query DiscountRedeemCodeCount {
    discountCodesCount {
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
  "query": "query DiscountRedeemCodeCount { discountCodesCount { count } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query DiscountRedeemCodeCount {
      discountCodesCount {
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
    query DiscountRedeemCodeCount {
      discountCodesCount {
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
    data: `query DiscountRedeemCodeCount {
      discountCodesCount {
        count
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query DiscountRedeemCodeCount {
    discountCodesCount {
      count
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodesCount": {
      "count": 29
    }
  }
  ```
