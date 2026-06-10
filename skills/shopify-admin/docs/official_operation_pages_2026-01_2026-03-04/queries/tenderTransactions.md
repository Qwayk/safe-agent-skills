---
title: tenderTransactions - GraphQL Admin
description: >-
  Transactions representing a movement of money between customers and the shop.
  Each transaction records the amount, payment method, processing details, and
  the associated
  [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order).


  Positive amounts indicate customer payments to the merchant. Negative amounts
  represent refunds from the merchant to the customer. Use the
  [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/tenderTransactions#arguments-query)
  parameter to filter transactions by attributes such as transaction ID,
  processing date, and point-of-sale device ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/tenderTransactions'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/tenderTransactions.md
---

# tender​Transactions

query

Transactions representing a movement of money between customers and the shop. Each transaction records the amount, payment method, processing details, and the associated [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order).

Positive amounts indicate customer payments to the merchant. Negative amounts represent refunds from the merchant to the customer. Use the [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/tenderTransactions#arguments-query) parameter to filter transactions by attributes such as transaction ID, processing date, and point-of-sale device ID.

## TenderTransactionConnection arguments

[TenderTransactionConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/TenderTransactionConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * id

      id

    * point\_of\_sale\_device\_id

      id

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * processed\_at

    time

  * test

    boolean

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Tender​Transaction​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TenderTransactionEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Tender​Transaction!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TenderTransaction)

  non-null

  A list of nodes that are contained in TenderTransactionEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieves a list of tender transactions

  #### Query

  ```graphql
  query TenderTransactionList {
    tenderTransactions(first: 10) {
      nodes {
        id
        order {
          id
        }
        amount {
          amount
          currencyCode
        }
        user {
          id
        }
        test
        processedAt
        remoteReference
        paymentDetails: transactionDetails {
          ... on TenderTransactionCreditCardDetails {
            creditCardCompany
            creditCardNumber
          }
        }
        paymentMethod
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
  "query": "query TenderTransactionList { tenderTransactions(first: 10) { nodes { id order { id } amount { amount currencyCode } user { id } test processedAt remoteReference paymentDetails: transactionDetails { ... on TenderTransactionCreditCardDetails { creditCardCompany creditCardNumber } } paymentMethod } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query TenderTransactionList {
      tenderTransactions(first: 10) {
        nodes {
          id
          order {
            id
          }
          amount {
            amount
            currencyCode
          }
          user {
            id
          }
          test
          processedAt
          remoteReference
          paymentDetails: transactionDetails {
            ... on TenderTransactionCreditCardDetails {
              creditCardCompany
              creditCardNumber
            }
          }
          paymentMethod
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
    query TenderTransactionList {
      tenderTransactions(first: 10) {
        nodes {
          id
          order {
            id
          }
          amount {
            amount
            currencyCode
          }
          user {
            id
          }
          test
          processedAt
          remoteReference
          paymentDetails: transactionDetails {
            ... on TenderTransactionCreditCardDetails {
              creditCardCompany
              creditCardNumber
            }
          }
          paymentMethod
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
    data: `query TenderTransactionList {
      tenderTransactions(first: 10) {
        nodes {
          id
          order {
            id
          }
          amount {
            amount
            currencyCode
          }
          user {
            id
          }
          test
          processedAt
          remoteReference
          paymentDetails: transactionDetails {
            ... on TenderTransactionCreditCardDetails {
              creditCardCompany
              creditCardNumber
            }
          }
          paymentMethod
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query TenderTransactionList {
    tenderTransactions(first: 10) {
      nodes {
        id
        order {
          id
        }
        amount {
          amount
          currencyCode
        }
        user {
          id
        }
        test
        processedAt
        remoteReference
        paymentDetails: transactionDetails {
          ... on TenderTransactionCreditCardDetails {
            creditCardCompany
            creditCardNumber
          }
        }
        paymentMethod
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "tenderTransactions": {
      "nodes": [
        {
          "id": "gid://shopify/TenderTransaction/765446009",
          "order": {
            "id": "gid://shopify/Order/148977776"
          },
          "amount": {
            "amount": "11.5",
            "currencyCode": "USD"
          },
          "user": {
            "id": "gid://shopify/StaffMember/902541635"
          },
          "test": false,
          "processedAt": "2005-07-31T15:57:11Z",
          "remoteReference": "1000",
          "paymentDetails": null,
          "paymentMethod": null
        }
      ]
    }
  }
  ```
