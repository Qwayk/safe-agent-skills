---
title: discountAutomaticAppCreate - GraphQL Admin
description: >-
  Creates an automatic discount that's managed by an app.

  Use this mutation with [Shopify
  Functions](https://shopify.dev/docs/apps/build/functions)

  when you need advanced, custom, or dynamic discount capabilities that aren't
  supported by

  [Shopify's native discount
  types](https://help.shopify.com/manual/discounts/discount-types).


  For example, use this mutation to create an automatic discount using an app's

  "Volume" discount type that applies a percentage

  off when customers purchase more than the minimum quantity of a product. For
  an example implementation,

  refer to [our
  tutorial](https://shopify.dev/docs/apps/build/discounts/build-discount-function).


  > Note:

  > To create code discounts with custom logic, use the

  [`discountCodeAppCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppCreate)

  mutation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppCreate.md
---

# discount​Automatic​App​Create

mutation

Requires `write_discounts` access scope.

Creates an automatic discount that's managed by an app. Use this mutation with [Shopify Functions](https://shopify.dev/docs/apps/build/functions) when you need advanced, custom, or dynamic discount capabilities that aren't supported by [Shopify's native discount types](https://help.shopify.com/manual/discounts/discount-types).

For example, use this mutation to create an automatic discount using an app's "Volume" discount type that applies a percentage off when customers purchase more than the minimum quantity of a product. For an example implementation, refer to [our tutorial](https://shopify.dev/docs/apps/build/discounts/build-discount-function).

***

**Note:** To create code discounts with custom logic, use the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppCreate">\<code>\<span class="PreventFireFoxApplyingGapToWBR">discount\<wbr/>Code\<wbr/>App\<wbr/>Create\</span>\</code>\</a> mutation.

***

## Arguments

* automatic​App​Discount

  [Discount​Automatic​App​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DiscountAutomaticAppInput)

  required

  The input data used to create the automatic discount.

***

## Discount​Automatic​App​Create​Payload returns

* automatic​App​Discount

  [Discount​Automatic​App](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomaticApp)

  The automatic discount that the app manages.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a non-combinable automatic order discount that's managed by an app

  #### Description

  Create an automatic discount that's managed by an app using \[Shopify Functions]\(https://shopify.dev/docs/apps/build/functions). This example shows how to create an automatic discount that takes $5 off the order subtotal and can't be \[combined]\(https://help.shopify.com/manual/discounts/combining-discounts/discount-combinations) with other discounts.

  #### Query

  ```graphql
  mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
    discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
      userErrors {
        field
        message
      }
      automaticAppDiscount {
        discountId
        title
        startsAt
        endsAt
        status
        appDiscountType {
          appKey
          functionId
        }
        combinesWith {
          orderDiscounts
          productDiscounts
          shippingDiscounts
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "automaticAppDiscount": {
      "title": "$5 discount",
      "functionId": "a3cdef66-d84a-4254-9216-b6dd723005ad",
      "startsAt": "2025-02-02T17:09:21Z",
      "endsAt": "2025-02-02T17:09:21Z",
      "combinesWith": {
        "orderDiscounts": false,
        "productDiscounts": false,
        "shippingDiscounts": false
      },
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 5}},\n    \"targets\": [{\"orderSubtotal\": {\"excludedVariantIds\": []}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
        }
      ]
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
  "query": "mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) { discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) { userErrors { field message } automaticAppDiscount { discountId title startsAt endsAt status appDiscountType { appKey functionId } combinesWith { orderDiscounts productDiscounts shippingDiscounts } } } }",
   "variables": {
      "automaticAppDiscount": {
        "title": "$5 discount",
        "functionId": "a3cdef66-d84a-4254-9216-b6dd723005ad",
        "startsAt": "2025-02-02T17:09:21Z",
        "endsAt": "2025-02-02T17:09:21Z",
        "combinesWith": {
          "orderDiscounts": false,
          "productDiscounts": false,
          "shippingDiscounts": false
        },
        "metafields": [
          {
            "namespace": "default",
            "key": "function-configuration",
            "type": "json",
            "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 5}},\n    \"targets\": [{\"orderSubtotal\": {\"excludedVariantIds\": []}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
          }
        ]
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
    mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
      discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
        userErrors {
          field
          message
        }
        automaticAppDiscount {
          discountId
          title
          startsAt
          endsAt
          status
          appDiscountType {
            appKey
            functionId
          }
          combinesWith {
            orderDiscounts
            productDiscounts
            shippingDiscounts
          }
        }
      }
    }`,
    {
      variables: {
          "automaticAppDiscount": {
              "title": "$5 discount",
              "functionId": "a3cdef66-d84a-4254-9216-b6dd723005ad",
              "startsAt": "2025-02-02T17:09:21Z",
              "endsAt": "2025-02-02T17:09:21Z",
              "combinesWith": {
                  "orderDiscounts": false,
                  "productDiscounts": false,
                  "shippingDiscounts": false
              },
              "metafields": [
                  {
                      "namespace": "default",
                      "key": "function-configuration",
                      "type": "json",
                      "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 5}},\n    \"targets\": [{\"orderSubtotal\": {\"excludedVariantIds\": []}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
                  }
              ]
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
    mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
      discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
        userErrors {
          field
          message
        }
        automaticAppDiscount {
          discountId
          title
          startsAt
          endsAt
          status
          appDiscountType {
            appKey
            functionId
          }
          combinesWith {
            orderDiscounts
            productDiscounts
            shippingDiscounts
          }
        }
      }
    }
  QUERY

  variables = {
    "automaticAppDiscount": {
      "title": "$5 discount",
      "functionId": "a3cdef66-d84a-4254-9216-b6dd723005ad",
      "startsAt": "2025-02-02T17:09:21Z",
      "endsAt": "2025-02-02T17:09:21Z",
      "combinesWith": {
        "orderDiscounts": false,
        "productDiscounts": false,
        "shippingDiscounts": false
      },
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 5}},\n    \"targets\": [{\"orderSubtotal\": {\"excludedVariantIds\": []}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
        }
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
        discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
          userErrors {
            field
            message
          }
          automaticAppDiscount {
            discountId
            title
            startsAt
            endsAt
            status
            appDiscountType {
              appKey
              functionId
            }
            combinesWith {
              orderDiscounts
              productDiscounts
              shippingDiscounts
            }
          }
        }
      }`,
      "variables": {
          "automaticAppDiscount": {
              "title": "$5 discount",
              "functionId": "a3cdef66-d84a-4254-9216-b6dd723005ad",
              "startsAt": "2025-02-02T17:09:21Z",
              "endsAt": "2025-02-02T17:09:21Z",
              "combinesWith": {
                  "orderDiscounts": false,
                  "productDiscounts": false,
                  "shippingDiscounts": false
              },
              "metafields": [
                  {
                      "namespace": "default",
                      "key": "function-configuration",
                      "type": "json",
                      "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 5}},\n    \"targets\": [{\"orderSubtotal\": {\"excludedVariantIds\": []}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
                  }
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
    discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
      userErrors {
        field
        message
      }
      automaticAppDiscount {
        discountId
        title
        startsAt
        endsAt
        status
        appDiscountType {
          appKey
          functionId
        }
        combinesWith {
          orderDiscounts
          productDiscounts
          shippingDiscounts
        }
      }
    }
  }' \
  --variables \
  '{
    "automaticAppDiscount": {
      "title": "$5 discount",
      "functionId": "a3cdef66-d84a-4254-9216-b6dd723005ad",
      "startsAt": "2025-02-02T17:09:21Z",
      "endsAt": "2025-02-02T17:09:21Z",
      "combinesWith": {
        "orderDiscounts": false,
        "productDiscounts": false,
        "shippingDiscounts": false
      },
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 5}},\n    \"targets\": [{\"orderSubtotal\": {\"excludedVariantIds\": []}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticAppCreate": {
      "userErrors": [],
      "automaticAppDiscount": {
        "discountId": "gid://shopify/DiscountAutomaticNode/1057856655",
        "title": "$5 discount",
        "startsAt": "2025-02-02T17:09:21Z",
        "endsAt": "2025-02-02T17:09:21Z",
        "status": "EXPIRED",
        "appDiscountType": {
          "appKey": "shopify-web",
          "functionId": "13d358d1-2a5b-4a39-a6f9-8f53394e440d"
        },
        "combinesWith": {
          "orderDiscounts": false,
          "productDiscounts": false,
          "shippingDiscounts": false
        }
      }
    }
  }
  ```

* ### Create an automatic app product discount for a customer segment

  #### Description

  Create an automatic discount that's managed by an app using \[Shopify Functions]\(https://shopify.dev/docs/apps/build/functions). This example shows how to create an automatic discount that takes $10 off a specific product and applies only to a specific customer segment.

  #### Query

  ```graphql
  mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
    discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
      userErrors {
        field
        message
      }
      automaticAppDiscount {
        discountId
        title
        startsAt
        endsAt
        status
        context {
          ... on DiscountCustomerSegments {
            segments {
              id
            }
          }
        }
        appDiscountType {
          appKey
          functionId
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "automaticAppDiscount": {
      "title": "Product discount $10 off",
      "functionId": "6bb26213-4a3c-4e83-94bf-98599b4b6648",
      "startsAt": "2025-07-25T19:52:03-04:00",
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/8961721"
          ]
        }
      },
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 10}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
        }
      ]
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
  "query": "mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) { discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) { userErrors { field message } automaticAppDiscount { discountId title startsAt endsAt status context { ... on DiscountCustomerSegments { segments { id } } } appDiscountType { appKey functionId } } } }",
   "variables": {
      "automaticAppDiscount": {
        "title": "Product discount $10 off",
        "functionId": "6bb26213-4a3c-4e83-94bf-98599b4b6648",
        "startsAt": "2025-07-25T19:52:03-04:00",
        "context": {
          "customerSegments": {
            "add": [
              "gid://shopify/Segment/8961721"
            ]
          }
        },
        "metafields": [
          {
            "namespace": "default",
            "key": "function-configuration",
            "type": "json",
            "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 10}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
          }
        ]
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
    mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
      discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
        userErrors {
          field
          message
        }
        automaticAppDiscount {
          discountId
          title
          startsAt
          endsAt
          status
          context {
            ... on DiscountCustomerSegments {
              segments {
                id
              }
            }
          }
          appDiscountType {
            appKey
            functionId
          }
        }
      }
    }`,
    {
      variables: {
          "automaticAppDiscount": {
              "title": "Product discount $10 off",
              "functionId": "6bb26213-4a3c-4e83-94bf-98599b4b6648",
              "startsAt": "2025-07-25T19:52:03-04:00",
              "context": {
                  "customerSegments": {
                      "add": [
                          "gid://shopify/Segment/8961721"
                      ]
                  }
              },
              "metafields": [
                  {
                      "namespace": "default",
                      "key": "function-configuration",
                      "type": "json",
                      "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 10}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
                  }
              ]
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
    mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
      discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
        userErrors {
          field
          message
        }
        automaticAppDiscount {
          discountId
          title
          startsAt
          endsAt
          status
          context {
            ... on DiscountCustomerSegments {
              segments {
                id
              }
            }
          }
          appDiscountType {
            appKey
            functionId
          }
        }
      }
    }
  QUERY

  variables = {
    "automaticAppDiscount": {
      "title": "Product discount $10 off",
      "functionId": "6bb26213-4a3c-4e83-94bf-98599b4b6648",
      "startsAt": "2025-07-25T19:52:03-04:00",
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/8961721"
          ]
        }
      },
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 10}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
        }
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
        discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
          userErrors {
            field
            message
          }
          automaticAppDiscount {
            discountId
            title
            startsAt
            endsAt
            status
            context {
              ... on DiscountCustomerSegments {
                segments {
                  id
                }
              }
            }
            appDiscountType {
              appKey
              functionId
            }
          }
        }
      }`,
      "variables": {
          "automaticAppDiscount": {
              "title": "Product discount $10 off",
              "functionId": "6bb26213-4a3c-4e83-94bf-98599b4b6648",
              "startsAt": "2025-07-25T19:52:03-04:00",
              "context": {
                  "customerSegments": {
                      "add": [
                          "gid://shopify/Segment/8961721"
                      ]
                  }
              },
              "metafields": [
                  {
                      "namespace": "default",
                      "key": "function-configuration",
                      "type": "json",
                      "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 10}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
                  }
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
    discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
      userErrors {
        field
        message
      }
      automaticAppDiscount {
        discountId
        title
        startsAt
        endsAt
        status
        context {
          ... on DiscountCustomerSegments {
            segments {
              id
            }
          }
        }
        appDiscountType {
          appKey
          functionId
        }
      }
    }
  }' \
  --variables \
  '{
    "automaticAppDiscount": {
      "title": "Product discount $10 off",
      "functionId": "6bb26213-4a3c-4e83-94bf-98599b4b6648",
      "startsAt": "2025-07-25T19:52:03-04:00",
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/8961721"
          ]
        }
      },
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 10}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticAppCreate": {
      "userErrors": [],
      "automaticAppDiscount": {
        "discountId": "gid://shopify/DiscountAutomaticNode/1057856656",
        "title": "Product discount $10 off",
        "startsAt": "2025-07-25T23:52:03Z",
        "endsAt": null,
        "status": "ACTIVE",
        "context": {
          "segments": [
            {
              "id": "gid://shopify/Segment/8961721"
            }
          ]
        },
        "appDiscountType": {
          "appKey": "shopify-web",
          "functionId": "6bb26213-4a3c-4e83-94bf-98599b4b6648"
        }
      }
    }
  }
  ```

* ### Create an automatic product discount that's managed by an app

  #### Description

  Create an automatic discount that's managed by an app using \[Shopify Functions]\(https://shopify.dev/docs/apps/build/functions). This example shows how to create an automatic discount that takes $10 off a specific product.

  #### Query

  ```graphql
  mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
    discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
      userErrors {
        field
        message
      }
      automaticAppDiscount {
        discountId
        title
        startsAt
        endsAt
        status
        appDiscountType {
          appKey
          functionId
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "automaticAppDiscount": {
      "title": "Product discount $10 off",
      "functionId": "677bc937-7dce-4fe4-8e8d-076c391d3e53",
      "startsAt": "2025-01-01T00:00:00Z",
      "endsAt": "2025-12-31T23:59:59Z",
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 10}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
        }
      ]
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
  "query": "mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) { discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) { userErrors { field message } automaticAppDiscount { discountId title startsAt endsAt status appDiscountType { appKey functionId } } } }",
   "variables": {
      "automaticAppDiscount": {
        "title": "Product discount $10 off",
        "functionId": "677bc937-7dce-4fe4-8e8d-076c391d3e53",
        "startsAt": "2025-01-01T00:00:00Z",
        "endsAt": "2025-12-31T23:59:59Z",
        "metafields": [
          {
            "namespace": "default",
            "key": "function-configuration",
            "type": "json",
            "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 10}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
          }
        ]
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
    mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
      discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
        userErrors {
          field
          message
        }
        automaticAppDiscount {
          discountId
          title
          startsAt
          endsAt
          status
          appDiscountType {
            appKey
            functionId
          }
        }
      }
    }`,
    {
      variables: {
          "automaticAppDiscount": {
              "title": "Product discount $10 off",
              "functionId": "677bc937-7dce-4fe4-8e8d-076c391d3e53",
              "startsAt": "2025-01-01T00:00:00Z",
              "endsAt": "2025-12-31T23:59:59Z",
              "metafields": [
                  {
                      "namespace": "default",
                      "key": "function-configuration",
                      "type": "json",
                      "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 10}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
                  }
              ]
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
    mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
      discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
        userErrors {
          field
          message
        }
        automaticAppDiscount {
          discountId
          title
          startsAt
          endsAt
          status
          appDiscountType {
            appKey
            functionId
          }
        }
      }
    }
  QUERY

  variables = {
    "automaticAppDiscount": {
      "title": "Product discount $10 off",
      "functionId": "677bc937-7dce-4fe4-8e8d-076c391d3e53",
      "startsAt": "2025-01-01T00:00:00Z",
      "endsAt": "2025-12-31T23:59:59Z",
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 10}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
        }
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
        discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
          userErrors {
            field
            message
          }
          automaticAppDiscount {
            discountId
            title
            startsAt
            endsAt
            status
            appDiscountType {
              appKey
              functionId
            }
          }
        }
      }`,
      "variables": {
          "automaticAppDiscount": {
              "title": "Product discount $10 off",
              "functionId": "677bc937-7dce-4fe4-8e8d-076c391d3e53",
              "startsAt": "2025-01-01T00:00:00Z",
              "endsAt": "2025-12-31T23:59:59Z",
              "metafields": [
                  {
                      "namespace": "default",
                      "key": "function-configuration",
                      "type": "json",
                      "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 10}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
                  }
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountAutomaticAppCreate($automaticAppDiscount: DiscountAutomaticAppInput!) {
    discountAutomaticAppCreate(automaticAppDiscount: $automaticAppDiscount) {
      userErrors {
        field
        message
      }
      automaticAppDiscount {
        discountId
        title
        startsAt
        endsAt
        status
        appDiscountType {
          appKey
          functionId
        }
      }
    }
  }' \
  --variables \
  '{
    "automaticAppDiscount": {
      "title": "Product discount $10 off",
      "functionId": "677bc937-7dce-4fe4-8e8d-076c391d3e53",
      "startsAt": "2025-01-01T00:00:00Z",
      "endsAt": "2025-12-31T23:59:59Z",
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 10}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticAppCreate": {
      "userErrors": [],
      "automaticAppDiscount": {
        "discountId": "gid://shopify/DiscountAutomaticNode/1057856654",
        "title": "Product discount $10 off",
        "startsAt": "2025-01-01T00:00:00Z",
        "endsAt": "2025-12-31T23:59:59Z",
        "status": "ACTIVE",
        "appDiscountType": {
          "appKey": "shopify-web",
          "functionId": "677bc937-7dce-4fe4-8e8d-076c391d3e53"
        }
      }
    }
  }
  ```

* ### discountAutomaticAppCreate reference
