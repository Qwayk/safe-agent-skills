---
title: marketingActivityUpsertExternal - GraphQL Admin
description: >-
  Creates a new external marketing activity or updates an existing one. When
  optional fields are absent or null, associated information will be removed
  from an existing marketing activity.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketingActivityUpsertExternal
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketingActivityUpsertExternal.md
---

# marketing​Activity​Upsert​External

mutation

Requires `write_marketing_events` access scope.

Creates a new external marketing activity or updates an existing one. When optional fields are absent or null, associated information will be removed from an existing marketing activity.

## Arguments

* input

  [Marketing​Activity​Upsert​External​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MarketingActivityUpsertExternalInput)

  required

  The input field for creating or updating an external marketing activity.

***

## Marketing​Activity​Upsert​External​Payload returns

* marketing​Activity

  [Marketing​Activity](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketingActivity)

  The external marketing activity that was created or updated.

* user​Errors

  [\[Marketing​Activity​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketingActivityUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Upsert (create or update) an external marketing activity

  #### Query

  ```graphql
  mutation marketingActivityUpsertExternal($input: MarketingActivityUpsertExternalInput!) {
    marketingActivityUpsertExternal(input: $input) {
      marketingActivity {
        id
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "remoteId": "A unique identifier",
      "title": "New Title",
      "remoteUrl": "https://example.com",
      "status": "ACTIVE",
      "utm": {
        "source": "email",
        "medium": "newsletter",
        "campaign": "external-campaign"
      },
      "tactic": "NEWSLETTER",
      "marketingChannelType": "EMAIL"
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
  "query": "mutation marketingActivityUpsertExternal($input: MarketingActivityUpsertExternalInput!) { marketingActivityUpsertExternal(input: $input) { marketingActivity { id } } }",
   "variables": {
      "input": {
        "remoteId": "A unique identifier",
        "title": "New Title",
        "remoteUrl": "https://example.com",
        "status": "ACTIVE",
        "utm": {
          "source": "email",
          "medium": "newsletter",
          "campaign": "external-campaign"
        },
        "tactic": "NEWSLETTER",
        "marketingChannelType": "EMAIL"
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
    mutation marketingActivityUpsertExternal($input: MarketingActivityUpsertExternalInput!) {
      marketingActivityUpsertExternal(input: $input) {
        marketingActivity {
          id
        }
      }
    }`,
    {
      variables: {
          "input": {
              "remoteId": "A unique identifier",
              "title": "New Title",
              "remoteUrl": "https://example.com",
              "status": "ACTIVE",
              "utm": {
                  "source": "email",
                  "medium": "newsletter",
                  "campaign": "external-campaign"
              },
              "tactic": "NEWSLETTER",
              "marketingChannelType": "EMAIL"
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
    mutation marketingActivityUpsertExternal($input: MarketingActivityUpsertExternalInput!) {
      marketingActivityUpsertExternal(input: $input) {
        marketingActivity {
          id
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "remoteId": "A unique identifier",
      "title": "New Title",
      "remoteUrl": "https://example.com",
      "status": "ACTIVE",
      "utm": {
        "source": "email",
        "medium": "newsletter",
        "campaign": "external-campaign"
      },
      "tactic": "NEWSLETTER",
      "marketingChannelType": "EMAIL"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation marketingActivityUpsertExternal($input: MarketingActivityUpsertExternalInput!) {
        marketingActivityUpsertExternal(input: $input) {
          marketingActivity {
            id
          }
        }
      }`,
      "variables": {
          "input": {
              "remoteId": "A unique identifier",
              "title": "New Title",
              "remoteUrl": "https://example.com",
              "status": "ACTIVE",
              "utm": {
                  "source": "email",
                  "medium": "newsletter",
                  "campaign": "external-campaign"
              },
              "tactic": "NEWSLETTER",
              "marketingChannelType": "EMAIL"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation marketingActivityUpsertExternal($input: MarketingActivityUpsertExternalInput!) {
    marketingActivityUpsertExternal(input: $input) {
      marketingActivity {
        id
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "remoteId": "A unique identifier",
      "title": "New Title",
      "remoteUrl": "https://example.com",
      "status": "ACTIVE",
      "utm": {
        "source": "email",
        "medium": "newsletter",
        "campaign": "external-campaign"
      },
      "tactic": "NEWSLETTER",
      "marketingChannelType": "EMAIL"
    }
  }'
  ```

  #### Response

  ```json
  {
    "marketingActivityUpsertExternal": {
      "marketingActivity": {
        "id": "gid://shopify/MarketingActivity/1063897336"
      }
    }
  }
  ```

* ### marketingActivityUpsertExternal reference
