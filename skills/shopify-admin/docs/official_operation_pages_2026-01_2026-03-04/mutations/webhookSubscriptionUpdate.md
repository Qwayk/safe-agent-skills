---
title: webhookSubscriptionUpdate - GraphQL Admin
description: >-
  Updates a webhook subscription's configuration. Modify the endpoint URL, event
  filters, included fields, or metafield namespaces without recreating the
  subscription.


  The mutation accepts a
  [`WebhookSubscriptionInput`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/WebhookSubscriptionInput)
  that specifies the new configuration. You can switch between endpoint types
  (HTTP, Pub/Sub, EventBridge) by providing a different URI format. Updates
  apply atomically without interrupting webhook delivery.



  Building an app? If you only use app-specific webhooks, you won't need this.
  App-specific webhook subscriptions specified in your `shopify.app.toml` may be
  easier. They are automatically kept up to date by Shopify & require less
  maintenance. Please read [About managing webhook
  subscriptions](https://shopify.dev/docs/apps/build/webhooks/subscribe).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/webhookSubscriptionUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/webhookSubscriptionUpdate.md
---

# webhook​Subscription​Update

mutation

Updates a webhook subscription's configuration. Modify the endpoint URL, event filters, included fields, or metafield namespaces without recreating the subscription.

The mutation accepts a [`WebhookSubscriptionInput`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/WebhookSubscriptionInput) that specifies the new configuration. You can switch between endpoint types (HTTP, Pub/Sub, EventBridge) by providing a different URI format. Updates apply atomically without interrupting webhook delivery.

Building an app? If you only use app-specific webhooks, you won't need this. App-specific webhook subscriptions specified in your `shopify.app.toml` may be easier. They are automatically kept up to date by Shopify & require less maintenance. Please read [About managing webhook subscriptions](https://shopify.dev/docs/apps/build/webhooks/subscribe).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the webhook subscription to update.

* webhook​Subscription

  [Webhook​Subscription​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/WebhookSubscriptionInput)

  required

  Specifies the input fields for a webhook subscription.

***

## Webhook​Subscription​Update​Payload returns

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

* webhook​Subscription

  [Webhook​Subscription](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebhookSubscription)

  The webhook subscription that was updated.

***

## Examples

* ### Update the uri of a webhook subscription

  #### Query

  ```graphql
  mutation webhookSubscriptionUpdate($id: ID!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionUpdate(id: $id, webhookSubscription: $webhookSubscription) {
      userErrors {
        field
        message
      }
      webhookSubscription {
        id
        topic
        uri
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/WebhookSubscription/525699895",
    "webhookSubscription": {
      "uri": "https://example.org/aValidEndpoint"
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
  "query": "mutation webhookSubscriptionUpdate($id: ID!, $webhookSubscription: WebhookSubscriptionInput!) { webhookSubscriptionUpdate(id: $id, webhookSubscription: $webhookSubscription) { userErrors { field message } webhookSubscription { id topic uri } } }",
   "variables": {
      "id": "gid://shopify/WebhookSubscription/525699895",
      "webhookSubscription": {
        "uri": "https://example.org/aValidEndpoint"
      }
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
    mutation webhookSubscriptionUpdate($id: ID!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionUpdate(id: $id, webhookSubscription: $webhookSubscription) {
        userErrors {
          field
          message
        }
        webhookSubscription {
          id
          topic
          uri
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/WebhookSubscription/525699895",
          "webhookSubscription": {
              "uri": "https://example.org/aValidEndpoint"
          }
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
    mutation webhookSubscriptionUpdate($id: ID!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionUpdate(id: $id, webhookSubscription: $webhookSubscription) {
        userErrors {
          field
          message
        }
        webhookSubscription {
          id
          topic
          uri
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/WebhookSubscription/525699895",
    "webhookSubscription": {
      "uri": "https://example.org/aValidEndpoint"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation webhookSubscriptionUpdate($id: ID!, $webhookSubscription: WebhookSubscriptionInput!) {
        webhookSubscriptionUpdate(id: $id, webhookSubscription: $webhookSubscription) {
          userErrors {
            field
            message
          }
          webhookSubscription {
            id
            topic
            uri
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/WebhookSubscription/525699895",
          "webhookSubscription": {
              "uri": "https://example.org/aValidEndpoint"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation webhookSubscriptionUpdate($id: ID!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionUpdate(id: $id, webhookSubscription: $webhookSubscription) {
      userErrors {
        field
        message
      }
      webhookSubscription {
        id
        topic
        uri
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/WebhookSubscription/525699895",
    "webhookSubscription": {
      "uri": "https://example.org/aValidEndpoint"
    }
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscriptionUpdate": {
      "userErrors": [],
      "webhookSubscription": {
        "id": "gid://shopify/WebhookSubscription/525699895",
        "topic": "ORDERS_CREATE",
        "uri": "https://example.org/aValidEndpoint"
      }
    }
  }
  ```

* ### webhookSubscriptionUpdate reference
