---
title: shop - GraphQL Admin
description: >-
  Returns the Shop resource corresponding to the access token used in the
  request. The Shop resource contains

  business and store management settings for the shop.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/shop'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/shop.md'
---

# shop

query

Returns the Shop resource corresponding to the access token used in the request. The Shop resource contains business and store management settings for the shop.

## Possible returns

* Shop

  [Shop!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Shop)

  The central configuration and settings hub for a Shopify store. Access business information, operational preferences, feature availability, and store-wide settings that control how the shop operates.

  Includes core business details like the shop name, contact emails, billing address, and currency settings. The shop configuration determines customer account requirements, available sales channels, enabled features, payment settings, and policy documents. Also provides access to shop-level resources such as staff members, fulfillment services, navigation settings, and storefront access tokens.

  * account​Owner

    [Staff​Member!](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember)

    non-null

    Account owner information.

  * alerts

    [\[Shop​Alert!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopAlert)

    non-null

    A list of the shop's active alert messages that appear in the Shopify admin.

  * all​Product​Categories​List

    [\[Taxonomy​Category!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TaxonomyCategory)

    non-null

    A list of the shop's product categories. Limit: 1000 product categories.

  * available​Channel​Apps

    [App​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/AppConnection)

    non-null

    The list of sales channels not currently installed on the shop.

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

  * channel​Definitions​For​Installed​Channels

    [\[Available​Channel​Definitions​By​Channel!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AvailableChannelDefinitionsByChannel)

    non-null

    List of all channel definitions associated with a shop.

  * checkout​Api​Supported

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Specifies whether the shop supports checkouts via Checkout API.

  * contact​Email

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The public-facing contact email address for the shop. Customers will use this email to communicate with the shop owner.

  * countries​In​Shipping​Zones

    [Countries​In​Shipping​Zones!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CountriesInShippingZones)

    non-null

    Countries that have been defined in shipping zones for the shop.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the shop was created.

  * currency​Code

    [Currency​Code!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CurrencyCode)

    non-null

    The three letter code for the currency that the shop sells in.

  * currency​Formats

    [Currency​Formats!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CurrencyFormats)

    non-null

    How currencies are displayed on your store.

  * currency​Settings

    [Currency​Setting​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CurrencySettingConnection)

    non-null

    The presentment currency settings for the shop excluding the shop's own currency.

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

  * customer​Accounts

    [Shop​Customer​Accounts​Setting!](https://shopify.dev/docs/api/admin-graphql/latest/enums/ShopCustomerAccountsSetting)

    non-null

    Whether customer accounts are required, optional, or disabled for the shop.

  * customer​Accounts​V2

    [Customer​Accounts​V2!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerAccountsV2)

    non-null

    Information about the shop's customer accounts.

  * customer​Tags

    [String​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/StringConnection)

    non-null

    A list of tags that have been added to customer accounts.

    * first

      [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      required

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    ***

  * description

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The shop's meta description used in search engine results.

  * draft​Order​Tags

    [String​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/StringConnection)

    non-null

    A list of tags that have been added to draft orders.

    * first

      [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      required

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    ***

  * email

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The shop owner's email address. Shopify will use this email address to communicate with the shop owner.

  * enabled​Presentment​Currencies

    [\[Currency​Code!\]!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CurrencyCode)

    non-null

    The presentment currencies enabled for the shop.

  * entitlements

    [Entitlements​Type!](https://shopify.dev/docs/api/admin-graphql/latest/objects/EntitlementsType)

    non-null

    The entitlements for a shop.

  * features

    [Shop​Features!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopFeatures)

    non-null

    The set of features enabled for the shop.

  * fulfillment​Services

    [\[Fulfillment​Service!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentService)

    non-null

    List of the shop's installed fulfillment services.

  * iana​Timezone

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The shop's time zone as defined by the IANA.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * marketing​Sms​Consent​Enabled​At​Checkout

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether SMS marketing has been enabled on the shop's checkout configuration settings.

  * merchant​Approval​Signals

    [Merchant​Approval​Signals](https://shopify.dev/docs/api/admin-graphql/latest/objects/MerchantApprovalSignals)

    The approval signals for a shop to support onboarding to channel apps.

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

  * myshopify​Domain

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The shop's .myshopify.com domain name.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The shop's name.

  * navigation​Settings

    [\[Navigation​Item!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/NavigationItem)

    non-null

    The shop's settings related to navigation.

  * order​Number​Format​Prefix

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The prefix that appears before order numbers.

  * order​Number​Format​Suffix

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The suffix that appears after order numbers.

  * order​Tags

    [String​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/StringConnection)

    non-null

    A list of tags that have been added to orders.

    * first

      [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      required

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * sort

      [Shop​Tag​Sort](https://shopify.dev/docs/api/admin-graphql/latest/enums/ShopTagSort)

      Default:ALPHABETICAL

      Sort type.

    ***

  * payment​Settings

    [Payment​Settings!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentSettings)

    non-null

    The shop's settings related to payments.

  * plan

    [Shop​Plan!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopPlan)

    non-null

    The shop's billing plan.

  * primary​Domain

    [Domain!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Domain)

    non-null

    The primary domain of the shop's online store.

  * resource​Limits

    [Shop​Resource​Limits!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopResourceLimits)

    non-null

    The shop's limits for specific resources. For example, the maximum number ofvariants allowed per product, or the maximum number of locations allowed.

  * rich​Text​Editor​Url

    [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    non-null

    The URL of the rich text editor that can be used for mobile devices.

  * search

    [Search​Result​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SearchResultConnection)

    non-null

    Fetches a list of admin search results by a specified query.

    * query

      [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      required

      ### Arguments

      The search query to filter by.

    * types

      [\[Search​Result​Type!\]](https://shopify.dev/docs/api/admin-graphql/latest/enums/SearchResultType)

      The search result types to filter by.

    * first

      [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      required

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    ***

  * search​Filters

    [Search​Filter​Options!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SearchFilterOptions)

    non-null

    The list of search filter options for the shop. These can be used to filter productvisibility for the shop.

  * setup​Required

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the shop has outstanding setup steps.

  * ships​To​Countries

    [\[Country​Code!\]!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CountryCode)

    non-null

    The list of countries that the shop ships to.

  * shop​Address

    [Shop​Address!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopAddress)

    non-null

    The shop's address information as it will appear to buyers.

  * shop​Owner​Name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of the shop owner.

  * shop​Policies

    [\[Shop​Policy!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopPolicy)

    non-null

    The list of all legal policies associated with a shop.

  * storefront​Access​Tokens

    [Storefront​Access​Token​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/StorefrontAccessTokenConnection)

    non-null

    The storefront access token of a private application. These are scoped per-application.

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

  * taxes​Included

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether applicable taxes are included in the shop's product prices.

  * tax​Shipping

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the shop charges taxes for shipping.

  * timezone​Abbreviation

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The shop's time zone abbreviation.

  * timezone​Offset

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The shop's time zone offset.

  * timezone​Offset​Minutes

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The shop's time zone offset expressed as a number of minutes.

  * transactional​Sms​Disabled

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether transactional SMS sent by Shopify have been disabled for a shop.

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

  * unit​System

    [Unit​System!](https://shopify.dev/docs/api/admin-graphql/latest/enums/UnitSystem)

    non-null

    The shop's unit system for weights and measures.

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the shop was last updated.

  * url

    [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    non-null

    The URL of the shop's online store.

  * weight​Unit

    [Weight​Unit!](https://shopify.dev/docs/api/admin-graphql/latest/enums/WeightUnit)

    non-null

    The shop's primary unit of weight for products and shipping.

  * all​Product​Categories

    [\[Product​Category!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductCategory)

    non-nullDeprecated

  * analytics​Token

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-nullDeprecated

  * assigned​Fulfillment​Orders

    [Fulfillment​Order​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/FulfillmentOrderConnection)

    non-nullDeprecated

    * assignment​Status

      [Fulfillment​Order​Assignment​Status](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentOrderAssignmentStatus)

      ### Arguments

      The assigment status of the fulfillment orders that should be returned. If `assignmentStatus` argument is not provided, then the query will return all assigned fulfillment orders, except those that have the `CLOSED` status.

    * location​Ids

      [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      Returns fulfillment orders only for certain locations, specified by a list of location IDs.

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

      [Fulfillment​Order​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentOrderSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    ***

  * billing​Address

    [Shop​Address!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopAddress)

    non-nullDeprecated

  * channels

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

  * collections

    [Collection​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CollectionConnection)

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

    * saved​Search​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      The ID of a [saved search](https://shopify.dev/api/admin-graphql/latest/objects/savedsearch#field-id). The search’s query string is used as the query argument.

    ***

  * customers

    [Customer​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CustomerConnection)

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

    * sort​Key

      [Customer​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/CustomerSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * default

          string

        * accepts\_marketing

          boolean

        * country

          string

        * customer\_date

          time

        * email

          string

        * first\_name

          string

        * id

          id

        * last\_abandoned\_order\_date

          time

        * last\_name

          string

        * order\_date

          time

        * orders\_count

          integer

        * phone

          string

        * state

          string

        * tag

          string

        * tag\_not

          string

        * total\_spent

          float

        * updated\_at

          time

        - Filter by a case-insensitive search of multiple fields in a document.

        - Example:

          * `query=Bob Norman`
          * `query=title:green hoodie`

          Filter by whether a customer has consented to receive marketing material.

        - Example:

          * `accepts_marketing:true`

          Filter by the country associated with the customer's address. Use either the country name or the two-letter country code.

        - Example:

          * `country:Canada`
          * `country:JP`

          Filter by the date and time when the customer record was created. This query parameter filters by the [`createdAt`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer#field-createdAt) field.

        - Example:

          * `customer_date:'2024-03-15T14:30:00Z'`
          * `customer_date: >='2024-01-01'`

          The customer's email address, used to communicate information about orders and for the purposes of email marketing campaigns. You can use a wildcard value to filter the query by customers who have an email address specified. Please note that *email* is a tokenized field: To retrieve exact matches, quote the email address (*phrase query*) as described in [Shopify API search syntax](https://shopify.dev/docs/api/usage/search-syntax).

        - Example:

          * `email:gmail.com`
          * `email:"bo.wang@example.com"`
          * `email:*`

          Filter by the customer's first name.

        - Example:

          * `first_name:Jane`

          Filter by `id` range.

        - Example:

          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

          Filter by the date and time of the customer's most recent abandoned checkout. An abandoned checkout occurs when a customer adds items to their cart, begins the checkout process, but leaves the site without completing their purchase.

        - Example:

          * `last_abandoned_order_date:'2024-04-01T10:00:00Z'`
          * `last_abandoned_order_date: >='2024-01-01'`

          Filter by the customer's last name.

        - Example:

          * `last_name:Reeves`

          Filter by the date and time that the order was placed by the customer. Use this query filter to check if a customer has placed at least one order within a specified date range.

        - Example:

          * `order_date:'2024-02-20T00:00:00Z'`
          * `order_date: >='2024-01-01'`
          * `order_date:'2024-01-01..2024-03-31'`

          Filter by the total number of orders a customer has placed.

        - Example:

          * `orders_count:5`

          The phone number of the customer, used to communicate information about orders and for the purposes of SMS marketing campaigns. You can use a wildcard value to filter the query by customers who have a phone number specified.

        - Example:

          * `phone:+18005550100`
          * `phone:*`

          Filter by the [state](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer#field-state) of the customer's account with the shop. This filter is only valid when [Classic Customer Accounts](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerAccountsV2#field-customerAccountsVersion) is active.

        - Example:

          * `state:ENABLED`
          * `state:INVITED`
          * `state:DISABLED`
          * `state:DECLINED`

          Filter by the tags that are associated with the customer. This query parameter accepts multiple tags separated by commas.

        - Example:

          * `tag:'VIP'`
          * `tag:'Wholesale,Repeat'`

          Filter by the tags that aren't associated with the customer. This query parameter accepts multiple tags separated by commas.

        - Example:

          * `tag_not:'Prospect'`
          * `tag_not:'Test,Internal'`

          Filter by the total amount of money a customer has spent across all orders.

        - Example:

          * `total_spent:100.50`
          * `total_spent:50.00`
          * `total_spent:>100.50`
          * `total_spent:>50.00`

          The date and time, matching a whole day, when the customer's information was last updated.

          Example:

          * `updated_at:2024-01-01T00:00:00Z`
          * `updated_at:<now`
          * `updated_at:<=2024`

    ***

  * domains

    [\[Domain!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Domain)

    non-nullDeprecated

  * fulfillment​Orders

    [Fulfillment​Order​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/FulfillmentOrderConnection)

    non-nullDeprecated

    * include​Closed

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      ### Arguments

      Whether to include closed fulfillment orders.

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

      [Fulfillment​Order​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentOrderSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * default

          string

        * assigned\_location\_id

          id

        - Filter by a case-insensitive search of multiple fields in a document.

        - Example:
          * `query=Bob Norman`
          * `query=title:green hoodie`

      * * id

          id

        * status

          string

        - Filter by `id` range.

        - Example:
          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

      * updated\_at

        time

    ***

  * inventory​Items

    [Inventory​Item​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/InventoryItemConnection)

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

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * created\_at

        time

      * * id

          id

        * sku

          string

        * updated\_at

          time

        - Filter by `id` range.

        - Example:

          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

          Filter by the inventory item [`sku`](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem#field-sku) field. [Learn more about SKUs](https://help.shopify.com/manual/products/details/sku).

        - Example:
          * `sku:XYZ-12345`

    ***

  * limited​Pending​Order​Count

    [Limited​Pending​Order​Count!](https://shopify.dev/docs/api/admin-graphql/latest/objects/LimitedPendingOrderCount)

    non-nullDeprecated

  * locations

    [Location​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/LocationConnection)

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

    * sort​Key

      [Location​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/LocationSortKeys)

      Default:NAME

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * default

          string

        * active

          string

        - Filter by a case-insensitive search of multiple fields in a document.

        - Example:
          * `query=Bob Norman`
          * `query=title:green hoodie`

      * address1

        string

      * address2

        string

      * city

        string

      * country

        string

      * created\_at

        time

      * geolocated

        boolean

      * * id

          id

        * legacy

          boolean

        - Filter by `id` range.

        - Example:
          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

      * location\_id

        id

      * name

        string

      * * pickup\_in\_store

          string

        * province

          string

        -
        - Valid values:
          * `enabled`
          * `disabled`

      * zip

        string

    * include​Legacy

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Whether to include the legacy locations of fulfillment services.

    * include​Inactive

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Whether to include the locations that are deactivated.

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

  * orders

    [Order​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/OrderConnection)

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

    * sort​Key

      [Order​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/OrderSortKeys)

      Default:PROCESSED\_AT

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * * default

          string

        * cart\_token

          string

        * channel

          string

        * channel\_id

          id

        * chargeback\_status

          string

        * checkout\_token

          string

        * confirmation\_number

          string

        * created\_at

          time

        * credit\_card\_last4

          string

        * current\_total\_price

          float

        * customer\_id

          id

        * delivery\_method

          string

        * discount\_code

          string

        * email

          string

        * financial\_status

          string

        * fraud\_protection\_level

          string

        * fulfillment\_location\_id

          id

        * fulfillment\_status

          string

        * gateway

          string

        * id

          id

        * location\_id

          id

        * metafields.{namespace}.{key}

          mixed

        * name

          string

        * payment\_id

          string

        * payment\_provider\_id

          id

        * po\_number

          string

        * processed\_at

          time

        * reference\_location\_id

          id

        * return\_status

          string

        * risk\_level

          string

        * sales\_channel

          string

        * sku

          string

        * source\_identifier

          string

        * source\_name

          string

        * status

          string

        * subtotal\_line\_items\_quantity

          string

        * tag

          string

        * tag\_not

          string

        * test

          boolean

        * total\_weight

          string

        * updated\_at

          time

        - Filter by a case-insensitive search of multiple fields in a document.

        - Example:

          * `query=Bob Norman`
          * `query=title:green hoodie`

          Filter by the cart token's unique value to track abandoned cart conversions or troubleshoot checkout issues. The token references the cart that's associated with an order.

        - Example:

          * `cart_token:abc123`

          Filter by the channel information [`handle`](https://shopify.dev/api/admin-graphql/latest/objects/ChannelInformation#field-ChannelInformation.fields.channelDefinition.handle) (`ChannelInformation.channelDefinition.handle`) field.

        - Example:

          * `channel:web`
          * `channel:web,pos`

          Filter by the channel [`id`](https://shopify.dev/api/admin-graphql/latest/objects/Channel#field-Channel.fields.id) field.

        - Example:

          * `channel_id:123`

          Filter by the order's chargeback status. A chargeback occurs when a customer questions the legitimacy of a charge with their financial institution.

        - Valid values:

          * `accepted`
          * `charge_refunded`
          * `lost`
          * `needs_response`
          * `under_review`
          * `won`

          Example:

          * `chargeback_status:accepted`

          Filter by the checkout token's unique value to analyze conversion funnels or resolve payment issues. The checkout token's value references the checkout that's associated with an order.

        - Example:

          * `checkout_token:abc123`

          Filter by the randomly generated alpha-numeric identifier for an order that can be displayed to the customer instead of the sequential order name. This value isn't guaranteed to be unique.

        - Example:

          * `confirmation_number:ABC123`

          Filter by the date and time when the order was created in Shopify's system.

        - Example:

          * `created_at:2020-10-21T23:39:20Z`
          * `created_at:<now`
          * `created_at:<=2024`

          Filter by the last four digits of the payment card that was used to pay for the order. This filter matches only the last four digits of the card for heightened security.

        - Example:

          * `credit_card_last4:1234`

          Filter by the current total price of the order in the shop currency, including any returns/refunds/removals. This filter supports both exact values and ranges.

        - Example:

          * `current_total_price:10`
          * `current_total_price:>=5.00 current_total_price:<=20.99`

          Filter orders by the customer [`id`](https://shopify.dev/api/admin-graphql/latest/objects/Customer#field-Customer.fields.id) field.

        - Example:

          * `customer_id:123`

          Filter by the delivery [`methodType`](https://shopify.dev/api/admin-graphql/2024-07/objects/DeliveryMethod#field-DeliveryMethod.fields.methodType) field.

        - Valid values:

          * `shipping`
          * `pick-up`
          * `retail`
          * `local`
          * `pickup-point`
          * `none`

          Example:

          * `delivery_method:shipping`

          Filter by the case-insensitive discount code that was applied to the order at checkout. Limited to the first discount code used on an order. Maximum characters: 255.

        - Example:

          * `discount_code:ABC123`

          Filter by the email address that's associated with the order to provide customer support or analyze purchasing patterns.

        - Example:

          * `email:example@shopify.com`

          Filter by the order [`displayFinancialStatus`](https://shopify.dev/api/admin-graphql/latest/objects/Order#field-Order.fields.displayFinancialStatus) field.

        - Valid values:

          * `paid`
          * `pending`
          * `authorized`
          * `partially_paid`
          * `partially_refunded`
          * `refunded`
          * `voided`
          * `expired`

          Example:

          * `financial_status:authorized`

          Filter by the level of fraud protection that's applied to the order. Use this filter to manage risk or handle disputes.

        - Valid values:

          * `fully_protected`
          * `partially_protected`
          * `not_protected`
          * `pending`
          * `not_eligible`
          * `not_available`

          Example:

          * `fraud_protection_level:fully_protected`

          Filter by the fulfillment location [`id`](https://shopify.dev/api/admin-graphql/latest/objects/Fulfillment#field-Fulfillment.fields.location.id) (`Fulfillment.location.id`) field.

        - Example:

          * `fulfillment_location_id:123`

          Filter by the [`displayFulfillmentStatus`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order#field-Order.fields.displayFulfillmentStatus) field to prioritize shipments or monitor order processing.

        - Valid values:

          * `unshipped`
          * `shipped`
          * `fulfilled`
          * `partial`
          * `scheduled`
          * `on_hold`
          * `unfulfilled`
          * `request_declined`

          Example:

          * `fulfillment_status:fulfilled`

          Filter by the [`paymentGatewayNames`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order#field-Order.fields.paymentGatewayNames) field. Use this filter to find orders that were processed through specific payment providers like Shopify Payments, PayPal, or other custom payment gateways.

        - Example:

          * `gateway:shopify_payments`

          Filter by `id` range.

        - Example:

          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

          Filter by the location [`id`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location#field-Location.fields.id) that's associated with the order to view and manage orders for specific locations. For POS orders, locations must be defined in the Shopify admin under **Settings** > **Locations**. If no ID is provided, then the primary location of the shop is returned.

        - Example:

          * `location_id:123`

          Filters resources by metafield value. Format: `metafields.{namespace}.{key}:{value}`. Learn more about [querying by metafield value](https://shopify.dev/apps/build/custom-data/metafields/query-by-metafield-value).

        - Example:

          * `metafields.custom.on_sale:true`
          * `metafields.product.material:"gid://shopify/Metaobject/43458085"`

          Filter by the order [`name`](https://shopify.dev/api/admin-graphql/latest/objects/Order#field-name) field.

        - Example:

          * `name:1001-A`

          Filter by the payment ID that's associated with the order to reconcile financial records or troubleshoot payment issues.

        - Example:

          * `payment_id:abc123`

          Filter by the ID of the payment provider that's associated with the order to manage payment methods or troubleshoot transactions.

        - Example:

          * `payment_provider_id:123`

          Filter by the order [`poNumber`](https://shopify.dev/api/admin-graphql/latest/objects/order#field-Order.fields.poNumber) field.

        - Example:

          * `po_number:P01001`

          Filter by the order [`processedAt`](https://shopify.dev/api/admin-graphql/latest/objects/order#field-Order.fields.processedAt) field.

        - Example:

          * `processed_at:2021-01-01T00:00:00Z`

          Filter by the ID of a location that's associated with the order, such as locations from fulfillments, refunds, or the shop's primary location.

        - Example:

          * `reference_location_id:123`

          Filter by the order's [`returnStatus`](https://shopify.dev/api/admin-graphql/latest/objects/Order#field-Order.fields.returnStatus) to monitor returns processing and track which orders have active returns.

        - Valid values:

          * `return_requested`
          * `in_progress`
          * `inspection_complete`
          * `returned`
          * `return_failed`
          * `no_return`

          Example:

          * `return_status:in_progress`

          Filter by the order risk assessment [`riskLevel`](https://shopify.dev/api/admin-graphql/latest/objects/OrderRiskAssessment#field-OrderRiskAssessment.fields.riskLevel) field.

        - Valid values:

          * `high`
          * `medium`
          * `low`
          * `none`
          * `pending`

          Example:

          * `risk_level:high`

          Filter by the [sales channel](https://shopify.dev/docs/apps/build/sales-channels) where the order was made to analyze performance or manage fulfillment processes.

        - Example:

          * `sales_channel: some_sales_channel`

          Filter by the product variant [`sku`](https://shopify.dev/api/admin-graphql/latest/objects/ProductVariant#field-ProductVariant.fields.sku) field. [Learn more about SKUs](https://help.shopify.com/manual/products/details/sku).

        - Example:

          * `sku:ABC123`

          Filter by the ID of the order placed on the originating platform, such as a unique POS or third-party identifier. This value doesn't correspond to the Shopify ID that's generated from a completed draft order.

        - Example:

          * `source_identifier:1234-12-1000`

          Filter by the platform where the order was placed to distinguish between web orders, POS sales, draft orders, or third-party channels. Use this filter to analyze sales performance across different ordering methods.

        - Example:

          * `source_name:web`
          * `source_name:shopify_draft_order`

          Filter by the order's status to manage workflows or analyze the order lifecycle.

        - Valid values:

          * `open`
          * `closed`
          * `cancelled`
          * `not_closed`

          Example:

          * `status:open`

          Filter by the total number of items across all line items in an order. This filter supports both exact values and ranges, and is useful for identifying bulk orders or analyzing purchase volume patterns.

        - Example:

          * `subtotal_line_items_quantity:10`
          * `subtotal_line_items_quantity:5..20`

          Filter objects by the `tag` field.

        - Example:

          * `tag:my_tag`

          Filter by objects that don’t have the specified tag.

        - Example:

          * `tag_not:my_tag`

          Filter by test orders. Test orders are made using the [Shopify Bogus Gateway](https://help.shopify.com/manual/checkout-settings/test-orders/payments-test-mode#bogus-gateway) or a payment provider with test mode enabled.

        - Example:

          * `test:true`

          Filter by the order weight. This filter supports both exact values and ranges, and is to be used to filter orders by the total weight of all items (excluding packaging). It takes a unit of measurement as a suffix. It accepts the following units: g, kg, lb, oz.

        - Example:

          * `total_weight:10.5kg`
          * `total_weight:>=5g total_weight:<=20g`
          * `total_weight:.5 lb`

          Filter by the date and time when the order was last updated in Shopify's system.

          Example:

          * `updated_at:2020-10-21T23:39:20Z`
          * `updated_at:<now`
          * `updated_at:<=2024`

    ***

  * product​Images

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

      Default:CREATED\_AT

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

    ***

  * products

    [Product​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductConnection)

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

  * product​Tags

    [String​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/StringConnection)

    non-nullDeprecated

    * first

      [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      required

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    ***

  * product​Types

    [String​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/StringConnection)

    non-nullDeprecated

    * first

      [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      required

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    ***

  * product​Variants

    [Product​Variant​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ProductVariantConnection)

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

    * sort​Key

      [Product​Variant​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProductVariantSortKeys)

      Default:ID

      Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

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

    ***

  * product​Vendors

    [String​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/StringConnection)

    non-nullDeprecated

    * first

      [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      required

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    ***

  * publication​Count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-nullDeprecated

  * staff​Members

    [Staff​Member​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/StaffMemberConnection)

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

  * storefront​Url

    [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    non-nullDeprecated

***

## Examples

* ### Get a metafield attached to a shop

  #### Description

  Get the metafield value identified by \`my\_fields.copyright\_year\` on a specific shop.

  #### Query

  ```graphql
  query ShopMetafield($namespace: String!, $key: String!) {
    shop {
      copyrightYear: metafield(namespace: $namespace, key: $key) {
        value
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "namespace": "my_fields",
    "key": "copyright_year"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query ShopMetafield($namespace: String!, $key: String!) { shop { copyrightYear: metafield(namespace: $namespace, key: $key) { value } } }",
   "variables": {
      "namespace": "my_fields",
      "key": "copyright_year"
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
    query ShopMetafield($namespace: String!, $key: String!) {
      shop {
        copyrightYear: metafield(namespace: $namespace, key: $key) {
          value
        }
      }
    }`,
    {
      variables: {
          "namespace": "my_fields",
          "key": "copyright_year"
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
    query ShopMetafield($namespace: String!, $key: String!) {
      shop {
        copyrightYear: metafield(namespace: $namespace, key: $key) {
          value
        }
      }
    }
  QUERY

  variables = {
    "namespace": "my_fields",
    "key": "copyright_year"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query ShopMetafield($namespace: String!, $key: String!) {
        shop {
          copyrightYear: metafield(namespace: $namespace, key: $key) {
            value
          }
        }
      }`,
      "variables": {
          "namespace": "my_fields",
          "key": "copyright_year"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ShopMetafield($namespace: String!, $key: String!) {
    shop {
      copyrightYear: metafield(namespace: $namespace, key: $key) {
        value
      }
    }
  }' \
  --variables \
  '{
    "namespace": "my_fields",
    "key": "copyright_year"
  }'
  ```

  #### Response

  ```json
  {
    "shop": {
      "copyrightYear": {
        "value": "2022"
      }
    }
  }
  ```

* ### Get metafields attached to a shop

  #### Description

  Get a page of metafields attached to a specific shop.

  #### Query

  ```graphql
  query ShopMetafields {
    shop {
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
  {}
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query ShopMetafields { shop { metafields(first: 3) { edges { node { namespace key value } } } } }",
   "variables": {}
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query ShopMetafields {
      shop {
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
      variables: {},
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
    query ShopMetafields {
      shop {
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

  variables = {}

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query ShopMetafields {
        shop {
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
      "variables": {},
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ShopMetafields {
    shop {
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
  }'
  ```

  #### Response

  ```json
  {
    "shop": {
      "metafields": {
        "edges": [
          {
            "node": {
              "namespace": "my_fields",
              "key": "copyright_year",
              "value": "2022"
            }
          }
        ]
      }
    }
  }
  ```

* ### Receive a list of all FulfillmentServices

  #### Query

  ```graphql
  query FulfillmentServiceList {
    shop {
      fulfillmentServices {
        id
        callbackUrl
        fulfillmentOrdersOptIn
        permitsSkuSharing
        handle
        inventoryManagement
        serviceName
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
  "query": "query FulfillmentServiceList { shop { fulfillmentServices { id callbackUrl fulfillmentOrdersOptIn permitsSkuSharing handle inventoryManagement serviceName } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query FulfillmentServiceList {
      shop {
        fulfillmentServices {
          id
          callbackUrl
          fulfillmentOrdersOptIn
          permitsSkuSharing
          handle
          inventoryManagement
          serviceName
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
    query FulfillmentServiceList {
      shop {
        fulfillmentServices {
          id
          callbackUrl
          fulfillmentOrdersOptIn
          permitsSkuSharing
          handle
          inventoryManagement
          serviceName
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
    data: `query FulfillmentServiceList {
      shop {
        fulfillmentServices {
          id
          callbackUrl
          fulfillmentOrdersOptIn
          permitsSkuSharing
          handle
          inventoryManagement
          serviceName
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query FulfillmentServiceList {
    shop {
      fulfillmentServices {
        id
        callbackUrl
        fulfillmentOrdersOptIn
        permitsSkuSharing
        handle
        inventoryManagement
        serviceName
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "shop": {
      "fulfillmentServices": [
        {
          "id": "gid://shopify/FulfillmentService/manual",
          "callbackUrl": null,
          "fulfillmentOrdersOptIn": false,
          "permitsSkuSharing": true,
          "handle": "manual",
          "inventoryManagement": false,
          "serviceName": "Manual"
        },
        {
          "id": "gid://shopify/FulfillmentService/18961920?id=true",
          "callbackUrl": "http://shipwire.com",
          "fulfillmentOrdersOptIn": true,
          "permitsSkuSharing": true,
          "handle": "shipwire",
          "inventoryManagement": false,
          "serviceName": "Shipwire"
        },
        {
          "id": "gid://shopify/FulfillmentService/198258461?id=true",
          "callbackUrl": "http://google.com",
          "fulfillmentOrdersOptIn": true,
          "permitsSkuSharing": false,
          "handle": "on-demand-delivery",
          "inventoryManagement": false,
          "serviceName": "On Demand Delivery"
        },
        {
          "id": "gid://shopify/FulfillmentService/736057333?id=true",
          "callbackUrl": null,
          "fulfillmentOrdersOptIn": false,
          "permitsSkuSharing": false,
          "handle": "mr-acme-drop-shipper",
          "inventoryManagement": false,
          "serviceName": "Mr. ACME Drop Shipper"
        },
        {
          "id": "gid://shopify/FulfillmentService/1061774486?id=true",
          "callbackUrl": null,
          "fulfillmentOrdersOptIn": false,
          "permitsSkuSharing": false,
          "handle": "mr-drop-shipper",
          "inventoryManagement": false,
          "serviceName": "Mr. Drop Shipper"
        }
      ]
    }
  }
  ```

* ### Retrieve information about a shop

  #### Description

  The following query retrieves some shop settings.

  #### Query

  ```graphql
  query {
    shop {
      name
      currencyCode
      checkoutApiSupported
      taxesIncluded
      resourceLimits {
        maxProductVariants
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
  "query": "query { shop { name currencyCode checkoutApiSupported taxesIncluded resourceLimits { maxProductVariants } } }"
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
      shop {
        name
        currencyCode
        checkoutApiSupported
        taxesIncluded
        resourceLimits {
          maxProductVariants
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
      shop {
        name
        currencyCode
        checkoutApiSupported
        taxesIncluded
        resourceLimits {
          maxProductVariants
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
      shop {
        name
        currencyCode
        checkoutApiSupported
        taxesIncluded
        resourceLimits {
          maxProductVariants
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
    shop {
      name
      currencyCode
      checkoutApiSupported
      taxesIncluded
      resourceLimits {
        maxProductVariants
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "shop": {
      "name": "Snowdevil",
      "currencyCode": "USD",
      "checkoutApiSupported": true,
      "taxesIncluded": false,
      "resourceLimits": {
        "maxProductVariants": 100
      }
    }
  }
  ```

* ### Retrieves a list of fulfillment orders assigned to the shop locations that are owned by the app

  #### Query

  ```graphql
  query AssignedFulfillmentOrderList($assignmentStatus: FulfillmentOrderAssignmentStatus) {
    shop {
      assignedFulfillmentOrders(first: 10, assignmentStatus: $assignmentStatus) {
        edges {
          node {
            id
            status
            requestStatus
            destination {
              firstName
              lastName
              address1
              city
              province
              zip
              countryCode
              phone
            }
            lineItems(first: 10) {
              edges {
                node {
                  id
                  productTitle
                  sku
                  remainingQuantity
                }
              }
            }
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "assignmentStatus": "FULFILLMENT_REQUESTED"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query AssignedFulfillmentOrderList($assignmentStatus: FulfillmentOrderAssignmentStatus) { shop { assignedFulfillmentOrders(first: 10, assignmentStatus: $assignmentStatus) { edges { node { id status requestStatus destination { firstName lastName address1 city province zip countryCode phone } lineItems(first: 10) { edges { node { id productTitle sku remainingQuantity } } } } } } } }",
   "variables": {
      "assignmentStatus": "FULFILLMENT_REQUESTED"
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
    query AssignedFulfillmentOrderList($assignmentStatus: FulfillmentOrderAssignmentStatus) {
      shop {
        assignedFulfillmentOrders(first: 10, assignmentStatus: $assignmentStatus) {
          edges {
            node {
              id
              status
              requestStatus
              destination {
                firstName
                lastName
                address1
                city
                province
                zip
                countryCode
                phone
              }
              lineItems(first: 10) {
                edges {
                  node {
                    id
                    productTitle
                    sku
                    remainingQuantity
                  }
                }
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "assignmentStatus": "FULFILLMENT_REQUESTED"
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
    query AssignedFulfillmentOrderList($assignmentStatus: FulfillmentOrderAssignmentStatus) {
      shop {
        assignedFulfillmentOrders(first: 10, assignmentStatus: $assignmentStatus) {
          edges {
            node {
              id
              status
              requestStatus
              destination {
                firstName
                lastName
                address1
                city
                province
                zip
                countryCode
                phone
              }
              lineItems(first: 10) {
                edges {
                  node {
                    id
                    productTitle
                    sku
                    remainingQuantity
                  }
                }
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "assignmentStatus": "FULFILLMENT_REQUESTED"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query AssignedFulfillmentOrderList($assignmentStatus: FulfillmentOrderAssignmentStatus) {
        shop {
          assignedFulfillmentOrders(first: 10, assignmentStatus: $assignmentStatus) {
            edges {
              node {
                id
                status
                requestStatus
                destination {
                  firstName
                  lastName
                  address1
                  city
                  province
                  zip
                  countryCode
                  phone
                }
                lineItems(first: 10) {
                  edges {
                    node {
                      id
                      productTitle
                      sku
                      remainingQuantity
                    }
                  }
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "assignmentStatus": "FULFILLMENT_REQUESTED"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query AssignedFulfillmentOrderList($assignmentStatus: FulfillmentOrderAssignmentStatus) {
    shop {
      assignedFulfillmentOrders(first: 10, assignmentStatus: $assignmentStatus) {
        edges {
          node {
            id
            status
            requestStatus
            destination {
              firstName
              lastName
              address1
              city
              province
              zip
              countryCode
              phone
            }
            lineItems(first: 10) {
              edges {
                node {
                  id
                  productTitle
                  sku
                  remainingQuantity
                }
              }
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "assignmentStatus": "FULFILLMENT_REQUESTED"
  }'
  ```

  #### Response

  ```json
  {
    "shop": {
      "assignedFulfillmentOrders": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/FulfillmentOrder/1046001474",
              "status": "OPEN",
              "requestStatus": "SUBMITTED",
              "destination": null,
              "lineItems": {
                "edges": []
              }
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieves a list of all users

  #### Query

  ```graphql
  query {
    shop {
      staffMembers(first: 10) {
        edges {
          node {
            active
            avatar {
              url
            }
            email
            exists
            firstName
            id
            initials
            isShopOwner
            lastName
            locale
            name
            phone
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
  "query": "query { shop { staffMembers(first: 10) { edges { node { active avatar { url } email exists firstName id initials isShopOwner lastName locale name phone } } } } }"
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
      shop {
        staffMembers(first: 10) {
          edges {
            node {
              active
              avatar {
                url
              }
              email
              exists
              firstName
              id
              initials
              isShopOwner
              lastName
              locale
              name
              phone
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
      shop {
        staffMembers(first: 10) {
          edges {
            node {
              active
              avatar {
                url
              }
              email
              exists
              firstName
              id
              initials
              isShopOwner
              lastName
              locale
              name
              phone
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
      shop {
        staffMembers(first: 10) {
          edges {
            node {
              active
              avatar {
                url
              }
              email
              exists
              firstName
              id
              initials
              isShopOwner
              lastName
              locale
              name
              phone
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
    shop {
      staffMembers(first: 10) {
        edges {
          node {
            active
            avatar {
              url
            }
            email
            exists
            firstName
            id
            initials
            isShopOwner
            lastName
            locale
            name
            phone
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "shop": {
      "staffMembers": {
        "edges": [
          {
            "node": {
              "active": true,
              "avatar": {
                "url": "https://cdn.shopify.com/proxy/106ea358a244c6081c66489854c884cbfa858aec3c1730397e34bd4f4992f21e/www.gravatar.com/avatar/a902d35d9cd3096a7285782c69dd4622.jpg?s=2048&d=https%3A%2F%2Fcdn.shopify.com%2Fshopifycloud%2Fshopify%2Fassets%2Fno-gravatar-new-04e7c2331218ac202e79e31be502fd5631bc96cb0206580dbcb0720ebbbd7c73.png"
              },
              "email": "sales@example.com",
              "exists": true,
              "firstName": "angie",
              "id": "gid://shopify/StaffMember/1039577421",
              "initials": [
                "a",
                "l"
              ],
              "isShopOwner": false,
              "lastName": "lucuos",
              "locale": "en",
              "name": "angie lucuos",
              "phone": null
            }
          },
          {
            "node": {
              "active": true,
              "avatar": {
                "url": "https://cdn.shopify.com/proxy/29f98977e6ce2b24120b4d26ce7fde694b7bafc46a6be575ce88cf26a789c4e6/www.gravatar.com/avatar/4df4299bb7b53d4a9e8989238f81c15d.jpg?s=2048&d=https%3A%2F%2Fcdn.shopify.com%2Fshopifycloud%2Fshopify%2Fassets%2Fno-gravatar-new-04e7c2331218ac202e79e31be502fd5631bc96cb0206580dbcb0720ebbbd7c73.png"
              },
              "email": "arnie@champion.example.com",
              "exists": true,
              "firstName": "Arnold",
              "id": "gid://shopify/StaffMember/863601736",
              "initials": [
                "S",
                "n"
              ],
              "isShopOwner": false,
              "lastName": "Schwarzenegger",
              "locale": "en",
              "name": "Snow Devil Inc.",
              "phone": null
            }
          },
          {
            "node": {
              "active": true,
              "avatar": {
                "url": "https://cdn.shopify.com/s/files/1/2637/1970/users/foo.jpg?v=1731443626"
              },
              "email": "bob@example.com",
              "exists": true,
              "firstName": "bob",
              "id": "gid://shopify/StaffMember/902541635",
              "initials": [
                "b",
                "b"
              ],
              "isShopOwner": true,
              "lastName": "bobsen",
              "locale": "en",
              "name": "bob bobsen",
              "phone": null
            }
          },
          {
            "node": {
              "active": true,
              "avatar": {
                "url": "https://cdn.shopify.com/proxy/a2fa3a40bc8b418a7e6a69413fb84a57164b6f4ce6757d4163ffda4302e02682/www.gravatar.com/avatar/59aa4f8e9b82c046003452b23e3b881e.jpg?s=2048&d=https%3A%2F%2Fcdn.shopify.com%2Fshopifycloud%2Fshopify%2Fassets%2Fno-gravatar-new-04e7c2331218ac202e79e31be502fd5631bc96cb0206580dbcb0720ebbbd7c73.png"
              },
              "email": "pos@shopify.com",
              "exists": true,
              "firstName": "bob",
              "id": "gid://shopify/StaffMember/1004723144",
              "initials": [
                "b",
                "b"
              ],
              "isShopOwner": false,
              "lastName": "bobsen",
              "locale": "en",
              "name": "bob bobsen",
              "phone": null
            }
          },
          {
            "node": {
              "active": true,
              "avatar": {
                "url": "https://cdn.shopify.com/proxy/739472b8350cf18a7f2058ef2d37019d4026bcb276844fa3d192eed26b594e27/www.gravatar.com/avatar/6fe88e20596eb227b53b543c2cece91e.jpg?s=2048&d=https%3A%2F%2Fcdn.shopify.com%2Fshopifycloud%2Fshopify%2Fassets%2Fno-gravatar-new-04e7c2331218ac202e79e31be502fd5631bc96cb0206580dbcb0720ebbbd7c73.png"
              },
              "email": "collaborator_bob@example.com",
              "exists": true,
              "firstName": "collaborator",
              "id": "gid://shopify/StaffMember/688782760",
              "initials": [
                "S",
                "n"
              ],
              "isShopOwner": false,
              "lastName": "bob",
              "locale": "en",
              "name": "Snow Devil Inc.",
              "phone": null
            }
          },
          {
            "node": {
              "active": true,
              "avatar": {
                "url": "https://cdn.shopify.com/proxy/8149b06b8974a1092082b18147941ef437a669fa6db5aba0ccd80bee9b33b788/www.gravatar.com/avatar/866ad7602839b586d7d18cb11b131881.jpg?s=2048&d=https%3A%2F%2Fcdn.shopify.com%2Fshopifycloud%2Fshopify%2Fassets%2Fno-gravatar-new-04e7c2331218ac202e79e31be502fd5631bc96cb0206580dbcb0720ebbbd7c73.png"
              },
              "email": "customereventsbob@example.com",
              "exists": true,
              "firstName": "customereventsbob",
              "id": "gid://shopify/StaffMember/216359514",
              "initials": [
                "c",
                "b"
              ],
              "isShopOwner": false,
              "lastName": "bobsen",
              "locale": "en",
              "name": "customereventsbob bobsen",
              "phone": null
            }
          },
          {
            "node": {
              "active": true,
              "avatar": {
                "url": "https://cdn.shopify.com/proxy/9a11b2a61faef02c90cae564d6cd8f61c9c5932abdc470375ea4af38d2234678/www.gravatar.com/avatar/a30775a5f88642adceaa3a6ff418ff4d.jpg?s=2048&d=https%3A%2F%2Fcdn.shopify.com%2Fshopifycloud%2Fshopify%2Fassets%2Fno-gravatar-new-04e7c2331218ac202e79e31be502fd5631bc96cb0206580dbcb0720ebbbd7c73.png"
              },
              "email": "customereventsbobnoapps@example.com",
              "exists": true,
              "firstName": "customereventsbobnoapps",
              "id": "gid://shopify/StaffMember/257608065",
              "initials": [
                "c",
                "b"
              ],
              "isShopOwner": false,
              "lastName": "bobsen",
              "locale": "en",
              "name": "customereventsbobnoapps bobsen",
              "phone": null
            }
          },
          {
            "node": {
              "active": true,
              "avatar": {
                "url": "https://cdn.shopify.com/proxy/d0f4af069a9948a91f75815dcf3c24b7bd775bb8fa66571da1b257f2fd2eacf5/www.gravatar.com/avatar/3111a27ed0d92a4209a15190114490d4.jpg?s=2048&d=https%3A%2F%2Fcdn.shopify.com%2Fshopifycloud%2Fshopify%2Fassets%2Fno-gravatar-new-04e7c2331218ac202e79e31be502fd5631bc96cb0206580dbcb0720ebbbd7c73.png"
              },
              "email": "customereventsbobwithoneapp@example.com",
              "exists": true,
              "firstName": "customereventsbobwithoneapp",
              "id": "gid://shopify/StaffMember/584611871",
              "initials": [
                "c",
                "b"
              ],
              "isShopOwner": false,
              "lastName": "bobsen",
              "locale": "en",
              "name": "customereventsbobwithoneapp bobsen",
              "phone": null
            }
          },
          {
            "node": {
              "active": false,
              "avatar": {
                "url": "https://cdn.shopify.com/proxy/0feaeef95fe37c482d1472c776d9f5c35f3f4b0a051fef68bf702422c284f5fd/www.gravatar.com/avatar/cc9f2fc36ad3c135e4984fc6f63c4c16.jpg?s=2048&d=https%3A%2F%2Fcdn.shopify.com%2Fshopifycloud%2Fshopify%2Fassets%2Fno-gravatar-new-04e7c2331218ac202e79e31be502fd5631bc96cb0206580dbcb0720ebbbd7c73.png"
              },
              "email": "deactivateduser@example.com",
              "exists": true,
              "firstName": "deactivated",
              "id": "gid://shopify/StaffMember/667736507",
              "initials": [
                "d",
                "u"
              ],
              "isShopOwner": false,
              "lastName": "user",
              "locale": "en",
              "name": "deactivated user",
              "phone": null
            }
          },
          {
            "node": {
              "active": true,
              "avatar": {
                "url": "https://cdn.shopify.com/proxy/bb267d2b2b59370b919f9c8f42719ece9e33c84ee51230220405746dd8c5c504/www.gravatar.com/avatar/68bd9ae0240cb5cfd89463b1fe778375.jpg?s=2048&d=https%3A%2F%2Fcdn.shopify.com%2Fshopifycloud%2Fshopify%2Fassets%2Fno-gravatar-new-04e7c2331218ac202e79e31be502fd5631bc96cb0206580dbcb0720ebbbd7c73.png"
              },
              "email": "existingbob@example.com",
              "exists": true,
              "firstName": "existingbob",
              "id": "gid://shopify/StaffMember/2108187",
              "initials": [
                "e",
                "b"
              ],
              "isShopOwner": false,
              "lastName": "bobsen",
              "locale": "en",
              "name": "existingbob bobsen",
              "phone": "3213213211"
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieves a list of currencies enabled on a shop

  #### Query

  ```graphql
  query {
    shop {
      currencySettings(first: 1) {
        edges {
          node {
            currencyCode
            rateUpdatedAt
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
  "query": "query { shop { currencySettings(first: 1) { edges { node { currencyCode rateUpdatedAt } } } } }"
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
      shop {
        currencySettings(first: 1) {
          edges {
            node {
              currencyCode
              rateUpdatedAt
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
      shop {
        currencySettings(first: 1) {
          edges {
            node {
              currencyCode
              rateUpdatedAt
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
      shop {
        currencySettings(first: 1) {
          edges {
            node {
              currencyCode
              rateUpdatedAt
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
    shop {
      currencySettings(first: 1) {
        edges {
          node {
            currencyCode
            rateUpdatedAt
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "shop": {
      "currencySettings": {
        "edges": [
          {
            "node": {
              "currencyCode": "CAD",
              "rateUpdatedAt": "2018-01-24T00:01:01Z"
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieves a list of storefront access tokens that have been issued

  #### Query

  ```graphql
  query storefrontAccessToken {
    shop {
      storefrontAccessTokens(first: 10) {
        edges {
          node {
            id
            accessToken
            accessScopes {
              handle
            }
            createdAt
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
  "query": "query storefrontAccessToken { shop { storefrontAccessTokens(first: 10) { edges { node { id accessToken accessScopes { handle } createdAt title } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query storefrontAccessToken {
      shop {
        storefrontAccessTokens(first: 10) {
          edges {
            node {
              id
              accessToken
              accessScopes {
                handle
              }
              createdAt
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
    query storefrontAccessToken {
      shop {
        storefrontAccessTokens(first: 10) {
          edges {
            node {
              id
              accessToken
              accessScopes {
                handle
              }
              createdAt
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
    data: `query storefrontAccessToken {
      shop {
        storefrontAccessTokens(first: 10) {
          edges {
            node {
              id
              accessToken
              accessScopes {
                handle
              }
              createdAt
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
  'query storefrontAccessToken {
    shop {
      storefrontAccessTokens(first: 10) {
        edges {
          node {
            id
            accessToken
            accessScopes {
              handle
            }
            createdAt
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
    "shop": {
      "storefrontAccessTokens": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/StorefrontAccessToken/55270800",
              "accessToken": "678d97641255a4ab5feff997ee233f4c",
              "accessScopes": [
                {
                  "handle": "unauthenticated_read_product_listings"
                },
                {
                  "handle": "unauthenticated_write_checkouts"
                },
                {
                  "handle": "unauthenticated_read_checkouts"
                },
                {
                  "handle": "unauthenticated_read_selling_plans"
                }
              ],
              "createdAt": "2024-11-12T20:33:46Z",
              "title": "Buy Button Extension"
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieves a list of the shop's policies

  #### Query

  ```graphql
  query ShopPolicyList {
    shop {
      shopPolicies {
        id
        url
        body
        type
        title
        createdAt
        updatedAt
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
  "query": "query ShopPolicyList { shop { shopPolicies { id url body type title createdAt updatedAt } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query ShopPolicyList {
      shop {
        shopPolicies {
          id
          url
          body
          type
          title
          createdAt
          updatedAt
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
    query ShopPolicyList {
      shop {
        shopPolicies {
          id
          url
          body
          type
          title
          createdAt
          updatedAt
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
    data: `query ShopPolicyList {
      shop {
        shopPolicies {
          id
          url
          body
          type
          title
          createdAt
          updatedAt
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ShopPolicyList {
    shop {
      shopPolicies {
        id
        url
        body
        type
        title
        createdAt
        updatedAt
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "shop": {
      "shopPolicies": [
        {
          "id": "gid://shopify/ShopPolicy/1",
          "url": "https://checkout.local/26371970/policies/1.html?locale=en",
          "body": "<p>The following is snowdevil's refund policy. blah blah blah blah blah.</p>",
          "type": "REFUND_POLICY",
          "title": "Refund policy",
          "createdAt": "2024-11-19T09:03:50-05:00",
          "updatedAt": "2024-11-19T09:03:50-05:00"
        },
        {
          "id": "gid://shopify/ShopPolicy/2",
          "url": "https://checkout.local/26371970/policies/2.html?locale=en",
          "body": "<p>PrivacyPolicy - this is a privacy policy document.</p>",
          "type": "PRIVACY_POLICY",
          "title": "Privacy policy",
          "createdAt": "2024-11-19T09:03:50-05:00",
          "updatedAt": "2024-11-19T09:03:50-05:00"
        },
        {
          "id": "gid://shopify/ShopPolicy/3",
          "url": "https://checkout.local/26371970/policies/3.html?locale=en",
          "body": "<p>Terms of Service - this is our terms of service</p>",
          "type": "TERMS_OF_SERVICE",
          "title": "Terms of service",
          "createdAt": "2024-11-19T09:03:50-05:00",
          "updatedAt": "2024-11-19T09:03:50-05:00"
        },
        {
          "id": "gid://shopify/ShopPolicy/4",
          "url": "https://checkout.local/26371970/policies/4.html?locale=en",
          "body": "<p>This is our Legal Notice</p>",
          "type": "LEGAL_NOTICE",
          "title": "Legal notice",
          "createdAt": "2024-11-19T09:03:50-05:00",
          "updatedAt": "2024-11-19T09:03:50-05:00"
        },
        {
          "id": "gid://shopify/ShopPolicy/5",
          "url": "https://checkout.local/26371970/policies/5.html?locale=en",
          "body": "<p>This is our Shipping Policy</p>",
          "type": "SHIPPING_POLICY",
          "title": "Shipping policy",
          "createdAt": "2024-11-19T09:03:50-05:00",
          "updatedAt": "2024-11-19T09:03:50-05:00"
        },
        {
          "id": "gid://shopify/ShopPolicy/6",
          "url": "https://checkout.local/26371970/policies/6.html?locale=en",
          "body": "<p>This is our Terms of Sale 🇫🇷</p>",
          "type": "TERMS_OF_SALE",
          "title": "Terms of sale",
          "createdAt": "2024-11-19T09:03:50-05:00",
          "updatedAt": "2024-11-19T09:03:50-05:00"
        },
        {
          "id": "gid://shopify/ShopPolicy/7",
          "url": "https://checkout.local/26371970/policies/7.html?locale=en",
          "body": "<p>This is our Subscription Policy</p>",
          "type": "SUBSCRIPTION_POLICY",
          "title": "Cancellation policy",
          "createdAt": "2024-11-19T09:03:50-05:00",
          "updatedAt": "2024-11-19T09:03:50-05:00"
        },
        {
          "id": "gid://shopify/ShopPolicy/8",
          "url": "https://checkout.local/26371970/policies/8.html?locale=en",
          "body": "<p>Contact Information - this is a contact information document.</p>",
          "type": "CONTACT_INFORMATION",
          "title": "Contact information",
          "createdAt": "2024-11-19T09:03:50-05:00",
          "updatedAt": "2024-11-19T09:03:50-05:00"
        }
      ]
    }
  }
  ```

* ### Retrieves the shop's configuration

  #### Query

  ```graphql
  query ShopShow {
    shop {
      accountOwner {
        name
      }
      alerts {
        action {
          title
          url
        }
        description
      }
      billingAddress {
        address1
        address2
        city
        company
        country
        countryCodeV2
        latitude
        longitude
        phone
        province
        provinceCode
        zip
      }
      checkoutApiSupported
      contactEmail
      createdAt
      currencyCode
      currencyFormats {
        moneyFormat
        moneyInEmailsFormat
        moneyWithCurrencyFormat
        moneyWithCurrencyInEmailsFormat
      }
      customerAccounts
      description
      email
      enabledPresentmentCurrencies
      fulfillmentServices {
        handle
        serviceName
      }
      ianaTimezone
      id
      marketingSmsConsentEnabledAtCheckout
      myshopifyDomain
      name
      paymentSettings {
        supportedDigitalWallets
      }
      plan {
        displayName
        partnerDevelopment
        shopifyPlus
      }
      primaryDomain {
        host
        id
      }
      productTypes(first: 250) {
        edges {
          node
        }
      }
      setupRequired
      shipsToCountries
      taxesIncluded
      taxShipping
      timezoneAbbreviation
      transactionalSmsDisabled
      updatedAt
      url
      weightUnit
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
  "query": "query ShopShow { shop { accountOwner { name } alerts { action { title url } description } billingAddress { address1 address2 city company country countryCodeV2 latitude longitude phone province provinceCode zip } checkoutApiSupported contactEmail createdAt currencyCode currencyFormats { moneyFormat moneyInEmailsFormat moneyWithCurrencyFormat moneyWithCurrencyInEmailsFormat } customerAccounts description email enabledPresentmentCurrencies fulfillmentServices { handle serviceName } ianaTimezone id marketingSmsConsentEnabledAtCheckout myshopifyDomain name paymentSettings { supportedDigitalWallets } plan { displayName partnerDevelopment shopifyPlus } primaryDomain { host id } productTypes(first: 250) { edges { node } } setupRequired shipsToCountries taxesIncluded taxShipping timezoneAbbreviation transactionalSmsDisabled updatedAt url weightUnit } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query ShopShow {
      shop {
        accountOwner {
          name
        }
        alerts {
          action {
            title
            url
          }
          description
        }
        billingAddress {
          address1
          address2
          city
          company
          country
          countryCodeV2
          latitude
          longitude
          phone
          province
          provinceCode
          zip
        }
        checkoutApiSupported
        contactEmail
        createdAt
        currencyCode
        currencyFormats {
          moneyFormat
          moneyInEmailsFormat
          moneyWithCurrencyFormat
          moneyWithCurrencyInEmailsFormat
        }
        customerAccounts
        description
        email
        enabledPresentmentCurrencies
        fulfillmentServices {
          handle
          serviceName
        }
        ianaTimezone
        id
        marketingSmsConsentEnabledAtCheckout
        myshopifyDomain
        name
        paymentSettings {
          supportedDigitalWallets
        }
        plan {
          displayName
          partnerDevelopment
          shopifyPlus
        }
        primaryDomain {
          host
          id
        }
        productTypes(first: 250) {
          edges {
            node
          }
        }
        setupRequired
        shipsToCountries
        taxesIncluded
        taxShipping
        timezoneAbbreviation
        transactionalSmsDisabled
        updatedAt
        url
        weightUnit
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
    query ShopShow {
      shop {
        accountOwner {
          name
        }
        alerts {
          action {
            title
            url
          }
          description
        }
        billingAddress {
          address1
          address2
          city
          company
          country
          countryCodeV2
          latitude
          longitude
          phone
          province
          provinceCode
          zip
        }
        checkoutApiSupported
        contactEmail
        createdAt
        currencyCode
        currencyFormats {
          moneyFormat
          moneyInEmailsFormat
          moneyWithCurrencyFormat
          moneyWithCurrencyInEmailsFormat
        }
        customerAccounts
        description
        email
        enabledPresentmentCurrencies
        fulfillmentServices {
          handle
          serviceName
        }
        ianaTimezone
        id
        marketingSmsConsentEnabledAtCheckout
        myshopifyDomain
        name
        paymentSettings {
          supportedDigitalWallets
        }
        plan {
          displayName
          partnerDevelopment
          shopifyPlus
        }
        primaryDomain {
          host
          id
        }
        productTypes(first: 250) {
          edges {
            node
          }
        }
        setupRequired
        shipsToCountries
        taxesIncluded
        taxShipping
        timezoneAbbreviation
        transactionalSmsDisabled
        updatedAt
        url
        weightUnit
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query ShopShow {
      shop {
        accountOwner {
          name
        }
        alerts {
          action {
            title
            url
          }
          description
        }
        billingAddress {
          address1
          address2
          city
          company
          country
          countryCodeV2
          latitude
          longitude
          phone
          province
          provinceCode
          zip
        }
        checkoutApiSupported
        contactEmail
        createdAt
        currencyCode
        currencyFormats {
          moneyFormat
          moneyInEmailsFormat
          moneyWithCurrencyFormat
          moneyWithCurrencyInEmailsFormat
        }
        customerAccounts
        description
        email
        enabledPresentmentCurrencies
        fulfillmentServices {
          handle
          serviceName
        }
        ianaTimezone
        id
        marketingSmsConsentEnabledAtCheckout
        myshopifyDomain
        name
        paymentSettings {
          supportedDigitalWallets
        }
        plan {
          displayName
          partnerDevelopment
          shopifyPlus
        }
        primaryDomain {
          host
          id
        }
        productTypes(first: 250) {
          edges {
            node
          }
        }
        setupRequired
        shipsToCountries
        taxesIncluded
        taxShipping
        timezoneAbbreviation
        transactionalSmsDisabled
        updatedAt
        url
        weightUnit
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query ShopShow {
    shop {
      accountOwner {
        name
      }
      alerts {
        action {
          title
          url
        }
        description
      }
      billingAddress {
        address1
        address2
        city
        company
        country
        countryCodeV2
        latitude
        longitude
        phone
        province
        provinceCode
        zip
      }
      checkoutApiSupported
      contactEmail
      createdAt
      currencyCode
      currencyFormats {
        moneyFormat
        moneyInEmailsFormat
        moneyWithCurrencyFormat
        moneyWithCurrencyInEmailsFormat
      }
      customerAccounts
      description
      email
      enabledPresentmentCurrencies
      fulfillmentServices {
        handle
        serviceName
      }
      ianaTimezone
      id
      marketingSmsConsentEnabledAtCheckout
      myshopifyDomain
      name
      paymentSettings {
        supportedDigitalWallets
      }
      plan {
        displayName
        partnerDevelopment
        shopifyPlus
      }
      primaryDomain {
        host
        id
      }
      productTypes(first: 250) {
        edges {
          node
        }
      }
      setupRequired
      shipsToCountries
      taxesIncluded
      taxShipping
      timezoneAbbreviation
      transactionalSmsDisabled
      updatedAt
      url
      weightUnit
    }
  }'
  ```

  #### Response

  ```json
  {
    "shop": {
      "accountOwner": {
        "name": "bob bobsen"
      },
      "alerts": [],
      "billingAddress": {
        "address1": "190 MacLaren Street",
        "address2": "suite 800",
        "city": "Ottawa",
        "company": "Snowdevil",
        "country": "Canada",
        "countryCodeV2": "CA",
        "latitude": 45.45,
        "longitude": -75.43,
        "phone": "6135551234",
        "province": "Ontario",
        "provinceCode": "ON",
        "zip": "K2P 0L6"
      },
      "checkoutApiSupported": true,
      "contactEmail": "email@snowdevil.ca",
      "createdAt": "2005-05-05T00:00:00Z",
      "currencyCode": "USD",
      "currencyFormats": {
        "moneyFormat": "${{amount}}",
        "moneyInEmailsFormat": "${{amount}}",
        "moneyWithCurrencyFormat": "${{amount}} USD",
        "moneyWithCurrencyInEmailsFormat": "${{amount}} USD"
      },
      "customerAccounts": "OPTIONAL",
      "description": "Snow devil",
      "email": "email@snowdevil.ca",
      "enabledPresentmentCurrencies": [
        "AUD",
        "CAD",
        "JPY",
        "USD"
      ],
      "fulfillmentServices": [
        {
          "handle": "manual",
          "serviceName": "Manual"
        },
        {
          "handle": "shipwire",
          "serviceName": "Shipwire"
        },
        {
          "handle": "on-demand-delivery",
          "serviceName": "On Demand Delivery"
        },
        {
          "handle": "mr-acme-drop-shipper",
          "serviceName": "Mr. ACME Drop Shipper"
        },
        {
          "handle": "mr-drop-shipper",
          "serviceName": "Mr. Drop Shipper"
        }
      ],
      "ianaTimezone": "America/New_York",
      "id": "gid://shopify/Shop/26371970",
      "marketingSmsConsentEnabledAtCheckout": false,
      "myshopifyDomain": "snowdevil.myshopify.com",
      "name": "Snowdevil",
      "paymentSettings": {
        "supportedDigitalWallets": []
      },
      "plan": {
        "displayName": "Basic",
        "partnerDevelopment": false,
        "shopifyPlus": false
      },
      "primaryDomain": {
        "host": "www.snowdevil.ca",
        "id": "gid://shopify/Domain/948873163"
      },
      "productTypes": {
        "edges": [
          {
            "node": "Boots"
          },
          {
            "node": "Cult Products"
          },
          {
            "node": "Footwear"
          },
          {
            "node": "Snowboards"
          }
        ]
      },
      "setupRequired": false,
      "shipsToCountries": [
        "AC",
        "AD",
        "AE",
        "AF",
        "AG",
        "AI",
        "AL",
        "AM",
        "AO",
        "AR",
        "AT",
        "AU",
        "AW",
        "AX",
        "AZ",
        "BA",
        "BB",
        "BD",
        "BE",
        "BF",
        "BG",
        "BH",
        "BI",
        "BJ",
        "BL",
        "BM",
        "BN",
        "BO",
        "BQ",
        "BR",
        "BS",
        "BT",
        "BW",
        "BY",
        "BZ",
        "CA",
        "CC",
        "CD",
        "CF",
        "CG",
        "CH",
        "CI",
        "CK",
        "CL",
        "CM",
        "CN",
        "CO",
        "CR",
        "CV",
        "CW",
        "CX",
        "CY",
        "CZ",
        "DE",
        "DJ",
        "DK",
        "DM",
        "DO",
        "DZ",
        "EC",
        "EE",
        "EG",
        "EH",
        "ER",
        "ES",
        "ET",
        "FI",
        "FJ",
        "FK",
        "FO",
        "FR",
        "GA",
        "GB",
        "GD",
        "GE",
        "GF",
        "GG",
        "GH",
        "GI",
        "GL",
        "GM",
        "GN",
        "GP",
        "GQ",
        "GR",
        "GS",
        "GT",
        "GW",
        "GY",
        "HK",
        "HN",
        "HR",
        "HT",
        "HU",
        "ID",
        "IE",
        "IL",
        "IM",
        "IN",
        "IO",
        "IQ",
        "IS",
        "IT",
        "JE",
        "JM",
        "JO",
        "JP",
        "KE",
        "KG",
        "KH",
        "KI",
        "KM",
        "KN",
        "KR",
        "KW",
        "KY",
        "KZ",
        "LA",
        "LB",
        "LC",
        "LI",
        "LK",
        "LR",
        "LS",
        "LT",
        "LU",
        "LV",
        "LY",
        "MA",
        "MC",
        "MD",
        "ME",
        "MF",
        "MG",
        "MK",
        "ML",
        "MM",
        "MN",
        "MO",
        "MQ",
        "MR",
        "MS",
        "MT",
        "MU",
        "MV",
        "MW",
        "MX",
        "MY",
        "MZ",
        "NA",
        "NC",
        "NE",
        "NF",
        "NG",
        "NI",
        "NL",
        "NO",
        "NP",
        "NR",
        "NU",
        "NZ",
        "OM",
        "PA",
        "PE",
        "PF",
        "PG",
        "PH",
        "PK",
        "PL",
        "PM",
        "PN",
        "PS",
        "PT",
        "PY",
        "QA",
        "RE",
        "RO",
        "RS",
        "RU",
        "RW",
        "SA",
        "SB",
        "SC",
        "SD",
        "SE",
        "SG",
        "SH",
        "SI",
        "SJ",
        "SK",
        "SL",
        "SM",
        "SN",
        "SO",
        "SR",
        "SS",
        "ST",
        "SV",
        "SX",
        "SZ",
        "TA",
        "TC",
        "TD",
        "TF",
        "TG",
        "TH",
        "TJ",
        "TK",
        "TL",
        "TM",
        "TN",
        "TO",
        "TR",
        "TT",
        "TV",
        "TW",
        "TZ",
        "UA",
        "UG",
        "UM",
        "US",
        "UY",
        "UZ",
        "VA",
        "VC",
        "VE",
        "VG",
        "VN",
        "VU",
        "WF",
        "WS",
        "XK",
        "YE",
        "YT",
        "ZA",
        "ZM",
        "ZW"
      ],
      "taxesIncluded": false,
      "taxShipping": false,
      "timezoneAbbreviation": "EST",
      "transactionalSmsDisabled": false,
      "updatedAt": "2024-11-19T14:03:50Z",
      "url": "https://www.snowdevil.ca",
      "weightUnit": "KILOGRAMS"
    }
  }
  ```
