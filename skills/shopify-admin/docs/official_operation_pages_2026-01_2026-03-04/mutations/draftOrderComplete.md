---
title: draftOrderComplete - GraphQL Admin
description: >-
  Completes a [draft
  order](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder)
  and

  converts it into a [regular
  order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order).

  The order appears in the merchant's orders list, and the customer can be
  notified about their order.


  Use the `draftOrderComplete` mutation when a merchant is ready to finalize a
  draft order and create a real

  order in their store. The `draftOrderComplete` mutation also supports sales
  channel attribution for tracking

  order sources using the
  [`sourceName`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderComplete#arguments-sourceName)

  argument, [cart
  validation](https://shopify.dev/docs/apps/build/checkout/cart-checkout-validation)

  controls for app integrations, and detailed error reporting for failed
  completions.


  You can complete a draft order with different [payment
  scenarios](https://help.shopify.com/manual/fulfillment/managing-orders/payments):


  - Mark the order as paid immediately.

  - Set the order as payment pending using [payment
  terms](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTerms).

  - Specify a custom payment amount.

  - Select a specific payment gateway.


  > Note:

  > When completing a draft order, inventory is
  [reserved](https://shopify.dev/docs/apps/build/orders-fulfillment/inventory-management-apps#inventory-states)

  for the items in the order. This means the items will no longer be available
  for other customers to purchase.

  Make sure to verify inventory availability before completing the draft order.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderComplete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderComplete.md
---

# draft​Order​Complete

mutation

Requires `write_draft_orders` access scope. Also: The user must have access to mark as paid, or set payment terms.

Completes a [draft order](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder) and converts it into a [regular order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order). The order appears in the merchant's orders list, and the customer can be notified about their order.

Use the `draftOrderComplete` mutation when a merchant is ready to finalize a draft order and create a real order in their store. The `draftOrderComplete` mutation also supports sales channel attribution for tracking order sources using the [`sourceName`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderComplete#arguments-sourceName) argument, [cart validation](https://shopify.dev/docs/apps/build/checkout/cart-checkout-validation) controls for app integrations, and detailed error reporting for failed completions.

You can complete a draft order with different [payment scenarios](https://help.shopify.com/manual/fulfillment/managing-orders/payments):

* Mark the order as paid immediately.
* Set the order as payment pending using [payment terms](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTerms).
* Specify a custom payment amount.
* Select a specific payment gateway.

***

**Note:** When completing a draft order, inventory is \<a href="https://shopify.dev/docs/apps/build/orders-fulfillment/inventory-management-apps#inventory-states">reserved\</a> for the items in the order. This means the items will no longer be available for other customers to purchase. Make sure to verify inventory availability before completing the draft order.

***

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The draft order to complete.

* payment​Gateway​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The gateway for the completed draft order.

* source​Name

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A channel definition handle used for sales channel attribution.

* payment​Pending

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  DeprecatedDefault:false

***

## Draft​Order​Complete​Payload returns

* draft​Order

  [Draft​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder)

  The completed draft order.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Complete a draft order

  #### Description

  Convert a finalized draft order into a completed \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) that's ready for fulfillment and payment processing. This example shows the process for completing an order. When an order is marked as paid, you receive a new order ID to track and fulfill the order. Use this example when a customer has confirmed their purchase and payment is received.

  #### Query

  ```graphql
  mutation draftOrderComplete($id: ID!) {
    draftOrderComplete(id: $id) {
      draftOrder {
        id
        order {
          id
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/DraftOrder/276395349"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation draftOrderComplete($id: ID!) { draftOrderComplete(id: $id) { draftOrder { id order { id } } } }",
   "variables": {
      "id": "gid://shopify/DraftOrder/276395349"
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
    mutation draftOrderComplete($id: ID!) {
      draftOrderComplete(id: $id) {
        draftOrder {
          id
          order {
            id
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DraftOrder/276395349"
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
    mutation draftOrderComplete($id: ID!) {
      draftOrderComplete(id: $id) {
        draftOrder {
          id
          order {
            id
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DraftOrder/276395349"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation draftOrderComplete($id: ID!) {
        draftOrderComplete(id: $id) {
          draftOrder {
            id
            order {
              id
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DraftOrder/276395349"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation draftOrderComplete($id: ID!) {
    draftOrderComplete(id: $id) {
      draftOrder {
        id
        order {
          id
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DraftOrder/276395349"
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderComplete": {
      "draftOrder": {
        "id": "gid://shopify/DraftOrder/276395349",
        "order": {
          "id": "gid://shopify/Order/1073459969"
        }
      }
    }
  }
  ```

* ### Complete a draft order using a payment gateway

  #### Description

  Create a draft order using the \[\`paymentGatewayId\`]\(https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderComplete#arguments-paymentGatewayId) argument for specialized payment processing. This example demonstrates completing orders through specific payment providers, such as custom payment gateways or alternative payment methods. Learn more about \[third-party payment providers]\(https://help.shopify.com/manual/payments/third-party-providers).

  #### Query

  ```graphql
  mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID) {
    draftOrderComplete(id: $id, paymentGatewayId: $paymentGatewayId) {
      draftOrder {
        id
        order {
          id
          paymentGatewayNames
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/DraftOrder/276395349",
    "paymentGatewayId": "gid://shopify/PaymentGateway/371889432"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID) { draftOrderComplete(id: $id, paymentGatewayId: $paymentGatewayId) { draftOrder { id order { id paymentGatewayNames } } } }",
   "variables": {
      "id": "gid://shopify/DraftOrder/276395349",
      "paymentGatewayId": "gid://shopify/PaymentGateway/371889432"
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
    mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID) {
      draftOrderComplete(id: $id, paymentGatewayId: $paymentGatewayId) {
        draftOrder {
          id
          order {
            id
            paymentGatewayNames
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DraftOrder/276395349",
          "paymentGatewayId": "gid://shopify/PaymentGateway/371889432"
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
    mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID) {
      draftOrderComplete(id: $id, paymentGatewayId: $paymentGatewayId) {
        draftOrder {
          id
          order {
            id
            paymentGatewayNames
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DraftOrder/276395349",
    "paymentGatewayId": "gid://shopify/PaymentGateway/371889432"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID) {
        draftOrderComplete(id: $id, paymentGatewayId: $paymentGatewayId) {
          draftOrder {
            id
            order {
              id
              paymentGatewayNames
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DraftOrder/276395349",
          "paymentGatewayId": "gid://shopify/PaymentGateway/371889432"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID) {
    draftOrderComplete(id: $id, paymentGatewayId: $paymentGatewayId) {
      draftOrder {
        id
        order {
          id
          paymentGatewayNames
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DraftOrder/276395349",
    "paymentGatewayId": "gid://shopify/PaymentGateway/371889432"
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderComplete": {
      "draftOrder": {
        "id": "gid://shopify/DraftOrder/276395349",
        "order": {
          "id": "gid://shopify/Order/1073459968",
          "paymentGatewayNames": [
            "Cash on Delivery (COD)"
          ]
        }
      }
    }
  }
  ```

* ### Completing a draft order with an invalid payment gateway returns a user error

  #### Description

  Create a draft order with an invalid \[\`paymentGatewayId\`]\(https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderComplete#arguments-paymentGatewayId) to demonstrate error handling. This example shows the \[\`userErrors\`]\(https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderComplete#returns-userErrors) response when specifying a payment gateway that doesn't exist or is disabled, helping you build robust payment processing that handles invalid payment gateway configurations.

  #### Query

  ```graphql
  mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID) {
    draftOrderComplete(id: $id, paymentGatewayId: $paymentGatewayId) {
      userErrors {
        message
        field
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/DraftOrder/276395349",
    "paymentGatewayId": "gid://shopify/PaymentGateway/12121213"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID) { draftOrderComplete(id: $id, paymentGatewayId: $paymentGatewayId) { userErrors { message field } } }",
   "variables": {
      "id": "gid://shopify/DraftOrder/276395349",
      "paymentGatewayId": "gid://shopify/PaymentGateway/12121213"
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
    mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID) {
      draftOrderComplete(id: $id, paymentGatewayId: $paymentGatewayId) {
        userErrors {
          message
          field
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DraftOrder/276395349",
          "paymentGatewayId": "gid://shopify/PaymentGateway/12121213"
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
    mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID) {
      draftOrderComplete(id: $id, paymentGatewayId: $paymentGatewayId) {
        userErrors {
          message
          field
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DraftOrder/276395349",
    "paymentGatewayId": "gid://shopify/PaymentGateway/12121213"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID) {
        draftOrderComplete(id: $id, paymentGatewayId: $paymentGatewayId) {
          userErrors {
            message
            field
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DraftOrder/276395349",
          "paymentGatewayId": "gid://shopify/PaymentGateway/12121213"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation draftOrderComplete($id: ID!, $paymentGatewayId: ID) {
    draftOrderComplete(id: $id, paymentGatewayId: $paymentGatewayId) {
      userErrors {
        message
        field
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DraftOrder/276395349",
    "paymentGatewayId": "gid://shopify/PaymentGateway/12121213"
  }'
  ```

  #### Response

  ```json
  {
    "draftOrderComplete": {
      "userErrors": [
        {
          "message": "Invalid payment gateway",
          "field": null
        }
      ]
    }
  }
  ```

* ### draftOrderComplete reference
