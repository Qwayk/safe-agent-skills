---
title: product - GraphQL Admin
description: >-
  Retrieves a
  [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)
  by its ID.

  A product is an item that a merchant can sell in their store.


  Use the `product` query when you need to:


  - Access essential product data (for example, title, description, price,
  images, SEO metadata, and metafields).

  - Build product detail pages and manage inventory.

  - Handle international sales with localized pricing and content.

  - Manage product variants and product options.


  Learn more about working with [Shopify's product
  model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/product-model-components).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/product'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/product.md'
---

# product

query

Retrieves a [product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) by its ID. A product is an item that a merchant can sell in their store.

Use the `product` query when you need to:

* Access essential product data (for example, title, description, price, images, SEO metadata, and metafields).
* Build product detail pages and manage inventory.
* Handle international sales with localized pricing and content.
* Manage product variants and product options.

Learn more about working with [Shopify's product model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/product-model-components).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `Product` to return.

***

## Possible returns

* Product

  [Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)

  The `Product` object lets you manage products in a merchant’s store.

  Products are the goods and services that merchants offer to customers. They can include various details such as title, description, price, images, and options such as size or color. You can use [product variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/productvariant) to create or update different versions of the same product. You can also add or update product [media](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/media). Products can be organized by grouping them into a [collection](https://shopify.dev/docs/api/admin-graphql/latest/objects/collection).

  Learn more about working with [Shopify's product model](https://shopify.dev/docs/apps/build/graphql/migrate/new-product-model/product-model-components), including limitations and considerations.

  * available​Publications​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    The number of [publications](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication) that a resource is published to, without [feedback errors](https://shopify.dev/docs/api/admin-graphql/latest/objects/ResourceFeedback).

  * bundle​Components

    [Product​Bundle​Component​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductBundleComponentConnection)

    non-null

    A list of [components](https://shopify.dev/docs/apps/build/product-merchandising/bundles/add-product-fixed-bundle) that are associated with a product in a bundle.

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

  * bundle​Consolidated​Options

    [\[Componentized​Products​Bundle​Consolidated​Option!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/ComponentizedProductsBundleConsolidatedOption)

    A list of consolidated options for a product in a bundle.

  * category

    [Taxonomy​Category](https://shopify.dev/docs/api/admin-graphql/latest/objects/TaxonomyCategory)

    The category of a product from [Shopify's Standard Product Taxonomy](https://shopify.github.io/product-taxonomy/releases/unstable/?categoryId=sg-4-17-2-17).

  * collections

    [Collection​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CollectionConnection)

    non-null

    A list of [collections](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection) that include the product.

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

      [Collection​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/CollectionSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

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

    ***

  * combined​Listing

    [Combined​Listing](https://shopify.dev/docs/api/admin-graphql/latest/objects/CombinedListing)

    A special product type that combines separate products from a store into a single product listing. [Combined listings](https://shopify.dev/apps/build/product-merchandising/combined-listings) are connected by a shared option, such as color, model, or dimension.

  * combined​Listing​Role

    [Combined​Listings​Role](https://shopify.dev/docs/api/admin-graphql/latest/enums/CombinedListingsRole)

    The [role of the product](https://shopify.dev/docs/apps/build/product-merchandising/combined-listings/build-for-combined-listings) in a combined listing.

    If `null`, then the product isn't part of any combined listing.

  * compare​At​Price​Range

    [Product​Compare​At​Price​Range](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductCompareAtPriceRange)

    The [compare-at price range](https://help.shopify.com/manual/products/details/product-pricing/sale-pricing) of the product in the shop's default currency.

  * contextual​Pricing

    [Product​Contextual​Pricing!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductContextualPricing)

    non-null

    The pricing that applies to a customer in a specific context. For example, a price might vary depending on the customer's location. Only active markets are considered in the price resolution.

    * context

      [Contextual​Pricing​Context!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ContextualPricingContext)

      required

      ### Arguments

      The context used to generate contextual pricing for the variant.

    ***

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the product was created.

  * default​Cursor

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A default [cursor](https://shopify.dev/api/usage/pagination-graphql) that returns the single next record, sorted ascending by ID.

  * description

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A single-line description of the product, with [HTML tags](https://developer.mozilla.org/en-US/docs/Web/HTML) removed.

    * truncate​At

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      Truncates a string after the given length.

    ***

  * description​Html

    [HTML!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/HTML)

    non-null

    The description of the product, with HTML tags. For example, the description might include bold `<strong></strong>` and italic `<i></i>` text.

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

  * featured​Media

    [Media](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Media)

    The featured [media](https://shopify.dev/docs/apps/build/online-store/product-media) associated with the product.

  * feedback

    [Resource​Feedback](https://shopify.dev/docs/api/admin-graphql/latest/objects/ResourceFeedback)

    The information that lets merchants know what steps they need to take to make sure that the app is set up correctly.

    For example, if a merchant hasn't set up a product correctly in the app, then the feedback might include a message that says "You need to add a price to this product".

  * gift​Card​Template​Suffix

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The [theme template](https://shopify.dev/docs/storefronts/themes/architecture/templates) that's used when customers view the gift card in a store.

  * handle

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A unique, human-readable string of the product's title. A handle can contain letters, hyphens (`-`), and numbers, but no spaces. The handle is used in the online store URL for the product.

  * has​Only​Default​Variant

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the product has only a single variant with the default option and value.

  * has​Out​Of​Stock​Variants

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the product has variants that are out of stock.

  * has​Variants​That​Requires​Components

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether at least one of the product variants requires [bundle components](https://shopify.dev/docs/apps/build/product-merchandising/bundles/add-product-fixed-bundle).

    Learn more about [store eligibility for bundles](https://shopify.dev/docs/apps/build/product-merchandising/bundles#store-eligibility).

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * in​Collection

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the product is in a specified [collection](https://shopify.dev/docs/api/admin-graphql/latest/objects/collection).

    * id

      [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      required

      ### Arguments

      The ID of the collection to check. For example, `id: "gid://shopify/Collection/123"`.

    ***

  * is​Gift​Card

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the product is a gift card.

  * legacy​Resource​Id

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The ID of the corresponding resource in the REST Admin API.

  * media

    [Media​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MediaConnection)

    non-null

    The [media](https://shopify.dev/docs/apps/build/online-store/product-media) associated with the product. Valid media are images, 3D models, videos.

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

      [Product​Media​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductMediaSortKeys)

      Default:POSITION

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * id

          id

        * media\_type

          string

        - Filter by `id` range.

        - Example:
          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`
          Valid values:
          * `IMAGE`
          * `VIDEO`
          * `MODEL_3D`
          * `EXTERNAL_VIDEO`

    ***

  * media​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    The total count of [media](https://shopify.dev/docs/apps/build/online-store/product-media) that's associated with a product.

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

  * online​Store​Preview​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    The [preview URL](https://help.shopify.com/manual/online-store/setting-up#preview-your-store) for the online store.

  * online​Store​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    The product's URL on the online store. If `null`, then the product isn't published to the online store sales channel.

  * options

    [\[Product​Option!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductOption)

    non-null

    A list of product options. The limit is defined by the [shop's resource limits for product options](https://shopify.dev/docs/api/admin-graphql/latest/objects/Shop#field-resourcelimits) (`Shop.resourceLimits.maxProductOptions`).

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      Truncate the array result to this size.

    ***

  * price​Range​V2

    [Product​Price​Range​V2!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductPriceRangeV2)

    non-null

    The minimum and maximum prices of a product, expressed in decimal numbers. For example, if the product is priced between $10.00 and $50.00, then the price range is $10.00 - $50.00.

  * product​Components

    [Product​Component​Type​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductComponentTypeConnection)

    non-null

    A list of products that contain at least one variant associated with at least one of the current products' variants via group relationship.

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

  * product​Components​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    A count of unique products that contain at least one variant associated with at least one of the current products' variants via group relationship.

  * product​Parents

    [Product​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductConnection)

    non-null

    A list of products that has a variant that contains any of this product's variants as a component.

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

  * product​Type

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The [product type](https://help.shopify.com/manual/products/details/product-type) that merchants define.

  * published​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time when the product was published to the online store.

  * published​In​Context

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the product is published for a customer only in a specified context. For example, a product might be published for a customer only in a specific location.

    * context

      [Contextual​Publication​Context!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ContextualPublicationContext)

      required

      ### Arguments

      The context used to determine publication status.

    ***

  * published​On​Publication

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the resource is published to a specified [publication](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication).

    * publication​Id

      [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      required

      ### Arguments

      The ID of the publication to check. For example, `id: "gid://shopify/Publication/123"`.

    ***

  * requires​Selling​Plan

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the product can only be purchased with a [selling plan](https://shopify.dev/docs/apps/build/purchase-options/subscriptions/selling-plans). Products that are sold on subscription (`requiresSellingPlan: true`) can be updated only for online stores. If you update a product to be subscription-only (`requiresSellingPlan:false`), then the product is unpublished from all channels, except the online store.

  * resource​Publications

    [Resource​Publication​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ResourcePublicationConnection)

    non-null

    The list of resources that are published to a [publication](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication).

    * only​Published

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:true

      ### Arguments

      Whether to return only the resources that are currently published. If false, then also returns the resources that are scheduled to be published.

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

  * resource​Publications​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    The number of [publications](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication) that a resource is published to, without [feedback errors](https://shopify.dev/docs/api/admin-graphql/latest/objects/ResourceFeedback).

    * only​Published

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:true

      ### Arguments

      Include only the resource's publications that are published. If false, then return all the resource's publications including future publications.

    ***

  * resource​Publications​V2

    [Resource​Publication​V2Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ResourcePublicationV2Connection)

    non-null

    The list of resources that are either published or staged to be published to a [publication](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication).

    * only​Published

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:true

      ### Arguments

      Whether to return only the resources that are currently published. If false, then also returns the resources that are scheduled or staged to be published.

    * catalog​Type

      [Catalog​Type](https://shopify.dev/docs/api/admin-graphql/latest/enums/CatalogType)

      Filter publications by catalog type.

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

  * restricted​For​Resource

    [Restricted​For​Resource](https://shopify.dev/docs/api/admin-graphql/latest/objects/RestrictedForResource)

    Whether the merchant can make changes to the product when they [edit the order](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/edit-orders) associated with the product. For example, a merchant might be restricted from changing product details when they edit an order.

    * calculated​Order​Id

      [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      required

      ### Arguments

      The resource Id of the order with edits applied but not saved.

    ***

  * selling​Plan​Groups

    [Selling​Plan​Group​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SellingPlanGroupConnection)

    non-null

    A list of all [selling plan groups](https://shopify.dev/docs/apps/build/purchase-options/subscriptions/selling-plans/build-a-selling-plan) that are associated with the product either directly, or through the product's variants.

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

    A count of [selling plan groups](https://shopify.dev/docs/apps/build/purchase-options/subscriptions/selling-plans/build-a-selling-plan) that are associated with the product.

  * seo

    [SEO!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SEO)

    non-null

    The [SEO title and description](https://help.shopify.com/manual/promoting-marketing/seo/adding-keywords) that are associated with a product.

  * status

    [Product​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductStatus)

    non-null

    The [product status](https://help.shopify.com/manual/products/details/product-details-page#product-status), which controls visibility across all sales channels.

  * tags

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A comma-separated list of searchable keywords that are associated with the product. For example, a merchant might apply the `sports` and `summer` tags to products that are associated with sportwear for summer.

    Updating `tags` overwrites any existing tags that were previously added to the product. To add new tags without overwriting existing tags, use the [`tagsAdd`](https://shopify.dev/api/admin-graphql/latest/mutations/tagsadd) mutation.

  * template​Suffix

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The [theme template](https://shopify.dev/docs/storefronts/themes/architecture/templates) that's used when customers view the product in a store.

  * title

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name for the product that displays to customers. The title is used to construct the product's handle. For example, if a product is titled "Black Sunglasses", then the handle is `black-sunglasses`.

  * total​Inventory

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The quantity of inventory that's in stock.

  * tracks​Inventory

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether [inventory tracking](https://help.shopify.com/manual/products/inventory/getting-started-with-inventory/set-up-inventory-tracking) has been enabled for the product.

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

  * unpublished​Publications

    [Publication​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/PublicationConnection)

    non-null

    The list of [publications](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication) that the resource isn't published to.

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

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the product was last modified. A product's `updatedAt` value can change for different reasons. For example, if an order is placed for a product that has inventory tracking set up, then the inventory adjustment is counted as an update.

  * variants

    [Product​Variant​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductVariantConnection)

    non-null

    A list of [variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) associated with the product. If querying a single product at the root, you can fetch up to 2048 variants.

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

      [Product​Variant​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductVariantSortKeys)

      Default:POSITION

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    ***

  * variants​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    The number of [variants](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) that are associated with the product.

  * vendor

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of the product's vendor.

  * body​Html

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Deprecated

  * custom​Product​Type

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Deprecated

  * description​Plain​Summary

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-nullDeprecated

  * featured​Image

    [Image](https://shopify.dev/docs/api/admin-graphql/latest/objects/Image)

    Deprecated

  * images

    [Image​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ImageConnection)

    non-nullDeprecated

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

      [Product​Image​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductImageSortKeys)

      Default:POSITION

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

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

  * price​Range

    [Product​Price​Range!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductPriceRange)

    non-nullDeprecated

  * product​Category

    [Product​Category](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductCategory)

    Deprecated

  * product​Publications

    [Product​Publication​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductPublicationConnection)

    non-nullDeprecated

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

  * publication​Count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-nullDeprecated

    * only​Published

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:true

      ### Arguments

      Include only the resource's publications that are published. If false, then return all the resource's publications including future publications.

    ***

  * publications

    [Product​Publication​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductPublicationConnection)

    non-nullDeprecated

    * only​Published

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:true

      ### Arguments

      Return only the publications that are published. If false, then return all publications.

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

  * published​On​Channel

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-nullDeprecated

    * channel​Id

      [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      required

      ### Arguments

      The ID of the channel to check.

    ***

  * published​On​Current​Channel

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-nullDeprecated

  * published​On​Current​Publication

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-nullDeprecated

  * resource​Publication​On​Current​Publication

    [Resource​Publication​V2](https://shopify.dev/docs/api/admin-graphql/latest/objects/ResourcePublicationV2)

    Deprecated

  * selling​Plan​Group​Count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-nullDeprecated

  * standardized​Product​Type

    [Standardized​Product​Type](https://shopify.dev/docs/api/admin-graphql/latest/objects/StandardizedProductType)

    Deprecated

  * storefront​Id

    [Storefront​ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/StorefrontID)

    non-nullDeprecated

  * total​Variants

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-nullDeprecated

  * unpublished​Channels

    [Channel​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ChannelConnection)

    non-nullDeprecated

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

***

## Examples

* ### Get metafields attached to a product

  #### Description

  Get a page of metafields attached to a specific product.

  #### Query

  ```graphql
  query ProductMetafields($ownerId: ID!) {
    product(id: $ownerId) {
      metafields(first: 3) {
        edges {
          node {
            namespace
            key
            value
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "ownerId": "gid://shopify/Product/108828309"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query ProductMetafields($ownerId: ID!) { product(id: $ownerId) { metafields(first: 3) { edges { node { namespace key value } } } } }",
   "variables": {
      "ownerId": "gid://shopify/Product/108828309"
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
    query ProductMetafields($ownerId: ID!) {
      product(id: $ownerId) {
        metafields(first: 3) {
          edges {
            node {
              namespace
              key
              value
            }
          }
        }
      }
    }`,
    {
      variables: {
          "ownerId": "gid://shopify/Product/108828309"
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
    query ProductMetafields($ownerId: ID!) {
      product(id: $ownerId) {
        metafields(first: 3) {
          edges {
            node {
              namespace
              key
              value
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "ownerId": "gid://shopify/Product/108828309"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query ProductMetafields($ownerId: ID!) {
        product(id: $ownerId) {
          metafields(first: 3) {
            edges {
              node {
                namespace
                key
                value
              }
            }
          }
        }
      }`,
      "variables": {
          "ownerId": "gid://shopify/Product/108828309"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ProductMetafields($ownerId: ID!) {
    product(id: $ownerId) {
      metafields(first: 3) {
        edges {
          node {
            namespace
            key
            value
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "ownerId": "gid://shopify/Product/108828309"
  }'
  ```

  #### Response

  ```json
  {
    "product": {
      "metafields": {
        "edges": [
          {
            "node": {
              "namespace": "my_fields",
              "key": "liner_material",
              "value": "synthetic leather"
            }
          }
        ]
      }
    }
  }
  ```

* ### Get the price range for a product for buyers from Canada

  #### Description

  Retrieve a product's price range for buyers from Canada by supplying the product ID. Prices are returned in the currency configured for the country in \[Markets settings]\(https://help.shopify.com/manual/international/managing). They may be calculated from the base variant prices, or provided by the merchant as fixed local prices.

  #### Query

  ```graphql
  query {
    product(id: "gid://shopify/Product/108828309") {
      contextualPricing(context: {country: CA}) {
        priceRange {
          maxVariantPrice {
            amount
            currencyCode
          }
          minVariantPrice {
            amount
            currencyCode
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
  "query": "query { product(id: \"gid://shopify/Product/108828309\") { contextualPricing(context: {country: CA}) { priceRange { maxVariantPrice { amount currencyCode } minVariantPrice { amount currencyCode } } } } }"
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
      product(id: "gid://shopify/Product/108828309") {
        contextualPricing(context: {country: CA}) {
          priceRange {
            maxVariantPrice {
              amount
              currencyCode
            }
            minVariantPrice {
              amount
              currencyCode
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
      product(id: "gid://shopify/Product/108828309") {
        contextualPricing(context: {country: CA}) {
          priceRange {
            maxVariantPrice {
              amount
              currencyCode
            }
            minVariantPrice {
              amount
              currencyCode
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
      product(id: "gid://shopify/Product/108828309") {
        contextualPricing(context: {country: CA}) {
          priceRange {
            maxVariantPrice {
              amount
              currencyCode
            }
            minVariantPrice {
              amount
              currencyCode
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
    product(id: "gid://shopify/Product/108828309") {
      contextualPricing(context: {country: CA}) {
        priceRange {
          maxVariantPrice {
            amount
            currencyCode
          }
          minVariantPrice {
            amount
            currencyCode
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "product": {
      "contextualPricing": {
        "priceRange": {
          "maxVariantPrice": {
            "amount": "12.99",
            "currencyCode": "CAD"
          },
          "minVariantPrice": {
            "amount": "12.99",
            "currencyCode": "CAD"
          }
        }
      }
    }
  }
  ```

* ### Query whether a product is published in a given country

  #### Description

  Supply the product ID to retrieve whether a product is published in a certain international context. A merchant selling internationally might choose to restrict some products due to logistics, licensing, or market-fit. This example returns whether the product is published in Canada, Great Britain, or the United States. You must have the \`read\_publications\` access scope to return publication information.

  #### Query

  ```graphql
  query {
    product(id: "gid://shopify/Product/49527214") {
      title
      publishedInCA: publishedInContext(context: {country: CA})
      publishedInGB: publishedInContext(context: {country: GB})
      publishedInUS: publishedInContext(context: {country: US})
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
  "query": "query { product(id: \"gid://shopify/Product/49527214\") { title publishedInCA: publishedInContext(context: {country: CA}) publishedInGB: publishedInContext(context: {country: GB}) publishedInUS: publishedInContext(context: {country: US}) } }"
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
      product(id: "gid://shopify/Product/49527214") {
        title
        publishedInCA: publishedInContext(context: {country: CA})
        publishedInGB: publishedInContext(context: {country: GB})
        publishedInUS: publishedInContext(context: {country: US})
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
      product(id: "gid://shopify/Product/49527214") {
        title
        publishedInCA: publishedInContext(context: {country: CA})
        publishedInGB: publishedInContext(context: {country: GB})
        publishedInUS: publishedInContext(context: {country: US})
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
      product(id: "gid://shopify/Product/49527214") {
        title
        publishedInCA: publishedInContext(context: {country: CA})
        publishedInGB: publishedInContext(context: {country: GB})
        publishedInUS: publishedInContext(context: {country: US})
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    product(id: "gid://shopify/Product/49527214") {
      title
      publishedInCA: publishedInContext(context: {country: CA})
      publishedInGB: publishedInContext(context: {country: GB})
      publishedInUS: publishedInContext(context: {country: US})
    }
  }'
  ```

  #### Response

  ```json
  {
    "product": {
      "title": "Alarm clock",
      "publishedInCA": true,
      "publishedInGB": false,
      "publishedInUS": true
    }
  }
  ```

* ### Retrieve a metafield associated with a product

  #### Description

  Get the metafield value identified by \`my\_fields.liner\_material\` on a specific product.

  #### Query

  ```graphql
  query ProductMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
    product(id: $ownerId) {
      linerMaterial: metafield(namespace: $namespace, key: $key) {
        value
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "namespace": "my_fields",
    "key": "liner_material",
    "ownerId": "gid://shopify/Product/108828309"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query ProductMetafield($namespace: String!, $key: String!, $ownerId: ID!) { product(id: $ownerId) { linerMaterial: metafield(namespace: $namespace, key: $key) { value } } }",
   "variables": {
      "namespace": "my_fields",
      "key": "liner_material",
      "ownerId": "gid://shopify/Product/108828309"
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
    query ProductMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
      product(id: $ownerId) {
        linerMaterial: metafield(namespace: $namespace, key: $key) {
          value
        }
      }
    }`,
    {
      variables: {
          "namespace": "my_fields",
          "key": "liner_material",
          "ownerId": "gid://shopify/Product/108828309"
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
    query ProductMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
      product(id: $ownerId) {
        linerMaterial: metafield(namespace: $namespace, key: $key) {
          value
        }
      }
    }
  QUERY

  variables = {
    "namespace": "my_fields",
    "key": "liner_material",
    "ownerId": "gid://shopify/Product/108828309"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query ProductMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
        product(id: $ownerId) {
          linerMaterial: metafield(namespace: $namespace, key: $key) {
            value
          }
        }
      }`,
      "variables": {
          "namespace": "my_fields",
          "key": "liner_material",
          "ownerId": "gid://shopify/Product/108828309"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ProductMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
    product(id: $ownerId) {
      linerMaterial: metafield(namespace: $namespace, key: $key) {
        value
      }
    }
  }' \
  --variables \
  '{
    "namespace": "my_fields",
    "key": "liner_material",
    "ownerId": "gid://shopify/Product/108828309"
  }'
  ```

  #### Response

  ```json
  {
    "product": {
      "linerMaterial": {
        "value": "synthetic leather"
      }
    }
  }
  ```

* ### Retrieve a product that is published to your app

  #### Description

  Supply the product ID to retrieve a product that's published to your app. This example returns comprehensive product information including basic details, timestamps, variants, and media. You must have the \`read\_product\_listings\` access scope to return publication information.

  #### Query

  ```graphql
  query ProductShow($id: ID!) {
    product(id: $id) {
      publishedOnCurrentPublication
      id
      createdAt
      updatedAt
      descriptionHtml
      handle
      productType
      title
      vendor
      tags
      publishedAt
      variants(first: 10) {
        nodes {
          id
        }
      }
      images(first: 10) {
        nodes {
          id
          height
          width
          url
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Product/20995642"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query ProductShow($id: ID!) { product(id: $id) { publishedOnCurrentPublication id createdAt updatedAt descriptionHtml handle productType title vendor tags publishedAt variants(first: 10) { nodes { id } } images(first: 10) { nodes { id height width url } } } }",
   "variables": {
      "id": "gid://shopify/Product/20995642"
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
    query ProductShow($id: ID!) {
      product(id: $id) {
        publishedOnCurrentPublication
        id
        createdAt
        updatedAt
        descriptionHtml
        handle
        productType
        title
        vendor
        tags
        publishedAt
        variants(first: 10) {
          nodes {
            id
          }
        }
        images(first: 10) {
          nodes {
            id
            height
            width
            url
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Product/20995642"
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
    query ProductShow($id: ID!) {
      product(id: $id) {
        publishedOnCurrentPublication
        id
        createdAt
        updatedAt
        descriptionHtml
        handle
        productType
        title
        vendor
        tags
        publishedAt
        variants(first: 10) {
          nodes {
            id
          }
        }
        images(first: 10) {
          nodes {
            id
            height
            width
            url
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Product/20995642"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query ProductShow($id: ID!) {
        product(id: $id) {
          publishedOnCurrentPublication
          id
          createdAt
          updatedAt
          descriptionHtml
          handle
          productType
          title
          vendor
          tags
          publishedAt
          variants(first: 10) {
            nodes {
              id
            }
          }
          images(first: 10) {
            nodes {
              id
              height
              width
              url
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Product/20995642"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ProductShow($id: ID!) {
    product(id: $id) {
      publishedOnCurrentPublication
      id
      createdAt
      updatedAt
      descriptionHtml
      handle
      productType
      title
      vendor
      tags
      publishedAt
      variants(first: 10) {
        nodes {
          id
        }
      }
      images(first: 10) {
        nodes {
          id
          height
          width
          url
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Product/20995642"
  }'
  ```

  #### Response

  ```json
  {
    "product": {
      "publishedOnCurrentPublication": true,
      "id": "gid://shopify/Product/20995642",
      "createdAt": "2005-01-01T00:00:00Z",
      "updatedAt": "2005-01-01T00:00:00Z",
      "descriptionHtml": "<p>bad board</p>",
      "handle": "element",
      "productType": "Snowboards",
      "title": "Element",
      "vendor": "Arbor",
      "tags": [],
      "publishedAt": "2005-01-01T00:00:00Z",
      "variants": {
        "nodes": [
          {
            "id": "gid://shopify/ProductVariant/30322695"
          },
          {
            "id": "gid://shopify/ProductVariant/113711323"
          },
          {
            "id": "gid://shopify/ProductVariant/236948360"
          }
        ]
      },
      "images": {
        "nodes": [
          {
            "id": "gid://shopify/ProductImage/916933471",
            "height": 400,
            "width": 85,
            "url": "https://cdn.shopify.com/s/files/1/2637/1970/products/element58.jpg?v=1749170878"
          },
          {
            "id": "gid://shopify/ProductImage/671149505",
            "height": 110,
            "width": 372,
            "url": "https://cdn.shopify.com/s/files/1/2637/1970/products/bacon.jpg?v=1749170878"
          }
        ]
      }
    }
  }
  ```

* ### Retrieve a product using the QueryRoot.node field and a GraphQL fragment

  #### Description

  Supply the product ID to retrieve the title of the product. This example returns the product title for the specified product.

  #### Query

  ```graphql
  query {
    node(id: "gid://shopify/Product/108828309") {
      id
      ... on Product {
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
  "query": "query { node(id: \"gid://shopify/Product/108828309\") { id ... on Product { title } } }"
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
      node(id: "gid://shopify/Product/108828309") {
        id
        ... on Product {
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
    query {
      node(id: "gid://shopify/Product/108828309") {
        id
        ... on Product {
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
    data: `query {
      node(id: "gid://shopify/Product/108828309") {
        id
        ... on Product {
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
  'query {
    node(id: "gid://shopify/Product/108828309") {
      id
      ... on Product {
        title
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "node": {
      "id": "gid://shopify/Product/108828309",
      "title": "Draft"
    }
  }
  ```

* ### Retrieve a product's fields and connections

  #### Description

  Supply the product ID to retrieve the product's fields and connections. This example returns comprehensive information about the product, including its collections, created date, description, handle, and variant information. You must have the \`read\_publications\` and \`read\_product\_listings\` access scopes to return publication information.

  #### Query

  ```graphql
  query {
    product(id: "gid://shopify/Product/108828309") {
      collections(first: 5) {
        edges {
          node {
            handle
          }
        }
      }
      createdAt
      defaultCursor
      description
      descriptionHtml
      featuredMedia {
        id
      }
      feedback {
        details {
          messages {
            message
          }
        }
      }
      giftCardTemplateSuffix
      handle
      hasOnlyDefaultVariant
      hasOutOfStockVariants
      id
      media(first: 5) {
        edges {
          node {
            id
          }
        }
      }
      inCollection(id: "gid://shopify/Collection/1007901140")
      isGiftCard
      legacyResourceId
      metafields(first: 5) {
        edges {
          node {
            id
          }
        }
      }
      onlineStorePreviewUrl
      onlineStoreUrl
      options {
        name
      }
      priceRangeV2 {
        maxVariantPrice {
          amount
        }
        minVariantPrice {
          amount
        }
      }
      productType
      resourcePublicationsCount {
        count
      }
      availablePublicationsCount {
        count
      }
      publishedAt
      resourcePublications(first: 5) {
        edges {
          node {
            isPublished
          }
        }
      }
      resourcePublicationOnCurrentPublication {
        publication {
          id
        }
        publishDate
        isPublished
      }
      seo {
        title
      }
      tags
      templateSuffix
      title
      totalInventory
      tracksInventory
      unpublishedPublications(first: 5) {
        edges {
          node {
            id
          }
        }
      }
      updatedAt
      variants(first: 5) {
        edges {
          node {
            displayName
          }
        }
      }
      variantsCount {
        count
      }
      vendor
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
  "query": "query { product(id: \"gid://shopify/Product/108828309\") { collections(first: 5) { edges { node { handle } } } createdAt defaultCursor description descriptionHtml featuredMedia { id } feedback { details { messages { message } } } giftCardTemplateSuffix handle hasOnlyDefaultVariant hasOutOfStockVariants id media(first: 5) { edges { node { id } } } inCollection(id: \"gid://shopify/Collection/1007901140\") isGiftCard legacyResourceId metafields(first: 5) { edges { node { id } } } onlineStorePreviewUrl onlineStoreUrl options { name } priceRangeV2 { maxVariantPrice { amount } minVariantPrice { amount } } productType resourcePublicationsCount { count } availablePublicationsCount { count } publishedAt resourcePublications(first: 5) { edges { node { isPublished } } } resourcePublicationOnCurrentPublication { publication { id } publishDate isPublished } seo { title } tags templateSuffix title totalInventory tracksInventory unpublishedPublications(first: 5) { edges { node { id } } } updatedAt variants(first: 5) { edges { node { displayName } } } variantsCount { count } vendor } }"
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
      product(id: "gid://shopify/Product/108828309") {
        collections(first: 5) {
          edges {
            node {
              handle
            }
          }
        }
        createdAt
        defaultCursor
        description
        descriptionHtml
        featuredMedia {
          id
        }
        feedback {
          details {
            messages {
              message
            }
          }
        }
        giftCardTemplateSuffix
        handle
        hasOnlyDefaultVariant
        hasOutOfStockVariants
        id
        media(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        inCollection(id: "gid://shopify/Collection/1007901140")
        isGiftCard
        legacyResourceId
        metafields(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        onlineStorePreviewUrl
        onlineStoreUrl
        options {
          name
        }
        priceRangeV2 {
          maxVariantPrice {
            amount
          }
          minVariantPrice {
            amount
          }
        }
        productType
        resourcePublicationsCount {
          count
        }
        availablePublicationsCount {
          count
        }
        publishedAt
        resourcePublications(first: 5) {
          edges {
            node {
              isPublished
            }
          }
        }
        resourcePublicationOnCurrentPublication {
          publication {
            id
          }
          publishDate
          isPublished
        }
        seo {
          title
        }
        tags
        templateSuffix
        title
        totalInventory
        tracksInventory
        unpublishedPublications(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        updatedAt
        variants(first: 5) {
          edges {
            node {
              displayName
            }
          }
        }
        variantsCount {
          count
        }
        vendor
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
      product(id: "gid://shopify/Product/108828309") {
        collections(first: 5) {
          edges {
            node {
              handle
            }
          }
        }
        createdAt
        defaultCursor
        description
        descriptionHtml
        featuredMedia {
          id
        }
        feedback {
          details {
            messages {
              message
            }
          }
        }
        giftCardTemplateSuffix
        handle
        hasOnlyDefaultVariant
        hasOutOfStockVariants
        id
        media(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        inCollection(id: "gid://shopify/Collection/1007901140")
        isGiftCard
        legacyResourceId
        metafields(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        onlineStorePreviewUrl
        onlineStoreUrl
        options {
          name
        }
        priceRangeV2 {
          maxVariantPrice {
            amount
          }
          minVariantPrice {
            amount
          }
        }
        productType
        resourcePublicationsCount {
          count
        }
        availablePublicationsCount {
          count
        }
        publishedAt
        resourcePublications(first: 5) {
          edges {
            node {
              isPublished
            }
          }
        }
        resourcePublicationOnCurrentPublication {
          publication {
            id
          }
          publishDate
          isPublished
        }
        seo {
          title
        }
        tags
        templateSuffix
        title
        totalInventory
        tracksInventory
        unpublishedPublications(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        updatedAt
        variants(first: 5) {
          edges {
            node {
              displayName
            }
          }
        }
        variantsCount {
          count
        }
        vendor
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
      product(id: "gid://shopify/Product/108828309") {
        collections(first: 5) {
          edges {
            node {
              handle
            }
          }
        }
        createdAt
        defaultCursor
        description
        descriptionHtml
        featuredMedia {
          id
        }
        feedback {
          details {
            messages {
              message
            }
          }
        }
        giftCardTemplateSuffix
        handle
        hasOnlyDefaultVariant
        hasOutOfStockVariants
        id
        media(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        inCollection(id: "gid://shopify/Collection/1007901140")
        isGiftCard
        legacyResourceId
        metafields(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        onlineStorePreviewUrl
        onlineStoreUrl
        options {
          name
        }
        priceRangeV2 {
          maxVariantPrice {
            amount
          }
          minVariantPrice {
            amount
          }
        }
        productType
        resourcePublicationsCount {
          count
        }
        availablePublicationsCount {
          count
        }
        publishedAt
        resourcePublications(first: 5) {
          edges {
            node {
              isPublished
            }
          }
        }
        resourcePublicationOnCurrentPublication {
          publication {
            id
          }
          publishDate
          isPublished
        }
        seo {
          title
        }
        tags
        templateSuffix
        title
        totalInventory
        tracksInventory
        unpublishedPublications(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        updatedAt
        variants(first: 5) {
          edges {
            node {
              displayName
            }
          }
        }
        variantsCount {
          count
        }
        vendor
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    product(id: "gid://shopify/Product/108828309") {
      collections(first: 5) {
        edges {
          node {
            handle
          }
        }
      }
      createdAt
      defaultCursor
      description
      descriptionHtml
      featuredMedia {
        id
      }
      feedback {
        details {
          messages {
            message
          }
        }
      }
      giftCardTemplateSuffix
      handle
      hasOnlyDefaultVariant
      hasOutOfStockVariants
      id
      media(first: 5) {
        edges {
          node {
            id
          }
        }
      }
      inCollection(id: "gid://shopify/Collection/1007901140")
      isGiftCard
      legacyResourceId
      metafields(first: 5) {
        edges {
          node {
            id
          }
        }
      }
      onlineStorePreviewUrl
      onlineStoreUrl
      options {
        name
      }
      priceRangeV2 {
        maxVariantPrice {
          amount
        }
        minVariantPrice {
          amount
        }
      }
      productType
      resourcePublicationsCount {
        count
      }
      availablePublicationsCount {
        count
      }
      publishedAt
      resourcePublications(first: 5) {
        edges {
          node {
            isPublished
          }
        }
      }
      resourcePublicationOnCurrentPublication {
        publication {
          id
        }
        publishDate
        isPublished
      }
      seo {
        title
      }
      tags
      templateSuffix
      title
      totalInventory
      tracksInventory
      unpublishedPublications(first: 5) {
        edges {
          node {
            id
          }
        }
      }
      updatedAt
      variants(first: 5) {
        edges {
          node {
            displayName
          }
        }
      }
      variantsCount {
        count
      }
      vendor
    }
  }'
  ```

  #### Response

  ```json
  {
    "product": {
      "collections": {
        "edges": [
          {
            "node": {
              "handle": "reorder_custom"
            }
          },
          {
            "node": {
              "handle": "everything"
            }
          },
          {
            "node": {
              "handle": "snowboards"
            }
          },
          {
            "node": {
              "handle": "everything-custom"
            }
          },
          {
            "node": {
              "handle": "featured_asc"
            }
          }
        ]
      },
      "createdAt": "2005-01-02T00:00:00Z",
      "defaultCursor": "eyJsaW1pdCI6MSwib3JkZXIiOiJpZCBhc2MiLCJsYXN0X2lkIjoxMDg4MjgzMDksImxhc3RfdmFsdWUiOjEwODgyODMwOSwiZGlyZWN0aW9uIjoibmV4dCJ9",
      "description": "good board",
      "descriptionHtml": "<p>good board</p>",
      "featuredMedia": {
        "id": "gid://shopify/ExternalVideo/1041834415"
      },
      "feedback": null,
      "giftCardTemplateSuffix": null,
      "handle": "draft",
      "hasOnlyDefaultVariant": false,
      "hasOutOfStockVariants": false,
      "id": "gid://shopify/Product/108828309",
      "media": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/ExternalVideo/1041834415"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Video/723685877"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Model3d/544780400"
            }
          },
          {
            "node": {
              "id": "gid://shopify/MediaImage/853695510"
            }
          },
          {
            "node": {
              "id": "gid://shopify/MediaImage/603944694"
            }
          }
        ]
      },
      "inCollection": true,
      "isGiftCard": false,
      "legacyResourceId": "108828309",
      "metafields": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/Metafield/61655654"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Metafield/147010266"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Metafield/204658793"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Metafield/485513001"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Metafield/632448133"
            }
          }
        ]
      },
      "onlineStorePreviewUrl": "https://www.snowdevil.ca/products/draft",
      "onlineStoreUrl": "https://www.snowdevil.ca/products/draft",
      "options": [
        {
          "name": "Title"
        }
      ],
      "priceRangeV2": {
        "maxVariantPrice": {
          "amount": "10.0"
        },
        "minVariantPrice": {
          "amount": "10.0"
        }
      },
      "productType": "Snowboards",
      "resourcePublicationsCount": {
        "count": 4
      },
      "availablePublicationsCount": {
        "count": 4
      },
      "publishedAt": "2005-01-02T00:00:00Z",
      "resourcePublications": {
        "edges": [
          {
            "node": {
              "isPublished": true
            }
          },
          {
            "node": {
              "isPublished": true
            }
          },
          {
            "node": {
              "isPublished": true
            }
          }
        ]
      },
      "resourcePublicationOnCurrentPublication": {
        "publication": {
          "id": "gid://shopify/Publication/762454635"
        },
        "publishDate": "2005-01-02T00:00:00Z",
        "isPublished": true
      },
      "seo": {
        "title": null
      },
      "tags": [
        "Deepsnow",
        "Dub Quote\"s",
        "quote's",
        "Wooden Core"
      ],
      "templateSuffix": null,
      "title": "Draft",
      "totalInventory": 1,
      "tracksInventory": true,
      "unpublishedPublications": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/Publication/49361227"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Publication/195806409"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Publication/224761294"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Publication/336184109"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Publication/347532733"
            }
          }
        ]
      },
      "updatedAt": "2005-01-02T00:00:00Z",
      "variants": {
        "edges": [
          {
            "node": {
              "displayName": "Draft - 151cm"
            }
          }
        ]
      },
      "variantsCount": {
        "count": 1
      },
      "vendor": "Arbor"
    }
  }
  ```

* ### Retrieve a single product

  #### Description

  Supply the product ID to retrieve the product. This example returns the product's ID, title, \[product variants]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant), and \[collections]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection).

  #### Query

  ```graphql
  query GetProduct($id: ID!) {
    product(id: $id) {
      id
      title
      variants(first: 10) {
        nodes {
          id
          title
        }
      }
      collections(first: 10) {
        nodes {
          id
          title
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Product/108828309"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query GetProduct($id: ID!) { product(id: $id) { id title variants(first: 10) { nodes { id title } } collections(first: 10) { nodes { id title } } } }",
   "variables": {
      "id": "gid://shopify/Product/108828309"
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
    query GetProduct($id: ID!) {
      product(id: $id) {
        id
        title
        variants(first: 10) {
          nodes {
            id
            title
          }
        }
        collections(first: 10) {
          nodes {
            id
            title
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Product/108828309"
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
    query GetProduct($id: ID!) {
      product(id: $id) {
        id
        title
        variants(first: 10) {
          nodes {
            id
            title
          }
        }
        collections(first: 10) {
          nodes {
            id
            title
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Product/108828309"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query GetProduct($id: ID!) {
        product(id: $id) {
          id
          title
          variants(first: 10) {
            nodes {
              id
              title
            }
          }
          collections(first: 10) {
            nodes {
              id
              title
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Product/108828309"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query GetProduct($id: ID!) {
    product(id: $id) {
      id
      title
      variants(first: 10) {
        nodes {
          id
          title
        }
      }
      collections(first: 10) {
        nodes {
          id
          title
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Product/108828309"
  }'
  ```

  #### Response

  ```json
  {
    "product": {
      "id": "gid://shopify/Product/108828309",
      "title": "Draft",
      "variants": {
        "nodes": [
          {
            "id": "gid://shopify/ProductVariant/43729076",
            "title": "151cm"
          }
        ]
      },
      "collections": {
        "nodes": [
          {
            "id": "gid://shopify/Collection/79210309",
            "title": "Custom Other Items"
          },
          {
            "id": "gid://shopify/Collection/94229130",
            "title": "All products more expensive than free"
          },
          {
            "id": "gid://shopify/Collection/142458073",
            "title": "All snowboards"
          },
          {
            "id": "gid://shopify/Collection/442946009",
            "title": "All products - handpicked!"
          },
          {
            "id": "gid://shopify/Collection/793607630",
            "title": "Featured items"
          },
          {
            "id": "gid://shopify/Collection/925420914",
            "title": "All snowboards called Draft"
          },
          {
            "id": "gid://shopify/Collection/1007901140",
            "title": "Featured items"
          },
          {
            "id": "gid://shopify/Collection/1063001310",
            "title": "Smart Other items"
          }
        ]
      }
    }
  }
  ```

* ### Retrieve media for a product

  #### Description

  Supply the product ID to retrieve the media, such as images and videos, for the product. This example returns the media for the specified product. Learn more about \[managing media for products]\(https://shopify.dev/docs/apps/build/online-store/product-media).

  #### Query

  ```graphql
  query {
    product(id: "gid://shopify/Product/108828309") {
      title
      media(first: 5) {
        edges {
          node {
            ...fieldsForMediaTypes
          }
        }
      }
    }
  }

  fragment fieldsForMediaTypes on Media {
    alt
    mediaContentType
    preview {
      image {
        id
        altText
        url
      }
    }
    status
    ... on Video {
      id
      sources {
        format
        height
        mimeType
        url
        width
      }
      originalSource {
        format
        height
        mimeType
        url
        width
      }
    }
    ... on ExternalVideo {
      id
      host
      originUrl
    }
    ... on Model3d {
      sources {
        format
        mimeType
        url
      }
      originalSource {
        format
        mimeType
        url
      }
    }
    ... on MediaImage {
      id
      image {
        altText
        url
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
  "query": "query { product(id: \"gid://shopify/Product/108828309\") { title media(first: 5) { edges { node { ...fieldsForMediaTypes } } } } } fragment fieldsForMediaTypes on Media { alt mediaContentType preview { image { id altText url } } status ... on Video { id sources { format height mimeType url width } originalSource { format height mimeType url width } } ... on ExternalVideo { id host originUrl } ... on Model3d { sources { format mimeType url } originalSource { format mimeType url } } ... on MediaImage { id image { altText url } } }"
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
      product(id: "gid://shopify/Product/108828309") {
        title
        media(first: 5) {
          edges {
            node {
              ...fieldsForMediaTypes
            }
          }
        }
      }
    }
    
    fragment fieldsForMediaTypes on Media {
      alt
      mediaContentType
      preview {
        image {
          id
          altText
          url
        }
      }
      status
      ... on Video {
        id
        sources {
          format
          height
          mimeType
          url
          width
        }
        originalSource {
          format
          height
          mimeType
          url
          width
        }
      }
      ... on ExternalVideo {
        id
        host
        originUrl
      }
      ... on Model3d {
        sources {
          format
          mimeType
          url
        }
        originalSource {
          format
          mimeType
          url
        }
      }
      ... on MediaImage {
        id
        image {
          altText
          url
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
      product(id: "gid://shopify/Product/108828309") {
        title
        media(first: 5) {
          edges {
            node {
              ...fieldsForMediaTypes
            }
          }
        }
      }
    }
    
    fragment fieldsForMediaTypes on Media {
      alt
      mediaContentType
      preview {
        image {
          id
          altText
          url
        }
      }
      status
      ... on Video {
        id
        sources {
          format
          height
          mimeType
          url
          width
        }
        originalSource {
          format
          height
          mimeType
          url
          width
        }
      }
      ... on ExternalVideo {
        id
        host
        originUrl
      }
      ... on Model3d {
        sources {
          format
          mimeType
          url
        }
        originalSource {
          format
          mimeType
          url
        }
      }
      ... on MediaImage {
        id
        image {
          altText
          url
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
      product(id: "gid://shopify/Product/108828309") {
        title
        media(first: 5) {
          edges {
            node {
              ...fieldsForMediaTypes
            }
          }
        }
      }
    }
    
    fragment fieldsForMediaTypes on Media {
      alt
      mediaContentType
      preview {
        image {
          id
          altText
          url
        }
      }
      status
      ... on Video {
        id
        sources {
          format
          height
          mimeType
          url
          width
        }
        originalSource {
          format
          height
          mimeType
          url
          width
        }
      }
      ... on ExternalVideo {
        id
        host
        originUrl
      }
      ... on Model3d {
        sources {
          format
          mimeType
          url
        }
        originalSource {
          format
          mimeType
          url
        }
      }
      ... on MediaImage {
        id
        image {
          altText
          url
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
    product(id: "gid://shopify/Product/108828309") {
      title
      media(first: 5) {
        edges {
          node {
            ...fieldsForMediaTypes
          }
        }
      }
    }
  }

  fragment fieldsForMediaTypes on Media {
    alt
    mediaContentType
    preview {
      image {
        id
        altText
        url
      }
    }
    status
    ... on Video {
      id
      sources {
        format
        height
        mimeType
        url
        width
      }
      originalSource {
        format
        height
        mimeType
        url
        width
      }
    }
    ... on ExternalVideo {
      id
      host
      originUrl
    }
    ... on Model3d {
      sources {
        format
        mimeType
        url
      }
      originalSource {
        format
        mimeType
        url
      }
    }
    ... on MediaImage {
      id
      image {
        altText
        url
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "product": {
      "title": "Draft",
      "media": {
        "edges": [
          {
            "node": {
              "alt": "This is a video",
              "mediaContentType": "EXTERNAL_VIDEO",
              "preview": {
                "image": {
                  "id": "gid://shopify/ImageSource/425689044",
                  "altText": "This is a video",
                  "url": "https://cdn.shopify.com/s/files/1/2637/1970/products/external_video_preview.jpg?v=1749170878"
                }
              },
              "status": "READY",
              "id": "gid://shopify/ExternalVideo/1041834415",
              "host": "YOUTUBE",
              "originUrl": "https://youtu.be/dQw4w9WgXcQ"
            }
          },
          {
            "node": {
              "alt": "This is a video",
              "mediaContentType": "VIDEO",
              "preview": {
                "image": {
                  "id": "gid://shopify/ImageSource/727549632",
                  "altText": "This is a video",
                  "url": "https://cdn.shopify.com/s/files/1/2637/1970/products/shopify_video_preview.jpg?v=1749170878"
                }
              },
              "status": "READY",
              "id": "gid://shopify/Video/723685877",
              "sources": [
                {
                  "format": "mp4",
                  "height": 1080,
                  "mimeType": "video/mp4",
                  "url": "https://cdn.shopify.com/videos/dev/vp/098dc4345e654352a24b0b033d2a3a1b/HD-1080p.mp4",
                  "width": 1920
                },
                {
                  "format": "mp4",
                  "height": 720,
                  "mimeType": "video/mp4",
                  "url": "https://cdn.shopify.com/videos/dev/vp/098dc4345e654352a24b0b033d2a3a1b/HD-720p.mp4",
                  "width": 1280
                },
                {
                  "format": "m3u8",
                  "height": 720,
                  "mimeType": "application/x-mpegURL",
                  "url": "https://cdn.shopify.com/videos/dev/vp/098dc4345e654352a24b0b033d2a3a1b/streaming.m3u8",
                  "width": 1280
                }
              ],
              "originalSource": {
                "format": "mov",
                "height": 360,
                "mimeType": "video/quicktime",
                "url": "https://cdn.shopify.com/videos/vp/03d15b89f02b4e1a97e9c5cd76bd0a6d/SD-360p.mov",
                "width": 480
              }
            }
          },
          {
            "node": {
              "alt": "This is a 3d Model",
              "mediaContentType": "MODEL_3D",
              "preview": {
                "image": {
                  "id": "gid://shopify/ImageSource/175601098",
                  "altText": "This is a 3d Model",
                  "url": "https://cdn.shopify.com/s/files/1/2637/1970/products/threed_preview_image.jpg?v=1749170878"
                }
              },
              "status": "READY",
              "sources": [
                {
                  "format": "glb",
                  "mimeType": "model/gltf-binary",
                  "url": "https://storage.googleapis.com/threed-models-test/temp.glb"
                },
                {
                  "format": "usdz",
                  "mimeType": "model/vnd.usdz+zip",
                  "url": "https://storage.googleapis.com/threed-models-test/temp.usdz"
                }
              ],
              "originalSource": {
                "format": "glb",
                "mimeType": "model/gltf-binary",
                "url": "https://storage.googleapis.com/threed-models-test/temp_original.glb"
              }
            }
          },
          {
            "node": {
              "alt": "",
              "mediaContentType": "IMAGE",
              "preview": {
                "image": {
                  "id": "gid://shopify/ImageSource/853695510",
                  "altText": "",
                  "url": "https://cdn.shopify.com/s/files/1/2637/1970/products/draft58.jpg?v=1749170878"
                }
              },
              "status": "READY",
              "id": "gid://shopify/MediaImage/853695510",
              "image": {
                "altText": "",
                "url": "https://cdn.shopify.com/s/files/1/2637/1970/products/draft58.jpg?v=1749170878"
              }
            }
          },
          {
            "node": {
              "alt": "",
              "mediaContentType": "IMAGE",
              "preview": {
                "image": {
                  "id": "gid://shopify/ImageSource/603944694",
                  "altText": "",
                  "url": "https://cdn.shopify.com/s/files/1/2637/1970/products/draft59.jpg?v=1749170878"
                }
              },
              "status": "READY",
              "id": "gid://shopify/MediaImage/603944694",
              "image": {
                "altText": "",
                "url": "https://cdn.shopify.com/s/files/1/2637/1970/products/draft59.jpg?v=1749170878"
              }
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieve the first ten collections for a product

  #### Description

  Supply the product ID to retrieve the \[collections]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection) for the product. This example returns the first ten collections for the specified product.

  #### Query

  ```graphql
  query CollectionsForProduct($productId: ID!) {
    product(id: $productId) {
      collections(first: 10) {
        nodes {
          id
          title
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/108828309"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query CollectionsForProduct($productId: ID!) { product(id: $productId) { collections(first: 10) { nodes { id title } } } }",
   "variables": {
      "productId": "gid://shopify/Product/108828309"
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
    query CollectionsForProduct($productId: ID!) {
      product(id: $productId) {
        collections(first: 10) {
          nodes {
            id
            title
          }
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/108828309"
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
    query CollectionsForProduct($productId: ID!) {
      product(id: $productId) {
        collections(first: 10) {
          nodes {
            id
            title
          }
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/108828309"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query CollectionsForProduct($productId: ID!) {
        product(id: $productId) {
          collections(first: 10) {
            nodes {
              id
              title
            }
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/108828309"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query CollectionsForProduct($productId: ID!) {
    product(id: $productId) {
      collections(first: 10) {
        nodes {
          id
          title
        }
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/108828309"
  }'
  ```

  #### Response

  ```json
  {
    "product": {
      "collections": {
        "nodes": [
          {
            "id": "gid://shopify/Collection/79210309",
            "title": "Custom Other Items"
          },
          {
            "id": "gid://shopify/Collection/94229130",
            "title": "All products more expensive than free"
          },
          {
            "id": "gid://shopify/Collection/142458073",
            "title": "All snowboards"
          },
          {
            "id": "gid://shopify/Collection/442946009",
            "title": "All products - handpicked!"
          },
          {
            "id": "gid://shopify/Collection/793607630",
            "title": "Featured items"
          },
          {
            "id": "gid://shopify/Collection/925420914",
            "title": "All snowboards called Draft"
          },
          {
            "id": "gid://shopify/Collection/1007901140",
            "title": "Featured items"
          },
          {
            "id": "gid://shopify/Collection/1063001310",
            "title": "Smart Other items"
          }
        ]
      }
    }
  }
  ```

* ### Retrieve the first ten images for a product

  #### Description

  This example demonstrates how to retrieve a product's images with \[pagination]\(https://shopify.dev/docs/api/usage/pagination-graphql), returning the first ten images. Learn more about \[managing media for products]\(https://shopify.dev/docs/apps/build/online-store/product-media).

  #### Query

  ```graphql
  query ProductImageList($productId: ID!) {
    product(id: $productId) {
      media(first: 10, query: "media_type:IMAGE", sortKey: POSITION) {
        nodes {
          id
          alt
          ... on MediaImage {
            createdAt
            image {
              width
              height
              url
            }
          }
        }
        pageInfo {
          startCursor
          endCursor
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "productId": "gid://shopify/Product/108828309"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query ProductImageList($productId: ID!) { product(id: $productId) { media(first: 10, query: \"media_type:IMAGE\", sortKey: POSITION) { nodes { id alt ... on MediaImage { createdAt image { width height url } } } pageInfo { startCursor endCursor } } } }",
   "variables": {
      "productId": "gid://shopify/Product/108828309"
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
    query ProductImageList($productId: ID!) {
      product(id: $productId) {
        media(first: 10, query: "media_type:IMAGE", sortKey: POSITION) {
          nodes {
            id
            alt
            ... on MediaImage {
              createdAt
              image {
                width
                height
                url
              }
            }
          }
          pageInfo {
            startCursor
            endCursor
          }
        }
      }
    }`,
    {
      variables: {
          "productId": "gid://shopify/Product/108828309"
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
    query ProductImageList($productId: ID!) {
      product(id: $productId) {
        media(first: 10, query: "media_type:IMAGE", sortKey: POSITION) {
          nodes {
            id
            alt
            ... on MediaImage {
              createdAt
              image {
                width
                height
                url
              }
            }
          }
          pageInfo {
            startCursor
            endCursor
          }
        }
      }
    }
  QUERY

  variables = {
    "productId": "gid://shopify/Product/108828309"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query ProductImageList($productId: ID!) {
        product(id: $productId) {
          media(first: 10, query: "media_type:IMAGE", sortKey: POSITION) {
            nodes {
              id
              alt
              ... on MediaImage {
                createdAt
                image {
                  width
                  height
                  url
                }
              }
            }
            pageInfo {
              startCursor
              endCursor
            }
          }
        }
      }`,
      "variables": {
          "productId": "gid://shopify/Product/108828309"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ProductImageList($productId: ID!) {
    product(id: $productId) {
      media(first: 10, query: "media_type:IMAGE", sortKey: POSITION) {
        nodes {
          id
          alt
          ... on MediaImage {
            createdAt
            image {
              width
              height
              url
            }
          }
        }
        pageInfo {
          startCursor
          endCursor
        }
      }
    }
  }' \
  --variables \
  '{
    "productId": "gid://shopify/Product/108828309"
  }'
  ```

  #### Response

  ```json
  {
    "product": {
      "media": {
        "nodes": [
          {
            "id": "gid://shopify/MediaImage/853695510",
            "alt": "",
            "createdAt": "2025-06-06T00:47:58Z",
            "image": {
              "width": 85,
              "height": 400,
              "url": "https://cdn.shopify.com/s/files/1/2637/1970/products/draft58.jpg?v=1749170878"
            }
          },
          {
            "id": "gid://shopify/MediaImage/603944694",
            "alt": "",
            "createdAt": "2025-06-06T00:47:58Z",
            "image": {
              "width": 85,
              "height": 400,
              "url": "https://cdn.shopify.com/s/files/1/2637/1970/products/draft59.jpg?v=1749170878"
            }
          }
        ],
        "pageInfo": {
          "startCursor": "eyJsYXN0X2lkIjo4NTM2OTU1MTAsImxhc3RfdmFsdWUiOiI0In0=",
          "endCursor": "eyJsYXN0X2lkIjo2MDM5NDQ2OTQsImxhc3RfdmFsdWUiOiI1In0="
        }
      }
    }
  }
  ```

* ### Retrieve the title, description, and online store URL of a product

  #### Description

  Supply the product ID to retrieve the title, description, and online store URL of the product. This example returns the title, description, and online store URL for the specified product.

  #### Query

  ```graphql
  query {
    product(id: "gid://shopify/Product/108828309") {
      title
      description
      onlineStoreUrl
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
  "query": "query { product(id: \"gid://shopify/Product/108828309\") { title description onlineStoreUrl } }"
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
      product(id: "gid://shopify/Product/108828309") {
        title
        description
        onlineStoreUrl
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
      product(id: "gid://shopify/Product/108828309") {
        title
        description
        onlineStoreUrl
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
      product(id: "gid://shopify/Product/108828309") {
        title
        description
        onlineStoreUrl
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    product(id: "gid://shopify/Product/108828309") {
      title
      description
      onlineStoreUrl
    }
  }'
  ```

  #### Response

  ```json
  {
    "product": {
      "title": "Draft",
      "description": "good board",
      "onlineStoreUrl": "https://www.snowdevil.ca/products/draft"
    }
  }
  ```

* ### Retrieve the total count of inventory in stock of a product

  #### Description

  Supply the product ID to retrieve the total count of inventory in stock of the product. This example returns the product title and total inventory count for the specified product.

  #### Query

  ```graphql
  query {
    product(id: "gid://shopify/Product/108828309") {
      title
      totalInventory
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
  "query": "query { product(id: \"gid://shopify/Product/108828309\") { title totalInventory } }"
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
      product(id: "gid://shopify/Product/108828309") {
        title
        totalInventory
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
      product(id: "gid://shopify/Product/108828309") {
        title
        totalInventory
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
      product(id: "gid://shopify/Product/108828309") {
        title
        totalInventory
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    product(id: "gid://shopify/Product/108828309") {
      title
      totalInventory
    }
  }'
  ```

  #### Response

  ```json
  {
    "product": {
      "title": "Draft",
      "totalInventory": 1
    }
  }
  ```

* ### Retrieve translations and localizations of a product's title and description

  #### Description

  Retrieve a product's title and description with translations (per-language overrides) and localizations (per-language, per-market overrides). This query returns the base title and description in HTML format, along with French translations and localizations. Translations and localizations are exposed separately, but the content that's actually surfaced in a particular context falls back to translations when a value isn't localized, and to the base language when a value isn't translated. Learn more about \[localizing your app]\(https://shopify.dev/docs/apps/build/localize-your-app).

  #### Query

  ```graphql
  query TranslationsAndLocalizations {
    product(id: "gid://shopify/Product/273955669") {
      title
      descriptionHtml
      translations(locale: "fr") {
        key
        value
      }
      localizations: translations(locale: "fr", marketId: "gid://shopify/Market/249692835") {
        key
        value
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
  "query": "query TranslationsAndLocalizations { product(id: \"gid://shopify/Product/273955669\") { title descriptionHtml translations(locale: \"fr\") { key value } localizations: translations(locale: \"fr\", marketId: \"gid://shopify/Market/249692835\") { key value } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query TranslationsAndLocalizations {
      product(id: "gid://shopify/Product/273955669") {
        title
        descriptionHtml
        translations(locale: "fr") {
          key
          value
        }
        localizations: translations(locale: "fr", marketId: "gid://shopify/Market/249692835") {
          key
          value
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
    query TranslationsAndLocalizations {
      product(id: "gid://shopify/Product/273955669") {
        title
        descriptionHtml
        translations(locale: "fr") {
          key
          value
        }
        localizations: translations(locale: "fr", marketId: "gid://shopify/Market/249692835") {
          key
          value
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
    data: `query TranslationsAndLocalizations {
      product(id: "gid://shopify/Product/273955669") {
        title
        descriptionHtml
        translations(locale: "fr") {
          key
          value
        }
        localizations: translations(locale: "fr", marketId: "gid://shopify/Market/249692835") {
          key
          value
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query TranslationsAndLocalizations {
    product(id: "gid://shopify/Product/273955669") {
      title
      descriptionHtml
      translations(locale: "fr") {
        key
        value
      }
      localizations: translations(locale: "fr", marketId: "gid://shopify/Market/249692835") {
        key
        value
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "product": {
      "title": "Wool sweater",
      "descriptionHtml": "<p>It is very warm!</p>",
      "translations": [
        {
          "key": "body_html",
          "value": "<p>C’est très chaud!</p>"
        },
        {
          "key": "title",
          "value": "Pull en laine"
        }
      ],
      "localizations": [
        {
          "key": "title",
          "value": "Chandail en laine"
        }
      ]
    }
  }
  ```

* ### Retrieve variants for a product

  #### Description

  Supply the product ID to retrieve the variants for the product. This example returns the variants and media for the specified product. Learn more about \[managing media for product variants]\(https://shopify.dev/docs/apps/build/online-store/product-variant-media).

  #### Query

  ```graphql
  query {
    product(id: "gid://shopify/Product/108828309") {
      title
      variants(first: 10) {
        edges {
          node {
            selectedOptions {
              name
              value
            }
            media(first: 10) {
              edges {
                node {
                  alt
                  mediaContentType
                  status
                  __typename
                  ... on MediaImage {
                    id
                    preview {
                      image {
                        originalSrc
                      }
                    }
                    __typename
                  }
                }
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
  "query": "query { product(id: \"gid://shopify/Product/108828309\") { title variants(first: 10) { edges { node { selectedOptions { name value } media(first: 10) { edges { node { alt mediaContentType status __typename ... on MediaImage { id preview { image { originalSrc } } __typename } } } } } } } } }"
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
      product(id: "gid://shopify/Product/108828309") {
        title
        variants(first: 10) {
          edges {
            node {
              selectedOptions {
                name
                value
              }
              media(first: 10) {
                edges {
                  node {
                    alt
                    mediaContentType
                    status
                    __typename
                    ... on MediaImage {
                      id
                      preview {
                        image {
                          originalSrc
                        }
                      }
                      __typename
                    }
                  }
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
      product(id: "gid://shopify/Product/108828309") {
        title
        variants(first: 10) {
          edges {
            node {
              selectedOptions {
                name
                value
              }
              media(first: 10) {
                edges {
                  node {
                    alt
                    mediaContentType
                    status
                    __typename
                    ... on MediaImage {
                      id
                      preview {
                        image {
                          originalSrc
                        }
                      }
                      __typename
                    }
                  }
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
      product(id: "gid://shopify/Product/108828309") {
        title
        variants(first: 10) {
          edges {
            node {
              selectedOptions {
                name
                value
              }
              media(first: 10) {
                edges {
                  node {
                    alt
                    mediaContentType
                    status
                    __typename
                    ... on MediaImage {
                      id
                      preview {
                        image {
                          originalSrc
                        }
                      }
                      __typename
                    }
                  }
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
    product(id: "gid://shopify/Product/108828309") {
      title
      variants(first: 10) {
        edges {
          node {
            selectedOptions {
              name
              value
            }
            media(first: 10) {
              edges {
                node {
                  alt
                  mediaContentType
                  status
                  __typename
                  ... on MediaImage {
                    id
                    preview {
                      image {
                        originalSrc
                      }
                    }
                    __typename
                  }
                }
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
    "product": {
      "title": "Draft",
      "variants": {
        "edges": [
          {
            "node": {
              "selectedOptions": [
                {
                  "name": "Title",
                  "value": "151cm"
                }
              ],
              "media": {
                "edges": [
                  {
                    "node": {
                      "alt": "",
                      "mediaContentType": "IMAGE",
                      "status": "READY",
                      "__typename": "MediaImage",
                      "id": "gid://shopify/MediaImage/853695510",
                      "preview": {
                        "image": {
                          "originalSrc": "https://cdn.shopify.com/s/files/1/2637/1970/products/draft58.jpg?v=1749170878"
                        }
                      }
                    }
                  }
                ]
              }
            }
          }
        ]
      }
    }
  }
  ```
