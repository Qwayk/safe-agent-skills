---
title: orderClose - GraphQL Admin
description: >-
  Marks an open
  [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) as
  closed. A closed order is one where merchants fulfill or cancel all
  [`LineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem)
  objects and complete all financial transactions.


  Once closed, the order indicates that no further work is required. The order's
  [`closedAt`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order#field-closedAt)
  timestamp is set when this mutation completes successfully.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderClose'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderClose.md'
---

# order​Close

mutation

Requires `write_orders` access scope. Also: User needs manage\_orders\_information permission.

Marks an open [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) as closed. A closed order is one where merchants fulfill or cancel all [`LineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem) objects and complete all financial transactions.

Once closed, the order indicates that no further work is required. The order's [`closedAt`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order#field-closedAt) timestamp is set when this mutation completes successfully.

## Arguments

* input

  [Order​Close​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OrderCloseInput)

  required

  The input for the mutation.

***

## Order​Close​Payload returns

* order

  [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

  The closed order.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Close an order

  #### Query

  ```graphql
  mutation OrderClose($input: OrderCloseInput!) {
    orderClose(input: $input) {
      order {
        canMarkAsPaid
        cancelReason
        cancelledAt
        clientIp
        confirmed
        customer {
          displayName
          email
        }
        discountCodes
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
      "id": "gid://shopify/Order/148977776"
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
  "query": "mutation OrderClose($input: OrderCloseInput!) { orderClose(input: $input) { order { canMarkAsPaid cancelReason cancelledAt clientIp confirmed customer { displayName email } discountCodes } userErrors { field message } } }",
   "variables": {
      "input": {
        "id": "gid://shopify/Order/148977776"
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
    mutation OrderClose($input: OrderCloseInput!) {
      orderClose(input: $input) {
        order {
          canMarkAsPaid
          cancelReason
          cancelledAt
          clientIp
          confirmed
          customer {
            displayName
            email
          }
          discountCodes
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
              "id": "gid://shopify/Order/148977776"
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
    mutation OrderClose($input: OrderCloseInput!) {
      orderClose(input: $input) {
        order {
          canMarkAsPaid
          cancelReason
          cancelledAt
          clientIp
          confirmed
          customer {
            displayName
            email
          }
          discountCodes
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
      "id": "gid://shopify/Order/148977776"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation OrderClose($input: OrderCloseInput!) {
        orderClose(input: $input) {
          order {
            canMarkAsPaid
            cancelReason
            cancelledAt
            clientIp
            confirmed
            customer {
              displayName
              email
            }
            discountCodes
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "id": "gid://shopify/Order/148977776"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation OrderClose($input: OrderCloseInput!) {
    orderClose(input: $input) {
      order {
        canMarkAsPaid
        cancelReason
        cancelledAt
        clientIp
        confirmed
        customer {
          displayName
          email
        }
        discountCodes
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
      "id": "gid://shopify/Order/148977776"
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderClose": {
      "order": {
        "canMarkAsPaid": false,
        "cancelReason": null,
        "cancelledAt": null,
        "clientIp": "216.191.105.144",
        "confirmed": true,
        "customer": {
          "displayName": "Bob Bobsen",
          "email": "bob@example.com"
        },
        "discountCodes": []
      },
      "userErrors": []
    }
  }
  ```

* ### orderClose reference
