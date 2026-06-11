---
title: discountAutomaticAppUpdate - GraphQL Admin
description: >-
  Updates an existing automatic discount that's managed by an app using

  [Shopify Functions](https://shopify.dev/docs/apps/build/functions).

  Use this mutation when you need advanced, custom, or

  dynamic discount capabilities that aren't supported by

  [Shopify's native discount
  types](https://help.shopify.com/manual/discounts/discount-types).


  For example, use this mutation to update a new "Volume" discount type that
  applies a percentage

  off when customers purchase more than the minimum quantity of a product. For
  an example implementation,

  refer to [our
  tutorial](https://shopify.dev/docs/apps/build/discounts/build-discount-function).


  > Note:

  > To update code discounts with custom logic, use the

  [`discountCodeAppUpdate`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppUpdate)

  mutation instead.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountAutomaticAppUpdate.md
---

# discount​Automatic​App​Update

mutation

Requires `write_discounts` access scope.

Updates an existing automatic discount that's managed by an app using [Shopify Functions](https://shopify.dev/docs/apps/build/functions). Use this mutation when you need advanced, custom, or dynamic discount capabilities that aren't supported by [Shopify's native discount types](https://help.shopify.com/manual/discounts/discount-types).

For example, use this mutation to update a new "Volume" discount type that applies a percentage off when customers purchase more than the minimum quantity of a product. For an example implementation, refer to [our tutorial](https://shopify.dev/docs/apps/build/discounts/build-discount-function).

***

**Note:** To update code discounts with custom logic, use the \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeAppUpdate">\<code>\<span class="PreventFireFoxApplyingGapToWBR">discount\<wbr/>Code\<wbr/>App\<wbr/>Update\</span>\</code>\</a> mutation instead.

***

## Arguments

* automatic​App​Discount

  [Discount​Automatic​App​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DiscountAutomaticAppInput)

  required

  The input fields required to update the automatic discount.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the automatic discount to update.

***

## Discount​Automatic​App​Update​Payload returns

* automatic​App​Discount

  [Discount​Automatic​App](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountAutomaticApp)

  The updated automatic discount that the app provides.

* user​Errors

  [\[Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update context for automatic app discount for a customer segment

  #### Description

  Update an automatic discount that's managed by an app using \[Shopify Functions]\(https://shopify.dev/docs/apps/build/functions). This example shows how to update the context defining which buyers can use the automatic discount.

  #### Query

  ```graphql
  mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
    discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
      automaticAppDiscount {
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
    "id": "gid://shopify/DiscountAutomaticNode/159339796",
    "automaticAppDiscount": {
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
  "query": "mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) { discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) { automaticAppDiscount { title context { ... on DiscountCustomerSegments { segments { id } } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DiscountAutomaticNode/159339796",
      "automaticAppDiscount": {
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
    mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
      discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
        automaticAppDiscount {
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
          "id": "gid://shopify/DiscountAutomaticNode/159339796",
          "automaticAppDiscount": {
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
    mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
      discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
        automaticAppDiscount {
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
    "id": "gid://shopify/DiscountAutomaticNode/159339796",
    "automaticAppDiscount": {
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
      "query": `mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
        discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
          automaticAppDiscount {
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
          "id": "gid://shopify/DiscountAutomaticNode/159339796",
          "automaticAppDiscount": {
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
  'mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
    discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
      automaticAppDiscount {
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
    "id": "gid://shopify/DiscountAutomaticNode/159339796",
    "automaticAppDiscount": {
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
    "discountAutomaticAppUpdate": {
      "automaticAppDiscount": {
        "title": "Percentage off (Product)",
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

* ### Update the date range of an automatic app discount

  #### Description

  Update an automatic discount that's managed by an app using \[Shopify Functions]\(https://shopify.dev/docs/apps/build/functions). This example shows how to update the start and end dates of an automatic discount.

  #### Query

  ```graphql
  mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
    discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
      automaticAppDiscount {
        title
        startsAt
        endsAt
        status
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
    "id": "gid://shopify/DiscountAutomaticNode/159339796",
    "automaticAppDiscount": {
      "startsAt": "2025-01-01T00:00:00Z",
      "endsAt": "2025-09-30T23:59:59Z"
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
  "query": "mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) { discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) { automaticAppDiscount { title startsAt endsAt status } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DiscountAutomaticNode/159339796",
      "automaticAppDiscount": {
        "startsAt": "2025-01-01T00:00:00Z",
        "endsAt": "2025-09-30T23:59:59Z"
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
    mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
      discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
        automaticAppDiscount {
          title
          startsAt
          endsAt
          status
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DiscountAutomaticNode/159339796",
          "automaticAppDiscount": {
              "startsAt": "2025-01-01T00:00:00Z",
              "endsAt": "2025-09-30T23:59:59Z"
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
    mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
      discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
        automaticAppDiscount {
          title
          startsAt
          endsAt
          status
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DiscountAutomaticNode/159339796",
    "automaticAppDiscount": {
      "startsAt": "2025-01-01T00:00:00Z",
      "endsAt": "2025-09-30T23:59:59Z"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
        discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
          automaticAppDiscount {
            title
            startsAt
            endsAt
            status
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DiscountAutomaticNode/159339796",
          "automaticAppDiscount": {
              "startsAt": "2025-01-01T00:00:00Z",
              "endsAt": "2025-09-30T23:59:59Z"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
    discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
      automaticAppDiscount {
        title
        startsAt
        endsAt
        status
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DiscountAutomaticNode/159339796",
    "automaticAppDiscount": {
      "startsAt": "2025-01-01T00:00:00Z",
      "endsAt": "2025-09-30T23:59:59Z"
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticAppUpdate": {
      "automaticAppDiscount": {
        "title": "Percentage off (Product)",
        "startsAt": "2025-01-01T00:00:00Z",
        "endsAt": "2025-09-30T23:59:59Z",
        "status": "ACTIVE"
      },
      "userErrors": []
    }
  }
  ```

* ### Update the title of an automatic app discount

  #### Description

  Update an automatic discount that's managed by an app using \[Shopify Functions]\(https://shopify.dev/docs/apps/build/functions). This example shows how to update the title of an automatic discount.

  #### Query

  ```graphql
  mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
    discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
      automaticAppDiscount {
        title
        status
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
    "id": "gid://shopify/DiscountAutomaticNode/159339796",
    "automaticAppDiscount": {
      "title": "$5 discount"
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
  "query": "mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) { discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) { automaticAppDiscount { title status appDiscountType { appKey functionId } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/DiscountAutomaticNode/159339796",
      "automaticAppDiscount": {
        "title": "$5 discount"
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
    mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
      discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
        automaticAppDiscount {
          title
          status
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
          "id": "gid://shopify/DiscountAutomaticNode/159339796",
          "automaticAppDiscount": {
              "title": "$5 discount"
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
    mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
      discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
        automaticAppDiscount {
          title
          status
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
    "id": "gid://shopify/DiscountAutomaticNode/159339796",
    "automaticAppDiscount": {
      "title": "$5 discount"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
        discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
          automaticAppDiscount {
            title
            status
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
          "id": "gid://shopify/DiscountAutomaticNode/159339796",
          "automaticAppDiscount": {
              "title": "$5 discount"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation discountAutomaticAppUpdate($automaticAppDiscount: DiscountAutomaticAppInput!, $id: ID!) {
    discountAutomaticAppUpdate(automaticAppDiscount: $automaticAppDiscount, id: $id) {
      automaticAppDiscount {
        title
        status
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
    "id": "gid://shopify/DiscountAutomaticNode/159339796",
    "automaticAppDiscount": {
      "title": "$5 discount"
    }
  }'
  ```

  #### Response

  ```json
  {
    "discountAutomaticAppUpdate": {
      "automaticAppDiscount": {
        "title": "$5 discount",
        "status": "EXPIRED",
        "appDiscountType": {
          "appKey": "shopify-vm-test-app",
          "functionId": "4a28b080-ffe4-4e16-97a5-1f8ffe8dfd98"
        }
      },
      "userErrors": []
    }
  }
  ```

* ### discountAutomaticAppUpdate reference
