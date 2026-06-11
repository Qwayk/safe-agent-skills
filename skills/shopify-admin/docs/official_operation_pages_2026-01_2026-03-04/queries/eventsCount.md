---
title: eventsCount - GraphQL Admin
description: Count of events. Limited to a maximum of 10000.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/eventsCount'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/eventsCount.md'
---

# events​Count

query

Count of events. Limited to a maximum of 10000.

## Arguments

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * action

      string

    * comments

      boolean

    * created\_at

      time

    * id

      id

    * subject\_type

      string

    - The action that occured.

    - Example:

      * `action:create`

      Whether or not to include [comment-events](https://shopify.dev/api/admin-graphql/latest/objects/CommentEvent) in your search, passing `false` will exclude comment-events, any other value will include comment-events.

    - Example:

      * `false`
      * `true`

      Filter by the date and time when the event occurred. Event data is retained for 1 year.

    - Example:

      * `created_at:>2025-10-21`
      * `created_at:<now`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      The resource type affected by this event. See [EventSubjectType](https://shopify.dev/api/admin-graphql/latest/enums/EventSubjectType) for possible values.

      Example:

      * `PRODUCT_VARIANT`
      * `PRODUCT`
      * `COLLECTION`

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

* ### Retrieve the amount of events after a given time

  #### Description

  Retrieve the amount of events that happened after the 1st of January 2024.

  #### Query

  ```graphql
  query {
    eventsCount(query: "created_at:>=2024-01-01") {
      count
      precision
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
  "query": "query { eventsCount(query: \"created_at:>=2024-01-01\") { count precision } }"
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
      eventsCount(query: "created_at:>=2024-01-01") {
        count
        precision
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
      eventsCount(query: "created_at:>=2024-01-01") {
        count
        precision
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
      eventsCount(query: "created_at:>=2024-01-01") {
        count
        precision
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    eventsCount(query: "created_at:>=2024-01-01") {
      count
      precision
    }
  }'
  ```

  #### Response

  ```json
  {
    "eventsCount": {
      "count": 28,
      "precision": "EXACT"
    }
  }
  ```

* ### Retrieve the amount of product events, including comment events

  #### Description

  Retrieve the amount of product events, including comment events.

  #### Query

  ```graphql
  query {
    eventsCount(query: "comments:1 AND subject_type:'PRODUCT'") {
      count
      precision
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
  "query": "query { eventsCount(query: \"comments:1 AND subject_type:'\''PRODUCT'\''\") { count precision } }"
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
      eventsCount(query: "comments:1 AND subject_type:'PRODUCT'") {
        count
        precision
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
      eventsCount(query: "comments:1 AND subject_type:'PRODUCT'") {
        count
        precision
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
      eventsCount(query: "comments:1 AND subject_type:'PRODUCT'") {
        count
        precision
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    eventsCount(query: "comments:1 AND subject_type:'PRODUCT'") {
      count
      precision
    }
  }'
  ```

  #### Response

  ```json
  {
    "eventsCount": {
      "count": 7,
      "precision": "EXACT"
    }
  }
  ```

* ### Retrieves a count of events

  #### Query

  ```graphql
  query EventCount {
    eventsCount {
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
  "query": "query EventCount { eventsCount { count } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query EventCount {
      eventsCount {
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
    query EventCount {
      eventsCount {
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
    data: `query EventCount {
      eventsCount {
        count
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query EventCount {
    eventsCount {
      count
    }
  }'
  ```

  #### Response

  ```json
  {
    "eventsCount": {
      "count": 166
    }
  }
  ```
