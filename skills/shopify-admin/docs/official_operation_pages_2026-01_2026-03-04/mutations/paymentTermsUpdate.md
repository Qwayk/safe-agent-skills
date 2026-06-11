---
title: paymentTermsUpdate - GraphQL Admin
description: >-
  Update payment terms on an order. To update payment terms on a draft order,
  use a draft order mutation and include the request with the `DraftOrderInput`.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentTermsUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentTermsUpdate.md
---

# payment​Terms​Update

mutation

Requires `write_payment_terms` access scope. Also: User must have either orders or draft orders access according to the reference.

Update payment terms on an order. To update payment terms on a draft order, use a draft order mutation and include the request with the `DraftOrderInput`.

## Arguments

* input

  [Payment​Terms​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PaymentTermsUpdateInput)

  required

  The input fields used to update the payment terms.

***

## Payment​Terms​Update​Payload returns

* payment​Terms

  [Payment​Terms](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTerms)

  The updated payment terms.

* user​Errors

  [\[Payment​Terms​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTermsUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update payment terms date

  #### Description

  Update the due date for fixed date payment terms.

  #### Query

  ```graphql
  mutation PaymentTermsUpdate($input: PaymentTermsUpdateInput!) {
    paymentTermsUpdate(input: $input) {
      paymentTerms {
        id
      }
      userErrors {
        code
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
      "paymentTermsId": "gid://shopify/PaymentTerms/977822362",
      "paymentTermsAttributes": {
        "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/7",
        "paymentSchedules": [
          {
            "dueAt": "2022-06-13T22:35:23.311Z"
          }
        ]
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
  "query": "mutation PaymentTermsUpdate($input: PaymentTermsUpdateInput!) { paymentTermsUpdate(input: $input) { paymentTerms { id } userErrors { code field message } } }",
   "variables": {
      "input": {
        "paymentTermsId": "gid://shopify/PaymentTerms/977822362",
        "paymentTermsAttributes": {
          "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/7",
          "paymentSchedules": [
            {
              "dueAt": "2022-06-13T22:35:23.311Z"
            }
          ]
        }
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
    mutation PaymentTermsUpdate($input: PaymentTermsUpdateInput!) {
      paymentTermsUpdate(input: $input) {
        paymentTerms {
          id
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "paymentTermsId": "gid://shopify/PaymentTerms/977822362",
              "paymentTermsAttributes": {
                  "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/7",
                  "paymentSchedules": [
                      {
                          "dueAt": "2022-06-13T22:35:23.311Z"
                      }
                  ]
              }
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
    mutation PaymentTermsUpdate($input: PaymentTermsUpdateInput!) {
      paymentTermsUpdate(input: $input) {
        paymentTerms {
          id
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "paymentTermsId": "gid://shopify/PaymentTerms/977822362",
      "paymentTermsAttributes": {
        "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/7",
        "paymentSchedules": [
          {
            "dueAt": "2022-06-13T22:35:23.311Z"
          }
        ]
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation PaymentTermsUpdate($input: PaymentTermsUpdateInput!) {
        paymentTermsUpdate(input: $input) {
          paymentTerms {
            id
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "paymentTermsId": "gid://shopify/PaymentTerms/977822362",
              "paymentTermsAttributes": {
                  "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/7",
                  "paymentSchedules": [
                      {
                          "dueAt": "2022-06-13T22:35:23.311Z"
                      }
                  ]
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation PaymentTermsUpdate($input: PaymentTermsUpdateInput!) {
    paymentTermsUpdate(input: $input) {
      paymentTerms {
        id
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "paymentTermsId": "gid://shopify/PaymentTerms/977822362",
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

  #### Response

  ```json
  {
    "paymentTermsUpdate": {
      "paymentTerms": {
        "id": "gid://shopify/PaymentTerms/977822362"
      },
      "userErrors": []
    }
  }
  ```

* ### Update payment terms type

  #### Description

  Change payment terms to net terms.

  #### Query

  ```graphql
  mutation PaymentTermsUpdate($input: PaymentTermsUpdateInput!) {
    paymentTermsUpdate(input: $input) {
      paymentTerms {
        id
      }
      userErrors {
        code
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
      "paymentTermsId": "gid://shopify/PaymentTerms/977822362",
      "paymentTermsAttributes": {
        "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/2",
        "paymentSchedules": [
          {
            "issuedAt": "2022-06-13T22:35:23.311Z"
          }
        ]
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
  "query": "mutation PaymentTermsUpdate($input: PaymentTermsUpdateInput!) { paymentTermsUpdate(input: $input) { paymentTerms { id } userErrors { code field message } } }",
   "variables": {
      "input": {
        "paymentTermsId": "gid://shopify/PaymentTerms/977822362",
        "paymentTermsAttributes": {
          "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/2",
          "paymentSchedules": [
            {
              "issuedAt": "2022-06-13T22:35:23.311Z"
            }
          ]
        }
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
    mutation PaymentTermsUpdate($input: PaymentTermsUpdateInput!) {
      paymentTermsUpdate(input: $input) {
        paymentTerms {
          id
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "paymentTermsId": "gid://shopify/PaymentTerms/977822362",
              "paymentTermsAttributes": {
                  "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/2",
                  "paymentSchedules": [
                      {
                          "issuedAt": "2022-06-13T22:35:23.311Z"
                      }
                  ]
              }
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
    mutation PaymentTermsUpdate($input: PaymentTermsUpdateInput!) {
      paymentTermsUpdate(input: $input) {
        paymentTerms {
          id
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "paymentTermsId": "gid://shopify/PaymentTerms/977822362",
      "paymentTermsAttributes": {
        "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/2",
        "paymentSchedules": [
          {
            "issuedAt": "2022-06-13T22:35:23.311Z"
          }
        ]
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation PaymentTermsUpdate($input: PaymentTermsUpdateInput!) {
        paymentTermsUpdate(input: $input) {
          paymentTerms {
            id
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "paymentTermsId": "gid://shopify/PaymentTerms/977822362",
              "paymentTermsAttributes": {
                  "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/2",
                  "paymentSchedules": [
                      {
                          "issuedAt": "2022-06-13T22:35:23.311Z"
                      }
                  ]
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation PaymentTermsUpdate($input: PaymentTermsUpdateInput!) {
    paymentTermsUpdate(input: $input) {
      paymentTerms {
        id
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "paymentTermsId": "gid://shopify/PaymentTerms/977822362",
      "paymentTermsAttributes": {
        "paymentTermsTemplateId": "gid://shopify/PaymentTermsTemplate/2",
        "paymentSchedules": [
          {
            "issuedAt": "2022-06-13T22:35:23.311Z"
          }
        ]
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "paymentTermsUpdate": {
      "paymentTerms": {
        "id": "gid://shopify/PaymentTerms/977822362"
      },
      "userErrors": []
    }
  }
  ```

* ### paymentTermsUpdate reference
