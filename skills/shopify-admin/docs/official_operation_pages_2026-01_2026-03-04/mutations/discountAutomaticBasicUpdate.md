---
title: discountAutomaticBasicUpdate - GraphQL Admin
description: >-
  Updates an existing

  [amount off
  discount](https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount)

  that's automatically applied on a cart and at checkout.


  > Note:

  > To update code discounts, use the

  [`discountCodeBasicUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBasicUpdate)

  mutation instead.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBasicUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticBasicUpdate.md
---

# discount​Automatic​Basic​Update

mutation

Requires Apps must have `write_discounts` access scope.

Updates an existing [amount off discount](https://help.shopify.com/manual/discounts/discount-types/percentage-fixed-amount) that's automatically applied on a cart and at checkout.

***

**Note:** To update code discounts, use the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBasicUpdate">\<code>\<span class="PreventFireFoxApplyingGapToWBR">discount\<wbr/>Code\<wbr/>Basic\<wbr/>Update\</span>\</code>\</a> mutation instead.

***

## Arguments

* automatic​Basic​Discount

  [Discount​Automatic​Basic​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DiscountAutomaticBasicInput)

  required

  The input data used to update the automatic amount off discount.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the automatic amount off discount to update.

***

## Discount​Automatic​Basic​Update​Payload returns

* automatic​Discount​Node

  [Discount​Automatic​Node](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomaticNode)

  The automatic discount that was updated.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update an automatic basic discount

  #### Description

  Modify an existing automatic discount's percentage discount and make it apply only on a specific collection.

  #### Query

  ```graphql
  mutation discountAutomaticBasicUpdate($id: ID!, $automaticBasicDiscount: DiscountAutomaticBasicInput!) {
    discountAutomaticBasicUpdate(id: $id, automaticBasicDiscount: $automaticBasicDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticBasic {
            customerGets {
              value {
                ... on DiscountPercentage {
                  percentage
                }
              }
              items {
                ... on DiscountCollections {
                  collections(first: 5) {
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
    "id": "gid://shopify/DiscountAutomaticNode/299501151",
    "automaticBasicDiscount": {
      "customerGets": {
        "value": {
          "percentage": 0.5
        },
        "items": {
          "collections": {
            "add": [
              "gid://shopify/Collection/142458073"
            ]
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
  "query": "mutation discountAutomaticBasicUpdate($id: ID!, $automaticBasicDiscount: DiscountAutomaticBasicInput!) { discountAutomaticBasicUpdate(id: $id, automaticBasicDiscount: $automaticBasicDiscount) { automaticDiscountNode { id automaticDiscount { ... on DiscountAutomaticBasic { customerGets { value { ... on DiscountPercentage { percentage } } items { ... on DiscountCollections { collections(first: 5) { nodes { id } } } } } } } } userErrors { field code message } } }",
   "variables": {
      "id": "gid://shopify/DiscountAutomaticNode/299501151",
      "automaticBasicDiscount": {
        "customerGets": {
          "value": {
            "percentage": 0.5
          },
          "items": {
            "collections": {
              "add": [
                "gid://shopify/Collection/142458073"
              ]
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
    mutation discountAutomaticBasicUpdate($id: ID!, $automaticBasicDiscount: DiscountAutomaticBasicInput!) {
      discountAutomaticBasicUpdate(id: $id, automaticBasicDiscount: $automaticBasicDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
              customerGets {
                value {
                  ... on DiscountPercentage {
                    percentage
                  }
                }
                items {
                  ... on DiscountCollections {
                    collections(first: 5) {
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
          "id": "gid://shopify/DiscountAutomaticNode/299501151",
          "automaticBasicDiscount": {
              "customerGets": {
                  "value": {
                      "percentage": 0.5
                  },
                  "items": {
                      "collections": {
                          "add": [
                              "gid://shopify/Collection/142458073"
                          ]
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
    mutation discountAutomaticBasicUpdate($id: ID!, $automaticBasicDiscount: DiscountAutomaticBasicInput!) {
      discountAutomaticBasicUpdate(id: $id, automaticBasicDiscount: $automaticBasicDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
              customerGets {
                value {
                  ... on DiscountPercentage {
                    percentage
                  }
                }
                items {
                  ... on DiscountCollections {
                    collections(first: 5) {
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
    "id": "gid://shopify/DiscountAutomaticNode/299501151",
    "automaticBasicDiscount": {
      "customerGets": {
        "value": {
          "percentage": 0.5
        },
        "items": {
          "collections": {
            "add": [
              "gid://shopify/Collection/142458073"
            ]
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
      "query": `mutation discountAutomaticBasicUpdate($id: ID!, $automaticBasicDiscount: DiscountAutomaticBasicInput!) {
        discountAutomaticBasicUpdate(id: $id, automaticBasicDiscount: $automaticBasicDiscount) {
          automaticDiscountNode {
            id
            automaticDiscount {
              ... on DiscountAutomaticBasic {
                customerGets {
                  value {
                    ... on DiscountPercentage {
                      percentage
                    }
                  }
                  items {
                    ... on DiscountCollections {
                      collections(first: 5) {
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
          "id": "gid://shopify/DiscountAutomaticNode/299501151",
          "automaticBasicDiscount": {
              "customerGets": {
                  "value": {
                      "percentage": 0.5
                  },
                  "items": {
                      "collections": {
                          "add": [
                              "gid://shopify/Collection/142458073"
                          ]
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
  'mutation discountAutomaticBasicUpdate($id: ID!, $automaticBasicDiscount: DiscountAutomaticBasicInput!) {
    discountAutomaticBasicUpdate(id: $id, automaticBasicDiscount: $automaticBasicDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticBasic {
            customerGets {
              value {
                ... on DiscountPercentage {
                  percentage
                }
              }
              items {
                ... on DiscountCollections {
                  collections(first: 5) {
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
    "id": "gid://shopify/DiscountAutomaticNode/299501151",
    "automaticBasicDiscount": {
      "customerGets": {
        "value": {
          "percentage": 0.5
        },
        "items": {
          "collections": {
            "add": [
              "gid://shopify/Collection/142458073"
            ]
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticBasicUpdate": {
      "automaticDiscountNode": {
        "id": "gid://shopify/DiscountAutomaticNode/299501151",
        "automaticDiscount": {
          "customerGets": {
            "value": {
              "percentage": 0.5
            },
            "items": {
              "collections": {
                "nodes": [
                  {
                    "id": "gid://shopify/Collection/142458073"
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

* ### Update context for automatic basic discount for a customer segment

  #### Description

  Modify an existing automatic discount's and make it apply only on a specific customer segment.

  #### Query

  ```graphql
  mutation discountAutomaticBasicUpdate($id: ID!, $automaticBasicDiscount: DiscountAutomaticBasicInput!) {
    discountAutomaticBasicUpdate(id: $id, automaticBasicDiscount: $automaticBasicDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticBasic {
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
    "id": "gid://shopify/DiscountAutomaticNode/299501151",
    "automaticBasicDiscount": {
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
  "query": "mutation discountAutomaticBasicUpdate($id: ID!, $automaticBasicDiscount: DiscountAutomaticBasicInput!) { discountAutomaticBasicUpdate(id: $id, automaticBasicDiscount: $automaticBasicDiscount) { automaticDiscountNode { id automaticDiscount { ... on DiscountAutomaticBasic { context { ... on DiscountCustomerSegments { segments { id } } } } } } userErrors { field code message } } }",
   "variables": {
      "id": "gid://shopify/DiscountAutomaticNode/299501151",
      "automaticBasicDiscount": {
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
    mutation discountAutomaticBasicUpdate($id: ID!, $automaticBasicDiscount: DiscountAutomaticBasicInput!) {
      discountAutomaticBasicUpdate(id: $id, automaticBasicDiscount: $automaticBasicDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
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
          "id": "gid://shopify/DiscountAutomaticNode/299501151",
          "automaticBasicDiscount": {
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
    mutation discountAutomaticBasicUpdate($id: ID!, $automaticBasicDiscount: DiscountAutomaticBasicInput!) {
      discountAutomaticBasicUpdate(id: $id, automaticBasicDiscount: $automaticBasicDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticBasic {
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
    "id": "gid://shopify/DiscountAutomaticNode/299501151",
    "automaticBasicDiscount": {
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
      "query": `mutation discountAutomaticBasicUpdate($id: ID!, $automaticBasicDiscount: DiscountAutomaticBasicInput!) {
        discountAutomaticBasicUpdate(id: $id, automaticBasicDiscount: $automaticBasicDiscount) {
          automaticDiscountNode {
            id
            automaticDiscount {
              ... on DiscountAutomaticBasic {
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
          "id": "gid://shopify/DiscountAutomaticNode/299501151",
          "automaticBasicDiscount": {
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
  'mutation discountAutomaticBasicUpdate($id: ID!, $automaticBasicDiscount: DiscountAutomaticBasicInput!) {
    discountAutomaticBasicUpdate(id: $id, automaticBasicDiscount: $automaticBasicDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticBasic {
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
    "id": "gid://shopify/DiscountAutomaticNode/299501151",
    "automaticBasicDiscount": {
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
    "discountAutomaticBasicUpdate": {
      "automaticDiscountNode": {
        "id": "gid://shopify/DiscountAutomaticNode/299501151",
        "automaticDiscount": {
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

* ### discountAutomaticBasicUpdate reference
