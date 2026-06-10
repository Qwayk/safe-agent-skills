---
title: giftCardCreate - GraphQL Admin
description: >-
  Creates a new
  [`GiftCard`](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCard)
  with a specified initial value. You can assign the gift card to a
  [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)
  or create it without assignment for manual distribution.


  You can customize the gift card with an optional code, expiration date, and
  internal note. If you don't provide a code, the system generates a random 16
  character alphanumeric code. The mutation also supports scheduling gift card
  notifications to recipients, with a personalized message, through the
  [`recipientAttributes`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/GiftCardCreateInput#fields-recipientAttributes)
  field on the `GiftCardCreateInput` input object.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/giftCardCreate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/giftCardCreate.md
---

# gift​Card​Create

mutation

Requires `write_gift_cards` access scope.

Creates a new [`GiftCard`](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCard) with a specified initial value. You can assign the gift card to a [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer) or create it without assignment for manual distribution.

You can customize the gift card with an optional code, expiration date, and internal note. If you don't provide a code, the system generates a random 16 character alphanumeric code. The mutation also supports scheduling gift card notifications to recipients, with a personalized message, through the [`recipientAttributes`](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/GiftCardCreateInput#fields-recipientAttributes) field on the `GiftCardCreateInput` input object.

## Arguments

* input

  [Gift​Card​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/GiftCardCreateInput)

  required

  The input fields to create a gift card.

***

## Gift​Card​Create​Payload returns

* gift​Card

  [Gift​Card](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCard)

  The created gift card.

* gift​Card​Code

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The created gift card's code.

* user​Errors

  [\[Gift​Card​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCardUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a gift card with a customer and a recipient

  #### Query

  ```graphql
  mutation giftCardCreate($input: GiftCardCreateInput!) {
    giftCardCreate(input: $input) {
      giftCard {
        id
        initialValue {
          amount
        }
        customer {
          id
        }
        recipientAttributes {
          recipient {
            id
          }
          message
          preferredName
          sendNotificationAt
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
    "input": {
      "initialValue": "100.0",
      "customerId": "gid://shopify/Customer/331283560",
      "recipientAttributes": {
        "id": "gid://shopify/Customer/743592264",
        "message": "Happy Birthday!",
        "preferredName": "Dad",
        "sendNotificationAt": "2024-10-01T12:00:00Z"
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
  "query": "mutation giftCardCreate($input: GiftCardCreateInput!) { giftCardCreate(input: $input) { giftCard { id initialValue { amount } customer { id } recipientAttributes { recipient { id } message preferredName sendNotificationAt } } userErrors { message field code } } }",
   "variables": {
      "input": {
        "initialValue": "100.0",
        "customerId": "gid://shopify/Customer/331283560",
        "recipientAttributes": {
          "id": "gid://shopify/Customer/743592264",
          "message": "Happy Birthday!",
          "preferredName": "Dad",
          "sendNotificationAt": "2024-10-01T12:00:00Z"
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
    mutation giftCardCreate($input: GiftCardCreateInput!) {
      giftCardCreate(input: $input) {
        giftCard {
          id
          initialValue {
            amount
          }
          customer {
            id
          }
          recipientAttributes {
            recipient {
              id
            }
            message
            preferredName
            sendNotificationAt
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
          "input": {
              "initialValue": "100.0",
              "customerId": "gid://shopify/Customer/331283560",
              "recipientAttributes": {
                  "id": "gid://shopify/Customer/743592264",
                  "message": "Happy Birthday!",
                  "preferredName": "Dad",
                  "sendNotificationAt": "2024-10-01T12:00:00Z"
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
    mutation giftCardCreate($input: GiftCardCreateInput!) {
      giftCardCreate(input: $input) {
        giftCard {
          id
          initialValue {
            amount
          }
          customer {
            id
          }
          recipientAttributes {
            recipient {
              id
            }
            message
            preferredName
            sendNotificationAt
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
    "input": {
      "initialValue": "100.0",
      "customerId": "gid://shopify/Customer/331283560",
      "recipientAttributes": {
        "id": "gid://shopify/Customer/743592264",
        "message": "Happy Birthday!",
        "preferredName": "Dad",
        "sendNotificationAt": "2024-10-01T12:00:00Z"
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
      "query": `mutation giftCardCreate($input: GiftCardCreateInput!) {
        giftCardCreate(input: $input) {
          giftCard {
            id
            initialValue {
              amount
            }
            customer {
              id
            }
            recipientAttributes {
              recipient {
                id
              }
              message
              preferredName
              sendNotificationAt
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
          "input": {
              "initialValue": "100.0",
              "customerId": "gid://shopify/Customer/331283560",
              "recipientAttributes": {
                  "id": "gid://shopify/Customer/743592264",
                  "message": "Happy Birthday!",
                  "preferredName": "Dad",
                  "sendNotificationAt": "2024-10-01T12:00:00Z"
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
  'mutation giftCardCreate($input: GiftCardCreateInput!) {
    giftCardCreate(input: $input) {
      giftCard {
        id
        initialValue {
          amount
        }
        customer {
          id
        }
        recipientAttributes {
          recipient {
            id
          }
          message
          preferredName
          sendNotificationAt
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
    "input": {
      "initialValue": "100.0",
      "customerId": "gid://shopify/Customer/331283560",
      "recipientAttributes": {
        "id": "gid://shopify/Customer/743592264",
        "message": "Happy Birthday!",
        "preferredName": "Dad",
        "sendNotificationAt": "2024-10-01T12:00:00Z"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCardCreate": {
      "giftCard": {
        "id": "gid://shopify/GiftCard/1063936324",
        "initialValue": {
          "amount": "100.0"
        },
        "customer": {
          "id": "gid://shopify/Customer/331283560"
        },
        "recipientAttributes": {
          "recipient": {
            "id": "gid://shopify/Customer/743592264"
          },
          "message": "Happy Birthday!",
          "preferredName": "Dad",
          "sendNotificationAt": "2024-10-01T12:00:00Z"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a non-expiring gift card with a generated code for a customer

  #### Query

  ```graphql
  mutation giftCardCreate($input: GiftCardCreateInput!) {
    giftCardCreate(input: $input) {
      userErrors {
        message
        field
      }
      giftCard {
        id
        expiresOn
        note
        initialValue {
          amount
        }
        customer {
          id
        }
      }
      giftCardCode
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "initialValue": "27.84",
      "customerId": "gid://shopify/Customer/743592264",
      "note": "Refund for Order #1"
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
  "query": "mutation giftCardCreate($input: GiftCardCreateInput!) { giftCardCreate(input: $input) { userErrors { message field } giftCard { id expiresOn note initialValue { amount } customer { id } } giftCardCode } }",
   "variables": {
      "input": {
        "initialValue": "27.84",
        "customerId": "gid://shopify/Customer/743592264",
        "note": "Refund for Order #1"
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
    mutation giftCardCreate($input: GiftCardCreateInput!) {
      giftCardCreate(input: $input) {
        userErrors {
          message
          field
        }
        giftCard {
          id
          expiresOn
          note
          initialValue {
            amount
          }
          customer {
            id
          }
        }
        giftCardCode
      }
    }`,
    {
      variables: {
          "input": {
              "initialValue": "27.84",
              "customerId": "gid://shopify/Customer/743592264",
              "note": "Refund for Order #1"
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
    mutation giftCardCreate($input: GiftCardCreateInput!) {
      giftCardCreate(input: $input) {
        userErrors {
          message
          field
        }
        giftCard {
          id
          expiresOn
          note
          initialValue {
            amount
          }
          customer {
            id
          }
        }
        giftCardCode
      }
    }
  QUERY

  variables = {
    "input": {
      "initialValue": "27.84",
      "customerId": "gid://shopify/Customer/743592264",
      "note": "Refund for Order #1"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation giftCardCreate($input: GiftCardCreateInput!) {
        giftCardCreate(input: $input) {
          userErrors {
            message
            field
          }
          giftCard {
            id
            expiresOn
            note
            initialValue {
              amount
            }
            customer {
              id
            }
          }
          giftCardCode
        }
      }`,
      "variables": {
          "input": {
              "initialValue": "27.84",
              "customerId": "gid://shopify/Customer/743592264",
              "note": "Refund for Order #1"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation giftCardCreate($input: GiftCardCreateInput!) {
    giftCardCreate(input: $input) {
      userErrors {
        message
        field
      }
      giftCard {
        id
        expiresOn
        note
        initialValue {
          amount
        }
        customer {
          id
        }
      }
      giftCardCode
    }
  }' \
  --variables \
  '{
    "input": {
      "initialValue": "27.84",
      "customerId": "gid://shopify/Customer/743592264",
      "note": "Refund for Order #1"
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCardCreate": {
      "userErrors": [],
      "giftCard": {
        "id": "gid://shopify/GiftCard/1063936322",
        "expiresOn": null,
        "note": "Refund for Order #1",
        "initialValue": {
          "amount": "27.84"
        },
        "customer": {
          "id": "gid://shopify/Customer/743592264"
        }
      },
      "giftCardCode": "a5bhbh645b32934f"
    }
  }
  ```

* ### Creates a gift card

  #### Query

  ```graphql
  mutation GiftCardCreate($input: GiftCardCreateInput!) {
    giftCardCreate(input: $input) {
      giftCard {
        id
        balance {
          amount
          currencyCode
        }
      }
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
      "initialValue": "100.0",
      "customerId": "gid://shopify/Customer/331283560"
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
  "query": "mutation GiftCardCreate($input: GiftCardCreateInput!) { giftCardCreate(input: $input) { giftCard { id balance { amount currencyCode } } userErrors { field message } } }",
   "variables": {
      "input": {
        "initialValue": "100.0",
        "customerId": "gid://shopify/Customer/331283560"
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
    mutation GiftCardCreate($input: GiftCardCreateInput!) {
      giftCardCreate(input: $input) {
        giftCard {
          id
          balance {
            amount
            currencyCode
          }
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "initialValue": "100.0",
              "customerId": "gid://shopify/Customer/331283560"
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
    mutation GiftCardCreate($input: GiftCardCreateInput!) {
      giftCardCreate(input: $input) {
        giftCard {
          id
          balance {
            amount
            currencyCode
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "initialValue": "100.0",
      "customerId": "gid://shopify/Customer/331283560"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation GiftCardCreate($input: GiftCardCreateInput!) {
        giftCardCreate(input: $input) {
          giftCard {
            id
            balance {
              amount
              currencyCode
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "initialValue": "100.0",
              "customerId": "gid://shopify/Customer/331283560"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation GiftCardCreate($input: GiftCardCreateInput!) {
    giftCardCreate(input: $input) {
      giftCard {
        id
        balance {
          amount
          currencyCode
        }
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "initialValue": "100.0",
      "customerId": "gid://shopify/Customer/331283560"
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCardCreate": {
      "giftCard": {
        "id": "gid://shopify/GiftCard/1063936323",
        "balance": {
          "amount": "100.0",
          "currencyCode": "USD"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### giftCardCreate reference
