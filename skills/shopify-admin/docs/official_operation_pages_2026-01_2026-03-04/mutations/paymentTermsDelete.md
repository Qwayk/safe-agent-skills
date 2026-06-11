---
title: paymentTermsDelete - GraphQL Admin
description: >-
  Delete payment terms for an order. To delete payment terms on a draft order,
  use a draft order mutation and include the request with the `DraftOrderInput`.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentTermsDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentTermsDelete.md
---

# payment​Terms​Delete

mutation

Requires `write_payment_terms` access scope. Also: User must have either orders or draft orders access according to the reference.

Delete payment terms for an order. To delete payment terms on a draft order, use a draft order mutation and include the request with the `DraftOrderInput`.

## Arguments

* input

  [Payment​Terms​Delete​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PaymentTermsDeleteInput)

  required

  The input fields used to delete the payment terms.

***

## Payment​Terms​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The deleted payment terms ID.

* user​Errors

  [\[Payment​Terms​Delete​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTermsDeleteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Delete payment terms

  #### Description

  Delete payment terms for an order.

  #### Query

  ```graphql
  mutation PaymentTermsDelete($input: PaymentTermsDeleteInput!) {
    paymentTermsDelete(input: $input) {
      deletedId
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
      "paymentTermsId": "gid://shopify/PaymentTerms/977822362"
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
  "query": "mutation PaymentTermsDelete($input: PaymentTermsDeleteInput!) { paymentTermsDelete(input: $input) { deletedId userErrors { field message } } }",
   "variables": {
      "input": {
        "paymentTermsId": "gid://shopify/PaymentTerms/977822362"
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
    mutation PaymentTermsDelete($input: PaymentTermsDeleteInput!) {
      paymentTermsDelete(input: $input) {
        deletedId
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "paymentTermsId": "gid://shopify/PaymentTerms/977822362"
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
    mutation PaymentTermsDelete($input: PaymentTermsDeleteInput!) {
      paymentTermsDelete(input: $input) {
        deletedId
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "paymentTermsId": "gid://shopify/PaymentTerms/977822362"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation PaymentTermsDelete($input: PaymentTermsDeleteInput!) {
        paymentTermsDelete(input: $input) {
          deletedId
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "paymentTermsId": "gid://shopify/PaymentTerms/977822362"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation PaymentTermsDelete($input: PaymentTermsDeleteInput!) {
    paymentTermsDelete(input: $input) {
      deletedId
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "paymentTermsId": "gid://shopify/PaymentTerms/977822362"
    }
  }'
  ```

  #### Response

  ```json
  {
    "paymentTermsDelete": {
      "deletedId": "gid://shopify/PaymentTerms/977822362",
      "userErrors": []
    }
  }
  ```

* ### paymentTermsDelete reference
