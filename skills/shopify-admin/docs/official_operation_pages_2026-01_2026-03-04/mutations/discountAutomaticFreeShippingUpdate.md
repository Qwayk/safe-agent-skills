---
title: discountAutomaticFreeShippingUpdate - GraphQL Admin
description: >-
  Updates existing automatic free shipping discounts, allowing merchants to
  modify promotion criteria, shipping destinations, and eligibility requirements
  without recreating the entire discount structure.


  For example, extending a holiday free shipping promotion to include additional
  countries, adjusting the minimum order value threshold, or expanding customer
  eligibility to include new segments.


  Use `DiscountAutomaticFreeShippingUpdate` to:

  - Modify shipping discount thresholds and criteria

  - Expand or restrict geographic availability

  - Update customer targeting and eligibility rules

  - Adjust promotion timing and activation periods


  Changes take effect immediately for new orders, while the mutation validates
  all modifications and reports any configuration conflicts through user errors.


  Learn more about [managing automatic
  discounts](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomaticFreeShipping).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticFreeShippingUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticFreeShippingUpdate.md
---

# discount​Automatic​Free​Shipping​Update

mutation

Requires Apps must have `write_discounts` access scope.

Updates existing automatic free shipping discounts, allowing merchants to modify promotion criteria, shipping destinations, and eligibility requirements without recreating the entire discount structure.

For example, extending a holiday free shipping promotion to include additional countries, adjusting the minimum order value threshold, or expanding customer eligibility to include new segments.

Use `DiscountAutomaticFreeShippingUpdate` to:

* Modify shipping discount thresholds and criteria
* Expand or restrict geographic availability
* Update customer targeting and eligibility rules
* Adjust promotion timing and activation periods

Changes take effect immediately for new orders, while the mutation validates all modifications and reports any configuration conflicts through user errors.

Learn more about [managing automatic discounts](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomaticFreeShipping).

## Arguments

* free​Shipping​Automatic​Discount

  [Discount​Automatic​Free​Shipping​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DiscountAutomaticFreeShippingInput)

  required

  The input data used to update the automatic free shipping discount.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the automatic free shipping discount to update.

***

## Discount​Automatic​Free​Shipping​Update​Payload returns

