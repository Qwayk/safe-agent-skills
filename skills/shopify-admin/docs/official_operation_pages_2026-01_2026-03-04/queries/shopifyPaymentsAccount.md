---
title: shopifyPaymentsAccount - GraphQL Admin
description: >-
  Returns the Shopify Payments account information for the shop. Includes
  current balances across all currencies, payout schedules, and bank account
  configurations.


  The account includes
  [`ShopifyPaymentsBalanceTransaction`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsBalanceTransaction)
  records showing charges, refunds, and adjustments that affect your balance.
  Also includes
  [`ShopifyPaymentsDispute`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDispute)
  records and
  [`ShopifyPaymentsPayout`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsPayout)
  history between the account and connected
  [`ShopifyPaymentsBankAccount`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsBankAccount)
  configurations.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/shopifyPaymentsAccount
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/shopifyPaymentsAccount.md
---

# shopify​Payments​Account

query

Returns the Shopify Payments account information for the shop. Includes current balances across all currencies, payout schedules, and bank account configurations.

The account includes [`ShopifyPaymentsBalanceTransaction`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsBalanceTransaction) records showing charges, refunds, and adjustments that affect your balance. Also includes [`ShopifyPaymentsDispute`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsDispute) records and [`ShopifyPaymentsPayout`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsPayout) history between the account and connected [`ShopifyPaymentsBankAccount`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsBankAccount) configurations.

## Possible returns

