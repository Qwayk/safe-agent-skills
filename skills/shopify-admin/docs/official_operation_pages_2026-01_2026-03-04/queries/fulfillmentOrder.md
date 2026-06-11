---
title: fulfillmentOrder - GraphQL Admin
description: Returns a `FulfillmentOrder` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/fulfillmentOrder'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/fulfillmentOrder.md
---

# fulfillment​Order

query

Returns a `FulfillmentOrder` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `FulfillmentOrder` to return.

***

## Possible returns

* Fulfillment​Order

  [Fulfillment​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  The FulfillmentOrder object represents either an item or a group of items in an [Order](https://shopify.dev/api/admin-graphql/latest/objects/Order) that are expected to be fulfilled from the same location. There can be more than one fulfillment order for an [order](https://shopify.dev/api/admin-graphql/latest/objects/Order) at a given location.

  ![](https://shopify.dev/assets/api/reference/fulfillment_order_relationships.png)

  Fulfillment orders represent the work which is intended to be done in relation to an order. When fulfillment has started for one or more line items, a [Fulfillment](https://shopify.dev/api/admin-graphql/latest/objects/Fulfillment) is created by a merchant or third party to represent the ongoing or completed work of fulfillment.

  [See below for more details on creating fulfillments](#the-lifecycle-of-a-fulfillment-order-at-a-location-which-is-managed-by-a-fulfillment-service).

  ***

  **Note:** Shopify creates fulfillment orders automatically when an order is created. It is not possible to manually create fulfillment orders.\</p> \<p>\<a href="#the-lifecycle-of-a-fulfillment-order">See below for more details on the lifecycle of a fulfillment order\</a>.

  ***

  ## Retrieving fulfillment orders

  ### Fulfillment orders from an order

  All fulfillment orders related to a given order can be retrieved with the [Order.fulfillmentOrders](https://shopify.dev/api/admin-graphql/latest/objects/Order#connection-order-fulfillmentorders) connection.

  [API access scopes](#api-access-scopes) govern which fulfillments orders are returned to clients. An API client will only receive a subset of the fulfillment orders which belong to an order if they don't have the necessary access scopes to view all of the fulfillment orders.

  ### Fulfillment orders assigned to the app for fulfillment

  Fulfillment service apps can retrieve the fulfillment orders which have been assigned to their locations with the [assignedFulfillmentOrders](https://shopify.dev/api/admin-graphql/2024-07/objects/queryroot#connection-assignedfulfillmentorders) connection. Use the `assignmentStatus` argument to control whether all assigned fulfillment orders should be returned or only those where a merchant has sent a [fulfillment request](https://shopify.dev/api/admin-graphql/latest/objects/FulfillmentOrderMerchantRequest) and it has yet to be responded to.

  The API client must be granted the `read_assigned_fulfillment_orders` access scope to access the assigned fulfillment orders.

  ### All fulfillment orders

  Apps can retrieve all fulfillment orders with the [fulfillmentOrders](https://shopify.dev/api/admin-graphql/latest/queries/fulfillmentOrders) query. This query returns all assigned, merchant-managed, and third-party fulfillment orders on the shop, which are accessible to the app according to the [fulfillment order access scopes](#api-access-scopes) it was granted with.

  ## The lifecycle of a fulfillment order

  ### Fulfillment Order Creation

  After an order is created, a background worker performs the order routing process which determines which locations will be responsible for fulfilling the purchased items. Once the order routing process is complete, one or more fulfillment orders will be created and assigned to these locations. It is not possible to manually create fulfillment orders.

  Once a fulfillment order has been created, it will have one of two different lifecycles depending on the type of location which the fulfillment order is assigned to.

  ### The lifecycle of a fulfillment order at a merchant managed location

  Fulfillment orders are completed by creating [fulfillments](https://shopify.dev/api/admin-graphql/latest/objects/Fulfillment). Fulfillments represents the work done.

  For digital products a merchant or an order management app would create a fulfilment once the digital asset has been provisioned. For example, in the case of a digital gift card, a merchant would to do this once the gift card has been activated - before the email has been shipped.

  On the other hand, for a traditional shipped order, a merchant or an order management app would create a fulfillment after picking and packing the items relating to a fulfillment order, but before the courier has collected the goods.

  [Learn about managing fulfillment orders as an order management app](https://shopify.dev/apps/fulfillment/order-management-apps/manage-fulfillments).

  ### The lifecycle of a fulfillment order at a location which is managed by a fulfillment service

  For fulfillment orders which are assigned to a location that is managed by a fulfillment service, a merchant or an Order Management App can [send a fulfillment request](https://shopify.dev/api/admin-graphql/latest/mutations/fulfillmentOrderSubmitFulfillmentRequest) to the fulfillment service which operates the location to request that they fulfill the associated items. A fulfillment service has the option to [accept](https://shopify.dev/api/admin-graphql/latest/mutations/fulfillmentOrderAcceptFulfillmentRequest) or [reject](https://shopify.dev/api/admin-graphql/latest/mutations/fulfillmentOrderRejectFulfillmentRequest) this fulfillment request.

  Once the fulfillment service has accepted the request, the request can no longer be cancelled by the merchant or order management app and instead a [cancellation request must be submitted](https://shopify.dev/api/admin-graphql/latest/mutations/fulfillmentOrderSubmitCancellationRequest) to the fulfillment service.

  Once a fulfillment service accepts a fulfillment request, then after they are ready to pack items and send them for delivery, they create fulfillments with the [fulfillmentCreate](https://shopify.dev/api/admin-graphql/unstable/mutations/fulfillmentCreate) mutation. They can provide tracking information right away or create fulfillments without it and then update the tracking information for fulfillments with the [fulfillmentTrackingInfoUpdate](https://shopify.dev/api/admin-graphql/unstable/mutations/fulfillmentTrackingInfoUpdate) mutation.

  [Learn about managing fulfillment orders as a fulfillment service](https://shopify.dev/apps/fulfillment/fulfillment-service-apps/manage-fulfillments).

  ## API access scopes

  Fulfillment orders are governed by the following API access scopes:

  * The `read_merchant_managed_fulfillment_orders` and `write_merchant_managed_fulfillment_orders` access scopes grant access to fulfillment orders assigned to merchant-managed locations.
  * The `read_assigned_fulfillment_orders` and `write_assigned_fulfillment_orders` access scopes are intended for fulfillment services. These scopes grant access to fulfillment orders assigned to locations that are being managed by fulfillment services.
  * The `read_third_party_fulfillment_orders` and `write_third_party_fulfillment_orders` access scopes grant access to fulfillment orders assigned to locations managed by other fulfillment services.

  ### Fulfillment service app access scopes

  Usually, **fulfillment services** have the `write_assigned_fulfillment_orders` access scope and don't have the `*_third_party_fulfillment_orders` or `*_merchant_managed_fulfillment_orders` access scopes. The app will only have access to the fulfillment orders assigned to their location (or multiple locations if the app registers multiple fulfillment services on the shop). The app will not have access to fulfillment orders assigned to merchant-managed locations or locations owned by other fulfillment service apps.

  ### Order management app access scopes

  **Order management apps** will usually request `write_merchant_managed_fulfillment_orders` and `write_third_party_fulfillment_orders` access scopes. This will allow them to manage all fulfillment orders on behalf of a merchant.

  If an app combines the functions of an order management app and a fulfillment service, then the app should request all access scopes to manage all assigned and all unassigned fulfillment orders.

  ## Notifications about fulfillment orders

  Fulfillment services are required to [register](https://shopify.dev/api/admin-graphql/latest/objects/FulfillmentService) a self-hosted callback URL which has a number of uses. One of these uses is that this callback URL will be notified whenever a merchant submits a fulfillment or cancellation request.

  Both merchants and apps can [subscribe](https://shopify.dev/apps/fulfillment/fulfillment-service-apps/manage-fulfillments#webhooks) to the [fulfillment order webhooks](https://shopify.dev/api/admin-graphql/latest/enums/WebhookSubscriptionTopic#value-fulfillmentorderscancellationrequestaccepted) to be notified whenever fulfillment order related domain events occur.

  [Learn about fulfillment workflows](https://shopify.dev/apps/fulfillment).

  * assigned​Location

    [Fulfillment​Order​Assigned​Location!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrderAssignedLocation)

    non-null

    The fulfillment order's assigned location. This is the location where the fulfillment is expected to happen.

    The fulfillment order's assigned location might change in the following cases:

    * The fulfillment order has been entirely moved to a new location. For example, the [fulfillmentOrderMove](https://shopify.dev/api/admin-graphql/latest/mutations/fulfillmentOrderMove) mutation has been called, and you see the original fulfillment order in the [movedFulfillmentOrder](https://shopify.dev/api/admin-graphql/latest/mutations/fulfillmentOrderMove#field-fulfillmentordermovepayload-movedfulfillmentorder) field within the mutation's response.
    * Work on the fulfillment order hasn't yet begun, which means that the fulfillment order has the [OPEN](https://shopify.dev/api/admin-graphql/latest/enums/FulfillmentOrderStatus#value-open), [SCHEDULED](https://shopify.dev/api/admin-graphql/latest/enums/FulfillmentOrderStatus#value-scheduled), or [ON\_HOLD](https://shopify.dev/api/admin-graphql/latest/enums/FulfillmentOrderStatus#value-onhold) status, and the shop's location properties might be undergoing edits (for example, in the Shopify admin).

  * channel​Id

    [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    ID of the channel that created the order.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    Date and time when the fulfillment order was created.

  * delivery​Method

    [Delivery​Method](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryMethod)

    Delivery method of this fulfillment order.

  * destination

    [Fulfillment​Order​Destination](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrderDestination)

    The destination where the items should be sent.

  * fulfill​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time at which the fulfillment order will be fulfillable. When this date and time is reached, the scheduled fulfillment order is automatically transitioned to open. For example, the `fulfill_at` date for a subscription order might be the 1st of each month, a pre-order `fulfill_at` date would be `nil`, and a standard order `fulfill_at` date would be the order creation date.

  * fulfill​By

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The latest date and time by which all items in the fulfillment order need to be fulfilled.

  * fulfillment​Holds

    [\[Fulfillment​Hold!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentHold)

    non-null

    The fulfillment holds applied on the fulfillment order.

  * fulfillment​Orders​For​Merge

    [Fulfillment​Order​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/FulfillmentOrderConnection)

    non-null

    Fulfillment orders eligible for merging with the given fulfillment order.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * fulfillments

    [Fulfillment​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/FulfillmentConnection)

    non-null

    A list of fulfillments for the fulfillment order.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * international​Duties

    [Fulfillment​Order​International​Duties](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrderInternationalDuties)

    The duties delivery method of this fulfillment order.

  * line​Items

    [Fulfillment​Order​Line​Item​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/FulfillmentOrderLineItemConnection)

    non-null

    A list of the fulfillment order's line items.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * locations​For​Move

    [Fulfillment​Order​Location​For​Move​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/FulfillmentOrderLocationForMoveConnection)

    non-null

    A list of locations that the fulfillment order can potentially move to.

    * line​Item​Ids

      [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      Default:\[]

      ### Arguments

      Filter to a list of Fulfillment Order Line Items.

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * default

          string

        * active

          string

        - Filter by a case-insensitive search of multiple fields in a document.

        - Example:
          * `query=Bob Norman`
          * `query=title:green hoodie`

      * address1

        string

      * address2

        string

      * city

        string

      * country

        string

      * created\_at

        time

      * geolocated

        boolean

      * * id

          id

        * legacy

          boolean

        - Filter by `id` range.

        - Example:
          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

      * location\_id

        id

      * name

        string

      * * pickup\_in\_store

          string

        * province

          string

        -
        - Valid values:
          * `enabled`
          * `disabled`

      * zip

        string

    * location​Ids

      [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      Specific Location ids to check for the movability for a fulfillment order.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * merchant​Requests

    [Fulfillment​Order​Merchant​Request​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/FulfillmentOrderMerchantRequestConnection)

    non-null

    A list of requests sent by the merchant or an order management app to the fulfillment service for the fulfillment order.

    * kind

      [Fulfillment​Order​Merchant​Request​Kind](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentOrderMerchantRequestKind)

      ### Arguments

      The kind of request the merchant sent.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * order

    [Order!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

    non-null

    The order that's associated with the fulfillment order.

  * order​Id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    ID of the order that's associated with the fulfillment order.

  * order​Name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The unique identifier for the order that appears on the order page in the Shopify admin and the **Order status** page. For example, "#1001", "EN1001", or "1001-A". This value isn't unique across multiple stores.

  * order​Processed​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the order was processed. This date and time might not match the date and time when the order was created.

  * request​Status

    [Fulfillment​Order​Request​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentOrderRequestStatus)

    non-null

    The request status of the fulfillment order.

  * status

    [Fulfillment​Order​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentOrderStatus)

    non-null

    The status of the fulfillment order.

  * supported​Actions

    [\[Fulfillment​Order​Supported​Action!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrderSupportedAction)

    non-null

    The actions that can be performed on this fulfillment order.

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the fulfillment order was last updated.

***

## Examples

* ### Retrieves a list of locations that a fulfillment order can potentially move to.

  #### Query

  ```graphql
  query LocationsForMoveList($fulfillmentOrderId: ID!) {
    fulfillmentOrder(id: $fulfillmentOrderId) {
      locationsForMove(first: 10) {
        edges {
          node {
            location {
              id
              name
            }
            message
            movable
            availableLineItemsCount {
              count
            }
            unavailableLineItemsCount {
              count
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
    "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/564786110"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query LocationsForMoveList($fulfillmentOrderId: ID!) { fulfillmentOrder(id: $fulfillmentOrderId) { locationsForMove(first: 10) { edges { node { location { id name } message movable availableLineItemsCount { count } unavailableLineItemsCount { count } } } } } }",
   "variables": {
      "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/564786110"
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
    query LocationsForMoveList($fulfillmentOrderId: ID!) {
      fulfillmentOrder(id: $fulfillmentOrderId) {
        locationsForMove(first: 10) {
          edges {
            node {
              location {
                id
                name
              }
              message
              movable
              availableLineItemsCount {
                count
              }
              unavailableLineItemsCount {
                count
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/564786110"
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
    query LocationsForMoveList($fulfillmentOrderId: ID!) {
      fulfillmentOrder(id: $fulfillmentOrderId) {
        locationsForMove(first: 10) {
          edges {
            node {
              location {
                id
                name
              }
              message
              movable
              availableLineItemsCount {
                count
              }
              unavailableLineItemsCount {
                count
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/564786110"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query LocationsForMoveList($fulfillmentOrderId: ID!) {
        fulfillmentOrder(id: $fulfillmentOrderId) {
          locationsForMove(first: 10) {
            edges {
              node {
                location {
                  id
                  name
                }
                message
                movable
                availableLineItemsCount {
                  count
                }
                unavailableLineItemsCount {
                  count
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/564786110"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query LocationsForMoveList($fulfillmentOrderId: ID!) {
    fulfillmentOrder(id: $fulfillmentOrderId) {
      locationsForMove(first: 10) {
        edges {
          node {
            location {
              id
              name
            }
            message
            movable
            availableLineItemsCount {
              count
            }
            unavailableLineItemsCount {
              count
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/564786110"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrder": {
      "locationsForMove": {
        "edges": [
          {
            "node": {
              "location": {
                "id": "gid://shopify/Location/346779380",
                "name": "Ottawa Store"
              },
              "message": "No items are stocked at this location.",
              "movable": false,
              "availableLineItemsCount": {
                "count": 0
              },
              "unavailableLineItemsCount": {
                "count": 1
              }
            }
          },
          {
            "node": {
              "location": {
                "id": "gid://shopify/Location/648019273",
                "name": "Ottawa Store geo located"
              },
              "message": "No items are stocked at this location.",
              "movable": false,
              "availableLineItemsCount": {
                "count": 0
              },
              "unavailableLineItemsCount": {
                "count": 1
              }
            }
          },
          {
            "node": {
              "location": {
                "id": "gid://shopify/Location/884687543",
                "name": "Ottawa Warehouse"
              },
              "message": "No items are stocked at this location.",
              "movable": false,
              "availableLineItemsCount": {
                "count": 0
              },
              "unavailableLineItemsCount": {
                "count": 1
              }
            }
          },
          {
            "node": {
              "location": {
                "id": "gid://shopify/Location/124656943",
                "name": "Shipping Origin"
              },
              "message": "Current location.",
              "movable": false,
              "availableLineItemsCount": {
                "count": 0
              },
              "unavailableLineItemsCount": {
                "count": 1
              }
            }
          },
          {
            "node": {
              "location": {
                "id": "gid://shopify/Location/215093630",
                "name": "Snowdevil Shipwire Warehouse"
              },
              "message": "No items are stocked at this location.",
              "movable": false,
              "availableLineItemsCount": {
                "count": 0
              },
              "unavailableLineItemsCount": {
                "count": 1
              }
            }
          },
          {
            "node": {
              "location": {
                "id": "gid://shopify/Location/750123840",
                "name": "Toronto Store"
              },
              "message": "No items are stocked at this location.",
              "movable": false,
              "availableLineItemsCount": {
                "count": 0
              },
              "unavailableLineItemsCount": {
                "count": 1
              }
            }
          },
          {
            "node": {
              "location": {
                "id": "gid://shopify/Location/415211365",
                "name": "US Store"
              },
              "message": "No items are stocked at this location.",
              "movable": false,
              "availableLineItemsCount": {
                "count": 0
              },
              "unavailableLineItemsCount": {
                "count": 1
              }
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieves a specific fulfillment order

  #### Query

  ```graphql
  query FulfillmentOrderShow($id: ID!) {
    fulfillmentOrder(id: $id) {
      assignedLocation {
        location {
          id
        }
      }
      channelId
      destination {
        address1
        address2
        city
        company
        countryCode
        zip
        firstName
        lastName
      }
      fulfillAt
      fulfillBy
      requestStatus
      status
      lineItems(first: 10) {
        edges {
          node {
            inventoryItemId
            remainingQuantity
            requiresShipping
            weight {
              unit
              value
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
    "id": "gid://shopify/FulfillmentOrder/564786110"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query FulfillmentOrderShow($id: ID!) { fulfillmentOrder(id: $id) { assignedLocation { location { id } } channelId destination { address1 address2 city company countryCode zip firstName lastName } fulfillAt fulfillBy requestStatus status lineItems(first: 10) { edges { node { inventoryItemId remainingQuantity requiresShipping weight { unit value } } } } } }",
   "variables": {
      "id": "gid://shopify/FulfillmentOrder/564786110"
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
    query FulfillmentOrderShow($id: ID!) {
      fulfillmentOrder(id: $id) {
        assignedLocation {
          location {
            id
          }
        }
        channelId
        destination {
          address1
          address2
          city
          company
          countryCode
          zip
          firstName
          lastName
        }
        fulfillAt
        fulfillBy
        requestStatus
        status
        lineItems(first: 10) {
          edges {
            node {
              inventoryItemId
              remainingQuantity
              requiresShipping
              weight {
                unit
                value
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/FulfillmentOrder/564786110"
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
    query FulfillmentOrderShow($id: ID!) {
      fulfillmentOrder(id: $id) {
        assignedLocation {
          location {
            id
          }
        }
        channelId
        destination {
          address1
          address2
          city
          company
          countryCode
          zip
          firstName
          lastName
        }
        fulfillAt
        fulfillBy
        requestStatus
        status
        lineItems(first: 10) {
          edges {
            node {
              inventoryItemId
              remainingQuantity
              requiresShipping
              weight {
                unit
                value
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/FulfillmentOrder/564786110"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query FulfillmentOrderShow($id: ID!) {
        fulfillmentOrder(id: $id) {
          assignedLocation {
            location {
              id
            }
          }
          channelId
          destination {
            address1
            address2
            city
            company
            countryCode
            zip
            firstName
            lastName
          }
          fulfillAt
          fulfillBy
          requestStatus
          status
          lineItems(first: 10) {
            edges {
              node {
                inventoryItemId
                remainingQuantity
                requiresShipping
                weight {
                  unit
                  value
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/FulfillmentOrder/564786110"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query FulfillmentOrderShow($id: ID!) {
    fulfillmentOrder(id: $id) {
      assignedLocation {
        location {
          id
        }
      }
      channelId
      destination {
        address1
        address2
        city
        company
        countryCode
        zip
        firstName
        lastName
      }
      fulfillAt
      fulfillBy
      requestStatus
      status
      lineItems(first: 10) {
        edges {
          node {
            inventoryItemId
            remainingQuantity
            requiresShipping
            weight {
              unit
              value
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/FulfillmentOrder/564786110"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrder": {
      "assignedLocation": {
        "location": {
          "id": "gid://shopify/Location/124656943"
        }
      },
      "channelId": null,
      "destination": {
        "address1": "123 Amoebobacterieae St",
        "address2": "Unit 806",
        "city": "Ottawa",
        "company": "",
        "countryCode": "CA",
        "zip": "K2P0V6",
        "firstName": "Bob",
        "lastName": "Bobsen"
      },
      "fulfillAt": null,
      "fulfillBy": null,
      "requestStatus": "UNSUBMITTED",
      "status": "OPEN",
      "lineItems": {
        "edges": [
          {
            "node": {
              "inventoryItemId": "gid://shopify/InventoryItem/43729076",
              "remainingQuantity": 1,
              "requiresShipping": true,
              "weight": {
                "unit": "GRAMS",
                "value": 1500
              }
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieves fulfillments associated with a fulfillment order

  #### Query

  ```graphql
  query FulfillmentList($fulfillmentOrderId: ID!) {
    fulfillmentOrder(id: $fulfillmentOrderId) {
      fulfillments(first: 10) {
        edges {
          node {
            id
            fulfillmentLineItems(first: 10) {
              edges {
                node {
                  id
                  lineItem {
                    title
                    variant {
                      id
                    }
                  }
                  quantity
                  originalTotalSet {
                    shopMoney {
                      amount
                      currencyCode
                    }
                  }
                }
              }
            }
            status
            estimatedDeliveryAt
            service {
              handle
            }
            trackingInfo(first: 10) {
              company
              number
              url
            }
            originAddress {
              address1
              address2
              city
              countryCode
              provinceCode
              zip
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
    "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/158170091"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query FulfillmentList($fulfillmentOrderId: ID!) { fulfillmentOrder(id: $fulfillmentOrderId) { fulfillments(first: 10) { edges { node { id fulfillmentLineItems(first: 10) { edges { node { id lineItem { title variant { id } } quantity originalTotalSet { shopMoney { amount currencyCode } } } } } status estimatedDeliveryAt service { handle } trackingInfo(first: 10) { company number url } originAddress { address1 address2 city countryCode provinceCode zip } } } } } }",
   "variables": {
      "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/158170091"
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
    query FulfillmentList($fulfillmentOrderId: ID!) {
      fulfillmentOrder(id: $fulfillmentOrderId) {
        fulfillments(first: 10) {
          edges {
            node {
              id
              fulfillmentLineItems(first: 10) {
                edges {
                  node {
                    id
                    lineItem {
                      title
                      variant {
                        id
                      }
                    }
                    quantity
                    originalTotalSet {
                      shopMoney {
                        amount
                        currencyCode
                      }
                    }
                  }
                }
              }
              status
              estimatedDeliveryAt
              service {
                handle
              }
              trackingInfo(first: 10) {
                company
                number
                url
              }
              originAddress {
                address1
                address2
                city
                countryCode
                provinceCode
                zip
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/158170091"
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
    query FulfillmentList($fulfillmentOrderId: ID!) {
      fulfillmentOrder(id: $fulfillmentOrderId) {
        fulfillments(first: 10) {
          edges {
            node {
              id
              fulfillmentLineItems(first: 10) {
                edges {
                  node {
                    id
                    lineItem {
                      title
                      variant {
                        id
                      }
                    }
                    quantity
                    originalTotalSet {
                      shopMoney {
                        amount
                        currencyCode
                      }
                    }
                  }
                }
              }
              status
              estimatedDeliveryAt
              service {
                handle
              }
              trackingInfo(first: 10) {
                company
                number
                url
              }
              originAddress {
                address1
                address2
                city
                countryCode
                provinceCode
                zip
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/158170091"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query FulfillmentList($fulfillmentOrderId: ID!) {
        fulfillmentOrder(id: $fulfillmentOrderId) {
          fulfillments(first: 10) {
            edges {
              node {
                id
                fulfillmentLineItems(first: 10) {
                  edges {
                    node {
                      id
                      lineItem {
                        title
                        variant {
                          id
                        }
                      }
                      quantity
                      originalTotalSet {
                        shopMoney {
                          amount
                          currencyCode
                        }
                      }
                    }
                  }
                }
                status
                estimatedDeliveryAt
                service {
                  handle
                }
                trackingInfo(first: 10) {
                  company
                  number
                  url
                }
                originAddress {
                  address1
                  address2
                  city
                  countryCode
                  provinceCode
                  zip
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/158170091"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query FulfillmentList($fulfillmentOrderId: ID!) {
    fulfillmentOrder(id: $fulfillmentOrderId) {
      fulfillments(first: 10) {
        edges {
          node {
            id
            fulfillmentLineItems(first: 10) {
              edges {
                node {
                  id
                  lineItem {
                    title
                    variant {
                      id
                    }
                  }
                  quantity
                  originalTotalSet {
                    shopMoney {
                      amount
                      currencyCode
                    }
                  }
                }
              }
            }
            status
            estimatedDeliveryAt
            service {
              handle
            }
            trackingInfo(first: 10) {
              company
              number
              url
            }
            originAddress {
              address1
              address2
              city
              countryCode
              provinceCode
              zip
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/158170091"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillmentOrder": {
      "fulfillments": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/Fulfillment/684880463",
              "fulfillmentLineItems": {
                "edges": [
                  {
                    "node": {
                      "id": "gid://shopify/FulfillmentLineItem/423076942",
                      "lineItem": {
                        "title": "Element",
                        "variant": {
                          "id": "gid://shopify/ProductVariant/214453824"
                        }
                      },
                      "quantity": 1,
                      "originalTotalSet": {
                        "shopMoney": {
                          "amount": "10.0",
                          "currencyCode": "USD"
                        }
                      }
                    }
                  }
                ]
              },
              "status": "SUCCESS",
              "estimatedDeliveryAt": null,
              "service": {
                "handle": "manual"
              },
              "trackingInfo": [
                {
                  "company": "UPS",
                  "number": "1Z1234512345123456",
                  "url": "https://www.ups.com/WebTracking?loc=en_US&requester=ST&trackNums=1Z1234512345123456"
                }
              ],
              "originAddress": null
            }
          }
        ]
      }
    }
  }
  ```
