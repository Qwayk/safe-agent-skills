---
title: discountRedeemCodeBulkAdd - GraphQL Admin
description: >-
  Asynchronously add

  [discount
  codes](https://help.shopify.com/manual/discounts/discount-types#discount-codes)

  in bulk that customers can use to redeem a discount. You can use the
  `discountRedeemCodeBulkAdd` mutation

  to automate the distribution of discount codes through emails or other

  marketing channels.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountRedeemCodeBulkAdd
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountRedeemCodeBulkAdd.md
---

# discount​Redeem​Code​Bulk​Add

mutation

Requires Apps must have `write_discounts` access scope.

Asynchronously add [discount codes](https://help.shopify.com/manual/discounts/discount-types#discount-codes) in bulk that customers can use to redeem a discount. You can use the `discountRedeemCodeBulkAdd` mutation to automate the distribution of discount codes through emails or other marketing channels.

## Arguments

* codes

  [\[Discount​Redeem​Code​Input!\]!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DiscountRedeemCodeInput)

  required

  The list of codes to associate with the [code discount](https://help.shopify.com/manual/discounts/discount-types#discount-codes). Maximum: 250 codes.

* discount​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the [`DiscountCodeNode`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountCodeNode#field-id) object that the codes will be added to. For example, `gid://shopify/DiscountCodeNode/123`. You can use the [`codeDiscountNodes` query](https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountNodes) to retrieve the ID.

***

## Discount​Redeem​Code​Bulk​Add​Payload returns

* bulk​Creation

  [Discount​Redeem​Code​Bulk​Creation](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountRedeemCodeBulkCreation)

  The ID of bulk operation that creates multiple unique discount codes. You can use the [`discountRedeemCodeBulkCreation` query](https://shopify.dev/api/admin-graphql/latest/queries/discountRedeemCodeBulkCreation) to track the status of the bulk operation.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Asynchronously add redeem codes to a code discount

  #### Description

  Asynchronously add 3 redeem codes to a code discount

  #### Query

  ```graphql
  mutation discountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
    discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
      bulkCreation {
        id
      }
      userErrors {
        code
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "codes": [
      {
        "code": "DISCOUNT_1"
      },
      {
        "code": "DISCOUNT_2"
      },
      {
        "code": "DISCOUNT_3"
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation discountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) { discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) { bulkCreation { id } userErrors { code field message } } }",
   "variables": {
      "discountId": "gid://shopify/DiscountCodeNode/2429471",
      "codes": [
        {
          "code": "DISCOUNT_1"
        },
        {
          "code": "DISCOUNT_2"
        },
        {
          "code": "DISCOUNT_3"
        }
      ]
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
    mutation discountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
      discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
        bulkCreation {
          id
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "discountId": "gid://shopify/DiscountCodeNode/2429471",
          "codes": [
              {
                  "code": "DISCOUNT_1"
              },
              {
                  "code": "DISCOUNT_2"
              },
              {
                  "code": "DISCOUNT_3"
              }
          ]
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
    mutation discountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
      discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
        bulkCreation {
          id
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "codes": [
      {
        "code": "DISCOUNT_1"
      },
      {
        "code": "DISCOUNT_2"
      },
      {
        "code": "DISCOUNT_3"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
        discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
          bulkCreation {
            id
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "discountId": "gid://shopify/DiscountCodeNode/2429471",
          "codes": [
              {
                  "code": "DISCOUNT_1"
              },
              {
                  "code": "DISCOUNT_2"
              },
              {
                  "code": "DISCOUNT_3"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
    discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
      bulkCreation {
        id
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "codes": [
      {
        "code": "DISCOUNT_1"
      },
      {
        "code": "DISCOUNT_2"
      },
      {
        "code": "DISCOUNT_3"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "discountRedeemCodeBulkAdd": {
      "bulkCreation": {
        "id": "gid://shopify/DiscountRedeemCodeBulkCreation/989355207"
      },
      "userErrors": []
    }
  }
  ```

* ### Creates a discount code

  #### Query

  ```graphql
  mutation DiscountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
    discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
      bulkCreation {
        id
        createdAt
        discountCode {
          id
        }
        done
        codesCount
        importedCount
        failedCount
      }
      userErrors {
        code
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "codes": [
      {
        "code": "DISCOUNT_1"
      },
      {
        "code": "DISCOUNT_2"
      },
      {
        "code": "DISCOUNT_3"
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation DiscountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) { discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) { bulkCreation { id createdAt discountCode { id } done codesCount importedCount failedCount } userErrors { code field message } } }",
   "variables": {
      "discountId": "gid://shopify/DiscountCodeNode/2429471",
      "codes": [
        {
          "code": "DISCOUNT_1"
        },
        {
          "code": "DISCOUNT_2"
        },
        {
          "code": "DISCOUNT_3"
        }
      ]
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
    mutation DiscountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
      discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
        bulkCreation {
          id
          createdAt
          discountCode {
            id
          }
          done
          codesCount
          importedCount
          failedCount
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "discountId": "gid://shopify/DiscountCodeNode/2429471",
          "codes": [
              {
                  "code": "DISCOUNT_1"
              },
              {
                  "code": "DISCOUNT_2"
              },
              {
                  "code": "DISCOUNT_3"
              }
          ]
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
    mutation DiscountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
      discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
        bulkCreation {
          id
          createdAt
          discountCode {
            id
          }
          done
          codesCount
          importedCount
          failedCount
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "codes": [
      {
        "code": "DISCOUNT_1"
      },
      {
        "code": "DISCOUNT_2"
      },
      {
        "code": "DISCOUNT_3"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation DiscountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
        discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
          bulkCreation {
            id
            createdAt
            discountCode {
              id
            }
            done
            codesCount
            importedCount
            failedCount
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "discountId": "gid://shopify/DiscountCodeNode/2429471",
          "codes": [
              {
                  "code": "DISCOUNT_1"
              },
              {
                  "code": "DISCOUNT_2"
              },
              {
                  "code": "DISCOUNT_3"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation DiscountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
    discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
      bulkCreation {
        id
        createdAt
        discountCode {
          id
        }
        done
        codesCount
        importedCount
        failedCount
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "codes": [
      {
        "code": "DISCOUNT_1"
      },
      {
        "code": "DISCOUNT_2"
      },
      {
        "code": "DISCOUNT_3"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "discountRedeemCodeBulkAdd": {
      "bulkCreation": {
        "id": "gid://shopify/DiscountRedeemCodeBulkCreation/989355210",
        "createdAt": "2024-11-06T21:59:51Z",
        "discountCode": {
          "id": "gid://shopify/DiscountCodeNode/2429471"
        },
        "done": false,
        "codesCount": 3,
        "importedCount": 0,
        "failedCount": 0
      },
      "userErrors": []
    }
  }
  ```

* ### Creates a discount code creation job

  #### Query

  ```graphql
  mutation DiscountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
    discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
      bulkCreation {
        id
        createdAt
        discountCode {
          id
        }
        done
        codesCount
        importedCount
        failedCount
      }
      userErrors {
        code
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "codes": [
      {
        "code": "DISCOUNT_1"
      },
      {
        "code": "DISCOUNT_2"
      },
      {
        "code": "DISCOUNT_3"
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation DiscountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) { discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) { bulkCreation { id createdAt discountCode { id } done codesCount importedCount failedCount } userErrors { code field message } } }",
   "variables": {
      "discountId": "gid://shopify/DiscountCodeNode/2429471",
      "codes": [
        {
          "code": "DISCOUNT_1"
        },
        {
          "code": "DISCOUNT_2"
        },
        {
          "code": "DISCOUNT_3"
        }
      ]
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
    mutation DiscountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
      discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
        bulkCreation {
          id
          createdAt
          discountCode {
            id
          }
          done
          codesCount
          importedCount
          failedCount
        }
        userErrors {
          code
          field
          message
        }
      }
    }`,
    {
      variables: {
          "discountId": "gid://shopify/DiscountCodeNode/2429471",
          "codes": [
              {
                  "code": "DISCOUNT_1"
              },
              {
                  "code": "DISCOUNT_2"
              },
              {
                  "code": "DISCOUNT_3"
              }
          ]
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
    mutation DiscountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
      discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
        bulkCreation {
          id
          createdAt
          discountCode {
            id
          }
          done
          codesCount
          importedCount
          failedCount
        }
        userErrors {
          code
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "codes": [
      {
        "code": "DISCOUNT_1"
      },
      {
        "code": "DISCOUNT_2"
      },
      {
        "code": "DISCOUNT_3"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation DiscountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
        discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
          bulkCreation {
            id
            createdAt
            discountCode {
              id
            }
            done
            codesCount
            importedCount
            failedCount
          }
          userErrors {
            code
            field
            message
          }
        }
      }`,
      "variables": {
          "discountId": "gid://shopify/DiscountCodeNode/2429471",
          "codes": [
              {
                  "code": "DISCOUNT_1"
              },
              {
                  "code": "DISCOUNT_2"
              },
              {
                  "code": "DISCOUNT_3"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation DiscountRedeemCodeBulkAdd($discountId: ID!, $codes: [DiscountRedeemCodeInput!]!) {
    discountRedeemCodeBulkAdd(discountId: $discountId, codes: $codes) {
      bulkCreation {
        id
        createdAt
        discountCode {
          id
        }
        done
        codesCount
        importedCount
        failedCount
      }
      userErrors {
        code
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "discountId": "gid://shopify/DiscountCodeNode/2429471",
    "codes": [
      {
        "code": "DISCOUNT_1"
      },
      {
        "code": "DISCOUNT_2"
      },
      {
        "code": "DISCOUNT_3"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "discountRedeemCodeBulkAdd": {
      "bulkCreation": {
        "id": "gid://shopify/DiscountRedeemCodeBulkCreation/989355209",
        "createdAt": "2024-11-06T21:59:51Z",
        "discountCode": {
          "id": "gid://shopify/DiscountCodeNode/2429471"
        },
        "done": false,
        "codesCount": 3,
        "importedCount": 0,
        "failedCount": 0
      },
      "userErrors": []
    }
  }
  ```

* ### discountRedeemCodeBulkAdd reference
