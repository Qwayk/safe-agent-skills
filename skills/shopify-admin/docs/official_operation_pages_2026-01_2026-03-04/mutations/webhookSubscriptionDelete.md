---
title: webhookSubscriptionDelete - GraphQL Admin
description: >-
  Deletes a
  [`WebhookSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebhookSubscription)
  and stops all future webhooks to its endpoint. Returns the deleted
  subscription's ID for confirmation.



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
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/webhookSubscriptionDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/webhookSubscriptionDelete.md
---

# webhook​Subscription​Delete

mutation

Deletes a [`WebhookSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebhookSubscription) and stops all future webhooks to its endpoint. Returns the deleted subscription's ID for confirmation.

Building an app? If you only use app-specific webhooks, you won't need this. App-specific webhook subscriptions specified in your `shopify.app.toml` may be easier. They are automatically kept up to date by Shopify & require less maintenance. Please read [About managing webhook subscriptions](https://shopify.dev/docs/apps/build/webhooks/subscribe).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the webhook subscription to delete.

***

## Webhook​Subscription​Delete​Payload returns

* deleted​Webhook​Subscription​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted webhook subscription.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Remove an existing Webhook

  #### Query

  ```graphql
  mutation webhookSubscriptionDelete($id: ID!) {
    webhookSubscriptionDelete(id: $id) {
      userErrors {
        field
        message
      }
      deletedWebhookSubscriptionId
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/WebhookSubscription/525699895"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation webhookSubscriptionDelete($id: ID!) { webhookSubscriptionDelete(id: $id) { userErrors { field message } deletedWebhookSubscriptionId } }",
   "variables": {
      "id": "gid://shopify/WebhookSubscription/525699895"
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
    mutation webhookSubscriptionDelete($id: ID!) {
      webhookSubscriptionDelete(id: $id) {
        userErrors {
          field
          message
        }
        deletedWebhookSubscriptionId
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/WebhookSubscription/525699895"
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
    mutation webhookSubscriptionDelete($id: ID!) {
      webhookSubscriptionDelete(id: $id) {
        userErrors {
          field
          message
        }
        deletedWebhookSubscriptionId
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/WebhookSubscription/525699895"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation webhookSubscriptionDelete($id: ID!) {
        webhookSubscriptionDelete(id: $id) {
          userErrors {
            field
            message
          }
          deletedWebhookSubscriptionId
        }
      }`,
      "variables": {
          "id": "gid://shopify/WebhookSubscription/525699895"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation webhookSubscriptionDelete($id: ID!) {
    webhookSubscriptionDelete(id: $id) {
      userErrors {
        field
        message
      }
      deletedWebhookSubscriptionId
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/WebhookSubscription/525699895"
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscriptionDelete": {
      "userErrors": [],
      "deletedWebhookSubscriptionId": "gid://shopify/WebhookSubscription/525699895"
    }
  }
  ```

* ### webhookSubscriptionDelete reference
