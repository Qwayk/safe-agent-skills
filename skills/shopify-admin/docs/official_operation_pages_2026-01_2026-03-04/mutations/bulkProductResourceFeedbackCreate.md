---
title: bulkProductResourceFeedbackCreate - GraphQL Admin
description: Creates product feedback for multiple products.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/bulkProductResourceFeedbackCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/bulkProductResourceFeedbackCreate.md
---

# bulk​Product​Resource​Feedback​Create

mutation

Requires `write_resource_feedbacks` access scope. Also: App must be configured to use the Storefront API or as a Sales Channel.

Creates product feedback for multiple products.

## Arguments

* feedback​Input

  [\[Product​Resource​Feedback​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductResourceFeedbackInput)

  required

  An array of inputs to create the feedback. Limited to 50.

***

## Bulk​Product​Resource​Feedback​Create​Payload returns

* feedback

  [\[Product​Resource​Feedback!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductResourceFeedback)

  The feedback that's created.

* user​Errors

  [\[Bulk​Product​Resource​Feedback​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BulkProductResourceFeedbackCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a feedback record indicating the product is usable by your app

  #### Description

  Indicates that the app does not have any outstanding issues with this product.

  #### Query

  ```graphql
  mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
    bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
      userErrors {
        field
        message
      }
      feedback {
        productId
        state
        feedbackGeneratedAt
        productUpdatedAt
        messages
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "feedbackInput": {
      "productId": "gid://shopify/Product/172561227",
      "state": "ACCEPTED",
      "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
      "productUpdatedAt": "2021-04-28T16:00:00Z",
      "messages": []
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
  "query": "mutation($feedbackInput: [ProductResourceFeedbackInput!]!) { bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) { userErrors { field message } feedback { productId state feedbackGeneratedAt productUpdatedAt messages } } }",
   "variables": {
      "feedbackInput": {
        "productId": "gid://shopify/Product/172561227",
        "state": "ACCEPTED",
        "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
        "productUpdatedAt": "2021-04-28T16:00:00Z",
        "messages": []
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
    mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
      bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
        userErrors {
          field
          message
        }
        feedback {
          productId
          state
          feedbackGeneratedAt
          productUpdatedAt
          messages
        }
      }
    }`,
    {
      variables: {
          "feedbackInput": {
              "productId": "gid://shopify/Product/172561227",
              "state": "ACCEPTED",
              "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
              "productUpdatedAt": "2021-04-28T16:00:00Z",
              "messages": []
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
    mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
      bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
        userErrors {
          field
          message
        }
        feedback {
          productId
          state
          feedbackGeneratedAt
          productUpdatedAt
          messages
        }
      }
    }
  QUERY

  variables = {
    "feedbackInput": {
      "productId": "gid://shopify/Product/172561227",
      "state": "ACCEPTED",
      "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
      "productUpdatedAt": "2021-04-28T16:00:00Z",
      "messages": []
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
        bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
          userErrors {
            field
            message
          }
          feedback {
            productId
            state
            feedbackGeneratedAt
            productUpdatedAt
            messages
          }
        }
      }`,
      "variables": {
          "feedbackInput": {
              "productId": "gid://shopify/Product/172561227",
              "state": "ACCEPTED",
              "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
              "productUpdatedAt": "2021-04-28T16:00:00Z",
              "messages": []
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
    bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
      userErrors {
        field
        message
      }
      feedback {
        productId
        state
        feedbackGeneratedAt
        productUpdatedAt
        messages
      }
    }
  }' \
  --variables \
  '{
    "feedbackInput": {
      "productId": "gid://shopify/Product/172561227",
      "state": "ACCEPTED",
      "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
      "productUpdatedAt": "2021-04-28T16:00:00Z",
      "messages": []
    }
  }'
  ```

  #### Response

  ```json
  {
    "bulkProductResourceFeedbackCreate": {
      "userErrors": [],
      "feedback": [
        {
          "productId": "gid://shopify/Product/172561227",
          "state": "ACCEPTED",
          "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
          "productUpdatedAt": "2021-04-28T16:00:00Z",
          "messages": []
        }
      ]
    }
  }
  ```

* ### Create a new Product ResourceFeedback

  #### Query

  ```graphql
  mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
    bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
      userErrors {
        field
        message
      }
      feedback {
        productId
        state
        feedbackGeneratedAt
        productUpdatedAt
        messages
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "feedbackInput": [
      {
        "productId": "gid://shopify/Product/172561227",
        "state": "REQUIRES_ACTION",
        "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
        "productUpdatedAt": "2021-04-28T16:00:00Z",
        "messages": [
          "Needs a description."
        ]
      },
      {
        "productId": "gid://shopify/Product/788638954",
        "state": "REQUIRES_ACTION",
        "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
        "productUpdatedAt": "2021-04-28T16:00:00Z",
        "messages": [
          "Needs an image."
        ]
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation($feedbackInput: [ProductResourceFeedbackInput!]!) { bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) { userErrors { field message } feedback { productId state feedbackGeneratedAt productUpdatedAt messages } } }",
   "variables": {
      "feedbackInput": [
        {
          "productId": "gid://shopify/Product/172561227",
          "state": "REQUIRES_ACTION",
          "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
          "productUpdatedAt": "2021-04-28T16:00:00Z",
          "messages": [
            "Needs a description."
          ]
        },
        {
          "productId": "gid://shopify/Product/788638954",
          "state": "REQUIRES_ACTION",
          "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
          "productUpdatedAt": "2021-04-28T16:00:00Z",
          "messages": [
            "Needs an image."
          ]
        }
      ]
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
    mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
      bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
        userErrors {
          field
          message
        }
        feedback {
          productId
          state
          feedbackGeneratedAt
          productUpdatedAt
          messages
        }
      }
    }`,
    {
      variables: {
          "feedbackInput": [
              {
                  "productId": "gid://shopify/Product/172561227",
                  "state": "REQUIRES_ACTION",
                  "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
                  "productUpdatedAt": "2021-04-28T16:00:00Z",
                  "messages": [
                      "Needs a description."
                  ]
              },
              {
                  "productId": "gid://shopify/Product/788638954",
                  "state": "REQUIRES_ACTION",
                  "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
                  "productUpdatedAt": "2021-04-28T16:00:00Z",
                  "messages": [
                      "Needs an image."
                  ]
              }
          ]
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
    mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
      bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
        userErrors {
          field
          message
        }
        feedback {
          productId
          state
          feedbackGeneratedAt
          productUpdatedAt
          messages
        }
      }
    }
  QUERY

  variables = {
    "feedbackInput": [
      {
        "productId": "gid://shopify/Product/172561227",
        "state": "REQUIRES_ACTION",
        "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
        "productUpdatedAt": "2021-04-28T16:00:00Z",
        "messages": [
          "Needs a description."
        ]
      },
      {
        "productId": "gid://shopify/Product/788638954",
        "state": "REQUIRES_ACTION",
        "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
        "productUpdatedAt": "2021-04-28T16:00:00Z",
        "messages": [
          "Needs an image."
        ]
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
        bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
          userErrors {
            field
            message
          }
          feedback {
            productId
            state
            feedbackGeneratedAt
            productUpdatedAt
            messages
          }
        }
      }`,
      "variables": {
          "feedbackInput": [
              {
                  "productId": "gid://shopify/Product/172561227",
                  "state": "REQUIRES_ACTION",
                  "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
                  "productUpdatedAt": "2021-04-28T16:00:00Z",
                  "messages": [
                      "Needs a description."
                  ]
              },
              {
                  "productId": "gid://shopify/Product/788638954",
                  "state": "REQUIRES_ACTION",
                  "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
                  "productUpdatedAt": "2021-04-28T16:00:00Z",
                  "messages": [
                      "Needs an image."
                  ]
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
    bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
      userErrors {
        field
        message
      }
      feedback {
        productId
        state
        feedbackGeneratedAt
        productUpdatedAt
        messages
      }
    }
  }' \
  --variables \
  '{
    "feedbackInput": [
      {
        "productId": "gid://shopify/Product/172561227",
        "state": "REQUIRES_ACTION",
        "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
        "productUpdatedAt": "2021-04-28T16:00:00Z",
        "messages": [
          "Needs a description."
        ]
      },
      {
        "productId": "gid://shopify/Product/788638954",
        "state": "REQUIRES_ACTION",
        "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
        "productUpdatedAt": "2021-04-28T16:00:00Z",
        "messages": [
          "Needs an image."
        ]
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "bulkProductResourceFeedbackCreate": {
      "userErrors": [],
      "feedback": [
        {
          "productId": "gid://shopify/Product/172561227",
          "state": "REQUIRES_ACTION",
          "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
          "productUpdatedAt": "2021-04-28T16:00:00Z",
          "messages": [
            "Needs a description."
          ]
        },
        {
          "productId": "gid://shopify/Product/788638954",
          "state": "REQUIRES_ACTION",
          "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
          "productUpdatedAt": "2021-04-28T16:00:00Z",
          "messages": [
            "Needs an image."
          ]
        }
      ]
    }
  }
  ```

* ### Error response

  #### Description

  Sending outdated feedback (previous feedback payload has a greater resource\_updated\_at value) returns an error

  #### Query

  ```graphql
  mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
    bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
      userErrors {
        field
        message
      }
      feedback {
        productId
        state
        messages
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "feedbackInput": {
      "productId": "gid://shopify/Product/172561227",
      "state": "REQUIRES_ACTION",
      "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
      "productUpdatedAt": "2021-04-28T16:00:00Z",
      "messages": [
        "Needs a description."
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
  "query": "mutation($feedbackInput: [ProductResourceFeedbackInput!]!) { bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) { userErrors { field message } feedback { productId state messages } } }",
   "variables": {
      "feedbackInput": {
        "productId": "gid://shopify/Product/172561227",
        "state": "REQUIRES_ACTION",
        "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
        "productUpdatedAt": "2021-04-28T16:00:00Z",
        "messages": [
          "Needs a description."
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
    mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
      bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
        userErrors {
          field
          message
        }
        feedback {
          productId
          state
          messages
        }
      }
    }`,
    {
      variables: {
          "feedbackInput": {
              "productId": "gid://shopify/Product/172561227",
              "state": "REQUIRES_ACTION",
              "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
              "productUpdatedAt": "2021-04-28T16:00:00Z",
              "messages": [
                  "Needs a description."
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
    mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
      bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
        userErrors {
          field
          message
        }
        feedback {
          productId
          state
          messages
        }
      }
    }
  QUERY

  variables = {
    "feedbackInput": {
      "productId": "gid://shopify/Product/172561227",
      "state": "REQUIRES_ACTION",
      "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
      "productUpdatedAt": "2021-04-28T16:00:00Z",
      "messages": [
        "Needs a description."
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
      "query": `mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
        bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
          userErrors {
            field
            message
          }
          feedback {
            productId
            state
            messages
          }
        }
      }`,
      "variables": {
          "feedbackInput": {
              "productId": "gid://shopify/Product/172561227",
              "state": "REQUIRES_ACTION",
              "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
              "productUpdatedAt": "2021-04-28T16:00:00Z",
              "messages": [
                  "Needs a description."
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
  'mutation($feedbackInput: [ProductResourceFeedbackInput!]!) {
    bulkProductResourceFeedbackCreate(feedbackInput: $feedbackInput) {
      userErrors {
        field
        message
      }
      feedback {
        productId
        state
        messages
      }
    }
  }' \
  --variables \
  '{
    "feedbackInput": {
      "productId": "gid://shopify/Product/172561227",
      "state": "REQUIRES_ACTION",
      "feedbackGeneratedAt": "2021-05-01T23:00:00Z",
      "productUpdatedAt": "2021-04-28T16:00:00Z",
      "messages": [
        "Needs a description."
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "bulkProductResourceFeedbackCreate": {
      "userErrors": [
        {
          "field": [
            "feedbackInput",
            "0",
            "feedbackGeneratedAt"
          ],
          "message": "Feedback for a future release of this resource was already accepted."
        }
      ],
      "feedback": []
    }
  }
  ```

* ### bulkProductResourceFeedbackCreate reference
