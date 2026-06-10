---
title: giftCardUpdate - GraphQL Admin
description: Update a gift card.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/giftCardUpdate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/giftCardUpdate.md
---

# gift​Card​Update

mutation

Requires `write_gift_cards` access scope.

Update a gift card.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the gift card to be updated.

* input

  [Gift​Card​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/GiftCardUpdateInput)

  required

  The input fields to update the gift card.

***

## Gift​Card​Update​Payload returns

* gift​Card

  [Gift​Card](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCard)

  The updated gift card.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update a gift card's customer

  #### Query

  ```graphql
  mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
    giftCardUpdate(id: $id, input: $input) {
      userErrors {
        message
        field
      }
      giftCard {
        id
        customer {
          id
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/GiftCard/63396415",
    "input": {
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
  "query": "mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) { giftCardUpdate(id: $id, input: $input) { userErrors { message field } giftCard { id customer { id } } } }",
   "variables": {
      "id": "gid://shopify/GiftCard/63396415",
      "input": {
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
    mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
      giftCardUpdate(id: $id, input: $input) {
        userErrors {
          message
          field
        }
        giftCard {
          id
          customer {
            id
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/GiftCard/63396415",
          "input": {
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
    mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
      giftCardUpdate(id: $id, input: $input) {
        userErrors {
          message
          field
        }
        giftCard {
          id
          customer {
            id
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/GiftCard/63396415",
    "input": {
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
      "query": `mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
        giftCardUpdate(id: $id, input: $input) {
          userErrors {
            message
            field
          }
          giftCard {
            id
            customer {
              id
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/GiftCard/63396415",
          "input": {
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
  'mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
    giftCardUpdate(id: $id, input: $input) {
      userErrors {
        message
        field
      }
      giftCard {
        id
        customer {
          id
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/GiftCard/63396415",
    "input": {
      "customerId": "gid://shopify/Customer/331283560"
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCardUpdate": {
      "userErrors": [],
      "giftCard": {
        "id": "gid://shopify/GiftCard/63396415",
        "customer": {
          "id": "gid://shopify/Customer/331283560"
        }
      }
    }
  }
  ```

* ### Update a gift card's expiration date so that it will never expire

  #### Query

  ```graphql
  mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
    giftCardUpdate(id: $id, input: $input) {
      userErrors {
        message
        field
      }
      giftCard {
        id
        expiresOn
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/GiftCard/746346263",
    "input": {
      "expiresOn": null
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
  "query": "mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) { giftCardUpdate(id: $id, input: $input) { userErrors { message field } giftCard { id expiresOn } } }",
   "variables": {
      "id": "gid://shopify/GiftCard/746346263",
      "input": {
        "expiresOn": null
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
    mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
      giftCardUpdate(id: $id, input: $input) {
        userErrors {
          message
          field
        }
        giftCard {
          id
          expiresOn
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/GiftCard/746346263",
          "input": {
              "expiresOn": null
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
    mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
      giftCardUpdate(id: $id, input: $input) {
        userErrors {
          message
          field
        }
        giftCard {
          id
          expiresOn
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/GiftCard/746346263",
    "input": {
      "expiresOn": null
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
        giftCardUpdate(id: $id, input: $input) {
          userErrors {
            message
            field
          }
          giftCard {
            id
            expiresOn
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/GiftCard/746346263",
          "input": {
              "expiresOn": null
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
    giftCardUpdate(id: $id, input: $input) {
      userErrors {
        message
        field
      }
      giftCard {
        id
        expiresOn
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/GiftCard/746346263",
    "input": {
      "expiresOn": null
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCardUpdate": {
      "userErrors": [],
      "giftCard": {
        "id": "gid://shopify/GiftCard/746346263",
        "expiresOn": null
      }
    }
  }
  ```

* ### Update a gift card's recipient

  #### Query

  ```graphql
  mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
    giftCardUpdate(id: $id, input: $input) {
      giftCard {
        id
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
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/GiftCard/63396415",
    "input": {
      "recipientAttributes": {
        "id": "gid://shopify/Customer/331283560",
        "message": "Happy Birthday!",
        "preferredName": "Dad",
        "sendNotificationAt": "2024-10-01T11:00:00Z"
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
  "query": "mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) { giftCardUpdate(id: $id, input: $input) { giftCard { id recipientAttributes { recipient { id } message preferredName sendNotificationAt } } userErrors { message field } } }",
   "variables": {
      "id": "gid://shopify/GiftCard/63396415",
      "input": {
        "recipientAttributes": {
          "id": "gid://shopify/Customer/331283560",
          "message": "Happy Birthday!",
          "preferredName": "Dad",
          "sendNotificationAt": "2024-10-01T11:00:00Z"
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
    mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
      giftCardUpdate(id: $id, input: $input) {
        giftCard {
          id
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
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/GiftCard/63396415",
          "input": {
              "recipientAttributes": {
                  "id": "gid://shopify/Customer/331283560",
                  "message": "Happy Birthday!",
                  "preferredName": "Dad",
                  "sendNotificationAt": "2024-10-01T11:00:00Z"
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
    mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
      giftCardUpdate(id: $id, input: $input) {
        giftCard {
          id
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
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/GiftCard/63396415",
    "input": {
      "recipientAttributes": {
        "id": "gid://shopify/Customer/331283560",
        "message": "Happy Birthday!",
        "preferredName": "Dad",
        "sendNotificationAt": "2024-10-01T11:00:00Z"
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
      "query": `mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
        giftCardUpdate(id: $id, input: $input) {
          giftCard {
            id
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
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/GiftCard/63396415",
          "input": {
              "recipientAttributes": {
                  "id": "gid://shopify/Customer/331283560",
                  "message": "Happy Birthday!",
                  "preferredName": "Dad",
                  "sendNotificationAt": "2024-10-01T11:00:00Z"
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
  'mutation giftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
    giftCardUpdate(id: $id, input: $input) {
      giftCard {
        id
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
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/GiftCard/63396415",
    "input": {
      "recipientAttributes": {
        "id": "gid://shopify/Customer/331283560",
        "message": "Happy Birthday!",
        "preferredName": "Dad",
        "sendNotificationAt": "2024-10-01T11:00:00Z"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCardUpdate": {
      "giftCard": {
        "id": "gid://shopify/GiftCard/63396415",
        "recipientAttributes": {
          "recipient": {
            "id": "gid://shopify/Customer/331283560"
          },
          "message": "Happy Birthday!",
          "preferredName": "Dad",
          "sendNotificationAt": "2024-10-01T11:00:00Z"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Update an existing gift card

  #### Query

  ```graphql
  mutation GiftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
    giftCardUpdate(id: $id, input: $input) {
      giftCard {
        id
        note
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
    "id": "gid://shopify/GiftCard/63396415",
    "input": {
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
  "query": "mutation GiftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) { giftCardUpdate(id: $id, input: $input) { giftCard { id note } userErrors { message field } } }",
   "variables": {
      "id": "gid://shopify/GiftCard/63396415",
      "input": {
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
    mutation GiftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
      giftCardUpdate(id: $id, input: $input) {
        giftCard {
          id
          note
        }
        userErrors {
          message
          field
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/GiftCard/63396415",
          "input": {
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
    mutation GiftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
      giftCardUpdate(id: $id, input: $input) {
        giftCard {
          id
          note
        }
        userErrors {
          message
          field
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/GiftCard/63396415",
    "input": {
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
      "query": `mutation GiftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
        giftCardUpdate(id: $id, input: $input) {
          giftCard {
            id
            note
          }
          userErrors {
            message
            field
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/GiftCard/63396415",
          "input": {
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
  'mutation GiftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
    giftCardUpdate(id: $id, input: $input) {
      giftCard {
        id
        note
      }
      userErrors {
        message
        field
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/GiftCard/63396415",
    "input": {
      "note": "A note."
    }
  }'
  ```

  #### Response

  ```json
  {
    "giftCardUpdate": {
      "giftCard": {
        "id": "gid://shopify/GiftCard/63396415",
        "note": "A note."
      },
      "userErrors": []
    }
  }
  ```

* ### giftCardUpdate reference
