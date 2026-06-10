---
title: returnCreate - GraphQL Admin
description: >-
  Creates a return from an existing order that has at least one fulfilled

  [line
  item](https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem)

  that hasn't yet been refunded. If you create a return on an archived order,
  then the order is automatically

  unarchived.


  Use the `returnCreate` mutation when your workflow involves

  [approving](https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnApproveRequest)
  or

  [declining](https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnDeclineRequest)
  requested returns

  outside of the Shopify platform.


  The `returnCreate` mutation performs the following actions:


  - Creates a return in the `OPEN` state, and assumes that the return request
  from the customer has already been

  approved

  - Creates a [reverse fulfillment
  order](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/manage-reverse-fulfillment-orders),

  and enables you to create a [reverse
  delivery](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/manage-reverse-deliveries)

  for the reverse fulfillment order

  - Creates a sales agreement with a `RETURN` reason, which links to all sales
  created for the return or exchange

  - Generates sales records that reverse the sales records for the items being
  returned

  - Generates sales records for any exchange line items


  After you've created a return, use the

  [`return`](https://shopify.dev/docs/api/admin-graphql/latest/queries/return)
  query to retrieve the

  return by its ID. Learn more about providing a

  [return management
  workflow](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/build-return-management)

  for merchants.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnCreate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnCreate.md'
---

# return​Create

mutation

Requires `write_returns` access scope or `write_marketplace_returns` access scope.

Creates a return from an existing order that has at least one fulfilled [line item](https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem) that hasn't yet been refunded. If you create a return on an archived order, then the order is automatically unarchived.

Use the `returnCreate` mutation when your workflow involves [approving](https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnApproveRequest) or [declining](https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnDeclineRequest) requested returns outside of the Shopify platform.

The `returnCreate` mutation performs the following actions:

* Creates a return in the `OPEN` state, and assumes that the return request from the customer has already been approved
* Creates a [reverse fulfillment order](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/manage-reverse-fulfillment-orders), and enables you to create a [reverse delivery](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/manage-reverse-deliveries) for the reverse fulfillment order
* Creates a sales agreement with a `RETURN` reason, which links to all sales created for the return or exchange
* Generates sales records that reverse the sales records for the items being returned
* Generates sales records for any exchange line items

After you've created a return, use the [`return`](https://shopify.dev/docs/api/admin-graphql/latest/queries/return) query to retrieve the return by its ID. Learn more about providing a [return management workflow](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/build-return-management) for merchants.

## Arguments

* return​Input

  [Return​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ReturnInput)

  required

  Specifies the input fields for a return.

***

## Return​Create​Payload returns

* return

  [Return](https://shopify.dev/docs/api/admin-graphql/latest/objects/Return)

  The created return.

* user​Errors

  [\[Return​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a return with a return reason definition

  #### Description

  Create a return using the new \`returnReasonDefinitionId\` field. This example demonstrates how to specify a standardized return reason when creating a return. The \`returnReasonDefinitionId\` should be obtained from the \`returnReasonDefinitions\` or \`suggestedReturnReasonDefinitions\` query. Learn more about \[building for return management]\(https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/build-return-management).

  #### Query

  ```graphql
  mutation ReturnCreate($returnInput: ReturnInput!) {
    returnCreate(returnInput: $returnInput) {
      userErrors {
        field
        message
      }
      return {
        id
        returnLineItems(first: 1) {
          edges {
            node {
              id
              quantity
              returnReasonDefinition {
                id
                handle
                name
              }
              returnReasonNote
            }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "returnInput": {
      "orderId": "gid://shopify/Order/625362839",
      "returnLineItems": [
        {
          "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
          "quantity": 1,
          "returnReasonDefinitionId": "gid://shopify/ReturnReasonDefinition/640710815",
          "returnReasonNote": "The size doesn't fit properly"
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
  "query": "mutation ReturnCreate($returnInput: ReturnInput!) { returnCreate(returnInput: $returnInput) { userErrors { field message } return { id returnLineItems(first: 1) { edges { node { id quantity returnReasonDefinition { id handle name } returnReasonNote } } } } } }",
   "variables": {
      "returnInput": {
        "orderId": "gid://shopify/Order/625362839",
        "returnLineItems": [
          {
            "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
            "quantity": 1,
            "returnReasonDefinitionId": "gid://shopify/ReturnReasonDefinition/640710815",
            "returnReasonNote": "The size doesn'\''t fit properly"
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
    mutation ReturnCreate($returnInput: ReturnInput!) {
      returnCreate(returnInput: $returnInput) {
        userErrors {
          field
          message
        }
        return {
          id
          returnLineItems(first: 1) {
            edges {
              node {
                id
                quantity
                returnReasonDefinition {
                  id
                  handle
                  name
                }
                returnReasonNote
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "returnInput": {
              "orderId": "gid://shopify/Order/625362839",
              "returnLineItems": [
                  {
                      "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
                      "quantity": 1,
                      "returnReasonDefinitionId": "gid://shopify/ReturnReasonDefinition/640710815",
                      "returnReasonNote": "The size doesn't fit properly"
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
    mutation ReturnCreate($returnInput: ReturnInput!) {
      returnCreate(returnInput: $returnInput) {
        userErrors {
          field
          message
        }
        return {
          id
          returnLineItems(first: 1) {
            edges {
              node {
                id
                quantity
                returnReasonDefinition {
                  id
                  handle
                  name
                }
                returnReasonNote
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "returnInput": {
      "orderId": "gid://shopify/Order/625362839",
      "returnLineItems": [
        {
          "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
          "quantity": 1,
          "returnReasonDefinitionId": "gid://shopify/ReturnReasonDefinition/640710815",
          "returnReasonNote": "The size doesn't fit properly"
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
      "query": `mutation ReturnCreate($returnInput: ReturnInput!) {
        returnCreate(returnInput: $returnInput) {
          userErrors {
            field
            message
          }
          return {
            id
            returnLineItems(first: 1) {
              edges {
                node {
                  id
                  quantity
                  returnReasonDefinition {
                    id
                    handle
                    name
                  }
                  returnReasonNote
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "returnInput": {
              "orderId": "gid://shopify/Order/625362839",
              "returnLineItems": [
                  {
                      "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
                      "quantity": 1,
                      "returnReasonDefinitionId": "gid://shopify/ReturnReasonDefinition/640710815",
                      "returnReasonNote": "The size doesn't fit properly"
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
  'mutation ReturnCreate($returnInput: ReturnInput!) {
    returnCreate(returnInput: $returnInput) {
      userErrors {
        field
        message
      }
      return {
        id
        returnLineItems(first: 1) {
          edges {
            node {
              id
              quantity
              returnReasonDefinition {
                id
                handle
                name
              }
              returnReasonNote
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "returnInput": {
      "orderId": "gid://shopify/Order/625362839",
      "returnLineItems": [
        {
          "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
          "quantity": 1,
          "returnReasonDefinitionId": "gid://shopify/ReturnReasonDefinition/640710815",
          "returnReasonNote": "The size doesn't fit properly"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "returnCreate": {
      "userErrors": [],
      "return": {
        "id": "gid://shopify/Return/963805100",
        "returnLineItems": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/ReturnLineItem/791246332",
                "quantity": 1,
                "returnReasonDefinition": {
                  "id": "gid://shopify/ReturnReasonDefinition/640710815",
                  "handle": "too-small",
                  "name": "Too Small"
                },
                "returnReasonNote": "The size doesn't fit properly"
              }
            }
          ]
        }
      }
    }
  }
  ```

* ### Create a return for a fulfilled line item

  #### Description

  Create a return for a fulfilled \[line item]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem) and include a custom reason note—a freeform note that allows the customer to explain their reason for returning the item. The example returns the created return's ID and the associated order ID. Learn more about \[building for return management]\(https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/build-return-management).

  #### Query

  ```graphql
  mutation ReturnCreate($returnInput: ReturnInput!) {
    returnCreate(returnInput: $returnInput) {
      userErrors {
        field
        message
      }
      return {
        id
        order {
          id
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "returnInput": {
      "orderId": "gid://shopify/Order/625362839",
      "returnLineItems": [
        {
          "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
          "quantity": 1,
          "returnReason": "SIZE_TOO_SMALL"
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
  "query": "mutation ReturnCreate($returnInput: ReturnInput!) { returnCreate(returnInput: $returnInput) { userErrors { field message } return { id order { id } } } }",
   "variables": {
      "returnInput": {
        "orderId": "gid://shopify/Order/625362839",
        "returnLineItems": [
          {
            "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
            "quantity": 1,
            "returnReason": "SIZE_TOO_SMALL"
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
    mutation ReturnCreate($returnInput: ReturnInput!) {
      returnCreate(returnInput: $returnInput) {
        userErrors {
          field
          message
        }
        return {
          id
          order {
            id
          }
        }
      }
    }`,
    {
      variables: {
          "returnInput": {
              "orderId": "gid://shopify/Order/625362839",
              "returnLineItems": [
                  {
                      "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
                      "quantity": 1,
                      "returnReason": "SIZE_TOO_SMALL"
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
    mutation ReturnCreate($returnInput: ReturnInput!) {
      returnCreate(returnInput: $returnInput) {
        userErrors {
          field
          message
        }
        return {
          id
          order {
            id
          }
        }
      }
    }
  QUERY

  variables = {
    "returnInput": {
      "orderId": "gid://shopify/Order/625362839",
      "returnLineItems": [
        {
          "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
          "quantity": 1,
          "returnReason": "SIZE_TOO_SMALL"
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
      "query": `mutation ReturnCreate($returnInput: ReturnInput!) {
        returnCreate(returnInput: $returnInput) {
          userErrors {
            field
            message
          }
          return {
            id
            order {
              id
            }
          }
        }
      }`,
      "variables": {
          "returnInput": {
              "orderId": "gid://shopify/Order/625362839",
              "returnLineItems": [
                  {
                      "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
                      "quantity": 1,
                      "returnReason": "SIZE_TOO_SMALL"
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
  'mutation ReturnCreate($returnInput: ReturnInput!) {
    returnCreate(returnInput: $returnInput) {
      userErrors {
        field
        message
      }
      return {
        id
        order {
          id
        }
      }
    }
  }' \
  --variables \
  '{
    "returnInput": {
      "orderId": "gid://shopify/Order/625362839",
      "returnLineItems": [
        {
          "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
          "quantity": 1,
          "returnReason": "SIZE_TOO_SMALL"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "returnCreate": {
      "userErrors": [],
      "return": {
        "id": "gid://shopify/Return/963805073",
        "order": {
          "id": "gid://shopify/Order/625362839"
        }
      }
    }
  }
  ```

* ### Create a return with a custom return reason note

  #### Description

  Create a return for a fulfilled \[line item]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem) with a note that explains the reason for the return. The example returns the created return's ID and the return reason note. Learn more about \[building for return management]\(https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/build-return-management).

  #### Query

  ```graphql
  mutation ReturnCreateWithNote($returnInput: ReturnInput!) {
    returnCreate(returnInput: $returnInput) {
      userErrors {
        field
        message
      }
      return {
        id
        returnLineItems(first: 1) {
          edges {
            node {
              returnReasonNote
            }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "returnInput": {
      "orderId": "gid://shopify/Order/625362839",
      "returnLineItems": [
        {
          "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
          "quantity": 1,
          "returnReason": "OTHER",
          "returnReasonNote": "Customer changed mind"
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
  "query": "mutation ReturnCreateWithNote($returnInput: ReturnInput!) { returnCreate(returnInput: $returnInput) { userErrors { field message } return { id returnLineItems(first: 1) { edges { node { returnReasonNote } } } } } }",
   "variables": {
      "returnInput": {
        "orderId": "gid://shopify/Order/625362839",
        "returnLineItems": [
          {
            "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
            "quantity": 1,
            "returnReason": "OTHER",
            "returnReasonNote": "Customer changed mind"
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
    mutation ReturnCreateWithNote($returnInput: ReturnInput!) {
      returnCreate(returnInput: $returnInput) {
        userErrors {
          field
          message
        }
        return {
          id
          returnLineItems(first: 1) {
            edges {
              node {
                returnReasonNote
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "returnInput": {
              "orderId": "gid://shopify/Order/625362839",
              "returnLineItems": [
                  {
                      "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
                      "quantity": 1,
                      "returnReason": "OTHER",
                      "returnReasonNote": "Customer changed mind"
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
    mutation ReturnCreateWithNote($returnInput: ReturnInput!) {
      returnCreate(returnInput: $returnInput) {
        userErrors {
          field
          message
        }
        return {
          id
          returnLineItems(first: 1) {
            edges {
              node {
                returnReasonNote
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "returnInput": {
      "orderId": "gid://shopify/Order/625362839",
      "returnLineItems": [
        {
          "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
          "quantity": 1,
          "returnReason": "OTHER",
          "returnReasonNote": "Customer changed mind"
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
      "query": `mutation ReturnCreateWithNote($returnInput: ReturnInput!) {
        returnCreate(returnInput: $returnInput) {
          userErrors {
            field
            message
          }
          return {
            id
            returnLineItems(first: 1) {
              edges {
                node {
                  returnReasonNote
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "returnInput": {
              "orderId": "gid://shopify/Order/625362839",
              "returnLineItems": [
                  {
                      "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
                      "quantity": 1,
                      "returnReason": "OTHER",
                      "returnReasonNote": "Customer changed mind"
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
  'mutation ReturnCreateWithNote($returnInput: ReturnInput!) {
    returnCreate(returnInput: $returnInput) {
      userErrors {
        field
        message
      }
      return {
        id
        returnLineItems(first: 1) {
          edges {
            node {
              returnReasonNote
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "returnInput": {
      "orderId": "gid://shopify/Order/625362839",
      "returnLineItems": [
        {
          "fulfillmentLineItemId": "gid://shopify/FulfillmentLineItem/820022594",
          "quantity": 1,
          "returnReason": "OTHER",
          "returnReasonNote": "Customer changed mind"
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "returnCreate": {
      "userErrors": [],
      "return": {
        "id": "gid://shopify/Return/963805074",
        "returnLineItems": {
          "edges": [
            {
              "node": {
                "returnReasonNote": "Customer changed mind"
              }
            }
          ]
        }
      }
    }
  }
  ```

* ### returnCreate reference
