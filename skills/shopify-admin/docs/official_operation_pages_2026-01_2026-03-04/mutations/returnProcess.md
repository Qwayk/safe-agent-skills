---
title: returnProcess - GraphQL Admin
description: >-
  Processes a return by confirming which items customers return and exchange,
  handling their disposition, and optionally issuing refunds. This mutation
  confirms the quantities for
  [`ReturnLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnLineItem)
  and
  [`ExchangeLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ExchangeLineItem)
  objects previously created on the
  [`Return`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Return).


  For returned items, you specify how to handle them through dispositions such
  as restocking or disposal. The mutation creates
  [`FulfillmentOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)
  objects for exchange items and records all transactions in the merchant's
  financial reports. You can optionally issue refunds through financial
  transfers, apply refund duties, and refund shipping costs.


  Learn more about [processing
  returns](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/build-return-management).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnProcess'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnProcess.md'
---

# return​Process

mutation

Requires `write_returns` access scope or `write_marketplace_returns` access scope.

Processes a return by confirming which items customers return and exchange, handling their disposition, and optionally issuing refunds. This mutation confirms the quantities for [`ReturnLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnLineItem) and [`ExchangeLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ExchangeLineItem) objects previously created on the [`Return`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Return).

For returned items, you specify how to handle them through dispositions such as restocking or disposal. The mutation creates [`FulfillmentOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder) objects for exchange items and records all transactions in the merchant's financial reports. You can optionally issue refunds through financial transfers, apply refund duties, and refund shipping costs.

Learn more about [processing returns](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/build-return-management).

## Arguments

* input

  [Return​Process​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ReturnProcessInput)

  required

  Specifies the input fields for processing a return.

***

## Return​Process​Payload returns

* return

  [Return](https://shopify.dev/docs/api/admin-graphql/latest/objects/Return)

  The processed return.

* user​Errors

  [\[Return​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Process a return

  #### Description

  Process and refund a return with a single return line item.

  #### Query

  ```graphql
  mutation ReturnProcessMutation($input: ReturnProcessInput!) {
    returnProcess(input: $input) {
      return {
        id
        __typename
      }
      userErrors {
        field
        message
        code
        __typename
      }
      __typename
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "returnId": "gid://shopify/Return/945000961",
      "returnLineItems": [
        {
          "id": "gid://shopify/ReturnLineItem/677614678",
          "quantity": 1
        }
      ],
      "financialTransfer": {
        "issueRefund": {
          "orderTransactions": [
            {
              "transactionAmount": {
                "amount": 25.99,
                "currencyCode": "USD"
              },
              "parentId": "gid://shopify/OrderTransaction/239853124"
            }
          ]
        }
      },
      "notifyCustomer": true
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
  "query": "mutation ReturnProcessMutation($input: ReturnProcessInput!) { returnProcess(input: $input) { return { id __typename } userErrors { field message code __typename } __typename } } ",
   "variables": {
      "input": {
        "returnId": "gid://shopify/Return/945000961",
        "returnLineItems": [
          {
            "id": "gid://shopify/ReturnLineItem/677614678",
            "quantity": 1
          }
        ],
        "financialTransfer": {
          "issueRefund": {
            "orderTransactions": [
              {
                "transactionAmount": {
                  "amount": 25.99,
                  "currencyCode": "USD"
                },
                "parentId": "gid://shopify/OrderTransaction/239853124"
              }
            ]
          }
        },
        "notifyCustomer": true
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
    mutation ReturnProcessMutation($input: ReturnProcessInput!) {
      returnProcess(input: $input) {
        return {
          id
          __typename
        }
        userErrors {
          field
          message
          code
          __typename
        }
        __typename
      }
    }
    `,
    {
      variables: {
          "input": {
              "returnId": "gid://shopify/Return/945000961",
              "returnLineItems": [
                  {
                      "id": "gid://shopify/ReturnLineItem/677614678",
                      "quantity": 1
                  }
              ],
              "financialTransfer": {
                  "issueRefund": {
                      "orderTransactions": [
                          {
                              "transactionAmount": {
                                  "amount": 25.99,
                                  "currencyCode": "USD"
                              },
                              "parentId": "gid://shopify/OrderTransaction/239853124"
                          }
                      ]
                  }
              },
              "notifyCustomer": true
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
    mutation ReturnProcessMutation($input: ReturnProcessInput!) {
      returnProcess(input: $input) {
        return {
          id
          __typename
        }
        userErrors {
          field
          message
          code
          __typename
        }
        __typename
      }
    }
    
  QUERY

  variables = {
    "input": {
      "returnId": "gid://shopify/Return/945000961",
      "returnLineItems": [
        {
          "id": "gid://shopify/ReturnLineItem/677614678",
          "quantity": 1
        }
      ],
      "financialTransfer": {
        "issueRefund": {
          "orderTransactions": [
            {
              "transactionAmount": {
                "amount": 25.99,
                "currencyCode": "USD"
              },
              "parentId": "gid://shopify/OrderTransaction/239853124"
            }
          ]
        }
      },
      "notifyCustomer": true
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation ReturnProcessMutation($input: ReturnProcessInput!) {
        returnProcess(input: $input) {
          return {
            id
            __typename
          }
          userErrors {
            field
            message
            code
            __typename
          }
          __typename
        }
      }
      `,
      "variables": {
          "input": {
              "returnId": "gid://shopify/Return/945000961",
              "returnLineItems": [
                  {
                      "id": "gid://shopify/ReturnLineItem/677614678",
                      "quantity": 1
                  }
              ],
              "financialTransfer": {
                  "issueRefund": {
                      "orderTransactions": [
                          {
                              "transactionAmount": {
                                  "amount": 25.99,
                                  "currencyCode": "USD"
                              },
                              "parentId": "gid://shopify/OrderTransaction/239853124"
                          }
                      ]
                  }
              },
              "notifyCustomer": true
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation ReturnProcessMutation($input: ReturnProcessInput!) {
    returnProcess(input: $input) {
      return {
        id
        __typename
      }
      userErrors {
        field
        message
        code
        __typename
      }
      __typename
    }
  }' \
  --variables \
  '{
    "input": {
      "returnId": "gid://shopify/Return/945000961",
      "returnLineItems": [
        {
          "id": "gid://shopify/ReturnLineItem/677614678",
          "quantity": 1
        }
      ],
      "financialTransfer": {
        "issueRefund": {
          "orderTransactions": [
            {
              "transactionAmount": {
                "amount": 25.99,
                "currencyCode": "USD"
              },
              "parentId": "gid://shopify/OrderTransaction/239853124"
            }
          ]
        }
      },
      "notifyCustomer": true
    }
  }'
  ```

  #### Response

  ```json
  {
    "returnProcess": {
      "userErrors": [],
      "return": {
        "id": "gid://shopify/Return/945000961"
      }
    }
  }
  ```

* ### returnProcess reference
