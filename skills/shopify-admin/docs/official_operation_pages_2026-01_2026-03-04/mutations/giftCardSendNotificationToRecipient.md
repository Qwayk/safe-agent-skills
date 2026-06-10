---
title: giftCardSendNotificationToRecipient - GraphQL Admin
description: Send notification to the recipient of a gift card.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/giftCardSendNotificationToRecipient
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/giftCardSendNotificationToRecipient.md
---

# gift​Card​Send​Notification​To​Recipient

mutation

Requires `write_gift_cards` access scope.

Send notification to the recipient of a gift card.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the gift card to send.

***

## Gift​Card​Send​Notification​To​Recipient​Payload returns

* gift​Card

  [Gift​Card](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCard)

  The gift card that was sent.

* user​Errors

  [\[Gift​Card​Send​Notification​To​Recipient​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCardSendNotificationToRecipientUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Send a notification to a gift card's recipient

  #### Query

  ```graphql
  mutation giftCardSendNotificationToRecipient($id: ID!) {
    giftCardSendNotificationToRecipient(id: $id) {
      giftCard {
        id
        recipientAttributes {
          recipient {
            id
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
    "id": "gid://shopify/GiftCard/698360200"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation giftCardSendNotificationToRecipient($id: ID!) { giftCardSendNotificationToRecipient(id: $id) { giftCard { id recipientAttributes { recipient { id } } } userErrors { message field code } } }",
   "variables": {
      "id": "gid://shopify/GiftCard/698360200"
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
    mutation giftCardSendNotificationToRecipient($id: ID!) {
      giftCardSendNotificationToRecipient(id: $id) {
        giftCard {
          id
          recipientAttributes {
            recipient {
              id
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
          "id": "gid://shopify/GiftCard/698360200"
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
    mutation giftCardSendNotificationToRecipient($id: ID!) {
      giftCardSendNotificationToRecipient(id: $id) {
        giftCard {
          id
          recipientAttributes {
            recipient {
              id
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
    "id": "gid://shopify/GiftCard/698360200"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation giftCardSendNotificationToRecipient($id: ID!) {
        giftCardSendNotificationToRecipient(id: $id) {
          giftCard {
            id
            recipientAttributes {
              recipient {
                id
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
          "id": "gid://shopify/GiftCard/698360200"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation giftCardSendNotificationToRecipient($id: ID!) {
    giftCardSendNotificationToRecipient(id: $id) {
      giftCard {
        id
        recipientAttributes {
          recipient {
            id
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
    "id": "gid://shopify/GiftCard/698360200"
  }'
  ```

  #### Response

  ```json
  {
    "giftCardSendNotificationToRecipient": {
      "giftCard": {
        "id": "gid://shopify/GiftCard/698360200",
        "recipientAttributes": {
          "recipient": {
            "id": "gid://shopify/Customer/105906728"
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### giftCardSendNotificationToRecipient reference
