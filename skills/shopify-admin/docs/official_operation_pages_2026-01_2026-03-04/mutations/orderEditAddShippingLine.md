---
title: orderEditAddShippingLine - GraphQL Admin
description: >-
  Adds a custom shipping line to an
  [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)
  during an edit session. Specify the shipping title and price to create a new
  [`ShippingLine`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShippingLine).

   Returns a [`CalculatedOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedOrder) showing the order with edits applied but not yet saved. To save your changes, use the [`orderEditCommit`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditCommit) mutation.

  Learn more about [editing existing
  orders](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/edit-orders).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditAddShippingLine
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditAddShippingLine.md
---

# order​Edit​Add​Shipping​Line

mutation

Requires `write_order_edits` access scope.

Adds a custom shipping line to an [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) during an edit session. Specify the shipping title and price to create a new [`ShippingLine`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShippingLine).

Returns a [`CalculatedOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedOrder) showing the order with edits applied but not yet saved. To save your changes, use the [`orderEditCommit`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditCommit) mutation.

Learn more about [editing existing orders](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/edit-orders).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the [calculated order](https://shopify.dev/api/admin-graphql/latest/objects/calculatedorder) or the order edit session to edit. This is the edit to which the shipping line is added.

* shipping​Line

  [Order​Edit​Add​Shipping​Line​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OrderEditAddShippingLineInput)

  required

  The shipping line to be added.

***

## Order​Edit​Add​Shipping​Line​Payload returns

* calculated​Order

  [Calculated​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedOrder)

  The [calculated order](https://shopify.dev/api/admin-graphql/latest/objects/calculatedorder) with the edits applied but not saved.

* calculated​Shipping​Line

  [Calculated​Shipping​Line](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedShippingLine)

  The [calculated shipping line](https://shopify.dev/api/admin-graphql/latest/objects/calculatedshippingline) that's added during this order edit.

* order​Edit​Session

  [Order​Edit​Session](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderEditSession)

  The order edit session with the edits applied but not saved.

* user​Errors

  [\[Order​Edit​Add​Shipping​Line​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderEditAddShippingLineUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Add a shipping line to an order edit

  #### Query

  ```graphql
  mutation addShippingLine($id: ID!, $shippingLine: OrderEditAddShippingLineInput!) {
    orderEditAddShippingLine(id: $id, shippingLine: $shippingLine) {
      calculatedOrder {
        id
        totalOutstandingSet {
          presentmentMoney {
            amount
            currencyCode
          }
        }
        totalPriceSet {
          presentmentMoney {
            amount
            currencyCode
          }
        }
      }
      calculatedShippingLine {
        id
        title
        price {
          presentmentMoney {
            amount
            currencyCode
          }
        }
        stagedStatus
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
    "id": "gid://shopify/CalculatedOrder/607673083",
    "shippingLine": {
      "title": "2-Day Shipping",
      "price": {
        "amount": 19.99,
        "currencyCode": "USD"
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
  "query": "mutation addShippingLine($id: ID!, $shippingLine: OrderEditAddShippingLineInput!) { orderEditAddShippingLine(id: $id, shippingLine: $shippingLine) { calculatedOrder { id totalOutstandingSet { presentmentMoney { amount currencyCode } } totalPriceSet { presentmentMoney { amount currencyCode } } } calculatedShippingLine { id title price { presentmentMoney { amount currencyCode } } stagedStatus } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/CalculatedOrder/607673083",
      "shippingLine": {
        "title": "2-Day Shipping",
        "price": {
          "amount": 19.99,
          "currencyCode": "USD"
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
    mutation addShippingLine($id: ID!, $shippingLine: OrderEditAddShippingLineInput!) {
      orderEditAddShippingLine(id: $id, shippingLine: $shippingLine) {
        calculatedOrder {
          id
          totalOutstandingSet {
            presentmentMoney {
              amount
              currencyCode
            }
          }
          totalPriceSet {
            presentmentMoney {
              amount
              currencyCode
            }
          }
        }
        calculatedShippingLine {
          id
          title
          price {
            presentmentMoney {
              amount
              currencyCode
            }
          }
          stagedStatus
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/CalculatedOrder/607673083",
          "shippingLine": {
              "title": "2-Day Shipping",
              "price": {
                  "amount": 19.99,
                  "currencyCode": "USD"
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
    mutation addShippingLine($id: ID!, $shippingLine: OrderEditAddShippingLineInput!) {
      orderEditAddShippingLine(id: $id, shippingLine: $shippingLine) {
        calculatedOrder {
          id
          totalOutstandingSet {
            presentmentMoney {
              amount
              currencyCode
            }
          }
          totalPriceSet {
            presentmentMoney {
              amount
              currencyCode
            }
          }
        }
        calculatedShippingLine {
          id
          title
          price {
            presentmentMoney {
              amount
              currencyCode
            }
          }
          stagedStatus
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/CalculatedOrder/607673083",
    "shippingLine": {
      "title": "2-Day Shipping",
      "price": {
        "amount": 19.99,
        "currencyCode": "USD"
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
      "query": `mutation addShippingLine($id: ID!, $shippingLine: OrderEditAddShippingLineInput!) {
        orderEditAddShippingLine(id: $id, shippingLine: $shippingLine) {
          calculatedOrder {
            id
            totalOutstandingSet {
              presentmentMoney {
                amount
                currencyCode
              }
            }
            totalPriceSet {
              presentmentMoney {
                amount
                currencyCode
              }
            }
          }
          calculatedShippingLine {
            id
            title
            price {
              presentmentMoney {
                amount
                currencyCode
              }
            }
            stagedStatus
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/CalculatedOrder/607673083",
          "shippingLine": {
              "title": "2-Day Shipping",
              "price": {
                  "amount": 19.99,
                  "currencyCode": "USD"
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
  'mutation addShippingLine($id: ID!, $shippingLine: OrderEditAddShippingLineInput!) {
    orderEditAddShippingLine(id: $id, shippingLine: $shippingLine) {
      calculatedOrder {
        id
        totalOutstandingSet {
          presentmentMoney {
            amount
            currencyCode
          }
        }
        totalPriceSet {
          presentmentMoney {
            amount
            currencyCode
          }
        }
      }
      calculatedShippingLine {
        id
        title
        price {
          presentmentMoney {
            amount
            currencyCode
          }
        }
        stagedStatus
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/CalculatedOrder/607673083",
    "shippingLine": {
      "title": "2-Day Shipping",
      "price": {
        "amount": 19.99,
        "currencyCode": "USD"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderEditAddShippingLine": {
      "calculatedOrder": {
        "id": "gid://shopify/CalculatedOrder/607673083",
        "totalOutstandingSet": {
          "presentmentMoney": {
            "amount": "19.99",
            "currencyCode": "USD"
          }
        },
        "totalPriceSet": {
          "presentmentMoney": {
            "amount": "31.49",
            "currencyCode": "USD"
          }
        }
      },
      "calculatedShippingLine": {
        "id": "gid://shopify/CalculatedShippingLine/52c5ee83-d24a-4a4d-a048-b00ad90aa19f",
        "title": "2-Day Shipping",
        "price": {
          "presentmentMoney": {
            "amount": "19.99",
            "currencyCode": "USD"
          }
        },
        "stagedStatus": "ADDED"
      },
      "userErrors": []
    }
  }
  ```

* ### orderEditAddShippingLine reference
