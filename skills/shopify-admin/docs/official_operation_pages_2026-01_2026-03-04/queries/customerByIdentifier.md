---
title: customerByIdentifier - GraphQL Admin
description: Return a customer by an identifier.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/customerByIdentifier
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/customerByIdentifier.md
---

# customer​By​Identifier

query

Requires `read_customers` access scope.

Return a customer by an identifier.

## Arguments

* identifier

  [Customer​Identifier​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CustomerIdentifierInput)

  required

  The identifier of the customer.

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

* ### Find a customer by custom id

  #### Query

  ```graphql
  query($identifier: CustomerIdentifierInput!) {
    customer: customerByIdentifier(identifier: $identifier) {
      id
      amountSpent {
        amount
        currencyCode
      }
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
        "value": "16a3a6dd"
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
  "query": "query($identifier: CustomerIdentifierInput!) { customer: customerByIdentifier(identifier: $identifier) { id amountSpent { amount currencyCode } } }",
   "variables": {
      "identifier": {
        "customId": {
          "namespace": "custom",
          "key": "id",
          "value": "16a3a6dd"
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
    query($identifier: CustomerIdentifierInput!) {
      customer: customerByIdentifier(identifier: $identifier) {
        id
        amountSpent {
          amount
          currencyCode
        }
      }
    }`,
    {
      variables: {
          "identifier": {
              "customId": {
                  "namespace": "custom",
                  "key": "id",
                  "value": "16a3a6dd"
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
    query($identifier: CustomerIdentifierInput!) {
      customer: customerByIdentifier(identifier: $identifier) {
        id
        amountSpent {
          amount
          currencyCode
        }
      }
    }
  QUERY

  variables = {
    "identifier": {
      "customId": {
        "namespace": "custom",
        "key": "id",
        "value": "16a3a6dd"
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
      "query": `query($identifier: CustomerIdentifierInput!) {
        customer: customerByIdentifier(identifier: $identifier) {
          id
          amountSpent {
            amount
            currencyCode
          }
        }
      }`,
      "variables": {
          "identifier": {
              "customId": {
                  "namespace": "custom",
                  "key": "id",
                  "value": "16a3a6dd"
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
  'query($identifier: CustomerIdentifierInput!) {
    customer: customerByIdentifier(identifier: $identifier) {
      id
      amountSpent {
        amount
        currencyCode
      }
    }
  }' \
  --variables \
  '{
    "identifier": {
      "customId": {
        "namespace": "custom",
        "key": "id",
        "value": "16a3a6dd"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "customer": {
      "id": "gid://shopify/Customer/544365967",
      "amountSpent": {
        "amount": "8305.6",
        "currencyCode": "USD"
      }
    }
  }
  ```

* ### Find a customer by email address

  #### Query

  ```graphql
  query($identifier: CustomerIdentifierInput!) {
    customer: customerByIdentifier(identifier: $identifier) {
      id
      amountSpent {
        amount
        currencyCode
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "identifier": {
      "emailAddress": "bob@example.com"
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
  "query": "query($identifier: CustomerIdentifierInput!) { customer: customerByIdentifier(identifier: $identifier) { id amountSpent { amount currencyCode } } }",
   "variables": {
      "identifier": {
        "emailAddress": "bob@example.com"
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
    query($identifier: CustomerIdentifierInput!) {
      customer: customerByIdentifier(identifier: $identifier) {
        id
        amountSpent {
          amount
          currencyCode
        }
      }
    }`,
    {
      variables: {
          "identifier": {
              "emailAddress": "bob@example.com"
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
    query($identifier: CustomerIdentifierInput!) {
      customer: customerByIdentifier(identifier: $identifier) {
        id
        amountSpent {
          amount
          currencyCode
        }
      }
    }
  QUERY

  variables = {
    "identifier": {
      "emailAddress": "bob@example.com"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query($identifier: CustomerIdentifierInput!) {
        customer: customerByIdentifier(identifier: $identifier) {
          id
          amountSpent {
            amount
            currencyCode
          }
        }
      }`,
      "variables": {
          "identifier": {
              "emailAddress": "bob@example.com"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query($identifier: CustomerIdentifierInput!) {
    customer: customerByIdentifier(identifier: $identifier) {
      id
      amountSpent {
        amount
        currencyCode
      }
    }
  }' \
  --variables \
  '{
    "identifier": {
      "emailAddress": "bob@example.com"
    }
  }'
  ```

  #### Response

  ```json
  {
    "customer": {
      "id": "gid://shopify/Customer/544365967",
      "amountSpent": {
        "amount": "8305.6",
        "currencyCode": "USD"
      }
    }
  }
  ```

* ### Find a customer by phone number

  #### Query

  ```graphql
  query($identifier: CustomerIdentifierInput!) {
    customer: customerByIdentifier(identifier: $identifier) {
      id
      amountSpent {
        amount
        currencyCode
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "identifier": {
      "phoneNumber": "+13125551212"
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
  "query": "query($identifier: CustomerIdentifierInput!) { customer: customerByIdentifier(identifier: $identifier) { id amountSpent { amount currencyCode } } }",
   "variables": {
      "identifier": {
        "phoneNumber": "+13125551212"
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
    query($identifier: CustomerIdentifierInput!) {
      customer: customerByIdentifier(identifier: $identifier) {
        id
        amountSpent {
          amount
          currencyCode
        }
      }
    }`,
    {
      variables: {
          "identifier": {
              "phoneNumber": "+13125551212"
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
    query($identifier: CustomerIdentifierInput!) {
      customer: customerByIdentifier(identifier: $identifier) {
        id
        amountSpent {
          amount
          currencyCode
        }
      }
    }
  QUERY

  variables = {
    "identifier": {
      "phoneNumber": "+13125551212"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query($identifier: CustomerIdentifierInput!) {
        customer: customerByIdentifier(identifier: $identifier) {
          id
          amountSpent {
            amount
            currencyCode
          }
        }
      }`,
      "variables": {
          "identifier": {
              "phoneNumber": "+13125551212"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query($identifier: CustomerIdentifierInput!) {
    customer: customerByIdentifier(identifier: $identifier) {
      id
      amountSpent {
        amount
        currencyCode
      }
    }
  }' \
  --variables \
  '{
    "identifier": {
      "phoneNumber": "+13125551212"
    }
  }'
  ```

  #### Response

  ```json
  {
    "customer": {
      "id": "gid://shopify/Customer/544365967",
      "amountSpent": {
        "amount": "8305.6",
        "currencyCode": "USD"
      }
    }
  }
  ```
