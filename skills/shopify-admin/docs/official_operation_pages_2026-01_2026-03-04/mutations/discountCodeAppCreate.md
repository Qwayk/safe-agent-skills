---
title: discountCodeAppCreate - GraphQL Admin
description: >-
  Creates a code discount. The discount type must be provided by an app
  extension that uses [Shopify
  Functions](https://shopify.dev/docs/apps/build/functions). Functions can
  implement
  [order](https://shopify.dev/docs/api/functions/reference/order-discounts),
  [product](https://shopify.dev/docs/api/functions/reference/product-discounts),
  or
  [shipping](https://shopify.dev/docs/api/functions/reference/shipping-discounts)
  discount functions. Use this mutation with Shopify Functions when you need
  custom logic beyond [Shopify's native discount
  types](https://help.shopify.com/manual/discounts/discount-types).


  For example, use this mutation to create a code discount using an app's
  "Volume" discount type that applies a percentage off when customers purchase
  more than the minimum quantity

  of a product. For an example implementation, refer to [our
  tutorial](https://shopify.dev/docs/apps/build/discounts/build-discount-function).


  > Note:

  > To create automatic discounts with custom logic, use
  [`discountAutomaticAppCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppCreate).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppCreate.md
---

# discount​Code​App​Create

mutation

Requires `write_discounts` access scope.

Creates a code discount. The discount type must be provided by an app extension that uses [Shopify Functions](https://shopify.dev/docs/apps/build/functions). Functions can implement [order](https://shopify.dev/docs/api/functions/reference/order-discounts), [product](https://shopify.dev/docs/api/functions/reference/product-discounts), or [shipping](https://shopify.dev/docs/api/functions/reference/shipping-discounts) discount functions. Use this mutation with Shopify Functions when you need custom logic beyond [Shopify's native discount types](https://help.shopify.com/manual/discounts/discount-types).

For example, use this mutation to create a code discount using an app's "Volume" discount type that applies a percentage off when customers purchase more than the minimum quantity of a product. For an example implementation, refer to [our tutorial](https://shopify.dev/docs/apps/build/discounts/build-discount-function).

***

**Note:** To create automatic discounts with custom logic, use \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppCreate">\<code>\<span class="PreventFireFoxApplyingGapToWBR">discount\<wbr/>Automatic\<wbr/>App\<wbr/>Create\</span>\</code>\</a>.

***

## Arguments

* code​App​Discount

  [Discount​Code​App​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DiscountCodeAppInput)

  required

  The input data used to create the discount.

***

## Discount​Code​App​Create​Payload returns

* code​App​Discount

  [Discount​Code​App](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountCodeApp)

  The discount that the app provides.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a product discount that's managed by an app

  #### Description

  Create a code discount that's managed by an app using \[Shopify Functions]\(https://shopify.dev/docs/apps/build/functions). This example shows how to create a code discount that takes 10% off specific products.

  #### Query

  ```graphql
  mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
    discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
      codeAppDiscount {
        discountId
        title
        appDiscountType {
          description
          functionId
        }
        combinesWith {
          orderDiscounts
          productDiscounts
          shippingDiscounts
        }
        codes(first: 5) {
          nodes {
            code
          }
        }
        status
        usageLimit
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
    "codeAppDiscount": {
      "code": "PRODUCT10",
      "title": "10% off selected products",
      "functionId": "859fcac2-cf96-44db-8146-977445fa90c8",
      "appliesOncePerCustomer": false,
      "combinesWith": {
        "orderDiscounts": false,
        "productDiscounts": false,
        "shippingDiscounts": true
      },
      "startsAt": "2025-01-01T00:00:00Z",
      "endsAt": "2025-12-31T23:59:59Z",
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\"discounts\":[{\"value\":{\"percentage\":0.10},\"targets\":[{\"productVariants\":\n                        {\"productsToDiscount\":[\"gid://shopify/Product/123\"],\"excludedVariantIds\":[]}}]}],\n                        \"discountApplicationStrategy\":\"FIRST\"}"
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
  "query": "mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) { discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) { codeAppDiscount { discountId title appDiscountType { description functionId } combinesWith { orderDiscounts productDiscounts shippingDiscounts } codes(first: 5) { nodes { code } } status usageLimit } userErrors { field message } } }",
   "variables": {
      "codeAppDiscount": {
        "code": "PRODUCT10",
        "title": "10% off selected products",
        "functionId": "859fcac2-cf96-44db-8146-977445fa90c8",
        "appliesOncePerCustomer": false,
        "combinesWith": {
          "orderDiscounts": false,
          "productDiscounts": false,
          "shippingDiscounts": true
        },
        "startsAt": "2025-01-01T00:00:00Z",
        "endsAt": "2025-12-31T23:59:59Z",
        "metafields": [
          {
            "namespace": "default",
            "key": "function-configuration",
            "type": "json",
            "value": "{\"discounts\":[{\"value\":{\"percentage\":0.10},\"targets\":[{\"productVariants\":\n                        {\"productsToDiscount\":[\"gid://shopify/Product/123\"],\"excludedVariantIds\":[]}}]}],\n                        \"discountApplicationStrategy\":\"FIRST\"}"
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
    mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
      discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
        codeAppDiscount {
          discountId
          title
          appDiscountType {
            description
            functionId
          }
          combinesWith {
            orderDiscounts
            productDiscounts
            shippingDiscounts
          }
          codes(first: 5) {
            nodes {
              code
            }
          }
          status
          usageLimit
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "codeAppDiscount": {
              "code": "PRODUCT10",
              "title": "10% off selected products",
              "functionId": "859fcac2-cf96-44db-8146-977445fa90c8",
              "appliesOncePerCustomer": false,
              "combinesWith": {
                  "orderDiscounts": false,
                  "productDiscounts": false,
                  "shippingDiscounts": true
              },
              "startsAt": "2025-01-01T00:00:00Z",
              "endsAt": "2025-12-31T23:59:59Z",
              "metafields": [
                  {
                      "namespace": "default",
                      "key": "function-configuration",
                      "type": "json",
                      "value": "{\"discounts\":[{\"value\":{\"percentage\":0.10},\"targets\":[{\"productVariants\":\n                        {\"productsToDiscount\":[\"gid://shopify/Product/123\"],\"excludedVariantIds\":[]}}]}],\n                        \"discountApplicationStrategy\":\"FIRST\"}"
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
    mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
      discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
        codeAppDiscount {
          discountId
          title
          appDiscountType {
            description
            functionId
          }
          combinesWith {
            orderDiscounts
            productDiscounts
            shippingDiscounts
          }
          codes(first: 5) {
            nodes {
              code
            }
          }
          status
          usageLimit
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "codeAppDiscount": {
      "code": "PRODUCT10",
      "title": "10% off selected products",
      "functionId": "859fcac2-cf96-44db-8146-977445fa90c8",
      "appliesOncePerCustomer": false,
      "combinesWith": {
        "orderDiscounts": false,
        "productDiscounts": false,
        "shippingDiscounts": true
      },
      "startsAt": "2025-01-01T00:00:00Z",
      "endsAt": "2025-12-31T23:59:59Z",
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\"discounts\":[{\"value\":{\"percentage\":0.10},\"targets\":[{\"productVariants\":\n                        {\"productsToDiscount\":[\"gid://shopify/Product/123\"],\"excludedVariantIds\":[]}}]}],\n                        \"discountApplicationStrategy\":\"FIRST\"}"
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
      "query": `mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
        discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
          codeAppDiscount {
            discountId
            title
            appDiscountType {
              description
              functionId
            }
            combinesWith {
              orderDiscounts
              productDiscounts
              shippingDiscounts
            }
            codes(first: 5) {
              nodes {
                code
              }
            }
            status
            usageLimit
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "codeAppDiscount": {
              "code": "PRODUCT10",
              "title": "10% off selected products",
              "functionId": "859fcac2-cf96-44db-8146-977445fa90c8",
              "appliesOncePerCustomer": false,
              "combinesWith": {
                  "orderDiscounts": false,
                  "productDiscounts": false,
                  "shippingDiscounts": true
              },
              "startsAt": "2025-01-01T00:00:00Z",
              "endsAt": "2025-12-31T23:59:59Z",
              "metafields": [
                  {
                      "namespace": "default",
                      "key": "function-configuration",
                      "type": "json",
                      "value": "{\"discounts\":[{\"value\":{\"percentage\":0.10},\"targets\":[{\"productVariants\":\n                        {\"productsToDiscount\":[\"gid://shopify/Product/123\"],\"excludedVariantIds\":[]}}]}],\n                        \"discountApplicationStrategy\":\"FIRST\"}"
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
  'mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
    discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
      codeAppDiscount {
        discountId
        title
        appDiscountType {
          description
          functionId
        }
        combinesWith {
          orderDiscounts
          productDiscounts
          shippingDiscounts
        }
        codes(first: 5) {
          nodes {
            code
          }
        }
        status
        usageLimit
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "codeAppDiscount": {
      "code": "PRODUCT10",
      "title": "10% off selected products",
      "functionId": "859fcac2-cf96-44db-8146-977445fa90c8",
      "appliesOncePerCustomer": false,
      "combinesWith": {
        "orderDiscounts": false,
        "productDiscounts": false,
        "shippingDiscounts": true
      },
      "startsAt": "2025-01-01T00:00:00Z",
      "endsAt": "2025-12-31T23:59:59Z",
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\"discounts\":[{\"value\":{\"percentage\":0.10},\"targets\":[{\"productVariants\":\n                        {\"productsToDiscount\":[\"gid://shopify/Product/123\"],\"excludedVariantIds\":[]}}]}],\n                        \"discountApplicationStrategy\":\"FIRST\"}"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeAppCreate": {
      "codeAppDiscount": {
        "discountId": "gid://shopify/DiscountCodeNode/1057856653",
        "title": "10% off selected products",
        "appDiscountType": {
          "description": "my function does a thing",
          "functionId": "859fcac2-cf96-44db-8146-977445fa90c8"
        },
        "combinesWith": {
          "orderDiscounts": false,
          "productDiscounts": false,
          "shippingDiscounts": true
        },
        "codes": {
          "nodes": [
            {
              "code": "PRODUCT10"
            }
          ]
        },
        "status": "ACTIVE",
        "usageLimit": null
      },
      "userErrors": []
    }
  }
  ```

* ### Create a product discount that's managed by an app with a customer segment

  #### Description

  Create a code discount that's managed by an app using \[Shopify Functions]\(https://shopify.dev/docs/apps/build/functions). This example shows how to create a code discount that takes $15 off a specific product and applies only to a specific customer segment.

  #### Query

  ```graphql
  mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
    discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
      codeAppDiscount {
        discountId
        title
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
    "codeAppDiscount": {
      "code": "SEGMENT15",
      "title": "Product discount $15 off for VIP customers",
      "functionId": "e7ba3f54-3002-4b7f-a620-cd89263077a9",
      "startsAt": "2025-07-25T16:27:07-04:00",
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
          "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 15}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
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
  "query": "mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) { discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) { codeAppDiscount { discountId title context { ... on DiscountCustomerSegments { segments { id } } } appDiscountType { appKey functionId } } userErrors { field message } } }",
   "variables": {
      "codeAppDiscount": {
        "code": "SEGMENT15",
        "title": "Product discount $15 off for VIP customers",
        "functionId": "e7ba3f54-3002-4b7f-a620-cd89263077a9",
        "startsAt": "2025-07-25T16:27:07-04:00",
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
            "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 15}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
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
    mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
      discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
        codeAppDiscount {
          discountId
          title
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
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "codeAppDiscount": {
              "code": "SEGMENT15",
              "title": "Product discount $15 off for VIP customers",
              "functionId": "e7ba3f54-3002-4b7f-a620-cd89263077a9",
              "startsAt": "2025-07-25T16:27:07-04:00",
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
                      "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 15}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
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
    mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
      discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
        codeAppDiscount {
          discountId
          title
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
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "codeAppDiscount": {
      "code": "SEGMENT15",
      "title": "Product discount $15 off for VIP customers",
      "functionId": "e7ba3f54-3002-4b7f-a620-cd89263077a9",
      "startsAt": "2025-07-25T16:27:07-04:00",
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
          "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 15}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
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
      "query": `mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
        discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
          codeAppDiscount {
            discountId
            title
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
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "codeAppDiscount": {
              "code": "SEGMENT15",
              "title": "Product discount $15 off for VIP customers",
              "functionId": "e7ba3f54-3002-4b7f-a620-cd89263077a9",
              "startsAt": "2025-07-25T16:27:07-04:00",
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
                      "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 15}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
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
  'mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
    discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
      codeAppDiscount {
        discountId
        title
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
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "codeAppDiscount": {
      "code": "SEGMENT15",
      "title": "Product discount $15 off for VIP customers",
      "functionId": "e7ba3f54-3002-4b7f-a620-cd89263077a9",
      "startsAt": "2025-07-25T16:27:07-04:00",
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
          "value": "{\n  \"discounts\": [{\n    \"value\": {\"fixedAmount\": {\"amount\": 15}},\n    \"targets\": [{\"productVariant\": {\"id\": \"gid://shopify/ProductVariant/12345\"}}]\n  }],\n  \"discountApplicationStrategy\": \"FIRST\"\n}"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeAppCreate": {
      "codeAppDiscount": {
        "discountId": "gid://shopify/DiscountCodeNode/1057856651",
        "title": "Product discount $15 off for VIP customers",
        "context": {
          "segments": [
            {
              "id": "gid://shopify/Segment/8961721"
            }
          ]
        },
        "appDiscountType": {
          "appKey": "shopify-web",
          "functionId": "e7ba3f54-3002-4b7f-a620-cd89263077a9"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create an order discount that's managed by an app

  #### Description

  Create a code discount that's managed by an app using \[Shopify Functions]\(https://shopify.dev/docs/apps/build/functions). This example shows how to create a \[combinable]\(https://help.shopify.com/manual/discounts/combining-discounts/discount-combinations) code discount that takes $5 off the order subtotal.

  #### Query

  ```graphql
  mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
    discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
      codeAppDiscount {
        discountId
        title
        appDiscountType {
          description
          functionId
        }
        combinesWith {
          orderDiscounts
          productDiscounts
          shippingDiscounts
        }
        codes(first: 100) {
          nodes {
            code
          }
        }
        status
        usageLimit
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
    "codeAppDiscount": {
      "code": "APP_DISCOUNT",
      "title": "Take 5$ from order discount",
      "functionId": "dce9760f-6514-4d94-a04b-8ab8614ea6cd",
      "appliesOncePerCustomer": true,
      "combinesWith": {
        "orderDiscounts": true,
        "productDiscounts": true,
        "shippingDiscounts": true
      },
      "startsAt": "2021-02-02T17:09:21Z",
      "endsAt": "2022-02-02T17:09:21Z",
      "usageLimit": 1,
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\"discounts\":[{\"value\":{\"fixedAmount\":{\"amount\":5}},\"targets\":\n                        [{\"orderSubtotal\":{\"excludedVariantIds\":[]}}]}],\"discountApplicationStrategy\":\"FIRST\"}"
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
  "query": "mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) { discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) { codeAppDiscount { discountId title appDiscountType { description functionId } combinesWith { orderDiscounts productDiscounts shippingDiscounts } codes(first: 100) { nodes { code } } status usageLimit } userErrors { field message } } }",
   "variables": {
      "codeAppDiscount": {
        "code": "APP_DISCOUNT",
        "title": "Take 5$ from order discount",
        "functionId": "dce9760f-6514-4d94-a04b-8ab8614ea6cd",
        "appliesOncePerCustomer": true,
        "combinesWith": {
          "orderDiscounts": true,
          "productDiscounts": true,
          "shippingDiscounts": true
        },
        "startsAt": "2021-02-02T17:09:21Z",
        "endsAt": "2022-02-02T17:09:21Z",
        "usageLimit": 1,
        "metafields": [
          {
            "namespace": "default",
            "key": "function-configuration",
            "type": "json",
            "value": "{\"discounts\":[{\"value\":{\"fixedAmount\":{\"amount\":5}},\"targets\":\n                        [{\"orderSubtotal\":{\"excludedVariantIds\":[]}}]}],\"discountApplicationStrategy\":\"FIRST\"}"
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
    mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
      discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
        codeAppDiscount {
          discountId
          title
          appDiscountType {
            description
            functionId
          }
          combinesWith {
            orderDiscounts
            productDiscounts
            shippingDiscounts
          }
          codes(first: 100) {
            nodes {
              code
            }
          }
          status
          usageLimit
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "codeAppDiscount": {
              "code": "APP_DISCOUNT",
              "title": "Take 5$ from order discount",
              "functionId": "dce9760f-6514-4d94-a04b-8ab8614ea6cd",
              "appliesOncePerCustomer": true,
              "combinesWith": {
                  "orderDiscounts": true,
                  "productDiscounts": true,
                  "shippingDiscounts": true
              },
              "startsAt": "2021-02-02T17:09:21Z",
              "endsAt": "2022-02-02T17:09:21Z",
              "usageLimit": 1,
              "metafields": [
                  {
                      "namespace": "default",
                      "key": "function-configuration",
                      "type": "json",
                      "value": "{\"discounts\":[{\"value\":{\"fixedAmount\":{\"amount\":5}},\"targets\":\n                        [{\"orderSubtotal\":{\"excludedVariantIds\":[]}}]}],\"discountApplicationStrategy\":\"FIRST\"}"
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
    mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
      discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
        codeAppDiscount {
          discountId
          title
          appDiscountType {
            description
            functionId
          }
          combinesWith {
            orderDiscounts
            productDiscounts
            shippingDiscounts
          }
          codes(first: 100) {
            nodes {
              code
            }
          }
          status
          usageLimit
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "codeAppDiscount": {
      "code": "APP_DISCOUNT",
      "title": "Take 5$ from order discount",
      "functionId": "dce9760f-6514-4d94-a04b-8ab8614ea6cd",
      "appliesOncePerCustomer": true,
      "combinesWith": {
        "orderDiscounts": true,
        "productDiscounts": true,
        "shippingDiscounts": true
      },
      "startsAt": "2021-02-02T17:09:21Z",
      "endsAt": "2022-02-02T17:09:21Z",
      "usageLimit": 1,
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\"discounts\":[{\"value\":{\"fixedAmount\":{\"amount\":5}},\"targets\":\n                        [{\"orderSubtotal\":{\"excludedVariantIds\":[]}}]}],\"discountApplicationStrategy\":\"FIRST\"}"
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
      "query": `mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
        discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
          codeAppDiscount {
            discountId
            title
            appDiscountType {
              description
              functionId
            }
            combinesWith {
              orderDiscounts
              productDiscounts
              shippingDiscounts
            }
            codes(first: 100) {
              nodes {
                code
              }
            }
            status
            usageLimit
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "codeAppDiscount": {
              "code": "APP_DISCOUNT",
              "title": "Take 5$ from order discount",
              "functionId": "dce9760f-6514-4d94-a04b-8ab8614ea6cd",
              "appliesOncePerCustomer": true,
              "combinesWith": {
                  "orderDiscounts": true,
                  "productDiscounts": true,
                  "shippingDiscounts": true
              },
              "startsAt": "2021-02-02T17:09:21Z",
              "endsAt": "2022-02-02T17:09:21Z",
              "usageLimit": 1,
              "metafields": [
                  {
                      "namespace": "default",
                      "key": "function-configuration",
                      "type": "json",
                      "value": "{\"discounts\":[{\"value\":{\"fixedAmount\":{\"amount\":5}},\"targets\":\n                        [{\"orderSubtotal\":{\"excludedVariantIds\":[]}}]}],\"discountApplicationStrategy\":\"FIRST\"}"
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
  'mutation discountCodeAppCreate($codeAppDiscount: DiscountCodeAppInput!) {
    discountCodeAppCreate(codeAppDiscount: $codeAppDiscount) {
      codeAppDiscount {
        discountId
        title
        appDiscountType {
          description
          functionId
        }
        combinesWith {
          orderDiscounts
          productDiscounts
          shippingDiscounts
        }
        codes(first: 100) {
          nodes {
            code
          }
        }
        status
        usageLimit
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "codeAppDiscount": {
      "code": "APP_DISCOUNT",
      "title": "Take 5$ from order discount",
      "functionId": "dce9760f-6514-4d94-a04b-8ab8614ea6cd",
      "appliesOncePerCustomer": true,
      "combinesWith": {
        "orderDiscounts": true,
        "productDiscounts": true,
        "shippingDiscounts": true
      },
      "startsAt": "2021-02-02T17:09:21Z",
      "endsAt": "2022-02-02T17:09:21Z",
      "usageLimit": 1,
      "metafields": [
        {
          "namespace": "default",
          "key": "function-configuration",
          "type": "json",
          "value": "{\"discounts\":[{\"value\":{\"fixedAmount\":{\"amount\":5}},\"targets\":\n                        [{\"orderSubtotal\":{\"excludedVariantIds\":[]}}]}],\"discountApplicationStrategy\":\"FIRST\"}"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeAppCreate": {
      "codeAppDiscount": {
        "discountId": "gid://shopify/DiscountCodeNode/1057856652",
        "title": "Take 5$ from order discount",
        "appDiscountType": {
          "description": "my function does a thing",
          "functionId": "9ae28a71-1ec6-40a7-a8a2-b6a425f9ddd1"
        },
        "combinesWith": {
          "orderDiscounts": true,
          "productDiscounts": true,
          "shippingDiscounts": true
        },
        "codes": {
          "nodes": [
            {
              "code": "APP_DISCOUNT"
            }
          ]
        },
        "status": "EXPIRED",
        "usageLimit": 1
      },
      "userErrors": []
    }
  }
  ```

* ### discountCodeAppCreate reference
