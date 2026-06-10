---
title: productVariants - GraphQL Admin
description: >-
  Retrieves a list of [product
  variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)

  associated with a
  [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product).


  A product variant is a specific version of a product that comes in more than

  one
  [option](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption),

  such as size or color. For example, if a merchant sells t-shirts with options
  for size and color,

  then a small, blue t-shirt would be one product variant and a large, blue
  t-shirt would be another.


  Use the `productVariants` query when you need to:


  - Search for product variants by attributes such as SKU, barcode, or inventory
  quantity.

  - Filter product variants by attributes, such as whether they're gift cards or
  have custom metafields.

  - Fetch product variants for bulk operations, such as updating prices or
  inventory.

  - Preload data for product variants, such as inventory items, selected
  options, or associated products.


  The `productVariants` query supports
  [pagination](https://shopify.dev/docs/api/usage/pagination-graphql)

  to handle large product catalogs and [saved
  searches](https://shopify.dev/docs/api/admin-graphql/latest/queries/productVariants#arguments-savedSearchId)

  for frequently used product variant queries.


  The `productVariants` query returns product variants with their associated
  metadata, including:


  - Basic product variant information (for example, title, SKU, barcode, price,
  and inventory)

  - Media attachments (for example, images and videos)

  - Associated products, selling plans, bundles, and metafields


  Learn more about working with [Shopify's product
  model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/product-model-components).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/productVariants'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/productVariants.md'
---

# product​Variants

query

Retrieves a list of [product variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) associated with a [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product).

A product variant is a specific version of a product that comes in more than one [option](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption), such as size or color. For example, if a merchant sells t-shirts with options for size and color, then a small, blue t-shirt would be one product variant and a large, blue t-shirt would be another.

Use the `productVariants` query when you need to:

* Search for product variants by attributes such as SKU, barcode, or inventory quantity.
* Filter product variants by attributes, such as whether they're gift cards or have custom metafields.
* Fetch product variants for bulk operations, such as updating prices or inventory.
* Preload data for product variants, such as inventory items, selected options, or associated products.

The `productVariants` query supports [pagination](https://shopify.dev/docs/api/usage/pagination-graphql) to handle large product catalogs and [saved searches](https://shopify.dev/docs/api/admin-graphql/latest/queries/productVariants#arguments-savedSearchId) for frequently used product variant queries.

The `productVariants` query returns product variants with their associated metadata, including:

* Basic product variant information (for example, title, SKU, barcode, price, and inventory)
* Media attachments (for example, images and videos)
* Associated products, selling plans, bundles, and metafields

Learn more about working with [Shopify's product model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/product-model-components).

## ProductVariantConnection arguments

[ProductVariantConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductVariantConnection)

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

    * collection

      string

    * delivery\_profile\_id

      id

    * exclude\_composite

      boolean

    * exclude\_variants\_with\_components

      boolean

    * gift\_card

      boolean

    * id

      id

    * inventory\_quantity

      integer

    * location\_id

      id

    * managed

      boolean

    * managed\_by

      string

    * option1

      string

    * option2

      string

    * option3

      string

    * product\_id

      id

    * product\_ids

      string

    * product\_publication\_status

      string

    * product\_status

      string

    * product\_type

      string

    * publishable\_status

      string

    * published\_status

      string

    * requires\_components

      boolean

    * sku

      string

    * tag

      string

    * tag\_not

      string

    * taxable

      boolean

    * title

      string

    * updated\_at

      time

    * vendor

      string

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      Filter by the product variant [`barcode`](https://shopify.dev/api/admin-graphql/latest/objects/ProductVariant#field-barcode) field.

    - Example:

      * `barcode:ABC-abc-123`

      Filter by the [ID of the collection](https://shopify.dev/api/admin-graphql/latest/objects/Collection#field-id) that the product variant belongs to.

    - Example:

      * `collection:465903092033`

      Filter by the product variant [delivery profile ID](https://shopify.dev/api/admin-graphql/latest/objects/ProductVariant#field-deliveryprofile) (`ProductVariant.deliveryProfile.id`).

    - Example:

      * `delivery_profile_id:108179161409`

      Filter by product variants that aren't composites.

    - Example:

      * `exclude_composite:true`

      Filter by whether there are [components](https://shopify.dev/docs/apps/build/product-merchandising/bundles/add-product-fixed-bundle) that are associated with the product variants in a bundle.

    - Example:

      * `exclude_variants_with_components:true`

      Filter by the product [`isGiftCard`](https://shopify.dev/api/admin-graphql/latest/objects/Product#field-isgiftcard) field.

    - Example:

      * `gift_card:true`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by an aggregate of inventory across all locations where the product variant is stocked.

    - Example:

      * `inventory_quantity:10`

      Filter by the [location ID](https://shopify.dev/api/admin-graphql/latest/objects/Location#field-id) for the product variant.

    - Example:

      * `location_id:88511152449`

      Filter by whether there is fulfillment service tracking associated with the product variants.

    - Example:

      * `managed:true`

      Filter by the fulfillment service that tracks the number of items in stock for the product variant.

    - Example:

      * `managed_by:shopify`

      Filter by a custom property that a shop owner uses to define product variants.

    - Example:

      * `option1:small`

      Filter by a custom property that a shop owner uses to define product variants.

    - Example:

      * `option2:medium`

      Filter by a custom property that a shop owner uses to define product variants.

    - Example:

      * `option3:large`

      Filter by the product [`id`](https://shopify.dev/api/admin-graphql/latest/objects/Product#field-id) field.

    - Example:

      * `product_id:8474977763649`

      Filter by a comma-separated list of product [IDs](https://shopify.dev/api/admin-graphql/latest/objects/Product#field-id).

    - Example:

      * `product_ids:8474977763649,8474977796417`

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

      Filter by a comma-separated list of product [statuses](https://shopify.dev/api/admin-graphql/latest/objects/Product#field-status).

    - Example:

      * `product_status:ACTIVE,DRAFT`

      Filter by the product type that's associated with the product variants.

    - Example:

      * `product_type:snowboard`

      **Deprecated:** This parameter is deprecated as of 2025-12 and will be removed in a future API version. Use [published\_status](https://shopify.dev/api/admin-graphql/latest/queries/products#argument-query-filter-publishable_status) for visibility checks. Filter by the publishable status of the resource on a channel. The value is a composite of the [channel `app` ID](https://shopify.dev/api/admin-graphql/latest/objects/Channel#app-price) (`Channel.app.id`) and one of the valid status values.

    - Valid values:

      * `* {channel_app_id}-unset`
      * `* {channel_app_id}-pending`
      * `* {channel_app_id}-approved`
      * `* {channel_app_id}-not_approved`

      Example:

      * `publishable_status:580111-unset`
      * `publishable_status:580111-pending`

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

      Filter by whether the product variant can only be purchased with components. [Learn more](https://shopify.dev/apps/build/product-merchandising/bundles#store-eligibility).

    - Example:

      * `requires_components:true`

      Filter by the product variant [`sku`](https://shopify.dev/api/admin-graphql/latest/objects/ProductVariant#field-sku) field. [Learn more about SKUs](https://help.shopify.com/manual/products/details/sku).

    - Example:

      * `sku:XYZ-12345`

      Filter objects by the `tag` field.

    - Example:

      * `tag:my_tag`

      Filter by objects that don’t have the specified tag.

    - Example:

      * `tag_not:my_tag`

      Filter by the product variant [`taxable`](https://shopify.dev/api/admin-graphql/latest/objects/ProductVariant#field-taxable) field.

    - Example:

      * `taxable:false`

      Filter by the product variant [`title`](https://shopify.dev/api/admin-graphql/latest/objects/ProductVariant#field-title) field.

    - Example:

      * `title:ice`

      Filter by date and time when the product variant was updated.

    - Example:

      * `updated_at:>2020-10-21T23:39:20Z`
      * `updated_at:<now`
      * `updated_at:<=2024`

      Filter by the origin or source of the product variant. Learn more about [vendors and managing vendor information](https://help.shopify.com/manual/products/managing-vendor-info).

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

  [Product​Variant​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductVariantSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Product​Variant​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariantEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Product​Variant!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)

  non-null

  A list of nodes that are contained in ProductVariantEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve a list of product variants for a product

  #### Description

  Retrieve the first ten product variants for a product. The example returns the IDs and titles of the product variants. The \`pageInfo\` field is also included, which contains \[pagination]\(https://shopify.dev/docs/api/usage/pagination-graphql) information. Learn more about using \[Shopify API search syntax]\(https://shopify.dev/docs/api/usage/search-syntax) to filter products.

  #### Query

  ```graphql
  query ProductVariantsList {
    productVariants(first: 10, query: "product_id:20995642") {
      nodes {
        id
        title
      }
      pageInfo {
        startCursor
        endCursor
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
  "query": "query ProductVariantsList { productVariants(first: 10, query: \"product_id:20995642\") { nodes { id title } pageInfo { startCursor endCursor } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query ProductVariantsList {
      productVariants(first: 10, query: "product_id:20995642") {
        nodes {
          id
          title
        }
        pageInfo {
          startCursor
          endCursor
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
    query ProductVariantsList {
      productVariants(first: 10, query: "product_id:20995642") {
        nodes {
          id
          title
        }
        pageInfo {
          startCursor
          endCursor
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
    data: `query ProductVariantsList {
      productVariants(first: 10, query: "product_id:20995642") {
        nodes {
          id
          title
        }
        pageInfo {
          startCursor
          endCursor
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ProductVariantsList {
    productVariants(first: 10, query: "product_id:20995642") {
      nodes {
        id
        title
      }
      pageInfo {
        startCursor
        endCursor
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "productVariants": {
      "nodes": [
        {
          "id": "gid://shopify/ProductVariant/30322695",
          "title": "151cm"
        },
        {
          "id": "gid://shopify/ProductVariant/113711323",
          "title": "155cm"
        },
        {
          "id": "gid://shopify/ProductVariant/236948360",
          "title": "158cm"
        }
      ],
      "pageInfo": {
        "startCursor": "eyJsYXN0X2lkIjozMDMyMjY5NSwibGFzdF92YWx1ZSI6IjMwMzIyNjk1In0=",
        "endCursor": "eyJsYXN0X2lkIjoyMzY5NDgzNjAsImxhc3RfdmFsdWUiOiIyMzY5NDgzNjAifQ=="
      }
    }
  }
  ```

* ### Retrieve product variants by SKU pattern

  #### Description

  Retrieve product variants using a \[SKU]\(https://help.shopify.com/manual/products/details/sku) pattern. This example uses a wildcard search to find all product variants with SKUs that start with "element". The \`\*\` wildcard allows you to find multiple variants that share a common SKU prefix, which is useful for finding related products or product lines. Learn more about using \[Shopify API search syntax]\(https://shopify.dev/docs/api/usage/search-syntax) to filter products.

  #### Query

  ```graphql
  query {
    productVariants(first: 10, query: "sku:element*") {
      edges {
        node {
          id
          title
          sku
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
  "query": "query { productVariants(first: 10, query: \"sku:element*\") { edges { node { id title sku } } } }"
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
      productVariants(first: 10, query: "sku:element*") {
        edges {
          node {
            id
            title
            sku
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
      productVariants(first: 10, query: "sku:element*") {
        edges {
          node {
            id
            title
            sku
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
      productVariants(first: 10, query: "sku:element*") {
        edges {
          node {
            id
            title
            sku
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
    productVariants(first: 10, query: "sku:element*") {
      edges {
        node {
          id
          title
          sku
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "productVariants": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/ProductVariant/30322695",
            "title": "151cm",
            "sku": "element-151"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/113711323",
            "title": "155cm",
            "sku": "element-155"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/236948360",
            "title": "158cm",
            "sku": "element-158"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve product variants by available quantity at a location

  #### Description

  Retrieve the first three product variants stocked at a location, sorted by lowest available quantity. This example returns the IDs and inventory quantities of the product variants. Learn more about using \[Shopify API search syntax]\(https://shopify.dev/docs/api/usage/search-syntax) to filter products.

  #### Query

  ```graphql
  query {
    productVariants(first: 3, query: "location_id:124656943", sortKey: INVENTORY_LEVELS_AVAILABLE) {
      edges {
        node {
          id
          inventoryItem {
            inventoryLevel(locationId: "gid://shopify/Location/124656943") {
              quantities(names: "available") {
                quantity
                name
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
  "query": "query { productVariants(first: 3, query: \"location_id:124656943\", sortKey: INVENTORY_LEVELS_AVAILABLE) { edges { node { id inventoryItem { inventoryLevel(locationId: \"gid://shopify/Location/124656943\") { quantities(names: \"available\") { quantity name } } } } } } }"
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
      productVariants(first: 3, query: "location_id:124656943", sortKey: INVENTORY_LEVELS_AVAILABLE) {
        edges {
          node {
            id
            inventoryItem {
              inventoryLevel(locationId: "gid://shopify/Location/124656943") {
                quantities(names: "available") {
                  quantity
                  name
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
    query {
      productVariants(first: 3, query: "location_id:124656943", sortKey: INVENTORY_LEVELS_AVAILABLE) {
        edges {
          node {
            id
            inventoryItem {
              inventoryLevel(locationId: "gid://shopify/Location/124656943") {
                quantities(names: "available") {
                  quantity
                  name
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
    data: `query {
      productVariants(first: 3, query: "location_id:124656943", sortKey: INVENTORY_LEVELS_AVAILABLE) {
        edges {
          node {
            id
            inventoryItem {
              inventoryLevel(locationId: "gid://shopify/Location/124656943") {
                quantities(names: "available") {
                  quantity
                  name
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
  'query {
    productVariants(first: 3, query: "location_id:124656943", sortKey: INVENTORY_LEVELS_AVAILABLE) {
      edges {
        node {
          id
          inventoryItem {
            inventoryLevel(locationId: "gid://shopify/Location/124656943") {
              quantities(names: "available") {
                quantity
                name
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
    "productVariants": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/ProductVariant/419425742",
            "inventoryItem": {
              "inventoryLevel": {
                "quantities": [
                  {
                    "quantity": 0,
                    "name": "available"
                  }
                ]
              }
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/30322695",
            "inventoryItem": {
              "inventoryLevel": {
                "quantities": [
                  {
                    "quantity": 1,
                    "name": "available"
                  }
                ]
              }
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/43729076",
            "inventoryItem": {
              "inventoryLevel": {
                "quantities": [
                  {
                    "quantity": 1,
                    "name": "available"
                  }
                ]
              }
            }
          }
        }
      ]
    }
  }
  ```

* ### Retrieve product variants by product IDs

  #### Description

  Retrieve product variants for a specific set of product IDs using the \`product\_ids\` query parameter. This example returns the IDs and titles of the product variants for the specified products. The \`product\` field is also included, which contains the ID of the product that's associated with the product variant. Learn more about using \[Shopify API search syntax]\(https://shopify.dev/docs/api/usage/search-syntax) to filter products.

  #### Query

  ```graphql
  query {
    productVariants(first: 100, query: "product_ids:20995642,108828309") {
      edges {
        node {
          id
          title
          product {
            id
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
  "query": "query { productVariants(first: 100, query: \"product_ids:20995642,108828309\") { edges { node { id title product { id } } } } }"
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
      productVariants(first: 100, query: "product_ids:20995642,108828309") {
        edges {
          node {
            id
            title
            product {
              id
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
      productVariants(first: 100, query: "product_ids:20995642,108828309") {
        edges {
          node {
            id
            title
            product {
              id
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
      productVariants(first: 100, query: "product_ids:20995642,108828309") {
        edges {
          node {
            id
            title
            product {
              id
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
    productVariants(first: 100, query: "product_ids:20995642,108828309") {
      edges {
        node {
          id
          title
          product {
            id
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "productVariants": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/ProductVariant/30322695",
            "title": "151cm",
            "product": {
              "id": "gid://shopify/Product/20995642"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/43729076",
            "title": "151cm",
            "product": {
              "id": "gid://shopify/Product/108828309"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/113711323",
            "title": "155cm",
            "product": {
              "id": "gid://shopify/Product/20995642"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/236948360",
            "title": "158cm",
            "product": {
              "id": "gid://shopify/Product/20995642"
            }
          }
        }
      ]
    }
  }
  ```

* ### Retrieve product variants by publication statuses

  #### Description

  Retrieve product variants by \`published\_status\` and \`product\_publication\_status\`. This example returns the title and \[SKU]\(https://help.shopify.com/manual/products/details/sku) of product variants that are both published and approved. A product variant is \`published\` when it's visible and available for purchase on a sales channel, such as the Online Store. A product variant is \`approved\` when it has passed any content review or approval workflows configured for the store. Learn more about using \[Shopify API search syntax]\(https://shopify.dev/docs/api/usage/search-syntax) to filter products.

  #### Query

  ```graphql
  query {
    productVariants(first: 1, query: "published_status:published AND product_publication_status:approved") {
      edges {
        node {
          title
          sku
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
  "query": "query { productVariants(first: 1, query: \"published_status:published AND product_publication_status:approved\") { edges { node { title sku } } } }"
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
      productVariants(first: 1, query: "published_status:published AND product_publication_status:approved") {
        edges {
          node {
            title
            sku
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
      productVariants(first: 1, query: "published_status:published AND product_publication_status:approved") {
        edges {
          node {
            title
            sku
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
      productVariants(first: 1, query: "published_status:published AND product_publication_status:approved") {
        edges {
          node {
            title
            sku
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
    productVariants(first: 1, query: "published_status:published AND product_publication_status:approved") {
      edges {
        node {
          title
          sku
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "productVariants": {
      "edges": [
        {
          "node": {
            "title": "151cm",
            "sku": "element-151"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the IDs of the first 10 product variants

  #### Description

  Retrieve the first 10 product variants in a store. The example returns the IDs of the product variants.

  #### Query

  ```graphql
  query {
    productVariants(first: 10) {
      edges {
        node {
          id
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
  "query": "query { productVariants(first: 10) { edges { node { id } } } }"
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
      productVariants(first: 10) {
        edges {
          node {
            id
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
      productVariants(first: 10) {
        edges {
          node {
            id
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
      productVariants(first: 10) {
        edges {
          node {
            id
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
    productVariants(first: 10) {
      edges {
        node {
          id
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "productVariants": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/ProductVariant/30322695"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/43729076"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/113711323"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/138327650"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/236948360"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/330284860"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/389013007"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/419425742"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/438458761"
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/445365074"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the first three product variants updated after a specified date

  #### Description

  Retrieve the first three products updated after 2021-01-01. This example returns the IDs, titles, prices, inventory quantities, and the date and time the product variant was last updated. The \`product\` field is also included, which contains the ID and title of the product that's associated with the product variant. Learn more about using \[Shopify API search syntax]\(https://shopify.dev/docs/api/usage/search-syntax) to filter products.

  #### Query

  ```graphql
  query {
    productVariants(first: 3, query: "updated_at:>2021-01-01") {
      edges {
        node {
          id
          title
          price
          updatedAt
          inventoryQuantity
          product {
            id
            title
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
  "query": "query { productVariants(first: 3, query: \"updated_at:>2021-01-01\") { edges { node { id title price updatedAt inventoryQuantity product { id title } } } } }"
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
      productVariants(first: 3, query: "updated_at:>2021-01-01") {
        edges {
          node {
            id
            title
            price
            updatedAt
            inventoryQuantity
            product {
              id
              title
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
      productVariants(first: 3, query: "updated_at:>2021-01-01") {
        edges {
          node {
            id
            title
            price
            updatedAt
            inventoryQuantity
            product {
              id
              title
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
      productVariants(first: 3, query: "updated_at:>2021-01-01") {
        edges {
          node {
            id
            title
            price
            updatedAt
            inventoryQuantity
            product {
              id
              title
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
    productVariants(first: 3, query: "updated_at:>2021-01-01") {
      edges {
        node {
          id
          title
          price
          updatedAt
          inventoryQuantity
          product {
            id
            title
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "productVariants": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/ProductVariant/30322695",
            "title": "151cm",
            "price": "10.00",
            "updatedAt": "2021-11-11T11:11:11Z",
            "inventoryQuantity": 3,
            "product": {
              "id": "gid://shopify/Product/20995642",
              "title": "Element"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/43729076",
            "title": "151cm",
            "price": "10.00",
            "updatedAt": "2021-11-11T11:11:11Z",
            "inventoryQuantity": 1,
            "product": {
              "id": "gid://shopify/Product/108828309",
              "title": "Draft"
            }
          }
        },
        {
          "node": {
            "id": "gid://shopify/ProductVariant/113711323",
            "title": "155cm",
            "price": "15.00",
            "updatedAt": "2021-11-11T11:11:11Z",
            "inventoryQuantity": 15,
            "product": {
              "id": "gid://shopify/Product/20995642",
              "title": "Element"
            }
          }
        }
      ]
    }
  }
  ```
