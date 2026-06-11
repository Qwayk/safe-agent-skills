---
title: giftCardDeactivate - GraphQL Admin
description: |-
  Deactivate a gift card. A deactivated gift card cannot be used by a customer.
  A deactivated gift card cannot be re-enabled.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/giftCardDeactivate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/giftCardDeactivate.md
---

# gift​Card​Deactivate

mutation

Requires `write_gift_cards` access scope.

Deactivate a gift card. A deactivated gift card cannot be used by a customer. A deactivated gift card cannot be re-enabled.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the gift card to deactivate.

***

## Gift​Card​Deactivate​Payload returns

* gift​Card

  [Gift​Card](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCard)

  The deactivated gift card.

* user​Errors

  [\[Gift​Card​Deactivate​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/GiftCardDeactivateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Disables a gift card

  #### Query

  ```graphql
  mutation giftCardDeactivate($id: ID!) {
    giftCardDeactivate(id: $id) {
      giftCard {
        id
        deactivatedAt
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
    "id": "gid://shopify/GiftCard/411106674"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation giftCardDeactivate($id: ID!) { giftCardDeactivate(id: $id) { giftCard { id deactivatedAt } userErrors { message field code } } }",
   "variables": {
      "id": "gid://shopify/GiftCard/411106674"
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
    mutation giftCardDeactivate($id: ID!) {
      giftCardDeactivate(id: $id) {
        giftCard {
          id
          deactivatedAt
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
          "id": "gid://shopify/GiftCard/411106674"
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
    mutation giftCardDeactivate($id: ID!) {
      giftCardDeactivate(id: $id) {
        giftCard {
          id
          deactivatedAt
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
    "id": "gid://shopify/GiftCard/411106674"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation giftCardDeactivate($id: ID!) {
        giftCardDeactivate(id: $id) {
          giftCard {
            id
            deactivatedAt
          }
          userErrors {
            message
            field
            code
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/GiftCard/411106674"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation giftCardDeactivate($id: ID!) {
    giftCardDeactivate(id: $id) {
      giftCard {
        id
        deactivatedAt
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
    "id": "gid://shopify/GiftCard/411106674"
  }'
  ```

  #### Response

  ```json
  {
    "giftCardDeactivate": {
      "giftCard": {
        "id": "gid://shopify/GiftCard/411106674",
        "deactivatedAt": "2024-11-05T15:35:29Z"
      },
      "userErrors": []
    }
  }
  ```

* ### giftCardDeactivate reference
