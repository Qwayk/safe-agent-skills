---
title: fulfillment - GraphQL Admin
description: >-
  Retrieves a
  [`Fulfillment`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Fulfillment)
  by its ID. A fulfillment is a record that the merchant has completed their
  work required for one or more line items in an
  [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order). It
  includes tracking information,
  [`LineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem)
  objects, and the status of the fulfillment.


  Use this query to track the progress of shipped items, view tracking details,
  or check [fulfillment
  events](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentEvent)
  for example when a package is out for delivery or delivered.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/fulfillment'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/fulfillment.md'
---

# fulfillment

query

Requires `read_orders` access scope, `read_marketplace_orders` access scope, `read_assigned_fulfillment_orders` access scope, `read_merchant_managed_fulfillment_orders` access scope, `read_third_party_fulfillment_orders` access scope or `read_marketplace_fulfillment_orders` access scope.

Retrieves a [`Fulfillment`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Fulfillment) by its ID. A fulfillment is a record that the merchant has completed their work required for one or more line items in an [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order). It includes tracking information, [`LineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem) objects, and the status of the fulfillment.

Use this query to track the progress of shipped items, view tracking details, or check [fulfillment events](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentEvent) for example when a package is out for delivery or delivered.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the Fulfillment to return.

***

## Possible returns

