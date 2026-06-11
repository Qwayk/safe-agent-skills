---
title: storeCreditAccountCredit - GraphQL Admin
description: >-
  Adds funds to a
  [`StoreCreditAccount`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StoreCreditAccount)
  by creating a
  [`StoreCreditAccountCreditTransaction`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StoreCreditAccountCreditTransaction).
  The mutation accepts either a store credit account ID, a
  [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)
  ID, or a
  [`CompanyLocation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation)
  ID. When you provide a customer or company location ID, it automatically
  creates an account if one doesn't exist for the specified currency.


  Store credit accounts are currency-specific. A single owner can have multiple
  accounts, each holding a different currency. Use the most appropriate currency
  for the given store credit account owner.


  Credits can optionally include an expiration date.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/storeCreditAccountCredit
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/storeCreditAccountCredit.md
---

# store​Credit​Account​Credit

mutation

Requires `write_store_credit_account_transactions` access scope.

Adds funds to a [`StoreCreditAccount`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StoreCreditAccount) by creating a [`StoreCreditAccountCreditTransaction`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StoreCreditAccountCreditTransaction). The mutation accepts either a store credit account ID, a [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer) ID, or a [`CompanyLocation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation) ID. When you provide a customer or company location ID, it automatically creates an account if one doesn't exist for the specified currency.

Store credit accounts are currency-specific. A single owner can have multiple accounts, each holding a different currency. Use the most appropriate currency for the given store credit account owner.

Credits can optionally include an expiration date.

## Arguments

* credit​Input

  [Store​Credit​Account​Credit​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/StoreCreditAccountCreditInput)

  required

  The input fields for a store credit account credit transaction.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the store credit account or the ID of the account owner.

***

## Store​Credit​Account​Credit​Payload returns

