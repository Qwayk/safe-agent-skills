---
title: orderMarkAsPaid - GraphQL Admin
description: >-
  Marks an order as paid by recording a payment transaction for the outstanding
  amount.


  Use the `orderMarkAsPaid` mutation to record payments received outside the
  standard checkout

  process. The `orderMarkAsPaid` mutation is particularly useful in scenarios
  where:


  - Orders were created with manual payment methods (cash on delivery, bank
  deposit, money order)

  - Payments were received offline and need to be recorded in the system

  - Previously authorized payments need to be captured manually

  - Orders require manual payment reconciliation due to external payment
  processing


  The mutation validates that the order can be marked as paid before processing.

  An order can be marked as paid only if it has a positive outstanding balance
  and its

  [financial
  status](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order#field-Order.fields.displayFinancialStatus)

  isn't already `PAID`. The mutation will either create a new sale transaction
  for the full

  outstanding amount or capture an existing authorized transaction, depending on
  the order's current payment state.


  After successfully marking an order as paid, the order's financial status is
  updated to

  reflect the payment, and payment events are logged for tracking and analytics

  purposes.


  Learn more about [managing
  orders](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps)

  in apps.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderMarkAsPaid'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderMarkAsPaid.md
---

# order​Mark​As​Paid

mutation

Requires `write_orders` access scope. Also: The user must have mark\_orders\_as\_paid permission.

Marks an order as paid by recording a payment transaction for the outstanding amount.

Use the `orderMarkAsPaid` mutation to record payments received outside the standard checkout process. The `orderMarkAsPaid` mutation is particularly useful in scenarios where:

* Orders were created with manual payment methods (cash on delivery, bank deposit, money order)
* Payments were received offline and need to be recorded in the system
* Previously authorized payments need to be captured manually
* Orders require manual payment reconciliation due to external payment processing

The mutation validates that the order can be marked as paid before processing. An order can be marked as paid only if it has a positive outstanding balance and its [financial status](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order#field-Order.fields.displayFinancialStatus) isn't already `PAID`. The mutation will either create a new sale transaction for the full outstanding amount or capture an existing authorized transaction, depending on the order's current payment state.

After successfully marking an order as paid, the order's financial status is updated to reflect the payment, and payment events are logged for tracking and analytics purposes.

Learn more about [managing orders](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps) in apps.

## Arguments

* input

  [Order​Mark​As​Paid​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OrderMarkAsPaidInput)

  required

  The input for the mutation.

***

## Order​Mark​As​Paid​Payload returns

* order

  [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

  The order marked as paid.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Attempt to mark an already paid order as paid

  #### Description

  Attempt to mark an \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) as paid when it has already been fully paid. The mutation returns user errors explaining why the operation can't be completed while still providing order data for reference.

  #### Query

  ```graphql
  mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) {
    orderMarkAsPaid(input: $input) {
      userErrors {
        field
        message
      }
      order {
        id
        name
        canMarkAsPaid
        displayFinancialStatus
        totalPrice
        totalOutstandingSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        transactions(first: 10) {
          id
          kind
          status
          amountSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          gateway
          createdAt
        }
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
  "query": "mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) { orderMarkAsPaid(input: $input) { userErrors { field message } order { id name canMarkAsPaid displayFinancialStatus totalPrice totalOutstandingSet { shopMoney { amount currencyCode } } transactions(first: 10) { id kind status amountSet { shopMoney { amount currencyCode } } gateway createdAt } } } }",
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
    mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) {
      orderMarkAsPaid(input: $input) {
        userErrors {
          field
          message
        }
        order {
          id
          name
          canMarkAsPaid
          displayFinancialStatus
          totalPrice
          totalOutstandingSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          transactions(first: 10) {
            id
            kind
            status
            amountSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            gateway
            createdAt
          }
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
    mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) {
      orderMarkAsPaid(input: $input) {
        userErrors {
          field
          message
        }
        order {
          id
          name
          canMarkAsPaid
          displayFinancialStatus
          totalPrice
          totalOutstandingSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          transactions(first: 10) {
            id
            kind
            status
            amountSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            gateway
            createdAt
          }
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
      "query": `mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) {
        orderMarkAsPaid(input: $input) {
          userErrors {
            field
            message
          }
          order {
            id
            name
            canMarkAsPaid
            displayFinancialStatus
            totalPrice
            totalOutstandingSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            transactions(first: 10) {
              id
              kind
              status
              amountSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
              gateway
              createdAt
            }
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
  'mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) {
    orderMarkAsPaid(input: $input) {
      userErrors {
        field
        message
      }
      order {
        id
        name
        canMarkAsPaid
        displayFinancialStatus
        totalPrice
        totalOutstandingSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        transactions(first: 10) {
          id
          kind
          status
          amountSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          gateway
          createdAt
        }
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
    "orderMarkAsPaid": {
      "userErrors": [
        {
          "field": [
            "id"
          ],
          "message": "Order cannot be marked as paid."
        }
      ],
      "order": {
        "id": "gid://shopify/Order/148977776",
        "name": "#1001",
        "canMarkAsPaid": false,
        "displayFinancialStatus": "PAID",
        "totalPrice": "11.50",
        "totalOutstandingSet": {
          "shopMoney": {
            "amount": "0.0",
            "currencyCode": "USD"
          }
        },
        "transactions": [
          {
            "id": "gid://shopify/OrderTransaction/42239183",
            "kind": "AUTHORIZATION",
            "status": "FAILURE",
            "amountSet": {
              "shopMoney": {
                "amount": "11.5",
                "currencyCode": "USD"
              }
            },
            "gateway": "bogus",
            "createdAt": "2005-07-31T15:57:10Z"
          },
          {
            "id": "gid://shopify/OrderTransaction/607668304",
            "kind": "SALE",
            "status": "AWAITING_RESPONSE",
            "amountSet": {
              "shopMoney": {
                "amount": "50.0",
                "currencyCode": "USD"
              }
            },
            "gateway": "bogus",
            "createdAt": "2005-07-31T15:57:11Z"
          },
          {
            "id": "gid://shopify/OrderTransaction/661056787",
            "kind": "AUTHORIZATION",
            "status": "SUCCESS",
            "amountSet": {
              "shopMoney": {
                "amount": "11.5",
                "currencyCode": "USD"
              }
            },
            "gateway": "bogus",
            "createdAt": "2005-07-31T15:57:10Z"
          },
          {
            "id": "gid://shopify/OrderTransaction/999225631",
            "kind": "CAPTURE",
            "status": "SUCCESS",
            "amountSet": {
              "shopMoney": {
                "amount": "11.5",
                "currencyCode": "USD"
              }
            },
            "gateway": "bogus",
            "createdAt": "2005-07-31T15:57:11Z"
          }
        ]
      }
    }
  }
  ```

* ### Mark an authorized order as paid

  #### Description

  Mark an \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) with authorized payment as paid by capturing the full authorized amount. The mutation creates a new \`CAPTURE\` transaction, updates the order's financial status to \`PAID\`, and sets the outstanding balance to zero. The response includes comprehensive order details and transaction history.

  #### Query

  ```graphql
  mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) {
    orderMarkAsPaid(input: $input) {
      userErrors {
        field
        message
      }
      order {
        id
        name
        canMarkAsPaid
        displayFinancialStatus
        totalPrice
        totalOutstandingSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        transactions(first: 10) {
          id
          kind
          status
          amountSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          gateway
          createdAt
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "id": "gid://shopify/Order/431501862"
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
  "query": "mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) { orderMarkAsPaid(input: $input) { userErrors { field message } order { id name canMarkAsPaid displayFinancialStatus totalPrice totalOutstandingSet { shopMoney { amount currencyCode } } transactions(first: 10) { id kind status amountSet { shopMoney { amount currencyCode } } gateway createdAt } } } }",
   "variables": {
      "input": {
        "id": "gid://shopify/Order/431501862"
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
    mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) {
      orderMarkAsPaid(input: $input) {
        userErrors {
          field
          message
        }
        order {
          id
          name
          canMarkAsPaid
          displayFinancialStatus
          totalPrice
          totalOutstandingSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          transactions(first: 10) {
            id
            kind
            status
            amountSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            gateway
            createdAt
          }
        }
      }
    }`,
    {
      variables: {
          "input": {
              "id": "gid://shopify/Order/431501862"
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
    mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) {
      orderMarkAsPaid(input: $input) {
        userErrors {
          field
          message
        }
        order {
          id
          name
          canMarkAsPaid
          displayFinancialStatus
          totalPrice
          totalOutstandingSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          transactions(first: 10) {
            id
            kind
            status
            amountSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            gateway
            createdAt
          }
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "id": "gid://shopify/Order/431501862"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) {
        orderMarkAsPaid(input: $input) {
          userErrors {
            field
            message
          }
          order {
            id
            name
            canMarkAsPaid
            displayFinancialStatus
            totalPrice
            totalOutstandingSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            transactions(first: 10) {
              id
              kind
              status
              amountSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
              gateway
              createdAt
            }
          }
        }
      }`,
      "variables": {
          "input": {
              "id": "gid://shopify/Order/431501862"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation orderMarkAsPaid($input: OrderMarkAsPaidInput!) {
    orderMarkAsPaid(input: $input) {
      userErrors {
        field
        message
      }
      order {
        id
        name
        canMarkAsPaid
        displayFinancialStatus
        totalPrice
        totalOutstandingSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        transactions(first: 10) {
          id
          kind
          status
          amountSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          gateway
          createdAt
        }
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "id": "gid://shopify/Order/431501862"
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderMarkAsPaid": {
      "userErrors": [],
      "order": {
        "id": "gid://shopify/Order/431501862",
        "name": "#1014",
        "canMarkAsPaid": false,
        "displayFinancialStatus": "PAID",
        "totalPrice": "1000.00",
        "totalOutstandingSet": {
          "shopMoney": {
            "amount": "0.0",
            "currencyCode": "USD"
          }
        },
        "transactions": [
          {
            "id": "gid://shopify/OrderTransaction/336526656",
            "kind": "AUTHORIZATION",
            "status": "SUCCESS",
            "amountSet": {
              "shopMoney": {
                "amount": "1000.0",
                "currencyCode": "USD"
              }
            },
            "gateway": "bogus",
            "createdAt": "2005-08-01T15:57:11Z"
          },
          {
            "id": "gid://shopify/OrderTransaction/1068278469",
            "kind": "CAPTURE",
            "status": "SUCCESS",
            "amountSet": {
              "shopMoney": {
                "amount": "1000.0",
                "currencyCode": "USD"
              }
            },
            "gateway": "manual",
            "createdAt": "2025-06-20T03:18:30Z"
          }
        ]
      }
    }
  }
  ```

* ### orderMarkAsPaid reference
