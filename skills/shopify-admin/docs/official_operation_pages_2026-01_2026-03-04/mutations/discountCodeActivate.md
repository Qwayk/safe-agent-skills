---
title: discountCodeActivate - GraphQL Admin
description: >-
  Activates a previously created code discount, making it available for
  customers to use during checkout. This mutation transitions inactive discount
  codes into an active state where they can be applied to orders.


  For example, after creating a "SUMMER20" discount code but leaving it inactive
  during setup, merchants can activate it when ready to launch their summer
  promotion campaign.


  Use `DiscountCodeActivate` to:

  - Launch scheduled promotional campaigns

  - Reactivate previously paused discount codes

  - Enable discount codes after configuration changes

  - Control the timing of discount availability


  The mutation returns the updated discount code node with its new active status
  and handles any validation errors that might prevent activation, such as
  conflicting discount rules or invalid date ranges.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeActivate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeActivate.md
---

# discount​Code​Activate

mutation

Requires Apps must have `write_discounts` access scope.

Activates a previously created code discount, making it available for customers to use during checkout. This mutation transitions inactive discount codes into an active state where they can be applied to orders.

For example, after creating a "SUMMER20" discount code but leaving it inactive during setup, merchants can activate it when ready to launch their summer promotion campaign.

Use `DiscountCodeActivate` to:

* Launch scheduled promotional campaigns
* Reactivate previously paused discount codes
* Enable discount codes after configuration changes
* Control the timing of discount availability

The mutation returns the updated discount code node with its new active status and handles any validation errors that might prevent activation, such as conflicting discount rules or invalid date ranges.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the code discount to activate.

***

## Discount​Code​Activate​Payload returns

* code​Discount​Node

  [Discount​Code​Node](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountCodeNode)

  The activated code discount.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Activate a code discount set to start in the future

  #### Description

  Activating a code discount set to start in the future sets its \`startsAt\` to now. In this example, the \`startsAt\` was originally set to January 1, 2049.

  #### Query

  ```graphql
  mutation discountCodeActivate($id: ID!) {
    discountCodeActivate(id: $id) {
      codeDiscountNode {
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            status
            startsAt
            endsAt
          }
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/DiscountCodeNode/206265824"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation discountCodeActivate($id: ID!) { discountCodeActivate(id: $id) { codeDiscountNode { codeDiscount { ... on DiscountCodeBasic { title status startsAt endsAt } } } userErrors { field code message } } }",
   "variables": {
      "id": "gid://shopify/DiscountCodeNode/206265824"
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
    mutation discountCodeActivate($id: ID!) {
      discountCodeActivate(id: $id) {
        codeDiscountNode {
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              status
              startsAt
              endsAt
            }
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DiscountCodeNode/206265824"
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
    mutation discountCodeActivate($id: ID!) {
      discountCodeActivate(id: $id) {
        codeDiscountNode {
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              status
              startsAt
              endsAt
            }
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DiscountCodeNode/206265824"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountCodeActivate($id: ID!) {
        discountCodeActivate(id: $id) {
          codeDiscountNode {
            codeDiscount {
              ... on DiscountCodeBasic {
                title
                status
                startsAt
                endsAt
              }
            }
          }
          userErrors {
            field
            code
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DiscountCodeNode/206265824"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountCodeActivate($id: ID!) {
    discountCodeActivate(id: $id) {
      codeDiscountNode {
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            status
            startsAt
            endsAt
          }
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DiscountCodeNode/206265824"
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeActivate": {
      "codeDiscountNode": {
        "codeDiscount": {
          "title": "percentage_off_code",
          "status": "ACTIVE",
          "startsAt": "2024-09-12T01:06:59Z",
          "endsAt": "2049-02-01T05:00:00Z"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Activate an expired code discount

  #### Description

  Activating an expired code discount sets its \`endsAt\` value to \`null\`

  #### Query

  ```graphql
  mutation discountCodeActivate($id: ID!) {
    discountCodeActivate(id: $id) {
      codeDiscountNode {
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            status
            startsAt
            endsAt
          }
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/DiscountCodeNode/424668491"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation discountCodeActivate($id: ID!) { discountCodeActivate(id: $id) { codeDiscountNode { codeDiscount { ... on DiscountCodeBasic { title status startsAt endsAt } } } userErrors { field code message } } }",
   "variables": {
      "id": "gid://shopify/DiscountCodeNode/424668491"
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
    mutation discountCodeActivate($id: ID!) {
      discountCodeActivate(id: $id) {
        codeDiscountNode {
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              status
              startsAt
              endsAt
            }
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DiscountCodeNode/424668491"
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
    mutation discountCodeActivate($id: ID!) {
      discountCodeActivate(id: $id) {
        codeDiscountNode {
          codeDiscount {
            ... on DiscountCodeBasic {
              title
              status
              startsAt
              endsAt
            }
          }
        }
        userErrors {
          field
          code
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DiscountCodeNode/424668491"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountCodeActivate($id: ID!) {
        discountCodeActivate(id: $id) {
          codeDiscountNode {
            codeDiscount {
              ... on DiscountCodeBasic {
                title
                status
                startsAt
                endsAt
              }
            }
          }
          userErrors {
            field
            code
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DiscountCodeNode/424668491"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountCodeActivate($id: ID!) {
    discountCodeActivate(id: $id) {
      codeDiscountNode {
        codeDiscount {
          ... on DiscountCodeBasic {
            title
            status
            startsAt
            endsAt
          }
        }
      }
      userErrors {
        field
        code
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DiscountCodeNode/424668491"
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeActivate": {
      "codeDiscountNode": {
        "codeDiscount": {
          "title": "EXPIRED10",
          "status": "ACTIVE",
          "startsAt": "2024-08-28T01:05:24Z",
          "endsAt": null
        }
      },
      "userErrors": []
    }
  }
  ```

* ### discountCodeActivate reference
