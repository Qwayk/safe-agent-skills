---
title: orderEditAddLineItemDiscount - GraphQL Admin
description: >-
  Applies a discount to a
  [`LineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem)
  during an order edit session. The discount can be either a fixed amount or
  percentage value.


  To modify pricing on specific line items, use this mutation after starting an
  order edit with the
  [`orderEditBegin`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditBegin)
  mutation. The changes remain staged until you commit them with the
  [`orderEditCommit`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditCommit)
  mutation.


  Learn more about [editing existing
  orders](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/edit-orders).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditAddLineItemDiscount
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditAddLineItemDiscount.md
---

# order​Edit​Add​Line​Item​Discount

mutation

Requires `write_order_edits` access scope. Also: The user must have apply\_discounts\_to\_orders permission.

Applies a discount to a [`LineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem) during an order edit session. The discount can be either a fixed amount or percentage value.

To modify pricing on specific line items, use this mutation after starting an order edit with the [`orderEditBegin`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditBegin) mutation. The changes remain staged until you commit them with the [`orderEditCommit`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditCommit) mutation.

Learn more about [editing existing orders](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/edit-orders).

## Arguments

* discount

  [Order​Edit​Applied​Discount​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OrderEditAppliedDiscountInput)

  required

  The discount to add to the line item.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the [calculated order](https://shopify.dev/api/admin-graphql/latest/objects/calculatedorder) or the order edit session to edit.

* line​Item​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the calculated line item to add the discount to.

***

## Order​Edit​Add​Line​Item​Discount​Payload returns

* added​Discount​Staged​Change

  [Order​Staged​Change​Add​Line​Item​Discount](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderStagedChangeAddLineItemDiscount)

  The discount applied to a line item during this order edit.

* calculated​Line​Item

  [Calculated​Line​Item](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedLineItem)

  The line item with the edits applied but not saved.

* calculated​Order

  [Calculated​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedOrder)

  An order with the edits applied but not saved.

* order​Edit​Session

  [Order​Edit​Session](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderEditSession)

  The order edit session with the edits applied but not saved.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Add a 50% discount to a line item in an order edit

  #### Query

  ```graphql
  mutation orderEditAddLineItemDiscount($id: ID!, $lineItemId: ID!, $discount: OrderEditAppliedDiscountInput!) {
    orderEditAddLineItemDiscount(id: $id, lineItemId: $lineItemId, discount: $discount) {
      calculatedOrder {
        id
      }
      calculatedLineItem {
        id
        calculatedDiscountAllocations {
          discountApplication {
            id
          }
        }
      }
      addedDiscountStagedChange {
        id
        description
        value {
          __typename
          ... on PricingPercentageValue {
            percentage
          }
        }
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
    "id": "gid://shopify/CalculatedOrder/607673109",
    "lineItemId": "gid://shopify/CalculatedLineItem/510711879",
    "discount": {
      "description": "50% off promotion",
      "percentValue": 50
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
  "query": "mutation orderEditAddLineItemDiscount($id: ID!, $lineItemId: ID!, $discount: OrderEditAppliedDiscountInput!) { orderEditAddLineItemDiscount(id: $id, lineItemId: $lineItemId, discount: $discount) { calculatedOrder { id } calculatedLineItem { id calculatedDiscountAllocations { discountApplication { id } } } addedDiscountStagedChange { id description value { __typename ... on PricingPercentageValue { percentage } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/CalculatedOrder/607673109",
      "lineItemId": "gid://shopify/CalculatedLineItem/510711879",
      "discount": {
        "description": "50% off promotion",
        "percentValue": 50
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
    mutation orderEditAddLineItemDiscount($id: ID!, $lineItemId: ID!, $discount: OrderEditAppliedDiscountInput!) {
      orderEditAddLineItemDiscount(id: $id, lineItemId: $lineItemId, discount: $discount) {
        calculatedOrder {
          id
        }
        calculatedLineItem {
          id
          calculatedDiscountAllocations {
            discountApplication {
              id
            }
          }
        }
        addedDiscountStagedChange {
          id
          description
          value {
            __typename
            ... on PricingPercentageValue {
              percentage
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/CalculatedOrder/607673109",
          "lineItemId": "gid://shopify/CalculatedLineItem/510711879",
          "discount": {
              "description": "50% off promotion",
              "percentValue": 50
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
    mutation orderEditAddLineItemDiscount($id: ID!, $lineItemId: ID!, $discount: OrderEditAppliedDiscountInput!) {
      orderEditAddLineItemDiscount(id: $id, lineItemId: $lineItemId, discount: $discount) {
        calculatedOrder {
          id
        }
        calculatedLineItem {
          id
          calculatedDiscountAllocations {
            discountApplication {
              id
            }
          }
        }
        addedDiscountStagedChange {
          id
          description
          value {
            __typename
            ... on PricingPercentageValue {
              percentage
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/CalculatedOrder/607673109",
    "lineItemId": "gid://shopify/CalculatedLineItem/510711879",
    "discount": {
      "description": "50% off promotion",
      "percentValue": 50
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation orderEditAddLineItemDiscount($id: ID!, $lineItemId: ID!, $discount: OrderEditAppliedDiscountInput!) {
        orderEditAddLineItemDiscount(id: $id, lineItemId: $lineItemId, discount: $discount) {
          calculatedOrder {
            id
          }
          calculatedLineItem {
            id
            calculatedDiscountAllocations {
              discountApplication {
                id
              }
            }
          }
          addedDiscountStagedChange {
            id
            description
            value {
              __typename
              ... on PricingPercentageValue {
                percentage
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/CalculatedOrder/607673109",
          "lineItemId": "gid://shopify/CalculatedLineItem/510711879",
          "discount": {
              "description": "50% off promotion",
              "percentValue": 50
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation orderEditAddLineItemDiscount($id: ID!, $lineItemId: ID!, $discount: OrderEditAppliedDiscountInput!) {
    orderEditAddLineItemDiscount(id: $id, lineItemId: $lineItemId, discount: $discount) {
      calculatedOrder {
        id
      }
      calculatedLineItem {
        id
        calculatedDiscountAllocations {
          discountApplication {
            id
          }
        }
      }
      addedDiscountStagedChange {
        id
        description
        value {
          __typename
          ... on PricingPercentageValue {
            percentage
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/CalculatedOrder/607673109",
    "lineItemId": "gid://shopify/CalculatedLineItem/510711879",
    "discount": {
      "description": "50% off promotion",
      "percentValue": 50
    }
  }'
  ```

  #### Response

  ```json
  {
    "orderEditAddLineItemDiscount": {
      "calculatedOrder": {
        "id": "gid://shopify/CalculatedOrder/607673109"
      },
      "calculatedLineItem": {
        "id": "gid://shopify/CalculatedLineItem/510711879",
        "calculatedDiscountAllocations": [
          {
            "discountApplication": {
              "id": "gid://shopify/CalculatedManualDiscountApplication/68bd25c3-b74e-4250-814f-9fec0549c043"
            }
          }
        ]
      },
      "addedDiscountStagedChange": {
        "id": "gid://shopify/OrderStagedChangeAddLineItemDiscount/925898897",
        "description": "50% off promotion",
        "value": {
          "__typename": "PricingPercentageValue",
          "percentage": 50
        }
      },
      "userErrors": []
    }
  }
  ```

* ### orderEditAddLineItemDiscount reference
