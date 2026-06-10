---
title: webhookSubscriptionCreate - GraphQL Admin
description: >-
  Creates a webhook subscription that notifies your
  [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App) when
  specific events occur in a shop. Webhooks push event data to your endpoint
  immediately when changes happen, eliminating the need for polling.


  The subscription configuration supports multiple endpoint types including
  HTTPS URLs, Google Pub/Sub topics, and AWS EventBridge event sources. You can
  filter events using [Shopify API search
  syntax](https://shopify.dev/docs/api/usage/search-syntax) to receive only
  relevant webhooks, control which data fields are included in webhook payloads,
  and specify metafield namespaces to include.


  > Note:

  > The Webhooks API version [configured in your
  app](https://shopify.dev/docs/apps/build/webhooks/subscribe/use-newer-api-version)
  determines the API version for webhook events. You can't specify it per
  subscription.



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
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/webhookSubscriptionCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/webhookSubscriptionCreate.md
---

# webhook​Subscription​Create

mutation

Creates a webhook subscription that notifies your [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App) when specific events occur in a shop. Webhooks push event data to your endpoint immediately when changes happen, eliminating the need for polling.

The subscription configuration supports multiple endpoint types including HTTPS URLs, Google Pub/Sub topics, and AWS EventBridge event sources. You can filter events using [Shopify API search syntax](https://shopify.dev/docs/api/usage/search-syntax) to receive only relevant webhooks, control which data fields are included in webhook payloads, and specify metafield namespaces to include.

***

**Note:** The Webhooks API version \<a href="https://shopify.dev/docs/apps/build/webhooks/subscribe/use-newer-api-version">configured in your app\</a> determines the API version for webhook events. You can\&#39;t specify it per subscription.

***

Building an app? If you only use app-specific webhooks, you won't need this. App-specific webhook subscriptions specified in your `shopify.app.toml` may be easier. They are automatically kept up to date by Shopify & require less maintenance. Please read [About managing webhook subscriptions](https://shopify.dev/docs/apps/build/webhooks/subscribe).

## Arguments

* topic

  [Webhook​Subscription​Topic!](https://shopify.dev/docs/api/admin-graphql/latest/enums/WebhookSubscriptionTopic)

  required

  The type of event that triggers the webhook.

* webhook​Subscription

  [Webhook​Subscription​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/WebhookSubscriptionInput)

  required

  Specifies the input fields for a webhook subscription.

***

## Webhook​Subscription​Create​Payload returns

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

* webhook​Subscription

  [Webhook​Subscription](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebhookSubscription)

  The webhook subscription that was created.

***

## Examples

* ### Create a METAOBJECTS\_CREATE webhook subscription for 'lookbook' metaobjects

  #### Query

  ```graphql
  mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        filter
        uri
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "topic": "METAOBJECTS_CREATE",
    "webhookSubscription": {
      "uri": "https://example.org/endpoint",
      "filter": "type:lookbook"
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
  "query": "mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) { webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) { webhookSubscription { id topic filter uri } userErrors { field message } } }",
   "variables": {
      "topic": "METAOBJECTS_CREATE",
      "webhookSubscription": {
        "uri": "https://example.org/endpoint",
        "filter": "type:lookbook"
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
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          filter
          uri
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "topic": "METAOBJECTS_CREATE",
          "webhookSubscription": {
              "uri": "https://example.org/endpoint",
              "filter": "type:lookbook"
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
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          filter
          uri
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "topic": "METAOBJECTS_CREATE",
    "webhookSubscription": {
      "uri": "https://example.org/endpoint",
      "filter": "type:lookbook"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
        webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
          webhookSubscription {
            id
            topic
            filter
            uri
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "topic": "METAOBJECTS_CREATE",
          "webhookSubscription": {
              "uri": "https://example.org/endpoint",
              "filter": "type:lookbook"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        filter
        uri
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "topic": "METAOBJECTS_CREATE",
    "webhookSubscription": {
      "uri": "https://example.org/endpoint",
      "filter": "type:lookbook"
    }
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscriptionCreate": {
      "webhookSubscription": {
        "id": "gid://shopify/WebhookSubscription/8589934634",
        "topic": "METAOBJECTS_CREATE",
        "filter": "type:lookbook",
        "uri": "https://example.org/endpoint"
      },
      "userErrors": []
    }
  }
  ```

* ### Create a PubSub webhook subscription for APP\_UNINSTALLED

  #### Query

  ```graphql
  mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        uri
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "topic": "APP_UNINSTALLED",
    "webhookSubscription": {
      "uri": "pubsub://my-gcp-project:my-gcp-topic"
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
  "query": "mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) { webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) { webhookSubscription { id topic uri } userErrors { field message } } }",
   "variables": {
      "topic": "APP_UNINSTALLED",
      "webhookSubscription": {
        "uri": "pubsub://my-gcp-project:my-gcp-topic"
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
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          uri
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "topic": "APP_UNINSTALLED",
          "webhookSubscription": {
              "uri": "pubsub://my-gcp-project:my-gcp-topic"
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
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          uri
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "topic": "APP_UNINSTALLED",
    "webhookSubscription": {
      "uri": "pubsub://my-gcp-project:my-gcp-topic"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
        webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
          webhookSubscription {
            id
            topic
            uri
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "topic": "APP_UNINSTALLED",
          "webhookSubscription": {
              "uri": "pubsub://my-gcp-project:my-gcp-topic"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        uri
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "topic": "APP_UNINSTALLED",
    "webhookSubscription": {
      "uri": "pubsub://my-gcp-project:my-gcp-topic"
    }
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscriptionCreate": {
      "webhookSubscription": {
        "id": "gid://shopify/WebhookSubscription/8589934629",
        "topic": "APP_UNINSTALLED",
        "uri": "pubsub://my-gcp-project:my-gcp-topic"
      },
      "userErrors": []
    }
  }
  ```

* ### Create an EventBridge webhook subscription for APP\_UNINSTALLED

  #### Query

  ```graphql
  mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        uri
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "topic": "APP_UNINSTALLED",
    "webhookSubscription": {
      "uri": "arn:aws:events:us-east-1::event-source/aws.partner/shopify.com/1002334195/test-event-source"
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
  "query": "mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) { webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) { webhookSubscription { id topic uri } userErrors { field message } } }",
   "variables": {
      "topic": "APP_UNINSTALLED",
      "webhookSubscription": {
        "uri": "arn:aws:events:us-east-1::event-source/aws.partner/shopify.com/1002334195/test-event-source"
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
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          uri
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "topic": "APP_UNINSTALLED",
          "webhookSubscription": {
              "uri": "arn:aws:events:us-east-1::event-source/aws.partner/shopify.com/1002334195/test-event-source"
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
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          uri
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "topic": "APP_UNINSTALLED",
    "webhookSubscription": {
      "uri": "arn:aws:events:us-east-1::event-source/aws.partner/shopify.com/1002334195/test-event-source"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
        webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
          webhookSubscription {
            id
            topic
            uri
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "topic": "APP_UNINSTALLED",
          "webhookSubscription": {
              "uri": "arn:aws:events:us-east-1::event-source/aws.partner/shopify.com/1002334195/test-event-source"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        uri
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "topic": "APP_UNINSTALLED",
    "webhookSubscription": {
      "uri": "arn:aws:events:us-east-1::event-source/aws.partner/shopify.com/1002334195/test-event-source"
    }
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscriptionCreate": {
      "webhookSubscription": {
        "id": "gid://shopify/WebhookSubscription/8589934633",
        "topic": "APP_UNINSTALLED",
        "uri": "arn:aws:events:us-east-1::event-source/aws.partner/shopify.com/1002334195/test-event-source"
      },
      "userErrors": []
    }
  }
  ```

* ### Create an HTTP webhook subscription for APP\_UNINSTALLED

  #### Query

  ```graphql
  mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        uri
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "topic": "APP_UNINSTALLED",
    "webhookSubscription": {
      "uri": "https://example.org/endpoint"
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
  "query": "mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) { webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) { webhookSubscription { id topic uri } userErrors { field message } } }",
   "variables": {
      "topic": "APP_UNINSTALLED",
      "webhookSubscription": {
        "uri": "https://example.org/endpoint"
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
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          uri
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "topic": "APP_UNINSTALLED",
          "webhookSubscription": {
              "uri": "https://example.org/endpoint"
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
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          uri
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "topic": "APP_UNINSTALLED",
    "webhookSubscription": {
      "uri": "https://example.org/endpoint"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
        webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
          webhookSubscription {
            id
            topic
            uri
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "topic": "APP_UNINSTALLED",
          "webhookSubscription": {
              "uri": "https://example.org/endpoint"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        uri
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "topic": "APP_UNINSTALLED",
    "webhookSubscription": {
      "uri": "https://example.org/endpoint"
    }
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscriptionCreate": {
      "webhookSubscription": {
        "id": "gid://shopify/WebhookSubscription/8589934632",
        "topic": "APP_UNINSTALLED",
        "uri": "https://example.org/endpoint"
      },
      "userErrors": []
    }
  }
  ```

* ### Create an ORDERS\_CREATE webhook subscription that includes metafields

  #### Query

  ```graphql
  mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        metafieldNamespaces
        uri
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "topic": "ORDERS_CREATE",
    "webhookSubscription": {
      "uri": "https://example.org/endpoint",
      "metafieldNamespaces": [
        "MY_NAMESPACE",
        "ANOTHER_NAMESPACE"
      ]
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
  "query": "mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) { webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) { webhookSubscription { id topic metafieldNamespaces uri } userErrors { field message } } }",
   "variables": {
      "topic": "ORDERS_CREATE",
      "webhookSubscription": {
        "uri": "https://example.org/endpoint",
        "metafieldNamespaces": [
          "MY_NAMESPACE",
          "ANOTHER_NAMESPACE"
        ]
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
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          metafieldNamespaces
          uri
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "topic": "ORDERS_CREATE",
          "webhookSubscription": {
              "uri": "https://example.org/endpoint",
              "metafieldNamespaces": [
                  "MY_NAMESPACE",
                  "ANOTHER_NAMESPACE"
              ]
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
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          metafieldNamespaces
          uri
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "topic": "ORDERS_CREATE",
    "webhookSubscription": {
      "uri": "https://example.org/endpoint",
      "metafieldNamespaces": [
        "MY_NAMESPACE",
        "ANOTHER_NAMESPACE"
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
        webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
          webhookSubscription {
            id
            topic
            metafieldNamespaces
            uri
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "topic": "ORDERS_CREATE",
          "webhookSubscription": {
              "uri": "https://example.org/endpoint",
              "metafieldNamespaces": [
                  "MY_NAMESPACE",
                  "ANOTHER_NAMESPACE"
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        metafieldNamespaces
        uri
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "topic": "ORDERS_CREATE",
    "webhookSubscription": {
      "uri": "https://example.org/endpoint",
      "metafieldNamespaces": [
        "MY_NAMESPACE",
        "ANOTHER_NAMESPACE"
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscriptionCreate": {
      "webhookSubscription": {
        "id": "gid://shopify/WebhookSubscription/8589934626",
        "topic": "ORDERS_CREATE",
        "metafieldNamespaces": [
          "MY_NAMESPACE",
          "ANOTHER_NAMESPACE"
        ],
        "uri": "https://example.org/endpoint"
      },
      "userErrors": []
    }
  }
  ```

* ### Create an ORDERS\_CREATE webhook subscription with fewer resource fields

  #### Query

  ```graphql
  mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        includeFields
        uri
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "topic": "ORDERS_CREATE",
    "webhookSubscription": {
      "uri": "https://example.org/endpoint",
      "includeFields": [
        "id",
        "note"
      ]
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
  "query": "mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) { webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) { webhookSubscription { id topic includeFields uri } userErrors { field message } } }",
   "variables": {
      "topic": "ORDERS_CREATE",
      "webhookSubscription": {
        "uri": "https://example.org/endpoint",
        "includeFields": [
          "id",
          "note"
        ]
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
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          includeFields
          uri
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "topic": "ORDERS_CREATE",
          "webhookSubscription": {
              "uri": "https://example.org/endpoint",
              "includeFields": [
                  "id",
                  "note"
              ]
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
    mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          includeFields
          uri
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "topic": "ORDERS_CREATE",
    "webhookSubscription": {
      "uri": "https://example.org/endpoint",
      "includeFields": [
        "id",
        "note"
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
        webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
          webhookSubscription {
            id
            topic
            includeFields
            uri
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "topic": "ORDERS_CREATE",
          "webhookSubscription": {
              "uri": "https://example.org/endpoint",
              "includeFields": [
                  "id",
                  "note"
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
    webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        includeFields
        uri
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "topic": "ORDERS_CREATE",
    "webhookSubscription": {
      "uri": "https://example.org/endpoint",
      "includeFields": [
        "id",
        "note"
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "webhookSubscriptionCreate": {
      "webhookSubscription": {
        "id": "gid://shopify/WebhookSubscription/8589934628",
        "topic": "ORDERS_CREATE",
        "includeFields": [
          "id",
          "note"
        ],
        "uri": "https://example.org/endpoint"
      },
      "userErrors": []
    }
  }
  ```

* ### webhookSubscriptionCreate reference