* Shopify​Payments​Account

  [Shopify​Payments​Account](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsAccount)

  Financial account information for merchants using Shopify Payments. Tracks current balances across all supported currencies, payout schedules, and [`ShopifyPaymentsBalanceTransaction`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsBalanceTransaction) records.

  The account includes configuration details such as [`ShopifyPaymentsBankAccount`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsBankAccount) objects for receiving [`ShopifyPaymentsPayout`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsPayout) transfers, statement descriptors that appear on customer credit card statements, and the [`ShopifyPaymentsPayoutSchedule`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsPayoutSchedule) that determines when funds transfer to your bank. Access balance transactions to review individual charges, refunds, and adjustments that affect your account balance. Query payouts to track money movement between your Shopify Payments balance and bank accounts.

  * account​Opener​Name

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The name of the account opener.

  * activated

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the Shopify Payments setup is completed.

  * balance

    [\[Money​V2!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyV2)

    non-null

    Current balances in all currencies for the account.

  * balance​Transactions

    [Shopify​Payments​Balance​Transaction​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ShopifyPaymentsBalanceTransactionConnection)

    non-null

    A list of balance transactions associated with the shop.

    * hide​Transfers

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      ### Arguments

      Determines if returned transactions contain transaction type transfer.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

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

    * sort​Key

      [Balance​Transaction​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/BalanceTransactionSortKeys)

      Default:PROCESSED\_AT

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * default

          string

        * available\_on

          time

        - Filter by a case-insensitive search of multiple fields in a document.

        - Example:
          * `query=Bob Norman`
          * `query=title:green hoodie`

      * credit\_card\_last4

        string

      * currency

        string

      * * id

          id

        * payment\_method\_name

          string

        - Filter by `id` range.

        - Example:
          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

      * payments\_transfer\_id

        id

      * payout\_date

        time

      * payout\_status

        string

      * processed\_at

        time

      * tax\_reporting\_exempt

        boolean

      * transaction\_type

        string

    * saved​Search​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

    ***

  * bank​Accounts

    [Shopify​Payments​Bank​Account​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ShopifyPaymentsBankAccountConnection)

    non-null

    All bank accounts configured for the Shopify Payments account.

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

  * charge​Statement​Descriptors

    [Shopify​Payments​Charge​Statement​Descriptor](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/ShopifyPaymentsChargeStatementDescriptor)

    The statement descriptors used for charges.

    These descriptors appear on a customer's credit card or bank statement when they make a purchase.

  * country

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The Shopify Payments account country.

  * default​Currency

    [Currency​Code!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CurrencyCode)

    non-null

    The default payout currency for the Shopify Payments account.

  * disputes

    [Shopify​Payments​Dispute​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ShopifyPaymentsDisputeConnection)

    non-null

    All disputes that originated from a transaction made with the Shopify Payments account.

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

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * id

          id

        * initiated\_at

          time

        - Filter by `id` range.

        - Example:
          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

      * status

        string

    ***

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * onboardable

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the Shopify Payments account can be onboarded.

  * payouts

    [Shopify​Payments​Payout​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ShopifyPaymentsPayoutConnection)

    non-null

    All current and previous payouts made between the account and the bank account.

    * transaction​Type

      [Shopify​Payments​Payout​Transaction​Type](https://shopify.dev/docs/api/admin-graphql/latest/enums/ShopifyPaymentsPayoutTransactionType)

      ### Arguments

      Filter the direction of the payout.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

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

    * sort​Key

      [Payout​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/PayoutSortKeys)

      Default:ISSUED\_AT

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * default

          string

        * amount

          float

        - Filter by a case-insensitive search of multiple fields in a document.

        - Example:
          * `query=Bob Norman`
          * `query=title:green hoodie`

      * bank\_account

        string

      * currency

        string

      * * id

          id

        * issued\_at

          time

        - Filter by `id` range.

        - Example:
          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

      * ledger\_type

        string

      * status

        string

      * transaction\_dates

        time

    * saved​Search​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

    ***

  * payout​Schedule

    [Shopify​Payments​Payout​Schedule!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyPaymentsPayoutSchedule)

    non-null

    The payout schedule for the account.

  * payout​Statement​Descriptor

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The descriptor used for payouts.

    The descriptor appears on a merchant's bank statement when they receive a payout.

  * charge​Statement​Descriptor

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Deprecated

***

## Examples

* ### Return a list of all balance transactions

  #### Query

  ```graphql
  query {
    shopifyPaymentsAccount {
      balanceTransactions(first: 10) {
        nodes {
          id
          type
          test
          associatedPayout {
            id
            status
          }
          amount {
            amount
            currencyCode
          }
          fee {
            amount
          }
          net {
            amount
          }
          sourceId
          sourceType
          sourceOrderTransactionId
          associatedOrder {
            id
          }
          adjustmentsOrders {
            orderTransactionId
            amount {
              amount
            }
            name
          }
          adjustmentReason
        }
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
  "query": "query { shopifyPaymentsAccount { balanceTransactions(first: 10) { nodes { id type test associatedPayout { id status } amount { amount currencyCode } fee { amount } net { amount } sourceId sourceType sourceOrderTransactionId associatedOrder { id } adjustmentsOrders { orderTransactionId amount { amount } name } adjustmentReason } } } }"
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
      shopifyPaymentsAccount {
        balanceTransactions(first: 10) {
          nodes {
            id
            type
            test
            associatedPayout {
              id
              status
            }
            amount {
              amount
              currencyCode
            }
            fee {
              amount
            }
            net {
              amount
            }
            sourceId
            sourceType
            sourceOrderTransactionId
            associatedOrder {
              id
            }
            adjustmentsOrders {
              orderTransactionId
              amount {
                amount
              }
              name
            }
            adjustmentReason
          }
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
      shopifyPaymentsAccount {
        balanceTransactions(first: 10) {
          nodes {
            id
            type
            test
            associatedPayout {
              id
              status
            }
            amount {
              amount
              currencyCode
            }
            fee {
              amount
            }
            net {
              amount
            }
            sourceId
            sourceType
            sourceOrderTransactionId
            associatedOrder {
              id
            }
            adjustmentsOrders {
              orderTransactionId
              amount {
                amount
              }
              name
            }
            adjustmentReason
          }
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
      shopifyPaymentsAccount {
        balanceTransactions(first: 10) {
          nodes {
            id
            type
            test
            associatedPayout {
              id
              status
            }
            amount {
              amount
              currencyCode
            }
            fee {
              amount
            }
            net {
              amount
            }
            sourceId
            sourceType
            sourceOrderTransactionId
            associatedOrder {
              id
            }
            adjustmentsOrders {
              orderTransactionId
              amount {
                amount
              }
              name
            }
            adjustmentReason
          }
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
    shopifyPaymentsAccount {
      balanceTransactions(first: 10) {
        nodes {
          id
          type
          test
          associatedPayout {
            id
            status
          }
          amount {
            amount
            currencyCode
          }
          fee {
            amount
          }
          net {
            amount
          }
          sourceId
          sourceType
          sourceOrderTransactionId
          associatedOrder {
            id
          }
          adjustmentsOrders {
            orderTransactionId
            amount {
              amount
            }
            name
          }
          adjustmentReason
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopifyPaymentsAccount": {
      "balanceTransactions": {
        "nodes": [
          {
            "id": "gid://shopify/ShopifyPaymentsBalanceTransaction/44598600",
            "type": "TRANSFER",
            "test": false,
            "associatedPayout": {
              "id": "gid://shopify/ShopifyPaymentsPayout/512467833",
              "status": "FAILED"
            },
            "amount": {
              "amount": "-41.9",
              "currencyCode": "USD"
            },
            "fee": {
              "amount": "0.0"
            },
            "net": {
              "amount": "-41.9"
            },
            "sourceId": "512467833",
            "sourceType": "TRANSFER",
            "sourceOrderTransactionId": null,
            "associatedOrder": null,
            "adjustmentsOrders": [],
            "adjustmentReason": null
          },
          {
            "id": "gid://shopify/ShopifyPaymentsBalanceTransaction/374523424",
            "type": "TRANSFER",
            "test": false,
            "associatedPayout": {
              "id": "gid://shopify/ShopifyPaymentsPayout/917000993",
              "status": "FAILED"
            },
            "amount": {
              "amount": "-41.9",
              "currencyCode": "USD"
            },
            "fee": {
              "amount": "0.0"
            },
            "net": {
              "amount": "-41.9"
            },
            "sourceId": "917000993",
            "sourceType": "TRANSFER",
            "sourceOrderTransactionId": null,
            "associatedOrder": null,
            "adjustmentsOrders": [],
            "adjustmentReason": null
          },
          {
            "id": "gid://shopify/ShopifyPaymentsBalanceTransaction/631321250",
            "type": "TRANSFER",
            "test": false,
            "associatedPayout": {
              "id": "gid://shopify/ShopifyPaymentsPayout/631321250",
              "status": "SCHEDULED"
            },
            "amount": {
              "amount": "-41.9",
              "currencyCode": "USD"
            },
            "fee": {
              "amount": "0.0"
            },
            "net": {
              "amount": "-41.9"
            },
            "sourceId": "631321250",
            "sourceType": "TRANSFER",
            "sourceOrderTransactionId": null,
            "associatedOrder": null,
            "adjustmentsOrders": [],
            "adjustmentReason": null
          },
          {
            "id": "gid://shopify/ShopifyPaymentsBalanceTransaction/725076685",
            "type": "TRANSFER",
            "test": false,
            "associatedPayout": {
              "id": "gid://shopify/ShopifyPaymentsPayout/725076685",
              "status": "PAID"
            },
            "amount": {
              "amount": "-41.9",
              "currencyCode": "USD"
            },
            "fee": {
              "amount": "0.0"
            },
            "net": {
              "amount": "-41.9"
            },
            "sourceId": "725076685",
            "sourceType": "TRANSFER",
            "sourceOrderTransactionId": null,
            "associatedOrder": null,
            "adjustmentsOrders": [],
            "adjustmentReason": null
          },
          {
            "id": "gid://shopify/ShopifyPaymentsBalanceTransaction/854848137",
            "type": "TRANSFER",
            "test": false,
            "associatedPayout": {
              "id": "gid://shopify/ShopifyPaymentsPayout/623721858",
              "status": "PAID"
            },
            "amount": {
              "amount": "-41.9",
              "currencyCode": "USD"
            },
            "fee": {
              "amount": "0.0"
            },
            "net": {
              "amount": "-41.9"
            },
            "sourceId": "623721858",
            "sourceType": "TRANSFER",
            "sourceOrderTransactionId": null,
            "associatedOrder": null,
            "adjustmentsOrders": [],
            "adjustmentReason": null
          },
          {
            "id": "gid://shopify/ShopifyPaymentsBalanceTransaction/867808544",
            "type": "TRANSFER",
            "test": false,
            "associatedPayout": {
              "id": "gid://shopify/ShopifyPaymentsPayout/867808544",
              "status": "PAID"
            },
            "amount": {
              "amount": "-41.9",
              "currencyCode": "USD"
            },
            "fee": {
              "amount": "0.0"
            },
            "net": {
              "amount": "-41.9"
            },
            "sourceId": "867808544",
            "sourceType": "TRANSFER",
            "sourceOrderTransactionId": null,
            "associatedOrder": null,
            "adjustmentsOrders": [],
            "adjustmentReason": null
          },
          {
            "id": "gid://shopify/ShopifyPaymentsBalanceTransaction/714327683",
            "type": "TRANSFER_FAILURE",
            "test": false,
            "associatedPayout": {
              "id": "gid://shopify/ShopifyPaymentsPayout/714327683",
              "status": "FAILED"
            },
            "amount": {
              "amount": "41.9",
              "currencyCode": "USD"
            },
            "fee": {
              "amount": "0.0"
            },
            "net": {
              "amount": "41.9"
            },
            "sourceId": "714327683",
            "sourceType": "TRANSFER",
            "sourceOrderTransactionId": null,
            "associatedOrder": null,
            "adjustmentsOrders": [],
            "adjustmentReason": null
          },
          {
            "id": "gid://shopify/ShopifyPaymentsBalanceTransaction/615671547",
            "type": "TRANSFER_FAILURE",
            "test": false,
            "associatedPayout": {
              "id": "gid://shopify/ShopifyPaymentsPayout/714327683",
              "status": "FAILED"
            },
            "amount": {
              "amount": "11.0",
              "currencyCode": "USD"
            },
            "fee": {
              "amount": "1.0"
            },
            "net": {
              "amount": "10.0"
            },
            "sourceId": null,
            "sourceType": null,
            "sourceOrderTransactionId": null,
            "associatedOrder": null,
            "adjustmentsOrders": [],
            "adjustmentReason": null
          },
          {
            "id": "gid://shopify/ShopifyPaymentsBalanceTransaction/965204187",
            "type": "TRANSFER",
            "test": false,
            "associatedPayout": {
              "id": "gid://shopify/ShopifyPaymentsPayout/39438702",
              "status": "IN_TRANSIT"
            },
            "amount": {
              "amount": "-43.12",
              "currencyCode": "USD"
            },
            "fee": {
              "amount": "0.0"
            },
            "net": {
              "amount": "-43.12"
            },
            "sourceId": "39438702",
            "sourceType": "TRANSFER",
            "sourceOrderTransactionId": null,
            "associatedOrder": null,
            "adjustmentsOrders": [],
            "adjustmentReason": null
          },
          {
            "id": "gid://shopify/ShopifyPaymentsBalanceTransaction/922259259",
            "type": "TRANSFER_FAILURE",
            "test": false,
            "associatedPayout": {
              "id": null,
              "status": "PENDING"
            },
            "amount": {
              "amount": "43.12",
              "currencyCode": "USD"
            },
            "fee": {
              "amount": "0.0"
            },
            "net": {
              "amount": "43.12"
            },
            "sourceId": "512467833",
            "sourceType": "TRANSFER",
            "sourceOrderTransactionId": null,
            "associatedOrder": null,
            "adjustmentsOrders": [],
            "adjustmentReason": null
          }
        ]
      }
    }
  }
  ```

* ### Return a list of all disputes

  #### Query

  ```graphql
  query ShopifyPaymentsListDisputes {
    shopifyPaymentsAccount {
      disputes(first: 10) {
        edges {
          node {
            amount {
              amount
              currencyCode
            }
            evidenceDueBy
            evidenceSentOn
            finalizedOn
            id
            initiatedAt
            reasonDetails {
              reason
              networkReasonCode
            }
            status
            type
          }
        }
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
  "query": "query ShopifyPaymentsListDisputes { shopifyPaymentsAccount { disputes(first: 10) { edges { node { amount { amount currencyCode } evidenceDueBy evidenceSentOn finalizedOn id initiatedAt reasonDetails { reason networkReasonCode } status type } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query ShopifyPaymentsListDisputes {
      shopifyPaymentsAccount {
        disputes(first: 10) {
          edges {
            node {
              amount {
                amount
                currencyCode
              }
              evidenceDueBy
              evidenceSentOn
              finalizedOn
              id
              initiatedAt
              reasonDetails {
                reason
                networkReasonCode
              }
              status
              type
            }
          }
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
    query ShopifyPaymentsListDisputes {
      shopifyPaymentsAccount {
        disputes(first: 10) {
          edges {
            node {
              amount {
                amount
                currencyCode
              }
              evidenceDueBy
              evidenceSentOn
              finalizedOn
              id
              initiatedAt
              reasonDetails {
                reason
                networkReasonCode
              }
              status
              type
            }
          }
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
    data: `query ShopifyPaymentsListDisputes {
      shopifyPaymentsAccount {
        disputes(first: 10) {
          edges {
            node {
              amount {
                amount
                currencyCode
              }
              evidenceDueBy
              evidenceSentOn
              finalizedOn
              id
              initiatedAt
              reasonDetails {
                reason
                networkReasonCode
              }
              status
              type
            }
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ShopifyPaymentsListDisputes {
    shopifyPaymentsAccount {
      disputes(first: 10) {
        edges {
          node {
            amount {
              amount
              currencyCode
            }
            evidenceDueBy
            evidenceSentOn
            finalizedOn
            id
            initiatedAt
            reasonDetails {
              reason
              networkReasonCode
            }
            status
            type
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopifyPaymentsAccount": {
      "disputes": {
        "edges": [
          {
            "node": {
              "amount": {
                "amount": "100.0",
                "currencyCode": "USD"
              },
              "evidenceDueBy": "2013-07-03T19:00:00-04:00",
              "evidenceSentOn": "2013-07-04T07:00:00-04:00",
              "finalizedOn": null,
              "id": "gid://shopify/ShopifyPaymentsDispute/1052608616",
              "initiatedAt": "2013-05-04T00:00:00Z",
              "reasonDetails": {
                "reason": "FRAUDULENT",
                "networkReasonCode": "4827"
              },
              "status": "WON",
              "type": "CHARGEBACK"
            }
          },
          {
            "node": {
              "amount": {
                "amount": "11.5",
                "currencyCode": "USD"
              },
              "evidenceDueBy": "2024-11-20T19:00:00-05:00",
              "evidenceSentOn": null,
              "finalizedOn": null,
              "id": "gid://shopify/ShopifyPaymentsDispute/815713555",
              "initiatedAt": "2013-05-04T00:00:00Z",
              "reasonDetails": {
                "reason": "CREDIT_NOT_PROCESSED",
                "networkReasonCode": "4827"
              },
              "status": "NEEDS_RESPONSE",
              "type": "CHARGEBACK"
            }
          },
          {
            "node": {
              "amount": {
                "amount": "11.5",
                "currencyCode": "USD"
              },
              "evidenceDueBy": "2013-07-03T19:00:00-04:00",
              "evidenceSentOn": "2013-07-04T07:00:00-04:00",
              "finalizedOn": null,
              "id": "gid://shopify/ShopifyPaymentsDispute/782360659",
              "initiatedAt": "2013-05-04T00:00:00Z",
              "reasonDetails": {
                "reason": "FRAUDULENT",
                "networkReasonCode": "4827"
              },
              "status": "WON",
              "type": "CHARGEBACK"
            }
          },
          {
            "node": {
              "amount": {
                "amount": "11.5",
                "currencyCode": "USD"
              },
              "evidenceDueBy": null,
              "evidenceSentOn": null,
              "finalizedOn": null,
              "id": "gid://shopify/ShopifyPaymentsDispute/670893524",
              "initiatedAt": "2013-05-04T00:00:00Z",
              "reasonDetails": {
                "reason": "FRAUDULENT",
                "networkReasonCode": "4827"
              },
              "status": "NEEDS_RESPONSE",
              "type": "INQUIRY"
            }
          },
          {
            "node": {
              "amount": {
                "amount": "11.5",
                "currencyCode": "USD"
              },
              "evidenceDueBy": "2024-11-20T19:00:00-05:00",
              "evidenceSentOn": null,
              "finalizedOn": null,
              "id": "gid://shopify/ShopifyPaymentsDispute/598735659",
              "initiatedAt": "2013-05-04T00:00:00Z",
              "reasonDetails": {
                "reason": "FRAUDULENT",
                "networkReasonCode": "4827"
              },
              "status": "NEEDS_RESPONSE",
              "type": "CHARGEBACK"
            }
          },
          {
            "node": {
              "amount": {
                "amount": "100.0",
                "currencyCode": "USD"
              },
              "evidenceDueBy": "2024-11-20T19:00:00-05:00",
              "evidenceSentOn": null,
              "finalizedOn": null,
              "id": "gid://shopify/ShopifyPaymentsDispute/297752803",
              "initiatedAt": "2013-05-04T00:00:00Z",
              "reasonDetails": {
                "reason": "FRAUDULENT",
                "networkReasonCode": "4827"
              },
              "status": "LOST",
              "type": "CHARGEBACK"
            }
          },
          {
            "node": {
              "amount": {
                "amount": "11.5",
                "currencyCode": "USD"
              },
              "evidenceDueBy": "2024-11-20T19:00:00-05:00",
              "evidenceSentOn": null,
              "finalizedOn": null,
              "id": "gid://shopify/ShopifyPaymentsDispute/257169523",
              "initiatedAt": "2013-05-04T00:00:00Z",
              "reasonDetails": {
                "reason": "FRAUDULENT",
                "networkReasonCode": "4827"
              },
              "status": "NEEDS_RESPONSE",
              "type": "CHARGEBACK"
            }
          },
          {
            "node": {
              "amount": {
                "amount": "11.5",
                "currencyCode": "USD"
              },
              "evidenceDueBy": "2024-11-20T19:00:00-05:00",
              "evidenceSentOn": "2024-11-07T19:00:00-05:00",
              "finalizedOn": null,
              "id": "gid://shopify/ShopifyPaymentsDispute/85190714",
              "initiatedAt": "2013-05-04T00:00:00Z",
              "reasonDetails": {
                "reason": "FRAUDULENT",
                "networkReasonCode": "4827"
              },
              "status": "UNDER_REVIEW",
              "type": "CHARGEBACK"
            }
          },
          {
            "node": {
              "amount": {
                "amount": "100.0",
                "currencyCode": "USD"
              },
              "evidenceDueBy": "2024-11-20T19:00:00-05:00",
              "evidenceSentOn": null,
              "finalizedOn": null,
              "id": "gid://shopify/ShopifyPaymentsDispute/46484353",
              "initiatedAt": "2013-05-04T00:00:00Z",
              "reasonDetails": {
                "reason": "FRAUDULENT",
                "networkReasonCode": "4827"
              },
              "status": "LOST",
              "type": "CHARGEBACK"
            }
          },
          {
            "node": {
              "amount": {
                "amount": "11.5",
                "currencyCode": "USD"
              },
              "evidenceDueBy": "2024-11-20T19:00:00-05:00",
              "evidenceSentOn": null,
              "finalizedOn": null,
              "id": "gid://shopify/ShopifyPaymentsDispute/35982383",
              "initiatedAt": "2013-05-04T00:00:00Z",
              "reasonDetails": {
                "reason": "SUBSCRIPTION_CANCELLED",
                "networkReasonCode": "4827"
              },
              "status": "NEEDS_RESPONSE",
              "type": "CHARGEBACK"
            }
          }
        ]
      }
    }
  }
  ```

* ### Return a list of all payouts

  #### Query

  ```graphql
  query ShopifyPaymentsPayoutShow {
    shopifyPaymentsAccount {
      payouts(first: 10) {
        nodes {
          id
          issuedAt
          net {
            amount
            currencyCode
          }
          status
          transactionType
        }
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
  "query": "query ShopifyPaymentsPayoutShow { shopifyPaymentsAccount { payouts(first: 10) { nodes { id issuedAt net { amount currencyCode } status transactionType } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query ShopifyPaymentsPayoutShow {
      shopifyPaymentsAccount {
        payouts(first: 10) {
          nodes {
            id
            issuedAt
            net {
              amount
              currencyCode
            }
            status
            transactionType
          }
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
    query ShopifyPaymentsPayoutShow {
      shopifyPaymentsAccount {
        payouts(first: 10) {
          nodes {
            id
            issuedAt
            net {
              amount
              currencyCode
            }
            status
            transactionType
          }
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
    data: `query ShopifyPaymentsPayoutShow {
      shopifyPaymentsAccount {
        payouts(first: 10) {
          nodes {
            id
            issuedAt
            net {
              amount
              currencyCode
            }
            status
            transactionType
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ShopifyPaymentsPayoutShow {
    shopifyPaymentsAccount {
      payouts(first: 10) {
        nodes {
          id
          issuedAt
          net {
            amount
            currencyCode
          }
          status
          transactionType
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopifyPaymentsAccount": {
      "payouts": {
        "nodes": [
          {
            "id": "gid://shopify/ShopifyPaymentsPayout/623721858",
            "issuedAt": "2012-11-12T00:00:00Z",
            "net": {
              "amount": "41.9",
              "currencyCode": "USD"
            },
            "status": "PAID",
            "transactionType": "DEPOSIT"
          },
          {
            "id": "gid://shopify/ShopifyPaymentsPayout/631321250",
            "issuedAt": "2012-11-12T00:00:00Z",
            "net": {
              "amount": "41.9",
              "currencyCode": "USD"
            },
            "status": "SCHEDULED",
            "transactionType": "DEPOSIT"
          },
          {
            "id": "gid://shopify/ShopifyPaymentsPayout/714327683",
            "issuedAt": "2012-11-12T00:00:00Z",
            "net": {
              "amount": "41.9",
              "currencyCode": "USD"
            },
            "status": "FAILED",
            "transactionType": "DEPOSIT"
          },
          {
            "id": "gid://shopify/ShopifyPaymentsPayout/725076685",
            "issuedAt": "2012-11-12T00:00:00Z",
            "net": {
              "amount": "41.9",
              "currencyCode": "USD"
            },
            "status": "PAID",
            "transactionType": "DEPOSIT"
          },
          {
            "id": "gid://shopify/ShopifyPaymentsPayout/867808544",
            "issuedAt": "2012-11-12T00:00:00Z",
            "net": {
              "amount": "41.9",
              "currencyCode": "USD"
            },
            "status": "PAID",
            "transactionType": "DEPOSIT"
          },
          {
            "id": "gid://shopify/ShopifyPaymentsPayout/917000993",
            "issuedAt": "2012-11-13T00:00:00Z",
            "net": {
              "amount": "41.9",
              "currencyCode": "USD"
            },
            "status": "FAILED",
            "transactionType": "DEPOSIT"
          },
          {
            "id": "gid://shopify/ShopifyPaymentsPayout/39438702",
            "issuedAt": "2013-11-01T00:00:00Z",
            "net": {
              "amount": "43.12",
              "currencyCode": "USD"
            },
            "status": "SCHEDULED",
            "transactionType": "DEPOSIT"
          },
          {
            "id": "gid://shopify/ShopifyPaymentsPayout/512467833",
            "issuedAt": "2013-12-01T00:00:00Z",
            "net": {
              "amount": "43.12",
              "currencyCode": "USD"
            },
            "status": "FAILED",
            "transactionType": "DEPOSIT"
          }
        ]
      }
    }
  }
  ```

* ### Return a single payout

  #### Query

  ```graphql
  query ShopifyPaymentsPayoutShow {
    shopifyPaymentsAccount {
      payouts(first: 10, query: "id:623721858") {
        nodes {
          id
          issuedAt
          net {
            amount
            currencyCode
          }
          status
          transactionType
        }
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
  "query": "query ShopifyPaymentsPayoutShow { shopifyPaymentsAccount { payouts(first: 10, query: \"id:623721858\") { nodes { id issuedAt net { amount currencyCode } status transactionType } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query ShopifyPaymentsPayoutShow {
      shopifyPaymentsAccount {
        payouts(first: 10, query: "id:623721858") {
          nodes {
            id
            issuedAt
            net {
              amount
              currencyCode
            }
            status
            transactionType
          }
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
    query ShopifyPaymentsPayoutShow {
      shopifyPaymentsAccount {
        payouts(first: 10, query: "id:623721858") {
          nodes {
            id
            issuedAt
            net {
              amount
              currencyCode
            }
            status
            transactionType
          }
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
    data: `query ShopifyPaymentsPayoutShow {
      shopifyPaymentsAccount {
        payouts(first: 10, query: "id:623721858") {
          nodes {
            id
            issuedAt
            net {
              amount
              currencyCode
            }
            status
            transactionType
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ShopifyPaymentsPayoutShow {
    shopifyPaymentsAccount {
      payouts(first: 10, query: "id:623721858") {
        nodes {
          id
          issuedAt
          net {
            amount
            currencyCode
          }
          status
          transactionType
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "shopifyPaymentsAccount": {
      "payouts": {
        "nodes": [
          {
            "id": "gid://shopify/ShopifyPaymentsPayout/623721858",
            "issuedAt": "2012-11-12T00:00:00Z",
            "net": {
              "amount": "41.9",
              "currencyCode": "USD"
            },
            "status": "PAID",
            "transactionType": "DEPOSIT"
          }
        ]
      }
    }
  }
  ```

* ### Return the current balance

  #### Query

  ```graphql
  query ShopifyPaymentsShowBalance {
    shopifyPaymentsAccount {
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
  "query": "query ShopifyPaymentsShowBalance { shopifyPaymentsAccount { balance { amount currencyCode } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query ShopifyPaymentsShowBalance {
      shopifyPaymentsAccount {
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
    query ShopifyPaymentsShowBalance {
      shopifyPaymentsAccount {
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
    data: `query ShopifyPaymentsShowBalance {
      shopifyPaymentsAccount {
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
  'query ShopifyPaymentsShowBalance {
    shopifyPaymentsAccount {
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
    "shopifyPaymentsAccount": {
      "balance": [
        {
          "amount": "0.0",
          "currencyCode": "USD"
        }
      ]
    }
  }
  ```
