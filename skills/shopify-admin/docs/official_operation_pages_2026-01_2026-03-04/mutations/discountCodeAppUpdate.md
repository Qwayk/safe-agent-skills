---
title: discountCodeAppUpdate - GraphQL Admin
description: >-
  Updates a code discount, where the discount type is provided by an app
  extension that uses [Shopify
  Functions](https://shopify.dev/docs/apps/build/functions). Use this mutation
  when you need advanced, custom, or dynamic discount capabilities that aren't
  supported by [Shopify's native discount
  types](https://help.shopify.com/manual/discounts/discount-types).


  > Note:

  > To update automatic discounts, use
  [`discountAutomaticAppUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppUpdate).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppUpdate.md
---

# discount​Code​App​Update

mutation

Requires `write_discounts` access scope.

Updates a code discount, where the discount type is provided by an app extension that uses [Shopify Functions](https://shopify.dev/docs/apps/build/functions). Use this mutation when you need advanced, custom, or dynamic discount capabilities that aren't supported by [Shopify's native discount types](https://help.shopify.com/manual/discounts/discount-types).

***

**Note:** To update automatic discounts, use \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppUpdate">\<code>\<span class="PreventFireFoxApplyingGapToWBR">discount\<wbr/>Automatic\<wbr/>App\<wbr/>Update\</span>\</code>\</a>.

***

## Arguments

* code​App​Discount

  [Discount​Code​App​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DiscountCodeAppInput)

  required

  The input fields required to update the discount.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the discount to update.

***

## Discount​Code​App​Update​Payload returns

* code​App​Discount

  [Discount​Code​App](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountCodeApp)

  The updated discount that the app provides.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update the context of a discount code that's managed by an app

  #### Description

  Update a code discount that's managed by an app using \[Shopify Functions]\(https://shopify.dev/docs/apps/build/functions). This example shows how to update the context defining which buyers can use the code discount.

  #### Query

  ```graphql
  mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!) {
    discountCodeAppUpdate(codeAppDiscount: $codeAppDiscount, id: $id) {
      codeAppDiscount {
        title
        context {
          ... on DiscountCustomerSegments {
            segments {
              id
            }
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
    "id": "gid://shopify/DiscountCodeNode/549381256",
    "codeAppDiscount": {
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/8961721"
          ]
        }
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
  "query": "mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!) { discountCodeAppUpdate(codeAppDiscount: $codeAppDiscount, id: $id) { codeAppDiscount { title context { ... on DiscountCustomerSegments { segments { id } } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DiscountCodeNode/549381256",
      "codeAppDiscount": {
        "context": {
          "customerSegments": {
            "add": [
              "gid://shopify/Segment/8961721"
            ]
          }
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
    mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!) {
      discountCodeAppUpdate(codeAppDiscount: $codeAppDiscount, id: $id) {
        codeAppDiscount {
          title
          context {
            ... on DiscountCustomerSegments {
              segments {
                id
              }
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
          "id": "gid://shopify/DiscountCodeNode/549381256",
          "codeAppDiscount": {
              "context": {
                  "customerSegments": {
                      "add": [
                          "gid://shopify/Segment/8961721"
                      ]
                  }
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
    mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!) {
      discountCodeAppUpdate(codeAppDiscount: $codeAppDiscount, id: $id) {
        codeAppDiscount {
          title
          context {
            ... on DiscountCustomerSegments {
              segments {
                id
              }
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
    "id": "gid://shopify/DiscountCodeNode/549381256",
    "codeAppDiscount": {
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/8961721"
          ]
        }
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
      "query": `mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!) {
        discountCodeAppUpdate(codeAppDiscount: $codeAppDiscount, id: $id) {
          codeAppDiscount {
            title
            context {
              ... on DiscountCustomerSegments {
                segments {
                  id
                }
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
          "id": "gid://shopify/DiscountCodeNode/549381256",
          "codeAppDiscount": {
              "context": {
                  "customerSegments": {
                      "add": [
                          "gid://shopify/Segment/8961721"
                      ]
                  }
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
  'mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!) {
    discountCodeAppUpdate(codeAppDiscount: $codeAppDiscount, id: $id) {
      codeAppDiscount {
        title
        context {
          ... on DiscountCustomerSegments {
            segments {
              id
            }
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
    "id": "gid://shopify/DiscountCodeNode/549381256",
    "codeAppDiscount": {
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/8961721"
          ]
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeAppUpdate": {
      "codeAppDiscount": {
        "title": "Code Percentage off (Product)",
        "context": {
          "segments": [
            {
              "id": "gid://shopify/Segment/8961721"
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Update the title of a discount code that's managed by an app

  #### Description

  Update a code discount that's managed by an app using \[Shopify Functions]\(https://shopify.dev/docs/apps/build/functions). This example shows how to update the title of the discount.

  #### Query

  ```graphql
  mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!) {
    discountCodeAppUpdate(codeAppDiscount: $codeAppDiscount, id: $id) {
      codeAppDiscount {
        discountId
        title
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
    "id": "gid://shopify/DiscountCodeNode/549381256",
    "codeAppDiscount": {
      "title": "Take 5$ from order discount"
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
  "query": "mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!) { discountCodeAppUpdate(codeAppDiscount: $codeAppDiscount, id: $id) { codeAppDiscount { discountId title } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DiscountCodeNode/549381256",
      "codeAppDiscount": {
        "title": "Take 5$ from order discount"
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
    mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!) {
      discountCodeAppUpdate(codeAppDiscount: $codeAppDiscount, id: $id) {
        codeAppDiscount {
          discountId
          title
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DiscountCodeNode/549381256",
          "codeAppDiscount": {
              "title": "Take 5$ from order discount"
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
    mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!) {
      discountCodeAppUpdate(codeAppDiscount: $codeAppDiscount, id: $id) {
        codeAppDiscount {
          discountId
          title
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DiscountCodeNode/549381256",
    "codeAppDiscount": {
      "title": "Take 5$ from order discount"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!) {
        discountCodeAppUpdate(codeAppDiscount: $codeAppDiscount, id: $id) {
          codeAppDiscount {
            discountId
            title
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DiscountCodeNode/549381256",
          "codeAppDiscount": {
              "title": "Take 5$ from order discount"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountCodeAppUpdate($codeAppDiscount: DiscountCodeAppInput!, $id: ID!) {
    discountCodeAppUpdate(codeAppDiscount: $codeAppDiscount, id: $id) {
      codeAppDiscount {
        discountId
        title
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DiscountCodeNode/549381256",
    "codeAppDiscount": {
      "title": "Take 5$ from order discount"
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeAppUpdate": {
      "codeAppDiscount": {
        "discountId": "gid://shopify/DiscountCodeNode/549381256",
        "title": "Take 5$ from order discount"
      },
      "userErrors": []
    }
  }
  ```

* ### discountCodeAppUpdate reference
