---
title: webhookSubscriptionsCount - GraphQL Admin
description: >-
  The count of webhook subscriptions.


  Building an app? If you only use app-specific webhooks, you won't need this.
  App-specific webhook subscriptions specified in your `shopify.app.toml` may be
  easier. They are automatically kept up to date by Shopify & require less
  maintenance. Please read [About managing webhook
  subscriptions](https://shopify.dev/docs/apps/build/webhooks/subscribe).
  Limited to a maximum of 10000 by default.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/webhookSubscriptionsCount
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/webhookSubscriptionsCount.md
---

# webhook​Subscriptions​Count

query

The count of webhook subscriptions.

Building an app? If you only use app-specific webhooks, you won't need this. App-specific webhook subscriptions specified in your `shopify.app.toml` may be easier. They are automatically kept up to date by Shopify & require less maintenance. Please read [About managing webhook subscriptions](https://shopify.dev/docs/apps/build/webhooks/subscribe). Limited to a maximum of 10000 by default.

## Arguments

* limit

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  Default:10000

  The upper bound on count value before returning a result. Use `null` to have no limit.

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * created\_at

    time

  * endpoint

    string

  * * id

      id

    * topic

      string

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * updated\_at

    time

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

* ### Receive a count of all Webhooks

  #### Query

  ```graphql
  query WebhookSubscriptionsCount($query: String!) {
    webhookSubscriptionsCount(query: $query) {
      count
      precision
    }
  }
  ```

  #### Variables

  ```json
  {
    "query": "topic:\"orders/create\""
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query WebhookSubscriptionsCount($query: String!) { webhookSubscriptionsCount(query: $query) { count precision } }",
   "variables": {
      "query": "topic:\"orders/create\""
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
    query WebhookSubscriptionsCount($query: String!) {
      webhookSubscriptionsCount(query: $query) {
        count
        precision
      }
    }`,
    {
      variables: {
          "query": "topic:\"orders/create\""
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
    query WebhookSubscriptionsCount($query: String!) {
      webhookSubscriptionsCount(query: $query) {
        count
        precision
      }
    }
  QUERY

  variables = {
    "query": "topic:\"orders/create\""
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query WebhookSubscriptionsCount($query: String!) {
        webhookSubscriptionsCount(query: $query) {
          count
          precision
        }
      }`,
      "variables": {
          "query": "topic:\"orders/create\""
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query WebhookSubscriptionsCount($query: String!) {
    webhookSubscriptionsCount(query: $query) {
      count
      precision
    }
  }' \
  --variables \
  '{
    "query": "topic:\"orders/create\""
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscriptionsCount": {
      "count": 1,
      "precision": "EXACT"
    }
  }
  ```
