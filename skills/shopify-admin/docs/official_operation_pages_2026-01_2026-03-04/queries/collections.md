---
title: collections - GraphQL Admin
description: >-
  Retrieves a list of
  [collections](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection)

  in a store. Collections are groups of
  [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  that merchants can organize for display in their [online
  store](https://shopify.dev/docs/apps/build/online-store) and

  other [sales channels](https://shopify.dev/docs/apps/build/sales-channels).

  For example, an athletics store might create different collections for running
  attire, shoes, and accessories.


  Use the `collections` query when you need to:


  - Build a browsing interface for a store's product groupings.

  - Create collection searching, sorting, and filtering experiences (for
  example, by title, type, or published status).

  - Sync collection data with external systems.

  - Manage both custom
  ([manual](https://help.shopify.com/manual/products/collections/manual-shopify-collection))

  and smart
  ([automated](https://help.shopify.com/manual/products/collections/automated-collections))
  collections.


  The `collections` query supports
  [pagination](https://shopify.dev/docs/api/usage/pagination-graphql)

  for large catalogs and [saved
  searches](https://shopify.dev/docs/api/admin-graphql/latest/queries/collections#arguments-savedSearchId)

  for frequently used collection queries.


  The `collections` query returns collections with their associated metadata,
  including:


  - Basic collection information (title, description, handle, and type)

  - Collection image and SEO metadata

  - Product count and product relationships

  - Collection rules (for smart collections)

  - Publishing status and publication details

  - Metafields and custom attributes


  Learn more about [using metafields with smart
  collections](https://shopify.dev/docs/apps/build/custom-data/metafields/use-metafield-capabilities).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/collections'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/collections.md'
---

# collections

query

Retrieves a list of [collections](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection) in a store. Collections are groups of [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) that merchants can organize for display in their [online store](https://shopify.dev/docs/apps/build/online-store) and other [sales channels](https://shopify.dev/docs/apps/build/sales-channels). For example, an athletics store might create different collections for running attire, shoes, and accessories.

Use the `collections` query when you need to:

* Build a browsing interface for a store's product groupings.
* Create collection searching, sorting, and filtering experiences (for example, by title, type, or published status).
* Sync collection data with external systems.
* Manage both custom ([manual](https://help.shopify.com/manual/products/collections/manual-shopify-collection)) and smart ([automated](https://help.shopify.com/manual/products/collections/automated-collections)) collections.

The `collections` query supports [pagination](https://shopify.dev/docs/api/usage/pagination-graphql) for large catalogs and [saved searches](https://shopify.dev/docs/api/admin-graphql/latest/queries/collections#arguments-savedSearchId) for frequently used collection queries.

The `collections` query returns collections with their associated metadata, including:

* Basic collection information (title, description, handle, and type)
* Collection image and SEO metadata
* Product count and product relationships
* Collection rules (for smart collections)
* Publishing status and publication details
* Metafields and custom attributes

Learn more about [using metafields with smart collections](https://shopify.dev/docs/apps/build/custom-data/metafields/use-metafield-capabilities).

## CollectionConnection arguments

[CollectionConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CollectionConnection)

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

  * * default

      string

    * collection\_type

      string

    * handle

      string

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:
      * `query=Bob Norman`
      * `query=title:green hoodie`

    - Valid values:
      * `custom`
      * `smart`

  * * id

      id

    * product\_id

      id

    - Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by collections containing a product by its ID.

  * * product\_publication\_status

      string

    * publishable\_status

      string

    * published\_at

      time

    - Filter by channel approval process status of the resource on a channel, such as the online store. The value is a composite of the [channel `app` ID](https://shopify.dev/api/admin-graphql/latest/objects/Channel#field-Channel.fields.app) (`Channel.app.id`) and one of the valid values. For simple visibility checks, use [published\_status](https://shopify.dev/api/admin-graphql/latest/queries/products#argument-query-filter-publishable_status) instead.

    - Valid values:

      * `* {channel_app_id}-approved`
      * `* {channel_app_id}-rejected`
      * `* {channel_app_id}-needs_action`
      * `* {channel_app_id}-awaiting_review`
      * `* {channel_app_id}-published`
      * `* {channel_app_id}-demoted`
      * `* {channel_app_id}-scheduled`
      * `* {channel_app_id}-provisionally_published`

      Example:

      * `product_publication_status:189769876-approved`

      **Deprecated:** This parameter is deprecated as of 2025-12 and will be removed in a future API version. Use [published\_status](https://shopify.dev/api/admin-graphql/latest/queries/products#argument-query-filter-publishable_status) for visibility checks. Filter by the publishable status of the resource on a channel. The value is a composite of the [channel `app` ID](https://shopify.dev/api/admin-graphql/latest/objects/Channel#app-price) (`Channel.app.id`) and one of the valid status values.

    - Valid values:

      * `* {channel_app_id}-unset`
      * `* {channel_app_id}-pending`
      * `* {channel_app_id}-approved`
      * `* {channel_app_id}-not_approved`

      Example:

      * `publishable_status:580111-unset`
      * `publishable_status:580111-pending`

      Filter by the date and time when the collection was published to the Online Store.

  * * published\_status

      string

    * title

      string

    - Filter resources by their visibility and publication state on a channel. Online store channel filtering: - `online_store_channel`: Returns all resources in the online store channel, regardless of publication status. - `published`/`visible`: Returns resources that are published to the online store. - `unpublished`: Returns resources that are not published to the online store. Channel-specific filtering using the [channel `app` ID](https://shopify.dev/api/admin-graphql/latest/objects/Channel#app-price) (`Channel.app.id`) with suffixes: - `{channel_app_id}-published`: Returns resources published to the specified channel. - `{channel_app_id}-visible`: Same as `{channel_app_id}-published` (kept for backwards compatibility). - `{channel_app_id}-intended`: Returns resources added to the channel but not yet published. - `{channel_app_id}-hidden`: Returns resources not added to the channel or not published. Other: - `unavailable`: Returns resources not published to any channel.

    - Valid values:
      * `online_store_channel`
      * `published`
      * `visible`
      * `unpublished`
      * `* {channel_app_id}-published`
      * `* {channel_app_id}-visible`
      * `* {channel_app_id}-intended`
      * `* {channel_app_id}-hidden`
      * `unavailable`
      Example:
      * `published_status:online_store_channel`
      * `published_status:published`
      * `published_status:580111-published`
      * `published_status:580111-hidden`
      * `published_status:unavailable`

  * updated\_at

    time

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

* sort​Key

  [Collection​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/CollectionSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Collection​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CollectionEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Collection!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection)

  non-null

  A list of nodes that are contained in CollectionEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Filter collections by title using a wildcard

  #### Description

  Retrieve collections whose titles start with a specific prefix using a wildcard in the query filter. In this example, the \`title:All\*\` is used to match collections with titles that begin with "All".

  #### Query

  ```graphql
  query {
    collections(first: 10, query: "title:All*") {
      edges {
        node {
          id
          title
          handle
          updatedAt
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
  "query": "query { collections(first: 10, query: \"title:All*\") { edges { node { id title handle updatedAt } } } }"
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
      collections(first: 10, query: "title:All*") {
        edges {
          node {
            id
            title
            handle
            updatedAt
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
      collections(first: 10, query: "title:All*") {
        edges {
          node {
            id
            title
            handle
            updatedAt
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
      collections(first: 10, query: "title:All*") {
        edges {
          node {
            id
            title
            handle
            updatedAt
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
    collections(first: 10, query: "title:All*") {
      edges {
        node {
          id
          title
          handle
          updatedAt
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "collections": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Collection/94229130",
            "title": "All products more expensive than free",
            "handle": "everything",
            "updatedAt": "2006-02-02T00:00:00Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Collection/142458073",
            "title": "All snowboards",
            "handle": "snowboards",
            "updatedAt": "2006-02-02T00:00:00Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Collection/431528632",
            "title": "All arbor products tagged deepsnow",
            "handle": "all-arbor-products-tagged-deepsnow",
            "updatedAt": "2006-02-02T00:00:00Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Collection/442946009",
            "title": "All products - handpicked!",
            "handle": "everything-custom",
            "updatedAt": "2006-02-02T00:00:00Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Collection/925420914",
            "title": "All snowboards called Draft",
            "handle": "drafts",
            "updatedAt": "2006-02-02T00:00:00Z"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve a list of custom collections

  #### Description

  Retrieve the first 50 \[custom collections]\(https://help.shopify.com/manual/products/collections/manual-shopify-collection), using the \`collection\_type\` query filter. The response provides details for each collection, including its ID, handle, title, last updated timestamp, description in HTML format, publication status, sort order, and the suffix of the Liquid template being used to show the collection in the online store. > Note: > You must have the \`read\_product\_listings\` access scope to retrieve publication information.

  #### Query

  ```graphql
  query CustomCollectionList {
    collections(first: 50, query: "collection_type:custom") {
      nodes {
        id
        handle
        title
        updatedAt
        descriptionHtml
        publishedOnCurrentPublication
        sortOrder
        templateSuffix
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
  "query": "query CustomCollectionList { collections(first: 50, query: \"collection_type:custom\") { nodes { id handle title updatedAt descriptionHtml publishedOnCurrentPublication sortOrder templateSuffix } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query CustomCollectionList {
      collections(first: 50, query: "collection_type:custom") {
        nodes {
          id
          handle
          title
          updatedAt
          descriptionHtml
          publishedOnCurrentPublication
          sortOrder
          templateSuffix
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
    query CustomCollectionList {
      collections(first: 50, query: "collection_type:custom") {
        nodes {
          id
          handle
          title
          updatedAt
          descriptionHtml
          publishedOnCurrentPublication
          sortOrder
          templateSuffix
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
    data: `query CustomCollectionList {
      collections(first: 50, query: "collection_type:custom") {
        nodes {
          id
          handle
          title
          updatedAt
          descriptionHtml
          publishedOnCurrentPublication
          sortOrder
          templateSuffix
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query CustomCollectionList {
    collections(first: 50, query: "collection_type:custom") {
      nodes {
        id
        handle
        title
        updatedAt
        descriptionHtml
        publishedOnCurrentPublication
        sortOrder
        templateSuffix
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "collections": {
      "nodes": [
        {
          "id": "gid://shopify/Collection/395646240",
          "handle": "ipods_two",
          "title": "IPods Two",
          "updatedAt": "2008-02-02T00:00:00Z",
          "descriptionHtml": "<p>The best selling ipod ever. Again</p>",
          "publishedOnCurrentPublication": true,
          "sortOrder": "MANUAL",
          "templateSuffix": null
        },
        {
          "id": "gid://shopify/Collection/691652237",
          "handle": "non-ipods",
          "title": "Non Ipods",
          "updatedAt": "2013-02-02T00:00:00Z",
          "descriptionHtml": "<p>No ipods here</p>",
          "publishedOnCurrentPublication": true,
          "sortOrder": "MANUAL",
          "templateSuffix": null
        },
        {
          "id": "gid://shopify/Collection/841564295",
          "handle": "ipods",
          "title": "IPods",
          "updatedAt": "2008-02-02T00:00:00Z",
          "descriptionHtml": "<p>The best selling ipod ever</p>",
          "publishedOnCurrentPublication": true,
          "sortOrder": "MANUAL",
          "templateSuffix": null
        }
      ]
    }
  }
  ```

* ### Retrieve a list of smart collections

  #### Description

  Retrieve the first 50 \[smart collections]\(https://help.shopify.com/manual/products/collections/smart-collections), using the \`collection\_type\` query filter. The response provides comprehensive details for each collection, including its ID, handle, title, last updated timestamp, description in HTML format, publication status, sort order, the suffix of the Liquid template being used to show the collection in the online store, and the rule set that defines the \[collection's conditions]\(https://help.shopify.com/manual/products/collections/smart-collections/conditions). > Note: > You must have the \`read\_product\_listings\` access scope to retrieve publication information.

  #### Query

  ```graphql
  query SmartCollectionList {
    collections(first: 50, query: "collection_type:smart") {
      nodes {
        id
        handle
        title
        updatedAt
        descriptionHtml
        publishedOnCurrentPublication
        sortOrder
        templateSuffix
        ruleSet {
          appliedDisjunctively
          rules {
            column
            relation
            condition
            conditionObject {
              ... on CollectionRuleMetafieldCondition {
                metafieldDefinition {
                  id
                }
              }
              ... on CollectionRuleProductCategoryCondition {
                __typename
              }
              ... on CollectionRuleTextCondition {
                value
              }
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
  "query": "query SmartCollectionList { collections(first: 50, query: \"collection_type:smart\") { nodes { id handle title updatedAt descriptionHtml publishedOnCurrentPublication sortOrder templateSuffix ruleSet { appliedDisjunctively rules { column relation condition conditionObject { ... on CollectionRuleMetafieldCondition { metafieldDefinition { id } } ... on CollectionRuleProductCategoryCondition { __typename } ... on CollectionRuleTextCondition { value } } } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query SmartCollectionList {
      collections(first: 50, query: "collection_type:smart") {
        nodes {
          id
          handle
          title
          updatedAt
          descriptionHtml
          publishedOnCurrentPublication
          sortOrder
          templateSuffix
          ruleSet {
            appliedDisjunctively
            rules {
              column
              relation
              condition
              conditionObject {
                ... on CollectionRuleMetafieldCondition {
                  metafieldDefinition {
                    id
                  }
                }
                ... on CollectionRuleProductCategoryCondition {
                  __typename
                }
                ... on CollectionRuleTextCondition {
                  value
                }
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
    query SmartCollectionList {
      collections(first: 50, query: "collection_type:smart") {
        nodes {
          id
          handle
          title
          updatedAt
          descriptionHtml
          publishedOnCurrentPublication
          sortOrder
          templateSuffix
          ruleSet {
            appliedDisjunctively
            rules {
              column
              relation
              condition
              conditionObject {
                ... on CollectionRuleMetafieldCondition {
                  metafieldDefinition {
                    id
                  }
                }
                ... on CollectionRuleProductCategoryCondition {
                  __typename
                }
                ... on CollectionRuleTextCondition {
                  value
                }
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
    data: `query SmartCollectionList {
      collections(first: 50, query: "collection_type:smart") {
        nodes {
          id
          handle
          title
          updatedAt
          descriptionHtml
          publishedOnCurrentPublication
          sortOrder
          templateSuffix
          ruleSet {
            appliedDisjunctively
            rules {
              column
              relation
              condition
              conditionObject {
                ... on CollectionRuleMetafieldCondition {
                  metafieldDefinition {
                    id
                  }
                }
                ... on CollectionRuleProductCategoryCondition {
                  __typename
                }
                ... on CollectionRuleTextCondition {
                  value
                }
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
  'query SmartCollectionList {
    collections(first: 50, query: "collection_type:smart") {
      nodes {
        id
        handle
        title
        updatedAt
        descriptionHtml
        publishedOnCurrentPublication
        sortOrder
        templateSuffix
        ruleSet {
          appliedDisjunctively
          rules {
            column
            relation
            condition
            conditionObject {
              ... on CollectionRuleMetafieldCondition {
                metafieldDefinition {
                  id
                }
              }
              ... on CollectionRuleProductCategoryCondition {
                __typename
              }
              ... on CollectionRuleTextCondition {
                value
              }
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
    "collections": {
      "nodes": [
        {
          "id": "gid://shopify/Collection/482865238",
          "handle": "smart-ipods",
          "title": "Smart iPods",
          "updatedAt": "2008-02-02T00:00:00Z",
          "descriptionHtml": "<p>The best selling ipod ever</p>",
          "publishedOnCurrentPublication": true,
          "sortOrder": "MANUAL",
          "templateSuffix": null,
          "ruleSet": {
            "appliedDisjunctively": false,
            "rules": [
              {
                "column": "TYPE",
                "relation": "EQUALS",
                "condition": "Cult Products",
                "conditionObject": {
                  "value": "Cult Products"
                }
              }
            ]
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the first five collections

  #### Description

  Retrieve the first five collections in a store. The response returns a list of the collections, including the collection ID, title, handle, last updated timestamp, and sort order.

  #### Query

  ```graphql
  query {
    collections(first: 5) {
      edges {
        node {
          id
          title
          handle
          updatedAt
          sortOrder
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
  "query": "query { collections(first: 5) { edges { node { id title handle updatedAt sortOrder } } } }"
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
      collections(first: 5) {
        edges {
          node {
            id
            title
            handle
            updatedAt
            sortOrder
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
      collections(first: 5) {
        edges {
          node {
            id
            title
            handle
            updatedAt
            sortOrder
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
      collections(first: 5) {
        edges {
          node {
            id
            title
            handle
            updatedAt
            sortOrder
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
    collections(first: 5) {
      edges {
        node {
          id
          title
          handle
          updatedAt
          sortOrder
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "collections": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Collection/79210309",
            "title": "Custom Other Items",
            "handle": "reorder_custom",
            "updatedAt": "2008-10-10T00:00:00Z",
            "sortOrder": "MANUAL"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Collection/94229130",
            "title": "All products more expensive than free",
            "handle": "everything",
            "updatedAt": "2006-02-02T00:00:00Z",
            "sortOrder": "MANUAL"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Collection/142458073",
            "title": "All snowboards",
            "handle": "snowboards",
            "updatedAt": "2006-02-02T00:00:00Z",
            "sortOrder": "MANUAL"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Collection/411960790",
            "title": "Bold snowboards",
            "handle": "bold",
            "updatedAt": "2006-02-02T00:00:00Z",
            "sortOrder": "MANUAL"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Collection/431528632",
            "title": "All arbor products tagged deepsnow",
            "handle": "all-arbor-products-tagged-deepsnow",
            "updatedAt": "2006-02-02T00:00:00Z",
            "sortOrder": "MANUAL"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the five most recently updated smart collections

  #### Description

  Retrieve the five most recently updated \[smart collections]\(https://help.shopify.com/manual/products/collections/smart-collections), using the \`collection\_type\` query filter and sorting by when they were last modified (\`UPDATED\_AT\` in reverse order). This query is useful for finding collections that have been recently changed. The response returns a list of collections, including their ID, title, handle, update timestamp, and sort order.

  #### Query

  ```graphql
  query {
    collections(first: 5, query: "collection_type:smart", sortKey: UPDATED_AT, reverse: true) {
      edges {
        node {
          id
          title
          handle
          updatedAt
          sortOrder
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
  "query": "query { collections(first: 5, query: \"collection_type:smart\", sortKey: UPDATED_AT, reverse: true) { edges { node { id title handle updatedAt sortOrder } } } }"
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
      collections(first: 5, query: "collection_type:smart", sortKey: UPDATED_AT, reverse: true) {
        edges {
          node {
            id
            title
            handle
            updatedAt
            sortOrder
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
      collections(first: 5, query: "collection_type:smart", sortKey: UPDATED_AT, reverse: true) {
        edges {
          node {
            id
            title
            handle
            updatedAt
            sortOrder
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
      collections(first: 5, query: "collection_type:smart", sortKey: UPDATED_AT, reverse: true) {
        edges {
          node {
            id
            title
            handle
            updatedAt
            sortOrder
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
    collections(first: 5, query: "collection_type:smart", sortKey: UPDATED_AT, reverse: true) {
      edges {
        node {
          id
          title
          handle
          updatedAt
          sortOrder
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "collections": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Collection/522532842",
            "title": "Frisbees",
            "handle": "reorder_smart_frisbees",
            "updatedAt": "2008-10-12T00:00:00Z",
            "sortOrder": "MANUAL"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Collection/1063001310",
            "title": "Smart Other items",
            "handle": "reorder_smart",
            "updatedAt": "2008-10-11T00:00:00Z",
            "sortOrder": "MANUAL"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Collection/1009501285",
            "title": "Dummy",
            "handle": "blank",
            "updatedAt": "2006-02-02T00:00:00Z",
            "sortOrder": "MANUAL"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Collection/925420914",
            "title": "All snowboards called Draft",
            "handle": "drafts",
            "updatedAt": "2006-02-02T00:00:00Z",
            "sortOrder": "MANUAL"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Collection/619119800",
            "title": "Cheap Stuff",
            "handle": "cheap",
            "updatedAt": "2006-02-02T00:00:00Z",
            "sortOrder": "MANUAL"
          }
        }
      ]
    }
  }
  ```
