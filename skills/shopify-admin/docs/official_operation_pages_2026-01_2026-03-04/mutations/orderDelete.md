---
title: orderDelete - GraphQL Admin
description: >-
  Permanently deletes an
  [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)
  from the store.


  You can only delete [specific order
  types](https://help.shopify.com/manual/orders/cancel-delete-order#delete-an-order).
  Other orders you can cancel using the
  [`orderCancel`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCancel)
  mutation instead.


  > Caution:

  > This action is irreversible. You can't recover deleted orders.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderDelete'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderDelete.md'
---

# order​Delete

mutation

Requires `write_orders` access scope. Also: The user must have delete\_orders permission.

Permanently deletes an [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) from the store.

You can only delete [specific order types](https://help.shopify.com/manual/orders/cancel-delete-order#delete-an-order). Other orders you can cancel using the [`orderCancel`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCancel) mutation instead.

***

**Caution:** This action is irreversible. You can\&#39;t recover deleted orders.

***

## Arguments

* order​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the order to be deleted.

***

## Order​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  Deleted order ID.

* user​Errors

  [\[Order​Delete​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderDeleteUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Delete an order

  #### Query

  ```graphql
  mutation OrderDelete($orderId: ID!) {
    orderDelete(orderId: $orderId) {
      deletedId
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "orderId": "gid://shopify/Order/776341364"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation OrderDelete($orderId: ID!) { orderDelete(orderId: $orderId) { deletedId userErrors { field message code } } }",
   "variables": {
      "orderId": "gid://shopify/Order/776341364"
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
    mutation OrderDelete($orderId: ID!) {
      orderDelete(orderId: $orderId) {
        deletedId
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "orderId": "gid://shopify/Order/776341364"
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
    mutation OrderDelete($orderId: ID!) {
      orderDelete(orderId: $orderId) {
        deletedId
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "orderId": "gid://shopify/Order/776341364"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation OrderDelete($orderId: ID!) {
        orderDelete(orderId: $orderId) {
          deletedId
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "orderId": "gid://shopify/Order/776341364"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation OrderDelete($orderId: ID!) {
    orderDelete(orderId: $orderId) {
      deletedId
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "orderId": "gid://shopify/Order/776341364"
  }'
  ```

  #### Response

  ```json
  {
    "orderDelete": {
      "deletedId": "gid://shopify/Order/776341364",
      "userErrors": []
    }
  }
  ```

* ### orderDelete reference
