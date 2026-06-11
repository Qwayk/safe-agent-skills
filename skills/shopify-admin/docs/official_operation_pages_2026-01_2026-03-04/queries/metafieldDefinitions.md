---
title: metafieldDefinitions - GraphQL Admin
description: Returns a list of metafield definitions.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/metafieldDefinitions
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/metafieldDefinitions.md
---

# metafield​Definitions

query

Returns a list of metafield definitions.

## MetafieldDefinitionConnection arguments

[MetafieldDefinitionConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MetafieldDefinitionConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* constraint​Status

  [Metafield​Definition​Constraint​Status](https://shopify.dev/docs/api/admin-graphql/latest/enums/MetafieldDefinitionConstraintStatus)

  Filter metafield definitions based on whether they are constrained.

* constraint​Subtype

  [Metafield​Definition​Constraint​Subtype​Identifier](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetafieldDefinitionConstraintSubtypeIdentifier)

  Filter metafield definitions based on whether they apply to a given resource subtype.

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* key

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  Filter metafield definition by key.

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* namespace

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  Filter metafield definition by namespace.

* owner​Type

  [Metafield​Owner​Type!](https://shopify.dev/docs/api/admin-graphql/latest/enums/MetafieldOwnerType)

  required

  Filter the metafield definition by the specific owner type.

* pinned​Status

  [Metafield​Definition​Pinned​Status](https://shopify.dev/docs/api/admin-graphql/latest/enums/MetafieldDefinitionPinnedStatus)

  Default:ANY

  Filter the metafield definition by the pinned status.

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * default

      string

    * created\_at

      time

    * id

      id

    * key

      string

    * namespace

      string

    * owner\_type

      string

    * type

      string

    * updated\_at

      time

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      Filter by the date and time when the metafield definition was created.

    - Example:

      * `created_at:>2020-10-21T23:39:20Z`
      * `created_at:<now`
      * `created_at:<=2024`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by the metafield definition [`key`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinition#field-key) field.

    - Example:

      * `key:some-key`

      Filter by the metafield definition [`namespace`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinition#field-namespace) field.

    - Example:

      * `namespace:some-namespace`

      Filter by the metafield definition [`ownerType`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinition#field-ownertype) field.

    - Example:

      * `owner_type:PRODUCT`

      Filter by the metafield definition [`type`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinition#field-type) field.

    - Example:

      * `type:single_line_text_field`

      Filter by the date and time when the metafield definition was last updated.

      Example:

      * `updated_at:>2020-10-21T23:39:20Z`
      * `updated_at:<now`
      * `updated_at:<=2024`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Metafield​Definition​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/MetafieldDefinitionSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Metafield​Definition​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinitionEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Metafield​Definition!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinition)

  non-null

  A list of nodes that are contained in MetafieldDefinitionEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieving a list of metafield definitions

  #### Description

  The following example shows you how to retrieve a list of metafield definitions.

  #### Query

  ```graphql
  query MetafieldDefinitions($ownerType: MetafieldOwnerType!, $first: Int) {
    metafieldDefinitions(ownerType: $ownerType, first: $first) {
      nodes {
        name
        namespace
        key
        type {
          name
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "ownerType": "PRODUCT",
    "first": 2
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query MetafieldDefinitions($ownerType: MetafieldOwnerType!, $first: Int) { metafieldDefinitions(ownerType: $ownerType, first: $first) { nodes { name namespace key type { name } } } }",
   "variables": {
      "ownerType": "PRODUCT",
      "first": 2
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
    query MetafieldDefinitions($ownerType: MetafieldOwnerType!, $first: Int) {
      metafieldDefinitions(ownerType: $ownerType, first: $first) {
        nodes {
          name
          namespace
          key
          type {
            name
          }
        }
      }
    }`,
    {
      variables: {
          "ownerType": "PRODUCT",
          "first": 2
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
    query MetafieldDefinitions($ownerType: MetafieldOwnerType!, $first: Int) {
      metafieldDefinitions(ownerType: $ownerType, first: $first) {
        nodes {
          name
          namespace
          key
          type {
            name
          }
        }
      }
    }
  QUERY

  variables = {
    "ownerType": "PRODUCT",
    "first": 2
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query MetafieldDefinitions($ownerType: MetafieldOwnerType!, $first: Int) {
        metafieldDefinitions(ownerType: $ownerType, first: $first) {
          nodes {
            name
            namespace
            key
            type {
              name
            }
          }
        }
      }`,
      "variables": {
          "ownerType": "PRODUCT",
          "first": 2
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query MetafieldDefinitions($ownerType: MetafieldOwnerType!, $first: Int) {
    metafieldDefinitions(ownerType: $ownerType, first: $first) {
      nodes {
        name
        namespace
        key
        type {
          name
        }
      }
    }
  }' \
  --variables \
  '{
    "ownerType": "PRODUCT",
    "first": 2
  }'
  ```

  #### Response

  ```json
  {
    "metafieldDefinitions": {
      "nodes": [
        {
          "name": "Roast type",
          "namespace": "coffee_descriptors",
          "key": "roast",
          "type": {
            "name": "single_line_text_field"
          }
        },
        {
          "name": "Country of origin",
          "namespace": "coffee_descriptors",
          "key": "country_of_origin",
          "type": {
            "name": "single_line_text_field"
          }
        }
      ]
    }
  }
  ```

* ### Retrieving a list of metafield definitions

  #### Description

  The following example shows you how to retrieve a list of metafield definitions.

  #### Query

  ```graphql
  query MetafieldDefinitions($ownerType: MetafieldOwnerType!, $first: Int) {
    metafieldDefinitions(ownerType: $ownerType, first: $first) {
      nodes {
        name
        namespace
        key
        type {
          name
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "ownerType": "PRODUCT",
    "first": 2
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query MetafieldDefinitions($ownerType: MetafieldOwnerType!, $first: Int) { metafieldDefinitions(ownerType: $ownerType, first: $first) { nodes { name namespace key type { name } } } }",
   "variables": {
      "ownerType": "PRODUCT",
      "first": 2
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
    query MetafieldDefinitions($ownerType: MetafieldOwnerType!, $first: Int) {
      metafieldDefinitions(ownerType: $ownerType, first: $first) {
        nodes {
          name
          namespace
          key
          type {
            name
          }
        }
      }
    }`,
    {
      variables: {
          "ownerType": "PRODUCT",
          "first": 2
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
    query MetafieldDefinitions($ownerType: MetafieldOwnerType!, $first: Int) {
      metafieldDefinitions(ownerType: $ownerType, first: $first) {
        nodes {
          name
          namespace
          key
          type {
            name
          }
        }
      }
    }
  QUERY

  variables = {
    "ownerType": "PRODUCT",
    "first": 2
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query MetafieldDefinitions($ownerType: MetafieldOwnerType!, $first: Int) {
        metafieldDefinitions(ownerType: $ownerType, first: $first) {
          nodes {
            name
            namespace
            key
            type {
              name
            }
          }
        }
      }`,
      "variables": {
          "ownerType": "PRODUCT",
          "first": 2
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query MetafieldDefinitions($ownerType: MetafieldOwnerType!, $first: Int) {
    metafieldDefinitions(ownerType: $ownerType, first: $first) {
      nodes {
        name
        namespace
        key
        type {
          name
        }
      }
    }
  }' \
  --variables \
  '{
    "ownerType": "PRODUCT",
    "first": 2
  }'
  ```

  #### Response

  ```json
  {
    "metafieldDefinitions": {
      "nodes": [
        {
          "name": "Roast type",
          "namespace": "coffee_descriptors",
          "key": "roast",
          "type": {
            "name": "single_line_text_field"
          }
        },
        {
          "name": "Country of origin",
          "namespace": "coffee_descriptors",
          "key": "country_of_origin",
          "type": {
            "name": "single_line_text_field"
          }
        }
      ]
    }
  }
  ```
