---
title: customer - GraphQL Admin
description: Returns a `Customer` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/customer'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/customer.md'
---

# customer

query

Returns a `Customer` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `Customer` to return.

***

## Possible returns

* Customer

  [Customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

  Information about a customer of the shop, such as the customer's contact details, purchase history, and marketing preferences.

  Tracks the customer's total spending through the [`amountSpent`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer#field-amountSpent) field and provides access to associated data such as payment methods and subscription contracts.

  ***

  **Caution:** Only use this data if it\&#39;s required for your app\&#39;s functionality. Shopify will restrict \<a href="https://shopify.dev/api/usage/access-scopes">access to scopes\</a> for apps that don\&#39;t have a legitimate use for the associated data.

  ***

  * addresses​V2

    [Mailing​Address​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MailingAddressConnection)

    non-null

    The addresses associated with the customer.

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

  * amount​Spent

    [Money​V2!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyV2)

    non-null

    The total amount that the customer has spent on orders in their lifetime.

  * can​Delete

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the merchant can delete the customer from their store.

    A customer can be deleted from a store only if they haven't yet made an order. After a customer makes an order, they can't be deleted from a store.

  * company​Contact​Profiles

    [\[Company​Contact!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyContact)

    non-null

    A list of the customer's company contact profiles.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the customer was added to the store.

  * data​Sale​Opt​Out

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the customer has opted out of having their data sold.

  * default​Address

    [Mailing​Address](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress)

    The default address associated with the customer.

  * default​Email​Address

    [Customer​Email​Address](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerEmailAddress)

    The customer's default email address.

  * default​Phone​Number

    [Customer​Phone​Number](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerPhoneNumber)

    The customer's default phone number.

  * display​Name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The full name of the customer, based on the values for first\_name and last\_name. If the first\_name and last\_name are not available, then this falls back to the customer's email address, and if that is not available, the customer's phone number.

  * events

    [Event​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/EventConnection)

    non-null

    A list of events associated with the customer.

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

  * first​Name

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The customer's first name.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * image

    [Image!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Image)

    non-null

    The image associated with the customer.

    * size

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      Deprecated

      ### Arguments

    ***

  * last​Name

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The customer's last name.

  * last​Order

    [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

    The customer's last order.

  * legacy​Resource​Id

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The ID of the corresponding resource in the REST Admin API.

  * lifetime​Duration

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The amount of time since the customer was first added to the store.

    Example: 'about 12 years'.

  * locale

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The customer's locale.

  * mergeable

    [Customer​Mergeable!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerMergeable)

    non-null

    Whether the customer can be merged with another customer.

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

  * multipass​Identifier

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    A unique identifier for the customer that's used with Multipass login.

  * note

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    A note about the customer.

  * number​Of​Orders

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The number of orders that the customer has made at the store in their lifetime.

  * orders

    [Order​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/OrderConnection)

    non-null

    A list of the customer's orders.

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

      Default:ID

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

  * payment​Methods

    [Customer​Payment​Method​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CustomerPaymentMethodConnection)

    non-null

    A list of the customer's payment methods.

    * show​Revoked

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      ### Arguments

      Whether to show the customer's revoked payment method.

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

  * product​Subscriber​Status

    [Customer​Product​Subscriber​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CustomerProductSubscriberStatus)

    non-null

    Possible subscriber states of a customer defined by their subscription contracts.

  * state

    [Customer​State!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CustomerState)

    non-null

    The state of the customer's account with the shop.

    Please note that this only meaningful when Classic Customer Accounts is active.

  * statistics

    [Customer​Statistics!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerStatistics)

    non-null

    The statistics for a given customer.

  * store​Credit​Accounts

    [Store​Credit​Account​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/StoreCreditAccountConnection)

    non-null

    Returns a list of store credit accounts that belong to the owner resource. A store credit account owner can hold multiple accounts each with a different currency.

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

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

      * currency\_code

        string

      * id

        id

        Filter by `id` range.

        Example:

        * `id:1234`
        * `id:>=1234`
        * `id:<=1234`

    ***

  * subscription​Contracts

    [Subscription​Contract​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SubscriptionContractConnection)

    non-null

    A list of the customer's subscription contracts.

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

  * tags

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A comma separated list of tags that have been added to the customer.

  * tax​Exempt

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the customer is exempt from being charged taxes on their orders.

  * tax​Exemptions

    [\[Tax​Exemption!\]!](https://shopify.dev/docs/api/admin-graphql/latest/enums/TaxExemption)

    non-null

    The list of tax exemptions applied to the customer.

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the customer was last updated.

  * verified​Email

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the customer has verified their email address. Defaults to `true` if the customer is created through the Shopify admin or API.

  * addresses

    [\[Mailing​Address!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress)

    non-nullDeprecated

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      Truncate the array result to this size.

    ***

  * email

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Deprecated

  * email​Marketing​Consent

    [Customer​Email​Marketing​Consent​State](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerEmailMarketingConsentState)

    Deprecated

  * has​Timeline​Comment

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-nullDeprecated

  * market

    [Market](https://shopify.dev/docs/api/admin-graphql/latest/objects/Market)

    Deprecated

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

  * phone

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Deprecated

  * sms​Marketing​Consent

    [Customer​Sms​Marketing​Consent​State](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerSmsMarketingConsentState)

    Deprecated

  * unsubscribe​Url

    [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    non-nullDeprecated

  * valid​Email​Address

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-nullDeprecated

***

## Examples

* ### Get a customer by ID

  #### Description

  The following query retrieves the customer with the associated ID. It returns the customer fields specified in the query.

  #### Query

  ```graphql
  query {
    customer(id: "gid://shopify/Customer/544365967") {
      id
      firstName
      lastName
      email
      phone
      numberOfOrders
      amountSpent {
        amount
        currencyCode
      }
      createdAt
      updatedAt
      note
      verifiedEmail
      validEmailAddress
      tags
      lifetimeDuration
      defaultAddress {
        formattedArea
        address1
      }
      addresses {
        address1
      }
      image {
        src
      }
      canDelete
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
  "query": "query { customer(id: \"gid://shopify/Customer/544365967\") { id firstName lastName email phone numberOfOrders amountSpent { amount currencyCode } createdAt updatedAt note verifiedEmail validEmailAddress tags lifetimeDuration defaultAddress { formattedArea address1 } addresses { address1 } image { src } canDelete } }"
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
      customer(id: "gid://shopify/Customer/544365967") {
        id
        firstName
        lastName
        email
        phone
        numberOfOrders
        amountSpent {
          amount
          currencyCode
        }
        createdAt
        updatedAt
        note
        verifiedEmail
        validEmailAddress
        tags
        lifetimeDuration
        defaultAddress {
          formattedArea
          address1
        }
        addresses {
          address1
        }
        image {
          src
        }
        canDelete
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
      customer(id: "gid://shopify/Customer/544365967") {
        id
        firstName
        lastName
        email
        phone
        numberOfOrders
        amountSpent {
          amount
          currencyCode
        }
        createdAt
        updatedAt
        note
        verifiedEmail
        validEmailAddress
        tags
        lifetimeDuration
        defaultAddress {
          formattedArea
          address1
        }
        addresses {
          address1
        }
        image {
          src
        }
        canDelete
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
      customer(id: "gid://shopify/Customer/544365967") {
        id
        firstName
        lastName
        email
        phone
        numberOfOrders
        amountSpent {
          amount
          currencyCode
        }
        createdAt
        updatedAt
        note
        verifiedEmail
        validEmailAddress
        tags
        lifetimeDuration
        defaultAddress {
          formattedArea
          address1
        }
        addresses {
          address1
        }
        image {
          src
        }
        canDelete
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    customer(id: "gid://shopify/Customer/544365967") {
      id
      firstName
      lastName
      email
      phone
      numberOfOrders
      amountSpent {
        amount
        currencyCode
      }
      createdAt
      updatedAt
      note
      verifiedEmail
      validEmailAddress
      tags
      lifetimeDuration
      defaultAddress {
        formattedArea
        address1
      }
      addresses {
        address1
      }
      image {
        src
      }
      canDelete
    }
  }'
  ```

  #### Response

  ```json
  {
    "customer": {
      "id": "gid://shopify/Customer/544365967",
      "firstName": "Bob",
      "lastName": "Bobsen",
      "email": "bob@example.com",
      "phone": "+13125551212",
      "numberOfOrders": "25",
      "amountSpent": {
        "amount": "8305.6",
        "currencyCode": "USD"
      },
      "createdAt": "2005-06-15T15:57:11Z",
      "updatedAt": "2005-06-16T15:57:11Z",
      "note": null,
      "verifiedEmail": true,
      "validEmailAddress": true,
      "tags": [
        "Bob",
        "Canadian",
        "Léon",
        "Noël"
      ],
      "lifetimeDuration": "almost 20 years",
      "defaultAddress": {
        "formattedArea": "Ottawa ON, Canada",
        "address1": "123 Amoebobacterieae St"
      },
      "addresses": [
        {
          "address1": "123 Amoebobacterieae St"
        }
      ],
      "image": {
        "src": "https://cdn.shopify.com/proxy/d02a582792c73c48b4b62a95f42bcbf6eff91c5d232efb2057ca4c41005e4728/www.gravatar.com/avatar/4b9bb80620f03eb3719e0a061c14283d.jpg?s=2048&d=https%3A%2F%2Fcdn.shopify.com%2Fshopifycloud%2Fshopify%2Fassets%2Fadmin%2Fcustomers%2Fpolaris%2Favatar-2-a0ee6e3fb3ae515b66b68388b265e5bd1e90646c4c72d59170518f45351e668b.png"
      },
      "canDelete": false
    }
  }
  ```

* ### Get a customer's name, email, and default address

  #### Description

  The following query retrieves the customer with the associated ID. It returns the customer's name, email and default address specified by the fields in the query.

  #### Query

  ```graphql
  query {
    customer(id: "gid://shopify/Customer/544365967") {
      email
      firstName
      lastName
      defaultAddress {
        address1
        city
        province
        zip
        country
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
  "query": "query { customer(id: \"gid://shopify/Customer/544365967\") { email firstName lastName defaultAddress { address1 city province zip country } } }"
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
      customer(id: "gid://shopify/Customer/544365967") {
        email
        firstName
        lastName
        defaultAddress {
          address1
          city
          province
          zip
          country
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
      customer(id: "gid://shopify/Customer/544365967") {
        email
        firstName
        lastName
        defaultAddress {
          address1
          city
          province
          zip
          country
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
      customer(id: "gid://shopify/Customer/544365967") {
        email
        firstName
        lastName
        defaultAddress {
          address1
          city
          province
          zip
          country
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
    customer(id: "gid://shopify/Customer/544365967") {
      email
      firstName
      lastName
      defaultAddress {
        address1
        city
        province
        zip
        country
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "customer": {
      "email": "bob@example.com",
      "firstName": "Bob",
      "lastName": "Bobsen",
      "defaultAddress": {
        "address1": "123 Amoebobacterieae St",
        "city": "Ottawa",
        "province": "Ontario",
        "zip": "K2P0V6",
        "country": "Canada"
      }
    }
  }
  ```

* ### Get all a customer's fields and connections

  #### Description

  The following query retrieves the customer with the associated ID. It returns all of the available fields and connections specified in the query.

  #### Query

  ```graphql
  query {
    customer(id: "gid://shopify/Customer/544365967") {
      addresses(first: 5) {
        address1
      }
      canDelete
      createdAt
      defaultAddress {
        address1
      }
      displayName
      email
      events(first: 5) {
        edges {
          node {
            message
          }
        }
      }
      firstName
      id
      image {
        id
      }
      lastName
      legacyResourceId
      lifetimeDuration
      mergeable {
        isMergeable
        reason
      }
      metafield(key: "app_key", namespace: "affiliates") {
        description
      }
      metafields(first: 5) {
        edges {
          node {
            id
          }
        }
      }
      note
      orders(first: 5) {
        edges {
          node {
            id
          }
        }
      }
      numberOfOrders
      phone
      state
      tags
      taxExempt
      amountSpent {
        amount
      }
      updatedAt
      validEmailAddress
      verifiedEmail
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
  "query": "query { customer(id: \"gid://shopify/Customer/544365967\") { addresses(first: 5) { address1 } canDelete createdAt defaultAddress { address1 } displayName email events(first: 5) { edges { node { message } } } firstName id image { id } lastName legacyResourceId lifetimeDuration mergeable { isMergeable reason } metafield(key: \"app_key\", namespace: \"affiliates\") { description } metafields(first: 5) { edges { node { id } } } note orders(first: 5) { edges { node { id } } } numberOfOrders phone state tags taxExempt amountSpent { amount } updatedAt validEmailAddress verifiedEmail } }"
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
      customer(id: "gid://shopify/Customer/544365967") {
        addresses(first: 5) {
          address1
        }
        canDelete
        createdAt
        defaultAddress {
          address1
        }
        displayName
        email
        events(first: 5) {
          edges {
            node {
              message
            }
          }
        }
        firstName
        id
        image {
          id
        }
        lastName
        legacyResourceId
        lifetimeDuration
        mergeable {
          isMergeable
          reason
        }
        metafield(key: "app_key", namespace: "affiliates") {
          description
        }
        metafields(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        note
        orders(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        numberOfOrders
        phone
        state
        tags
        taxExempt
        amountSpent {
          amount
        }
        updatedAt
        validEmailAddress
        verifiedEmail
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
      customer(id: "gid://shopify/Customer/544365967") {
        addresses(first: 5) {
          address1
        }
        canDelete
        createdAt
        defaultAddress {
          address1
        }
        displayName
        email
        events(first: 5) {
          edges {
            node {
              message
            }
          }
        }
        firstName
        id
        image {
          id
        }
        lastName
        legacyResourceId
        lifetimeDuration
        mergeable {
          isMergeable
          reason
        }
        metafield(key: "app_key", namespace: "affiliates") {
          description
        }
        metafields(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        note
        orders(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        numberOfOrders
        phone
        state
        tags
        taxExempt
        amountSpent {
          amount
        }
        updatedAt
        validEmailAddress
        verifiedEmail
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
      customer(id: "gid://shopify/Customer/544365967") {
        addresses(first: 5) {
          address1
        }
        canDelete
        createdAt
        defaultAddress {
          address1
        }
        displayName
        email
        events(first: 5) {
          edges {
            node {
              message
            }
          }
        }
        firstName
        id
        image {
          id
        }
        lastName
        legacyResourceId
        lifetimeDuration
        mergeable {
          isMergeable
          reason
        }
        metafield(key: "app_key", namespace: "affiliates") {
          description
        }
        metafields(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        note
        orders(first: 5) {
          edges {
            node {
              id
            }
          }
        }
        numberOfOrders
        phone
        state
        tags
        taxExempt
        amountSpent {
          amount
        }
        updatedAt
        validEmailAddress
        verifiedEmail
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    customer(id: "gid://shopify/Customer/544365967") {
      addresses(first: 5) {
        address1
      }
      canDelete
      createdAt
      defaultAddress {
        address1
      }
      displayName
      email
      events(first: 5) {
        edges {
          node {
            message
          }
        }
      }
      firstName
      id
      image {
        id
      }
      lastName
      legacyResourceId
      lifetimeDuration
      mergeable {
        isMergeable
        reason
      }
      metafield(key: "app_key", namespace: "affiliates") {
        description
      }
      metafields(first: 5) {
        edges {
          node {
            id
          }
        }
      }
      note
      orders(first: 5) {
        edges {
          node {
            id
          }
        }
      }
      numberOfOrders
      phone
      state
      tags
      taxExempt
      amountSpent {
        amount
      }
      updatedAt
      validEmailAddress
      verifiedEmail
    }
  }'
  ```

  #### Response

  ```json
  {
    "customer": {
      "addresses": [
        {
          "address1": "123 Amoebobacterieae St"
        }
      ],
      "canDelete": false,
      "createdAt": "2005-06-15T15:57:11Z",
      "defaultAddress": {
        "address1": "123 Amoebobacterieae St"
      },
      "displayName": "Bob Bobsen",
      "email": "bob@example.com",
      "events": {
        "edges": []
      },
      "firstName": "Bob",
      "id": "gid://shopify/Customer/544365967",
      "image": {
        "id": null
      },
      "lastName": "Bobsen",
      "legacyResourceId": "544365967",
      "lifetimeDuration": "almost 20 years",
      "mergeable": {
        "isMergeable": false,
        "reason": "Bob Bobsen is scheduled for redaction or has been redacted and can’t be merged."
      },
      "metafield": null,
      "metafields": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/Metafield/749520593"
            }
          }
        ]
      },
      "note": null,
      "orders": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/Order/116757651"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Order/126216516"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Order/148977776"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Order/215577410"
            }
          },
          {
            "node": {
              "id": "gid://shopify/Order/235240302"
            }
          }
        ]
      },
      "numberOfOrders": "25",
      "phone": "+13125551212",
      "state": "ENABLED",
      "tags": [
        "Bob",
        "Canadian",
        "Léon",
        "Noël"
      ],
      "taxExempt": false,
      "amountSpent": {
        "amount": "8305.6"
      },
      "updatedAt": "2005-06-16T15:57:11Z",
      "validEmailAddress": true,
      "verifiedEmail": true
    }
  }
  ```

* ### Get metafields attached to a customer

  #### Description

  Get a page of metafields attached to a specific customer.

  #### Query

  ```graphql
  query CustomerMetafields($ownerId: ID!) {
    customer(id: $ownerId) {
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
    "ownerId": "gid://shopify/Customer/544365967"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query CustomerMetafields($ownerId: ID!) { customer(id: $ownerId) { metafields(first: 3) { edges { node { namespace key value } } } } }",
   "variables": {
      "ownerId": "gid://shopify/Customer/544365967"
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
    query CustomerMetafields($ownerId: ID!) {
      customer(id: $ownerId) {
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
          "ownerId": "gid://shopify/Customer/544365967"
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
    query CustomerMetafields($ownerId: ID!) {
      customer(id: $ownerId) {
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
    "ownerId": "gid://shopify/Customer/544365967"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query CustomerMetafields($ownerId: ID!) {
        customer(id: $ownerId) {
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
          "ownerId": "gid://shopify/Customer/544365967"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query CustomerMetafields($ownerId: ID!) {
    customer(id: $ownerId) {
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
    "ownerId": "gid://shopify/Customer/544365967"
  }'
  ```

  #### Response

  ```json
  {
    "customer": {
      "metafields": {
        "edges": [
          {
            "node": {
              "namespace": "my_fields",
              "key": "nickname",
              "value": "rob"
            }
          }
        ]
      }
    }
  }
  ```

* ### Get the email, name, and account creation date of three customers using a fragment

  #### Description

  The following query retrieves three specific customers with the associated IDs, which are aliased to the names provided. It returns the customer fields specified in the fragment.

  #### Query

  ```graphql
  query {
    Bob: customer(id: "gid://shopify/Customer/544365967") {
      ...customerProfile
    }
    Jane: customer(id: "gid://shopify/Customer/567375318") {
      ...customerProfile
    }
    Jenny: customer(id: "gid://shopify/Customer/56501169") {
      ...customerProfile
    }
  }

  fragment customerProfile on Customer {
    firstName
    lastName
    email
    createdAt
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query { Bob: customer(id: \"gid://shopify/Customer/544365967\") { ...customerProfile } Jane: customer(id: \"gid://shopify/Customer/567375318\") { ...customerProfile } Jenny: customer(id: \"gid://shopify/Customer/56501169\") { ...customerProfile } } fragment customerProfile on Customer { firstName lastName email createdAt }"
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
      Bob: customer(id: "gid://shopify/Customer/544365967") {
        ...customerProfile
      }
      Jane: customer(id: "gid://shopify/Customer/567375318") {
        ...customerProfile
      }
      Jenny: customer(id: "gid://shopify/Customer/56501169") {
        ...customerProfile
      }
    }
    
    fragment customerProfile on Customer {
      firstName
      lastName
      email
      createdAt
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
      Bob: customer(id: "gid://shopify/Customer/544365967") {
        ...customerProfile
      }
      Jane: customer(id: "gid://shopify/Customer/567375318") {
        ...customerProfile
      }
      Jenny: customer(id: "gid://shopify/Customer/56501169") {
        ...customerProfile
      }
    }
    
    fragment customerProfile on Customer {
      firstName
      lastName
      email
      createdAt
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      Bob: customer(id: "gid://shopify/Customer/544365967") {
        ...customerProfile
      }
      Jane: customer(id: "gid://shopify/Customer/567375318") {
        ...customerProfile
      }
      Jenny: customer(id: "gid://shopify/Customer/56501169") {
        ...customerProfile
      }
    }
    
    fragment customerProfile on Customer {
      firstName
      lastName
      email
      createdAt
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    Bob: customer(id: "gid://shopify/Customer/544365967") {
      ...customerProfile
    }
    Jane: customer(id: "gid://shopify/Customer/567375318") {
      ...customerProfile
    }
    Jenny: customer(id: "gid://shopify/Customer/56501169") {
      ...customerProfile
    }
  }

  fragment customerProfile on Customer {
    firstName
    lastName
    email
    createdAt
  }'
  ```

  #### Response

  ```json
  {
    "Bob": {
      "firstName": "Bob",
      "lastName": "Bobsen",
      "email": "bob@example.com",
      "createdAt": "2005-06-15T15:57:11Z"
    },
    "Jane": {
      "firstName": "Jane",
      "lastName": "Smith",
      "email": "janesmith@b2b.example.com",
      "createdAt": "2025-05-12T20:21:18Z"
    },
    "Jenny": {
      "firstName": "Jenny",
      "lastName": "Test",
      "email": "jennytest@b2b.example.com",
      "createdAt": "2025-05-12T20:21:18Z"
    }
  }
  ```

* ### Get the first five line items of the customer's last order

  #### Description

  The following query retrieves the customer with the associated ID. It returns details about the last 5 line items associated with the customer's most recent order.

  #### Query

  ```graphql
  query {
    customer(id: "gid://shopify/Customer/624407574") {
      lastOrder {
        lineItems(first: 5) {
          edges {
            node {
              name
              quantity
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
  "query": "query { customer(id: \"gid://shopify/Customer/624407574\") { lastOrder { lineItems(first: 5) { edges { node { name quantity } } } } } }"
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
      customer(id: "gid://shopify/Customer/624407574") {
        lastOrder {
          lineItems(first: 5) {
            edges {
              node {
                name
                quantity
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
      customer(id: "gid://shopify/Customer/624407574") {
        lastOrder {
          lineItems(first: 5) {
            edges {
              node {
                name
                quantity
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
      customer(id: "gid://shopify/Customer/624407574") {
        lastOrder {
          lineItems(first: 5) {
            edges {
              node {
                name
                quantity
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
    customer(id: "gid://shopify/Customer/624407574") {
      lastOrder {
        lineItems(first: 5) {
          edges {
            node {
              name
              quantity
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
    "customer": {
      "lastOrder": {
        "lineItems": {
          "edges": [
            {
              "node": {
                "name": "Draft - 151cm",
                "quantity": 1
              }
            }
          ]
        }
      }
    }
  }
  ```

* ### Get the merge status of a customer

  #### Description

  Retrieve the merge status of a customer.

  #### Query

  ```graphql
  query {
    customer(id: "gid://shopify/Customer/105906728") {
      mergeable {
        isMergeable
        reason
        errorFields
        mergeInProgress {
          jobId
          status
          resultingCustomerId
          customerMergeErrors {
            errorFields
            message
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
  "query": "query { customer(id: \"gid://shopify/Customer/105906728\") { mergeable { isMergeable reason errorFields mergeInProgress { jobId status resultingCustomerId customerMergeErrors { errorFields message } } } } }"
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
      customer(id: "gid://shopify/Customer/105906728") {
        mergeable {
          isMergeable
          reason
          errorFields
          mergeInProgress {
            jobId
            status
            resultingCustomerId
            customerMergeErrors {
              errorFields
              message
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
      customer(id: "gid://shopify/Customer/105906728") {
        mergeable {
          isMergeable
          reason
          errorFields
          mergeInProgress {
            jobId
            status
            resultingCustomerId
            customerMergeErrors {
              errorFields
              message
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
      customer(id: "gid://shopify/Customer/105906728") {
        mergeable {
          isMergeable
          reason
          errorFields
          mergeInProgress {
            jobId
            status
            resultingCustomerId
            customerMergeErrors {
              errorFields
              message
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
    customer(id: "gid://shopify/Customer/105906728") {
      mergeable {
        isMergeable
        reason
        errorFields
        mergeInProgress {
          jobId
          status
          resultingCustomerId
          customerMergeErrors {
            errorFields
            message
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "customer": {
      "mergeable": {
        "isMergeable": false,
        "reason": "John Smith is scheduled for redaction or has been redacted and can’t be merged.",
        "errorFields": [
          "REDACTED_AT"
        ],
        "mergeInProgress": null
      }
    }
  }
  ```

* ### Get two specific customers by their ID using aliases

  #### Description

  The following query retrieves two specific customers with the associated IDs. It returns the customer fields specified in the query, aliased to the names provided.

  #### Query

  ```graphql
  query {
    bob: customer(id: "gid://shopify/Customer/544365967") {
      firstName
      lastName
      email
    }
    john: customer(id: "gid://shopify/Customer/105906728") {
      firstName
      lastName
      email
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
  "query": "query { bob: customer(id: \"gid://shopify/Customer/544365967\") { firstName lastName email } john: customer(id: \"gid://shopify/Customer/105906728\") { firstName lastName email } }"
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
      bob: customer(id: "gid://shopify/Customer/544365967") {
        firstName
        lastName
        email
      }
      john: customer(id: "gid://shopify/Customer/105906728") {
        firstName
        lastName
        email
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
      bob: customer(id: "gid://shopify/Customer/544365967") {
        firstName
        lastName
        email
      }
      john: customer(id: "gid://shopify/Customer/105906728") {
        firstName
        lastName
        email
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
      bob: customer(id: "gid://shopify/Customer/544365967") {
        firstName
        lastName
        email
      }
      john: customer(id: "gid://shopify/Customer/105906728") {
        firstName
        lastName
        email
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    bob: customer(id: "gid://shopify/Customer/544365967") {
      firstName
      lastName
      email
    }
    john: customer(id: "gid://shopify/Customer/105906728") {
      firstName
      lastName
      email
    }
  }'
  ```

  #### Response

  ```json
  {
    "bob": {
      "firstName": "Bob",
      "lastName": "Bobsen",
      "email": "bob@example.com"
    },
    "john": {
      "firstName": "John",
      "lastName": "Smith",
      "email": "johnsmith@example.com"
    }
  }
  ```

* ### Retrieve a metafield associated with a customer

  #### Description

  Get the metafield value identified by \`my\_fields.nickname\` on a specific customer.

  #### Query

  ```graphql
  query CustomerMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
    customer(id: $ownerId) {
      nickname: metafield(namespace: $namespace, key: $key) {
        value
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "namespace": "my_fields",
    "key": "nickname",
    "ownerId": "gid://shopify/Customer/544365967"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query CustomerMetafield($namespace: String!, $key: String!, $ownerId: ID!) { customer(id: $ownerId) { nickname: metafield(namespace: $namespace, key: $key) { value } } }",
   "variables": {
      "namespace": "my_fields",
      "key": "nickname",
      "ownerId": "gid://shopify/Customer/544365967"
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
    query CustomerMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
      customer(id: $ownerId) {
        nickname: metafield(namespace: $namespace, key: $key) {
          value
        }
      }
    }`,
    {
      variables: {
          "namespace": "my_fields",
          "key": "nickname",
          "ownerId": "gid://shopify/Customer/544365967"
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
    query CustomerMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
      customer(id: $ownerId) {
        nickname: metafield(namespace: $namespace, key: $key) {
          value
        }
      }
    }
  QUERY

  variables = {
    "namespace": "my_fields",
    "key": "nickname",
    "ownerId": "gid://shopify/Customer/544365967"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query CustomerMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
        customer(id: $ownerId) {
          nickname: metafield(namespace: $namespace, key: $key) {
            value
          }
        }
      }`,
      "variables": {
          "namespace": "my_fields",
          "key": "nickname",
          "ownerId": "gid://shopify/Customer/544365967"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query CustomerMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
    customer(id: $ownerId) {
      nickname: metafield(namespace: $namespace, key: $key) {
        value
      }
    }
  }' \
  --variables \
  '{
    "namespace": "my_fields",
    "key": "nickname",
    "ownerId": "gid://shopify/Customer/544365967"
  }'
  ```

  #### Response

  ```json
  {
    "customer": {
      "nickname": {
        "value": "rob"
      }
    }
  }
  ```

* ### Retrieve details for all addresses associated with a customer

  #### Description

  This query retrieves a customer's ID, address, and city for the first 250 addresses associated with a \[customer]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/customer) using the \`addressesV2\` field. Use the \`id\` argument to specify the customer.

  #### Query

  ```graphql
  query CustomerAddressShow($id: ID!) {
    customer(id: $id) {
      addressesV2(first: 250) {
        edges {
          node {
            id
            address1
            city
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Customer/544365967"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query CustomerAddressShow($id: ID!) { customer(id: $id) { addressesV2(first: 250) { edges { node { id address1 city } } } } }",
   "variables": {
      "id": "gid://shopify/Customer/544365967"
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
    query CustomerAddressShow($id: ID!) {
      customer(id: $id) {
        addressesV2(first: 250) {
          edges {
            node {
              id
              address1
              city
            }
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Customer/544365967"
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
    query CustomerAddressShow($id: ID!) {
      customer(id: $id) {
        addressesV2(first: 250) {
          edges {
            node {
              id
              address1
              city
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Customer/544365967"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query CustomerAddressShow($id: ID!) {
        customer(id: $id) {
          addressesV2(first: 250) {
            edges {
              node {
                id
                address1
                city
              }
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Customer/544365967"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query CustomerAddressShow($id: ID!) {
    customer(id: $id) {
      addressesV2(first: 250) {
        edges {
          node {
            id
            address1
            city
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Customer/544365967"
  }'
  ```

  #### Response

  ```json
  {
    "customer": {
      "addressesV2": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/MailingAddress/544365967?model_name=CustomerAddress",
              "address1": "123 Amoebobacterieae St",
              "city": "Ottawa"
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieve pinned metafield definitions associated with a customer

  #### Description

  This query retrieves the first 10 \[pinned metafield definitions]\(https://help.shopify.com/en/manual/custom-data/metafields/pinning-metafield-definitions) for a customer.It shows each definition's name, namespace, key, and data type, ordered by pinned position.

  #### Query

  ```graphql
  query CustomerMetafieldDefinitions($ownerId: ID!, $first: Int, $pinnedStatus: MetafieldDefinitionPinnedStatus, $sortKey: MetafieldDefinitionSortKeys) {
    customer(id: $ownerId) {
      metafieldDefinitions(first: $first, pinnedStatus: $pinnedStatus, sortKey: $sortKey) {
        edges {
          node {
            name
            namespace
            key
            type {
              name
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
    "pinnedStatus": "PINNED",
    "ownerId": "gid://shopify/Customer/544365967",
    "first": 10,
    "sortKey": "PINNED_POSITION"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query CustomerMetafieldDefinitions($ownerId: ID!, $first: Int, $pinnedStatus: MetafieldDefinitionPinnedStatus, $sortKey: MetafieldDefinitionSortKeys) { customer(id: $ownerId) { metafieldDefinitions(first: $first, pinnedStatus: $pinnedStatus, sortKey: $sortKey) { edges { node { name namespace key type { name } } } } } }",
   "variables": {
      "pinnedStatus": "PINNED",
      "ownerId": "gid://shopify/Customer/544365967",
      "first": 10,
      "sortKey": "PINNED_POSITION"
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
    query CustomerMetafieldDefinitions($ownerId: ID!, $first: Int, $pinnedStatus: MetafieldDefinitionPinnedStatus, $sortKey: MetafieldDefinitionSortKeys) {
      customer(id: $ownerId) {
        metafieldDefinitions(first: $first, pinnedStatus: $pinnedStatus, sortKey: $sortKey) {
          edges {
            node {
              name
              namespace
              key
              type {
                name
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "pinnedStatus": "PINNED",
          "ownerId": "gid://shopify/Customer/544365967",
          "first": 10,
          "sortKey": "PINNED_POSITION"
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
    query CustomerMetafieldDefinitions($ownerId: ID!, $first: Int, $pinnedStatus: MetafieldDefinitionPinnedStatus, $sortKey: MetafieldDefinitionSortKeys) {
      customer(id: $ownerId) {
        metafieldDefinitions(first: $first, pinnedStatus: $pinnedStatus, sortKey: $sortKey) {
          edges {
            node {
              name
              namespace
              key
              type {
                name
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "pinnedStatus": "PINNED",
    "ownerId": "gid://shopify/Customer/544365967",
    "first": 10,
    "sortKey": "PINNED_POSITION"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query CustomerMetafieldDefinitions($ownerId: ID!, $first: Int, $pinnedStatus: MetafieldDefinitionPinnedStatus, $sortKey: MetafieldDefinitionSortKeys) {
        customer(id: $ownerId) {
          metafieldDefinitions(first: $first, pinnedStatus: $pinnedStatus, sortKey: $sortKey) {
            edges {
              node {
                name
                namespace
                key
                type {
                  name
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "pinnedStatus": "PINNED",
          "ownerId": "gid://shopify/Customer/544365967",
          "first": 10,
          "sortKey": "PINNED_POSITION"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query CustomerMetafieldDefinitions($ownerId: ID!, $first: Int, $pinnedStatus: MetafieldDefinitionPinnedStatus, $sortKey: MetafieldDefinitionSortKeys) {
    customer(id: $ownerId) {
      metafieldDefinitions(first: $first, pinnedStatus: $pinnedStatus, sortKey: $sortKey) {
        edges {
          node {
            name
            namespace
            key
            type {
              name
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "pinnedStatus": "PINNED",
    "ownerId": "gid://shopify/Customer/544365967",
    "first": 10,
    "sortKey": "PINNED_POSITION"
  }'
  ```

  #### Response

  ```json
  {
    "customer": {
      "metafieldDefinitions": {
        "edges": [
          {
            "node": {
              "name": "Pronouns",
              "namespace": "my_fields",
              "key": "pronouns",
              "type": {
                "name": "single_line_text_field"
              }
            }
          },
          {
            "node": {
              "name": "Nickname",
              "namespace": "my_fields",
              "key": "nickname",
              "type": {
                "name": "single_line_text_field"
              }
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieves a list of addresses for a customer

  #### Description

  This query retrieves the default address and the first 10 secondary addresses for a \[customer]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/customer) using the \`addressesV2\` field. Use the \`id\` argument to specify the customer.

  #### Query

  ```graphql
  query CustomerAddressList($id: ID!) {
    customer(id: $id) {
      defaultAddress {
        address1
        city
      }
      addressesV2(first: 10) {
        edges {
          node {
            address1
            city
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Customer/544365967"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query CustomerAddressList($id: ID!) { customer(id: $id) { defaultAddress { address1 city } addressesV2(first: 10) { edges { node { address1 city } } } } }",
   "variables": {
      "id": "gid://shopify/Customer/544365967"
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
    query CustomerAddressList($id: ID!) {
      customer(id: $id) {
        defaultAddress {
          address1
          city
        }
        addressesV2(first: 10) {
          edges {
            node {
              address1
              city
            }
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Customer/544365967"
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
    query CustomerAddressList($id: ID!) {
      customer(id: $id) {
        defaultAddress {
          address1
          city
        }
        addressesV2(first: 10) {
          edges {
            node {
              address1
              city
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Customer/544365967"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query CustomerAddressList($id: ID!) {
        customer(id: $id) {
          defaultAddress {
            address1
            city
          }
          addressesV2(first: 10) {
            edges {
              node {
                address1
                city
              }
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Customer/544365967"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query CustomerAddressList($id: ID!) {
    customer(id: $id) {
      defaultAddress {
        address1
        city
      }
      addressesV2(first: 10) {
        edges {
          node {
            address1
            city
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Customer/544365967"
  }'
  ```

  #### Response

  ```json
  {
    "customer": {
      "defaultAddress": {
        "address1": "123 Amoebobacterieae St",
        "city": "Ottawa"
      },
      "addressesV2": {
        "edges": [
          {
            "node": {
              "address1": "123 Amoebobacterieae St",
              "city": "Ottawa"
            }
          }
        ]
      }
    }
  }
  ```
