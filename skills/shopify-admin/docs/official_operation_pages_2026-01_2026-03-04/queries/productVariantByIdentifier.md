---
title: productVariantByIdentifier - GraphQL Admin
description: Return a product variant by an identifier.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/productVariantByIdentifier
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/productVariantByIdentifier.md
---

# product​Variant​By​Identifier

query

Requires `read_products` access scope.

Return a product variant by an identifier.

## Arguments

* identifier

  [Product​Variant​Identifier​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ProductVariantIdentifierInput)

  required

  The identifier of the product variant.

***

## Possible returns

* Product​Variant

  [Product​Variant](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant)

  The `ProductVariant` object represents a version of a [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) that comes in more than one [option](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption), such as size or color. For example, if a merchant sells t-shirts with options for size and color, then a small, blue t-shirt would be one product variant and a large, blue t-shirt would be another.

  Use the `ProductVariant` object to manage the full lifecycle and configuration of a product's variants. Common use cases for using the `ProductVariant` object include:

  * Tracking inventory for each variant
  * Setting unique prices for each variant
  * Assigning barcodes and SKUs to connect variants to fulfillment services
  * Attaching variant-specific images and media
  * Setting delivery and tax requirements
  * Supporting product bundles, subscriptions, and selling plans

  A `ProductVariant` is associated with a parent [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) object. `ProductVariant` serves as the central link between a product's merchandising configuration, inventory, pricing, fulfillment, and sales channels within the GraphQL Admin API schema. Each variant can reference other GraphQL types such as:

  * [`InventoryItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem): Used for inventory tracking
  * [`Image`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Image): Used for variant-specific images
  * [`SellingPlanGroup`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroup): Used for subscriptions and selling plans

  Learn more about [Shopify's product model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/product-model-components).

  * available​For​Sale

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the product variant is available for sale.

  * barcode

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The value of the barcode associated with the product.

  * compare​At​Price

    [Money](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    The compare-at price of the variant in the default shop currency.

  * contextual​Pricing

    [Product​Variant​Contextual​Pricing!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariantContextualPricing)

    non-null

    The pricing that applies for a customer in a given context. As of API version 2025-04, only active markets are considered in the price resolution.

    * context

      [Contextual​Pricing​Context!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ContextualPricingContext)

      required

      ### Arguments

      The context used to generate contextual pricing for the variant.

    ***

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the variant was created.

  * default​Cursor

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A default [cursor](https://shopify.dev/api/usage/pagination-graphql) that returns the single next record, sorted ascending by ID.

  * delivery​Profile

    [Delivery​Profile](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryProfile)

    The [delivery profile](https://shopify.dev/api/admin-graphql/latest/objects/DeliveryProfile) for the variant.

  * display​Name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    Display name of the variant, based on product's title + variant's title.

  * events

    [Event​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/EventConnection)

    non-null

    The paginated list of events associated with the host subject.

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

      [Event​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/EventSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

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

    ***

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * inventory​Item

    [Inventory​Item!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem)

    non-null

    The inventory item, which is used to query for inventory information.

  * inventory​Policy

    [Product​Variant​Inventory​Policy!](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductVariantInventoryPolicy)

    non-null

    Whether customers are allowed to place an order for the product variant when it's out of stock.

  * inventory​Quantity

    [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    The total sellable quantity of the variant.

  * legacy​Resource​Id

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The ID of the corresponding resource in the REST Admin API.

  * media

    [Media​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MediaConnection)

    non-null

    The media associated with the product variant.

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

  * metafield

    [Metafield](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metafield)

    A [custom field](https://shopify.dev/docs/apps/build/custom-data), including its `namespace` and `key`, that's associated with a Shopify resource for the purposes of adding and storing additional information.

    * namespace

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      ### Arguments

      The container the metafield belongs to. If omitted, the app-reserved namespace will be used.

    * key

      [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      required

      The key for the metafield.

    ***

  * metafields

    [Metafield​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MetafieldConnection)

    non-null

    A list of [custom fields](https://shopify.dev/docs/apps/build/custom-data) that a merchant associates with a Shopify resource.

    * namespace

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      ### Arguments

      The metafield namespace to filter by. If omitted, all metafields are returned.

    * keys

      [\[String!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      List of keys of metafields in the format `namespace.key`, will be returned in the same format.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

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

  * position

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The order of the product variant in the list of product variants. The first position in the list is 1.

  * price

    [Money!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    non-null

    The price of the product variant in the default shop currency.

  * product

    [Product!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

    non-null

    The product that this variant belongs to.

  * product​Parents

    [Product​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductConnection)

    non-null

    A list of products that have product variants that contain this variant as a product component.

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

    ***

  * product​Variant​Components

    [Product​Variant​Component​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductVariantComponentConnection)

    non-null

    A list of the product variant components.

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

  * requires​Components

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether a product variant requires components. The default value is `false`. If `true`, then the product variant can only be purchased as a parent bundle with components and it will be omitted from channels that don't support bundles.

  * selected​Options

    [\[Selected​Option!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SelectedOption)

    non-null

    List of product options applied to the variant.

  * sellable​Online​Quantity

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The total sellable quantity of the variant for online channels. This doesn't represent the total available inventory or capture [limitations based on customer location](https://help.shopify.com/manual/markets/inventory_and_fulfillment).

  * selling​Plan​Groups

    [Selling​Plan​Group​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SellingPlanGroupConnection)

    non-null

    A list of all selling plan groups defined in the current shop associated with the product variant.

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

  * selling​Plan​Groups​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    Count of selling plan groups associated with the product variant.

  * show​Unit​Price

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether to show the unit price for this product variant.

  * sku

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    A case-sensitive identifier for the product variant in the shop. Required in order to connect to a fulfillment service.

  * taxable

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether a tax is charged when the product variant is sold.

  * title

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The title of the product variant.

  * translations

    [\[Translation!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Translation)

    non-null

    The published translations associated with the resource.

    * locale

      [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      required

      ### Arguments

      Filters translations locale.

    * market​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      Filters translations by market ID. Use this argument to retrieve content specific to a market.

    ***

  * unit​Price

    [Money​V2](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyV2)

    The unit price value for the variant based on the variant measurement.

  * unit​Price​Measurement

    [Unit​Price​Measurement](https://shopify.dev/docs/api/admin-graphql/latest/objects/UnitPriceMeasurement)

    The unit price measurement for the variant.

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time (ISO 8601 format) when the product variant was last modified.

  * image

    [Image](https://shopify.dev/docs/api/admin-graphql/latest/objects/Image)

    Deprecated

    * max​Width

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      Deprecated

      ### Arguments

    * max​Height

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      Deprecated

    * crop

      [Crop​Region](https://shopify.dev/docs/api/admin-graphql/latest/enums/CropRegion)

      Deprecated

    * scale

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      DeprecatedDefault:1

    ***

  * metafield​Definitions

    [Metafield​Definition​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MetafieldDefinitionConnection)

    non-nullDeprecated

    * namespace

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      ### Arguments

      Filter metafield definitions by namespace.

    * pinned​Status

      [Metafield​Definition​Pinned​Status](https://shopify.dev/docs/api/admin-graphql/latest/enums/MetafieldDefinitionPinnedStatus)

      Default:ANY

      Filter by the definition's pinned status.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

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

      [Metafield​Definition​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/MetafieldDefinitionSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

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

    ***

  * presentment​Prices

    [Product​Variant​Price​Pair​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductVariantPricePairConnection)

    non-nullDeprecated

    * presentment​Currencies

      [\[Currency​Code!\]](https://shopify.dev/docs/api/admin-graphql/latest/enums/CurrencyCode)

      ### Arguments

      The presentment currencies prices should return in.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

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

  * selling​Plan​Group​Count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-nullDeprecated

  * storefront​Id

    [Storefront​ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/StorefrontID)

    non-nullDeprecated

  * tax​Code

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Deprecated

***

## Examples

* ### Find a variant by custom id

  #### Query

  ```graphql
  query($identifier: ProductVariantIdentifierInput!) {
    variant: productVariantByIdentifier(identifier: $identifier) {
      id
      title
    }
  }
  ```

  #### Variables

  ```json
  {
    "identifier": {
      "customId": {
        "namespace": "custom",
        "key": "id",
        "value": "1001"
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
  "query": "query($identifier: ProductVariantIdentifierInput!) { variant: productVariantByIdentifier(identifier: $identifier) { id title } }",
   "variables": {
      "identifier": {
        "customId": {
          "namespace": "custom",
          "key": "id",
          "value": "1001"
        }
      }
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
    query($identifier: ProductVariantIdentifierInput!) {
      variant: productVariantByIdentifier(identifier: $identifier) {
        id
        title
      }
    }`,
    {
      variables: {
          "identifier": {
              "customId": {
                  "namespace": "custom",
                  "key": "id",
                  "value": "1001"
              }
          }
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
    query($identifier: ProductVariantIdentifierInput!) {
      variant: productVariantByIdentifier(identifier: $identifier) {
        id
        title
      }
    }
  QUERY

  variables = {
    "identifier": {
      "customId": {
        "namespace": "custom",
        "key": "id",
        "value": "1001"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query($identifier: ProductVariantIdentifierInput!) {
        variant: productVariantByIdentifier(identifier: $identifier) {
          id
          title
        }
      }`,
      "variables": {
          "identifier": {
              "customId": {
                  "namespace": "custom",
                  "key": "id",
                  "value": "1001"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query($identifier: ProductVariantIdentifierInput!) {
    variant: productVariantByIdentifier(identifier: $identifier) {
      id
      title
    }
  }' \
  --variables \
  '{
    "identifier": {
      "customId": {
        "namespace": "custom",
        "key": "id",
        "value": "1001"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "variant": {
      "id": "gid://shopify/ProductVariant/30322695",
      "title": "151cm"
    }
  }
  ```
