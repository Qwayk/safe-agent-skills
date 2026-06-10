---
title: publication - GraphQL Admin
description: >-
  Retrieves a
  [`Publication`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication)
  by [`ID`](https://shopify.dev/docs/api/usage/gids).


  Returns `null` if the publication doesn't exist.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/publication'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/publication.md'
---

# publication

query

Retrieves a [`Publication`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication) by [`ID`](https://shopify.dev/docs/api/usage/gids).

Returns `null` if the publication doesn't exist.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the Publication to return.

***

## Possible returns

* Publication

  [Publication](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication)

  A group of [products](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) and [collections](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection) that are published to an app.

  Each publication manages which products and collections display on its associated [`Channel`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Channel). Merchants can automatically publish products when they're created if [`autoPublish`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication#field-Publication.fields.autoPublish) is enabled, or manually control publication through publication records.

  Publications support scheduled publishing through future publish dates for online store channels, allowing merchants to coordinate product launches and promotional campaigns. The [`catalog`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication#field-Publication.fields.catalog) field links to pricing and availability rules specific to that publication's context.

  * auto​Publish

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether new products are automatically published to this publication.

  * catalog

    [Catalog](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Catalog)

    The catalog associated with the publication.

  * collection​Publications​V3

    [Resource​Publication​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ResourcePublicationConnection)

    non-null

    The list of collection publication records, each representing the publication status and details for a collection published to this publication (typically channel).

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

  * collections

    [Collection​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CollectionConnection)

    non-null

    The list of collections published to the publication.

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

  * has​Collection

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the collection is available to the publication.

    * id

      [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      required

      ### Arguments

      Collection ID to check.

    ***

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * included​Products

    [Product​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductConnection)

    non-null

    The list of products included, but not necessarily published, in the publication.

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

      [Product​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

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

    * saved​Search​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

    ***

  * included​Products​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    The count of products included in the publication. Limited to a maximum of 10000 by default.

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      ### Arguments

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

    * saved​Search​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      The ID of an existing saved search. The search’s query string is used as the query argument. Refer to the [`SavedSearch`](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch) object.

    * limit

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      Default:10000

      The upper bound on count value before returning a result. Use `null` to have no limit.

    ***

  * operation

    [Publication​Operation](https://shopify.dev/docs/api/admin-graphql/latest/unions/PublicationOperation)

    A background operation associated with this publication.

  * product​Publications​V3

    [Resource​Publication​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ResourcePublicationConnection)

    non-null

    The product publications for the list of products published to the publication.

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

  * products

    [Product​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductConnection)

    non-null

    The list of products published to the publication.

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

      [Product​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

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

    * saved​Search​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

    ***

  * supports​Future​Publishing

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the publication supports future publishing.

  * app

    [App!](https://shopify.dev/docs/api/admin-graphql/latest/objects/App)

    non-nullDeprecated

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-nullDeprecated

***

## Examples

* ### Retrieve a publication that doesn't exist

  #### Description

  Retrieving a publication by an ID that doesn't exist returns \`null\`.

  #### Query

  ```graphql
  query publication($id: ID!) {
    publication(id: $id) {
      name
      collections(first: 5) {
        edges {
          node {
            id
            title
            updatedAt
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Publication/-1"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query publication($id: ID!) { publication(id: $id) { name collections(first: 5) { edges { node { id title updatedAt } } } } }",
   "variables": {
      "id": "gid://shopify/Publication/-1"
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
    query publication($id: ID!) {
      publication(id: $id) {
        name
        collections(first: 5) {
          edges {
            node {
              id
              title
              updatedAt
            }
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Publication/-1"
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
    query publication($id: ID!) {
      publication(id: $id) {
        name
        collections(first: 5) {
          edges {
            node {
              id
              title
              updatedAt
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Publication/-1"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query publication($id: ID!) {
        publication(id: $id) {
          name
          collections(first: 5) {
            edges {
              node {
                id
                title
                updatedAt
              }
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Publication/-1"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query publication($id: ID!) {
    publication(id: $id) {
      name
      collections(first: 5) {
        edges {
          node {
            id
            title
            updatedAt
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Publication/-1"
  }'
  ```

  #### Response

  ```json
  {
    "publication": null
  }
  ```

* ### Retrieve an existing publication

  #### Query

  ```graphql
  query publication($id: ID!) {
    publication(id: $id) {
      name
      collections(first: 5) {
        edges {
          node {
            id
            title
            updatedAt
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Publication/244171671"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query publication($id: ID!) { publication(id: $id) { name collections(first: 5) { edges { node { id title updatedAt } } } } }",
   "variables": {
      "id": "gid://shopify/Publication/244171671"
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
    query publication($id: ID!) {
      publication(id: $id) {
        name
        collections(first: 5) {
          edges {
            node {
              id
              title
              updatedAt
            }
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Publication/244171671"
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
    query publication($id: ID!) {
      publication(id: $id) {
        name
        collections(first: 5) {
          edges {
            node {
              id
              title
              updatedAt
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Publication/244171671"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query publication($id: ID!) {
        publication(id: $id) {
          name
          collections(first: 5) {
            edges {
              node {
                id
                title
                updatedAt
              }
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Publication/244171671"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query publication($id: ID!) {
    publication(id: $id) {
      name
      collections(first: 5) {
        edges {
          node {
            id
            title
            updatedAt
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Publication/244171671"
  }'
  ```

  #### Response

  ```json
  {
    "publication": {
      "name": "Online Store",
      "collections": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/Collection/79210309",
              "title": "Custom Other Items",
              "updatedAt": "2008-10-10T00:00:00Z"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Collection/94229130",
              "title": "All products more expensive than free",
              "updatedAt": "2006-02-02T00:00:00Z"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Collection/142458073",
              "title": "All snowboards",
              "updatedAt": "2006-02-02T00:00:00Z"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Collection/411960790",
              "title": "Bold snowboards",
              "updatedAt": "2006-02-02T00:00:00Z"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Collection/431528632",
              "title": "All arbor products tagged deepsnow",
              "updatedAt": "2006-02-02T00:00:00Z"
            }
          }
        ]
      }
    }
  }
  ```
