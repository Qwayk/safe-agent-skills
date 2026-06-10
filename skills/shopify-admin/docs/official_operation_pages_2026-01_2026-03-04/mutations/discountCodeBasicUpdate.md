---
title: discountCodeBasicUpdate - GraphQL Admin
description: >-
  Updates an [amount off
  discount](https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount)
  that's applied on a cart and at checkout when a customer enters a code. Amount
  off discounts can be a percentage off or a fixed amount off.


  > Note:

  > To update discounts that are automatically applied on a cart and at
  checkout, use the
  [`discountAutomaticBasicUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBasicUpdate)
  mutation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBasicUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBasicUpdate.md
---

# discount​Code​Basic​Update

mutation

Requires Apps must have `write_discounts` access scope.

Updates an [amount off discount](https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's applied on a cart and at checkout when a customer enters a code. Amount off discounts can be a percentage off or a fixed amount off.

***

**Note:** To update discounts that are automatically applied on a cart and at checkout, use the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBasicUpdate">\<code>\<span class="PreventFireFoxApplyingGapToWBR">discount\<wbr/>Automatic\<wbr/>Basic\<wbr/>Update\</span>\</code>\</a> mutation.

***

## Arguments

* basic​Code​Discount

  [Discount​Code​Basic​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DiscountCodeBasicInput)

  required

  The input data used to update the discount code.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the discount code to update.

***

## Discount​Code​Basic​Update​Payload returns

* code​Discount​Node

  [Discount​Code​Node](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountCodeNode)

  The discount code that was updated.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update the code, end date, and percentage value of a discount code

  #### Description

  Update an \[amount off discount]\(https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's applied on a cart and at checkout when customers enter a code. This example shows how to modify the discount to apply 40% off, set a new discount code, and set the discount to never expire. The update also limits the discount to one for each customer.

  #### Query

  ```graphql
  mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
    discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
      codeDiscountNode {
        id
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
    "id": "gid://shopify/DiscountCodeNode/206265824",
    "basicCodeDiscount": {
      "endsAt": null,
      "code": "NEW_CODE",
      "appliesOncePerCustomer": true,
      "customerGets": {
        "value": {
          "percentage": 0.4
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
  "query": "mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) { discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) { codeDiscountNode { id } userErrors { field code message } } }",
   "variables": {
      "id": "gid://shopify/DiscountCodeNode/206265824",
      "basicCodeDiscount": {
        "endsAt": null,
        "code": "NEW_CODE",
        "appliesOncePerCustomer": true,
        "customerGets": {
          "value": {
            "percentage": 0.4
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
    mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
      discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
        codeDiscountNode {
          id
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
          "id": "gid://shopify/DiscountCodeNode/206265824",
          "basicCodeDiscount": {
              "endsAt": null,
              "code": "NEW_CODE",
              "appliesOncePerCustomer": true,
              "customerGets": {
                  "value": {
                      "percentage": 0.4
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
    mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
      discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
        codeDiscountNode {
          id
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
    "id": "gid://shopify/DiscountCodeNode/206265824",
    "basicCodeDiscount": {
      "endsAt": null,
      "code": "NEW_CODE",
      "appliesOncePerCustomer": true,
      "customerGets": {
        "value": {
          "percentage": 0.4
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
      "query": `mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
        discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
          codeDiscountNode {
            id
          }
          userErrors {
            field
            code
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DiscountCodeNode/206265824",
          "basicCodeDiscount": {
              "endsAt": null,
              "code": "NEW_CODE",
              "appliesOncePerCustomer": true,
              "customerGets": {
                  "value": {
                      "percentage": 0.4
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
  'mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
    discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
      codeDiscountNode {
        id
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
    "id": "gid://shopify/DiscountCodeNode/206265824",
    "basicCodeDiscount": {
      "endsAt": null,
      "code": "NEW_CODE",
      "appliesOncePerCustomer": true,
      "customerGets": {
        "value": {
          "percentage": 0.4
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeBasicUpdate": {
      "codeDiscountNode": {
        "id": "gid://shopify/DiscountCodeNode/206265824"
      },
      "userErrors": []
    }
  }
  ```

* ### Update the context of a discount code

  #### Description

  Update an \[amount off discount]\(https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's applied on a cart and at checkout when customers enter a code. This example shows how to update the discount's customer eligibility to apply only to a specific customer segment.

  #### Query

  ```graphql
  mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
    discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeBasic {
            context {
              ... on DiscountCustomerSegments {
                segments {
                  id
                }
              }
            }
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
    "id": "gid://shopify/DiscountCodeNode/206265824",
    "basicCodeDiscount": {
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/210588551"
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
  "query": "mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) { discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) { codeDiscountNode { id codeDiscount { ... on DiscountCodeBasic { context { ... on DiscountCustomerSegments { segments { id } } } } } } userErrors { field code message } } }",
   "variables": {
      "id": "gid://shopify/DiscountCodeNode/206265824",
      "basicCodeDiscount": {
        "context": {
          "customerSegments": {
            "add": [
              "gid://shopify/Segment/210588551"
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
    mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
      discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              context {
                ... on DiscountCustomerSegments {
                  segments {
                    id
                  }
                }
              }
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
          "id": "gid://shopify/DiscountCodeNode/206265824",
          "basicCodeDiscount": {
              "context": {
                  "customerSegments": {
                      "add": [
                          "gid://shopify/Segment/210588551"
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
    mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
      discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeBasic {
              context {
                ... on DiscountCustomerSegments {
                  segments {
                    id
                  }
                }
              }
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
    "id": "gid://shopify/DiscountCodeNode/206265824",
    "basicCodeDiscount": {
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/210588551"
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
      "query": `mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
        discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
          codeDiscountNode {
            id
            codeDiscount {
              ... on DiscountCodeBasic {
                context {
                  ... on DiscountCustomerSegments {
                    segments {
                      id
                    }
                  }
                }
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
          "id": "gid://shopify/DiscountCodeNode/206265824",
          "basicCodeDiscount": {
              "context": {
                  "customerSegments": {
                      "add": [
                          "gid://shopify/Segment/210588551"
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
  'mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
    discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeBasic {
            context {
              ... on DiscountCustomerSegments {
                segments {
                  id
                }
              }
            }
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
    "id": "gid://shopify/DiscountCodeNode/206265824",
    "basicCodeDiscount": {
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/210588551"
          ]
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeBasicUpdate": {
      "codeDiscountNode": {
        "id": "gid://shopify/DiscountCodeNode/206265824",
        "codeDiscount": {
          "context": {
            "segments": [
              {
                "id": "gid://shopify/Segment/210588551"
              }
            ]
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Update the variants and percentage value of a discount code

  #### Description

  Update an \[amount off discount]\(https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's applied on a cart and at checkout when customers enter a code. This example shows how to modify the discount to apply only to specific products, take 10% off the selected products, make it available for the first 100 orders, limit it to one use for each customer, and set an end date.

  #### Query

  ```graphql
  mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
    discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
      codeDiscountNode {
        id
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
    "id": "gid://shopify/DiscountCodeNode/139986317",
    "basicCodeDiscount": {
      "endsAt": "2025-12-31T23:59:59Z",
      "usageLimit": 100,
      "appliesOncePerCustomer": true,
      "customerGets": {
        "items": {
          "products": {
            "productsToAdd": [
              "gid://shopify/Product/121709582",
              "gid://shopify/Product/108828309"
            ]
          }
        },
        "value": {
          "percentage": 0.1
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
  "query": "mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) { discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) { codeDiscountNode { id } userErrors { field code message } } }",
   "variables": {
      "id": "gid://shopify/DiscountCodeNode/139986317",
      "basicCodeDiscount": {
        "endsAt": "2025-12-31T23:59:59Z",
        "usageLimit": 100,
        "appliesOncePerCustomer": true,
        "customerGets": {
          "items": {
            "products": {
              "productsToAdd": [
                "gid://shopify/Product/121709582",
                "gid://shopify/Product/108828309"
              ]
            }
          },
          "value": {
            "percentage": 0.1
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
    mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
      discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
        codeDiscountNode {
          id
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
          "id": "gid://shopify/DiscountCodeNode/139986317",
          "basicCodeDiscount": {
              "endsAt": "2025-12-31T23:59:59Z",
              "usageLimit": 100,
              "appliesOncePerCustomer": true,
              "customerGets": {
                  "items": {
                      "products": {
                          "productsToAdd": [
                              "gid://shopify/Product/121709582",
                              "gid://shopify/Product/108828309"
                          ]
                      }
                  },
                  "value": {
                      "percentage": 0.1
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
    mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
      discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
        codeDiscountNode {
          id
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
    "id": "gid://shopify/DiscountCodeNode/139986317",
    "basicCodeDiscount": {
      "endsAt": "2025-12-31T23:59:59Z",
      "usageLimit": 100,
      "appliesOncePerCustomer": true,
      "customerGets": {
        "items": {
          "products": {
            "productsToAdd": [
              "gid://shopify/Product/121709582",
              "gid://shopify/Product/108828309"
            ]
          }
        },
        "value": {
          "percentage": 0.1
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
      "query": `mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
        discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
          codeDiscountNode {
            id
          }
          userErrors {
            field
            code
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DiscountCodeNode/139986317",
          "basicCodeDiscount": {
              "endsAt": "2025-12-31T23:59:59Z",
              "usageLimit": 100,
              "appliesOncePerCustomer": true,
              "customerGets": {
                  "items": {
                      "products": {
                          "productsToAdd": [
                              "gid://shopify/Product/121709582",
                              "gid://shopify/Product/108828309"
                          ]
                      }
                  },
                  "value": {
                      "percentage": 0.1
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
  'mutation discountCodeBasicUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
    discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
      codeDiscountNode {
        id
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
    "id": "gid://shopify/DiscountCodeNode/139986317",
    "basicCodeDiscount": {
      "endsAt": "2025-12-31T23:59:59Z",
      "usageLimit": 100,
      "appliesOncePerCustomer": true,
      "customerGets": {
        "items": {
          "products": {
            "productsToAdd": [
              "gid://shopify/Product/121709582",
              "gid://shopify/Product/108828309"
            ]
          }
        },
        "value": {
          "percentage": 0.1
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeBasicUpdate": {
      "codeDiscountNode": {
        "id": "gid://shopify/DiscountCodeNode/139986317"
      },
      "userErrors": []
    }
  }
  ```

* ### discountCodeBasicUpdate reference
