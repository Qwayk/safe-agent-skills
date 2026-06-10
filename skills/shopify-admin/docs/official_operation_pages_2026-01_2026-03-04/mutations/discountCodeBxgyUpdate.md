---
title: discountCodeBxgyUpdate - GraphQL Admin
description: >-
  Updates a

  [buy X get Y discount
  (BXGY)](https://help.shopify.com/manual/discounts/discount-types/buy-x-get-y)

  that's applied on a cart and at checkout when a customer enters a code.


  > Note:

  > To update discounts that are automatically applied on a cart and at
  checkout, use the

  [`discountAutomaticBxgyUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBxgyUpdate)

  mutation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBxgyUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBxgyUpdate.md
---

# discount​Code​Bxgy​Update

mutation

Requires Apps must have `write_discounts` access scope.

Updates a [buy X get Y discount (BXGY)](https://help.shopify.com/manual/discounts/discount-types/buy-x-get-y) that's applied on a cart and at checkout when a customer enters a code.

***

**Note:** To update discounts that are automatically applied on a cart and at checkout, use the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBxgyUpdate">\<code>\<span class="PreventFireFoxApplyingGapToWBR">discount\<wbr/>Automatic\<wbr/>Bxgy\<wbr/>Update\</span>\</code>\</a> mutation.

***

## Arguments

* bxgy​Code​Discount

  [Discount​Code​Bxgy​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DiscountCodeBxgyInput)

  required

  The input data used to update the BXGY code discount.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the BXGY code discount to update.

***

## Discount​Code​Bxgy​Update​Payload returns

* code​Discount​Node

  [Discount​Code​Node](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountCodeNode)

  The code discount that was updated.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update the context for a BXGY discount code

  #### Description

  Update a \[BXGY discount]\(https://help.shopify.com/manual/discounts/discount-types/buy-x-get-y) that's applied when customers enter a code. This example shows how to update the discount so it applies to a specific customer segment.

  #### Query

  ```graphql
  mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
    discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeBxgy {
            title
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
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/DiscountCodeNode/732991387",
    "bxgyCodeDiscount": {
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
  "query": "mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) { discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) { codeDiscountNode { id codeDiscount { ... on DiscountCodeBxgy { title context { ... on DiscountCustomerSegments { segments { id } } } } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DiscountCodeNode/732991387",
      "bxgyCodeDiscount": {
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
    mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
      discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeBxgy {
              title
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
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DiscountCodeNode/732991387",
          "bxgyCodeDiscount": {
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
    mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
      discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeBxgy {
              title
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
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DiscountCodeNode/732991387",
    "bxgyCodeDiscount": {
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
      "query": `mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
        discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
          codeDiscountNode {
            id
            codeDiscount {
              ... on DiscountCodeBxgy {
                title
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
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DiscountCodeNode/732991387",
          "bxgyCodeDiscount": {
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
  'mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
    discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeBxgy {
            title
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
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DiscountCodeNode/732991387",
    "bxgyCodeDiscount": {
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
    "discountCodeBxgyUpdate": {
      "codeDiscountNode": {
        "id": "gid://shopify/DiscountCodeNode/732991387",
        "codeDiscount": {
          "title": "simple_bogo",
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

* ### Update the end date of a BXGY discount code

  #### Description

  Update a \[BXGY discount]\(https://help.shopify.com/manual/discounts/discount-types/buy-x-get-y) that's applied when customers enter a code. This example shows how to update the discount's expiration date.

  #### Query

  ```graphql
  mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
    discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
      codeDiscountNode {
        codeDiscount {
          ... on DiscountCodeBxgy {
            title
            codes(first: 10) {
              nodes {
                code
              }
            }
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
    "id": "gid://shopify/DiscountCodeNode/732991387",
    "bxgyCodeDiscount": {
      "endsAt": "2022-12-25T00:00:00Z"
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
  "query": "mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) { discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) { codeDiscountNode { codeDiscount { ... on DiscountCodeBxgy { title codes(first: 10) { nodes { code } } endsAt } } } userErrors { field code message } } }",
   "variables": {
      "id": "gid://shopify/DiscountCodeNode/732991387",
      "bxgyCodeDiscount": {
        "endsAt": "2022-12-25T00:00:00Z"
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
    mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
      discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
        codeDiscountNode {
          codeDiscount {
            ... on DiscountCodeBxgy {
              title
              codes(first: 10) {
                nodes {
                  code
                }
              }
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
          "id": "gid://shopify/DiscountCodeNode/732991387",
          "bxgyCodeDiscount": {
              "endsAt": "2022-12-25T00:00:00Z"
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
    mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
      discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
        codeDiscountNode {
          codeDiscount {
            ... on DiscountCodeBxgy {
              title
              codes(first: 10) {
                nodes {
                  code
                }
              }
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
    "id": "gid://shopify/DiscountCodeNode/732991387",
    "bxgyCodeDiscount": {
      "endsAt": "2022-12-25T00:00:00Z"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
        discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
          codeDiscountNode {
            codeDiscount {
              ... on DiscountCodeBxgy {
                title
                codes(first: 10) {
                  nodes {
                    code
                  }
                }
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
          "id": "gid://shopify/DiscountCodeNode/732991387",
          "bxgyCodeDiscount": {
              "endsAt": "2022-12-25T00:00:00Z"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
    discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
      codeDiscountNode {
        codeDiscount {
          ... on DiscountCodeBxgy {
            title
            codes(first: 10) {
              nodes {
                code
              }
            }
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
    "id": "gid://shopify/DiscountCodeNode/732991387",
    "bxgyCodeDiscount": {
      "endsAt": "2022-12-25T00:00:00Z"
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeBxgyUpdate": {
      "codeDiscountNode": {
        "codeDiscount": {
          "title": "simple_bogo",
          "codes": {
            "nodes": [
              {
                "code": "BOGO"
              }
            ]
          },
          "endsAt": "2022-12-25T00:00:00Z"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Update the variants, quantities, and percentage off of a BXGY discount code

  #### Description

  Update a \[BXGY discount]\(https://help.shopify.com/manual/discounts/discount-types/buy-x-get-y) that's applied when customers enter a code. This example shows how to add a new product variant, set the required quantity to two, and set the percentage to 50%.

  #### Query

  ```graphql
  mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
    discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
      codeDiscountNode {
        codeDiscount {
          ... on DiscountCodeBxgy {
            title
            codes(first: 10) {
              nodes {
                code
              }
            }
            customerBuys {
              value {
                ... on DiscountQuantity {
                  quantity
                }
              }
              items {
                ... on DiscountProducts {
                  productVariants(first: 5) {
                    nodes {
                      id
                    }
                  }
                }
              }
            }
            customerGets {
              value {
                ... on DiscountOnQuantity {
                  effect {
                    ... on DiscountPercentage {
                      percentage
                    }
                  }
                }
              }
              items {
                ... on DiscountProducts {
                  products(first: 5) {
                    nodes {
                      id
                    }
                  }
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
    "id": "gid://shopify/DiscountCodeNode/101551934",
    "bxgyCodeDiscount": {
      "customerBuys": {
        "items": {
          "products": {
            "productVariantsToAdd": [
              "gid://shopify/ProductVariant/138327650"
            ]
          }
        },
        "value": {
          "quantity": "2"
        }
      },
      "customerGets": {
        "items": {
          "products": {
            "productsToAdd": [
              "gid://shopify/Product/121709582"
            ]
          }
        },
        "value": {
          "discountOnQuantity": {
            "effect": {
              "percentage": 0.5
            }
          }
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
  "query": "mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) { discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) { codeDiscountNode { codeDiscount { ... on DiscountCodeBxgy { title codes(first: 10) { nodes { code } } customerBuys { value { ... on DiscountQuantity { quantity } } items { ... on DiscountProducts { productVariants(first: 5) { nodes { id } } } } } customerGets { value { ... on DiscountOnQuantity { effect { ... on DiscountPercentage { percentage } } } } items { ... on DiscountProducts { products(first: 5) { nodes { id } } } } } } } } userErrors { field code message } } }",
   "variables": {
      "id": "gid://shopify/DiscountCodeNode/101551934",
      "bxgyCodeDiscount": {
        "customerBuys": {
          "items": {
            "products": {
              "productVariantsToAdd": [
                "gid://shopify/ProductVariant/138327650"
              ]
            }
          },
          "value": {
            "quantity": "2"
          }
        },
        "customerGets": {
          "items": {
            "products": {
              "productsToAdd": [
                "gid://shopify/Product/121709582"
              ]
            }
          },
          "value": {
            "discountOnQuantity": {
              "effect": {
                "percentage": 0.5
              }
            }
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
    mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
      discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
        codeDiscountNode {
          codeDiscount {
            ... on DiscountCodeBxgy {
              title
              codes(first: 10) {
                nodes {
                  code
                }
              }
              customerBuys {
                value {
                  ... on DiscountQuantity {
                    quantity
                  }
                }
                items {
                  ... on DiscountProducts {
                    productVariants(first: 5) {
                      nodes {
                        id
                      }
                    }
                  }
                }
              }
              customerGets {
                value {
                  ... on DiscountOnQuantity {
                    effect {
                      ... on DiscountPercentage {
                        percentage
                      }
                    }
                  }
                }
                items {
                  ... on DiscountProducts {
                    products(first: 5) {
                      nodes {
                        id
                      }
                    }
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
          "id": "gid://shopify/DiscountCodeNode/101551934",
          "bxgyCodeDiscount": {
              "customerBuys": {
                  "items": {
                      "products": {
                          "productVariantsToAdd": [
                              "gid://shopify/ProductVariant/138327650"
                          ]
                      }
                  },
                  "value": {
                      "quantity": "2"
                  }
              },
              "customerGets": {
                  "items": {
                      "products": {
                          "productsToAdd": [
                              "gid://shopify/Product/121709582"
                          ]
                      }
                  },
                  "value": {
                      "discountOnQuantity": {
                          "effect": {
                              "percentage": 0.5
                          }
                      }
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
    mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
      discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
        codeDiscountNode {
          codeDiscount {
            ... on DiscountCodeBxgy {
              title
              codes(first: 10) {
                nodes {
                  code
                }
              }
              customerBuys {
                value {
                  ... on DiscountQuantity {
                    quantity
                  }
                }
                items {
                  ... on DiscountProducts {
                    productVariants(first: 5) {
                      nodes {
                        id
                      }
                    }
                  }
                }
              }
              customerGets {
                value {
                  ... on DiscountOnQuantity {
                    effect {
                      ... on DiscountPercentage {
                        percentage
                      }
                    }
                  }
                }
                items {
                  ... on DiscountProducts {
                    products(first: 5) {
                      nodes {
                        id
                      }
                    }
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
    "id": "gid://shopify/DiscountCodeNode/101551934",
    "bxgyCodeDiscount": {
      "customerBuys": {
        "items": {
          "products": {
            "productVariantsToAdd": [
              "gid://shopify/ProductVariant/138327650"
            ]
          }
        },
        "value": {
          "quantity": "2"
        }
      },
      "customerGets": {
        "items": {
          "products": {
            "productsToAdd": [
              "gid://shopify/Product/121709582"
            ]
          }
        },
        "value": {
          "discountOnQuantity": {
            "effect": {
              "percentage": 0.5
            }
          }
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
      "query": `mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
        discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
          codeDiscountNode {
            codeDiscount {
              ... on DiscountCodeBxgy {
                title
                codes(first: 10) {
                  nodes {
                    code
                  }
                }
                customerBuys {
                  value {
                    ... on DiscountQuantity {
                      quantity
                    }
                  }
                  items {
                    ... on DiscountProducts {
                      productVariants(first: 5) {
                        nodes {
                          id
                        }
                      }
                    }
                  }
                }
                customerGets {
                  value {
                    ... on DiscountOnQuantity {
                      effect {
                        ... on DiscountPercentage {
                          percentage
                        }
                      }
                    }
                  }
                  items {
                    ... on DiscountProducts {
                      products(first: 5) {
                        nodes {
                          id
                        }
                      }
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
          "id": "gid://shopify/DiscountCodeNode/101551934",
          "bxgyCodeDiscount": {
              "customerBuys": {
                  "items": {
                      "products": {
                          "productVariantsToAdd": [
                              "gid://shopify/ProductVariant/138327650"
                          ]
                      }
                  },
                  "value": {
                      "quantity": "2"
                  }
              },
              "customerGets": {
                  "items": {
                      "products": {
                          "productsToAdd": [
                              "gid://shopify/Product/121709582"
                          ]
                      }
                  },
                  "value": {
                      "discountOnQuantity": {
                          "effect": {
                              "percentage": 0.5
                          }
                      }
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
  'mutation discountCodeBxgyUpdate($id: ID!, $bxgyCodeDiscount: DiscountCodeBxgyInput!) {
    discountCodeBxgyUpdate(id: $id, bxgyCodeDiscount: $bxgyCodeDiscount) {
      codeDiscountNode {
        codeDiscount {
          ... on DiscountCodeBxgy {
            title
            codes(first: 10) {
              nodes {
                code
              }
            }
            customerBuys {
              value {
                ... on DiscountQuantity {
                  quantity
                }
              }
              items {
                ... on DiscountProducts {
                  productVariants(first: 5) {
                    nodes {
                      id
                    }
                  }
                }
              }
            }
            customerGets {
              value {
                ... on DiscountOnQuantity {
                  effect {
                    ... on DiscountPercentage {
                      percentage
                    }
                  }
                }
              }
              items {
                ... on DiscountProducts {
                  products(first: 5) {
                    nodes {
                      id
                    }
                  }
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
    "id": "gid://shopify/DiscountCodeNode/101551934",
    "bxgyCodeDiscount": {
      "customerBuys": {
        "items": {
          "products": {
            "productVariantsToAdd": [
              "gid://shopify/ProductVariant/138327650"
            ]
          }
        },
        "value": {
          "quantity": "2"
        }
      },
      "customerGets": {
        "items": {
          "products": {
            "productsToAdd": [
              "gid://shopify/Product/121709582"
            ]
          }
        },
        "value": {
          "discountOnQuantity": {
            "effect": {
              "percentage": 0.5
            }
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeBxgyUpdate": {
      "codeDiscountNode": {
        "codeDiscount": {
          "title": "simple_bxgy",
          "codes": {
            "nodes": [
              {
                "code": "BXGY"
              }
            ]
          },
          "customerBuys": {
            "value": {
              "quantity": "2"
            },
            "items": {
              "productVariants": {
                "nodes": [
                  {
                    "id": "gid://shopify/ProductVariant/30322695"
                  },
                  {
                    "id": "gid://shopify/ProductVariant/138327650"
                  }
                ]
              }
            }
          },
          "customerGets": {
            "value": {
              "effect": {
                "percentage": 0.5
              }
            },
            "items": {
              "products": {
                "nodes": [
                  {
                    "id": "gid://shopify/Product/121709582"
                  }
                ]
              }
            }
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### discountCodeBxgyUpdate reference
