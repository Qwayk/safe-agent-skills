---
title: paymentTermsCreate - GraphQL Admin
description: >-
  Create payment terms on an order. To create payment terms on a draft order,
  use a draft order mutation and include the request with the `DraftOrderInput`.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentTermsCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentTermsCreate.md
---

# payment​Terms​Create

mutation

Requires `write_payment_terms` access scope. Also: The user must have access to orders or draft orders.

Create payment terms on an order. To create payment terms on a draft order, use a draft order mutation and include the request with the `DraftOrderInput`.

## Arguments

* payment​Terms​Attributes

  [Payment​Terms​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PaymentTermsCreateInput)

  required

  The attributes used to create the payment terms.

* reference​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  Specifies the reference orderId to add the payment terms for.

***

## Payment​Terms​Create​Payload returns

* payment​Terms

  [Payment​Terms](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTerms)

  The created payment terms.

* user​Errors

  [\[Payment​Terms​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTermsCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create due on receipt payment terms

  #### Description

  Create payment terms that indicate payment is due when the invoice is sent by the merchant.

  #### Query

  ```graphql
  mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
    paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
      paymentTerms {
        id
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
    "referenceId": "gid://shopify/Order/922426937",
    "paymentTermsAttributes": {
      "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/1"
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
  "query": "mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) { paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) { paymentTerms { id } userErrors { field message } } }",
   "variables": {
      "referenceId": "gid://shopify/Order/922426937",
      "paymentTermsAttributes": {
        "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/1"
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
    mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
      paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
        paymentTerms {
          id
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "referenceId": "gid://shopify/Order/922426937",
          "paymentTermsAttributes": {
              "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/1"
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
    mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
      paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
        paymentTerms {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "referenceId": "gid://shopify/Order/922426937",
    "paymentTermsAttributes": {
      "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/1"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
        paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
          paymentTerms {
            id
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "referenceId": "gid://shopify/Order/922426937",
          "paymentTermsAttributes": {
              "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/1"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
    paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
      paymentTerms {
        id
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "referenceId": "gid://shopify/Order/922426937",
    "paymentTermsAttributes": {
      "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/1"
    }
  }'
  ```

  #### Response

  ```json
  {
    "paymentTermsCreate": {
      "paymentTerms": {
        "id": "gid://shopify/PaymentTerms/1054663035"
      },
      "userErrors": []
    }
  }
  ```

* ### Create fixed payment terms

  #### Description

  Create payment terms that indicate payment is due on a fixed date.

  #### Query

  ```graphql
  mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
    paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
      paymentTerms {
        id
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
    "referenceId": "gid://shopify/Order/922426937",
    "paymentTermsAttributes": {
      "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/7",
      "paymentSchedules": [
        {
          "dueAt": "2022-06-13T22:35:23.311Z"
        }
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
  "query": "mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) { paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) { paymentTerms { id } userErrors { field message } } }",
   "variables": {
      "referenceId": "gid://shopify/Order/922426937",
      "paymentTermsAttributes": {
        "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/7",
        "paymentSchedules": [
          {
            "dueAt": "2022-06-13T22:35:23.311Z"
          }
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
    mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
      paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
        paymentTerms {
          id
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "referenceId": "gid://shopify/Order/922426937",
          "paymentTermsAttributes": {
              "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/7",
              "paymentSchedules": [
                  {
                      "dueAt": "2022-06-13T22:35:23.311Z"
                  }
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
    mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
      paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
        paymentTerms {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "referenceId": "gid://shopify/Order/922426937",
    "paymentTermsAttributes": {
      "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/7",
      "paymentSchedules": [
        {
          "dueAt": "2022-06-13T22:35:23.311Z"
        }
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
      "query": `mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
        paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
          paymentTerms {
            id
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "referenceId": "gid://shopify/Order/922426937",
          "paymentTermsAttributes": {
              "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/7",
              "paymentSchedules": [
                  {
                      "dueAt": "2022-06-13T22:35:23.311Z"
                  }
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
  'mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
    paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
      paymentTerms {
        id
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "referenceId": "gid://shopify/Order/922426937",
    "paymentTermsAttributes": {
      "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/7",
      "paymentSchedules": [
        {
          "dueAt": "2022-06-13T22:35:23.311Z"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "paymentTermsCreate": {
      "paymentTerms": {
        "id": "gid://shopify/PaymentTerms/1054663034"
      },
      "userErrors": []
    }
  }
  ```

* ### Create net payment terms

  #### Description

  Create payment terms that indicate payment is due a set number of days after the invoice is sent.

  #### Query

  ```graphql
  mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
    paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
      paymentTerms {
        id
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
    "referenceId": "gid://shopify/Order/922426937",
    "paymentTermsAttributes": {
      "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/2",
      "paymentSchedules": [
        {
          "issuedAt": "2022-06-13T22:30:18.019Z"
        }
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
  "query": "mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) { paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) { paymentTerms { id } userErrors { field message } } }",
   "variables": {
      "referenceId": "gid://shopify/Order/922426937",
      "paymentTermsAttributes": {
        "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/2",
        "paymentSchedules": [
          {
            "issuedAt": "2022-06-13T22:30:18.019Z"
          }
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
    mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
      paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
        paymentTerms {
          id
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "referenceId": "gid://shopify/Order/922426937",
          "paymentTermsAttributes": {
              "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/2",
              "paymentSchedules": [
                  {
                      "issuedAt": "2022-06-13T22:30:18.019Z"
                  }
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
    mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
      paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
        paymentTerms {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "referenceId": "gid://shopify/Order/922426937",
    "paymentTermsAttributes": {
      "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/2",
      "paymentSchedules": [
        {
          "issuedAt": "2022-06-13T22:30:18.019Z"
        }
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
      "query": `mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
        paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
          paymentTerms {
            id
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "referenceId": "gid://shopify/Order/922426937",
          "paymentTermsAttributes": {
              "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/2",
              "paymentSchedules": [
                  {
                      "issuedAt": "2022-06-13T22:30:18.019Z"
                  }
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
  'mutation PaymentTermsCreate($referenceId: ID!, $paymentTermsAttributes: PaymentTermsCreateInput!) {
    paymentTermsCreate(referenceId: $referenceId, paymentTermsAttributes: $paymentTermsAttributes) {
      paymentTerms {
        id
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "referenceId": "gid://shopify/Order/922426937",
    "paymentTermsAttributes": {
      "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/2",
      "paymentSchedules": [
        {
          "issuedAt": "2022-06-13T22:30:18.019Z"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "paymentTermsCreate": {
      "paymentTerms": {
        "id": "gid://shopify/PaymentTerms/1054663033"
      },
      "userErrors": []
    }
  }
  ```

* ### paymentTermsCreate reference