* Fulfillment

  [Fulfillment](https://shopify.dev/docs/api/admin-graphql/latest/objects/Fulfillment)

  A shipment of one or more items from an [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order). Tracks which [`LineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem) objects ship, their quantities, and the shipment's tracking information.

  Includes tracking details such as the carrier, tracking numbers, and URLs. The fulfillment connects to both the original order and any associated [`FulfillmentOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder) objects. [`FulfillmentEvent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentEvent) objects record milestones throughout the shipment lifecycle, from creation through delivery.

  Multiple fulfillments can exist for a single order when items either ship separately or from different locations.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the fulfillment was created.

  * delivered​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date that this fulfillment was delivered.

  * display​Status

    [Fulfillment​Display​Status](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentDisplayStatus)

    Human readable display status for this fulfillment.

  * estimated​Delivery​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The estimated date that this fulfillment will arrive.

  * events

    [Fulfillment​Event​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/FulfillmentEventConnection)

    non-null

    The history of events associated with this fulfillment.

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

    * sort​Key

      [Fulfillment​Event​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentEventSortKeys)

      Default:HAPPENED\_AT

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    ***

  * fulfillment​Line​Items

    [Fulfillment​Line​Item​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/FulfillmentLineItemConnection)

    non-null

    List of the fulfillment's line items.

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

  * fulfillment​Orders

    [Fulfillment​Order​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/FulfillmentOrderConnection)

    non-null

    A paginated list of fulfillment orders for the fulfillment.

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

  * in​Transit​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time when the fulfillment went into transit.

  * legacy​Resource​Id

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The ID of the corresponding resource in the REST Admin API.

  * location

    [Location](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)

    The location that the fulfillment was processed at.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    Human readable reference identifier for this fulfillment.

  * order

    [Order!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

    non-null

    The order for which the fulfillment was created.

  * origin​Address

    [Fulfillment​Origin​Address](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOriginAddress)

    The address at which the fulfillment occurred. This field is intended for tax purposes, as a full address is required for tax providers to accurately calculate taxes. Typically this is the address of the warehouse or fulfillment center. To retrieve a fulfillment location's address, use the `assignedLocation` field on the [`FulfillmentOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder) object instead.

  * requires​Shipping

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether any of the line items in the fulfillment require shipping.

  * service

    [Fulfillment​Service](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentService)

    Fulfillment service associated with the fulfillment.

  * status

    [Fulfillment​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentStatus)

    non-null

    The status of the fulfillment.

  * total​Quantity

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    Sum of all line item quantities for the fulfillment.

  * tracking​Info

    [\[Fulfillment​Tracking​Info!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentTrackingInfo)

    non-null

    Tracking information associated with the fulfillment, such as the tracking company, tracking number, and tracking URL.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      Truncate the array result to this size.

    ***

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the fulfillment was last modified.

***

## Examples

* ### Receive a single Fulfillment

  #### Query

  ```graphql
  query FulfillmentShow($id: ID!) {
    fulfillment(id: $id) {
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
      location {
        id
        legacyResourceId
      }
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
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Fulfillment/237894043"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query FulfillmentShow($id: ID!) { fulfillment(id: $id) { fulfillmentLineItems(first: 10) { edges { node { id lineItem { title variant { id } } quantity originalTotalSet { shopMoney { amount currencyCode } } } } } status estimatedDeliveryAt location { id legacyResourceId } service { handle } trackingInfo(first: 10) { company number url } originAddress { address1 address2 city countryCode provinceCode zip } } }",
   "variables": {
      "id": "gid://shopify/Fulfillment/237894043"
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
    query FulfillmentShow($id: ID!) {
      fulfillment(id: $id) {
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
        location {
          id
          legacyResourceId
        }
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
    }`,
    {
      variables: {
          "id": "gid://shopify/Fulfillment/237894043"
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
    query FulfillmentShow($id: ID!) {
      fulfillment(id: $id) {
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
        location {
          id
          legacyResourceId
        }
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
  QUERY

  variables = {
    "id": "gid://shopify/Fulfillment/237894043"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query FulfillmentShow($id: ID!) {
        fulfillment(id: $id) {
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
          location {
            id
            legacyResourceId
          }
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
      }`,
      "variables": {
          "id": "gid://shopify/Fulfillment/237894043"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query FulfillmentShow($id: ID!) {
    fulfillment(id: $id) {
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
      location {
        id
        legacyResourceId
      }
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
  }' \
  --variables \
  '{
    "id": "gid://shopify/Fulfillment/237894043"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillment": {
      "fulfillmentLineItems": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/FulfillmentLineItem/761422146",
              "lineItem": {
                "title": "Draft",
                "variant": {
                  "id": "gid://shopify/ProductVariant/43729076"
                }
              },
              "quantity": 2,
              "originalTotalSet": {
                "shopMoney": {
                  "amount": "20.0",
                  "currencyCode": "USD"
                }
              }
            }
          }
        ]
      },
      "status": "SUCCESS",
      "estimatedDeliveryAt": null,
      "location": {
        "id": "gid://shopify/Location/124656943",
        "legacyResourceId": "124656943"
      },
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
      "originAddress": {
        "address1": "150 Elgin St",
        "address2": null,
        "city": "Ottawa",
        "countryCode": "CA",
        "provinceCode": "ON",
        "zip": "K2P 1L4"
      }
    }
  }
  ```

* ### Retrieves a list of fulfillment events for a specific fulfillment

  #### Query

  ```graphql
  query FulfillmentEventList($id: ID!) {
    fulfillment(id: $id) {
      events(first: 10) {
        edges {
          node {
            happenedAt
            status
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Fulfillment/237894043"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query FulfillmentEventList($id: ID!) { fulfillment(id: $id) { events(first: 10) { edges { node { happenedAt status } } } } }",
   "variables": {
      "id": "gid://shopify/Fulfillment/237894043"
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
    query FulfillmentEventList($id: ID!) {
      fulfillment(id: $id) {
        events(first: 10) {
          edges {
            node {
              happenedAt
              status
            }
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Fulfillment/237894043"
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
    query FulfillmentEventList($id: ID!) {
      fulfillment(id: $id) {
        events(first: 10) {
          edges {
            node {
              happenedAt
              status
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Fulfillment/237894043"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query FulfillmentEventList($id: ID!) {
        fulfillment(id: $id) {
          events(first: 10) {
            edges {
              node {
                happenedAt
                status
              }
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Fulfillment/237894043"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query FulfillmentEventList($id: ID!) {
    fulfillment(id: $id) {
      events(first: 10) {
        edges {
          node {
            happenedAt
            status
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Fulfillment/237894043"
  }'
  ```

  #### Response

  ```json
  {
    "fulfillment": {
      "events": {
        "edges": [
          {
            "node": {
              "happenedAt": "2016-05-02T11:00:00Z",
              "status": "LABEL_PURCHASED"
            }
          },
          {
            "node": {
              "happenedAt": "2016-05-03T11:00:00Z",
              "status": "OUT_FOR_DELIVERY"
            }
          }
        ]
      }
    }
  }
  ```
