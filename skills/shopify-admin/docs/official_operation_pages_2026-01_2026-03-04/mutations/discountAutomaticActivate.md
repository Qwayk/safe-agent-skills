---
title: discountAutomaticActivate - GraphQL Admin
description: Activates an automatic discount.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticActivate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticActivate.md
---

# discount​Automatic​Activate

mutation

Requires Apps must have `write_discounts` access scope.

Activates an automatic discount.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the automatic discount to activate.

***

## Discount​Automatic​Activate​Payload returns

* automatic​Discount​Node

  [Discount​Automatic​Node](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomaticNode)

  The activated automatic discount.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Activate an automatic discount set to start in the future

  #### Description

  Activating an automatic discount set to start in the future sets its \`startsAt\` to now. In this example, the \`startsAt\` was originally set to January 1, 2049.

  #### Query

  ```graphql
  mutation discountAutomaticActivate($id: ID!) {
    discountAutomaticActivate(id: $id) {
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
  "query": "mutation discountAutomaticActivate($id: ID!) { discountAutomaticActivate(id: $id) { automaticDiscountNode { automaticDiscount { ... on DiscountAutomaticBxgy { status startsAt endsAt } } } userErrors { field message } } }",
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
    mutation discountAutomaticActivate($id: ID!) {
      discountAutomaticActivate(id: $id) {
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
    mutation discountAutomaticActivate($id: ID!) {
      discountAutomaticActivate(id: $id) {
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
      "query": `mutation discountAutomaticActivate($id: ID!) {
        discountAutomaticActivate(id: $id) {
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
  'mutation discountAutomaticActivate($id: ID!) {
    discountAutomaticActivate(id: $id) {
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
    "discountAutomaticActivate": {
      "automaticDiscountNode": {
        "automaticDiscount": {
          "status": "ACTIVE",
          "startsAt": "2024-09-12T01:06:56Z",
          "endsAt": "2049-02-01T05:00:00Z"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Activate an expired automatic discount

  #### Description

  Activating an expired automatic discount sets its endsAt value to null

  #### Query

  ```graphql
  mutation discountAutomaticActivate($id: ID!) {
    discountAutomaticActivate(id: $id) {
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
  "query": "mutation discountAutomaticActivate($id: ID!) { discountAutomaticActivate(id: $id) { automaticDiscountNode { automaticDiscount { ... on DiscountAutomaticBxgy { status startsAt endsAt } } } userErrors { field message } } }",
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
    mutation discountAutomaticActivate($id: ID!) {
      discountAutomaticActivate(id: $id) {
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
    mutation discountAutomaticActivate($id: ID!) {
      discountAutomaticActivate(id: $id) {
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
      "query": `mutation discountAutomaticActivate($id: ID!) {
        discountAutomaticActivate(id: $id) {
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
  'mutation discountAutomaticActivate($id: ID!) {
    discountAutomaticActivate(id: $id) {
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
    "discountAutomaticActivate": {
      "automaticDiscountNode": {
        "automaticDiscount": {
          "status": "ACTIVE",
          "startsAt": "2024-07-12T01:06:56Z",
          "endsAt": null
        }
      },
      "userErrors": []
    }
  }
  ```

* ### discountAutomaticActivate reference
