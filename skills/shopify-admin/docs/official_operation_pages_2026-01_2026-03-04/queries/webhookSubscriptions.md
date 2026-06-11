---
title: webhookSubscriptions - GraphQL Admin
description: >-
  Retrieves a paginated list of webhook subscriptions created using the API for
  the current app and shop.


  > Note: Returns only shop-scoped subscriptions, not app-scoped subscriptions
  configured in TOML files.


  Subscription details include event topics, endpoint URIs, filtering rules,
  field inclusion settings, and metafield namespace permissions. Results support
  cursor-based pagination that you can filter by topic, format, or custom search
  criteria.



  Building an app? If you only use app-specific webhooks, you won't need this.
  App-specific webhook subscriptions specified in your `shopify.app.toml` may be
  easier. They are automatically kept up to date by Shopify & require less
  maintenance. Please read [About managing webhook
  subscriptions](https://shopify.dev/docs/apps/build/webhooks/subscribe).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/webhookSubscriptions
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/webhookSubscriptions.md
---

# webhook​Subscriptions

query

Retrieves a paginated list of webhook subscriptions created using the API for the current app and shop.

***

**Note:** Returns only shop-scoped subscriptions, not app-scoped subscriptions configured in TOML files.

***

Subscription details include event topics, endpoint URIs, filtering rules, field inclusion settings, and metafield namespace permissions. Results support cursor-based pagination that you can filter by topic, format, or custom search criteria.

Building an app? If you only use app-specific webhooks, you won't need this. App-specific webhook subscriptions specified in your `shopify.app.toml` may be easier. They are automatically kept up to date by Shopify & require less maintenance. Please read [About managing webhook subscriptions](https://shopify.dev/docs/apps/build/webhooks/subscribe).

## WebhookSubscriptionConnection arguments

[WebhookSubscriptionConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/WebhookSubscriptionConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* format

  [Webhook​Subscription​Format](https://shopify.dev/docs/api/admin-graphql/latest/enums/WebhookSubscriptionFormat)

  Response format to filter by.

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * created\_at

    time

  * * id

      id

    * updated\_at

      time

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Webhook​Subscription​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/WebhookSubscriptionSortKeys)

  Default:CREATED\_AT

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

* topics

  [\[Webhook​Subscription​Topic!\]](https://shopify.dev/docs/api/admin-graphql/latest/enums/WebhookSubscriptionTopic)

  List of webhook subscription topics to filter by.

* uri

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  URI to filter by. Supports an HTTPS URL, a Google Pub/Sub URI (pubsub://{project-id}:{topic-id}) or an Amazon EventBridge event source ARN.

* callback​Url

  [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

  Deprecated

***

## Possible returns

* edges

  [\[Webhook​Subscription​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebhookSubscriptionEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Webhook​Subscription!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebhookSubscription)

  non-null

  A list of nodes that are contained in WebhookSubscriptionEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Get the IDs, topics and URIs of the first 2 webhook subscriptions

  #### Query

  ```graphql
  query {
    webhookSubscriptions(first: 2) {
      edges {
        node {
          id
          topic
          uri
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
  "query": "query { webhookSubscriptions(first: 2) { edges { node { id topic uri } } } }"
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
      webhookSubscriptions(first: 2) {
        edges {
          node {
            id
            topic
            uri
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
      webhookSubscriptions(first: 2) {
        edges {
          node {
            id
            topic
            uri
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
      webhookSubscriptions(first: 2) {
        edges {
          node {
            id
            topic
            uri
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
    webhookSubscriptions(first: 2) {
      edges {
        node {
          id
          topic
          uri
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscriptions": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/WebhookSubscription/892403750",
            "topic": "ORDERS_CANCELLED",
            "uri": "https://example.org/fully_loaded_1"
          }
        },
        {
          "node": {
            "id": "gid://shopify/WebhookSubscription/901431826",
            "topic": "APP_UNINSTALLED",
            "uri": "https://apple.com/uninstall"
          }
        }
      ]
    }
  }
  ```

* ### Get the first two webhook subscriptions with an APP\_UNINSTALLED topic

  #### Query

  ```graphql
  query {
    webhookSubscriptions(first: 2, topics: APP_UNINSTALLED) {
      edges {
        node {
          id
          topic
          uri
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
  "query": "query { webhookSubscriptions(first: 2, topics: APP_UNINSTALLED) { edges { node { id topic uri } } } }"
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
      webhookSubscriptions(first: 2, topics: APP_UNINSTALLED) {
        edges {
          node {
            id
            topic
            uri
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
      webhookSubscriptions(first: 2, topics: APP_UNINSTALLED) {
        edges {
          node {
            id
            topic
            uri
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
      webhookSubscriptions(first: 2, topics: APP_UNINSTALLED) {
        edges {
          node {
            id
            topic
            uri
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
    webhookSubscriptions(first: 2, topics: APP_UNINSTALLED) {
      edges {
        node {
          id
          topic
          uri
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscriptions": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/WebhookSubscription/901431826",
            "topic": "APP_UNINSTALLED",
            "uri": "https://apple.com/uninstall"
          }
        },
        {
          "node": {
            "id": "gid://shopify/WebhookSubscription/1014196360",
            "topic": "APP_UNINSTALLED",
            "uri": "https://example.org/app_uninstalled"
          }
        }
      ]
    }
  }
  ```
