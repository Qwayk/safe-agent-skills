---
title: fulfillmentOrderLineItemsPreparedForPickup - GraphQL Admin
description: >-
  Marks [fulfillment order line
  items](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrderLineItem)
  as ready for customer pickup. When executed, this mutation automatically sends
  a "Ready For Pickup" notification to the customer.


  Use this mutation for local pickup orders after the items have been prepared
  and are available for the customer to collect. You can specify one or more
  [fulfillment
  order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)
  objects by providing the fulfillment order IDs in the
  [`lineItemsByFulfillmentOrder`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PreparedFulfillmentOrderLineItemsInput)
  field. This allows you to mark fulfillment order line items from different
  fulfillment orders as ready for pickup.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderLineItemsPreparedForPickup
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderLineItemsPreparedForPickup.md
---

# fulfillment​Order​Line​Items​Prepared​For​Pickup

mutation

Requires `write_merchant_managed_fulfillment_orders` access scope. Also: The user must have fulfill\_and\_ship\_orders permission.

Marks [fulfillment order line items](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrderLineItem) as ready for customer pickup. When executed, this mutation automatically sends a "Ready For Pickup" notification to the customer.

Use this mutation for local pickup orders after the items have been prepared and are available for the customer to collect. You can specify one or more [fulfillment order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder) objects by providing the fulfillment order IDs in the [`lineItemsByFulfillmentOrder`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PreparedFulfillmentOrderLineItemsInput) field. This allows you to mark fulfillment order line items from different fulfillment orders as ready for pickup.

## Arguments

* input

  [Fulfillment​Order​Line​Items​Prepared​For​Pickup​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/FulfillmentOrderLineItemsPreparedForPickupInput)

  required

  The input for marking fulfillment order line items as ready for pickup.

***

## Fulfillment​Order​Line​Items​Prepared​For​Pickup​Payload returns

* user​Errors

  [\[Fulfillment​Order​Line​Items​Prepared​For​Pickup​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrderLineItemsPreparedForPickupUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Mark all line items associated with a fulfillment order as being ready for a customer to pick up

  #### Description

  Marks all line items associated with a fulfillment order as being ready to pick up and sends a 'Ready For Pickup' notification to the customer to let them know that their order is ready to be picked up.

  #### Query

  ```graphql
  mutation fulfillmentOrderLineItemsPreparedForPickup($input: FulfillmentOrderLineItemsPreparedForPickupInput!) {
    fulfillmentOrderLineItemsPreparedForPickup(input: $input) {
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
      "lineItemsByFulfillmentOrder": [
        {
          "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/1046000776"
        }
      ]
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
  "query": "mutation fulfillmentOrderLineItemsPreparedForPickup($input: FulfillmentOrderLineItemsPreparedForPickupInput!) { fulfillmentOrderLineItemsPreparedForPickup(input: $input) { userErrors { field message } } }",
   "variables": {
      "input": {
        "lineItemsByFulfillmentOrder": [
          {
            "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/1046000776"
          }
        ]
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
    mutation fulfillmentOrderLineItemsPreparedForPickup($input: FulfillmentOrderLineItemsPreparedForPickupInput!) {
      fulfillmentOrderLineItemsPreparedForPickup(input: $input) {
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "lineItemsByFulfillmentOrder": [
                  {
                      "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/1046000776"
                  }
              ]
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
    mutation fulfillmentOrderLineItemsPreparedForPickup($input: FulfillmentOrderLineItemsPreparedForPickupInput!) {
      fulfillmentOrderLineItemsPreparedForPickup(input: $input) {
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "lineItemsByFulfillmentOrder": [
        {
          "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/1046000776"
        }
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentOrderLineItemsPreparedForPickup($input: FulfillmentOrderLineItemsPreparedForPickupInput!) {
        fulfillmentOrderLineItemsPreparedForPickup(input: $input) {
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "lineItemsByFulfillmentOrder": [
                  {
                      "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/1046000776"
                  }
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentOrderLineItemsPreparedForPickup($input: FulfillmentOrderLineItemsPreparedForPickupInput!) {
    fulfillmentOrderLineItemsPreparedForPickup(input: $input) {
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "lineItemsByFulfillmentOrder": [
        {
          "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/1046000776"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrderLineItemsPreparedForPickup": {
      "userErrors": []
    }
  }
  ```

* ### fulfillmentOrderLineItemsPreparedForPickup reference
