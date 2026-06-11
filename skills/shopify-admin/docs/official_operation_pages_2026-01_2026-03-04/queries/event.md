---
title: event - GraphQL Admin
description: >-
  Retrieves a single event by ID. Events chronicle activities in your store such
  as resource creation, updates, or staff comments. The query returns an
  [`Event`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Event)
  interface of type
  [`BasicEvent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/BasicEvent)
  or
  [`CommentEvent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CommentEvent).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/event'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/event.md'
---

# event

query

Retrieves a single event by ID. Events chronicle activities in your store such as resource creation, updates, or staff comments. The query returns an [`Event`](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Event) interface of type [`BasicEvent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/BasicEvent) or [`CommentEvent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CommentEvent).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the event.

***

## Possible returns

* Event

  [Event](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Event)

  Events chronicle resource activities such as the creation of an article, the fulfillment of an order, or the addition of a product.

  * action

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The action that occured.

  * app​Title

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The name of the app that created the event.

  * attribute​To​App

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the event was created by an app.

  * attribute​To​User

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the event was caused by an admin user.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the event was created.

  * critical​Alert

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the event is critical.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * message

    [Formatted​String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/FormattedString)

    non-null

    Human readable text that describes the event.

***

## Examples

* ### Retrieve the first basic-event

  #### Description

  Retrieve an event by its id.

  #### Query

  ```graphql
  query {
    event(id: "gid://shopify/BasicEvent/422690323") {
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
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query { event(id: \"gid://shopify/BasicEvent/422690323\") { id message ... on BasicEvent { action subjectType subject { __typename } } } }"
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
      event(id: "gid://shopify/BasicEvent/422690323") {
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
      event(id: "gid://shopify/BasicEvent/422690323") {
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
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      event(id: "gid://shopify/BasicEvent/422690323") {
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
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    event(id: "gid://shopify/BasicEvent/422690323") {
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
  }'
  ```

  #### Response

  ```json
  {
    "event": {
      "id": "gid://shopify/BasicEvent/422690323",
      "message": "bob bobsen included a product on Online Store: <a href=\"https://admin.myshopify.io/store/snowdevil/admin/products/440089423\">IPod Nano - 8GB</a>.",
      "action": "published",
      "subjectType": "PRODUCT",
      "subject": {
        "__typename": "Product"
      }
    }
  }
  ```

* ### Retrieves a single event

  #### Query

  ```graphql
  query EventShow($id: ID!) {
    event(id: $id) {
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
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/BasicEvent/267851118"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query EventShow($id: ID!) { event(id: $id) { id action createdAt message ... on BasicEvent { arguments subjectId subjectType additionalContent } } }",
   "variables": {
      "id": "gid://shopify/BasicEvent/267851118"
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
    query EventShow($id: ID!) {
      event(id: $id) {
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
    }`,
    {
      variables: {
          "id": "gid://shopify/BasicEvent/267851118"
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
    query EventShow($id: ID!) {
      event(id: $id) {
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
  QUERY

  variables = {
    "id": "gid://shopify/BasicEvent/267851118"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query EventShow($id: ID!) {
        event(id: $id) {
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
      }`,
      "variables": {
          "id": "gid://shopify/BasicEvent/267851118"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query EventShow($id: ID!) {
    event(id: $id) {
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
  }' \
  --variables \
  '{
    "id": "gid://shopify/BasicEvent/267851118"
  }'
  ```

  #### Response

  ```json
  {
    "event": {
      "id": "gid://shopify/BasicEvent/267851118",
      "action": "unpublished",
      "createdAt": "2006-06-09T12:00:00Z",
      "message": "",
      "arguments": [],
      "subjectId": "gid://shopify/Product/630255015",
      "subjectType": "PRODUCT",
      "additionalContent": "null"
    }
  }
  ```