* automatic​Discount​Node

  [Discount​Automatic​Node](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomaticNode)

  The automatic discount that was updated.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update context for an automatic free shipping discount

  #### Description

  Update the context of an automatic \[free shipping discount]\(https://help.shopify.com/manual/discounts/discount-types/free-shipping) discount.

  #### Query

  ```graphql
  mutation discountAutomaticFreeShippingUpdate($id: ID!, $automaticFreeShippingDiscount: DiscountAutomaticFreeShippingInput!) {
    discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $automaticFreeShippingDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticFreeShipping {
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
    "id": "gid://shopify/DiscountAutomaticNode/1057856672",
    "automaticFreeShippingDiscount": {
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
  "query": "mutation discountAutomaticFreeShippingUpdate($id: ID!, $automaticFreeShippingDiscount: DiscountAutomaticFreeShippingInput!) { discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $automaticFreeShippingDiscount) { automaticDiscountNode { id automaticDiscount { ... on DiscountAutomaticFreeShipping { context { ... on DiscountCustomerSegments { segments { id } } } } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DiscountAutomaticNode/1057856672",
      "automaticFreeShippingDiscount": {
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
    mutation discountAutomaticFreeShippingUpdate($id: ID!, $automaticFreeShippingDiscount: DiscountAutomaticFreeShippingInput!) {
      discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $automaticFreeShippingDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticFreeShipping {
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
          "id": "gid://shopify/DiscountAutomaticNode/1057856672",
          "automaticFreeShippingDiscount": {
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
    mutation discountAutomaticFreeShippingUpdate($id: ID!, $automaticFreeShippingDiscount: DiscountAutomaticFreeShippingInput!) {
      discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $automaticFreeShippingDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticFreeShipping {
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
    "id": "gid://shopify/DiscountAutomaticNode/1057856672",
    "automaticFreeShippingDiscount": {
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
      "query": `mutation discountAutomaticFreeShippingUpdate($id: ID!, $automaticFreeShippingDiscount: DiscountAutomaticFreeShippingInput!) {
        discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $automaticFreeShippingDiscount) {
          automaticDiscountNode {
            id
            automaticDiscount {
              ... on DiscountAutomaticFreeShipping {
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
          "id": "gid://shopify/DiscountAutomaticNode/1057856672",
          "automaticFreeShippingDiscount": {
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
  'mutation discountAutomaticFreeShippingUpdate($id: ID!, $automaticFreeShippingDiscount: DiscountAutomaticFreeShippingInput!) {
    discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $automaticFreeShippingDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticFreeShipping {
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
    "id": "gid://shopify/DiscountAutomaticNode/1057856672",
    "automaticFreeShippingDiscount": {
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
    "discountAutomaticFreeShippingUpdate": {
      "automaticDiscountNode": {
        "id": "gid://shopify/DiscountAutomaticNode/1057856672",
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

* ### Update the date range of an automatic free shipping discount

  #### Description

  Update the date range of an automatic \[free shipping discount]\(https://help.shopify.com/manual/discounts/discount-types/free-shipping) discount. This example shows how to update the start, end dates, minimum quantity, and destination of an automatic free shipping discount.

  #### Query

  ```graphql
  mutation discountAutomaticFreeShippingUpdate($id: ID!, $automaticFreeShippingDiscount: DiscountAutomaticFreeShippingInput!) {
    discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $automaticFreeShippingDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticFreeShipping {
            startsAt
            endsAt
            minimumRequirement {
              ... on DiscountMinimumQuantity {
                greaterThanOrEqualToQuantity
              }
            }
            destinationSelection {
              ... on DiscountCountryAll {
                allCountries
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
    "id": "gid://shopify/DiscountAutomaticNode/1057856673",
    "automaticFreeShippingDiscount": {
      "startsAt": "2024-10-01T00:00:00Z",
      "endsAt": "2024-12-31T23:59:59Z",
      "minimumRequirement": {
        "quantity": {
          "greaterThanOrEqualToQuantity": "50"
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
  "query": "mutation discountAutomaticFreeShippingUpdate($id: ID!, $automaticFreeShippingDiscount: DiscountAutomaticFreeShippingInput!) { discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $automaticFreeShippingDiscount) { automaticDiscountNode { id automaticDiscount { ... on DiscountAutomaticFreeShipping { startsAt endsAt minimumRequirement { ... on DiscountMinimumQuantity { greaterThanOrEqualToQuantity } } destinationSelection { ... on DiscountCountryAll { allCountries } } } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DiscountAutomaticNode/1057856673",
      "automaticFreeShippingDiscount": {
        "startsAt": "2024-10-01T00:00:00Z",
        "endsAt": "2024-12-31T23:59:59Z",
        "minimumRequirement": {
          "quantity": {
            "greaterThanOrEqualToQuantity": "50"
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
    mutation discountAutomaticFreeShippingUpdate($id: ID!, $automaticFreeShippingDiscount: DiscountAutomaticFreeShippingInput!) {
      discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $automaticFreeShippingDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticFreeShipping {
              startsAt
              endsAt
              minimumRequirement {
                ... on DiscountMinimumQuantity {
                  greaterThanOrEqualToQuantity
                }
              }
              destinationSelection {
                ... on DiscountCountryAll {
                  allCountries
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
          "id": "gid://shopify/DiscountAutomaticNode/1057856673",
          "automaticFreeShippingDiscount": {
              "startsAt": "2024-10-01T00:00:00Z",
              "endsAt": "2024-12-31T23:59:59Z",
              "minimumRequirement": {
                  "quantity": {
                      "greaterThanOrEqualToQuantity": "50"
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
    mutation discountAutomaticFreeShippingUpdate($id: ID!, $automaticFreeShippingDiscount: DiscountAutomaticFreeShippingInput!) {
      discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $automaticFreeShippingDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticFreeShipping {
              startsAt
              endsAt
              minimumRequirement {
                ... on DiscountMinimumQuantity {
                  greaterThanOrEqualToQuantity
                }
              }
              destinationSelection {
                ... on DiscountCountryAll {
                  allCountries
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
    "id": "gid://shopify/DiscountAutomaticNode/1057856673",
    "automaticFreeShippingDiscount": {
      "startsAt": "2024-10-01T00:00:00Z",
      "endsAt": "2024-12-31T23:59:59Z",
      "minimumRequirement": {
        "quantity": {
          "greaterThanOrEqualToQuantity": "50"
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
      "query": `mutation discountAutomaticFreeShippingUpdate($id: ID!, $automaticFreeShippingDiscount: DiscountAutomaticFreeShippingInput!) {
        discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $automaticFreeShippingDiscount) {
          automaticDiscountNode {
            id
            automaticDiscount {
              ... on DiscountAutomaticFreeShipping {
                startsAt
                endsAt
                minimumRequirement {
                  ... on DiscountMinimumQuantity {
                    greaterThanOrEqualToQuantity
                  }
                }
                destinationSelection {
                  ... on DiscountCountryAll {
                    allCountries
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
          "id": "gid://shopify/DiscountAutomaticNode/1057856673",
          "automaticFreeShippingDiscount": {
              "startsAt": "2024-10-01T00:00:00Z",
              "endsAt": "2024-12-31T23:59:59Z",
              "minimumRequirement": {
                  "quantity": {
                      "greaterThanOrEqualToQuantity": "50"
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
  'mutation discountAutomaticFreeShippingUpdate($id: ID!, $automaticFreeShippingDiscount: DiscountAutomaticFreeShippingInput!) {
    discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $automaticFreeShippingDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticFreeShipping {
            startsAt
            endsAt
            minimumRequirement {
              ... on DiscountMinimumQuantity {
                greaterThanOrEqualToQuantity
              }
            }
            destinationSelection {
              ... on DiscountCountryAll {
                allCountries
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
    "id": "gid://shopify/DiscountAutomaticNode/1057856673",
    "automaticFreeShippingDiscount": {
      "startsAt": "2024-10-01T00:00:00Z",
      "endsAt": "2024-12-31T23:59:59Z",
      "minimumRequirement": {
        "quantity": {
          "greaterThanOrEqualToQuantity": "50"
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
    "discountAutomaticFreeShippingUpdate": {
      "automaticDiscountNode": {
        "id": "gid://shopify/DiscountAutomaticNode/1057856673",
        "automaticDiscount": {
          "startsAt": "2024-10-01T00:00:00Z",
          "endsAt": "2024-12-31T23:59:59Z",
          "minimumRequirement": {
            "greaterThanOrEqualToQuantity": "50"
          },
          "destinationSelection": {
            "allCountries": true
          }
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Update the title of an automatic free shipping discount

  #### Description

  Update the title of an automatic \[free shipping discount]\(https://help.shopify.com/manual/discounts/discount-types/free-shipping) discount.

  #### Query

  ```graphql
  mutation M($id: ID!, $freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput!) {
    discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $freeShippingAutomaticDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticFreeShipping {
            title
          }
        }
      }
      userErrors {
        message
        field
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/DiscountAutomaticNode/1057856674",
    "freeShippingAutomaticDiscount": {
      "title": "A new title"
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
  "query": "mutation M($id: ID!, $freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput!) { discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $freeShippingAutomaticDiscount) { automaticDiscountNode { id automaticDiscount { ... on DiscountAutomaticFreeShipping { title } } } userErrors { message field code } } }",
   "variables": {
      "id": "gid://shopify/DiscountAutomaticNode/1057856674",
      "freeShippingAutomaticDiscount": {
        "title": "A new title"
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
    mutation M($id: ID!, $freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput!) {
      discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $freeShippingAutomaticDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticFreeShipping {
              title
            }
          }
        }
        userErrors {
          message
          field
          code
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DiscountAutomaticNode/1057856674",
          "freeShippingAutomaticDiscount": {
              "title": "A new title"
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
    mutation M($id: ID!, $freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput!) {
      discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $freeShippingAutomaticDiscount) {
        automaticDiscountNode {
          id
          automaticDiscount {
            ... on DiscountAutomaticFreeShipping {
              title
            }
          }
        }
        userErrors {
          message
          field
          code
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DiscountAutomaticNode/1057856674",
    "freeShippingAutomaticDiscount": {
      "title": "A new title"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation M($id: ID!, $freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput!) {
        discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $freeShippingAutomaticDiscount) {
          automaticDiscountNode {
            id
            automaticDiscount {
              ... on DiscountAutomaticFreeShipping {
                title
              }
            }
          }
          userErrors {
            message
            field
            code
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DiscountAutomaticNode/1057856674",
          "freeShippingAutomaticDiscount": {
              "title": "A new title"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation M($id: ID!, $freeShippingAutomaticDiscount: DiscountAutomaticFreeShippingInput!) {
    discountAutomaticFreeShippingUpdate(id: $id, freeShippingAutomaticDiscount: $freeShippingAutomaticDiscount) {
      automaticDiscountNode {
        id
        automaticDiscount {
          ... on DiscountAutomaticFreeShipping {
            title
          }
        }
      }
      userErrors {
        message
        field
        code
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DiscountAutomaticNode/1057856674",
    "freeShippingAutomaticDiscount": {
      "title": "A new title"
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticFreeShippingUpdate": {
      "automaticDiscountNode": {
        "id": "gid://shopify/DiscountAutomaticNode/1057856674",
        "automaticDiscount": {
          "title": "A new title"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### discountAutomaticFreeShippingUpdate reference
