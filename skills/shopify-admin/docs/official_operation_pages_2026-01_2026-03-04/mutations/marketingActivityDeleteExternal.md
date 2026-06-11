---
title: marketingActivityDeleteExternal - GraphQL Admin
description: Deletes an external marketing activity.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketingActivityDeleteExternal
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketingActivityDeleteExternal.md
---

# marketing​Activity​Delete​External

mutation

Requires `write_marketing_events` access scope.

Deletes an external marketing activity.

## Arguments

* marketing​Activity​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the marketing activity. A marketing activity ID or remote ID must be provided.

* remote​Id

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A custom unique identifier for the marketing activity, which can be used to manage the activity and send engagement metrics without having to store our marketing activity ID in your systems. A marketing activity ID or remote ID must be provided.

***

## Marketing​Activity​Delete​External​Payload returns

* deleted​Marketing​Activity​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the marketing activity that was deleted, if one was deleted.

* user​Errors

  [\[Marketing​Activity​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketingActivityUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Delete an external marketing activity using the remote ID

  #### Query

  ```graphql
  mutation marketingActivityUpdateExternal($remoteId: String!) {
    marketingActivityDeleteExternal(remoteId: $remoteId) {
      deletedMarketingActivityId
    }
  }
  ```

  #### Variables

  ```json
  {
    "remoteId": "abcdefg"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation marketingActivityUpdateExternal($remoteId: String!) { marketingActivityDeleteExternal(remoteId: $remoteId) { deletedMarketingActivityId } }",
   "variables": {
      "remoteId": "abcdefg"
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
    mutation marketingActivityUpdateExternal($remoteId: String!) {
      marketingActivityDeleteExternal(remoteId: $remoteId) {
        deletedMarketingActivityId
      }
    }`,
    {
      variables: {
          "remoteId": "abcdefg"
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
    mutation marketingActivityUpdateExternal($remoteId: String!) {
      marketingActivityDeleteExternal(remoteId: $remoteId) {
        deletedMarketingActivityId
      }
    }
  QUERY

  variables = {
    "remoteId": "abcdefg"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation marketingActivityUpdateExternal($remoteId: String!) {
        marketingActivityDeleteExternal(remoteId: $remoteId) {
          deletedMarketingActivityId
        }
      }`,
      "variables": {
          "remoteId": "abcdefg"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation marketingActivityUpdateExternal($remoteId: String!) {
    marketingActivityDeleteExternal(remoteId: $remoteId) {
      deletedMarketingActivityId
    }
  }' \
  --variables \
  '{
    "remoteId": "abcdefg"
  }'
  ```

  #### Response

  ```json
  {
    "marketingActivityDeleteExternal": {
      "deletedMarketingActivityId": "gid://shopify/MarketingActivity/36187062"
    }
  }
  ```

* ### Deletes a marketing event

  #### Query

  ```graphql
  mutation marketingActivityDeleteExternal($marketingActivityId: ID!) {
    marketingActivityDeleteExternal(marketingActivityId: $marketingActivityId) {
      deletedMarketingActivityId
    }
  }
  ```

  #### Variables

  ```json
  {
    "marketingActivityId": "gid://shopify/MarketingActivity/36187062"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation marketingActivityDeleteExternal($marketingActivityId: ID!) { marketingActivityDeleteExternal(marketingActivityId: $marketingActivityId) { deletedMarketingActivityId } }",
   "variables": {
      "marketingActivityId": "gid://shopify/MarketingActivity/36187062"
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
    mutation marketingActivityDeleteExternal($marketingActivityId: ID!) {
      marketingActivityDeleteExternal(marketingActivityId: $marketingActivityId) {
        deletedMarketingActivityId
      }
    }`,
    {
      variables: {
          "marketingActivityId": "gid://shopify/MarketingActivity/36187062"
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
    mutation marketingActivityDeleteExternal($marketingActivityId: ID!) {
      marketingActivityDeleteExternal(marketingActivityId: $marketingActivityId) {
        deletedMarketingActivityId
      }
    }
  QUERY

  variables = {
    "marketingActivityId": "gid://shopify/MarketingActivity/36187062"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation marketingActivityDeleteExternal($marketingActivityId: ID!) {
        marketingActivityDeleteExternal(marketingActivityId: $marketingActivityId) {
          deletedMarketingActivityId
        }
      }`,
      "variables": {
          "marketingActivityId": "gid://shopify/MarketingActivity/36187062"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation marketingActivityDeleteExternal($marketingActivityId: ID!) {
    marketingActivityDeleteExternal(marketingActivityId: $marketingActivityId) {
      deletedMarketingActivityId
    }
  }' \
  --variables \
  '{
    "marketingActivityId": "gid://shopify/MarketingActivity/36187062"
  }'
  ```

  #### Response

  ```json
  {
    "marketingActivityDeleteExternal": {
      "deletedMarketingActivityId": "gid://shopify/MarketingActivity/36187062"
    }
  }
  ```

* ### marketingActivityDeleteExternal reference
