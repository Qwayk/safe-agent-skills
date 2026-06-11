---
title: paymentReminderSend - GraphQL Admin
description: Sends an email payment reminder for a payment schedule.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentReminderSend
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentReminderSend.md
---

# payment​Reminder​Send

mutation

Requires `write_orders` access scope.

Sends an email payment reminder for a payment schedule.

## Arguments

* payment​Schedule​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The payment schedule id associated with the reminder.

***

## Payment​Reminder​Send​Payload returns

* success

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Whether the payment reminder email was successfully sent.

* user​Errors

  [\[Payment​Reminder​Send​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentReminderSendUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Send a payment reminder

  #### Description

  Send a payment reminder email to a customer.

  #### Query

  ```graphql
  mutation paymentReminderSend($paymentScheduleId: ID!) {
    paymentReminderSend(paymentScheduleId: $paymentScheduleId) {
      success
      userErrors {
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "paymentScheduleId": "gid://shopify/PaymentSchedule/864539144"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation paymentReminderSend($paymentScheduleId: ID!) { paymentReminderSend(paymentScheduleId: $paymentScheduleId) { success userErrors { message } } }",
   "variables": {
      "paymentScheduleId": "gid://shopify/PaymentSchedule/864539144"
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
    mutation paymentReminderSend($paymentScheduleId: ID!) {
      paymentReminderSend(paymentScheduleId: $paymentScheduleId) {
        success
        userErrors {
          message
        }
      }
    }`,
    {
      variables: {
          "paymentScheduleId": "gid://shopify/PaymentSchedule/864539144"
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
    mutation paymentReminderSend($paymentScheduleId: ID!) {
      paymentReminderSend(paymentScheduleId: $paymentScheduleId) {
        success
        userErrors {
          message
        }
      }
    }
  QUERY

  variables = {
    "paymentScheduleId": "gid://shopify/PaymentSchedule/864539144"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation paymentReminderSend($paymentScheduleId: ID!) {
        paymentReminderSend(paymentScheduleId: $paymentScheduleId) {
          success
          userErrors {
            message
          }
        }
      }`,
      "variables": {
          "paymentScheduleId": "gid://shopify/PaymentSchedule/864539144"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation paymentReminderSend($paymentScheduleId: ID!) {
    paymentReminderSend(paymentScheduleId: $paymentScheduleId) {
      success
      userErrors {
        message
      }
    }
  }' \
  --variables \
  '{
    "paymentScheduleId": "gid://shopify/PaymentSchedule/864539144"
  }'
  ```

  #### Response

  ```json
  {
    "paymentReminderSend": {
      "success": true,
      "userErrors": []
    }
  }
  ```

* ### paymentReminderSend reference
