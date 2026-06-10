---
title: orderInvoiceSend - GraphQL Admin
description: >-
  Sends an email invoice for an
  [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order).


  You can customize the email recipient, sender, and subject line using the
  [`email`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderInvoiceSend#arguments-email)
  argument.


  > Note:

  > Use store or staff account email addresses for the
  [`from`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderInvoiceSend#arguments-email.fields.from)
  and
  [`bcc`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderInvoiceSend#arguments-email.fields.bcc)
  input fields.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderInvoiceSend'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderInvoiceSend.md
---

# order​Invoice​Send

mutation

Requires `write_orders` access scope. Also: The user must have access to orders and manage orders information.

Sends an email invoice for an [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order).

You can customize the email recipient, sender, and subject line using the [`email`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderInvoiceSend#arguments-email) argument.

***

**Note:** Use store or staff account email addresses for the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderInvoiceSend#arguments-email.fields.from">\<code>from\</code>\</a> and \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderInvoiceSend#arguments-email.fields.bcc">\<code>bcc\</code>\</a> input fields.

***

## Arguments

* email

  [Email​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/EmailInput)

  The email input fields for the order invoice. The `bcc` and `from` fields should be store or staff account emails.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The order associated with the invoice.

***

## Order​Invoice​Send​Payload returns

* order

  [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

  The order associated with the invoice email.

* user​Errors

  [\[Order​Invoice​Send​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderInvoiceSendUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Send invoice

  #### Description

  Send an order invoice to a customer.

  #### Query

  ```graphql
  mutation OrderInvoiceSend($orderId: ID!, $email: EmailInput) {
    orderInvoiceSend(id: $orderId, email: $email) {
      order {
        id
      }
      userErrors {
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "orderId": "gid://shopify/Order/17181286",
    "email": {
      "to": "test@example.net",
      "from": "Sales Modyl <salesmodel@example.com>",
      "subject": "Invoice #1001",
      "customMessage": "Thank you for your order"
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
  "query": "mutation OrderInvoiceSend($orderId: ID!, $email: EmailInput) { orderInvoiceSend(id: $orderId, email: $email) { order { id } userErrors { message } } }",
   "variables": {
      "orderId": "gid://shopify/Order/17181286",
      "email": {
        "to": "test@example.net",
        "from": "Sales Modyl <salesmodel@example.com>",
        "subject": "Invoice #1001",
        "customMessage": "Thank you for your order"
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
    mutation OrderInvoiceSend($orderId: ID!, $email: EmailInput) {
      orderInvoiceSend(id: $orderId, email: $email) {
        order {
          id
        }
        userErrors {
          message
        }
      }
    }`,
    {
      variables: {
          "orderId": "gid://shopify/Order/17181286",
          "email": {
              "to": "test@example.net",
              "from": "Sales Modyl <salesmodel@example.com>",
              "subject": "Invoice #1001",
              "customMessage": "Thank you for your order"
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
    mutation OrderInvoiceSend($orderId: ID!, $email: EmailInput) {
      orderInvoiceSend(id: $orderId, email: $email) {
        order {
          id
        }
        userErrors {
          message
        }
      }
    }
  QUERY

  variables = {
    "orderId": "gid://shopify/Order/17181286",
    "email": {
      "to": "test@example.net",
      "from": "Sales Modyl <salesmodel@example.com>",
      "subject": "Invoice #1001",
      "customMessage": "Thank you for your order"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation OrderInvoiceSend($orderId: ID!, $email: EmailInput) {
        orderInvoiceSend(id: $orderId, email: $email) {
          order {
            id
          }
          userErrors {
            message
          }
        }
      }`,
      "variables": {
          "orderId": "gid://shopify/Order/17181286",
          "email": {
              "to": "test@example.net",
              "from": "Sales Modyl <salesmodel@example.com>",
              "subject": "Invoice #1001",
              "customMessage": "Thank you for your order"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation OrderInvoiceSend($orderId: ID!, $email: EmailInput) {
    orderInvoiceSend(id: $orderId, email: $email) {
      order {
        id
      }
      userErrors {
        message
      }
    }
  }' \
  --variables \
  '{
    "orderId": "gid://shopify/Order/17181286",
    "email": {
      "to": "test@example.net",
      "from": "Sales Modyl <salesmodel@example.com>",
      "subject": "Invoice #1001",
      "customMessage": "Thank you for your order"
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderInvoiceSend": {
      "order": {
        "id": "gid://shopify/Order/17181286"
      },
      "userErrors": []
    }
  }
  ```

* ### orderInvoiceSend reference
