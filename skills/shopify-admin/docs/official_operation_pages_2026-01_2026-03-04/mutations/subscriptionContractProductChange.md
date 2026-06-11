---
title: subscriptionContractProductChange - GraphQL Admin
description: >-
  Allows for the easy change of a Product in a Contract or a Product price
  change.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionContractProductChange
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/subscriptionContractProductChange.md
---

# subscription​Contract​Product​Change

mutation

Requires `write_own_subscription_contracts` access scope. Also: The user must have manage\_orders\_information permission.

Allows for the easy change of a Product in a Contract or a Product price change.

## Arguments

* input

  [Subscription​Contract​Product​Change​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SubscriptionContractProductChangeInput)

  required

  The properties of the Product changes.

* line​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The gid of the Subscription Line to update.

* subscription​Contract​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the subscription contract.

***

## Subscription​Contract​Product​Change​Payload returns

* contract

  [Subscription​Contract](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionContract)

  The new Subscription Contract object.

* line​Updated

  [Subscription​Line](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionLine)

  The updated Subscription Line.

* user​Errors

  [\[Subscription​Draft​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionDraftUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update both product and price in a subscription contract

  #### Description

  Swaps a product and changes the price of a line in a subscription contract.

  #### Query

  ```graphql
  mutation($contractId: ID!, $lineId: ID!, $variantId: ID!) {
    subscriptionContractProductChange(subscriptionContractId: $contractId, lineId: $lineId, input: {productVariantId: $variantId, currentPrice: 500}) {
      contract {
        id
        updatedAt
      }
      lineUpdated {
        id
        currentPrice {
          amount
        }
        variantId
      }
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
    "contractId": "gid://shopify/SubscriptionContract/593791907",
    "lineId": "gid://shopify/SubscriptionLine/25476bfc-b794-4ff5-b41f-7a00eb252d55",
    "variantId": "gid://shopify/ProductVariant/30322695"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation($contractId: ID!, $lineId: ID!, $variantId: ID!) { subscriptionContractProductChange(subscriptionContractId: $contractId, lineId: $lineId, input: {productVariantId: $variantId, currentPrice: 500}) { contract { id updatedAt } lineUpdated { id currentPrice { amount } variantId } userErrors { field message code } } }",
   "variables": {
      "contractId": "gid://shopify/SubscriptionContract/593791907",
      "lineId": "gid://shopify/SubscriptionLine/25476bfc-b794-4ff5-b41f-7a00eb252d55",
      "variantId": "gid://shopify/ProductVariant/30322695"
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
    mutation($contractId: ID!, $lineId: ID!, $variantId: ID!) {
      subscriptionContractProductChange(subscriptionContractId: $contractId, lineId: $lineId, input: {productVariantId: $variantId, currentPrice: 500}) {
        contract {
          id
          updatedAt
        }
        lineUpdated {
          id
          currentPrice {
            amount
          }
          variantId
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "contractId": "gid://shopify/SubscriptionContract/593791907",
          "lineId": "gid://shopify/SubscriptionLine/25476bfc-b794-4ff5-b41f-7a00eb252d55",
          "variantId": "gid://shopify/ProductVariant/30322695"
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
    mutation($contractId: ID!, $lineId: ID!, $variantId: ID!) {
      subscriptionContractProductChange(subscriptionContractId: $contractId, lineId: $lineId, input: {productVariantId: $variantId, currentPrice: 500}) {
        contract {
          id
          updatedAt
        }
        lineUpdated {
          id
          currentPrice {
            amount
          }
          variantId
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "contractId": "gid://shopify/SubscriptionContract/593791907",
    "lineId": "gid://shopify/SubscriptionLine/25476bfc-b794-4ff5-b41f-7a00eb252d55",
    "variantId": "gid://shopify/ProductVariant/30322695"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation($contractId: ID!, $lineId: ID!, $variantId: ID!) {
        subscriptionContractProductChange(subscriptionContractId: $contractId, lineId: $lineId, input: {productVariantId: $variantId, currentPrice: 500}) {
          contract {
            id
            updatedAt
          }
          lineUpdated {
            id
            currentPrice {
              amount
            }
            variantId
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "contractId": "gid://shopify/SubscriptionContract/593791907",
          "lineId": "gid://shopify/SubscriptionLine/25476bfc-b794-4ff5-b41f-7a00eb252d55",
          "variantId": "gid://shopify/ProductVariant/30322695"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation($contractId: ID!, $lineId: ID!, $variantId: ID!) {
    subscriptionContractProductChange(subscriptionContractId: $contractId, lineId: $lineId, input: {productVariantId: $variantId, currentPrice: 500}) {
      contract {
        id
        updatedAt
      }
      lineUpdated {
        id
        currentPrice {
          amount
        }
        variantId
      }
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "contractId": "gid://shopify/SubscriptionContract/593791907",
    "lineId": "gid://shopify/SubscriptionLine/25476bfc-b794-4ff5-b41f-7a00eb252d55",
    "variantId": "gid://shopify/ProductVariant/30322695"
  }'
  ```

  #### Response

  ```json
  {
    "subscriptionContractProductChange": {
      "contract": {
        "id": "gid://shopify/SubscriptionContract/593791907",
        "updatedAt": "2024-09-12T01:09:12Z"
      },
      "lineUpdated": {
        "id": "gid://shopify/SubscriptionLine/25476bfc-b794-4ff5-b41f-7a00eb252d55",
        "currentPrice": {
          "amount": "500.0"
        },
        "variantId": "gid://shopify/ProductVariant/30322695"
      },
      "userErrors": []
    }
  }
  ```

* ### subscriptionContractProductChange reference
