---
title: products - GraphQL Admin
description: >-
  Retrieves a list of
  [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  in a store. Products are the items that merchants can sell in their store.


  Use the `products` query when you need to:


  - Build a browsing interface for a product catalog.

  - Create product
  [searching](https://shopify.dev/docs/api/usage/search-syntax),
  [sorting](https://shopify.dev/docs/api/admin-graphql/latest/queries/products#arguments-sortKey),
  and
  [filtering](https://shopify.dev/docs/api/admin-graphql/latest/queries/products#arguments-query)
  experiences.

  - Implement product recommendations.

  - Sync product data with external systems.


  The `products` query supports
  [pagination](https://shopify.dev/docs/api/usage/pagination-graphql)

  to handle large product catalogs and [saved
  searches](https://shopify.dev/docs/api/admin-graphql/latest/queries/products#arguments-savedSearchId)

  for frequently used product queries.


  The `products` query returns products with their associated metadata,
  including:


  - Basic product information (for example, title, description, vendor, and
  type)

  - Product options and product variants, with their prices and inventory

  - Media attachments (for example, images and videos)

  - SEO metadata

  - Product categories and tags

  - Product availability and publishing statuses


  Learn more about working with [Shopify's product
  model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/product-model-components).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/products'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/products.md'
---

# products

query

Retrieves a list of [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) in a store. Products are the items that merchants can sell in their store.

Use the `products` query when you need to:

* Build a browsing interface for a product catalog.
* Create product [searching](https://shopify.dev/docs/api/usage/search-syntax), [sorting](https://shopify.dev/docs/api/admin-graphql/latest/queries/products#arguments-sortKey), and [filtering](https://shopify.dev/docs/api/admin-graphql/latest/queries/products#arguments-query) experiences.
* Implement product recommendations.
* Sync product data with external systems.

The `products` query supports [pagination](https://shopify.dev/docs/api/usage/pagination-graphql) to handle large product catalogs and [saved searches](https://shopify.dev/docs/api/admin-graphql/latest/queries/products#arguments-savedSearchId) for frequently used product queries.

The `products` query returns products with their associated metadata, including:

* Basic product information (for example, title, description, vendor, and type)
* Product options and product variants, with their prices and inventory
* Media attachments (for example, images and videos)
* SEO metadata
* Product categories and tags
* Product availability and publishing statuses

Learn more about working with [Shopify's product model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/product-model-components).

## ProductConnection arguments

[ProductConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductConnection)

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

    * barcode

      string

    * bundles

      boolean

    * category\_id

      string

    * collection\_id

      id

    * combined\_listing\_role

      string

    * created\_at

      time

    * delivery\_profile\_id

      id

    * error\_feedback

      string

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      Filter by the product variant [`barcode`](https://shopify.dev/api/admin-graphql/latest/objects/ProductVariant#field-barcode) field.

    - Example:

      * `barcode:ABC-abc-1234`

      Filter by a [product bundle](https://shopify.dev/docs/apps/build/product-merchandising/bundles). A product bundle is a set of two or more related products, which are commonly offered at a discount.

    - Example:

      * `bundles:true`

      Filter by the product [category ID](https://shopify.dev/api/admin-graphql/latest/objects/Product#field-category) (`product.category.id`). A product category is the category of a product from [Shopify's Standard Product Taxonomy](https://shopify.github.io/product-taxonomy/releases/unstable/?categoryId=sg-4-17-2-17).

    - Example:

      * `category_id:sg-4-17-2-17`

      Filter by the collection [`id`](https://shopify.dev/api/admin-graphql/latest/objects/Collection#field-id) field.

    - Example:

      * `collection_id:108179161409`

      Filter by the role of the product in a [combined listing](https://shopify.dev/apps/build/product-merchandising/combined-listings).

    - Valid values:

      * `parent`
      * `child`
      * `no_role`

      Example:

      * `combined_listing_role:parent`

      Filter by the date and time when the product was created.

    - Example:

      * `created_at:>'2020-10-21T23:39:20Z'`
      * `created_at:<now`
      * `created_at:<='2024'`

      Filter by the delivery profile [`id`](https://shopify.dev/api/admin-graphql/latest/objects/DeliveryProfile#field-id) field.

    - Example:

      * `delivery_profile_id:108179161409`

      Filter by products with publishing errors.

  * * gift\_card

      boolean

    * handle

      string

    * has\_only\_composites

      boolean

    * has\_only\_default\_variant

      boolean

    * has\_variant\_with\_components

      boolean

    * id

      id

    * inventory\_total

      integer

    * is\_price\_reduced

      boolean

    * metafields.{namespace}.{key}

      mixed

    * out\_of\_stock\_somewhere

      boolean

    * price

      bigdecimal

    * product\_configuration\_owner

      string

    * product\_publication\_status

      string

    * product\_type

      string

    * publication\_ids

      string

    * publishable\_status

      string

    * published\_at

      time

    * published\_status

      string

    * sku

      string

    * status

      string

    * tag

      string

    * tag\_not

      string

    * title

      string

    * updated\_at

      time

    * variant\_id

      id

    * variant\_title

      string

    * vendor

      string

    - Filter by the product [`isGiftCard`](https://shopify.dev/api/admin-graphql/latest/objects/Product#field-isgiftcard) field.

    - Example:

      * `gift_card:true`

      Filter by a comma-separated list of product [handles](https://shopify.dev/api/admin-graphql/latest/queries/products#argument-query-filter-handle).

    - Example:

      * `handle:the-minimal-snowboard`

      Filter by products that have only composite variants.

    - Example:

      * `has_only_composites:true`

      Filter by products that have only a default variant. A default variant is the only variant if no other variants are specified.

    - Example:

      * `has_only_default_variant:true`

      Filter by products that have variants with associated components.

    - Example:

      * `has_variant_with_components:true`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by inventory count.

    - Example:

      * `inventory_total:0`
      * `inventory_total:>150`
      * `inventory_total:>=200`

      Filter by products that have a reduced price. For more information, refer to the [`CollectionRule`](https://shopify.dev/api/admin-graphql/latest/objects/CollectionRule) object.

    - Example:

      * `is_price_reduced:true`

      Filters resources by metafield value. Format: `metafields.{namespace}.{key}:{value}`. Learn more about [querying by metafield value](https://shopify.dev/apps/build/custom-data/metafields/query-by-metafield-value).

    - Example:

      * `metafields.custom.on_sale:true`
      * `metafields.product.material:"gid://shopify/Metaobject/43458085"`

      Filter by products that are out of stock in at least one location.

    - Example:

      * `out_of_stock_somewhere:true`

      Filter by the product variant [`price`](https://shopify.dev/api/admin-graphql/latest/objects/Productvariant#field-price) field.

    - Example:

      * `price:100.57`

      Filter by the app [`id`](https://shopify.dev/api/admin-graphql/latest/objects/App#field-id) field.

    - Example:

      * `product_configuration_owner:10001`

      Filter by channel approval process status of the resource on a channel, such as the online store. The value is a composite of the [channel `app` ID](https://shopify.dev/api/admin-graphql/latest/objects/Channel#field-Channel.fields.app) (`Channel.app.id`) and one of the valid values. For simple visibility checks, use [published\_status](https://shopify.dev/api/admin-graphql/latest/queries/products#argument-query-filter-publishable_status) instead.

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

      Filter by a comma-separated list of [product types](https://help.shopify.com/manual/products/details/product-type).

    - Example:

      * `product_type:snowboard`

      Filter by a comma-separated list of publication IDs that are associated with the product.

    - Example:

      * `publication_ids:184111530305,184111694145`

      **Deprecated:** This parameter is deprecated as of 2025-12 and will be removed in a future API version. Use [published\_status](https://shopify.dev/api/admin-graphql/latest/queries/products#argument-query-filter-publishable_status) for visibility checks. Filter by the publishable status of the resource on a channel. The value is a composite of the [channel `app` ID](https://shopify.dev/api/admin-graphql/latest/objects/Channel#app-price) (`Channel.app.id`) and one of the valid status values.

    - Valid values:

      * `* {channel_app_id}-unset`
      * `* {channel_app_id}-pending`
      * `* {channel_app_id}-approved`
      * `* {channel_app_id}-not_approved`

      Example:

      * `publishable_status:580111-unset`
      * `publishable_status:580111-pending`

      Filter by the date and time when the product was published to the online store and other sales channels.

    - Example:

      * `published_at:>2020-10-21T23:39:20Z`
      * `published_at:<now`
      * `published_at:<=2024`

      Filter resources by their visibility and publication state on a channel. Online store channel filtering: - `online_store_channel`: Returns all resources in the online store channel, regardless of publication status. - `published`/`visible`: Returns resources that are published to the online store. - `unpublished`: Returns resources that are not published to the online store. Channel-specific filtering using the [channel `app` ID](https://shopify.dev/api/admin-graphql/latest/objects/Channel#app-price) (`Channel.app.id`) with suffixes: - `{channel_app_id}-published`: Returns resources published to the specified channel. - `{channel_app_id}-visible`: Same as `{channel_app_id}-published` (kept for backwards compatibility). - `{channel_app_id}-intended`: Returns resources added to the channel but not yet published. - `{channel_app_id}-hidden`: Returns resources not added to the channel or not published. Other: - `unavailable`: Returns resources not published to any channel.

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

      Filter by the product variant [`sku`](https://shopify.dev/api/admin-graphql/latest/objects/ProductVariant#field-sku) field. [Learn more about SKUs](https://help.shopify.com/manual/products/details/sku).

    - Example:

      * `sku:XYZ-12345`

      Filter by a comma-separated list of statuses. You can use statuses to manage inventory. Shopify only displays products with an `ACTIVE` status in online stores, sales channels, and apps.

    - Valid values:

      * `active` Default
      * `archived`
      * `draft`

      Example:

      * `status:active,draft`

      Filter objects by the `tag` field.

    - Example:

      * `tag:my_tag`

      Filter by objects that don’t have the specified tag.

    - Example:

      * `tag_not:my_tag`

      Filter by the product [`title`](https://shopify.dev/api/admin-graphql/latest/objects/Product#field-title) field.

    - Example:

      * `title:The Minimal Snowboard`

      Filter by the date and time when the product was last updated.

    - Example:

      * `updated_at:>'2020-10-21T23:39:20Z'`
      * `updated_at:<now`
      * `updated_at:<='2024'`

      Filter by the product variant [`id`](https://shopify.dev/api/admin-graphql/latest/objects/ProductVariant#field-id) field.

    - Example:

      * `variant_id:45779434701121`

      Filter by the product variant [`title`](https://shopify.dev/api/admin-graphql/latest/objects/ProductVariant#field-title) field.

    - Example:

      * `variant_title:'Special ski wax'`

      Filter by the origin or source of the product. Learn more about [vendors and managing vendor information](https://help.shopify.com/manual/products/managing-vendor-info).

      Example:

      * `vendor:Snowdevil`
      * `vendor:Snowdevil OR vendor:Icedevil`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

* sort​Key

  [Product​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Product​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Product!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  non-null

  A list of nodes that are contained in ProductEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve a list of products

  #### Description

  Retrieve a list of the first ten products. This example returns the ID and title for each product.

  #### Query

  ```graphql
  query GetProducts {
    products(first: 10) {
      nodes {
        id
        title
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
  "query": "query GetProducts { products(first: 10) { nodes { id title } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query GetProducts {
      products(first: 10) {
        nodes {
          id
          title
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
    query GetProducts {
      products(first: 10) {
        nodes {
          id
          title
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
    data: `query GetProducts {
      products(first: 10) {
        nodes {
          id
          title
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query GetProducts {
    products(first: 10) {
      nodes {
        id
        title
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "products": {
      "nodes": [
        {
          "id": "gid://shopify/Product/20995642",
          "title": "Element"
        },
        {
          "id": "gid://shopify/Product/108828309",
          "title": "Draft"
        },
        {
          "id": "gid://shopify/Product/121709582",
          "title": "Boots"
        },
        {
          "id": "gid://shopify/Product/440089423",
          "title": "IPod Nano - 8GB"
        },
        {
          "id": "gid://shopify/Product/558169081",
          "title": "Unpublished Boots"
        },
        {
          "id": "gid://shopify/Product/910489600",
          "title": "Crafty Shoes"
        },
        {
          "id": "gid://shopify/Product/912855135",
          "title": "SEO Boots"
        }
      ]
    }
  }
  ```

* ### Retrieve multiple sets of products with a single query

  #### Description

  Retrieve the five oldest and newest products by using \[aliases]\(https://shopify.dev/docs/apps/build/graphql/basics/advanced#make-multiple-queries-in-one-request) to name the results. This example returns the ID and title for each product.

  #### Query

  ```graphql
  query {
    newestProducts: products(first: 5, reverse: true) {
      edges {
        node {
          id
          title
        }
      }
    }
    oldestProducts: products(first: 5) {
      edges {
        node {
          id
          title
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
  "query": "query { newestProducts: products(first: 5, reverse: true) { edges { node { id title } } } oldestProducts: products(first: 5) { edges { node { id title } } } }"
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
      newestProducts: products(first: 5, reverse: true) {
        edges {
          node {
            id
            title
          }
        }
      }
      oldestProducts: products(first: 5) {
        edges {
          node {
            id
            title
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
      newestProducts: products(first: 5, reverse: true) {
        edges {
          node {
            id
            title
          }
        }
      }
      oldestProducts: products(first: 5) {
        edges {
          node {
            id
            title
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
      newestProducts: products(first: 5, reverse: true) {
        edges {
          node {
            id
            title
          }
        }
      }
      oldestProducts: products(first: 5) {
        edges {
          node {
            id
            title
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
    newestProducts: products(first: 5, reverse: true) {
      edges {
        node {
          id
          title
        }
      }
    }
    oldestProducts: products(first: 5) {
      edges {
        node {
          id
          title
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "newestProducts": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Product/912855135",
            "title": "SEO Boots"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/910489600",
            "title": "Crafty Shoes"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/558169081",
            "title": "Unpublished Boots"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/440089423",
            "title": "IPod Nano - 8GB"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/121709582",
            "title": "Boots"
          }
        }
      ]
    },
    "oldestProducts": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Product/20995642",
            "title": "Element"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/108828309",
            "title": "Draft"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/121709582",
            "title": "Boots"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/440089423",
            "title": "IPod Nano - 8GB"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/558169081",
            "title": "Unpublished Boots"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve product IDs from published products

  #### Description

  Retrieve the IDs of the first two products that are published to your app. This example returns the product ID and whether the product is published to your app. You must have the \`read\_product\_listings\` access scope to return publication information.

  #### Query

  ```graphql
  query ProductList {
    products(first: 2) {
      nodes {
        publishedOnCurrentPublication
        id
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
  "query": "query ProductList { products(first: 2) { nodes { publishedOnCurrentPublication id } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query ProductList {
      products(first: 2) {
        nodes {
          publishedOnCurrentPublication
          id
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
    query ProductList {
      products(first: 2) {
        nodes {
          publishedOnCurrentPublication
          id
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
    data: `query ProductList {
      products(first: 2) {
        nodes {
          publishedOnCurrentPublication
          id
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ProductList {
    products(first: 2) {
      nodes {
        publishedOnCurrentPublication
        id
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "products": {
      "nodes": [
        {
          "publishedOnCurrentPublication": true,
          "id": "gid://shopify/Product/20995642"
        },
        {
          "publishedOnCurrentPublication": true,
          "id": "gid://shopify/Product/108828309"
        }
      ]
    }
  }
  ```

* ### Retrieve products by their ID using aliases

  #### Description

  This example demonstrates using \[aliases]\(https://shopify.dev/docs/apps/build/graphql/basics/advanced#make-multiple-queries-in-one-request) to retrieve multiple products in a single query.

  #### Query

  ```graphql
  query {
    glasses: product(id: "gid://shopify/Product/108828309") {
      title
      description
    }
    shoes: product(id: "gid://shopify/Product/910489600") {
      title
      description
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
  "query": "query { glasses: product(id: \"gid://shopify/Product/108828309\") { title description } shoes: product(id: \"gid://shopify/Product/910489600\") { title description } }"
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
      glasses: product(id: "gid://shopify/Product/108828309") {
        title
        description
      }
      shoes: product(id: "gid://shopify/Product/910489600") {
        title
        description
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
      glasses: product(id: "gid://shopify/Product/108828309") {
        title
        description
      }
      shoes: product(id: "gid://shopify/Product/910489600") {
        title
        description
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
      glasses: product(id: "gid://shopify/Product/108828309") {
        title
        description
      }
      shoes: product(id: "gid://shopify/Product/910489600") {
        title
        description
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    glasses: product(id: "gid://shopify/Product/108828309") {
      title
      description
    }
    shoes: product(id: "gid://shopify/Product/910489600") {
      title
      description
    }
  }'
  ```

  #### Response

  ```json
  {
    "glasses": {
      "title": "Cool Glasses",
      "description": "Cool Glasses"
    },
    "shoes": {
      "title": "Crafty Shoes",
      "description": "Crafty Shoes"
    }
  }
  ```

* ### Retrieve the first ten products after a given cursor

  #### Description

  Retrieve the first ten products after a given cursor and whether there's a subsequent page of results. This example returns the cursor for the next page of results. Learn more about \[pagination]\(https://shopify.dev/docs/api/usage/pagination-graphql).

  #### Query

  ```graphql
  query {
    products(first: 10, after: "eyJsYXN0X2lkIjoyMDk5NTY0MiwibGFzdF92YWx1ZSI6IjIwOTk1NjQyIn0=") {
      edges {
        node {
          id
          title
          handle
        }
        cursor
      }
      pageInfo {
        hasNextPage
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
  "query": "query { products(first: 10, after: \"eyJsYXN0X2lkIjoyMDk5NTY0MiwibGFzdF92YWx1ZSI6IjIwOTk1NjQyIn0=\") { edges { node { id title handle } cursor } pageInfo { hasNextPage } } }"
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
      products(first: 10, after: "eyJsYXN0X2lkIjoyMDk5NTY0MiwibGFzdF92YWx1ZSI6IjIwOTk1NjQyIn0=") {
        edges {
          node {
            id
            title
            handle
          }
          cursor
        }
        pageInfo {
          hasNextPage
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
      products(first: 10, after: "eyJsYXN0X2lkIjoyMDk5NTY0MiwibGFzdF92YWx1ZSI6IjIwOTk1NjQyIn0=") {
        edges {
          node {
            id
            title
            handle
          }
          cursor
        }
        pageInfo {
          hasNextPage
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
      products(first: 10, after: "eyJsYXN0X2lkIjoyMDk5NTY0MiwibGFzdF92YWx1ZSI6IjIwOTk1NjQyIn0=") {
        edges {
          node {
            id
            title
            handle
          }
          cursor
        }
        pageInfo {
          hasNextPage
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
    products(first: 10, after: "eyJsYXN0X2lkIjoyMDk5NTY0MiwibGFzdF92YWx1ZSI6IjIwOTk1NjQyIn0=") {
      edges {
        node {
          id
          title
          handle
        }
        cursor
      }
      pageInfo {
        hasNextPage
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "products": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Product/108828309",
            "title": "Draft",
            "handle": "draft"
          },
          "cursor": "eyJsYXN0X2lkIjoxMDg4MjgzMDksImxhc3RfdmFsdWUiOiIxMDg4MjgzMDkifQ=="
        },
        {
          "node": {
            "id": "gid://shopify/Product/121709582",
            "title": "Boots",
            "handle": "boots"
          },
          "cursor": "eyJsYXN0X2lkIjoxMjE3MDk1ODIsImxhc3RfdmFsdWUiOiIxMjE3MDk1ODIifQ=="
        },
        {
          "node": {
            "id": "gid://shopify/Product/440089423",
            "title": "IPod Nano - 8GB",
            "handle": "ipod-nano"
          },
          "cursor": "eyJsYXN0X2lkIjo0NDAwODk0MjMsImxhc3RfdmFsdWUiOiI0NDAwODk0MjMifQ=="
        },
        {
          "node": {
            "id": "gid://shopify/Product/558169081",
            "title": "Unpublished Boots",
            "handle": "unpublished_boots"
          },
          "cursor": "eyJsYXN0X2lkIjo1NTgxNjkwODEsImxhc3RfdmFsdWUiOiI1NTgxNjkwODEifQ=="
        },
        {
          "node": {
            "id": "gid://shopify/Product/910489600",
            "title": "Crafty Shoes",
            "handle": "crappy-shoes"
          },
          "cursor": "eyJsYXN0X2lkIjo5MTA0ODk2MDAsImxhc3RfdmFsdWUiOiI5MTA0ODk2MDAifQ=="
        },
        {
          "node": {
            "id": "gid://shopify/Product/912855135",
            "title": "SEO Boots",
            "handle": "seo_boots"
          },
          "cursor": "eyJsYXN0X2lkIjo5MTI4NTUxMzUsImxhc3RfdmFsdWUiOiI5MTI4NTUxMzUifQ=="
        }
      ],
      "pageInfo": {
        "hasNextPage": false
      }
    }
  }
  ```

* ### Retrieve the first ten products associated with a product type

  #### Description

  Retrieve the first ten products associated with the snowboards product type. A \[product type]\(https://help.shopify.com/manual/products/details/product-type) is a category that you can use to group products. Learn more about using \[Shopify API search syntax]\(https://shopify.dev/docs/api/usage/search-syntax) to filter products.

  #### Query

  ```graphql
  query {
    products(first: 10, query: "product_type:snowboards") {
      edges {
        node {
          title
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
  "query": "query { products(first: 10, query: \"product_type:snowboards\") { edges { node { title } } } }"
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
      products(first: 10, query: "product_type:snowboards") {
        edges {
          node {
            title
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
      products(first: 10, query: "product_type:snowboards") {
        edges {
          node {
            title
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
      products(first: 10, query: "product_type:snowboards") {
        edges {
          node {
            title
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
    products(first: 10, query: "product_type:snowboards") {
      edges {
        node {
          title
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "products": {
      "edges": [
        {
          "node": {
            "title": "Element"
          }
        },
        {
          "node": {
            "title": "Draft"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the first ten products updated after a specified date

  #### Description

  Retrieve the first ten products updated after 2019-12-01. This example returns the ID and updated date for each product. Learn more about using \[Shopify API search syntax]\(https://shopify.dev/docs/api/usage/search-syntax) to filter products.

  #### Query

  ```graphql
  query {
    products(first: 10, query: "updated_at:>2019-12-01") {
      edges {
        node {
          id
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
  "query": "query { products(first: 10, query: \"updated_at:>2019-12-01\") { edges { node { id updatedAt } } } }"
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
      products(first: 10, query: "updated_at:>2019-12-01") {
        edges {
          node {
            id
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
      products(first: 10, query: "updated_at:>2019-12-01") {
        edges {
          node {
            id
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
      products(first: 10, query: "updated_at:>2019-12-01") {
        edges {
          node {
            id
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
    products(first: 10, query: "updated_at:>2019-12-01") {
      edges {
        node {
          id
          updatedAt
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "products": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Product/440089423",
            "updatedAt": "2021-12-01T12:14:52Z"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the ten most recently created products

  #### Description

  Retrieve the ten most recently created products and the \[publication]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication) information for each product. You must have the \`read\_product\_listings\` access scope to return publication information.

  #### Query

  ```graphql
  query {
    products(first: 10, reverse: true) {
      edges {
        node {
          id
          title
          handle
          resourcePublicationOnCurrentPublication {
            publication {
              id
            }
            publishDate
            isPublished
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
  "query": "query { products(first: 10, reverse: true) { edges { node { id title handle resourcePublicationOnCurrentPublication { publication { id } publishDate isPublished } } } } }"
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
      products(first: 10, reverse: true) {
        edges {
          node {
            id
            title
            handle
            resourcePublicationOnCurrentPublication {
              publication {
                id
              }
              publishDate
              isPublished
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
      products(first: 10, reverse: true) {
        edges {
          node {
            id
            title
            handle
            resourcePublicationOnCurrentPublication {
              publication {
                id
              }
              publishDate
              isPublished
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
      products(first: 10, reverse: true) {
        edges {
          node {
            id
            title
            handle
            resourcePublicationOnCurrentPublication {
              publication {
                id
              }
              publishDate
              isPublished
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
    products(first: 10, reverse: true) {
      edges {
        node {
          id
          title
          handle
          resourcePublicationOnCurrentPublication {
            publication {
              id
            }
            publishDate
            isPublished
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "products": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Product/912855135",
            "title": "SEO Boots",
            "handle": "seo_boots",
            "resourcePublicationOnCurrentPublication": null
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/910489600",
            "title": "Crafty Shoes",
            "handle": "crappy-shoes",
            "resourcePublicationOnCurrentPublication": null
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/558169081",
            "title": "Unpublished Boots",
            "handle": "unpublished_boots",
            "resourcePublicationOnCurrentPublication": null
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/440089423",
            "title": "IPod Nano - 8GB",
            "handle": "ipod-nano",
            "resourcePublicationOnCurrentPublication": null
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/121709582",
            "title": "Boots",
            "handle": "boots",
            "resourcePublicationOnCurrentPublication": null
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/108828309",
            "title": "Draft",
            "handle": "draft",
            "resourcePublicationOnCurrentPublication": {
              "publication": {
                "id": "gid://shopify/Publication/762454635"
              },
              "publishDate": "2005-01-02T00:00:00Z",
              "isPublished": true
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/Product/20995642",
            "title": "Element",
            "handle": "element",
            "resourcePublicationOnCurrentPublication": null
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the total inventory and price range of products

  #### Description

  Retrieve the total inventory and price range of three products using a fragment. The example returns the minimum and maximum variant prices and total inventory count for each product. Learn more about \[fragments]\(https://shopify.dev/docs/apps/build/graphql/basics/advanced#inline-fragments).

  #### Query

  ```graphql
  query {
    Glasses: product(id: "gid://shopify/Product/20995642") {
      ...productInformation
    }
    Shoes: product(id: "gid://shopify/Product/910489600") {
      ...productInformation
    }
    Bracelet: product(id: "gid://shopify/Product/108828309") {
      ...productInformation
    }
  }

  fragment productInformation on Product {
    totalInventory
    priceRangeV2 {
      minVariantPrice {
        amount
      }
      maxVariantPrice {
        amount
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
  "query": "query { Glasses: product(id: \"gid://shopify/Product/20995642\") { ...productInformation } Shoes: product(id: \"gid://shopify/Product/910489600\") { ...productInformation } Bracelet: product(id: \"gid://shopify/Product/108828309\") { ...productInformation } } fragment productInformation on Product { totalInventory priceRangeV2 { minVariantPrice { amount } maxVariantPrice { amount } } }"
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
      Glasses: product(id: "gid://shopify/Product/20995642") {
        ...productInformation
      }
      Shoes: product(id: "gid://shopify/Product/910489600") {
        ...productInformation
      }
      Bracelet: product(id: "gid://shopify/Product/108828309") {
        ...productInformation
      }
    }
    
    fragment productInformation on Product {
      totalInventory
      priceRangeV2 {
        minVariantPrice {
          amount
        }
        maxVariantPrice {
          amount
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
      Glasses: product(id: "gid://shopify/Product/20995642") {
        ...productInformation
      }
      Shoes: product(id: "gid://shopify/Product/910489600") {
        ...productInformation
      }
      Bracelet: product(id: "gid://shopify/Product/108828309") {
        ...productInformation
      }
    }
    
    fragment productInformation on Product {
      totalInventory
      priceRangeV2 {
        minVariantPrice {
          amount
        }
        maxVariantPrice {
          amount
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
      Glasses: product(id: "gid://shopify/Product/20995642") {
        ...productInformation
      }
      Shoes: product(id: "gid://shopify/Product/910489600") {
        ...productInformation
      }
      Bracelet: product(id: "gid://shopify/Product/108828309") {
        ...productInformation
      }
    }
    
    fragment productInformation on Product {
      totalInventory
      priceRangeV2 {
        minVariantPrice {
          amount
        }
        maxVariantPrice {
          amount
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
    Glasses: product(id: "gid://shopify/Product/20995642") {
      ...productInformation
    }
    Shoes: product(id: "gid://shopify/Product/910489600") {
      ...productInformation
    }
    Bracelet: product(id: "gid://shopify/Product/108828309") {
      ...productInformation
    }
  }

  fragment productInformation on Product {
    totalInventory
    priceRangeV2 {
      minVariantPrice {
        amount
      }
      maxVariantPrice {
        amount
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "Glasses": {
      "totalInventory": 19,
      "priceRangeV2": {
        "minVariantPrice": {
          "amount": "10.0"
        },
        "maxVariantPrice": {
          "amount": "15.0"
        }
      }
    },
    "Shoes": {
      "totalInventory": 4000,
      "priceRangeV2": {
        "minVariantPrice": {
          "amount": "100.0"
        },
        "maxVariantPrice": {
          "amount": "100.0"
        }
      }
    },
    "Bracelet": {
      "totalInventory": 1,
      "priceRangeV2": {
        "minVariantPrice": {
          "amount": "10.0"
        },
        "maxVariantPrice": {
          "amount": "10.0"
        }
      }
    }
  }
  ```
