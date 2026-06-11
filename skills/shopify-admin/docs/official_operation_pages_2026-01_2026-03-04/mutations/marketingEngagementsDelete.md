---
title: marketingEngagementsDelete - GraphQL Admin
description: |-
  Marks channel-level engagement data such that it no longer appears in reports.
            Activity-level data cannot be deleted directly, instead the MarketingActivity itself should be deleted to
            hide it from reports.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketingEngagementsDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketingEngagementsDelete.md
---

# marketing​Engagements​Delete

mutation

Requires `write_marketing_events` access scope.

Marks channel-level engagement data such that it no longer appears in reports. Activity-level data cannot be deleted directly, instead the MarketingActivity itself should be deleted to hide it from reports.

## Arguments

* channel​Handle

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The handle of the channel for which engagement data should be deleted.

* delete​Engagements​For​All​Channels

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  When true, engagements for all channels that belong to the api client will be deleted.

***

## Marketing​Engagements​Delete​Payload returns

* result

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  Informational message about the engagement data that has been marked for deletion.

* user​Errors

  [\[Marketing​Activity​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketingActivityUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Mark all channel level engagement data associated to the api client for deletion

  #### Query

  ```graphql
  mutation M($channelHandle: String, $deleteEngagementsForAllChannels: Boolean) {
    marketingEngagementsDelete(channelHandle: $channelHandle, deleteEngagementsForAllChannels: $deleteEngagementsForAllChannels) {
      result
      userErrors {
        field
        message
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
  "query": "mutation M($channelHandle: String, $deleteEngagementsForAllChannels: Boolean) { marketingEngagementsDelete(channelHandle: $channelHandle, deleteEngagementsForAllChannels: $deleteEngagementsForAllChannels) { result userErrors { field message } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation M($channelHandle: String, $deleteEngagementsForAllChannels: Boolean) {
      marketingEngagementsDelete(channelHandle: $channelHandle, deleteEngagementsForAllChannels: $deleteEngagementsForAllChannels) {
        result
        userErrors {
          field
          message
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
    mutation M($channelHandle: String, $deleteEngagementsForAllChannels: Boolean) {
      marketingEngagementsDelete(channelHandle: $channelHandle, deleteEngagementsForAllChannels: $deleteEngagementsForAllChannels) {
        result
        userErrors {
          field
          message
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
    data: `mutation M($channelHandle: String, $deleteEngagementsForAllChannels: Boolean) {
      marketingEngagementsDelete(channelHandle: $channelHandle, deleteEngagementsForAllChannels: $deleteEngagementsForAllChannels) {
        result
        userErrors {
          field
          message
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation M($channelHandle: String, $deleteEngagementsForAllChannels: Boolean) {
    marketingEngagementsDelete(channelHandle: $channelHandle, deleteEngagementsForAllChannels: $deleteEngagementsForAllChannels) {
      result
      userErrors {
        field
        message
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "marketingEngagementsDelete": {
      "result": "Engagement data marked for deletion for 5 channel(s)",
      "userErrors": []
    }
  }
  ```

* ### Mark engagement data associated to a specific channel for deletion

  #### Query

  ```graphql
  mutation M($channelHandle: String, $deleteEngagementsForAllChannels: Boolean) {
    marketingEngagementsDelete(channelHandle: $channelHandle, deleteEngagementsForAllChannels: $deleteEngagementsForAllChannels) {
      result
      userErrors {
        field
        message
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
  "query": "mutation M($channelHandle: String, $deleteEngagementsForAllChannels: Boolean) { marketingEngagementsDelete(channelHandle: $channelHandle, deleteEngagementsForAllChannels: $deleteEngagementsForAllChannels) { result userErrors { field message } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation M($channelHandle: String, $deleteEngagementsForAllChannels: Boolean) {
      marketingEngagementsDelete(channelHandle: $channelHandle, deleteEngagementsForAllChannels: $deleteEngagementsForAllChannels) {
        result
        userErrors {
          field
          message
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
    mutation M($channelHandle: String, $deleteEngagementsForAllChannels: Boolean) {
      marketingEngagementsDelete(channelHandle: $channelHandle, deleteEngagementsForAllChannels: $deleteEngagementsForAllChannels) {
        result
        userErrors {
          field
          message
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
    data: `mutation M($channelHandle: String, $deleteEngagementsForAllChannels: Boolean) {
      marketingEngagementsDelete(channelHandle: $channelHandle, deleteEngagementsForAllChannels: $deleteEngagementsForAllChannels) {
        result
        userErrors {
          field
          message
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation M($channelHandle: String, $deleteEngagementsForAllChannels: Boolean) {
    marketingEngagementsDelete(channelHandle: $channelHandle, deleteEngagementsForAllChannels: $deleteEngagementsForAllChannels) {
      result
      userErrors {
        field
        message
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "marketingEngagementsDelete": {
      "result": "Engagement data associated to channel handle 'my-channel-handle' marked for deletion",
      "userErrors": []
    }
  }
  ```

* ### marketingEngagementsDelete reference
