---
title: shopResourceFeedbackCreate - GraphQL Admin
description: >-
  The `ResourceFeedback` object lets your app report the status of shops and
  their resources. For example, if

  your app is a marketplace channel, then you can use resource feedback to alert
  merchants that they need to connect their marketplace account by signing in.


  Resource feedback notifications are displayed to the merchant on the home
  screen of their Shopify admin, and in the product details view for any
  products that are published to your app.


  This resource should be used only in cases where you're describing steps that
  a merchant is required to complete. If your app offers optional or promotional
  set-up steps, or if it makes recommendations, then don't use resource feedback
  to let merchants know about them.


  ## Sending feedback on a shop


  You can send resource feedback on a shop to let the merchant know what steps
  they need to take to make sure that your app is set up correctly. Feedback can
  have one of two states: `requires_action` or `success`. You need to send a
  `requires_action` feedback request for each step that the merchant is required
  to complete.


  If there are multiple set-up steps that require merchant action, then send
  feedback with a state of `requires_action` as merchants complete prior steps.
  And to remove the feedback message from the Shopify admin, send a `success`
  feedback request.


  #### Important

  Sending feedback replaces previously sent feedback for the shop. Send a new
  `shopResourceFeedbackCreate` mutation to push the latest state of a shop or
  its resources to Shopify.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/shopResourceFeedbackCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/shopResourceFeedbackCreate.md
---

# shop​Resource​Feedback​Create

mutation

Requires `write_resource_feedbacks` access scope. Also: App must be configured to use the Storefront API or as a Sales Channel.

The `ResourceFeedback` object lets your app report the status of shops and their resources. For example, if your app is a marketplace channel, then you can use resource feedback to alert merchants that they need to connect their marketplace account by signing in.

Resource feedback notifications are displayed to the merchant on the home screen of their Shopify admin, and in the product details view for any products that are published to your app.

This resource should be used only in cases where you're describing steps that a merchant is required to complete. If your app offers optional or promotional set-up steps, or if it makes recommendations, then don't use resource feedback to let merchants know about them.

## Sending feedback on a shop

You can send resource feedback on a shop to let the merchant know what steps they need to take to make sure that your app is set up correctly. Feedback can have one of two states: `requires_action` or `success`. You need to send a `requires_action` feedback request for each step that the merchant is required to complete.

If there are multiple set-up steps that require merchant action, then send feedback with a state of `requires_action` as merchants complete prior steps. And to remove the feedback message from the Shopify admin, send a `success` feedback request.

#### Important

Sending feedback replaces previously sent feedback for the shop. Send a new `shopResourceFeedbackCreate` mutation to push the latest state of a shop or its resources to Shopify.

## Arguments

* input

  [Resource​Feedback​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ResourceFeedbackCreateInput)

  required

  The fields required to create shop feedback.

***

## Shop​Resource​Feedback​Create​Payload returns

* feedback

  [App​Feedback](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppFeedback)

  The shop feedback that's created.

