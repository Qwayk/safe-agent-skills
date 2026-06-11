---
title: returnReasonDefinitions - GraphQL Admin
description: >-
  Returns the full library of available return reason definitions.


  Use this query to retrieve the standardized return reasons available for
  creating returns.

  Filter by IDs or handles to get specific definitions.


  Only non-deleted reasons should be shown to customers when creating new
  returns.

  Deleted reasons have been replaced with better alternatives and are no longer
  recommended.

  However, they remain valid options and may still appear on existing returns.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/returnReasonDefinitions
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/returnReasonDefinitions.md
---

# return​Reason​Definitions

query

Requires `read_returns` access scope.

Returns the full library of available return reason definitions.

Use this query to retrieve the standardized return reasons available for creating returns. Filter by IDs or handles to get specific definitions.

Only non-deleted reasons should be shown to customers when creating new returns. Deleted reasons have been replaced with better alternatives and are no longer recommended. However, they remain valid options and may still appear on existing returns.

## ReturnReasonDefinitionConnection arguments

[ReturnReasonDefinitionConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ReturnReasonDefinitionConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* handles

  [\[String!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A list of return reason definition handles to filter by.

* ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  A list of return reason definition IDs to filter by.

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * default

      string

    * deleted

      boolean

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      Filter by whether the return reason has been removed from taxonomy.

  * * id

      id

    * name

      string

    - Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by name.

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Return​Reason​Definition​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ReturnReasonDefinitionSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Return​Reason​Definition​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnReasonDefinitionEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Return​Reason​Definition!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnReasonDefinition)

  non-null

  A list of nodes that are contained in ReturnReasonDefinitionEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve available return reason definitions

  #### Description

  Retrieve the list of return reason definitions available for creating returns. Return reason definitions provide standardized, localized reasons for returns. Use the \`id\` field when creating returns, and the \`name\` field to display the reason to customers.

  #### Query

  ```graphql
  query {
    returnReasonDefinitions(first: 10) {
      edges {
        node {
          id
          handle
          name
          deleted
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
  "query": "query { returnReasonDefinitions(first: 10) { edges { node { id handle name deleted } } } }"
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
      returnReasonDefinitions(first: 10) {
        edges {
          node {
            id
            handle
            name
            deleted
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
      returnReasonDefinitions(first: 10) {
        edges {
          node {
            id
            handle
            name
            deleted
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
      returnReasonDefinitions(first: 10) {
        edges {
          node {
            id
            handle
            name
            deleted
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
    returnReasonDefinitions(first: 10) {
      edges {
        node {
          id
          handle
          name
          deleted
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "returnReasonDefinitions": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/ReturnReasonDefinition/27368211",
            "handle": "damaged",
            "name": "Damaged",
            "deleted": false
          }
        },
        {
          "node": {
            "id": "gid://shopify/ReturnReasonDefinition/61598531",
            "handle": "not_as_described",
            "name": "Not as Described",
            "deleted": false
          }
        },
        {
          "node": {
            "id": "gid://shopify/ReturnReasonDefinition/118463786",
            "handle": "unwanted_2",
            "name": "Unwanted",
            "deleted": false
          }
        },
        {
          "node": {
            "id": "gid://shopify/ReturnReasonDefinition/148612955",
            "handle": "too-big",
            "name": "Too Big",
            "deleted": false
          }
        },
        {
          "node": {
            "id": "gid://shopify/ReturnReasonDefinition/305697940",
            "handle": "defective",
            "name": "Defective",
            "deleted": false
          }
        },
        {
          "node": {
            "id": "gid://shopify/ReturnReasonDefinition/551551176",
            "handle": "other-reason",
            "name": "Other",
            "deleted": false
          }
        },
        {
          "node": {
            "id": "gid://shopify/ReturnReasonDefinition/640710815",
            "handle": "too-small",
            "name": "Too Small",
            "deleted": false
          }
        },
        {
          "node": {
            "id": "gid://shopify/ReturnReasonDefinition/712232956",
            "handle": "style",
            "name": "Style",
            "deleted": false
          }
        },
        {
          "node": {
            "id": "gid://shopify/ReturnReasonDefinition/845857515",
            "handle": "too-late",
            "name": "Too Late",
            "deleted": false
          }
        },
        {
          "node": {
            "id": "gid://shopify/ReturnReasonDefinition/955827578",
            "handle": "defective_2",
            "name": "Defective",
            "deleted": false
          }
        }
      ]
    }
  }
  ```
