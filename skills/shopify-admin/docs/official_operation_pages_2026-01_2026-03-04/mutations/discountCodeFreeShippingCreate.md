---
title: discountCodeFreeShippingCreate - GraphQL Admin
description: >-
  Creates an [free shipping
  discount](https://help.shopify.com/manual/discounts/discount-types/free-shipping)
  that's applied on a cart and at checkout when a customer enters a code.


  > Note:

  > To create discounts that are automatically applied on a cart and at
  checkout, use the
  [`discountAutomaticFreeShippingCreate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticFreeShippingCreate)
  mutation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeFreeShippingCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeFreeShippingCreate.md
---

# discount​Code​Free​Shipping​Create

mutation

Requires Apps must have `write_discounts` access scope.

Creates an [free shipping discount](https://help.shopify.com/manual/discounts/discount-types/free-shipping) that's applied on a cart and at checkout when a customer enters a code.

***

**Note:** To create discounts that are automatically applied on a cart and at checkout, use the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticFreeShippingCreate">\<code>\<span class="PreventFireFoxApplyingGapToWBR">discount\<wbr/>Automatic\<wbr/>Free\<wbr/>Shipping\<wbr/>Create\</span>\</code>\</a> mutation.

***

## Arguments

* free​Shipping​Code​Discount

  [Discount​Code​Free​Shipping​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DiscountCodeFreeShippingInput)

  required

  The input data used to create the discount code.

***

## Discount​Code​Free​Shipping​Create​Payload returns

* code​Discount​Node

  [Discount​Code​Node](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountCodeNode)

  The discount code that was created.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a free shipping discount code

  #### Description

  Create a \[free shipping discount]\(https://help.shopify.com/manual/discounts/discount-types/free-shipping) that's applied when customers enter a code. This example shows how to create a discount code that offers free shipping on orders over $20.

  #### Query

  ```graphql
  mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) {
    discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeFreeShipping {
            title
            startsAt
            endsAt
            maximumShippingPrice {
              amount
            }
            customerSelection {
              ... on DiscountCustomerAll {
                allCustomers
              }
            }
            destinationSelection {
              ... on DiscountCountryAll {
                allCountries
              }
            }
            minimumRequirement {
              ... on DiscountMinimumSubtotal {
                greaterThanOrEqualToSubtotal {
                  amount
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
      "startsAt": "2022-06-22T21:12:07.000Z",
      "appliesOncePerCustomer": false,
      "title": "FreeShipping",
      "code": "FreeShipping",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": 20
        }
      },
      "customerSelection": {
        "all": true
      },
      "destination": {
        "all": true
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
  "query": "mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) { discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) { codeDiscountNode { id codeDiscount { ... on DiscountCodeFreeShipping { title startsAt endsAt maximumShippingPrice { amount } customerSelection { ... on DiscountCustomerAll { allCustomers } } destinationSelection { ... on DiscountCountryAll { allCountries } } minimumRequirement { ... on DiscountMinimumSubtotal { greaterThanOrEqualToSubtotal { amount } } } codes(first: 2) { nodes { code } } } } } userErrors { field code message } } }",
   "variables": {
      "freeShippingCodeDiscount": {
        "startsAt": "2022-06-22T21:12:07.000Z",
        "appliesOncePerCustomer": false,
        "title": "FreeShipping",
        "code": "FreeShipping",
        "minimumRequirement": {
          "subtotal": {
            "greaterThanOrEqualToSubtotal": 20
          }
        },
        "customerSelection": {
          "all": true
        },
        "destination": {
          "all": true
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
    mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) {
      discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeFreeShipping {
              title
              startsAt
              endsAt
              maximumShippingPrice {
                amount
              }
              customerSelection {
                ... on DiscountCustomerAll {
                  allCustomers
                }
              }
              destinationSelection {
                ... on DiscountCountryAll {
                  allCountries
                }
              }
              minimumRequirement {
                ... on DiscountMinimumSubtotal {
                  greaterThanOrEqualToSubtotal {
                    amount
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
              "startsAt": "2022-06-22T21:12:07.000Z",
              "appliesOncePerCustomer": false,
              "title": "FreeShipping",
              "code": "FreeShipping",
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": 20
                  }
              },
              "customerSelection": {
                  "all": true
              },
              "destination": {
                  "all": true
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
    mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) {
      discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) {
        codeDiscountNode {
          id
          codeDiscount {
            ... on DiscountCodeFreeShipping {
              title
              startsAt
              endsAt
              maximumShippingPrice {
                amount
              }
              customerSelection {
                ... on DiscountCustomerAll {
                  allCustomers
                }
              }
              destinationSelection {
                ... on DiscountCountryAll {
                  allCountries
                }
              }
              minimumRequirement {
                ... on DiscountMinimumSubtotal {
                  greaterThanOrEqualToSubtotal {
                    amount
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
      "startsAt": "2022-06-22T21:12:07.000Z",
      "appliesOncePerCustomer": false,
      "title": "FreeShipping",
      "code": "FreeShipping",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": 20
        }
      },
      "customerSelection": {
        "all": true
      },
      "destination": {
        "all": true
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
      "query": `mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) {
        discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) {
          codeDiscountNode {
            id
            codeDiscount {
              ... on DiscountCodeFreeShipping {
                title
                startsAt
                endsAt
                maximumShippingPrice {
                  amount
                }
                customerSelection {
                  ... on DiscountCustomerAll {
                    allCustomers
                  }
                }
                destinationSelection {
                  ... on DiscountCountryAll {
                    allCountries
                  }
                }
                minimumRequirement {
                  ... on DiscountMinimumSubtotal {
                    greaterThanOrEqualToSubtotal {
                      amount
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
              "startsAt": "2022-06-22T21:12:07.000Z",
              "appliesOncePerCustomer": false,
              "title": "FreeShipping",
              "code": "FreeShipping",
              "minimumRequirement": {
                  "subtotal": {
                      "greaterThanOrEqualToSubtotal": 20
                  }
              },
              "customerSelection": {
                  "all": true
              },
              "destination": {
                  "all": true
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
  'mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) {
    discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) {
      codeDiscountNode {
        id
        codeDiscount {
          ... on DiscountCodeFreeShipping {
            title
            startsAt
            endsAt
            maximumShippingPrice {
              amount
            }
            customerSelection {
              ... on DiscountCustomerAll {
                allCustomers
              }
            }
            destinationSelection {
              ... on DiscountCountryAll {
                allCountries
              }
            }
            minimumRequirement {
              ... on DiscountMinimumSubtotal {
                greaterThanOrEqualToSubtotal {
                  amount
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
      "startsAt": "2022-06-22T21:12:07.000Z",
      "appliesOncePerCustomer": false,
      "title": "FreeShipping",
      "code": "FreeShipping",
      "minimumRequirement": {
        "subtotal": {
          "greaterThanOrEqualToSubtotal": 20
        }
      },
      "customerSelection": {
        "all": true
      },
      "destination": {
        "all": true
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeFreeShippingCreate": {
      "codeDiscountNode": {
        "id": "gid://shopify/DiscountCodeNode/1057856657",
        "codeDiscount": {
          "title": "FreeShipping",
          "startsAt": "2022-06-22T21:12:07Z",
          "endsAt": null,
          "maximumShippingPrice": null,
          "customerSelection": {
            "allCustomers": true
          },
          "destinationSelection": {
            "allCountries": true
          },
          "minimumRequirement": {
            "greaterThanOrEqualToSubtotal": {
              "amount": "20.0"
            }
          },
          "codes": {
            "nodes": [
              {
                "code": "FreeShipping"
              }
            ]
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Create a free shipping discount code for a customer segment

  #### Description

  Create a \[free shipping discount]\(https://help.shopify.com/manual/discounts/discount-types/free-shipping) that's applied when customers enter a code. This example shows how to create a discount code that offers free shipping for a specific customer segment.

  #### Query

  ```graphql
  mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) {
    discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) {
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
            destinationSelection {
              ... on DiscountCountryAll {
                allCountries
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
      "startsAt": "2025-07-24T16:18:00-04:00",
      "appliesOncePerCustomer": false,
      "title": "FreeShipping",
      "code": "FreeShipping",
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/210588551"
          ]
        }
      },
      "destination": {
        "all": true
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
  "query": "mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) { discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) { codeDiscountNode { id codeDiscount { ... on DiscountCodeFreeShipping { title startsAt endsAt context { ... on DiscountCustomerSegments { segments { id } } } destinationSelection { ... on DiscountCountryAll { allCountries } } codes(first: 2) { nodes { code } } } } } userErrors { field code message } } }",
   "variables": {
      "freeShippingCodeDiscount": {
        "startsAt": "2025-07-24T16:18:00-04:00",
        "appliesOncePerCustomer": false,
        "title": "FreeShipping",
        "code": "FreeShipping",
        "context": {
          "customerSegments": {
            "add": [
              "gid://shopify/Segment/210588551"
            ]
          }
        },
        "destination": {
          "all": true
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
    mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) {
      discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) {
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
              destinationSelection {
                ... on DiscountCountryAll {
                  allCountries
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
              "startsAt": "2025-07-24T16:18:00-04:00",
              "appliesOncePerCustomer": false,
              "title": "FreeShipping",
              "code": "FreeShipping",
              "context": {
                  "customerSegments": {
                      "add": [
                          "gid://shopify/Segment/210588551"
                      ]
                  }
              },
              "destination": {
                  "all": true
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
    mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) {
      discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) {
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
              destinationSelection {
                ... on DiscountCountryAll {
                  allCountries
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
      "startsAt": "2025-07-24T16:18:00-04:00",
      "appliesOncePerCustomer": false,
      "title": "FreeShipping",
      "code": "FreeShipping",
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/210588551"
          ]
        }
      },
      "destination": {
        "all": true
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
      "query": `mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) {
        discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) {
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
                destinationSelection {
                  ... on DiscountCountryAll {
                    allCountries
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
              "startsAt": "2025-07-24T16:18:00-04:00",
              "appliesOncePerCustomer": false,
              "title": "FreeShipping",
              "code": "FreeShipping",
              "context": {
                  "customerSegments": {
                      "add": [
                          "gid://shopify/Segment/210588551"
                      ]
                  }
              },
              "destination": {
                  "all": true
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
  'mutation discountCodeFreeShippingCreate($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) {
    discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) {
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
            destinationSelection {
              ... on DiscountCountryAll {
                allCountries
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
      "startsAt": "2025-07-24T16:18:00-04:00",
      "appliesOncePerCustomer": false,
      "title": "FreeShipping",
      "code": "FreeShipping",
      "context": {
        "customerSegments": {
          "add": [
            "gid://shopify/Segment/210588551"
          ]
        }
      },
      "destination": {
        "all": true
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountCodeFreeShippingCreate": {
      "codeDiscountNode": {
        "id": "gid://shopify/DiscountCodeNode/1057856658",
        "codeDiscount": {
          "title": "FreeShipping",
          "startsAt": "2025-07-24T20:18:00Z",
          "endsAt": null,
          "context": {
            "segments": [
              {
                "id": "gid://shopify/Segment/210588551"
              }
            ]
          },
          "destinationSelection": {
            "allCountries": true
          },
          "codes": {
            "nodes": [
              {
                "code": "FreeShipping"
              }
            ]
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### discountCodeFreeShippingCreate reference