* store​Credit​Account​Transaction

  [Store​Credit​Account​Credit​Transaction](https://shopify.dev/docs/api/admin-graphql/latest/objects/StoreCreditAccountCreditTransaction)

  The store credit account transaction that was created.

* user​Errors

  [\[Store​Credit​Account​Credit​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/StoreCreditAccountCreditUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Credit an amount to a store credit account by customer ID

  #### Query

  ```graphql
  mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
    storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
    "creditInput": {
      "creditAmount": {
        "amount": "49.99",
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
  "query": "mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) { storeCreditAccountCredit(id: $id, creditInput: $creditInput) { storeCreditAccountTransaction { amount { amount currencyCode } account { id balance { amount currencyCode } } } userErrors { message field } } }",
   "variables": {
      "id": "gid://shopify/Customer/544365967",
      "creditInput": {
        "creditAmount": {
          "amount": "49.99",
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
    mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
      storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
          "creditInput": {
              "creditAmount": {
                  "amount": "49.99",
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
    mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
      storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
    "creditInput": {
      "creditAmount": {
        "amount": "49.99",
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
      "query": `mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
        storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
          "creditInput": {
              "creditAmount": {
                  "amount": "49.99",
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
  'mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
    storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
    "creditInput": {
      "creditAmount": {
        "amount": "49.99",
        "currencyCode": "USD"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "storeCreditAccountCredit": {
      "storeCreditAccountTransaction": {
        "amount": {
          "amount": "49.99",
          "currencyCode": "USD"
        },
        "account": {
          "id": "gid://shopify/StoreCreditAccount/316863792",
          "balance": {
            "amount": "61.1",
            "currencyCode": "USD"
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Credit an expiring amount to a store credit account by account ID

  #### Query

  ```graphql
  mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
    storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
    "creditInput": {
      "expiresAt": "2028-10-26",
      "creditAmount": {
        "amount": "49.99",
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
  "query": "mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) { storeCreditAccountCredit(id: $id, creditInput: $creditInput) { storeCreditAccountTransaction { amount { amount currencyCode } account { id balance { amount currencyCode } } } userErrors { message field } } }",
   "variables": {
      "id": "gid://shopify/StoreCreditAccount/316863792",
      "creditInput": {
        "expiresAt": "2028-10-26",
        "creditAmount": {
          "amount": "49.99",
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
    mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
      storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
          "creditInput": {
              "expiresAt": "2028-10-26",
              "creditAmount": {
                  "amount": "49.99",
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
    mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
      storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
    "creditInput": {
      "expiresAt": "2028-10-26",
      "creditAmount": {
        "amount": "49.99",
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
      "query": `mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
        storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
          "creditInput": {
              "expiresAt": "2028-10-26",
              "creditAmount": {
                  "amount": "49.99",
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
  'mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
    storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
    "creditInput": {
      "expiresAt": "2028-10-26",
      "creditAmount": {
        "amount": "49.99",
        "currencyCode": "USD"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "storeCreditAccountCredit": {
      "storeCreditAccountTransaction": {
        "amount": {
          "amount": "49.99",
          "currencyCode": "USD"
        },
        "account": {
          "id": "gid://shopify/StoreCreditAccount/316863792",
          "balance": {
            "amount": "61.1",
            "currencyCode": "USD"
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Crediting a negative amount returns an error

  #### Query

  ```graphql
  mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
    storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
    "id": "gid://shopify/Customer/1018520244",
    "creditInput": {
      "creditAmount": {
        "amount": "-100.00",
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
  "query": "mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) { storeCreditAccountCredit(id: $id, creditInput: $creditInput) { storeCreditAccountTransaction { amount { amount currencyCode } account { id balance { amount currencyCode } } } userErrors { message field } } }",
   "variables": {
      "id": "gid://shopify/Customer/1018520244",
      "creditInput": {
        "creditAmount": {
          "amount": "-100.00",
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
    mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
      storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
          "id": "gid://shopify/Customer/1018520244",
          "creditInput": {
              "creditAmount": {
                  "amount": "-100.00",
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
    mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
      storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
    "id": "gid://shopify/Customer/1018520244",
    "creditInput": {
      "creditAmount": {
        "amount": "-100.00",
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
      "query": `mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
        storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
          "id": "gid://shopify/Customer/1018520244",
          "creditInput": {
              "creditAmount": {
                  "amount": "-100.00",
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
  'mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
    storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
    "id": "gid://shopify/Customer/1018520244",
    "creditInput": {
      "creditAmount": {
        "amount": "-100.00",
        "currencyCode": "USD"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "storeCreditAccountCredit": {
      "storeCreditAccountTransaction": null,
      "userErrors": [
        {
          "message": "A positive amount must be used to credit a store credit account",
          "field": [
            "creditInput",
            "creditAmount",
            "amount"
          ]
        }
      ]
    }
  }
  ```

* ### Crediting an amount that exceeds the account limit returns an error

  #### Description

  Store credit accounts have a limit which can differ depending on the currency of the account. Attempting to credit an amount that would exceed the account's limit will return an error.

  #### Query

  ```graphql
  mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
    storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
    "id": "gid://shopify/Customer/1018520244",
    "creditInput": {
      "creditAmount": {
        "amount": "100000.00",
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
  "query": "mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) { storeCreditAccountCredit(id: $id, creditInput: $creditInput) { storeCreditAccountTransaction { amount { amount currencyCode } account { id balance { amount currencyCode } } } userErrors { message field } } }",
   "variables": {
      "id": "gid://shopify/Customer/1018520244",
      "creditInput": {
        "creditAmount": {
          "amount": "100000.00",
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
    mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
      storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
          "id": "gid://shopify/Customer/1018520244",
          "creditInput": {
              "creditAmount": {
                  "amount": "100000.00",
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
    mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
      storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
    "id": "gid://shopify/Customer/1018520244",
    "creditInput": {
      "creditAmount": {
        "amount": "100000.00",
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
      "query": `mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
        storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
          "id": "gid://shopify/Customer/1018520244",
          "creditInput": {
              "creditAmount": {
                  "amount": "100000.00",
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
  'mutation storeCreditAccountCredit($id: ID!, $creditInput: StoreCreditAccountCreditInput!) {
    storeCreditAccountCredit(id: $id, creditInput: $creditInput) {
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
    "id": "gid://shopify/Customer/1018520244",
    "creditInput": {
      "creditAmount": {
        "amount": "100000.00",
        "currencyCode": "USD"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "storeCreditAccountCredit": {
      "storeCreditAccountTransaction": null,
      "userErrors": [
        {
          "message": "The operation would cause the account's credit limit to be exceeded",
          "field": [
            "creditInput",
            "creditAmount",
            "amount"
          ]
        }
      ]
    }
  }
  ```

* ### storeCreditAccountCredit reference
