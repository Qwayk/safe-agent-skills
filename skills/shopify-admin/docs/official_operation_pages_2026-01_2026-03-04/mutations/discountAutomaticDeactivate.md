---
title: discountAutomaticDeactivate - GraphQL Admin
description: Deactivates an automatic discount.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticDeactivate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticDeactivate.md
---

# discount​Automatic​Deactivate

mutation

Requires Apps must have `write_discounts` access scope.

Deactivates an automatic discount.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the automatic discount to deactivate.

***

## Discount​Automatic​Deactivate​Payload returns

* automatic​Discount​Node

  [Discount​Automatic​Node](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomaticNode)

  The deactivated automatic discount.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Deactivate an active automatic discount

  #### Description

  Deactivating an active automatic discount sets the \`endsAt\` to now. In this example, the \`endsAt\` was originally set to January 1, 2049.

  #### Query

  ```graphql
  mutation discountAutomaticDeactivate($id: ID!) {
    discountAutomaticDeactivate(id: $id) {
      automaticDiscountNode {
        automaticDiscount {
          ... on DiscountAutomaticBxgy {
            status
            startsAt
            endsAt
          }
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
    "id": "gid://shopify/DiscountAutomaticNode/198286294"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation discountAutomaticDeactivate($id: ID!) { discountAutomaticDeactivate(id: $id) { automaticDiscountNode { automaticDiscount { ... on DiscountAutomaticBxgy { status startsAt endsAt } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DiscountAutomaticNode/198286294"
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
    mutation discountAutomaticDeactivate($id: ID!) {
      discountAutomaticDeactivate(id: $id) {
        automaticDiscountNode {
          automaticDiscount {
            ... on DiscountAutomaticBxgy {
              status
              startsAt
              endsAt
            }
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
          "id": "gid://shopify/DiscountAutomaticNode/198286294"
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
    mutation discountAutomaticDeactivate($id: ID!) {
      discountAutomaticDeactivate(id: $id) {
        automaticDiscountNode {
          automaticDiscount {
            ... on DiscountAutomaticBxgy {
              status
              startsAt
              endsAt
            }
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
    "id": "gid://shopify/DiscountAutomaticNode/198286294"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountAutomaticDeactivate($id: ID!) {
        discountAutomaticDeactivate(id: $id) {
          automaticDiscountNode {
            automaticDiscount {
              ... on DiscountAutomaticBxgy {
                status
                startsAt
                endsAt
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DiscountAutomaticNode/198286294"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountAutomaticDeactivate($id: ID!) {
    discountAutomaticDeactivate(id: $id) {
      automaticDiscountNode {
        automaticDiscount {
          ... on DiscountAutomaticBxgy {
            status
            startsAt
            endsAt
          }
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
    "id": "gid://shopify/DiscountAutomaticNode/198286294"
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticDeactivate": {
      "automaticDiscountNode": {
        "automaticDiscount": {
          "status": "EXPIRED",
          "startsAt": "2024-09-12T01:08:08Z",
          "endsAt": "2024-09-12T01:08:08Z"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Deactivate an automatic discount set to start in the future

  #### Description

  Deactivating an automatic discount set in the future sets its \`startsAt\` and \`endsAt\` to now. In this example, the \`startsAt\` and \`endsAt\` were originally set in the year 2049.

  #### Query

  ```graphql
  mutation discountAutomaticDeactivate($id: ID!) {
    discountAutomaticDeactivate(id: $id) {
      automaticDiscountNode {
        automaticDiscount {
          ... on DiscountAutomaticBxgy {
            status
            startsAt
            endsAt
          }
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
    "id": "gid://shopify/DiscountAutomaticNode/198286294"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation discountAutomaticDeactivate($id: ID!) { discountAutomaticDeactivate(id: $id) { automaticDiscountNode { automaticDiscount { ... on DiscountAutomaticBxgy { status startsAt endsAt } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DiscountAutomaticNode/198286294"
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
    mutation discountAutomaticDeactivate($id: ID!) {
      discountAutomaticDeactivate(id: $id) {
        automaticDiscountNode {
          automaticDiscount {
            ... on DiscountAutomaticBxgy {
              status
              startsAt
              endsAt
            }
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
          "id": "gid://shopify/DiscountAutomaticNode/198286294"
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
    mutation discountAutomaticDeactivate($id: ID!) {
      discountAutomaticDeactivate(id: $id) {
        automaticDiscountNode {
          automaticDiscount {
            ... on DiscountAutomaticBxgy {
              status
              startsAt
              endsAt
            }
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
    "id": "gid://shopify/DiscountAutomaticNode/198286294"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountAutomaticDeactivate($id: ID!) {
        discountAutomaticDeactivate(id: $id) {
          automaticDiscountNode {
            automaticDiscount {
              ... on DiscountAutomaticBxgy {
                status
                startsAt
                endsAt
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DiscountAutomaticNode/198286294"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountAutomaticDeactivate($id: ID!) {
    discountAutomaticDeactivate(id: $id) {
      automaticDiscountNode {
        automaticDiscount {
          ... on DiscountAutomaticBxgy {
            status
            startsAt
            endsAt
          }
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
    "id": "gid://shopify/DiscountAutomaticNode/198286294"
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticDeactivate": {
      "automaticDiscountNode": {
        "automaticDiscount": {
          "status": "EXPIRED",
          "startsAt": "2024-09-12T01:08:08Z",
          "endsAt": "2024-09-12T01:08:08Z"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### discountAutomaticDeactivate reference
