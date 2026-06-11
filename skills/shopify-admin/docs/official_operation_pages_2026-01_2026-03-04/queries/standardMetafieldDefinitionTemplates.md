---
title: standardMetafieldDefinitionTemplates - GraphQL Admin
description: >-
  Retrieves preset metafield definition templates for common use cases. Each
  template provides a reserved namespace and key combination for specific
  purposes like product subtitles, care guides, or ISBN numbers. Use these
  templates to create standardized metafields across your store. Filter
  templates by constraint status or exclude those you've already activated.


  See the [list of standard metafield
  definitions](https://shopify.dev/docs/apps/build/custom-data/metafields/list-of-standard-definitions)
  for available templates.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/standardMetafieldDefinitionTemplates
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/standardMetafieldDefinitionTemplates.md
---

# standard​Metafield​Definition​Templates

query

Retrieves preset metafield definition templates for common use cases. Each template provides a reserved namespace and key combination for specific purposes like product subtitles, care guides, or ISBN numbers. Use these templates to create standardized metafields across your store. Filter templates by constraint status or exclude those you've already activated.

See the [list of standard metafield definitions](https://shopify.dev/docs/apps/build/custom-data/metafields/list-of-standard-definitions) for available templates.

## StandardMetafieldDefinitionTemplateConnection arguments

[StandardMetafieldDefinitionTemplateConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/StandardMetafieldDefinitionTemplateConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* constraint​Status

  [Metafield​Definition​Constraint​Status](https://shopify.dev/docs/api/admin-graphql/latest/enums/MetafieldDefinitionConstraintStatus)

  Filter standard metafield definitions based on whether they are constrained.

* constraint​Subtype

  [Metafield​Definition​Constraint​Subtype​Identifier](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetafieldDefinitionConstraintSubtypeIdentifier)

  Filter standard metafield definitions based on whether they apply to a given resource subtype.

* exclude​Activated

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Filter standard metafield definitions that have already been activated.

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Standard​Metafield​Definition​Template​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/StandardMetafieldDefinitionTemplateEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Standard​Metafield​Definition​Template!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/StandardMetafieldDefinitionTemplate)

  non-null

  A list of nodes that are contained in StandardMetafieldDefinitionTemplateEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Get a list of standard metafield definition templates

  #### Description

  The following query retrieves the first 5 standard metafield definition templates.

  #### Query

  ```graphql
  query StandardMetafieldDefinitionTemplates {
    standardMetafieldDefinitionTemplates(first: 5) {
      edges {
        node {
          id
          name
          namespace
          key
          description
          ownerTypes
          type {
            name
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
  "query": "query StandardMetafieldDefinitionTemplates { standardMetafieldDefinitionTemplates(first: 5) { edges { node { id name namespace key description ownerTypes type { name } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query StandardMetafieldDefinitionTemplates {
      standardMetafieldDefinitionTemplates(first: 5) {
        edges {
          node {
            id
            name
            namespace
            key
            description
            ownerTypes
            type {
              name
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
    query StandardMetafieldDefinitionTemplates {
      standardMetafieldDefinitionTemplates(first: 5) {
        edges {
          node {
            id
            name
            namespace
            key
            description
            ownerTypes
            type {
              name
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
    data: `query StandardMetafieldDefinitionTemplates {
      standardMetafieldDefinitionTemplates(first: 5) {
        edges {
          node {
            id
            name
            namespace
            key
            description
            ownerTypes
            type {
              name
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
  'query StandardMetafieldDefinitionTemplates {
    standardMetafieldDefinitionTemplates(first: 5) {
      edges {
        node {
          id
          name
          namespace
          key
          description
          ownerTypes
          type {
            name
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "standardMetafieldDefinitionTemplates": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/StandardMetafieldDefinitionTemplate/1",
            "name": "Product subtitle",
            "namespace": "descriptors",
            "key": "subtitle",
            "description": "Used as a shorthand for a product name",
            "ownerTypes": [
              "PRODUCT",
              "PRODUCTVARIANT"
            ],
            "type": {
              "name": "single_line_text_field"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/StandardMetafieldDefinitionTemplate/2",
            "name": "Care guide",
            "namespace": "descriptors",
            "key": "care_guide",
            "description": "Instructions for taking care of a product or apparel",
            "ownerTypes": [
              "PRODUCT",
              "PRODUCTVARIANT"
            ],
            "type": {
              "name": "multi_line_text_field"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/StandardMetafieldDefinitionTemplate/3",
            "name": "ISBN",
            "namespace": "facts",
            "key": "isbn",
            "description": "International Standard Book Number",
            "ownerTypes": [
              "PRODUCT",
              "PRODUCTVARIANT"
            ],
            "type": {
              "name": "single_line_text_field"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/StandardMetafieldDefinitionTemplate/4",
            "name": "UPC",
            "namespace": "facts",
            "key": "upc",
            "description": "Universal Product Code",
            "ownerTypes": [
              "PRODUCT",
              "PRODUCTVARIANT"
            ],
            "type": {
              "name": "single_line_text_field"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/StandardMetafieldDefinitionTemplate/5",
            "name": "EAN",
            "namespace": "facts",
            "key": "ean",
            "description": "European Article Number",
            "ownerTypes": [
              "PRODUCT",
              "PRODUCTVARIANT"
            ],
            "type": {
              "name": "single_line_text_field"
            }
          }
        }
      ]
    }
  }
  ```