* user​Errors

  [\[Shop​Resource​Feedback​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopResourceFeedbackCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a new ResourceFeedback

  #### Query

  ```graphql
  mutation ShopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
    shopResourceFeedbackCreate(input: $input) {
      feedback {
        messages {
          message
        }
        feedbackGeneratedAt
        state
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
    "input": {
      "messages": [
        "is not connected. Connect your account to use this sales channel."
      ],
      "state": "REQUIRES_ACTION",
      "feedbackGeneratedAt": "2024-12-05T14:05:02.351662Z"
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
  "query": "mutation ShopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) { shopResourceFeedbackCreate(input: $input) { feedback { messages { message } feedbackGeneratedAt state } userErrors { field message } } }",
   "variables": {
      "input": {
        "messages": [
          "is not connected. Connect your account to use this sales channel."
        ],
        "state": "REQUIRES_ACTION",
        "feedbackGeneratedAt": "2024-12-05T14:05:02.351662Z"
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
    mutation ShopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
      shopResourceFeedbackCreate(input: $input) {
        feedback {
          messages {
            message
          }
          feedbackGeneratedAt
          state
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "messages": [
                  "is not connected. Connect your account to use this sales channel."
              ],
              "state": "REQUIRES_ACTION",
              "feedbackGeneratedAt": "2024-12-05T14:05:02.351662Z"
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
    mutation ShopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
      shopResourceFeedbackCreate(input: $input) {
        feedback {
          messages {
            message
          }
          feedbackGeneratedAt
          state
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "messages": [
        "is not connected. Connect your account to use this sales channel."
      ],
      "state": "REQUIRES_ACTION",
      "feedbackGeneratedAt": "2024-12-05T14:05:02.351662Z"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation ShopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
        shopResourceFeedbackCreate(input: $input) {
          feedback {
            messages {
              message
            }
            feedbackGeneratedAt
            state
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "messages": [
                  "is not connected. Connect your account to use this sales channel."
              ],
              "state": "REQUIRES_ACTION",
              "feedbackGeneratedAt": "2024-12-05T14:05:02.351662Z"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation ShopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
    shopResourceFeedbackCreate(input: $input) {
      feedback {
        messages {
          message
        }
        feedbackGeneratedAt
        state
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "messages": [
        "is not connected. Connect your account to use this sales channel."
      ],
      "state": "REQUIRES_ACTION",
      "feedbackGeneratedAt": "2024-12-05T14:05:02.351662Z"
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopResourceFeedbackCreate": {
      "feedback": {
        "messages": [
          {
            "message": "Generic Channel is not connected. Connect your account to use this sales channel."
          }
        ],
        "feedbackGeneratedAt": "2024-12-05T14:05:02Z",
        "state": "REQUIRES_ACTION"
      },
      "userErrors": []
    }
  }
  ```

* ### Create a shop feedback record indicating a problem specific to your app

  #### Query

  ```graphql
  mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
    shopResourceFeedbackCreate(input: $input) {
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
    "input": {
      "messages": [
        "is not connected. Connect your account to use this sales channel."
      ],
      "state": "REQUIRES_ACTION",
      "feedbackGeneratedAt": "2024-12-05T14:05:00.688444Z"
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
  "query": "mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) { shopResourceFeedbackCreate(input: $input) { userErrors { field message } } }",
   "variables": {
      "input": {
        "messages": [
          "is not connected. Connect your account to use this sales channel."
        ],
        "state": "REQUIRES_ACTION",
        "feedbackGeneratedAt": "2024-12-05T14:05:00.688444Z"
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
    mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
      shopResourceFeedbackCreate(input: $input) {
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "messages": [
                  "is not connected. Connect your account to use this sales channel."
              ],
              "state": "REQUIRES_ACTION",
              "feedbackGeneratedAt": "2024-12-05T14:05:00.688444Z"
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
    mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
      shopResourceFeedbackCreate(input: $input) {
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "messages": [
        "is not connected. Connect your account to use this sales channel."
      ],
      "state": "REQUIRES_ACTION",
      "feedbackGeneratedAt": "2024-12-05T14:05:00.688444Z"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
        shopResourceFeedbackCreate(input: $input) {
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "messages": [
                  "is not connected. Connect your account to use this sales channel."
              ],
              "state": "REQUIRES_ACTION",
              "feedbackGeneratedAt": "2024-12-05T14:05:00.688444Z"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
    shopResourceFeedbackCreate(input: $input) {
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "messages": [
        "is not connected. Connect your account to use this sales channel."
      ],
      "state": "REQUIRES_ACTION",
      "feedbackGeneratedAt": "2024-12-05T14:05:00.688444Z"
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopResourceFeedbackCreate": {
      "userErrors": []
    }
  }
  ```

* ### Create a shop feedback record indicating the shop is usable by your app

  #### Query

  ```graphql
  mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
    shopResourceFeedbackCreate(input: $input) {
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
    "input": {
      "state": "ACCEPTED",
      "feedbackGeneratedAt": "2024-12-05T14:05:01.601550Z"
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
  "query": "mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) { shopResourceFeedbackCreate(input: $input) { userErrors { field message } } }",
   "variables": {
      "input": {
        "state": "ACCEPTED",
        "feedbackGeneratedAt": "2024-12-05T14:05:01.601550Z"
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
    mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
      shopResourceFeedbackCreate(input: $input) {
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "state": "ACCEPTED",
              "feedbackGeneratedAt": "2024-12-05T14:05:01.601550Z"
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
    mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
      shopResourceFeedbackCreate(input: $input) {
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "state": "ACCEPTED",
      "feedbackGeneratedAt": "2024-12-05T14:05:01.601550Z"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
        shopResourceFeedbackCreate(input: $input) {
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "state": "ACCEPTED",
              "feedbackGeneratedAt": "2024-12-05T14:05:01.601550Z"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
    shopResourceFeedbackCreate(input: $input) {
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "state": "ACCEPTED",
      "feedbackGeneratedAt": "2024-12-05T14:05:01.601550Z"
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopResourceFeedbackCreate": {
      "userErrors": []
    }
  }
  ```

* ### Sending an invalid feedback payload returns an error

  #### Query

  ```graphql
  mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
    shopResourceFeedbackCreate(input: $input) {
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
    "input": {
      "state": "FOOBAR",
      "feedbackGeneratedAt": "2024-12-05T14:05:01.831106Z"
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
  "query": "mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) { shopResourceFeedbackCreate(input: $input) { userErrors { field message } } }",
   "variables": {
      "input": {
        "state": "FOOBAR",
        "feedbackGeneratedAt": "2024-12-05T14:05:01.831106Z"
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
    mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
      shopResourceFeedbackCreate(input: $input) {
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "state": "FOOBAR",
              "feedbackGeneratedAt": "2024-12-05T14:05:01.831106Z"
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
    mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
      shopResourceFeedbackCreate(input: $input) {
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "state": "FOOBAR",
      "feedbackGeneratedAt": "2024-12-05T14:05:01.831106Z"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
        shopResourceFeedbackCreate(input: $input) {
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "state": "FOOBAR",
              "feedbackGeneratedAt": "2024-12-05T14:05:01.831106Z"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
    shopResourceFeedbackCreate(input: $input) {
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "state": "FOOBAR",
      "feedbackGeneratedAt": "2024-12-05T14:05:01.831106Z"
    }
  }'
  ```

* ### Sending outdated feedback (previous feedback payload has a greater resource\_updated\_at value) returns an error

  #### Query

  ```graphql
  mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
    shopResourceFeedbackCreate(input: $input) {
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
    "input": {
      "messages": [
        "is not connected. Connect your account to use this sales channel."
      ],
      "state": "REQUIRES_ACTION",
      "feedbackGeneratedAt": "1998-06-07T10:00:00Z"
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
  "query": "mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) { shopResourceFeedbackCreate(input: $input) { userErrors { field message } } }",
   "variables": {
      "input": {
        "messages": [
          "is not connected. Connect your account to use this sales channel."
        ],
        "state": "REQUIRES_ACTION",
        "feedbackGeneratedAt": "1998-06-07T10:00:00Z"
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
    mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
      shopResourceFeedbackCreate(input: $input) {
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "messages": [
                  "is not connected. Connect your account to use this sales channel."
              ],
              "state": "REQUIRES_ACTION",
              "feedbackGeneratedAt": "1998-06-07T10:00:00Z"
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
    mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
      shopResourceFeedbackCreate(input: $input) {
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "messages": [
        "is not connected. Connect your account to use this sales channel."
      ],
      "state": "REQUIRES_ACTION",
      "feedbackGeneratedAt": "1998-06-07T10:00:00Z"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
        shopResourceFeedbackCreate(input: $input) {
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "messages": [
                  "is not connected. Connect your account to use this sales channel."
              ],
              "state": "REQUIRES_ACTION",
              "feedbackGeneratedAt": "1998-06-07T10:00:00Z"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation shopResourceFeedbackCreate($input: ResourceFeedbackCreateInput!) {
    shopResourceFeedbackCreate(input: $input) {
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "messages": [
        "is not connected. Connect your account to use this sales channel."
      ],
      "state": "REQUIRES_ACTION",
      "feedbackGeneratedAt": "1998-06-07T10:00:00Z"
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopResourceFeedbackCreate": {
      "userErrors": [
        {
          "field": [
            "input"
          ],
          "message": "Feedback for a future release of this resource was already accepted."
        }
      ]
    }
  }
  ```

* ### shopResourceFeedbackCreate reference
