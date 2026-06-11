---
title: events - GraphQL Admin
description: >-
  A paginated list of events that chronicle activities in the store.
  [`Event`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Event)
  is an interface implemented by types such as
  [`BasicEvent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/BasicEvent)
  and
  [`CommentEvent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CommentEvent)
  that track actions such as creating
  [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article)
  objects, fulfilling
  [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)
  objects, adding
  [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)
  objects, or staff comments on timelines.


  The query supports filtering and sorting to help you find specific events or
  audit store activity over time.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/events'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/events.md'
---

# events

query

A paginated list of events that chronicle activities in the store. [`Event`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Event) is an interface implemented by types such as [`BasicEvent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/BasicEvent) and [`CommentEvent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CommentEvent) that track actions such as creating [`Article`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Article) objects, fulfilling [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) objects, adding [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) objects, or staff comments on timelines.

The query supports filtering and sorting to help you find specific events or audit store activity over time.

## EventConnection arguments

[EventConnection](https://shopify.dev/docs/api/admin-graphql/latest/connections/EventConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * action

      string

    * comments

      boolean

    * created\_at

      time

    * id

      id

    * subject\_type

      string

    - The action that occured.

    - Example:

      * `action:create`

      Whether or not to include [comment-events](https://shopify.dev/api/admin-graphql/latest/objects/CommentEvent) in your search, passing `false` will exclude comment-events, any other value will include comment-events.

    - Example:

      * `false`
      * `true`

      Filter by the date and time when the event occurred. Event data is retained for 1 year.

    - Example:

      * `created_at:>2025-10-21`
      * `created_at:<now`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      The resource type affected by this event. See [EventSubjectType](https://shopify.dev/api/admin-graphql/latest/enums/EventSubjectType) for possible values.

      Example:

      * `PRODUCT_VARIANT`
      * `PRODUCT`
      * `COLLECTION`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Event​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/EventSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Event​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/EventEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Event!\]!](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Event)

  non-null

  A list of nodes that are contained in EventEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve the first 10 destroy events for products

  #### Description

  Retrieves the list of product events resulting from a delete.

  #### Query

  ```graphql
  query {
    events(query: "action:'destroy' AND subject_type:'PRODUCT'", first: 10) {
      edges {
        node {
          id
          message
          ... on BasicEvent {
            action
            subjectType
            subject {
              __typename
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
  "query": "query { events(query: \"action:'\''destroy'\'' AND subject_type:'\''PRODUCT'\''\", first: 10) { edges { node { id message ... on BasicEvent { action subjectType subject { __typename } } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      events(query: "action:'destroy' AND subject_type:'PRODUCT'", first: 10) {
        edges {
          node {
            id
            message
            ... on BasicEvent {
              action
              subjectType
              subject {
                __typename
              }
            }
          }
        }
      }
    }`,
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
    query {
      events(query: "action:'destroy' AND subject_type:'PRODUCT'", first: 10) {
        edges {
          node {
            id
            message
            ... on BasicEvent {
              action
              subjectType
              subject {
                __typename
              }
            }
          }
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      events(query: "action:'destroy' AND subject_type:'PRODUCT'", first: 10) {
        edges {
          node {
            id
            message
            ... on BasicEvent {
              action
              subjectType
              subject {
                __typename
              }
            }
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    events(query: "action:'destroy' AND subject_type:'PRODUCT'", first: 10) {
      edges {
        node {
          id
          message
          ... on BasicEvent {
            action
            subjectType
            subject {
              __typename
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
    "events": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/BasicEvent/625930779",
            "message": "Product was deleted: Dandy Googles (Blue).",
            "action": "destroy",
            "subjectType": "PRODUCT",
            "subject": {
              "__typename": "Product"
            }
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the first 10 events after a given time

  #### Description

  Retrieves the first 10 events after the 1st of January 2024.

  #### Query

  ```graphql
  query {
    events(query: "created_at:>=2024-01-01", first: 10) {
      edges {
        node {
          id
          message
          createdAt
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
  "query": "query { events(query: \"created_at:>=2024-01-01\", first: 10) { edges { node { id message createdAt } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      events(query: "created_at:>=2024-01-01", first: 10) {
        edges {
          node {
            id
            message
            createdAt
          }
        }
      }
    }`,
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
    query {
      events(query: "created_at:>=2024-01-01", first: 10) {
        edges {
          node {
            id
            message
            createdAt
          }
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      events(query: "created_at:>=2024-01-01", first: 10) {
        edges {
          node {
            id
            message
            createdAt
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    events(query: "created_at:>=2024-01-01", first: 10) {
      edges {
        node {
          id
          message
          createdAt
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "events": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/BasicEvent/20851159",
            "message": "Tax amount was updated from $22.36 USD to $19.85 USD.",
            "createdAt": "2024-11-07T15:11:35Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/31716108",
            "message": "bob bobsen approved an order cancellation processed by limitedaccessbob bobsen on Point of Sale.",
            "createdAt": "2024-11-07T15:11:35Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/132778104",
            "message": "Unknown event Order#access_order_fulfillment_approval...",
            "createdAt": "2024-11-07T15:11:35Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/155674255",
            "message": "This customer's orders were added to <a href=\"https://snowdevil.myshopify.com/admin/companies/1/locations/1\">Montreal</a>.",
            "createdAt": "2024-11-07T15:11:35Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/197669626",
            "message": "Order <a href=\"https://snowdevil.myshopify.com/admin/orders/647667644\">#1002</a> was created from this draft order.",
            "createdAt": "2024-11-07T15:11:35Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/NotificationSentEvent/233139490",
            "message": "An invoice was sent to Bob Bobsen (bobsburgers@example.net).",
            "createdAt": "2024-11-07T15:11:35Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/254468230",
            "message": "Order <a href=\"https://snowdevil.myshopify.com/admin/orders/148977776\">#1001</a> was created from this draft order.",
            "createdAt": "2024-11-07T15:11:35Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/272432974",
            "message": "Payment reminder email was sent to bob@example.com.",
            "createdAt": "2024-11-07T15:11:35Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/381046666",
            "message": "This customer's orders were removed from <a href=\"https://snowdevil.myshopify.com/admin/companies/1/locations/1\">Montreal</a>.",
            "createdAt": "2024-11-07T15:11:35Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/458992081",
            "message": "Order covered by the <a href=\"https://help.shopify.com/manual/shipping/shop-promise#limited-guarantee\">Shop Promise guarantee</a>.",
            "createdAt": "2024-11-07T15:11:35Z"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the first 10 events for products including comment events

  #### Description

  Retrieves the list of product events including comment events.

  #### Query

  ```graphql
  query {
    events(query: "comments:1 AND subject_type:'PRODUCT'", first: 10) {
      edges {
        node {
          id
          message
          ... on CommentEvent {
            rawMessage
          }
          ... on BasicEvent {
            action
            subjectType
            subject {
              __typename
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
  "query": "query { events(query: \"comments:1 AND subject_type:'\''PRODUCT'\''\", first: 10) { edges { node { id message ... on CommentEvent { rawMessage } ... on BasicEvent { action subjectType subject { __typename } } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      events(query: "comments:1 AND subject_type:'PRODUCT'", first: 10) {
        edges {
          node {
            id
            message
            ... on CommentEvent {
              rawMessage
            }
            ... on BasicEvent {
              action
              subjectType
              subject {
                __typename
              }
            }
          }
        }
      }
    }`,
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
    query {
      events(query: "comments:1 AND subject_type:'PRODUCT'", first: 10) {
        edges {
          node {
            id
            message
            ... on CommentEvent {
              rawMessage
            }
            ... on BasicEvent {
              action
              subjectType
              subject {
                __typename
              }
            }
          }
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      events(query: "comments:1 AND subject_type:'PRODUCT'", first: 10) {
        edges {
          node {
            id
            message
            ... on CommentEvent {
              rawMessage
            }
            ... on BasicEvent {
              action
              subjectType
              subject {
                __typename
              }
            }
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    events(query: "comments:1 AND subject_type:'PRODUCT'", first: 10) {
      edges {
        node {
          id
          message
          ... on CommentEvent {
            rawMessage
          }
          ... on BasicEvent {
            action
            subjectType
            subject {
              __typename
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
    "events": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/BasicEvent/267851118",
            "message": "",
            "action": "unpublished",
            "subjectType": "PRODUCT",
            "subject": null
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/422690323",
            "message": "bob bobsen included a product on Online Store: <a href=\"https://admin.myshopify.io/store/snowdevil/admin/products/440089423\">IPod Nano - 8GB</a>.",
            "action": "published",
            "subjectType": "PRODUCT",
            "subject": {
              "__typename": "Product"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/625930779",
            "message": "Product was deleted: Dandy Googles (Blue).",
            "action": "destroy",
            "subjectType": "PRODUCT",
            "subject": {
              "__typename": "Product"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/686413589",
            "message": "",
            "action": "create",
            "subjectType": "PRODUCT",
            "subject": null
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/806005652",
            "message": "bob bobsen included a product on POS Test Account: <a href=\"https://admin.myshopify.io/store/snowdevil/admin/products/912855135\">SEO Boots</a>.",
            "action": "published",
            "subjectType": "PRODUCT",
            "subject": {
              "__typename": "Product"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/836798121",
            "message": "",
            "action": "create",
            "subjectType": "PRODUCT",
            "subject": null
          }
        },
        {
          "node": {
            "id": "gid://shopify/BasicEvent/842889634",
            "message": "",
            "action": "unpublished",
            "subjectType": "PRODUCT",
            "subject": null
          }
        }
      ]
    }
  }
  ```

* ### Retrieves a list of events

  #### Query

  ```graphql
  query EventList {
    events(first: 5) {
      nodes {
        id
        action
        createdAt
        message
        ... on BasicEvent {
          arguments
          subjectId
          subjectType
          additionalContent
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
  "query": "query EventList { events(first: 5) { nodes { id action createdAt message ... on BasicEvent { arguments subjectId subjectType additionalContent } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query EventList {
      events(first: 5) {
        nodes {
          id
          action
          createdAt
          message
          ... on BasicEvent {
            arguments
            subjectId
            subjectType
            additionalContent
          }
        }
      }
    }`,
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
    query EventList {
      events(first: 5) {
        nodes {
          id
          action
          createdAt
          message
          ... on BasicEvent {
            arguments
            subjectId
            subjectType
            additionalContent
          }
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query EventList {
      events(first: 5) {
        nodes {
          id
          action
          createdAt
          message
          ... on BasicEvent {
            arguments
            subjectId
            subjectType
            additionalContent
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query EventList {
    events(first: 5) {
      nodes {
        id
        action
        createdAt
        message
        ... on BasicEvent {
          arguments
          subjectId
          subjectType
          additionalContent
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "events": {
      "nodes": [
        {
          "id": "gid://shopify/BasicEvent/9889833",
          "action": "restock_line_items",
          "createdAt": "2014-03-19T13:31:30Z",
          "message": "bob bobsen restocked 2 line items.",
          "arguments": [
            2
          ],
          "subjectId": "gid://shopify/Order/271719359",
          "subjectType": "ORDER",
          "additionalContent": "null"
        },
        {
          "id": "gid://shopify/BasicEvent/12536286",
          "action": "fulfillment_success",
          "createdAt": "2008-06-06T12:00:00Z",
          "message": "Shopify fulfilled 1 item via Mr. Drop Shipper.",
          "arguments": [
            "267732048",
            1
          ],
          "subjectId": "gid://shopify/Order/535108883",
          "subjectType": "ORDER",
          "additionalContent": "{\"root_component\":{\"type\":\"root_component\",\"content\":[{\"type\":\"list\",\"content\":[{\"type\":\"list_item\",\"content\":[{\"type\":\"text\",\"content\":\"1 × Draft - 151cm\",\"options\":{}},{\"type\":\"text\",\"content\":\" draft-151\",\"options\":{\"subdued\":true}}],\"options\":{\"large_margin\":true}}],\"options\":{\"title\":\"Items\",\"border_bottom\":true}},{\"type\":\"key_value_list\",\"content\":[{\"type\":\"key_value_pair\",\"key\":[{\"type\":\"text\",\"content\":\"Service\",\"options\":{}}],\"value\":[{\"type\":\"text\",\"content\":\"Mr. Drop Shipper\",\"options\":{}}],\"options\":{}}],\"options\":{\"title\":null}}]}}"
        },
        {
          "id": "gid://shopify/BasicEvent/14596041",
          "action": "confirmation_number_generated",
          "createdAt": "2014-03-18T13:31:30Z",
          "message": "Confirmation #QWE1234TF was generated for this order.",
          "arguments": [
            "QWE1234TF"
          ],
          "subjectId": "gid://shopify/Order/148977776",
          "subjectType": "ORDER",
          "additionalContent": "null"
        },
        {
          "id": "gid://shopify/BasicEvent/20851159",
          "action": "taxes_updated",
          "createdAt": "2024-11-07T15:11:35Z",
          "message": "Tax amount was updated from $22.36 USD to $19.85 USD.",
          "arguments": [
            22.36,
            19.85
          ],
          "subjectId": "gid://shopify/Order/148977776",
          "subjectType": "ORDER",
          "additionalContent": "null"
        },
        {
          "id": "gid://shopify/BasicEvent/22713642",
          "action": "exchange_created",
          "createdAt": "2008-06-06T12:00:00Z",
          "message": "bob bobsen completed an exchange on order <a href=\"https://snowdevil.myshopify.com/admin/orders/120375246\">#1060</a>.",
          "arguments": [],
          "subjectId": "gid://shopify/Order/989922345",
          "subjectType": "ORDER",
          "additionalContent": "null"
        }
      ]
    }
  }
  ```
