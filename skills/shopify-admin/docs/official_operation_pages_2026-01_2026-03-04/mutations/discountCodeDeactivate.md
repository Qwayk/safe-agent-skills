---
title: discountCodeDeactivate - GraphQL Admin
description: >-
  Temporarily suspends a code discount without permanently removing it from the
  store. Deactivation allows merchants to pause promotional campaigns while
  preserving the discount configuration for potential future use.


  For example, when a flash sale needs to end immediately or a discount code
  requires temporary suspension due to inventory issues, merchants can
  deactivate it to stop new redemptions while keeping the discount structure
  intact.


  Use `DiscountCodeDeactivate` to:

  - Pause active promotional campaigns timely

  - Temporarily suspend problematic discount codes

  - Control discount availability during inventory shortages

  - Maintain discount history while stopping usage


  Deactivated discounts remain in the system and can be reactivated later,
  unlike deletion which persistently removes the code. Customers attempting to
  use deactivated codes will receive appropriate error messages.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeDeactivate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeDeactivate.md
---

# discount​Code​Deactivate

mutation

Requires Apps must have `write_discounts` access scope.

Temporarily suspends a code discount without permanently removing it from the store. Deactivation allows merchants to pause promotional campaigns while preserving the discount configuration for potential future use.

For example, when a flash sale needs to end immediately or a discount code requires temporary suspension due to inventory issues, merchants can deactivate it to stop new redemptions while keeping the discount structure intact.

Use `DiscountCodeDeactivate` to:

* Pause active promotional campaigns timely
* Temporarily suspend problematic discount codes
* Control discount availability during inventory shortages
* Maintain discount history while stopping usage

Deactivated discounts remain in the system and can be reactivated later, unlike deletion which persistently removes the code. Customers attempting to use deactivated codes will receive appropriate error messages.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the code discount to deactivate.

***

## Discount​Code​Deactivate​Payload returns

* code​Discount​Node

  [Discount​Code​Node](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountCodeNode)

  The deactivated code discount.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Deactivate a code discount set to start in the future

  #### Description

  Deactivating a code discount set in the future sets its \`startsAt\` and \`endsAt\` to now. In this example, the \`startsAt\` and \`endsAt\` were originally set in the year 2049.

  #### Query

  ```graphql
  mutation discountCodeDeactivate($id: ID!) {
    discountCodeDeactivate(id: $id) {
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
  "query": "mutation discountCodeDeactivate($id: ID!) { discountCodeDeactivate(id: $id) { codeDiscountNode { codeDiscount { ... on DiscountCodeBasic { title status startsAt endsAt } } } userErrors { field code message } } }",
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
    mutation discountCodeDeactivate($id: ID!) {
      discountCodeDeactivate(id: $id) {
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
    mutation discountCodeDeactivate($id: ID!) {
      discountCodeDeactivate(id: $id) {
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
      "query": `mutation discountCodeDeactivate($id: ID!) {
        discountCodeDeactivate(id: $id) {
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
  'mutation discountCodeDeactivate($id: ID!) {
    discountCodeDeactivate(id: $id) {
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
    "discountCodeDeactivate": {
      "codeDiscountNode": {
        "codeDiscount": {
          "title": "percentage_off_code",
          "status": "EXPIRED",
          "startsAt": "2024-09-12T01:06:40Z",
          "endsAt": "2024-09-12T01:06:40Z"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Deactivate an active code discount

  #### Description

  Deactivating an active code discount sets the \`endsAt\` to now. In this example, the \`endsAt\` was originally set to January 1, 2049.

  #### Query

  ```graphql
  mutation discountCodeDeactivate($id: ID!) {
    discountCodeDeactivate(id: $id) {
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
  "query": "mutation discountCodeDeactivate($id: ID!) { discountCodeDeactivate(id: $id) { codeDiscountNode { codeDiscount { ... on DiscountCodeBasic { title status startsAt endsAt } } } userErrors { field code message } } }",
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
    mutation discountCodeDeactivate($id: ID!) {
      discountCodeDeactivate(id: $id) {
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
    mutation discountCodeDeactivate($id: ID!) {
      discountCodeDeactivate(id: $id) {
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
      "query": `mutation discountCodeDeactivate($id: ID!) {
        discountCodeDeactivate(id: $id) {
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
  'mutation discountCodeDeactivate($id: ID!) {
    discountCodeDeactivate(id: $id) {
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
    "discountCodeDeactivate": {
      "codeDiscountNode": {
        "codeDiscount": {
          "title": "percentage_off_code",
          "status": "EXPIRED",
          "startsAt": "2024-09-03T01:05:24Z",
          "endsAt": "2024-09-12T01:06:40Z"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### discountCodeDeactivate reference
