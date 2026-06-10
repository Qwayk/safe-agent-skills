---
title: storeCreditAccountDebit - GraphQL Admin
description: >-
  Creates a debit transaction that decreases the store credit account balance by
  the given amount.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/storeCreditAccountDebit
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/storeCreditAccountDebit.md
---

# store​Credit​Account​Debit

mutation

Requires `write_store_credit_account_transactions` access scope.

Creates a debit transaction that decreases the store credit account balance by the given amount.

## Arguments

* debit​Input

  [Store​Credit​Account​Debit​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/StoreCreditAccountDebitInput)

  required

  The input fields for a store credit account debit transaction.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the store credit account or the ID of the account owner.

***

## Store​Credit​Account​Debit​Payload returns

* store​Credit​Account​Transaction

  [Store​Credit​Account​Debit​Transaction](https://shopify.dev/docs/api/admin-graphql/latest/objects/StoreCreditAccountDebitTransaction)

  The store credit account transaction that was created.

* user​Errors

  [\[Store​Credit​Account​Debit​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/StoreCreditAccountDebitUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Debit a store credit account by account ID

  #### Query

  ```graphql
  mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
    storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
      storeCreditAccountTransaction {
        amount {
          amount
          currencyCode
        }
        account {
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
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/StoreCreditAccount/316863792",
    "debitInput": {
      "debitAmount": {
        "amount": "9.99",
        "currencyCode": "USD"
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
  "query": "mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) { storeCreditAccountDebit(id: $id, debitInput: $debitInput) { storeCreditAccountTransaction { amount { amount currencyCode } account { id balance { amount currencyCode } } } userErrors { message field } } }",
   "variables": {
      "id": "gid://shopify/StoreCreditAccount/316863792",
      "debitInput": {
        "debitAmount": {
          "amount": "9.99",
          "currencyCode": "USD"
        }
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
    mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
      storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
        storeCreditAccountTransaction {
          amount {
            amount
            currencyCode
          }
          account {
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
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/StoreCreditAccount/316863792",
          "debitInput": {
              "debitAmount": {
                  "amount": "9.99",
                  "currencyCode": "USD"
              }
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
    mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
      storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
        storeCreditAccountTransaction {
          amount {
            amount
            currencyCode
          }
          account {
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
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/StoreCreditAccount/316863792",
    "debitInput": {
      "debitAmount": {
        "amount": "9.99",
        "currencyCode": "USD"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
        storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
          storeCreditAccountTransaction {
            amount {
              amount
              currencyCode
            }
            account {
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
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/StoreCreditAccount/316863792",
          "debitInput": {
              "debitAmount": {
                  "amount": "9.99",
                  "currencyCode": "USD"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
    storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
      storeCreditAccountTransaction {
        amount {
          amount
          currencyCode
        }
        account {
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
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/StoreCreditAccount/316863792",
    "debitInput": {
      "debitAmount": {
        "amount": "9.99",
        "currencyCode": "USD"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "storeCreditAccountDebit": {
      "storeCreditAccountTransaction": {
        "amount": {
          "amount": "-9.99",
          "currencyCode": "USD"
        },
        "account": {
          "id": "gid://shopify/StoreCreditAccount/316863792",
          "balance": {
            "amount": "1.12",
            "currencyCode": "USD"
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Debit a store credit account by customer ID

  #### Query

  ```graphql
  mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
    storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
      storeCreditAccountTransaction {
        amount {
          amount
          currencyCode
        }
        account {
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
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Customer/544365967",
    "debitInput": {
      "debitAmount": {
        "amount": "9.99",
        "currencyCode": "USD"
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
  "query": "mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) { storeCreditAccountDebit(id: $id, debitInput: $debitInput) { storeCreditAccountTransaction { amount { amount currencyCode } account { id balance { amount currencyCode } } } userErrors { message field } } }",
   "variables": {
      "id": "gid://shopify/Customer/544365967",
      "debitInput": {
        "debitAmount": {
          "amount": "9.99",
          "currencyCode": "USD"
        }
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
    mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
      storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
        storeCreditAccountTransaction {
          amount {
            amount
            currencyCode
          }
          account {
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
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Customer/544365967",
          "debitInput": {
              "debitAmount": {
                  "amount": "9.99",
                  "currencyCode": "USD"
              }
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
    mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
      storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
        storeCreditAccountTransaction {
          amount {
            amount
            currencyCode
          }
          account {
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
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Customer/544365967",
    "debitInput": {
      "debitAmount": {
        "amount": "9.99",
        "currencyCode": "USD"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
        storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
          storeCreditAccountTransaction {
            amount {
              amount
              currencyCode
            }
            account {
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
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Customer/544365967",
          "debitInput": {
              "debitAmount": {
                  "amount": "9.99",
                  "currencyCode": "USD"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
    storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
      storeCreditAccountTransaction {
        amount {
          amount
          currencyCode
        }
        account {
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
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Customer/544365967",
    "debitInput": {
      "debitAmount": {
        "amount": "9.99",
        "currencyCode": "USD"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "storeCreditAccountDebit": {
      "storeCreditAccountTransaction": {
        "amount": {
          "amount": "-9.99",
          "currencyCode": "USD"
        },
        "account": {
          "id": "gid://shopify/StoreCreditAccount/316863792",
          "balance": {
            "amount": "1.12",
            "currencyCode": "USD"
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Debiting an amount that exceeds the account balance returns an error

  #### Query

  ```graphql
  mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
    storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
      storeCreditAccountTransaction {
        amount {
          amount
          currencyCode
        }
        account {
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
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/StoreCreditAccount/316863792",
    "debitInput": {
      "debitAmount": {
        "amount": "100.00",
        "currencyCode": "USD"
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
  "query": "mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) { storeCreditAccountDebit(id: $id, debitInput: $debitInput) { storeCreditAccountTransaction { amount { amount currencyCode } account { id balance { amount currencyCode } } } userErrors { message field } } }",
   "variables": {
      "id": "gid://shopify/StoreCreditAccount/316863792",
      "debitInput": {
        "debitAmount": {
          "amount": "100.00",
          "currencyCode": "USD"
        }
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
    mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
      storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
        storeCreditAccountTransaction {
          amount {
            amount
            currencyCode
          }
          account {
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
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/StoreCreditAccount/316863792",
          "debitInput": {
              "debitAmount": {
                  "amount": "100.00",
                  "currencyCode": "USD"
              }
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
    mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
      storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
        storeCreditAccountTransaction {
          amount {
            amount
            currencyCode
          }
          account {
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
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/StoreCreditAccount/316863792",
    "debitInput": {
      "debitAmount": {
        "amount": "100.00",
        "currencyCode": "USD"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
        storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
          storeCreditAccountTransaction {
            amount {
              amount
              currencyCode
            }
            account {
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
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/StoreCreditAccount/316863792",
          "debitInput": {
              "debitAmount": {
                  "amount": "100.00",
                  "currencyCode": "USD"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation storeCreditAccountDebit($id: ID!, $debitInput: StoreCreditAccountDebitInput!) {
    storeCreditAccountDebit(id: $id, debitInput: $debitInput) {
      storeCreditAccountTransaction {
        amount {
          amount
          currencyCode
        }
        account {
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
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/StoreCreditAccount/316863792",
    "debitInput": {
      "debitAmount": {
        "amount": "100.00",
        "currencyCode": "USD"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "storeCreditAccountDebit": {
      "storeCreditAccountTransaction": null,
      "userErrors": [
        {
          "message": "The store credit account does not have sufficient funds to satisfy the request",
          "field": [
            "debitInput",
            "debitAmount",
            "amount"
          ]
        }
      ]
    }
  }
  ```

* ### storeCreditAccountDebit reference
