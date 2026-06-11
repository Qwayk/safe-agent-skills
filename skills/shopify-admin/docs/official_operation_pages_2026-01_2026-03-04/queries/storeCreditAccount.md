---
title: storeCreditAccount - GraphQL Admin
description: >-
  Retrieves a
  [`StoreCreditAccount`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StoreCreditAccount)
  by ID. Store credit accounts hold monetary balances that account owners can
  use at checkout. The owner is either a
  [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)
  or a
  [`CompanyLocation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/storeCreditAccount'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/storeCreditAccount.md
---

# store​Credit​Account

query

Retrieves a [`StoreCreditAccount`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StoreCreditAccount) by ID. Store credit accounts hold monetary balances that account owners can use at checkout. The owner is either a [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer) or a [`CompanyLocation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the store credit account to return.

***

## Possible returns

* Store​Credit​Account

  [Store​Credit​Account](https://shopify.dev/docs/api/admin-graphql/latest/objects/StoreCreditAccount)

  A store credit account contains a monetary balance that can be redeemed at checkout for purchases in the shop. The account is held in the specified currency and has an owner that cannot be transferred.

  The account balance is redeemable at checkout only when the owner is authenticated via [new customer accounts authentication](https://shopify.dev/docs/api/customer).

  * balance

    [Money​V2!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyV2)

    non-null

    The current balance of the store credit account.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * owner

    [Has​Store​Credit​Accounts!](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/HasStoreCreditAccounts)

    non-null

    The owner of the store credit account.

  * transactions

    [Store​Credit​Account​Transaction​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/StoreCreditAccountTransactionConnection)

    non-null

    The transaction history of the store credit account.

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

    * sort​Key

      [Transaction​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/TransactionSortKeys)

      Default:CREATED\_AT

      Sort the underlying list by the given key.

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * expires\_at

          time

        * id

          id

        * type

          string

        - Filter transactions by expiry date. Only applicable to StoreCreditAccountCreditTransaction objects. All other objects are handled as if they have a null expiry date.

        - Example:

          * `expires_at:<='2025-01-01T00:00:00+01:00'`
          * `expires_at:<='2025-12-31T23:00:00Z'`

          Filter by `id` range.

        - Example:

          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

          Filter transactions by type. Any value other than the accepted values will be ignored.

          Valid values:

          * `credit`
          * `debit`
          * `debit_revert`
          * `expiration`

          Example:

          * `type:expiration`
          * `type:credit OR type:debit_revert`

    ***

***

## Examples

* ### Get a store credit account by account ID

  #### Query

  ```graphql
  query storeCreditAccount($accountId: ID!) {
    storeCreditAccount(id: $accountId) {
      id
      balance {
        amount
        currencyCode
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "accountId": "gid://shopify/StoreCreditAccount/316863792"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query storeCreditAccount($accountId: ID!) { storeCreditAccount(id: $accountId) { id balance { amount currencyCode } } }",
   "variables": {
      "accountId": "gid://shopify/StoreCreditAccount/316863792"
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
    query storeCreditAccount($accountId: ID!) {
      storeCreditAccount(id: $accountId) {
        id
        balance {
          amount
          currencyCode
        }
      }
    }`,
    {
      variables: {
          "accountId": "gid://shopify/StoreCreditAccount/316863792"
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
    query storeCreditAccount($accountId: ID!) {
      storeCreditAccount(id: $accountId) {
        id
        balance {
          amount
          currencyCode
        }
      }
    }
  QUERY

  variables = {
    "accountId": "gid://shopify/StoreCreditAccount/316863792"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query storeCreditAccount($accountId: ID!) {
        storeCreditAccount(id: $accountId) {
          id
          balance {
            amount
            currencyCode
          }
        }
      }`,
      "variables": {
          "accountId": "gid://shopify/StoreCreditAccount/316863792"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query storeCreditAccount($accountId: ID!) {
    storeCreditAccount(id: $accountId) {
      id
      balance {
        amount
        currencyCode
      }
    }
  }' \
  --variables \
  '{
    "accountId": "gid://shopify/StoreCreditAccount/316863792"
  }'
  ```

  #### Response

  ```json
  {
    "storeCreditAccount": {
      "id": "gid://shopify/StoreCreditAccount/316863792",
      "balance": {
        "amount": "11.11",
        "currencyCode": "USD"
      }
    }
  }
  ```

* ### Get the first two expirable credit transactions of a store credit account

  #### Query

  ```graphql
  query storeCreditAccount($accountId: ID!, $first: Int!) {
    storeCreditAccount(id: $accountId) {
      id
      transactions(first: $first, query: "type:credit AND expires_at:*") {
        edges {
          node {
            amount {
              amount
              currencyCode
            }
            balanceAfterTransaction {
              amount
              currencyCode
            }
            createdAt
            ... on StoreCreditAccountCreditTransaction {
              id
              expiresAt
              remainingAmount {
                amount
                currencyCode
              }
            }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "accountId": "gid://shopify/StoreCreditAccount/669614221",
    "first": 2
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query storeCreditAccount($accountId: ID!, $first: Int!) { storeCreditAccount(id: $accountId) { id transactions(first: $first, query: \"type:credit AND expires_at:*\") { edges { node { amount { amount currencyCode } balanceAfterTransaction { amount currencyCode } createdAt ... on StoreCreditAccountCreditTransaction { id expiresAt remainingAmount { amount currencyCode } } } } } } }",
   "variables": {
      "accountId": "gid://shopify/StoreCreditAccount/669614221",
      "first": 2
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
    query storeCreditAccount($accountId: ID!, $first: Int!) {
      storeCreditAccount(id: $accountId) {
        id
        transactions(first: $first, query: "type:credit AND expires_at:*") {
          edges {
            node {
              amount {
                amount
                currencyCode
              }
              balanceAfterTransaction {
                amount
                currencyCode
              }
              createdAt
              ... on StoreCreditAccountCreditTransaction {
                id
                expiresAt
                remainingAmount {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "accountId": "gid://shopify/StoreCreditAccount/669614221",
          "first": 2
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
    query storeCreditAccount($accountId: ID!, $first: Int!) {
      storeCreditAccount(id: $accountId) {
        id
        transactions(first: $first, query: "type:credit AND expires_at:*") {
          edges {
            node {
              amount {
                amount
                currencyCode
              }
              balanceAfterTransaction {
                amount
                currencyCode
              }
              createdAt
              ... on StoreCreditAccountCreditTransaction {
                id
                expiresAt
                remainingAmount {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "accountId": "gid://shopify/StoreCreditAccount/669614221",
    "first": 2
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query storeCreditAccount($accountId: ID!, $first: Int!) {
        storeCreditAccount(id: $accountId) {
          id
          transactions(first: $first, query: "type:credit AND expires_at:*") {
            edges {
              node {
                amount {
                  amount
                  currencyCode
                }
                balanceAfterTransaction {
                  amount
                  currencyCode
                }
                createdAt
                ... on StoreCreditAccountCreditTransaction {
                  id
                  expiresAt
                  remainingAmount {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "accountId": "gid://shopify/StoreCreditAccount/669614221",
          "first": 2
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query storeCreditAccount($accountId: ID!, $first: Int!) {
    storeCreditAccount(id: $accountId) {
      id
      transactions(first: $first, query: "type:credit AND expires_at:*") {
        edges {
          node {
            amount {
              amount
              currencyCode
            }
            balanceAfterTransaction {
              amount
              currencyCode
            }
            createdAt
            ... on StoreCreditAccountCreditTransaction {
              id
              expiresAt
              remainingAmount {
                amount
                currencyCode
              }
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "accountId": "gid://shopify/StoreCreditAccount/669614221",
    "first": 2
  }'
  ```

  #### Response

  ```json
  {
    "storeCreditAccount": {
      "id": "gid://shopify/StoreCreditAccount/669614221",
      "transactions": {
        "edges": [
          {
            "node": {
              "amount": {
                "amount": "100.0",
                "currencyCode": "USD"
              },
              "balanceAfterTransaction": {
                "amount": "100.0",
                "currencyCode": "USD"
              },
              "createdAt": "2024-01-01T00:00:00Z",
              "id": "gid://shopify/StoreCreditAccountCreditTransaction/870993577",
              "expiresAt": "2024-02-01T00:00:00Z",
              "remainingAmount": {
                "amount": "50.0",
                "currencyCode": "USD"
              }
            }
          },
          {
            "node": {
              "amount": {
                "amount": "54.99",
                "currencyCode": "USD"
              },
              "balanceAfterTransaction": {
                "amount": "104.99",
                "currencyCode": "USD"
              },
              "createdAt": "2024-01-03T00:00:00Z",
              "id": "gid://shopify/StoreCreditAccountCreditTransaction/870993579",
              "expiresAt": "2024-02-03T00:00:00Z",
              "remainingAmount": {
                "amount": "54.99",
                "currencyCode": "USD"
              }
            }
          }
        ]
      }
    }
  }
  ```

* ### Get the four most recent transactions of a store credit account

  #### Query

  ```graphql
  query storeCreditAccount($accountId: ID!, $first: Int!) {
    storeCreditAccount(id: $accountId) {
      id
      transactions(first: $first, sortKey: CREATED_AT, reverse: true) {
        edges {
          node {
            amount {
              amount
              currencyCode
            }
            balanceAfterTransaction {
              amount
              currencyCode
            }
            createdAt
            ... on StoreCreditAccountCreditTransaction {
              id
              expiresAt
              remainingAmount {
                amount
                currencyCode
              }
            }
            ... on StoreCreditAccountDebitTransaction {
              id
            }
            ... on StoreCreditAccountDebitRevertTransaction {
              id
              debitTransaction {
                id
              }
            }
            ... on StoreCreditAccountExpirationTransaction {
              creditTransaction {
                id
              }
            }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "accountId": "gid://shopify/StoreCreditAccount/669614221",
    "first": 4
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query storeCreditAccount($accountId: ID!, $first: Int!) { storeCreditAccount(id: $accountId) { id transactions(first: $first, sortKey: CREATED_AT, reverse: true) { edges { node { amount { amount currencyCode } balanceAfterTransaction { amount currencyCode } createdAt ... on StoreCreditAccountCreditTransaction { id expiresAt remainingAmount { amount currencyCode } } ... on StoreCreditAccountDebitTransaction { id } ... on StoreCreditAccountDebitRevertTransaction { id debitTransaction { id } } ... on StoreCreditAccountExpirationTransaction { creditTransaction { id } } } } } } }",
   "variables": {
      "accountId": "gid://shopify/StoreCreditAccount/669614221",
      "first": 4
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
    query storeCreditAccount($accountId: ID!, $first: Int!) {
      storeCreditAccount(id: $accountId) {
        id
        transactions(first: $first, sortKey: CREATED_AT, reverse: true) {
          edges {
            node {
              amount {
                amount
                currencyCode
              }
              balanceAfterTransaction {
                amount
                currencyCode
              }
              createdAt
              ... on StoreCreditAccountCreditTransaction {
                id
                expiresAt
                remainingAmount {
                  amount
                  currencyCode
                }
              }
              ... on StoreCreditAccountDebitTransaction {
                id
              }
              ... on StoreCreditAccountDebitRevertTransaction {
                id
                debitTransaction {
                  id
                }
              }
              ... on StoreCreditAccountExpirationTransaction {
                creditTransaction {
                  id
                }
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "accountId": "gid://shopify/StoreCreditAccount/669614221",
          "first": 4
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
    query storeCreditAccount($accountId: ID!, $first: Int!) {
      storeCreditAccount(id: $accountId) {
        id
        transactions(first: $first, sortKey: CREATED_AT, reverse: true) {
          edges {
            node {
              amount {
                amount
                currencyCode
              }
              balanceAfterTransaction {
                amount
                currencyCode
              }
              createdAt
              ... on StoreCreditAccountCreditTransaction {
                id
                expiresAt
                remainingAmount {
                  amount
                  currencyCode
                }
              }
              ... on StoreCreditAccountDebitTransaction {
                id
              }
              ... on StoreCreditAccountDebitRevertTransaction {
                id
                debitTransaction {
                  id
                }
              }
              ... on StoreCreditAccountExpirationTransaction {
                creditTransaction {
                  id
                }
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "accountId": "gid://shopify/StoreCreditAccount/669614221",
    "first": 4
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query storeCreditAccount($accountId: ID!, $first: Int!) {
        storeCreditAccount(id: $accountId) {
          id
          transactions(first: $first, sortKey: CREATED_AT, reverse: true) {
            edges {
              node {
                amount {
                  amount
                  currencyCode
                }
                balanceAfterTransaction {
                  amount
                  currencyCode
                }
                createdAt
                ... on StoreCreditAccountCreditTransaction {
                  id
                  expiresAt
                  remainingAmount {
                    amount
                    currencyCode
                  }
                }
                ... on StoreCreditAccountDebitTransaction {
                  id
                }
                ... on StoreCreditAccountDebitRevertTransaction {
                  id
                  debitTransaction {
                    id
                  }
                }
                ... on StoreCreditAccountExpirationTransaction {
                  creditTransaction {
                    id
                  }
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "accountId": "gid://shopify/StoreCreditAccount/669614221",
          "first": 4
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query storeCreditAccount($accountId: ID!, $first: Int!) {
    storeCreditAccount(id: $accountId) {
      id
      transactions(first: $first, sortKey: CREATED_AT, reverse: true) {
        edges {
          node {
            amount {
              amount
              currencyCode
            }
            balanceAfterTransaction {
              amount
              currencyCode
            }
            createdAt
            ... on StoreCreditAccountCreditTransaction {
              id
              expiresAt
              remainingAmount {
                amount
                currencyCode
              }
            }
            ... on StoreCreditAccountDebitTransaction {
              id
            }
            ... on StoreCreditAccountDebitRevertTransaction {
              id
              debitTransaction {
                id
              }
            }
            ... on StoreCreditAccountExpirationTransaction {
              creditTransaction {
                id
              }
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "accountId": "gid://shopify/StoreCreditAccount/669614221",
    "first": 4
  }'
  ```

  #### Response

  ```json
  {
    "storeCreditAccount": {
      "id": "gid://shopify/StoreCreditAccount/669614221",
      "transactions": {
        "edges": [
          {
            "node": {
              "amount": {
                "amount": "-90.0",
                "currencyCode": "USD"
              },
              "balanceAfterTransaction": {
                "amount": "0.0",
                "currencyCode": "USD"
              },
              "createdAt": "2024-02-01T00:00:00Z",
              "creditTransaction": {
                "id": "gid://shopify/StoreCreditAccountCreditTransaction/870993581"
              }
            }
          },
          {
            "node": {
              "amount": {
                "amount": "40.0",
                "currencyCode": "USD"
              },
              "balanceAfterTransaction": {
                "amount": "90.0",
                "currencyCode": "USD"
              },
              "createdAt": "2024-01-03T00:00:00Z",
              "id": "gid://shopify/StoreCreditAccountDebitRevertTransaction/870993583",
              "debitTransaction": {
                "id": "gid://shopify/StoreCreditAccountDebitTransaction/870993582"
              }
            }
          },
          {
            "node": {
              "amount": {
                "amount": "-50.0",
                "currencyCode": "USD"
              },
              "balanceAfterTransaction": {
                "amount": "50.0",
                "currencyCode": "USD"
              },
              "createdAt": "2024-01-02T00:00:00Z",
              "id": "gid://shopify/StoreCreditAccountDebitTransaction/870993582"
            }
          },
          {
            "node": {
              "amount": {
                "amount": "100.0",
                "currencyCode": "USD"
              },
              "balanceAfterTransaction": {
                "amount": "100.0",
                "currencyCode": "USD"
              },
              "createdAt": "2024-01-01T00:00:00Z",
              "id": "gid://shopify/StoreCreditAccountCreditTransaction/870993581",
              "expiresAt": "2024-02-01T00:00:00Z",
              "remainingAmount": {
                "amount": "90.0",
                "currencyCode": "USD"
              }
            }
          }
        ]
      }
    }
  }
  ```
