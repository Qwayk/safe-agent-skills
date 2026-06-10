---
title: giftCard - GraphQL Admin
description: >-
  Retrieves a
  [`GiftCard`](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCard)
  by its ID. Returns the gift card's balance, transaction history,
  [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)
  information, and whether it's enabled.


  Additional fields include the initial value, expiration date, deactivation
  timestamp (if applicable), and the associated
  [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) if
  the gift card was purchased by a customer through checkout. Gift cards that
  merchants create manually won't have an associated order.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/giftCard'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/giftCard.md'
---

# gift​Card

query

Requires `read_gift_cards` access scope.

Retrieves a [`GiftCard`](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCard) by its ID. Returns the gift card's balance, transaction history, [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer) information, and whether it's enabled.

Additional fields include the initial value, expiration date, deactivation timestamp (if applicable), and the associated [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) if the gift card was purchased by a customer through checkout. Gift cards that merchants create manually won't have an associated order.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the GiftCard to return.

***

## Possible returns

* Gift​Card

  [Gift​Card](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCard)

  A gift card that customers use as a payment method. Stores the initial value, current balance, and expiration date.

  You can issue gift cards to a specific [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer) or send them to a [`GiftCardRecipient`](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCardRecipient) with a personalized message. The card tracks its transaction history through [`GiftCardCreditTransaction`](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCardCreditTransaction) and [`GiftCardDebitTransaction`](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCardDebitTransaction) records. You can create and deactivate gift cards using the [`GiftCardCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/giftCardCreate) and [`GiftCardDeactivate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/giftCardDeactivate) mutations, respectively.

  ***

  **Note:** After a gift card is deactivated, it can\&#39;t be used for further purchases or re-enabled.

  ***

  * balance

    [Money​V2!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyV2)

    non-null

    The gift card's remaining balance.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time at which the gift card was created.

  * customer

    [Customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

    The customer who will receive the gift card.

  * deactivated​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time at which the gift card was deactivated.

  * enabled

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the gift card is enabled.

  * expires​On

    [Date](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Date)

    The date at which the gift card will expire.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * initial​Value

    [Money​V2!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyV2)

    non-null

    The initial value of the gift card.

  * last​Characters

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The final four characters of the gift card code.

  * masked​Code

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The gift card code. Everything but the final four characters is masked.

  * note

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The note associated with the gift card, which isn't visible to the customer.

  * order

    [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

    The order associated with the gift card. This value is `null` if the gift card was issued manually.

  * recipient​Attributes

    [Gift​Card​Recipient](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCardRecipient)

    The recipient who will receive the gift card.

  * template​Suffix

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The theme template used to render the gift card online.

  * transactions

    [Gift​Card​Transaction​Connection](https://shopify.dev/docs/api/admin-graphql/latest/connections/GiftCardTransactionConnection)

    The transaction history of the gift card.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time at which the gift card was updated.

***

## Examples

* ### Receive a list of all Gift Card Adjustments

  #### Query

  ```graphql
  query GiftCardTransactionList($id: ID!, $firstTransactions: Int) {
    giftCard(id: $id) {
      id
      balance {
        amount
        currencyCode
      }
      transactions(first: $firstTransactions) {
        nodes {
          amount {
            amount
            currencyCode
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/GiftCard/411106674",
    "firstTransactions": 5
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query GiftCardTransactionList($id: ID!, $firstTransactions: Int) { giftCard(id: $id) { id balance { amount currencyCode } transactions(first: $firstTransactions) { nodes { amount { amount currencyCode } } } } }",
   "variables": {
      "id": "gid://shopify/GiftCard/411106674",
      "firstTransactions": 5
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
    query GiftCardTransactionList($id: ID!, $firstTransactions: Int) {
      giftCard(id: $id) {
        id
        balance {
          amount
          currencyCode
        }
        transactions(first: $firstTransactions) {
          nodes {
            amount {
              amount
              currencyCode
            }
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/GiftCard/411106674",
          "firstTransactions": 5
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
    query GiftCardTransactionList($id: ID!, $firstTransactions: Int) {
      giftCard(id: $id) {
        id
        balance {
          amount
          currencyCode
        }
        transactions(first: $firstTransactions) {
          nodes {
            amount {
              amount
              currencyCode
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/GiftCard/411106674",
    "firstTransactions": 5
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query GiftCardTransactionList($id: ID!, $firstTransactions: Int) {
        giftCard(id: $id) {
          id
          balance {
            amount
            currencyCode
          }
          transactions(first: $firstTransactions) {
            nodes {
              amount {
                amount
                currencyCode
              }
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/GiftCard/411106674",
          "firstTransactions": 5
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query GiftCardTransactionList($id: ID!, $firstTransactions: Int) {
    giftCard(id: $id) {
      id
      balance {
        amount
        currencyCode
      }
      transactions(first: $firstTransactions) {
        nodes {
          amount {
            amount
            currencyCode
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/GiftCard/411106674",
    "firstTransactions": 5
  }'
  ```

  #### Response

  ```json
  {
    "giftCard": {
      "id": "gid://shopify/GiftCard/411106674",
      "balance": {
        "amount": "25.0",
        "currencyCode": "USD"
      },
      "transactions": {
        "nodes": []
      }
    }
  }
  ```

* ### Retrieves a single gift card

  #### Description

  The following query takes a gift card ID, and returns the balance of the gift card.

  #### Query

  ```graphql
  query {
    giftCard(id: "gid://shopify/GiftCard/411106674") {
      balance {
        amount
        currencyCode
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
  "query": "query { giftCard(id: \"gid://shopify/GiftCard/411106674\") { balance { amount currencyCode } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      giftCard(id: "gid://shopify/GiftCard/411106674") {
        balance {
          amount
          currencyCode
        }
      }
    }`,
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
    query {
      giftCard(id: "gid://shopify/GiftCard/411106674") {
        balance {
          amount
          currencyCode
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      giftCard(id: "gid://shopify/GiftCard/411106674") {
        balance {
          amount
          currencyCode
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    giftCard(id: "gid://shopify/GiftCard/411106674") {
      balance {
        amount
        currencyCode
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCard": {
      "balance": {
        "amount": "25.0",
        "currencyCode": "USD"
      }
    }
  }
  ```
