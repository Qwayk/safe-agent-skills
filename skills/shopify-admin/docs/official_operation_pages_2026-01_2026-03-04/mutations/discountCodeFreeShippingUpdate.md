---
title: discountCodeFreeShippingUpdate - GraphQL Admin
description: >-
  Updates a [free shipping
  discount](https://help.shopify.com/manual/discounts/discount-types/free-shipping)
  that's applied on a cart and at checkout when a customer enters a code.


  > Note:

  > To update a free shipping discount that's automatically applied on a cart
  and at checkout, use the
  [`discountAutomaticFreeShippingUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticFreeShippingUpdate)
  mutation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeFreeShippingUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeFreeShippingUpdate.md
---

# discount​Code​Free​Shipping​Update

mutation

Requires Apps must have `write_discounts` access scope.

Updates a [free shipping discount](https://help.shopify.com/manual/discounts/discount-types/free-shipping) that's applied on a cart and at checkout when a customer enters a code.

***

**Note:** To update a free shipping discount that\&#39;s automatically applied on a cart and at checkout, use the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticFreeShippingUpdate">\<code>\<span class="PreventFireFoxApplyingGapToWBR">discount\<wbr/>Automatic\<wbr/>Free\<wbr/>Shipping\<wbr/>Update\</span>\</code>\</a> mutation.

***

## Arguments

* free​Shipping​Code​Discount

  [Discount​Code​Free​Shipping​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DiscountCodeFreeShippingInput)

  required

  The input data used to update the discount code.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the discount code to update.

***

## Discount​Code​Free​Shipping​Update​Payload returns

* code​Discount​Node

  [Discount​Code​Node](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountCodeNode)

  The discount code that was updated.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update a free shipping discount code

  #### Description

  Update a \[free shipping discount]\(https://help.shopify.com/manual/discounts/discount-types/free-shipping) that's applied when customers enter a code. This example shows how to update the minimum subtotal requirement to 25 USD, make it valid for the first week of August, and update the discount's code.

  #### Query

  ```graphql
  mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!) {
    discountCodeFreeShippingUpdate(freeShippingCodeDiscount: $freeShippingCodeDiscount, id: $id) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeFreeShipping {
            title
            startsAt
            endsAt
            minimumRequirement {
              ... on DiscountMinimumSubtotal {
                greaterThanOrEqualToSubtotal {
                  amount
                  currencyCode
                }
              }
            }
            codes(first: 2) {
              nodes {
                code
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
    "freeShippingCodeDiscount": {
      "code": "FRSHP25",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": 25
        }
      },
      "startsAt": "2022-08-01",
      "endsAt": "2022-08-08",
      "title": "Free shipping for orders above $25"
    },
    "id": "gid://shopify/DiscountCodeFreeShipping/445378512"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!) { discountCodeFreeShippingUpdate(freeShippingCodeDiscount: $freeShippingCodeDiscount, id: $id) { codeDiscountNode { id codeDiscount { ... on DiscountCodeFreeShipping { title startsAt endsAt minimumRequirement { ... on DiscountMinimumSubtotal { greaterThanOrEqualToSubtotal { amount currencyCode } } } codes(first: 2) { nodes { code } } } } } userErrors { field code message } } }",
   "variables": {
      "freeShippingCodeDiscount": {
        "code": "FRSHP25",
        "minimumRequirement": {
          "subtotal": {
            "greaterThanOrEqualToSubtotal": 25
          }
        },
        "startsAt": "2022-08-01",
        "endsAt": "2022-08-08",
        "title": "Free shipping for orders above $25"
      },
      "id": "gid://shopify/DiscountCodeFreeShipping/445378512"
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
    mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!) {
      discountCodeFreeShippingUpdate(freeShippingCodeDiscount: $freeShippingCodeDiscount, id: $id) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeFreeShipping {
              title
              startsAt
              endsAt
              minimumRequirement {
                ... on DiscountMinimumSubtotal {
                  greaterThanOrEqualToSubtotal {
                    amount
                    currencyCode
                  }
                }
              }
              codes(first: 2) {
                nodes {
                  code
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
          "freeShippingCodeDiscount": {
              "code": "FRSHP25",
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": 25
                  }
              },
              "startsAt": "2022-08-01",
              "endsAt": "2022-08-08",
              "title": "Free shipping for orders above $25"
          },
          "id": "gid://shopify/DiscountCodeFreeShipping/445378512"
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
    mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!) {
      discountCodeFreeShippingUpdate(freeShippingCodeDiscount: $freeShippingCodeDiscount, id: $id) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeFreeShipping {
              title
              startsAt
              endsAt
              minimumRequirement {
                ... on DiscountMinimumSubtotal {
                  greaterThanOrEqualToSubtotal {
                    amount
                    currencyCode
                  }
                }
              }
              codes(first: 2) {
                nodes {
                  code
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
    "freeShippingCodeDiscount": {
      "code": "FRSHP25",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": 25
        }
      },
      "startsAt": "2022-08-01",
      "endsAt": "2022-08-08",
      "title": "Free shipping for orders above $25"
    },
    "id": "gid://shopify/DiscountCodeFreeShipping/445378512"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!) {
        discountCodeFreeShippingUpdate(freeShippingCodeDiscount: $freeShippingCodeDiscount, id: $id) {
          codeDiscountNode {
            id
            codeDiscount {
              ... on DiscountCodeFreeShipping {
                title
                startsAt
                endsAt
                minimumRequirement {
                  ... on DiscountMinimumSubtotal {
                    greaterThanOrEqualToSubtotal {
                      amount
                      currencyCode
                    }
                  }
                }
                codes(first: 2) {
                  nodes {
                    code
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
          "freeShippingCodeDiscount": {
              "code": "FRSHP25",
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": 25
                  }
              },
              "startsAt": "2022-08-01",
              "endsAt": "2022-08-08",
              "title": "Free shipping for orders above $25"
          },
          "id": "gid://shopify/DiscountCodeFreeShipping/445378512"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!) {
    discountCodeFreeShippingUpdate(freeShippingCodeDiscount: $freeShippingCodeDiscount, id: $id) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeFreeShipping {
            title
            startsAt
            endsAt
            minimumRequirement {
              ... on DiscountMinimumSubtotal {
                greaterThanOrEqualToSubtotal {
                  amount
                  currencyCode
                }
              }
            }
            codes(first: 2) {
              nodes {
                code
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
    "freeShippingCodeDiscount": {
      "code": "FRSHP25",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": 25
        }
      },
      "startsAt": "2022-08-01",
      "endsAt": "2022-08-08",
      "title": "Free shipping for orders above $25"
    },
    "id": "gid://shopify/DiscountCodeFreeShipping/445378512"
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeFreeShippingUpdate": {
      "codeDiscountNode": {
        "id": "gid://shopify/DiscountCodeNode/445378512",
        "codeDiscount": {
          "title": "Free shipping for orders above $25",
          "startsAt": "2022-08-01T00:00:00Z",
          "endsAt": "2022-08-08T00:00:00Z",
          "minimumRequirement": {
            "greaterThanOrEqualToSubtotal": {
              "amount": "25.0",
              "currencyCode": "USD"
            }
          },
          "codes": {
            "nodes": [
              {
                "code": "FRSHP25"
              }
            ]
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Update the context of a free shipping discount code

  #### Description

  Update a \[free shipping discount]\(https://help.shopify.com/manual/discounts/discount-types/free-shipping) that's applied when customers enter a code. This example shows how to update the context and code for a free shipping discount.

  #### Query

  ```graphql
  mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!) {
    discountCodeFreeShippingUpdate(freeShippingCodeDiscount: $freeShippingCodeDiscount, id: $id) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeFreeShipping {
            title
            startsAt
            endsAt
            context {
              ... on DiscountCustomerSegments {
                segments {
                  id
                }
              }
            }
            codes(first: 2) {
              nodes {
                code
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
    "freeShippingCodeDiscount": {
      "code": "FRSHP25",
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/210588551"
          ]
        }
      },
      "startsAt": "2025-07-24T16:18:22-04:00",
      "endsAt": "2025-07-29T16:18:22-04:00"
    },
    "id": "gid://shopify/DiscountCodeFreeShipping/445378512"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!) { discountCodeFreeShippingUpdate(freeShippingCodeDiscount: $freeShippingCodeDiscount, id: $id) { codeDiscountNode { id codeDiscount { ... on DiscountCodeFreeShipping { title startsAt endsAt context { ... on DiscountCustomerSegments { segments { id } } } codes(first: 2) { nodes { code } } } } } userErrors { field code message } } }",
   "variables": {
      "freeShippingCodeDiscount": {
        "code": "FRSHP25",
        "context": {
          "customerSegments": {
            "add": [
              "gid://shopify/Segment/210588551"
            ]
          }
        },
        "startsAt": "2025-07-24T16:18:22-04:00",
        "endsAt": "2025-07-29T16:18:22-04:00"
      },
      "id": "gid://shopify/DiscountCodeFreeShipping/445378512"
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
    mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!) {
      discountCodeFreeShippingUpdate(freeShippingCodeDiscount: $freeShippingCodeDiscount, id: $id) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeFreeShipping {
              title
              startsAt
              endsAt
              context {
                ... on DiscountCustomerSegments {
                  segments {
                    id
                  }
                }
              }
              codes(first: 2) {
                nodes {
                  code
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
          "freeShippingCodeDiscount": {
              "code": "FRSHP25",
              "context": {
                  "customerSegments": {
                      "add": [
                          "gid://shopify/Segment/210588551"
                      ]
                  }
              },
              "startsAt": "2025-07-24T16:18:22-04:00",
              "endsAt": "2025-07-29T16:18:22-04:00"
          },
          "id": "gid://shopify/DiscountCodeFreeShipping/445378512"
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
    mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!) {
      discountCodeFreeShippingUpdate(freeShippingCodeDiscount: $freeShippingCodeDiscount, id: $id) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeFreeShipping {
              title
              startsAt
              endsAt
              context {
                ... on DiscountCustomerSegments {
                  segments {
                    id
                  }
                }
              }
              codes(first: 2) {
                nodes {
                  code
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
    "freeShippingCodeDiscount": {
      "code": "FRSHP25",
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/210588551"
          ]
        }
      },
      "startsAt": "2025-07-24T16:18:22-04:00",
      "endsAt": "2025-07-29T16:18:22-04:00"
    },
    "id": "gid://shopify/DiscountCodeFreeShipping/445378512"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!) {
        discountCodeFreeShippingUpdate(freeShippingCodeDiscount: $freeShippingCodeDiscount, id: $id) {
          codeDiscountNode {
            id
            codeDiscount {
              ... on DiscountCodeFreeShipping {
                title
                startsAt
                endsAt
                context {
                  ... on DiscountCustomerSegments {
                    segments {
                      id
                    }
                  }
                }
                codes(first: 2) {
                  nodes {
                    code
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
          "freeShippingCodeDiscount": {
              "code": "FRSHP25",
              "context": {
                  "customerSegments": {
                      "add": [
                          "gid://shopify/Segment/210588551"
                      ]
                  }
              },
              "startsAt": "2025-07-24T16:18:22-04:00",
              "endsAt": "2025-07-29T16:18:22-04:00"
          },
          "id": "gid://shopify/DiscountCodeFreeShipping/445378512"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountCodeFreeShippingUpdate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!, $id: ID!) {
    discountCodeFreeShippingUpdate(freeShippingCodeDiscount: $freeShippingCodeDiscount, id: $id) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeFreeShipping {
            title
            startsAt
            endsAt
            context {
              ... on DiscountCustomerSegments {
                segments {
                  id
                }
              }
            }
            codes(first: 2) {
              nodes {
                code
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
    "freeShippingCodeDiscount": {
      "code": "FRSHP25",
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/210588551"
          ]
        }
      },
      "startsAt": "2025-07-24T16:18:22-04:00",
      "endsAt": "2025-07-29T16:18:22-04:00"
    },
    "id": "gid://shopify/DiscountCodeFreeShipping/445378512"
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeFreeShippingUpdate": {
      "codeDiscountNode": {
        "id": "gid://shopify/DiscountCodeNode/445378512",
        "codeDiscount": {
          "title": "LMAOFREESHIPPING",
          "startsAt": "2025-07-24T20:18:22Z",
          "endsAt": "2025-07-29T20:18:22Z",
          "context": {
            "segments": [
              {
                "id": "gid://shopify/Segment/210588551"
              }
            ]
          },
          "codes": {
            "nodes": [
              {
                "code": "FRSHP25"
              }
            ]
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### discountCodeFreeShippingUpdate reference
