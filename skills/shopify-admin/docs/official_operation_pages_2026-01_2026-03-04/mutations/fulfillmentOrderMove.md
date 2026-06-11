---
title: fulfillmentOrderMove - GraphQL Admin
description: >-
  Changes the location which is assigned to fulfill a number of unfulfilled
  fulfillment order line items.


  Moving a fulfillment order will fail in the following circumstances:


  * The fulfillment order is closed.

  * The fulfillment order has had progress manually reported. To move a
  fulfillment order that has had progress manually reported, the fulfillment
  order must first be marked as open resolving the ongoing progress state.

  * The destination location doesn't stock the requested inventory item.

  * The API client doesn't have the correct permissions.


  Line items which have already been fulfilled can't be re-assigned

  and will always remain assigned to the original location.


  You can't change the assigned location while a fulfillment order has a

  [request
  status](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentOrderRequestStatus)

  of `SUBMITTED`, `ACCEPTED`, `CANCELLATION_REQUESTED`, or
  `CANCELLATION_REJECTED`.

  These request statuses mean that a fulfillment order is awaiting action by a
  fulfillment service

  and can't be re-assigned without first having the fulfillment service accept a
  cancellation request.

  This behavior is intended to prevent items from being fulfilled by multiple
  locations or fulfillment services.


  ### How re-assigning line items affects fulfillment orders


  **First scenario:** Re-assign all line items belonging to a fulfillment order
  to a new location.


  In this case, the

  [assignedLocation](https://shopify.dev/docs/api/admin-graphql/latest/objects/fulfillmentorder#field-fulfillmentorder-assignedlocation)

  of the original fulfillment order will be updated to the new location.


  **Second scenario:** Re-assign a subset of the line items belonging to a
  fulfillment order to a new location.

  You can specify a subset of line items using the `fulfillmentOrderLineItems`
  parameter

  (available as of the `2023-04` API version),

  or specify that the original fulfillment order contains line items which have
  already been fulfilled.


  If the new location is already assigned to another active fulfillment order,
  on the same order, then

  a new fulfillment order is created. The existing fulfillment order is closed
  and line items are recreated

  in a new fulfillment order.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderMove
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/fulfillmentOrderMove.md
---

# fulfillment​Order​Move

mutation

Requires `write_merchant_managed_fulfillment_orders` access scope or `write_third_party_fulfillment_orders` access scope. Also: The user must have fulfill\_and\_ship\_orders permission.

Changes the location which is assigned to fulfill a number of unfulfilled fulfillment order line items.

Moving a fulfillment order will fail in the following circumstances:

* The fulfillment order is closed.
* The fulfillment order has had progress manually reported. To move a fulfillment order that has had progress manually reported, the fulfillment order must first be marked as open resolving the ongoing progress state.
* The destination location doesn't stock the requested inventory item.
* The API client doesn't have the correct permissions.

Line items which have already been fulfilled can't be re-assigned and will always remain assigned to the original location.

You can't change the assigned location while a fulfillment order has a [request status](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentOrderRequestStatus) of `SUBMITTED`, `ACCEPTED`, `CANCELLATION_REQUESTED`, or `CANCELLATION_REJECTED`. These request statuses mean that a fulfillment order is awaiting action by a fulfillment service and can't be re-assigned without first having the fulfillment service accept a cancellation request. This behavior is intended to prevent items from being fulfilled by multiple locations or fulfillment services.

### How re-assigning line items affects fulfillment orders

**First scenario:** Re-assign all line items belonging to a fulfillment order to a new location.

In this case, the [assignedLocation](https://shopify.dev/docs/api/admin-graphql/latest/objects/fulfillmentorder#field-fulfillmentorder-assignedlocation) of the original fulfillment order will be updated to the new location.

**Second scenario:** Re-assign a subset of the line items belonging to a fulfillment order to a new location. You can specify a subset of line items using the `fulfillmentOrderLineItems` parameter (available as of the `2023-04` API version), or specify that the original fulfillment order contains line items which have already been fulfilled.

If the new location is already assigned to another active fulfillment order, on the same order, then a new fulfillment order is created. The existing fulfillment order is closed and line items are recreated in a new fulfillment order.

## Arguments

* fulfillment​Order​Line​Items

  [\[Fulfillment​Order​Line​Item​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/FulfillmentOrderLineItemInput)

  The fulfillment order line items to be moved. If left blank, all unfulfilled line items belonging to the fulfillment order are moved.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the fulfillment order to be moved.

* new​Location​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the location where the fulfillment order will be moved.

***

## Fulfillment​Order​Move​Payload returns

* moved​Fulfillment​Order

  [Fulfillment​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  The fulfillment order which now contains the moved line items and is assigned to the destination location.

  If the original fulfillment order doesn't have any line items which are fully or partially fulfilled, the original fulfillment order will be moved to the new location. However if this isn't the case, the moved fulfillment order will differ from the original one.

* original​Fulfillment​Order

  [Fulfillment​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  The final state of the original fulfillment order.

  As a result of the move operation, the original fulfillment order might be moved to the new location or remain in the original location. The original fulfillment order might have the same status or be closed.

* remaining​Fulfillment​Order

  [Fulfillment​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  This field is deprecated.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Move some of the line items in a fulfillment order to a new location

  #### Description

  Only the line items that are stocked at the new location get moved.

  #### Query

  ```graphql
  mutation fulfillmentOrderMove($id: ID!, $newLocationId: ID!) {
    fulfillmentOrderMove(id: $id, newLocationId: $newLocationId) {
      movedFulfillmentOrder {
        id
        status
      }
      originalFulfillmentOrder {
        id
        status
      }
      remainingFulfillmentOrder {
        id
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
    "id": "gid://shopify/FulfillmentOrder/940656279",
    "newLocationId": "gid://shopify/Location/346779380"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fulfillmentOrderMove($id: ID!, $newLocationId: ID!) { fulfillmentOrderMove(id: $id, newLocationId: $newLocationId) { movedFulfillmentOrder { id status } originalFulfillmentOrder { id status } remainingFulfillmentOrder { id status } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/FulfillmentOrder/940656279",
      "newLocationId": "gid://shopify/Location/346779380"
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
    mutation fulfillmentOrderMove($id: ID!, $newLocationId: ID!) {
      fulfillmentOrderMove(id: $id, newLocationId: $newLocationId) {
        movedFulfillmentOrder {
          id
          status
        }
        originalFulfillmentOrder {
          id
          status
        }
        remainingFulfillmentOrder {
          id
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
          "id": "gid://shopify/FulfillmentOrder/940656279",
          "newLocationId": "gid://shopify/Location/346779380"
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
    mutation fulfillmentOrderMove($id: ID!, $newLocationId: ID!) {
      fulfillmentOrderMove(id: $id, newLocationId: $newLocationId) {
        movedFulfillmentOrder {
          id
          status
        }
        originalFulfillmentOrder {
          id
          status
        }
        remainingFulfillmentOrder {
          id
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
    "id": "gid://shopify/FulfillmentOrder/940656279",
    "newLocationId": "gid://shopify/Location/346779380"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentOrderMove($id: ID!, $newLocationId: ID!) {
        fulfillmentOrderMove(id: $id, newLocationId: $newLocationId) {
          movedFulfillmentOrder {
            id
            status
          }
          originalFulfillmentOrder {
            id
            status
          }
          remainingFulfillmentOrder {
            id
            status
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/FulfillmentOrder/940656279",
          "newLocationId": "gid://shopify/Location/346779380"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentOrderMove($id: ID!, $newLocationId: ID!) {
    fulfillmentOrderMove(id: $id, newLocationId: $newLocationId) {
      movedFulfillmentOrder {
        id
        status
      }
      originalFulfillmentOrder {
        id
        status
      }
      remainingFulfillmentOrder {
        id
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
    "id": "gid://shopify/FulfillmentOrder/940656279",
    "newLocationId": "gid://shopify/Location/346779380"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrderMove": {
      "movedFulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/1046000780",
        "status": "OPEN"
      },
      "originalFulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/940656279",
        "status": "OPEN"
      },
      "remainingFulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/940656279",
        "status": "OPEN"
      },
      "userErrors": []
    }
  }
  ```

* ### Moves a fulfillment order to a new location

  #### Description

  Move all of the line items in a fulfillment order to a new location.

  #### Query

  ```graphql
  mutation fulfillmentOrderMove($id: ID!, $newLocationId: ID!) {
    fulfillmentOrderMove(id: $id, newLocationId: $newLocationId) {
      movedFulfillmentOrder {
        id
        status
      }
      originalFulfillmentOrder {
        id
        status
      }
      remainingFulfillmentOrder {
        id
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
    "id": "gid://shopify/FulfillmentOrder/564786110",
    "newLocationId": "gid://shopify/Location/346779380"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation fulfillmentOrderMove($id: ID!, $newLocationId: ID!) { fulfillmentOrderMove(id: $id, newLocationId: $newLocationId) { movedFulfillmentOrder { id status } originalFulfillmentOrder { id status } remainingFulfillmentOrder { id status } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/FulfillmentOrder/564786110",
      "newLocationId": "gid://shopify/Location/346779380"
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
    mutation fulfillmentOrderMove($id: ID!, $newLocationId: ID!) {
      fulfillmentOrderMove(id: $id, newLocationId: $newLocationId) {
        movedFulfillmentOrder {
          id
          status
        }
        originalFulfillmentOrder {
          id
          status
        }
        remainingFulfillmentOrder {
          id
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
          "id": "gid://shopify/FulfillmentOrder/564786110",
          "newLocationId": "gid://shopify/Location/346779380"
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
    mutation fulfillmentOrderMove($id: ID!, $newLocationId: ID!) {
      fulfillmentOrderMove(id: $id, newLocationId: $newLocationId) {
        movedFulfillmentOrder {
          id
          status
        }
        originalFulfillmentOrder {
          id
          status
        }
        remainingFulfillmentOrder {
          id
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
    "id": "gid://shopify/FulfillmentOrder/564786110",
    "newLocationId": "gid://shopify/Location/346779380"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation fulfillmentOrderMove($id: ID!, $newLocationId: ID!) {
        fulfillmentOrderMove(id: $id, newLocationId: $newLocationId) {
          movedFulfillmentOrder {
            id
            status
          }
          originalFulfillmentOrder {
            id
            status
          }
          remainingFulfillmentOrder {
            id
            status
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/FulfillmentOrder/564786110",
          "newLocationId": "gid://shopify/Location/346779380"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation fulfillmentOrderMove($id: ID!, $newLocationId: ID!) {
    fulfillmentOrderMove(id: $id, newLocationId: $newLocationId) {
      movedFulfillmentOrder {
        id
        status
      }
      originalFulfillmentOrder {
        id
        status
      }
      remainingFulfillmentOrder {
        id
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
    "id": "gid://shopify/FulfillmentOrder/564786110",
    "newLocationId": "gid://shopify/Location/346779380"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrderMove": {
      "movedFulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/564786110",
        "status": "OPEN"
      },
      "originalFulfillmentOrder": {
        "id": "gid://shopify/FulfillmentOrder/564786110",
        "status": "OPEN"
      },
      "remainingFulfillmentOrder": null,
      "userErrors": []
    }
  }
  ```

* ### fulfillmentOrderMove reference
