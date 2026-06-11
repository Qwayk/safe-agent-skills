---
title: webhookSubscription - GraphQL Admin
description: >-
  Returns a webhook subscription by ID.


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
    https://shopify.dev/docs/api/admin-graphql/latest/queries/webhookSubscription
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/webhookSubscription.md
---

# webhook​Subscription

query

Returns a webhook subscription by ID.

Building an app? If you only use app-specific webhooks, you won't need this. App-specific webhook subscriptions specified in your `shopify.app.toml` may be easier. They are automatically kept up to date by Shopify & require less maintenance. Please read [About managing webhook subscriptions](https://shopify.dev/docs/apps/build/webhooks/subscribe).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `WebhookSubscription` to return.

***

## Possible returns

* Webhook​Subscription

  [Webhook​Subscription](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebhookSubscription)

  A webhook subscription is a persisted data object created by an app using the REST Admin API or GraphQL Admin API. It describes the topic that the app wants to receive, and a destination where Shopify should send webhooks of the specified topic. When an event for a given topic occurs, the webhook subscription sends a relevant payload to the destination. Learn more about the [webhooks system](https://shopify.dev/apps/webhooks).

  * api​Version

    [Api​Version!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ApiVersion)

    non-null

    The Admin API version that Shopify uses to serialize webhook events. This value is inherited from the app that created the webhook subscription.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the webhook subscription was created.

  * filter

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    A constraint specified using search syntax that ensures only webhooks that match the specified filter are emitted. See our [guide on filters](https://shopify.dev/docs/apps/build/webhooks/customize/filters) for more details.

  * format

    [Webhook​Subscription​Format!](https://shopify.dev/docs/api/admin-graphql/latest/enums/WebhookSubscriptionFormat)

    non-null

    The format in which the webhook subscription should send the data.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * include​Fields

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The list of fields to be included in the webhook subscription. Only the fields specified will be included in the webhook payload. If null, then all fields will be included. Learn more about [modifying webhook payloads](https://shopify.dev/docs/apps/build/webhooks/customize/modify-payloads).

  * legacy​Resource​Id

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The ID of the corresponding resource in the REST Admin API.

  * metafield​Namespaces

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The list of namespaces for any metafields that should be included in the webhook subscription.

  * metafields

    [\[Webhook​Subscription​Metafield​Identifier!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebhookSubscriptionMetafieldIdentifier)

    non-null

    The list of identifiers specifying metafields to include in the webhook subscription.

  * topic

    [Webhook​Subscription​Topic!](https://shopify.dev/docs/api/admin-graphql/latest/enums/WebhookSubscriptionTopic)

    non-null

    The type of event that triggers the webhook. The topic determines when the webhook subscription sends a webhook, as well as what class of data object that webhook contains.

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the webhook subscription was updated.

  * uri

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The URI to which the webhook subscription will send events.

  * callback​Url

    [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    non-nullDeprecated

  * endpoint

    [Webhook​Subscription​Endpoint!](https://shopify.dev/docs/api/admin-graphql/latest/unions/WebhookSubscriptionEndpoint)

    non-nullDeprecated

***

## Examples

* ### Get a single webhook subscription's ID, topic and URI

  #### Query

  ```graphql
  query {
    webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
      id
      topic
      uri
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
  "query": "query { webhookSubscription(id: \"gid://shopify/WebhookSubscription/892403750\") { id topic uri } }"
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
      webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
        id
        topic
        uri
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
      webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
        id
        topic
        uri
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
      webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
        id
        topic
        uri
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
      id
      topic
      uri
    }
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscription": {
      "id": "gid://shopify/WebhookSubscription/892403750",
      "topic": "ORDERS_CANCELLED",
      "uri": "https://example.org/fully_loaded_1"
    }
  }
  ```

* ### Get a specific webhook subscription using the node field and a GraphQL fragment

  #### Query

  ```graphql
  query {
    node(id: "gid://shopify/WebhookSubscription/892403750") {
      ... on WebhookSubscription {
        id
        createdAt
        updatedAt
        legacyResourceId
        topic
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
  "query": "query { node(id: \"gid://shopify/WebhookSubscription/892403750\") { ... on WebhookSubscription { id createdAt updatedAt legacyResourceId topic } } }"
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
      node(id: "gid://shopify/WebhookSubscription/892403750") {
        ... on WebhookSubscription {
          id
          createdAt
          updatedAt
          legacyResourceId
          topic
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
      node(id: "gid://shopify/WebhookSubscription/892403750") {
        ... on WebhookSubscription {
          id
          createdAt
          updatedAt
          legacyResourceId
          topic
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
      node(id: "gid://shopify/WebhookSubscription/892403750") {
        ... on WebhookSubscription {
          id
          createdAt
          updatedAt
          legacyResourceId
          topic
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
    node(id: "gid://shopify/WebhookSubscription/892403750") {
      ... on WebhookSubscription {
        id
        createdAt
        updatedAt
        legacyResourceId
        topic
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "node": {
      "id": "gid://shopify/WebhookSubscription/892403750",
      "createdAt": "2021-12-01T10:23:43Z",
      "updatedAt": "2021-12-01T10:23:43Z",
      "legacyResourceId": "892403750",
      "topic": "ORDERS_CANCELLED"
    }
  }
  ```

* ### Get the dates a webhook subscription was created and updated

  #### Query

  ```graphql
  query {
    webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
      createdAt
      updatedAt
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
  "query": "query { webhookSubscription(id: \"gid://shopify/WebhookSubscription/892403750\") { createdAt updatedAt } }"
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
      webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
        createdAt
        updatedAt
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
      webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
        createdAt
        updatedAt
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
      webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
        createdAt
        updatedAt
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
      createdAt
      updatedAt
    }
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscription": {
      "createdAt": "2021-12-01T10:23:43Z",
      "updatedAt": "2021-12-01T10:23:43Z"
    }
  }
  ```

* ### Get the topic of a webhook subscription

  #### Query

  ```graphql
  query {
    webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
      topic
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
  "query": "query { webhookSubscription(id: \"gid://shopify/WebhookSubscription/892403750\") { topic } }"
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
      webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
        topic
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
      webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
        topic
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
      webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
        topic
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    webhookSubscription(id: "gid://shopify/WebhookSubscription/892403750") {
      topic
    }
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscription": {
      "topic": "ORDERS_CANCELLED"
    }
  }
  ```
