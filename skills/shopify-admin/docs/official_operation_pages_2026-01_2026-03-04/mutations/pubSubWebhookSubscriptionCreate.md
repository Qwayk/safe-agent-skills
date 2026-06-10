---
title: pubSubWebhookSubscriptionCreate - GraphQL Admin
description: >-
  Creates a webhook subscription that notifies your
  [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App) when
  specific events occur in a shop. Webhooks push event data to your endpoint
  immediately when changes happen, eliminating the need for polling.


  This mutation configures webhook delivery to a Google Cloud Pub/Sub topic. You
  can filter events using [Shopify API search
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
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/pubSubWebhookSubscriptionCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/pubSubWebhookSubscriptionCreate.md
---

# pub​Sub​Webhook​Subscription​Create

mutation

Deprecated. Use [webhookSubscriptionCreate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/webhookSubscriptionCreate) instead.

Creates a webhook subscription that notifies your [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App) when specific events occur in a shop. Webhooks push event data to your endpoint immediately when changes happen, eliminating the need for polling.

This mutation configures webhook delivery to a Google Cloud Pub/Sub topic. You can filter events using [Shopify API search syntax](https://shopify.dev/docs/api/usage/search-syntax) to receive only relevant webhooks, control which data fields are included in webhook payloads, and specify metafield namespaces to include.

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

  [Pub​Sub​Webhook​Subscription​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PubSubWebhookSubscriptionInput)

  required

  Specifies the input fields for a Google Cloud Pub/Sub webhook subscription.

***

## Pub​Sub​Webhook​Subscription​Create​Payload returns

* user​Errors

  [\[Pub​Sub​Webhook​Subscription​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PubSubWebhookSubscriptionCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

* webhook​Subscription

  [Webhook​Subscription](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebhookSubscription)

  The webhook subscription that was created.

***

## Examples

* ### Create a Google Cloud Pub/Sub webhook subscription for ORDERS\_CREATE events

  #### Query

  ```graphql
  mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
    pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        format
        endpoint {
          __typename
          ... on WebhookPubSubEndpoint {
            pubSubProject
            pubSubTopic
          }
        }
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
      "pubSubProject": "my-gcp-project",
      "pubSubTopic": "my-gcp-topic",
      "format": "JSON"
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
  "query": "mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) { pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) { webhookSubscription { id topic format endpoint { __typename ... on WebhookPubSubEndpoint { pubSubProject pubSubTopic } } } userErrors { field message } } }",
   "variables": {
      "topic": "ORDERS_CREATE",
      "webhookSubscription": {
        "pubSubProject": "my-gcp-project",
        "pubSubTopic": "my-gcp-topic",
        "format": "JSON"
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
    mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
      pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          format
          endpoint {
            __typename
            ... on WebhookPubSubEndpoint {
              pubSubProject
              pubSubTopic
            }
          }
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
              "pubSubProject": "my-gcp-project",
              "pubSubTopic": "my-gcp-topic",
              "format": "JSON"
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
    mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
      pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          format
          endpoint {
            __typename
            ... on WebhookPubSubEndpoint {
              pubSubProject
              pubSubTopic
            }
          }
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
      "pubSubProject": "my-gcp-project",
      "pubSubTopic": "my-gcp-topic",
      "format": "JSON"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
        pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
          webhookSubscription {
            id
            topic
            format
            endpoint {
              __typename
              ... on WebhookPubSubEndpoint {
                pubSubProject
                pubSubTopic
              }
            }
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
              "pubSubProject": "my-gcp-project",
              "pubSubTopic": "my-gcp-topic",
              "format": "JSON"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
    pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        format
        endpoint {
          __typename
          ... on WebhookPubSubEndpoint {
            pubSubProject
            pubSubTopic
          }
        }
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
      "pubSubProject": "my-gcp-project",
      "pubSubTopic": "my-gcp-topic",
      "format": "JSON"
    }
  }'
  ```

  #### Response

  ```json
  {
    "pubSubWebhookSubscriptionCreate": {
      "webhookSubscription": {
        "id": "gid://shopify/WebhookSubscription/8589934664",
        "topic": "ORDERS_CREATE",
        "format": "JSON",
        "endpoint": {
          "__typename": "WebhookPubSubEndpoint",
          "pubSubProject": "my-gcp-project",
          "pubSubTopic": "my-gcp-topic"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a METAOBJECTS\_CREATE Pub/Sub webhook subscription for lookbook metaobjects

  #### Query

  ```graphql
  mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
    pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        filter
        format
        endpoint {
          __typename
          ... on WebhookPubSubEndpoint {
            pubSubProject
            pubSubTopic
          }
        }
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
      "pubSubProject": "my-gcp-project",
      "pubSubTopic": "my-gcp-topic",
      "format": "JSON",
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
  "query": "mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) { pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) { webhookSubscription { id topic filter format endpoint { __typename ... on WebhookPubSubEndpoint { pubSubProject pubSubTopic } } } userErrors { field message } } }",
   "variables": {
      "topic": "METAOBJECTS_CREATE",
      "webhookSubscription": {
        "pubSubProject": "my-gcp-project",
        "pubSubTopic": "my-gcp-topic",
        "format": "JSON",
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
    mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
      pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          filter
          format
          endpoint {
            __typename
            ... on WebhookPubSubEndpoint {
              pubSubProject
              pubSubTopic
            }
          }
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
              "pubSubProject": "my-gcp-project",
              "pubSubTopic": "my-gcp-topic",
              "format": "JSON",
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
    mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
      pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          filter
          format
          endpoint {
            __typename
            ... on WebhookPubSubEndpoint {
              pubSubProject
              pubSubTopic
            }
          }
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
      "pubSubProject": "my-gcp-project",
      "pubSubTopic": "my-gcp-topic",
      "format": "JSON",
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
      "query": `mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
        pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
          webhookSubscription {
            id
            topic
            filter
            format
            endpoint {
              __typename
              ... on WebhookPubSubEndpoint {
                pubSubProject
                pubSubTopic
              }
            }
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
              "pubSubProject": "my-gcp-project",
              "pubSubTopic": "my-gcp-topic",
              "format": "JSON",
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
  'mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
    pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        filter
        format
        endpoint {
          __typename
          ... on WebhookPubSubEndpoint {
            pubSubProject
            pubSubTopic
          }
        }
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
      "pubSubProject": "my-gcp-project",
      "pubSubTopic": "my-gcp-topic",
      "format": "JSON",
      "filter": "type:lookbook"
    }
  }'
  ```

  #### Response

  ```json
  {
    "pubSubWebhookSubscriptionCreate": {
      "webhookSubscription": {
        "id": "gid://shopify/WebhookSubscription/8589934655",
        "topic": "METAOBJECTS_CREATE",
        "filter": "type:lookbook",
        "format": "JSON",
        "endpoint": {
          "__typename": "WebhookPubSubEndpoint",
          "pubSubProject": "my-gcp-project",
          "pubSubTopic": "my-gcp-topic"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create an ORDERS\_CREATE Pub/Sub webhook subscription that includes metafields during serialization

  #### Query

  ```graphql
  mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
    pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        format
        metafieldNamespaces
        endpoint {
          __typename
          ... on WebhookPubSubEndpoint {
            pubSubProject
            pubSubTopic
          }
        }
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
      "pubSubProject": "my-gcp-project",
      "pubSubTopic": "my-gcp-topic",
      "format": "JSON",
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
  "query": "mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) { pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) { webhookSubscription { id topic format metafieldNamespaces endpoint { __typename ... on WebhookPubSubEndpoint { pubSubProject pubSubTopic } } } userErrors { field message } } }",
   "variables": {
      "topic": "ORDERS_CREATE",
      "webhookSubscription": {
        "pubSubProject": "my-gcp-project",
        "pubSubTopic": "my-gcp-topic",
        "format": "JSON",
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
    mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
      pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          format
          metafieldNamespaces
          endpoint {
            __typename
            ... on WebhookPubSubEndpoint {
              pubSubProject
              pubSubTopic
            }
          }
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
              "pubSubProject": "my-gcp-project",
              "pubSubTopic": "my-gcp-topic",
              "format": "JSON",
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
    mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
      pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          format
          metafieldNamespaces
          endpoint {
            __typename
            ... on WebhookPubSubEndpoint {
              pubSubProject
              pubSubTopic
            }
          }
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
      "pubSubProject": "my-gcp-project",
      "pubSubTopic": "my-gcp-topic",
      "format": "JSON",
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
      "query": `mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
        pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
          webhookSubscription {
            id
            topic
            format
            metafieldNamespaces
            endpoint {
              __typename
              ... on WebhookPubSubEndpoint {
                pubSubProject
                pubSubTopic
              }
            }
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
              "pubSubProject": "my-gcp-project",
              "pubSubTopic": "my-gcp-topic",
              "format": "JSON",
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
  'mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
    pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        format
        metafieldNamespaces
        endpoint {
          __typename
          ... on WebhookPubSubEndpoint {
            pubSubProject
            pubSubTopic
          }
        }
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
      "pubSubProject": "my-gcp-project",
      "pubSubTopic": "my-gcp-topic",
      "format": "JSON",
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
    "pubSubWebhookSubscriptionCreate": {
      "webhookSubscription": {
        "id": "gid://shopify/WebhookSubscription/8589934658",
        "topic": "ORDERS_CREATE",
        "format": "JSON",
        "metafieldNamespaces": [
          "MY_NAMESPACE",
          "ANOTHER_NAMESPACE"
        ],
        "endpoint": {
          "__typename": "WebhookPubSubEndpoint",
          "pubSubProject": "my-gcp-project",
          "pubSubTopic": "my-gcp-topic"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create an ORDERS\_CREATE Pub/Sub webhook subscription with fewer resource fields

  #### Query

  ```graphql
  mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
    pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        format
        includeFields
        endpoint {
          __typename
          ... on WebhookPubSubEndpoint {
            pubSubProject
            pubSubTopic
          }
        }
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
      "pubSubProject": "my-gcp-project",
      "pubSubTopic": "my-gcp-topic",
      "format": "JSON",
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
  "query": "mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) { pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) { webhookSubscription { id topic format includeFields endpoint { __typename ... on WebhookPubSubEndpoint { pubSubProject pubSubTopic } } } userErrors { field message } } }",
   "variables": {
      "topic": "ORDERS_CREATE",
      "webhookSubscription": {
        "pubSubProject": "my-gcp-project",
        "pubSubTopic": "my-gcp-topic",
        "format": "JSON",
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
    mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
      pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          format
          includeFields
          endpoint {
            __typename
            ... on WebhookPubSubEndpoint {
              pubSubProject
              pubSubTopic
            }
          }
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
              "pubSubProject": "my-gcp-project",
              "pubSubTopic": "my-gcp-topic",
              "format": "JSON",
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
    mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
      pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
        webhookSubscription {
          id
          topic
          format
          includeFields
          endpoint {
            __typename
            ... on WebhookPubSubEndpoint {
              pubSubProject
              pubSubTopic
            }
          }
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
      "pubSubProject": "my-gcp-project",
      "pubSubTopic": "my-gcp-topic",
      "format": "JSON",
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
      "query": `mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
        pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
          webhookSubscription {
            id
            topic
            format
            includeFields
            endpoint {
              __typename
              ... on WebhookPubSubEndpoint {
                pubSubProject
                pubSubTopic
              }
            }
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
              "pubSubProject": "my-gcp-project",
              "pubSubTopic": "my-gcp-topic",
              "format": "JSON",
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
  'mutation pubSubWebhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: PubSubWebhookSubscriptionInput!) {
    pubSubWebhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
      webhookSubscription {
        id
        topic
        format
        includeFields
        endpoint {
          __typename
          ... on WebhookPubSubEndpoint {
            pubSubProject
            pubSubTopic
          }
        }
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
      "pubSubProject": "my-gcp-project",
      "pubSubTopic": "my-gcp-topic",
      "format": "JSON",
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
    "pubSubWebhookSubscriptionCreate": {
      "webhookSubscription": {
        "id": "gid://shopify/WebhookSubscription/8589934662",
        "topic": "ORDERS_CREATE",
        "format": "JSON",
        "includeFields": [
          "id",
          "note"
        ],
        "endpoint": {
          "__typename": "WebhookPubSubEndpoint",
          "pubSubProject": "my-gcp-project",
          "pubSubTopic": "my-gcp-topic"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### pubSubWebhookSubscriptionCreate reference
