---
title: giftCardCredit - GraphQL Admin
description: Credit a gift card.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/giftCardCredit'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/giftCardCredit.md
---

# gift​Card​Credit

mutation

Requires `write_gift_card_transactions` access scope.

Credit a gift card.

## Arguments

* credit​Input

  [Gift​Card​Credit​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/GiftCardCreditInput)

  required

  The input fields to credit a gift card.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the gift card to be credited.

***

## Gift​Card​Credit​Payload returns

* gift​Card​Credit​Transaction

  [Gift​Card​Credit​Transaction](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCardCreditTransaction)

  The gift card credit transaction that was created.

* user​Errors

  [\[Gift​Card​Transaction​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCardTransactionUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a new Gift Card Adjustment

  #### Query

  ```graphql
  mutation giftCardCredit($id: ID!, $creditInput: GiftCardCreditInput!) {
    giftCardCredit(id: $id, creditInput: $creditInput) {
      giftCardCreditTransaction {
        id
        amount {
          amount
          currencyCode
        }
        processedAt
        note
        giftCard {
          id
          balance {
            amount
            currencyCode
          }
        }
      }
      userErrors {
        message
        field
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/GiftCard/411106674",
    "creditInput": {
      "creditAmount": {
        "amount": "10",
        "currencyCode": "USD"
      },
      "processedAt": "2024-09-09T12:48:33-04:00",
      "note": "A note."
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
  "query": "mutation giftCardCredit($id: ID!, $creditInput: GiftCardCreditInput!) { giftCardCredit(id: $id, creditInput: $creditInput) { giftCardCreditTransaction { id amount { amount currencyCode } processedAt note giftCard { id balance { amount currencyCode } } } userErrors { message field code } } }",
   "variables": {
      "id": "gid://shopify/GiftCard/411106674",
      "creditInput": {
        "creditAmount": {
          "amount": "10",
          "currencyCode": "USD"
        },
        "processedAt": "2024-09-09T12:48:33-04:00",
        "note": "A note."
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
    mutation giftCardCredit($id: ID!, $creditInput: GiftCardCreditInput!) {
      giftCardCredit(id: $id, creditInput: $creditInput) {
        giftCardCreditTransaction {
          id
          amount {
            amount
            currencyCode
          }
          processedAt
          note
          giftCard {
            id
            balance {
              amount
              currencyCode
            }
          }
        }
        userErrors {
          message
          field
          code
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/GiftCard/411106674",
          "creditInput": {
              "creditAmount": {
                  "amount": "10",
                  "currencyCode": "USD"
              },
              "processedAt": "2024-09-09T12:48:33-04:00",
              "note": "A note."
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
    mutation giftCardCredit($id: ID!, $creditInput: GiftCardCreditInput!) {
      giftCardCredit(id: $id, creditInput: $creditInput) {
        giftCardCreditTransaction {
          id
          amount {
            amount
            currencyCode
          }
          processedAt
          note
          giftCard {
            id
            balance {
              amount
              currencyCode
            }
          }
        }
        userErrors {
          message
          field
          code
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/GiftCard/411106674",
    "creditInput": {
      "creditAmount": {
        "amount": "10",
        "currencyCode": "USD"
      },
      "processedAt": "2024-09-09T12:48:33-04:00",
      "note": "A note."
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation giftCardCredit($id: ID!, $creditInput: GiftCardCreditInput!) {
        giftCardCredit(id: $id, creditInput: $creditInput) {
          giftCardCreditTransaction {
            id
            amount {
              amount
              currencyCode
            }
            processedAt
            note
            giftCard {
              id
              balance {
                amount
                currencyCode
              }
            }
          }
          userErrors {
            message
            field
            code
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/GiftCard/411106674",
          "creditInput": {
              "creditAmount": {
                  "amount": "10",
                  "currencyCode": "USD"
              },
              "processedAt": "2024-09-09T12:48:33-04:00",
              "note": "A note."
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation giftCardCredit($id: ID!, $creditInput: GiftCardCreditInput!) {
    giftCardCredit(id: $id, creditInput: $creditInput) {
      giftCardCreditTransaction {
        id
        amount {
          amount
          currencyCode
        }
        processedAt
        note
        giftCard {
          id
          balance {
            amount
            currencyCode
          }
        }
      }
      userErrors {
        message
        field
        code
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/GiftCard/411106674",
    "creditInput": {
      "creditAmount": {
        "amount": "10",
        "currencyCode": "USD"
      },
      "processedAt": "2024-09-09T12:48:33-04:00",
      "note": "A note."
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCardCredit": {
      "giftCardCreditTransaction": {
        "id": "gid://shopify/GiftCardCreditTransaction/1064273912",
        "amount": {
          "amount": "10.0",
          "currencyCode": "USD"
        },
        "processedAt": "2024-09-09T16:48:33Z",
        "note": "A note.",
        "giftCard": {
          "id": "gid://shopify/GiftCard/411106674",
          "balance": {
            "amount": "35.0",
            "currencyCode": "USD"
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### giftCardCredit reference
