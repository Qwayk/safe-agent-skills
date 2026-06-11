---
title: order - GraphQL Admin
description: >-
  The `order` query retrieves an
  [order](https://shopify.dev/docs/api/admin-graphql/latest/objects/order) by
  its ID. This query provides access to comprehensive order information such as
  customer details, line items, financial data, and fulfillment status.


  Use the `order` query to retrieve information associated with the following
  processes:


  - [Order management and
  fulfillment](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps)

  - [Financial reporting](https://help.shopify.com/manual/finance)

  - [Customer purchase
  history](https://help.shopify.com/manual/reports-and-analytics/shopify-reports/report-types/default-reports/customers-reports)
  and [transaction
  analysis](https://shopify.dev/docs/apps/launch/billing/view-charges-earnings#transaction-data-through-the-graphql-admin-api)

  - [Shipping](https://shopify.dev/docs/apps/build/checkout/delivery-shipping)
  and [inventory
  management](https://shopify.dev/docs/apps/build/orders-fulfillment/inventory-management-apps)


  You can only retrieve the last 60 days worth of orders from a store by
  default. If you want to access older orders, then you need to [request access
  to all
  orders](https://shopify.dev/docs/api/usage/access-scopes#orders-permissions).


  For large order datasets, consider using [bulk
  operations](https://shopify.dev/docs/api/usage/bulk-operations/queries).

  Bulk operations handle pagination automatically and allow you to retrieve data
  asynchronously without being constrained by API rate limits.

  Learn more about [creating
  orders](https://shopify.dev/docs/api/admin-graphql/latest/mutations/ordercreate)
  and [building order management
  apps](https://shopify.dev/docs/apps/build/orders-fulfillment).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/order'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/order.md'
---

# order

query

The `order` query retrieves an [order](https://shopify.dev/docs/api/admin-graphql/latest/objects/order) by its ID. This query provides access to comprehensive order information such as customer details, line items, financial data, and fulfillment status.

Use the `order` query to retrieve information associated with the following processes:

* [Order management and fulfillment](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps)
* [Financial reporting](https://help.shopify.com/manual/finance)
* [Customer purchase history](https://help.shopify.com/manual/reports-and-analytics/shopify-reports/report-types/default-reports/customers-reports) and [transaction analysis](https://shopify.dev/docs/apps/launch/billing/view-charges-earnings#transaction-data-through-the-graphql-admin-api)
* [Shipping](https://shopify.dev/docs/apps/build/checkout/delivery-shipping) and [inventory management](https://shopify.dev/docs/apps/build/orders-fulfillment/inventory-management-apps)

You can only retrieve the last 60 days worth of orders from a store by default. If you want to access older orders, then you need to [request access to all orders](https://shopify.dev/docs/api/usage/access-scopes#orders-permissions).

For large order datasets, consider using [bulk operations](https://shopify.dev/docs/api/usage/bulk-operations/queries). Bulk operations handle pagination automatically and allow you to retrieve data asynchronously without being constrained by API rate limits. Learn more about [creating orders](https://shopify.dev/docs/api/admin-graphql/latest/mutations/ordercreate) and [building order management apps](https://shopify.dev/docs/apps/build/orders-fulfillment).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `Order` to return.

***

## Possible returns

* Order

  [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

  The `Order` object represents a customer's request to purchase one or more products from a store. Use the `Order` object to handle the complete purchase lifecycle from checkout to fulfillment.

  Use the `Order` object when you need to:

  * Display order details on customer account pages or admin dashboards.
  * Create orders for phone sales, wholesale customers, or subscription services.
  * Update order information like shipping addresses, notes, or fulfillment status.
  * Process returns, exchanges, and partial refunds.
  * Generate invoices, receipts, and shipping labels.

  The `Order` object serves as the central hub connecting customer information, product details, payment processing, and fulfillment data within the GraphQL Admin API schema.

  ***

  **Note:** Only the last 60 days\&#39; worth of orders from a store are accessible from the \<code>Order\</code> object by default. If you want to access older records, then you need to \<a href="https://shopify.dev/docs/api/usage/access-scopes#orders-permissions">request access to all orders\</a>. If your app is granted access, then you can add the \<code>\<span class="PreventFireFoxApplyingGapToWBR">read\<wbr/>\_all\<wbr/>\_orders\</span>\</code>, \<code>\<span class="PreventFireFoxApplyingGapToWBR">read\<wbr/>\_orders\</span>\</code>, and \<code>\<span class="PreventFireFoxApplyingGapToWBR">write\<wbr/>\_orders\</span>\</code> scopes.

  ***

  ***

  **Caution:** Only use orders data if it\&#39;s required for your app\&#39;s functionality. Shopify will restrict \<a href="https://shopify.dev/docs/api/usage/access-scopes#requesting-specific-permissions">access to scopes\</a> for apps that don\&#39;t have a legitimate use for the associated data.

  ***

  Learn more about [building apps for orders and fulfillment](https://shopify.dev/docs/apps/build/orders-fulfillment).

  * additional​Fees

    [\[Additional​Fee!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AdditionalFee)

    non-null

    A list of additional fees applied to an order, such as duties, import fees, or [tax lines](https://shopify.dev/docs/api/admin-graphql/latest/objects/order#field-Order.fields.additionalFees.taxLines).

  * agreements

    [Sales​Agreement​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SalesAgreementConnection)

    non-null

    A list of sales agreements associated with the order, such as contracts defining payment terms, or delivery schedules between merchants and customers.

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

      * happened\_at

        time

      * id

        id

        Filter by `id` range.

        Example:

        * `id:1234`
        * `id:>=1234`
        * `id:<=1234`

    ***

  * alerts

    [\[Resource​Alert!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ResourceAlert)

    non-null

    A list of messages that appear on the **Orders** page in the Shopify admin. These alerts provide merchants with important information about an order's status or required actions.

  * app

    [Order​App](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderApp)

    The application that created the order. For example, "Online Store", "Point of Sale", or a custom app name. Use this to identify the order source for attribution and fulfillment workflows. Learn more about [building apps for orders and fulfillment](https://shopify.dev/docs/apps/build/orders-fulfillment).

  * billing​Address

    [Mailing​Address](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress)

    The billing address associated with the payment method selected by the customer for an order. Returns `null` if no billing address was provided during checkout.

  * billing​Address​Matches​Shipping​Address

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the billing address matches the [shipping address](https://shopify.dev/docs/api/admin-graphql/latest/objects/order#field-Order.fields.shippingAddress). Returns `true` if both addresses are the same, and `false` if they're different or if an address is missing.

  * cancellation

    [Order​Cancellation](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderCancellation)

    Details of an order's cancellation, if it has been canceled. This includes the reason, date, and any [staff notes](https://shopify.dev/api/admin-graphql/latest/objects/OrderCancellation#field-OrderCancellation.fields.staffNote).

  * cancelled​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time in [ISO 8601 format](https://en.wikipedia.org/wiki/ISO_8601) when an order was canceled. Returns `null` if the order hasn't been canceled.

  * cancel​Reason

    [Order​Cancel​Reason](https://shopify.dev/docs/api/admin-graphql/latest/enums/OrderCancelReason)

    The reason provided for an order cancellation. For example, a merchant might cancel an order if there's insufficient inventory. Returns `null` if the order hasn't been canceled.

  * can​Mark​As​Paid

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether an order can be manually marked as paid. Returns `false` if the order is already paid, is canceled, has pending [Shopify Payments](https://help.shopify.com/en/manual/payments/shopify-payments/payouts) transactions, or has a negative payment amount.

  * can​Notify​Customer

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether order notifications can be sent to the customer. Returns `true` if the customer has a valid [email address](https://shopify.dev/docs/api/admin-graphql/latest/objects/order#field-Order.fields.email).

  * capturable

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether an authorized payment for an order can be captured. Returns `true` if an authorized payment exists that hasn't been fully captured yet. Learn more about [capturing payments](https://help.shopify.com/en/manual/fulfillment/managing-orders/payments/capturing-payments).

  * cart​Discount​Amount​Set

    [Money​Bag](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    The total discount amount applied at the time the order was created, displayed in both shop and presentment currencies, before returns, refunds, order edits, and cancellations. This field only includes discounts applied to the entire order.

  * channel​Information

    [Channel​Information](https://shopify.dev/docs/api/admin-graphql/latest/objects/ChannelInformation)

    Details about the sales channel that created the order, such as the [channel app type](https://shopify.dev/docs/api/admin-graphql/latest/objects/channel#field-Channel.fields.channelType) and [channel name](https://shopify.dev/docs/api/admin-graphql/latest/objects/ChannelDefinition#field-ChannelDefinition.fields.channelName), which helps to track order sources.

  * client​Ip

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The IP address of the customer who placed the order. Useful for fraud detection and geographic analysis.

  * closed

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether an order is closed. An order is considered closed if all its line items have been fulfilled or canceled, and all financial transactions are complete.

  * closed​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time [ISO 8601 format](https://en.wikipedia.org/wiki/ISO_8601) when an order was closed. Shopify automatically records this timestamp when all items have been fulfilled or canceled, and all financial transactions are complete. Returns `null` if the order isn't closed.

  * confirmation​Number

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    A customer-facing order identifier, often shown instead of the sequential order name. It uses a random alphanumeric format (for example, `XPAV284CT`) and isn't guaranteed to be unique across orders.

  * confirmed

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether inventory has been reserved for an order. Returns `true` if inventory quantities for an order's [line items](https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem) have been reserved. Learn more about [managing inventory quantities and states](https://shopify.dev/docs/apps/build/orders-fulfillment/inventory-management-apps/manage-quantities-states).

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time in [ISO 8601 format](https://en.wikipedia.org/wiki/ISO_8601) when an order was created. This timestamp is set when the customer completes checkout and remains unchanged throughout an order's lifecycle.

  * currency​Code

    [Currency​Code!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CurrencyCode)

    non-null

    The shop currency when the order was placed. For example, "USD" or "CAD".

  * current​Cart​Discount​Amount​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The current total of all discounts applied to the entire order, after returns, refunds, order edits, and cancellations. This includes discount codes, automatic discounts, and other promotions that affect the whole order rather than individual line items. To get the original discount amount at the time of order creation, use the [`cartDiscountAmountSet`](https://shopify.dev/docs/api/admin-graphql/latest/objects/order#field-Order.fields.cartDiscountAmountSet) field.

  * current​Shipping​Price​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The current shipping price after applying refunds and discounts. If the parent `order.taxesIncluded` field is true, then this price includes taxes. Otherwise, this field is the pre-tax price.

  * current​Subtotal​Line​Items​Quantity

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The current sum of the quantities for all line items that contribute to the order's subtotal price, after returns, refunds, order edits, and cancellations.

  * current​Subtotal​Price​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total price of the order, after returns and refunds, in shop and presentment currencies. This includes taxes and discounts.

  * current​Tax​Lines

    [\[Tax​Line!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TaxLine)

    non-null

    A list of all tax lines applied to line items on the order, after returns. Tax line prices represent the total price for all tax lines with the same `rate` and `title`.

  * current​Total​Additional​Fees​Set

    [Money​Bag](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    The current total of all additional fees for an order, after any returns or modifications. Modifications include returns, refunds, order edits, and cancellations. Additional fees can include charges such as duties, import fees, and special handling.

  * current​Total​Discounts​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total amount discounted on the order after returns and refunds, in shop and presentment currencies. This includes both order and line level discounts.

  * current​Total​Duties​Set

    [Money​Bag](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    The current total duties amount for an order, after any returns or modifications. Modifications include returns, refunds, order edits, and cancellations.

  * current​Total​Price​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total price of the order, after returns, in shop and presentment currencies. This includes taxes and discounts.

  * current​Total​Tax​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The sum of the prices of all tax lines applied to line items on the order, after returns and refunds, in shop and presentment currencies.

  * current​Total​Weight

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The total weight of the order after returns and refunds, in grams.

  * custom​Attributes

    [\[Attribute!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Attribute)

    non-null

    A list of additional information that has been attached to the order. For example, gift message, delivery instructions, or internal notes.

  * customer

    [Customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

    The customer who placed an order. Returns `null` if an order was created through a checkout without customer authentication, such as a guest checkout. Learn more about [customer accounts](https://help.shopify.com/manual/customers/customer-accounts).

  * customer​Accepts​Marketing

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the customer agreed to receive marketing emails at the time of purchase. Use this to ensure compliance with marketing consent laws and to segment customers for email campaigns. Learn more about [building customer segments](https://shopify.dev/docs/apps/build/marketing-analytics/customer-segments).

  * customer​Journey​Summary

    [Customer​Journey​Summary](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerJourneySummary)

    The customer's visits and interactions with the online store before placing the order. Use this to understand customer behavior, attribution sources, and marketing effectiveness to optimize your sales funnel.

  * customer​Locale

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The customer's language and region preference at the time of purchase. For example, "en" for English, "fr-CA" for French (Canada), or "es-MX" for Spanish (Mexico). Use this to provide localized customer service and targeted marketing in the customer's preferred language.

  * discount​Applications

    [Discount​Application​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/DiscountApplicationConnection)

    non-null

    A list of discounts that are applied to the order, excluding order edits and refunds. Includes discount codes, automatic discounts, and other promotions that reduce the order total.

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

  * discount​Code

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The discount code used for an order. Returns `null` if no discount code was applied.

  * discount​Codes

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The discount codes used for the order. Multiple codes can be applied to a single order.

  * display​Address

    [Mailing​Address](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress)

    The primary address of the customer, prioritizing shipping address over billing address when both are available. Returns `null` if neither shipping address nor billing address was provided.

  * display​Financial​Status

    [Order​Display​Financial​Status](https://shopify.dev/docs/api/admin-graphql/latest/enums/OrderDisplayFinancialStatus)

    An order's financial status for display in the Shopify admin.

  * display​Fulfillment​Status

    [Order​Display​Fulfillment​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/OrderDisplayFulfillmentStatus)

    non-null

    The order's fulfillment status that displays in the Shopify admin to merchants. For example, an order might be unfulfilled or scheduled. For detailed processing, use the [`FulfillmentOrder`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder) object.

  * disputes

    [\[Order​Dispute​Summary!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderDisputeSummary)

    non-null

    A list of payment disputes associated with the order, such as chargebacks or payment inquiries. Disputes occur when customers challenge transactions with their bank or payment provider.

  * duties​Included

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether duties are included in the subtotal price of the order. Duties are import taxes charged by customs authorities when goods cross international borders.

  * edited

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the order has had any edits applied. For example, adding or removing line items, updating quantities, or changing prices.

  * email

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The email address associated with the customer for this order. Used for sending order confirmations, shipping notifications, and other order-related communications. Returns `null` if no email address was provided during checkout.

  * estimated​Taxes

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether taxes on the order are estimated. This field returns `false` when taxes on the order are finalized and aren't subject to any changes.

  * events

    [Event​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/EventConnection)

    non-null

    A list of events associated with the order. Events track significant changes and activities related to the order, such as creation, payment, fulfillment, and cancellation.

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

  * fulfillable

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether there are line items that can be fulfilled. This field returns `false` when the order has no fulfillable line items. For a more granular view of the fulfillment status, refer to the [FulfillmentOrder](https://shopify.dev/api/admin-graphql/latest/objects/FulfillmentOrder) object.

  * fulfillment​Orders

    [Fulfillment​Order​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/FulfillmentOrderConnection)

    non-null

    A list of [fulfillment orders](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder) for an order. Each fulfillment order groups [line items](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order#field-Order.fields.lineItems) that are fulfilled together, allowing an order to be processed in parts if needed.

    * displayable

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      ### Arguments

      If false, all fulfillment orders will be returned. If true, fulfillment orders that are normally hidden from the merchant will be excluded. For example, fulfillment orders that were closed after being combined or moved are hidden.

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

  * fulfillments

    [\[Fulfillment!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Fulfillment)

    non-null

    A list of shipments for the order. Fulfillments represent the physical shipment of products to customers.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      Truncate the array result to this size.

    * query

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      Optional query string to filter fulfillments by timestamps. Examples: `created_at:>='2024-05-07T08:37:00Z' updated_at:<'2025-05-07T08:37:00Z'`, `created_at:'2024-05-07T08:37:00Z'`

    ***

  * fulfillments​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    The total number of fulfillments for the order, including canceled ones.

  * fully​Paid

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the order has been paid in full. This field returns `true` when the total amount received equals or exceeds the order total.

  * has​Timeline​Comment

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the merchant has added a timeline comment to the order.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * legacy​Resource​Id

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The ID of the corresponding resource in the REST Admin API.

  * line​Items

    [Line​Item​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/LineItemConnection)

    non-null

    A list of the order's line items. Line items represent the individual products and quantities that make up the order.

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

  * localized​Fields

    [Localized​Field​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/LocalizedFieldConnection)

    non-null

    List of localized fields for the resource.

    * country​Codes

      [\[Country​Code!\]](https://shopify.dev/docs/api/admin-graphql/latest/enums/CountryCode)

      ### Arguments

      The country codes of the extensions.

    * purposes

      [\[Localized​Field​Purpose!\]](https://shopify.dev/docs/api/admin-graphql/latest/enums/LocalizedFieldPurpose)

      The purpose of the extensions.

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

  * merchant​Business​Entity

    [Business​Entity!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessEntity)

    non-null

    The legal business structure that the merchant operates under for this order, such as an LLC, corporation, or partnership. Used for tax reporting, legal compliance, and determining which business entity is responsible for the order.

  * merchant​Editable

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the order can be edited by the merchant. Returns `false` for orders that can't be modified, such as canceled orders or orders with specific payment statuses.

  * merchant​Editable​Errors

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A list of reasons why the order can't be edited. For example, canceled orders can't be edited.

  * merchant​Of​Record​App

    [Order​App](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderApp)

    The application acting as the Merchant of Record for the order. The Merchant of Record is responsible for tax collection and remittance.

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

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The unique identifier for the order that appears on the order page in the Shopify admin and the **Order status** page. For example, "#1001", "EN1001", or "1001-A". This value isn't unique across multiple stores. Use this field to identify orders in the Shopify admin and for order tracking.

  * net​Payment​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The net payment for the order, based on the total amount received minus the total amount refunded, in shop and presentment currencies.

  * non​Fulfillable​Line​Items

    [Line​Item​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/LineItemConnection)

    non-null

    A list of line items that can't be fulfilled. For example, tips and fully refunded line items can't be fulfilled. For a more granular view of the fulfillment status, refer to the [FulfillmentOrder](https://shopify.dev/api/admin-graphql/latest/objects/FulfillmentOrder) object.

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

  * note

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The note associated with the order. Contains additional information or instructions added by merchants or customers during the order process. Commonly used for special delivery instructions, gift messages, or internal processing notes.

  * number

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The order number used to generate the name using the store's configured order number prefix/suffix. This number isn't guaranteed to follow a consecutive integer sequence (e.g. 1, 2, 3..), nor is it guaranteed to be unique across multiple stores, or even for a single store.

  * original​Total​Additional​Fees​Set

    [Money​Bag](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    The total amount of all additional fees, such as import fees or taxes, that were applied when an order was created. Returns `null` if additional fees aren't applicable.

  * original​Total​Duties​Set

    [Money​Bag](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    The total amount of duties calculated when an order was created, before any modifications. Modifications include returns, refunds, order edits, and cancellations. Use [`currentTotalDutiesSet`](https://shopify.dev/docs/api/admin-graphql/latest/objects/order#field-Order.fields.currentTotalDutiesSet) to retrieve the current duties amount after adjustments.

  * original​Total​Price​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total price of the order at the time of order creation, in shop and presentment currencies. Use this to compare the original order value against the current total after edits, returns, or refunds.

  * payment​Collection​Details

    [Order​Payment​Collection​Details!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderPaymentCollectionDetails)

    non-null

    The payment collection details for the order, including payment status, outstanding amounts, and collection information. Use this to understand when and how payments should be collected, especially for orders with deferred or installment payment terms.

  * payment​Gateway​Names

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A list of the names of all payment gateways used for the order. For example, "Shopify Payments" and "Cash on Delivery (COD)".

  * payment​Terms

    [Payment​Terms](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTerms)

    The payment terms associated with the order, such as net payment due dates or early payment discounts. Payment terms define when and how an order should be paid. Returns `null` if no specific payment terms were set for the order.

  * phone

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The phone number associated with the customer for this order. Useful for contacting customers about shipping updates, delivery notifications, or order issues. Returns `null` if no phone number was provided during checkout.

  * po​Number

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The purchase order (PO) number that's associated with an order. This is typically provided by business customers who require a PO number for their procurement.

  * presentment​Currency​Code

    [Currency​Code!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CurrencyCode)

    non-null

    The currency used by the customer when placing the order. For example, "USD", "EUR", or "CAD". This may differ from the shop's base currency when serving international customers or using multi-currency pricing.

  * processed​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time in [ISO 8601 format](https://en.wikipedia.org/wiki/ISO_8601) when the order was processed. This date and time might not match the date and time when the order was created.

  * product​Network

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the customer also purchased items from other stores in the network.

  * publication

    [Publication](https://shopify.dev/docs/api/admin-graphql/latest/objects/Publication)

    The sales channel that the order was created from, such as the [Online Store](https://shopify.dev/docs/apps/build/app-surfaces#online-store) or [Shopify POS](https://shopify.dev/docs/apps/build/app-surfaces#point-of-sale).

  * purchasing​Entity

    [Purchasing​Entity](https://shopify.dev/docs/api/admin-graphql/latest/unions/PurchasingEntity)

    The business entity that placed the order, including company details and purchasing relationships. Used for B2B transactions to track which company or organization is responsible for the purchase and payment terms.

  * refundable

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the order can be refunded based on its payment transactions. Returns `false` for orders with no eligible payment transactions, such as fully refunded orders or orders with non-refundable payment methods.

  * refund​Discrepancy​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The difference between the suggested and actual refund amount of all refunds that have been applied to the order. A positive value indicates a difference in the merchant's favor, and a negative value indicates a difference in the customer's favor.

  * refunds

    [\[Refund!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Refund)

    non-null

    A list of refunds that have been applied to the order. Refunds represent money returned to customers for returned items, cancellations, or adjustments.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      Truncate the array result to this size.

    ***

  * registered​Source​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    The URL of the source that the order originated from, if found in the domain registry. Returns `null` if the source URL isn't in the domain registry.

  * requires​Shipping

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the order requires physical shipping to the customer. Returns `false` for digital-only orders (such as gift cards or downloadable products) and `true` for orders with physical products that need delivery. Use this to determine shipping workflows and logistics requirements.

  * restockable

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether any line items on the order can be restocked into inventory. Returns `false` for digital products, custom items, or items that can't be resold.

  * retail​Location

    [Location](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)

    The physical location where a retail order is created or completed, except for draft POS orders completed using the "mark as paid" flow in the Shopify admin, which return `null`. Transactions associated with the order might have been processed at a different location.

  * returns

    [Return​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ReturnConnection)

    non-null

    The returns associated with the order. Contains information about items that customers have requested to return, including return reasons, status, and refund details. Use this to track and manage the return process for order items.

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

      * * id

          id

        * status

          string

        - Filter by `id` range.

        - Example:
          * `id:1234`
          * `id:>=1234`
          * `id:<=1234`

    ***

  * return​Status

    [Order​Return​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/OrderReturnStatus)

    non-null

    The order's aggregated return status for display purposes. Indicates the overall state of returns for the order, helping merchants track and manage the return process.

  * risk

    [Order​Risk​Summary!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderRiskSummary)

    non-null

    The risk assessment summary for the order. Provides fraud analysis and risk scoring to help you identify potentially fraudulent orders. Use this to make informed decisions about order fulfillment and payment processing.

  * shipping​Address

    [Mailing​Address](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress)

    The shipping address where the order will be delivered. Contains the customer's delivery location for fulfillment and shipping label generation. Returns `null` for digital orders or orders that don't require shipping.

  * shipping​Line

    [Shipping​Line](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShippingLine)

    A summary of all shipping costs on the order. Aggregates shipping charges, discounts, and taxes to provide a single view of delivery costs.

  * shipping​Lines

    [Shipping​Line​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ShippingLineConnection)

    non-null

    The shipping methods applied to the order. Each shipping line represents a shipping option chosen during checkout, including the carrier, service level, and cost. Use this to understand shipping charges and delivery options for the order.

    * include​Removals

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      ### Arguments

      Whether results should contain removed shipping lines.

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

  * shopify​Protect

    [Shopify​Protect​Order​Summary](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShopifyProtectOrderSummary)

    The Shopify Protect details for the order, including fraud protection status and coverage information. Shopify Protect helps protect eligible orders against fraudulent chargebacks. Returns `null` if Shopify Protect is disabled for the shop or the order isn't eligible for protection. Learn more about [Shopify Protect](https://www.shopify.com/protect).

  * source​Identifier

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    A unique POS or third party order identifier. For example, "1234-12-1000" or "111-98567-54". The [`receiptNumber`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order#field-receiptNumber) field is derived from this value for POS orders.

  * source​Name

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The name of the source associated with the order, such as "web", "mobile\_app", or "pos". Use this field to identify the platform where the order was placed.

  * staff​Member

    [Staff​Member](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember)

    The staff member who created or is responsible for the order. Useful for tracking which team member handled phone orders, manual orders, or order modifications. Returns `null` for orders created directly by customers through the online store.

  * status​Page​Url

    [URL!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    non-null

    The URL where customers can check their order's current status, including tracking information and delivery updates. Provides order tracking links in emails, apps, or customer communications.

    * audience

      [Audience](https://shopify.dev/docs/api/admin-graphql/latest/enums/Audience)

      ### Arguments

      Specifies the intended audience for the status page URL.

    * notification​Usage

      [Notification​Usage](https://shopify.dev/docs/api/admin-graphql/latest/enums/NotificationUsage)

      Specifies the intended notification usage for the status page URL.

    ***

  * subtotal​Line​Items​Quantity

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The sum of quantities for all line items that contribute to the order's subtotal price. This excludes quantities for items like tips, shipping costs, or gift cards that don't affect the subtotal. Use this to quickly understand the total item count for pricing calculations.

  * subtotal​Price​Set

    [Money​Bag](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    The sum of the prices for all line items after discounts and before returns, in shop and presentment currencies. If `taxesIncluded` is `true`, then the subtotal also includes tax.

  * suggested​Refund

    [Suggested​Refund](https://shopify.dev/docs/api/admin-graphql/latest/objects/SuggestedRefund)

    A calculated refund suggestion for the order based on specified line items, shipping, and duties. Use this to preview refund amounts, taxes, and processing fees before creating an actual refund.

    * shipping​Amount

      [Money](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

      ### Arguments

      The amount to refund for shipping. Overrides the `refundShipping` argument.

    * refund​Shipping

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Whether to refund the full shipping amount.

    * refund​Line​Items

      [\[Refund​Line​Item​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/RefundLineItemInput)

      The line items from the order to include in the refund.

    * refund​Duties

      [\[Refund​Duty​Input!\]](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/RefundDutyInput)

      The duties from the order to include in the refund.

    * suggest​Full​Refund

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Whether the suggested refund should be created from all refundable line items on the order. If `true`, the `refundLineItems` argument will be ignored.

    * refund​Method​Allocation

      [Refund​Method​Allocation](https://shopify.dev/docs/api/admin-graphql/latest/enums/RefundMethodAllocation)

      Default:ORIGINAL\_PAYMENT\_METHODS

      Specifies which refund methods to allocate the suggested refund amount to.

    ***

  * tags

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A comma separated list of tags associated with the order. Updating `tags` overwrites any existing tags that were previously added to the order. To add new tags without overwriting existing tags, use the [tagsAdd](https://shopify.dev/api/admin-graphql/latest/mutations/tagsadd) mutation.

  * taxes​Included

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether taxes are included in the subtotal price of the order. When `true`, the subtotal and line item prices include tax amounts. When `false`, taxes are calculated and displayed separately.

  * tax​Exempt

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether taxes are exempt on the order. Returns `true` for orders where the customer or business has a valid tax exemption, such as non-profit organizations or tax-free purchases. Use this to understand if tax calculations were skipped during checkout.

  * tax​Lines

    [\[Tax​Line!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TaxLine)

    non-null

    A list of all tax lines applied to line items on the order, before returns. Tax line prices represent the total price for all tax lines with the same `rate` and `title`.

  * test

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the order is a test. Test orders are made using the Shopify Bogus Gateway or a payment provider with test mode enabled. A test order can't be converted into a real order and vice versa.

  * total​Capturable​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The authorized amount that's uncaptured or undercaptured, in shop and presentment currencies. This amount isn't adjusted for returns.

  * total​Cash​Rounding​Adjustment

    [Cash​Rounding​Adjustment!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CashRoundingAdjustment)

    non-null

    The total rounding adjustment applied to payments or refunds for an order involving cash payments. Applies to some countries where cash transactions are rounded to the nearest currency denomination.

  * total​Discounts​Set

    [Money​Bag](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    The total amount discounted on the order before returns, in shop and presentment currencies. This includes both order and line level discounts.

  * total​Outstanding​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total amount not yet transacted for the order, in shop and presentment currencies. A positive value indicates a difference in the merchant's favor (payment from customer to merchant) and a negative value indicates a difference in the customer's favor (refund from merchant to customer).

  * total​Price​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total price of the order, before returns, in shop and presentment currencies. This includes taxes and discounts.

  * total​Received​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total amount received from the customer before returns, in shop and presentment currencies.

  * total​Refunded​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total amount that was refunded, in shop and presentment currencies.

  * total​Refunded​Shipping​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total amount of shipping that was refunded, in shop and presentment currencies.

  * total​Shipping​Price​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total shipping costs returned to the customer, in shop and presentment currencies. This includes fees and any related discounts that were refunded.

  * total​Tax​Set

    [Money​Bag](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    The total tax amount before returns, in shop and presentment currencies.

  * total​Tip​Received​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The sum of all tip amounts for the order, in shop and presentment currencies.

  * total​Weight

    [Unsigned​Int64](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    The total weight of the order before returns, in grams.

  * transactions

    [\[Order​Transaction!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderTransaction)

    non-null

    A list of transactions associated with the order.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      Truncate the array result to this size.

    * capturable

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Filter transactions by whether they are capturable.

    * manually​Resolvable

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Filter transactions by whether they can be resolved manually. For example, fully captured or voided transactions aren't manually resolvable.

    ***

  * transactions​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    The number of transactions associated with the order.

  * unpaid

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether no payments have been made for the order.

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time in [ISO 8601 format](https://en.wikipedia.org/wiki/ISO_8601) when the order was last modified.

  * cart​Discount​Amount

    [Money](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    Deprecated

  * channel

    [Channel](https://shopify.dev/docs/api/admin-graphql/latest/objects/Channel)

    Deprecated

  * customer​Journey

    [Customer​Journey](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerJourney)

    Deprecated

  * landing​Page​Display​Text

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Deprecated

  * landing​Page​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    Deprecated

  * localization​Extensions

    [Localization​Extension​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/LocalizationExtensionConnection)

    non-nullDeprecated

    * country​Codes

      [\[Country​Code!\]](https://shopify.dev/docs/api/admin-graphql/latest/enums/CountryCode)

      ### Arguments

      The country codes of the extensions.

    * purposes

      [\[Localization​Extension​Purpose!\]](https://shopify.dev/docs/api/admin-graphql/latest/enums/LocalizationExtensionPurpose)

      The purpose of the extensions.

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

  * net​Payment

    [Money!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    non-nullDeprecated

  * physical​Location

    [Location](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)

    Deprecated

  * referral​Code

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Deprecated

  * referrer​Display​Text

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Deprecated

  * referrer​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    Deprecated

  * risk​Level

    [Order​Risk​Level!](https://shopify.dev/docs/api/admin-graphql/latest/enums/OrderRiskLevel)

    non-nullDeprecated

  * risks

    [\[Order​Risk!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderRisk)

    non-nullDeprecated

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      Truncate the array result to this size.

    ***

  * subtotal​Price

    [Money](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    Deprecated

  * total​Capturable

    [Money!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    non-nullDeprecated

  * total​Discounts

    [Money](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    Deprecated

  * total​Price

    [Money!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    non-nullDeprecated

  * total​Received

    [Money!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    non-nullDeprecated

  * total​Refunded

    [Money!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    non-nullDeprecated

  * total​Shipping​Price

    [Money!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    non-nullDeprecated

  * total​Tax

    [Money](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    Deprecated

  * total​Tip​Received

    [Money​V2!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyV2)

    non-nullDeprecated

***

## Examples

* ### Calculate a full duty refund

  #### Description

  This query retrieves the full refund amount for duty on an order by requesting a \`FULL\` \[refund type]\(https://shopify.dev/docs/api/admin-graphql/latest/enums/RefundDutyRefundType). The example uses the \`refundDuties\` field within a \[\`RefundDutyInput\`]\(https://shopify.dev/docs/api/admin-graphql/latest/input\_objects/RefundDutyInput) input object to calculate the refund.

  #### Query

  ```graphql
  query suggestedRefund {
    order(id: "gid://shopify/Order/469306983") {
      suggestedRefund(refundDuties: [{dutyId: "gid://shopify/Duty/1064114503", refundType: FULL}]) {
        refundDuties {
          amountSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          originalDuty {
            id
          }
        }
        totalDutiesSet {
          shopMoney {
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
  "query": "query suggestedRefund { order(id: \"gid://shopify/Order/469306983\") { suggestedRefund(refundDuties: [{dutyId: \"gid://shopify/Duty/1064114503\", refundType: FULL}]) { refundDuties { amountSet { shopMoney { amount currencyCode } } originalDuty { id } } totalDutiesSet { shopMoney { amount currencyCode } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query suggestedRefund {
      order(id: "gid://shopify/Order/469306983") {
        suggestedRefund(refundDuties: [{dutyId: "gid://shopify/Duty/1064114503", refundType: FULL}]) {
          refundDuties {
            amountSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            originalDuty {
              id
            }
          }
          totalDutiesSet {
            shopMoney {
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
    query suggestedRefund {
      order(id: "gid://shopify/Order/469306983") {
        suggestedRefund(refundDuties: [{dutyId: "gid://shopify/Duty/1064114503", refundType: FULL}]) {
          refundDuties {
            amountSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            originalDuty {
              id
            }
          }
          totalDutiesSet {
            shopMoney {
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
    data: `query suggestedRefund {
      order(id: "gid://shopify/Order/469306983") {
        suggestedRefund(refundDuties: [{dutyId: "gid://shopify/Duty/1064114503", refundType: FULL}]) {
          refundDuties {
            amountSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            originalDuty {
              id
            }
          }
          totalDutiesSet {
            shopMoney {
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
  'query suggestedRefund {
    order(id: "gid://shopify/Order/469306983") {
      suggestedRefund(refundDuties: [{dutyId: "gid://shopify/Duty/1064114503", refundType: FULL}]) {
        refundDuties {
          amountSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          originalDuty {
            id
          }
        }
        totalDutiesSet {
          shopMoney {
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
    "order": {
      "suggestedRefund": {
        "refundDuties": [
          {
            "amountSet": {
              "shopMoney": {
                "amount": "8.97",
                "currencyCode": "USD"
              }
            },
            "originalDuty": {
              "id": "gid://shopify/Duty/1064114503"
            }
          }
        ],
        "totalDutiesSet": {
          "shopMoney": {
            "amount": "8.97",
            "currencyCode": "USD"
          }
        }
      }
    }
  }
  ```

* ### Calculate a proportional duty refund

  #### Description

  This query calculates the duty refund amount for an order using a \`PROPORTIONAL\` \[refund type]\(https://shopify.dev/docs/api/admin-graphql/latest/enums/RefundDutyRefundType). The duty is refunded in proportion to the items being refunded (for example, if refunding one of three items, a third of the duty would be refunded). The example uses the \[\`RefundDutyInput\`]\(https://shopify.dev/docs/api/admin-graphql/latest/input\_objects/RefundDutyInput) and \[\`RefundLineItemInput\`]\(https://shopify.dev/docs/api/admin-graphql/latest/input\_objects/RefundLineItemInput) input objects to determine the amount that should be refunded to customers for the selected items.

  #### Query

  ```graphql
  query suggestedRefund {
    order(id: "gid://shopify/Order/469306983") {
      suggestedRefund(refundLineItems: [{lineItemId: "gid://shopify/LineItem/983004162", quantity: 1}], refundDuties: [{dutyId: "gid://shopify/Duty/1064114503", refundType: PROPORTIONAL}]) {
        refundDuties {
          amountSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          originalDuty {
            id
          }
        }
        totalDutiesSet {
          shopMoney {
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
  "query": "query suggestedRefund { order(id: \"gid://shopify/Order/469306983\") { suggestedRefund(refundLineItems: [{lineItemId: \"gid://shopify/LineItem/983004162\", quantity: 1}], refundDuties: [{dutyId: \"gid://shopify/Duty/1064114503\", refundType: PROPORTIONAL}]) { refundDuties { amountSet { shopMoney { amount currencyCode } } originalDuty { id } } totalDutiesSet { shopMoney { amount currencyCode } } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query suggestedRefund {
      order(id: "gid://shopify/Order/469306983") {
        suggestedRefund(refundLineItems: [{lineItemId: "gid://shopify/LineItem/983004162", quantity: 1}], refundDuties: [{dutyId: "gid://shopify/Duty/1064114503", refundType: PROPORTIONAL}]) {
          refundDuties {
            amountSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            originalDuty {
              id
            }
          }
          totalDutiesSet {
            shopMoney {
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
    query suggestedRefund {
      order(id: "gid://shopify/Order/469306983") {
        suggestedRefund(refundLineItems: [{lineItemId: "gid://shopify/LineItem/983004162", quantity: 1}], refundDuties: [{dutyId: "gid://shopify/Duty/1064114503", refundType: PROPORTIONAL}]) {
          refundDuties {
            amountSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            originalDuty {
              id
            }
          }
          totalDutiesSet {
            shopMoney {
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
    data: `query suggestedRefund {
      order(id: "gid://shopify/Order/469306983") {
        suggestedRefund(refundLineItems: [{lineItemId: "gid://shopify/LineItem/983004162", quantity: 1}], refundDuties: [{dutyId: "gid://shopify/Duty/1064114503", refundType: PROPORTIONAL}]) {
          refundDuties {
            amountSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            originalDuty {
              id
            }
          }
          totalDutiesSet {
            shopMoney {
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
  'query suggestedRefund {
    order(id: "gid://shopify/Order/469306983") {
      suggestedRefund(refundLineItems: [{lineItemId: "gid://shopify/LineItem/983004162", quantity: 1}], refundDuties: [{dutyId: "gid://shopify/Duty/1064114503", refundType: PROPORTIONAL}]) {
        refundDuties {
          amountSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          originalDuty {
            id
          }
        }
        totalDutiesSet {
          shopMoney {
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
    "order": {
      "suggestedRefund": {
        "refundDuties": [
          {
            "amountSet": {
              "shopMoney": {
                "amount": "8.97",
                "currencyCode": "USD"
              }
            },
            "originalDuty": {
              "id": "gid://shopify/Duty/1064114503"
            }
          }
        ],
        "totalDutiesSet": {
          "shopMoney": {
            "amount": "8.97",
            "currencyCode": "USD"
          }
        }
      }
    }
  }
  ```

* ### Calculate a refund to store credit

  #### Description

  This query calculates a suggested refund for a specific \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order). The example uses the \[\`RefundLineItemInput\`]\(https://shopify.dev/docs/api/admin-graphql/latest/input\_objects/RefundLineItemInput) input object to specify which line items to include in the calculation. The \[\`RefundMethodAllocation\`]\(https://shopify.dev/docs/api/admin-graphql/latest/input\_objects/RefundMethodAllocation) input object is used to specify if the suggested refund should be allocated to store credit or the original payment methods.

  #### Query

  ```graphql
  query SuggestedRefundToStoreCredit($id: ID!, $refundLineItems: [RefundLineItemInput!], $refundMethodAllocation: RefundMethodAllocation!) {
    order(id: $id) {
      id
      suggestedRefund(refundLineItems: $refundLineItems, refundMethodAllocation: $refundMethodAllocation) {
        subtotalSet {
          presentmentMoney {
            amount
            currencyCode
          }
        }
        refundLineItems {
          lineItem {
            id
          }
          quantity
        }
        suggestedTransactions {
          parentTransaction {
            id
          }
          gateway
          formattedGateway
          amountSet {
            presentmentMoney {
              amount
              currencyCode
            }
          }
        }
        suggestedRefundMethods {
          __typename
          amount {
            presentmentMoney {
              amount
              currencyCode
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
    "id": "gid://shopify/Order/1073460046",
    "refundLineItems": [
      {
        "lineItemId": "gid://shopify/LineItem/1071823266",
        "quantity": 1
      }
    ],
    "refundMethodAllocation": "STORE_CREDIT"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query SuggestedRefundToStoreCredit($id: ID!, $refundLineItems: [RefundLineItemInput!], $refundMethodAllocation: RefundMethodAllocation!) { order(id: $id) { id suggestedRefund(refundLineItems: $refundLineItems, refundMethodAllocation: $refundMethodAllocation) { subtotalSet { presentmentMoney { amount currencyCode } } refundLineItems { lineItem { id } quantity } suggestedTransactions { parentTransaction { id } gateway formattedGateway amountSet { presentmentMoney { amount currencyCode } } } suggestedRefundMethods { __typename amount { presentmentMoney { amount currencyCode } } } } } }",
   "variables": {
      "id": "gid://shopify/Order/1073460046",
      "refundLineItems": [
        {
          "lineItemId": "gid://shopify/LineItem/1071823266",
          "quantity": 1
        }
      ],
      "refundMethodAllocation": "STORE_CREDIT"
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
    query SuggestedRefundToStoreCredit($id: ID!, $refundLineItems: [RefundLineItemInput!], $refundMethodAllocation: RefundMethodAllocation!) {
      order(id: $id) {
        id
        suggestedRefund(refundLineItems: $refundLineItems, refundMethodAllocation: $refundMethodAllocation) {
          subtotalSet {
            presentmentMoney {
              amount
              currencyCode
            }
          }
          refundLineItems {
            lineItem {
              id
            }
            quantity
          }
          suggestedTransactions {
            parentTransaction {
              id
            }
            gateway
            formattedGateway
            amountSet {
              presentmentMoney {
                amount
                currencyCode
              }
            }
          }
          suggestedRefundMethods {
            __typename
            amount {
              presentmentMoney {
                amount
                currencyCode
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Order/1073460046",
          "refundLineItems": [
              {
                  "lineItemId": "gid://shopify/LineItem/1071823266",
                  "quantity": 1
              }
          ],
          "refundMethodAllocation": "STORE_CREDIT"
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
    query SuggestedRefundToStoreCredit($id: ID!, $refundLineItems: [RefundLineItemInput!], $refundMethodAllocation: RefundMethodAllocation!) {
      order(id: $id) {
        id
        suggestedRefund(refundLineItems: $refundLineItems, refundMethodAllocation: $refundMethodAllocation) {
          subtotalSet {
            presentmentMoney {
              amount
              currencyCode
            }
          }
          refundLineItems {
            lineItem {
              id
            }
            quantity
          }
          suggestedTransactions {
            parentTransaction {
              id
            }
            gateway
            formattedGateway
            amountSet {
              presentmentMoney {
                amount
                currencyCode
              }
            }
          }
          suggestedRefundMethods {
            __typename
            amount {
              presentmentMoney {
                amount
                currencyCode
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Order/1073460046",
    "refundLineItems": [
      {
        "lineItemId": "gid://shopify/LineItem/1071823266",
        "quantity": 1
      }
    ],
    "refundMethodAllocation": "STORE_CREDIT"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query SuggestedRefundToStoreCredit($id: ID!, $refundLineItems: [RefundLineItemInput!], $refundMethodAllocation: RefundMethodAllocation!) {
        order(id: $id) {
          id
          suggestedRefund(refundLineItems: $refundLineItems, refundMethodAllocation: $refundMethodAllocation) {
            subtotalSet {
              presentmentMoney {
                amount
                currencyCode
              }
            }
            refundLineItems {
              lineItem {
                id
              }
              quantity
            }
            suggestedTransactions {
              parentTransaction {
                id
              }
              gateway
              formattedGateway
              amountSet {
                presentmentMoney {
                  amount
                  currencyCode
                }
              }
            }
            suggestedRefundMethods {
              __typename
              amount {
                presentmentMoney {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Order/1073460046",
          "refundLineItems": [
              {
                  "lineItemId": "gid://shopify/LineItem/1071823266",
                  "quantity": 1
              }
          ],
          "refundMethodAllocation": "STORE_CREDIT"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query SuggestedRefundToStoreCredit($id: ID!, $refundLineItems: [RefundLineItemInput!], $refundMethodAllocation: RefundMethodAllocation!) {
    order(id: $id) {
      id
      suggestedRefund(refundLineItems: $refundLineItems, refundMethodAllocation: $refundMethodAllocation) {
        subtotalSet {
          presentmentMoney {
            amount
            currencyCode
          }
        }
        refundLineItems {
          lineItem {
            id
          }
          quantity
        }
        suggestedTransactions {
          parentTransaction {
            id
          }
          gateway
          formattedGateway
          amountSet {
            presentmentMoney {
              amount
              currencyCode
            }
          }
        }
        suggestedRefundMethods {
          __typename
          amount {
            presentmentMoney {
              amount
              currencyCode
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Order/1073460046",
    "refundLineItems": [
      {
        "lineItemId": "gid://shopify/LineItem/1071823266",
        "quantity": 1
      }
    ],
    "refundMethodAllocation": "STORE_CREDIT"
  }'
  ```

  #### Response

  ```json
  {
    "order": {
      "id": "gid://shopify/Order/1073460046",
      "suggestedRefund": {
        "subtotalSet": {
          "presentmentMoney": {
            "amount": "20.0",
            "currencyCode": "USD"
          }
        },
        "refundLineItems": [
          {
            "lineItem": {
              "id": "gid://shopify/LineItem/1071823266"
            },
            "quantity": 1
          }
        ],
        "suggestedTransactions": [
          {
            "parentTransaction": {
              "id": "gid://shopify/OrderTransaction/1068278508"
            },
            "gateway": "bogus",
            "formattedGateway": "(For Testing) Bogus Gateway",
            "amountSet": {
              "presentmentMoney": {
                "amount": "0.0",
                "currencyCode": "USD"
              }
            }
          }
        ],
        "suggestedRefundMethods": [
          {
            "__typename": "SuggestedStoreCreditRefund",
            "amount": {
              "presentmentMoney": {
                "amount": "20.0",
                "currencyCode": "USD"
              }
            }
          }
        ]
      }
    }
  }
  ```

* ### Calculate a suggested refund

  #### Description

  This query calculates a suggested refund for a specific \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order). The example uses the \[\`RefundLineItemInput\`]\(https://shopify.dev/docs/api/admin-graphql/latest/input\_objects/RefundLineItemInput) input object to specify which line items to include in the calculation and returns the subtotal of each refunded item.

  #### Query

  ```graphql
  query SuggestedRefund($id: ID!, $refundLineItems: [RefundLineItemInput!]) {
    order(id: $id) {
      id
      suggestedRefund(refundLineItems: $refundLineItems) {
        subtotalSet {
          shopMoney {
            amount
            currencyCode
          }
          presentmentMoney {
            amount
            currencyCode
          }
        }
        refundLineItems {
          lineItem {
            id
          }
          quantity
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Order/469306983",
    "refundLineItems": [
      {
        "lineItemId": "gid://shopify/LineItem/983004162",
        "quantity": 1
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query SuggestedRefund($id: ID!, $refundLineItems: [RefundLineItemInput!]) { order(id: $id) { id suggestedRefund(refundLineItems: $refundLineItems) { subtotalSet { shopMoney { amount currencyCode } presentmentMoney { amount currencyCode } } refundLineItems { lineItem { id } quantity } } } }",
   "variables": {
      "id": "gid://shopify/Order/469306983",
      "refundLineItems": [
        {
          "lineItemId": "gid://shopify/LineItem/983004162",
          "quantity": 1
        }
      ]
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
    query SuggestedRefund($id: ID!, $refundLineItems: [RefundLineItemInput!]) {
      order(id: $id) {
        id
        suggestedRefund(refundLineItems: $refundLineItems) {
          subtotalSet {
            shopMoney {
              amount
              currencyCode
            }
            presentmentMoney {
              amount
              currencyCode
            }
          }
          refundLineItems {
            lineItem {
              id
            }
            quantity
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Order/469306983",
          "refundLineItems": [
              {
                  "lineItemId": "gid://shopify/LineItem/983004162",
                  "quantity": 1
              }
          ]
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
    query SuggestedRefund($id: ID!, $refundLineItems: [RefundLineItemInput!]) {
      order(id: $id) {
        id
        suggestedRefund(refundLineItems: $refundLineItems) {
          subtotalSet {
            shopMoney {
              amount
              currencyCode
            }
            presentmentMoney {
              amount
              currencyCode
            }
          }
          refundLineItems {
            lineItem {
              id
            }
            quantity
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Order/469306983",
    "refundLineItems": [
      {
        "lineItemId": "gid://shopify/LineItem/983004162",
        "quantity": 1
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query SuggestedRefund($id: ID!, $refundLineItems: [RefundLineItemInput!]) {
        order(id: $id) {
          id
          suggestedRefund(refundLineItems: $refundLineItems) {
            subtotalSet {
              shopMoney {
                amount
                currencyCode
              }
              presentmentMoney {
                amount
                currencyCode
              }
            }
            refundLineItems {
              lineItem {
                id
              }
              quantity
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Order/469306983",
          "refundLineItems": [
              {
                  "lineItemId": "gid://shopify/LineItem/983004162",
                  "quantity": 1
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query SuggestedRefund($id: ID!, $refundLineItems: [RefundLineItemInput!]) {
    order(id: $id) {
      id
      suggestedRefund(refundLineItems: $refundLineItems) {
        subtotalSet {
          shopMoney {
            amount
            currencyCode
          }
          presentmentMoney {
            amount
            currencyCode
          }
        }
        refundLineItems {
          lineItem {
            id
          }
          quantity
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Order/469306983",
    "refundLineItems": [
      {
        "lineItemId": "gid://shopify/LineItem/983004162",
        "quantity": 1
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "order": {
      "id": "gid://shopify/Order/469306983",
      "suggestedRefund": {
        "subtotalSet": {
          "shopMoney": {
            "amount": "8.26",
            "currencyCode": "USD"
          },
          "presentmentMoney": {
            "amount": "7.0",
            "currencyCode": "EUR"
          }
        },
        "refundLineItems": [
          {
            "lineItem": {
              "id": "gid://shopify/LineItem/983004162"
            },
            "quantity": 1
          }
        ]
      }
    }
  }
  ```

* ### Get an order using the QueryRoot.node field and a GraphQL fragment

  #### Description

  The following query retrieves an order, including the order name.

  #### Query

  ```graphql
  query {
    node(id: "gid://shopify/Order/148977776") {
      id
      ... on Order {
        name
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
  "query": "query { node(id: \"gid://shopify/Order/148977776\") { id ... on Order { name } } }"
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
      node(id: "gid://shopify/Order/148977776") {
        id
        ... on Order {
          name
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
      node(id: "gid://shopify/Order/148977776") {
        id
        ... on Order {
          name
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
      node(id: "gid://shopify/Order/148977776") {
        id
        ... on Order {
          name
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
    node(id: "gid://shopify/Order/148977776") {
      id
      ... on Order {
        name
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "node": {
      "id": "gid://shopify/Order/148977776",
      "name": "#1001"
    }
  }
  ```

* ### Get metafields attached to an order

  #### Description

  Get a page of metafields attached to a specific order.

  #### Query

  ```graphql
  query OrderMetafields($ownerId: ID!) {
    order(id: $ownerId) {
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
    "ownerId": "gid://shopify/Order/148977776"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query OrderMetafields($ownerId: ID!) { order(id: $ownerId) { metafields(first: 3) { edges { node { namespace key value } } } } }",
   "variables": {
      "ownerId": "gid://shopify/Order/148977776"
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
    query OrderMetafields($ownerId: ID!) {
      order(id: $ownerId) {
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
          "ownerId": "gid://shopify/Order/148977776"
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
    query OrderMetafields($ownerId: ID!) {
      order(id: $ownerId) {
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
    "ownerId": "gid://shopify/Order/148977776"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query OrderMetafields($ownerId: ID!) {
        order(id: $ownerId) {
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
          "ownerId": "gid://shopify/Order/148977776"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query OrderMetafields($ownerId: ID!) {
    order(id: $ownerId) {
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
    "ownerId": "gid://shopify/Order/148977776"
  }'
  ```

  #### Response

  ```json
  {
    "order": {
      "metafields": {
        "edges": [
          {
            "node": {
              "namespace": "my_fields",
              "key": "purchase_order",
              "value": "123"
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieve a count of fulfillments associated with an order

  #### Description

  This query retrieves the total number of fulfillments for an \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order). The example uses the \[\`fulfillmentsCount\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order#field-fulfillmentscount) field, which returns the count, eliminating the need to query the full list of fulfillments.

  #### Query

  ```graphql
  query FulfillmentsCount($orderId: ID!) {
    order(id: $orderId) {
      fulfillmentsCount {
        count
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "orderId": "gid://shopify/Order/148977776"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query FulfillmentsCount($orderId: ID!) { order(id: $orderId) { fulfillmentsCount { count } } }",
   "variables": {
      "orderId": "gid://shopify/Order/148977776"
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
    query FulfillmentsCount($orderId: ID!) {
      order(id: $orderId) {
        fulfillmentsCount {
          count
        }
      }
    }`,
    {
      variables: {
          "orderId": "gid://shopify/Order/148977776"
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
    query FulfillmentsCount($orderId: ID!) {
      order(id: $orderId) {
        fulfillmentsCount {
          count
        }
      }
    }
  QUERY

  variables = {
    "orderId": "gid://shopify/Order/148977776"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query FulfillmentsCount($orderId: ID!) {
        order(id: $orderId) {
          fulfillmentsCount {
            count
          }
        }
      }`,
      "variables": {
          "orderId": "gid://shopify/Order/148977776"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query FulfillmentsCount($orderId: ID!) {
    order(id: $orderId) {
      fulfillmentsCount {
        count
      }
    }
  }' \
  --variables \
  '{
    "orderId": "gid://shopify/Order/148977776"
  }'
  ```

  #### Response

  ```json
  {
    "order": {
      "fulfillmentsCount": {
        "count": 0
      }
    }
  }
  ```

* ### Retrieve a count of transactions for an order

  #### Description

  This query retrieves the total number of transactions for an \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order). The example uses the \[\`transactionsCount\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order#field-transactionsCount) field to get the total, without having to retrieve the complete transactions list.

  #### Query

  ```graphql
  query TransactionsCountForOrder($orderId: ID!) {
    order(id: $orderId) {
      transactionsCount {
        count
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "orderId": "gid://shopify/Order/148977776"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query TransactionsCountForOrder($orderId: ID!) { order(id: $orderId) { transactionsCount { count } } }",
   "variables": {
      "orderId": "gid://shopify/Order/148977776"
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
    query TransactionsCountForOrder($orderId: ID!) {
      order(id: $orderId) {
        transactionsCount {
          count
        }
      }
    }`,
    {
      variables: {
          "orderId": "gid://shopify/Order/148977776"
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
    query TransactionsCountForOrder($orderId: ID!) {
      order(id: $orderId) {
        transactionsCount {
          count
        }
      }
    }
  QUERY

  variables = {
    "orderId": "gid://shopify/Order/148977776"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query TransactionsCountForOrder($orderId: ID!) {
        order(id: $orderId) {
          transactionsCount {
            count
          }
        }
      }`,
      "variables": {
          "orderId": "gid://shopify/Order/148977776"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query TransactionsCountForOrder($orderId: ID!) {
    order(id: $orderId) {
      transactionsCount {
        count
      }
    }
  }' \
  --variables \
  '{
    "orderId": "gid://shopify/Order/148977776"
  }'
  ```

  #### Response

  ```json
  {
    "order": {
      "transactionsCount": {
        "count": 4
      }
    }
  }
  ```

* ### Retrieve a list of fulfillment orders

  #### Description

  This query retrieves a list of fulfillment orders for an \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order), providing information about how the order's line items are grouped for fulfillment. It uses the \`fulfillmentOrders\` field to return \[\`FulfillmentOrder\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder) objects that contain data such as assigned location, delivery method, and associated line items.

  #### Query

  ```graphql
  query FulfillmentOrderList($orderId: ID!) {
    order(id: $orderId) {
      fulfillmentOrders(first: 250) {
        nodes {
          id
          createdAt
          updatedAt
          requestStatus
          status
          fulfillAt
          destination {
            id
            address1
            address2
            city
            company
            countryCode
            email
            firstName
            lastName
            phone
            province
            zip
          }
          lineItems(first: 250) {
            nodes {
              id
              totalQuantity
              inventoryItemId
              remainingQuantity
              variant {
                id
              }
            }
          }
          internationalDuties {
            incoterm
          }
          fulfillmentHolds {
            reason
            reasonNotes
          }
          fulfillBy
          deliveryMethod {
            id
            methodType
            minDeliveryDateTime
            maxDeliveryDateTime
            additionalInformation {
              instructions
              phone
            }
            serviceCode
            sourceReference
            presentedName
            brandedPromise {
              handle
              name
            }
          }
          assignedLocation {
            address1
            address2
            city
            countryCode
            location {
              id
            }
            name
            phone
            province
            zip
          }
          merchantRequests(first: 250) {
            nodes {
              message
              requestOptions
              kind
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
    "orderId": "gid://shopify/Order/148977776"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query FulfillmentOrderList($orderId: ID!) { order(id: $orderId) { fulfillmentOrders(first: 250) { nodes { id createdAt updatedAt requestStatus status fulfillAt destination { id address1 address2 city company countryCode email firstName lastName phone province zip } lineItems(first: 250) { nodes { id totalQuantity inventoryItemId remainingQuantity variant { id } } } internationalDuties { incoterm } fulfillmentHolds { reason reasonNotes } fulfillBy deliveryMethod { id methodType minDeliveryDateTime maxDeliveryDateTime additionalInformation { instructions phone } serviceCode sourceReference presentedName brandedPromise { handle name } } assignedLocation { address1 address2 city countryCode location { id } name phone province zip } merchantRequests(first: 250) { nodes { message requestOptions kind } } } } } }",
   "variables": {
      "orderId": "gid://shopify/Order/148977776"
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
    query FulfillmentOrderList($orderId: ID!) {
      order(id: $orderId) {
        fulfillmentOrders(first: 250) {
          nodes {
            id
            createdAt
            updatedAt
            requestStatus
            status
            fulfillAt
            destination {
              id
              address1
              address2
              city
              company
              countryCode
              email
              firstName
              lastName
              phone
              province
              zip
            }
            lineItems(first: 250) {
              nodes {
                id
                totalQuantity
                inventoryItemId
                remainingQuantity
                variant {
                  id
                }
              }
            }
            internationalDuties {
              incoterm
            }
            fulfillmentHolds {
              reason
              reasonNotes
            }
            fulfillBy
            deliveryMethod {
              id
              methodType
              minDeliveryDateTime
              maxDeliveryDateTime
              additionalInformation {
                instructions
                phone
              }
              serviceCode
              sourceReference
              presentedName
              brandedPromise {
                handle
                name
              }
            }
            assignedLocation {
              address1
              address2
              city
              countryCode
              location {
                id
              }
              name
              phone
              province
              zip
            }
            merchantRequests(first: 250) {
              nodes {
                message
                requestOptions
                kind
              }
            }
          }
        }
      }
    }`,
    {
      variables: {
          "orderId": "gid://shopify/Order/148977776"
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
    query FulfillmentOrderList($orderId: ID!) {
      order(id: $orderId) {
        fulfillmentOrders(first: 250) {
          nodes {
            id
            createdAt
            updatedAt
            requestStatus
            status
            fulfillAt
            destination {
              id
              address1
              address2
              city
              company
              countryCode
              email
              firstName
              lastName
              phone
              province
              zip
            }
            lineItems(first: 250) {
              nodes {
                id
                totalQuantity
                inventoryItemId
                remainingQuantity
                variant {
                  id
                }
              }
            }
            internationalDuties {
              incoterm
            }
            fulfillmentHolds {
              reason
              reasonNotes
            }
            fulfillBy
            deliveryMethod {
              id
              methodType
              minDeliveryDateTime
              maxDeliveryDateTime
              additionalInformation {
                instructions
                phone
              }
              serviceCode
              sourceReference
              presentedName
              brandedPromise {
                handle
                name
              }
            }
            assignedLocation {
              address1
              address2
              city
              countryCode
              location {
                id
              }
              name
              phone
              province
              zip
            }
            merchantRequests(first: 250) {
              nodes {
                message
                requestOptions
                kind
              }
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "orderId": "gid://shopify/Order/148977776"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query FulfillmentOrderList($orderId: ID!) {
        order(id: $orderId) {
          fulfillmentOrders(first: 250) {
            nodes {
              id
              createdAt
              updatedAt
              requestStatus
              status
              fulfillAt
              destination {
                id
                address1
                address2
                city
                company
                countryCode
                email
                firstName
                lastName
                phone
                province
                zip
              }
              lineItems(first: 250) {
                nodes {
                  id
                  totalQuantity
                  inventoryItemId
                  remainingQuantity
                  variant {
                    id
                  }
                }
              }
              internationalDuties {
                incoterm
              }
              fulfillmentHolds {
                reason
                reasonNotes
              }
              fulfillBy
              deliveryMethod {
                id
                methodType
                minDeliveryDateTime
                maxDeliveryDateTime
                additionalInformation {
                  instructions
                  phone
                }
                serviceCode
                sourceReference
                presentedName
                brandedPromise {
                  handle
                  name
                }
              }
              assignedLocation {
                address1
                address2
                city
                countryCode
                location {
                  id
                }
                name
                phone
                province
                zip
              }
              merchantRequests(first: 250) {
                nodes {
                  message
                  requestOptions
                  kind
                }
              }
            }
          }
        }
      }`,
      "variables": {
          "orderId": "gid://shopify/Order/148977776"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query FulfillmentOrderList($orderId: ID!) {
    order(id: $orderId) {
      fulfillmentOrders(first: 250) {
        nodes {
          id
          createdAt
          updatedAt
          requestStatus
          status
          fulfillAt
          destination {
            id
            address1
            address2
            city
            company
            countryCode
            email
            firstName
            lastName
            phone
            province
            zip
          }
          lineItems(first: 250) {
            nodes {
              id
              totalQuantity
              inventoryItemId
              remainingQuantity
              variant {
                id
              }
            }
          }
          internationalDuties {
            incoterm
          }
          fulfillmentHolds {
            reason
            reasonNotes
          }
          fulfillBy
          deliveryMethod {
            id
            methodType
            minDeliveryDateTime
            maxDeliveryDateTime
            additionalInformation {
              instructions
              phone
            }
            serviceCode
            sourceReference
            presentedName
            brandedPromise {
              handle
              name
            }
          }
          assignedLocation {
            address1
            address2
            city
            countryCode
            location {
              id
            }
            name
            phone
            province
            zip
          }
          merchantRequests(first: 250) {
            nodes {
              message
              requestOptions
              kind
            }
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "orderId": "gid://shopify/Order/148977776"
  }'
  ```

  #### Response

  ```json
  {
    "order": {
      "fulfillmentOrders": {
        "nodes": [
          {
            "id": "gid://shopify/FulfillmentOrder/564786110",
            "createdAt": "2025-04-29T14:25:19Z",
            "updatedAt": "2025-04-29T14:25:19Z",
            "requestStatus": "UNSUBMITTED",
            "status": "OPEN",
            "fulfillAt": null,
            "destination": {
              "id": "gid://shopify/FulfillmentOrderDestination/402903185",
              "address1": "123 Amoebobacterieae St",
              "address2": "Unit 806",
              "city": "Ottawa",
              "company": "",
              "countryCode": "CA",
              "email": "bob@example.com",
              "firstName": "Bob",
              "lastName": "Bobsen",
              "phone": "(555)555-5555",
              "province": "Ontario",
              "zip": "K2P0V6"
            },
            "lineItems": {
              "nodes": [
                {
                  "id": "gid://shopify/FulfillmentOrderLineItem/445529754",
                  "totalQuantity": 1,
                  "inventoryItemId": "gid://shopify/InventoryItem/43729076",
                  "remainingQuantity": 1,
                  "variant": {
                    "id": "gid://shopify/ProductVariant/43729076"
                  }
                }
              ]
            },
            "internationalDuties": {
              "incoterm": "DAP"
            },
            "fulfillmentHolds": [],
            "fulfillBy": null,
            "deliveryMethod": {
              "id": "gid://shopify/DeliveryMethod/889454384",
              "methodType": "SHIPPING",
              "minDeliveryDateTime": null,
              "maxDeliveryDateTime": null,
              "additionalInformation": {
                "instructions": null,
                "phone": null
              },
              "serviceCode": null,
              "sourceReference": null,
              "presentedName": null,
              "brandedPromise": null
            },
            "assignedLocation": {
              "address1": "190 MacLaren Street",
              "address2": null,
              "city": "Ottawa",
              "countryCode": "CA",
              "location": {
                "id": "gid://shopify/Location/124656943"
              },
              "name": "Shipping Origin",
              "phone": null,
              "province": "Ontario",
              "zip": "K2P 0L6"
            },
            "merchantRequests": {
              "nodes": []
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieve a list of transactions

  #### Description

  This query retrieves the first 10 transactions for an \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order). The example uses the \`transactions\` field which returns a list of \[\`OrderTransaction\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderTransaction) objects with comprehensive data, including payment details, gateway information, and current status. The query also uses inline fragments to retrieve information about payment methods.

  #### Query

  ```graphql
  query TransactionsForOrder($orderId: ID!) {
    order(id: $orderId) {
      transactions(first: 10) {
        accountNumber
        amountSet {
          presentmentMoney {
            amount
            currencyCode
          }
          shopMoney {
            amount
            currencyCode
          }
        }
        authorizationCode
        authorizationExpiresAt
        createdAt
        errorCode
        fees {
          amount {
            amount
            currencyCode
          }
        }
        formattedGateway
        gateway
        id
        kind
        manuallyCapturable
        maximumRefundableV2 {
          amount
          currencyCode
        }
        multiCapturable
        order {
          id
        }
        parentTransaction {
          id
        }
        paymentDetails {
          ... on CardPaymentDetails {
            paymentMethodName
          }
          ... on ShopPayInstallmentsPaymentDetails {
            paymentMethodName
          }
        }
        paymentIcon {
          url
        }
        paymentId
        processedAt
        receiptJson
        settlementCurrency
        shopifyPaymentsSet {
          refundSet {
            acquirerReferenceNumber
          }
        }
        status
        test
        totalUnsettledSet {
          presentmentMoney {
            amount
            currencyCode
          }
          shopMoney {
            amount
            currencyCode
          }
        }
        user {
          id
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "orderId": "gid://shopify/Order/148977776"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query TransactionsForOrder($orderId: ID!) { order(id: $orderId) { transactions(first: 10) { accountNumber amountSet { presentmentMoney { amount currencyCode } shopMoney { amount currencyCode } } authorizationCode authorizationExpiresAt createdAt errorCode fees { amount { amount currencyCode } } formattedGateway gateway id kind manuallyCapturable maximumRefundableV2 { amount currencyCode } multiCapturable order { id } parentTransaction { id } paymentDetails { ... on CardPaymentDetails { paymentMethodName } ... on ShopPayInstallmentsPaymentDetails { paymentMethodName } } paymentIcon { url } paymentId processedAt receiptJson settlementCurrency shopifyPaymentsSet { refundSet { acquirerReferenceNumber } } status test totalUnsettledSet { presentmentMoney { amount currencyCode } shopMoney { amount currencyCode } } user { id } } } }",
   "variables": {
      "orderId": "gid://shopify/Order/148977776"
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
    query TransactionsForOrder($orderId: ID!) {
      order(id: $orderId) {
        transactions(first: 10) {
          accountNumber
          amountSet {
            presentmentMoney {
              amount
              currencyCode
            }
            shopMoney {
              amount
              currencyCode
            }
          }
          authorizationCode
          authorizationExpiresAt
          createdAt
          errorCode
          fees {
            amount {
              amount
              currencyCode
            }
          }
          formattedGateway
          gateway
          id
          kind
          manuallyCapturable
          maximumRefundableV2 {
            amount
            currencyCode
          }
          multiCapturable
          order {
            id
          }
          parentTransaction {
            id
          }
          paymentDetails {
            ... on CardPaymentDetails {
              paymentMethodName
            }
            ... on ShopPayInstallmentsPaymentDetails {
              paymentMethodName
            }
          }
          paymentIcon {
            url
          }
          paymentId
          processedAt
          receiptJson
          settlementCurrency
          shopifyPaymentsSet {
            refundSet {
              acquirerReferenceNumber
            }
          }
          status
          test
          totalUnsettledSet {
            presentmentMoney {
              amount
              currencyCode
            }
            shopMoney {
              amount
              currencyCode
            }
          }
          user {
            id
          }
        }
      }
    }`,
    {
      variables: {
          "orderId": "gid://shopify/Order/148977776"
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
    query TransactionsForOrder($orderId: ID!) {
      order(id: $orderId) {
        transactions(first: 10) {
          accountNumber
          amountSet {
            presentmentMoney {
              amount
              currencyCode
            }
            shopMoney {
              amount
              currencyCode
            }
          }
          authorizationCode
          authorizationExpiresAt
          createdAt
          errorCode
          fees {
            amount {
              amount
              currencyCode
            }
          }
          formattedGateway
          gateway
          id
          kind
          manuallyCapturable
          maximumRefundableV2 {
            amount
            currencyCode
          }
          multiCapturable
          order {
            id
          }
          parentTransaction {
            id
          }
          paymentDetails {
            ... on CardPaymentDetails {
              paymentMethodName
            }
            ... on ShopPayInstallmentsPaymentDetails {
              paymentMethodName
            }
          }
          paymentIcon {
            url
          }
          paymentId
          processedAt
          receiptJson
          settlementCurrency
          shopifyPaymentsSet {
            refundSet {
              acquirerReferenceNumber
            }
          }
          status
          test
          totalUnsettledSet {
            presentmentMoney {
              amount
              currencyCode
            }
            shopMoney {
              amount
              currencyCode
            }
          }
          user {
            id
          }
        }
      }
    }
  QUERY

  variables = {
    "orderId": "gid://shopify/Order/148977776"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query TransactionsForOrder($orderId: ID!) {
        order(id: $orderId) {
          transactions(first: 10) {
            accountNumber
            amountSet {
              presentmentMoney {
                amount
                currencyCode
              }
              shopMoney {
                amount
                currencyCode
              }
            }
            authorizationCode
            authorizationExpiresAt
            createdAt
            errorCode
            fees {
              amount {
                amount
                currencyCode
              }
            }
            formattedGateway
            gateway
            id
            kind
            manuallyCapturable
            maximumRefundableV2 {
              amount
              currencyCode
            }
            multiCapturable
            order {
              id
            }
            parentTransaction {
              id
            }
            paymentDetails {
              ... on CardPaymentDetails {
                paymentMethodName
              }
              ... on ShopPayInstallmentsPaymentDetails {
                paymentMethodName
              }
            }
            paymentIcon {
              url
            }
            paymentId
            processedAt
            receiptJson
            settlementCurrency
            shopifyPaymentsSet {
              refundSet {
                acquirerReferenceNumber
              }
            }
            status
            test
            totalUnsettledSet {
              presentmentMoney {
                amount
                currencyCode
              }
              shopMoney {
                amount
                currencyCode
              }
            }
            user {
              id
            }
          }
        }
      }`,
      "variables": {
          "orderId": "gid://shopify/Order/148977776"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query TransactionsForOrder($orderId: ID!) {
    order(id: $orderId) {
      transactions(first: 10) {
        accountNumber
        amountSet {
          presentmentMoney {
            amount
            currencyCode
          }
          shopMoney {
            amount
            currencyCode
          }
        }
        authorizationCode
        authorizationExpiresAt
        createdAt
        errorCode
        fees {
          amount {
            amount
            currencyCode
          }
        }
        formattedGateway
        gateway
        id
        kind
        manuallyCapturable
        maximumRefundableV2 {
          amount
          currencyCode
        }
        multiCapturable
        order {
          id
        }
        parentTransaction {
          id
        }
        paymentDetails {
          ... on CardPaymentDetails {
            paymentMethodName
          }
          ... on ShopPayInstallmentsPaymentDetails {
            paymentMethodName
          }
        }
        paymentIcon {
          url
        }
        paymentId
        processedAt
        receiptJson
        settlementCurrency
        shopifyPaymentsSet {
          refundSet {
            acquirerReferenceNumber
          }
        }
        status
        test
        totalUnsettledSet {
          presentmentMoney {
            amount
            currencyCode
          }
          shopMoney {
            amount
            currencyCode
          }
        }
        user {
          id
        }
      }
    }
  }' \
  --variables \
  '{
    "orderId": "gid://shopify/Order/148977776"
  }'
  ```

  #### Response

  ```json
  {
    "order": {
      "transactions": [
        {
          "accountNumber": "",
          "amountSet": {
            "presentmentMoney": {
              "amount": "11.5",
              "currencyCode": "USD"
            },
            "shopMoney": {
              "amount": "11.5",
              "currencyCode": "USD"
            }
          },
          "authorizationCode": "0",
          "authorizationExpiresAt": null,
          "createdAt": "2005-07-31T15:57:10Z",
          "errorCode": null,
          "fees": [],
          "formattedGateway": "(For Testing) Bogus Gateway",
          "gateway": "bogus",
          "id": "gid://shopify/OrderTransaction/42239183",
          "kind": "AUTHORIZATION",
          "manuallyCapturable": false,
          "maximumRefundableV2": null,
          "multiCapturable": true,
          "order": {
            "id": "gid://shopify/Order/148977776"
          },
          "parentTransaction": null,
          "paymentDetails": null,
          "paymentIcon": null,
          "paymentId": "c148977776.1",
          "processedAt": "2005-07-31T15:57:10Z",
          "receiptJson": "{\"testcase\":true,\"response_code\":3,\"response_reason_code\":\"16\",\"response_reason_text\":\"The transaction cannot be found.\",\"avs_result_code\":\"P\",\"transaction_id\":\"0\",\"card_code\":\"M\"}",
          "settlementCurrency": null,
          "shopifyPaymentsSet": null,
          "status": "FAILURE",
          "test": false,
          "totalUnsettledSet": {
            "presentmentMoney": {
              "amount": "0.0",
              "currencyCode": "USD"
            },
            "shopMoney": {
              "amount": "0.0",
              "currencyCode": "USD"
            }
          },
          "user": null
        },
        {
          "accountNumber": "",
          "amountSet": {
            "presentmentMoney": {
              "amount": "50.0",
              "currencyCode": "USD"
            },
            "shopMoney": {
              "amount": "50.0",
              "currencyCode": "USD"
            }
          },
          "authorizationCode": null,
          "authorizationExpiresAt": null,
          "createdAt": "2005-07-31T15:57:11Z",
          "errorCode": null,
          "fees": [],
          "formattedGateway": "(For Testing) Bogus Gateway",
          "gateway": "bogus",
          "id": "gid://shopify/OrderTransaction/607668304",
          "kind": "SALE",
          "manuallyCapturable": false,
          "maximumRefundableV2": null,
          "multiCapturable": true,
          "order": {
            "id": "gid://shopify/Order/148977776"
          },
          "parentTransaction": null,
          "paymentDetails": null,
          "paymentIcon": null,
          "paymentId": "c148977776.3",
          "processedAt": "2005-07-31T15:57:11Z",
          "receiptJson": "{\"testcase\":true}",
          "settlementCurrency": null,
          "shopifyPaymentsSet": null,
          "status": "AWAITING_RESPONSE",
          "test": false,
          "totalUnsettledSet": {
            "presentmentMoney": {
              "amount": "0.0",
              "currencyCode": "USD"
            },
            "shopMoney": {
              "amount": "0.0",
              "currencyCode": "USD"
            }
          },
          "user": null
        },
        {
          "accountNumber": "•••• •••• •••• 4242",
          "amountSet": {
            "presentmentMoney": {
              "amount": "11.5",
              "currencyCode": "USD"
            },
            "shopMoney": {
              "amount": "11.5",
              "currencyCode": "USD"
            }
          },
          "authorizationCode": "1001",
          "authorizationExpiresAt": null,
          "createdAt": "2005-07-31T15:57:10Z",
          "errorCode": null,
          "fees": [],
          "formattedGateway": "(For Testing) Bogus Gateway",
          "gateway": "bogus",
          "id": "gid://shopify/OrderTransaction/661056787",
          "kind": "AUTHORIZATION",
          "manuallyCapturable": false,
          "maximumRefundableV2": null,
          "multiCapturable": true,
          "order": {
            "id": "gid://shopify/Order/148977776"
          },
          "parentTransaction": null,
          "paymentDetails": {
            "paymentMethodName": "card"
          },
          "paymentIcon": {
            "url": "https://cdn.shopify.com/shopifycloud/shopify/assets/payment_icons/visa-319d545c6fd255c9aad5eeaad21fd6f7f7b4fdbdb1a35ce83b89cca12a187f00.svg.png"
          },
          "paymentId": "c148977776.1",
          "processedAt": "2005-07-31T15:57:10Z",
          "receiptJson": "{\"testcase\":true,\"response_code\":1,\"response_reason_code\":\"1\",\"response_reason_text\":\"This transaction has been approved.\",\"avs_result_code\":\"Y\",\"transaction_id\":\"123456789\",\"card_code\":\"M\"}",
          "settlementCurrency": null,
          "shopifyPaymentsSet": null,
          "status": "SUCCESS",
          "test": false,
          "totalUnsettledSet": {
            "presentmentMoney": {
              "amount": "0.0",
              "currencyCode": "USD"
            },
            "shopMoney": {
              "amount": "0.0",
              "currencyCode": "USD"
            }
          },
          "user": null
        },
        {
          "accountNumber": "•••• •••• •••• 4242",
          "amountSet": {
            "presentmentMoney": {
              "amount": "11.5",
              "currencyCode": "USD"
            },
            "shopMoney": {
              "amount": "11.5",
              "currencyCode": "USD"
            }
          },
          "authorizationCode": "1000",
          "authorizationExpiresAt": null,
          "createdAt": "2005-07-31T15:57:11Z",
          "errorCode": null,
          "fees": [],
          "formattedGateway": "(For Testing) Bogus Gateway",
          "gateway": "bogus",
          "id": "gid://shopify/OrderTransaction/999225631",
          "kind": "CAPTURE",
          "manuallyCapturable": false,
          "maximumRefundableV2": null,
          "multiCapturable": true,
          "order": {
            "id": "gid://shopify/Order/148977776"
          },
          "parentTransaction": {
            "id": "gid://shopify/OrderTransaction/661056787"
          },
          "paymentDetails": {
            "paymentMethodName": "card"
          },
          "paymentIcon": {
            "url": "https://cdn.shopify.com/shopifycloud/shopify/assets/payment_icons/visa-319d545c6fd255c9aad5eeaad21fd6f7f7b4fdbdb1a35ce83b89cca12a187f00.svg.png"
          },
          "paymentId": "c148977776.2",
          "processedAt": "2005-07-31T15:57:11Z",
          "receiptJson": "{\"testcase\":true}",
          "settlementCurrency": null,
          "shopifyPaymentsSet": null,
          "status": "SUCCESS",
          "test": false,
          "totalUnsettledSet": {
            "presentmentMoney": {
              "amount": "0.0",
              "currencyCode": "USD"
            },
            "shopMoney": {
              "amount": "0.0",
              "currencyCode": "USD"
            }
          },
          "user": null
        }
      ]
    }
  }
  ```

* ### Retrieve a metafield associated with an order

  #### Description

  Get the metafield value identified by \`my\_fields.purchase\_order\` on a specific order.

  #### Query

  ```graphql
  query OrderMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
    order(id: $ownerId) {
      purchaseOrder: metafield(namespace: $namespace, key: $key) {
        value
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "namespace": "my_fields",
    "key": "purchase_order",
    "ownerId": "gid://shopify/Order/148977776"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query OrderMetafield($namespace: String!, $key: String!, $ownerId: ID!) { order(id: $ownerId) { purchaseOrder: metafield(namespace: $namespace, key: $key) { value } } }",
   "variables": {
      "namespace": "my_fields",
      "key": "purchase_order",
      "ownerId": "gid://shopify/Order/148977776"
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
    query OrderMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
      order(id: $ownerId) {
        purchaseOrder: metafield(namespace: $namespace, key: $key) {
          value
        }
      }
    }`,
    {
      variables: {
          "namespace": "my_fields",
          "key": "purchase_order",
          "ownerId": "gid://shopify/Order/148977776"
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
    query OrderMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
      order(id: $ownerId) {
        purchaseOrder: metafield(namespace: $namespace, key: $key) {
          value
        }
      }
    }
  QUERY

  variables = {
    "namespace": "my_fields",
    "key": "purchase_order",
    "ownerId": "gid://shopify/Order/148977776"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query OrderMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
        order(id: $ownerId) {
          purchaseOrder: metafield(namespace: $namespace, key: $key) {
            value
          }
        }
      }`,
      "variables": {
          "namespace": "my_fields",
          "key": "purchase_order",
          "ownerId": "gid://shopify/Order/148977776"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query OrderMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
    order(id: $ownerId) {
      purchaseOrder: metafield(namespace: $namespace, key: $key) {
        value
      }
    }
  }' \
  --variables \
  '{
    "namespace": "my_fields",
    "key": "purchase_order",
    "ownerId": "gid://shopify/Order/148977776"
  }'
  ```

  #### Response

  ```json
  {
    "order": {
      "purchaseOrder": {
        "value": "123"
      }
    }
  }
  ```

* ### Retrieve a specific order

  #### Description

  This query retrieves a specific \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) by its ID. The example returns basic order information including the order's name, total amount, and a list of the first 10 line items, or individual products that are included in the customer's order.

  #### Query

  ```graphql
  query {
    order(id: "gid://shopify/Order/148977776") {
      id
      name
      totalPriceSet {
        presentmentMoney {
          amount
        }
      }
      lineItems(first: 10) {
        nodes {
          id
          name
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
  "query": "query { order(id: \"gid://shopify/Order/148977776\") { id name totalPriceSet { presentmentMoney { amount } } lineItems(first: 10) { nodes { id name } } } }"
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
      order(id: "gid://shopify/Order/148977776") {
        id
        name
        totalPriceSet {
          presentmentMoney {
            amount
          }
        }
        lineItems(first: 10) {
          nodes {
            id
            name
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
      order(id: "gid://shopify/Order/148977776") {
        id
        name
        totalPriceSet {
          presentmentMoney {
            amount
          }
        }
        lineItems(first: 10) {
          nodes {
            id
            name
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
      order(id: "gid://shopify/Order/148977776") {
        id
        name
        totalPriceSet {
          presentmentMoney {
            amount
          }
        }
        lineItems(first: 10) {
          nodes {
            id
            name
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
    order(id: "gid://shopify/Order/148977776") {
      id
      name
      totalPriceSet {
        presentmentMoney {
          amount
        }
      }
      lineItems(first: 10) {
        nodes {
          id
          name
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "order": {
      "id": "gid://shopify/Order/148977776",
      "name": "#1001",
      "totalPriceSet": {
        "presentmentMoney": {
          "amount": "11.5"
        }
      },
      "lineItems": {
        "nodes": [
          {
            "id": "gid://shopify/LineItem/510711879",
            "name": "Draft - 151cm"
          }
        ]
      }
    }
  }
  ```

* ### Retrieve an order using node and a fragment

  #### Description

  This query retrieves an \[\`order\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) by its \`id\` using the \`node\` field. It uses a GraphQL fragment, \`...on Order\`, to access the order's \`name\` when querying through the \[\`Node\`]\(https://shopify.dev/docs/api/admin-graphql/latest/interfaces/Node) interface.

  #### Query

  ```graphql
  query {
    node(id: "gid://shopify/Order/148977776") {
      id
      ... on Order {
        name
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
  "query": "query { node(id: \"gid://shopify/Order/148977776\") { id ... on Order { name } } }"
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
      node(id: "gid://shopify/Order/148977776") {
        id
        ... on Order {
          name
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
      node(id: "gid://shopify/Order/148977776") {
        id
        ... on Order {
          name
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
      node(id: "gid://shopify/Order/148977776") {
        id
        ... on Order {
          name
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
    node(id: "gid://shopify/Order/148977776") {
      id
      ... on Order {
        name
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "node": {
      "id": "gid://shopify/Order/148977776",
      "name": "#1001"
    }
  }
  ```

* ### Retrieve duties applied to an order

  #### Description

  This query retrieves duty information for an \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order). The example returns the total duty amount with \`currentTotalDutiesSet\` and the first 10 line items with their applied duties. Each line item includes a list of \[\`Duty\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Duty) objects containing harmonized system codes and amounts.

  #### Query

  ```graphql
  query {
    order(id: "gid://shopify/Order/469306983") {
      currentTotalDutiesSet {
        shopMoney {
          amount
        }
      }
      lineItems(first: 10) {
        edges {
          node {
            id
            name
            refundableQuantity
            duties {
              id
              harmonizedSystemCode
              price {
                shopMoney {
                  amount
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
  "query": "query { order(id: \"gid://shopify/Order/469306983\") { currentTotalDutiesSet { shopMoney { amount } } lineItems(first: 10) { edges { node { id name refundableQuantity duties { id harmonizedSystemCode price { shopMoney { amount } } } } } } } }"
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
      order(id: "gid://shopify/Order/469306983") {
        currentTotalDutiesSet {
          shopMoney {
            amount
          }
        }
        lineItems(first: 10) {
          edges {
            node {
              id
              name
              refundableQuantity
              duties {
                id
                harmonizedSystemCode
                price {
                  shopMoney {
                    amount
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
      order(id: "gid://shopify/Order/469306983") {
        currentTotalDutiesSet {
          shopMoney {
            amount
          }
        }
        lineItems(first: 10) {
          edges {
            node {
              id
              name
              refundableQuantity
              duties {
                id
                harmonizedSystemCode
                price {
                  shopMoney {
                    amount
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
      order(id: "gid://shopify/Order/469306983") {
        currentTotalDutiesSet {
          shopMoney {
            amount
          }
        }
        lineItems(first: 10) {
          edges {
            node {
              id
              name
              refundableQuantity
              duties {
                id
                harmonizedSystemCode
                price {
                  shopMoney {
                    amount
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
    order(id: "gid://shopify/Order/469306983") {
      currentTotalDutiesSet {
        shopMoney {
          amount
        }
      }
      lineItems(first: 10) {
        edges {
          node {
            id
            name
            refundableQuantity
            duties {
              id
              harmonizedSystemCode
              price {
                shopMoney {
                  amount
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
    "order": {
      "currentTotalDutiesSet": {
        "shopMoney": {
          "amount": "8.97"
        }
      },
      "lineItems": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/LineItem/983004162",
              "name": "Element - 151cm",
              "refundableQuantity": 1,
              "duties": [
                {
                  "id": "gid://shopify/Duty/1064114503",
                  "harmonizedSystemCode": "91051930",
                  "price": {
                    "shopMoney": {
                      "amount": "8.97"
                    }
                  }
                }
              ]
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieve fulfillments associated with an order

  #### Description

  This query retrieves the first 10 \[fulfillments]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Fulfillment) for an \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order). For each fulfillment, the example returns the first 10 \[\`FulfillmentLineItem\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentLineItem) objects with quantities and pricing information.

  #### Query

  ```graphql
  query FulfillmentList($orderId: ID!) {
    order(id: $orderId) {
      fulfillments(first: 10) {
        fulfillmentLineItems(first: 10) {
          edges {
            node {
              id
              lineItem {
                title
                variant {
                  id
                }
              }
              quantity
              originalTotalSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
        status
        estimatedDeliveryAt
        location {
          id
          legacyResourceId
        }
        service {
          handle
        }
        trackingInfo(first: 10) {
          company
          number
          url
        }
        originAddress {
          address1
          address2
          city
          countryCode
          provinceCode
          zip
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "orderId": "gid://shopify/Order/148977776"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query FulfillmentList($orderId: ID!) { order(id: $orderId) { fulfillments(first: 10) { fulfillmentLineItems(first: 10) { edges { node { id lineItem { title variant { id } } quantity originalTotalSet { shopMoney { amount currencyCode } } } } } status estimatedDeliveryAt location { id legacyResourceId } service { handle } trackingInfo(first: 10) { company number url } originAddress { address1 address2 city countryCode provinceCode zip } } } }",
   "variables": {
      "orderId": "gid://shopify/Order/148977776"
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
    query FulfillmentList($orderId: ID!) {
      order(id: $orderId) {
        fulfillments(first: 10) {
          fulfillmentLineItems(first: 10) {
            edges {
              node {
                id
                lineItem {
                  title
                  variant {
                    id
                  }
                }
                quantity
                originalTotalSet {
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
          status
          estimatedDeliveryAt
          location {
            id
            legacyResourceId
          }
          service {
            handle
          }
          trackingInfo(first: 10) {
            company
            number
            url
          }
          originAddress {
            address1
            address2
            city
            countryCode
            provinceCode
            zip
          }
        }
      }
    }`,
    {
      variables: {
          "orderId": "gid://shopify/Order/148977776"
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
    query FulfillmentList($orderId: ID!) {
      order(id: $orderId) {
        fulfillments(first: 10) {
          fulfillmentLineItems(first: 10) {
            edges {
              node {
                id
                lineItem {
                  title
                  variant {
                    id
                  }
                }
                quantity
                originalTotalSet {
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
          status
          estimatedDeliveryAt
          location {
            id
            legacyResourceId
          }
          service {
            handle
          }
          trackingInfo(first: 10) {
            company
            number
            url
          }
          originAddress {
            address1
            address2
            city
            countryCode
            provinceCode
            zip
          }
        }
      }
    }
  QUERY

  variables = {
    "orderId": "gid://shopify/Order/148977776"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query FulfillmentList($orderId: ID!) {
        order(id: $orderId) {
          fulfillments(first: 10) {
            fulfillmentLineItems(first: 10) {
              edges {
                node {
                  id
                  lineItem {
                    title
                    variant {
                      id
                    }
                  }
                  quantity
                  originalTotalSet {
                    shopMoney {
                      amount
                      currencyCode
                    }
                  }
                }
              }
            }
            status
            estimatedDeliveryAt
            location {
              id
              legacyResourceId
            }
            service {
              handle
            }
            trackingInfo(first: 10) {
              company
              number
              url
            }
            originAddress {
              address1
              address2
              city
              countryCode
              provinceCode
              zip
            }
          }
        }
      }`,
      "variables": {
          "orderId": "gid://shopify/Order/148977776"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query FulfillmentList($orderId: ID!) {
    order(id: $orderId) {
      fulfillments(first: 10) {
        fulfillmentLineItems(first: 10) {
          edges {
            node {
              id
              lineItem {
                title
                variant {
                  id
                }
              }
              quantity
              originalTotalSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
        status
        estimatedDeliveryAt
        location {
          id
          legacyResourceId
        }
        service {
          handle
        }
        trackingInfo(first: 10) {
          company
          number
          url
        }
        originAddress {
          address1
          address2
          city
          countryCode
          provinceCode
          zip
        }
      }
    }
  }' \
  --variables \
  '{
    "orderId": "gid://shopify/Order/148977776"
  }'
  ```

  #### Response

  ```json
  {
    "order": {
      "fulfillments": []
    }
  }
  ```

* ### Retrieve multiple orders using GraphQL aliases

  #### Description

  This query retrieves two \[orders]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) in a single request using their ID. The example uses \[GraphQL aliases]\(https://shopify.dev/docs/api/usage/graphql-queries#aliases), \`order1:\` and \`order2:\`, to request the same field multiple times without naming conflicts.

  #### Query

  ```graphql
  query {
    order1: order(id: "gid://shopify/Order/148977776") {
      id
      name
      createdAt
      displayFinancialStatus
      displayFulfillmentStatus
      totalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      customer {
        firstName
        lastName
      }
    }
    order2: order(id: "gid://shopify/Order/1073459961") {
      id
      name
      createdAt
      displayFinancialStatus
      displayFulfillmentStatus
      totalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      customer {
        firstName
        lastName
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
  "query": "query { order1: order(id: \"gid://shopify/Order/148977776\") { id name createdAt displayFinancialStatus displayFulfillmentStatus totalPriceSet { shopMoney { amount currencyCode } } customer { firstName lastName } } order2: order(id: \"gid://shopify/Order/1073459961\") { id name createdAt displayFinancialStatus displayFulfillmentStatus totalPriceSet { shopMoney { amount currencyCode } } customer { firstName lastName } } }"
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
      order1: order(id: "gid://shopify/Order/148977776") {
        id
        name
        createdAt
        displayFinancialStatus
        displayFulfillmentStatus
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        customer {
          firstName
          lastName
        }
      }
      order2: order(id: "gid://shopify/Order/1073459961") {
        id
        name
        createdAt
        displayFinancialStatus
        displayFulfillmentStatus
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        customer {
          firstName
          lastName
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
      order1: order(id: "gid://shopify/Order/148977776") {
        id
        name
        createdAt
        displayFinancialStatus
        displayFulfillmentStatus
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        customer {
          firstName
          lastName
        }
      }
      order2: order(id: "gid://shopify/Order/1073459961") {
        id
        name
        createdAt
        displayFinancialStatus
        displayFulfillmentStatus
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        customer {
          firstName
          lastName
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
      order1: order(id: "gid://shopify/Order/148977776") {
        id
        name
        createdAt
        displayFinancialStatus
        displayFulfillmentStatus
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        customer {
          firstName
          lastName
        }
      }
      order2: order(id: "gid://shopify/Order/1073459961") {
        id
        name
        createdAt
        displayFinancialStatus
        displayFulfillmentStatus
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        customer {
          firstName
          lastName
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
    order1: order(id: "gid://shopify/Order/148977776") {
      id
      name
      createdAt
      displayFinancialStatus
      displayFulfillmentStatus
      totalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      customer {
        firstName
        lastName
      }
    }
    order2: order(id: "gid://shopify/Order/1073459961") {
      id
      name
      createdAt
      displayFinancialStatus
      displayFulfillmentStatus
      totalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      customer {
        firstName
        lastName
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "order1": {
      "id": "gid://shopify/Order/148977776",
      "name": "#1001",
      "createdAt": "2005-07-31T15:57:11Z",
      "displayFinancialStatus": "PAID",
      "displayFulfillmentStatus": "UNFULFILLED",
      "totalPriceSet": {
        "shopMoney": {
          "amount": "11.5",
          "currencyCode": "USD"
        }
      },
      "customer": {
        "firstName": "Bob",
        "lastName": "Bobsen"
      }
    },
    "order2": {
      "id": "gid://shopify/Order/1073459961",
      "name": "#1018",
      "createdAt": "2008-07-31T15:57:11Z",
      "displayFinancialStatus": "PAID",
      "displayFulfillmentStatus": "UNFULFILLED",
      "totalPriceSet": {
        "shopMoney": {
          "amount": "11.5",
          "currencyCode": "USD"
        }
      },
      "customer": null
    }
  }
  ```

* ### Retrieve order risk assessments

  #### Description

  This query retrieves fraud risk information for an \`order\`. It uses the \`risk\` field, which returns an \[OrderRiskSummary]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderRiskSummary) object containing a list of \`assessments\` and a \[\`recommendation\`]\(https://shopify.dev/docs/api/admin-graphql/latest/enums/OrderRiskRecommendationResult).

  #### Query

  ```graphql
  query OrderRiskAssessmentsList($orderId: ID!) {
    order(id: $orderId) {
      risk {
        assessments {
          riskLevel
          provider {
            title
          }
          facts {
            description
            sentiment
          }
        }
        recommendation
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "orderId": "gid://shopify/Order/647667644"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query OrderRiskAssessmentsList($orderId: ID!) { order(id: $orderId) { risk { assessments { riskLevel provider { title } facts { description sentiment } } recommendation } } }",
   "variables": {
      "orderId": "gid://shopify/Order/647667644"
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
    query OrderRiskAssessmentsList($orderId: ID!) {
      order(id: $orderId) {
        risk {
          assessments {
            riskLevel
            provider {
              title
            }
            facts {
              description
              sentiment
            }
          }
          recommendation
        }
      }
    }`,
    {
      variables: {
          "orderId": "gid://shopify/Order/647667644"
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
    query OrderRiskAssessmentsList($orderId: ID!) {
      order(id: $orderId) {
        risk {
          assessments {
            riskLevel
            provider {
              title
            }
            facts {
              description
              sentiment
            }
          }
          recommendation
        }
      }
    }
  QUERY

  variables = {
    "orderId": "gid://shopify/Order/647667644"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query OrderRiskAssessmentsList($orderId: ID!) {
        order(id: $orderId) {
          risk {
            assessments {
              riskLevel
              provider {
                title
              }
              facts {
                description
                sentiment
              }
            }
            recommendation
          }
        }
      }`,
      "variables": {
          "orderId": "gid://shopify/Order/647667644"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query OrderRiskAssessmentsList($orderId: ID!) {
    order(id: $orderId) {
      risk {
        assessments {
          riskLevel
          provider {
            title
          }
          facts {
            description
            sentiment
          }
        }
        recommendation
      }
    }
  }' \
  --variables \
  '{
    "orderId": "gid://shopify/Order/647667644"
  }'
  ```

  #### Response

  ```json
  {
    "order": {
      "risk": {
        "assessments": [
          {
            "riskLevel": "HIGH",
            "provider": null,
            "facts": [
              {
                "description": "The order is high risk.",
                "sentiment": "NEGATIVE"
              }
            ]
          },
          {
            "riskLevel": "MEDIUM",
            "provider": {
              "title": "Private Mobile App for Channel"
            },
            "facts": []
          }
        ],
        "recommendation": "NONE"
      }
    }
  }
  ```

* ### Retrieve pinned metafield definitions associated with an order

  #### Description

  This query retrieves the first 10 \[pinned metafield definitions]\(https://help.shopify.com/en/manual/custom-data/metafields/pinning-metafield-definitions) for an order.It shows each definition's name, namespace, key, and data type, ordered by pinned position.

  #### Query

  ```graphql
  query OrderMetafieldDefinitions($ownerId: ID!, $first: Int, $pinnedStatus: MetafieldDefinitionPinnedStatus, $sortKey: MetafieldDefinitionSortKeys) {
    order(id: $ownerId) {
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
    "ownerId": "gid://shopify/Order/148977776",
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
  "query": "query OrderMetafieldDefinitions($ownerId: ID!, $first: Int, $pinnedStatus: MetafieldDefinitionPinnedStatus, $sortKey: MetafieldDefinitionSortKeys) { order(id: $ownerId) { metafieldDefinitions(first: $first, pinnedStatus: $pinnedStatus, sortKey: $sortKey) { edges { node { name namespace key type { name } } } } } }",
   "variables": {
      "pinnedStatus": "PINNED",
      "ownerId": "gid://shopify/Order/148977776",
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
    query OrderMetafieldDefinitions($ownerId: ID!, $first: Int, $pinnedStatus: MetafieldDefinitionPinnedStatus, $sortKey: MetafieldDefinitionSortKeys) {
      order(id: $ownerId) {
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
          "ownerId": "gid://shopify/Order/148977776",
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
    query OrderMetafieldDefinitions($ownerId: ID!, $first: Int, $pinnedStatus: MetafieldDefinitionPinnedStatus, $sortKey: MetafieldDefinitionSortKeys) {
      order(id: $ownerId) {
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
    "ownerId": "gid://shopify/Order/148977776",
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
      "query": `query OrderMetafieldDefinitions($ownerId: ID!, $first: Int, $pinnedStatus: MetafieldDefinitionPinnedStatus, $sortKey: MetafieldDefinitionSortKeys) {
        order(id: $ownerId) {
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
          "ownerId": "gid://shopify/Order/148977776",
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
  'query OrderMetafieldDefinitions($ownerId: ID!, $first: Int, $pinnedStatus: MetafieldDefinitionPinnedStatus, $sortKey: MetafieldDefinitionSortKeys) {
    order(id: $ownerId) {
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
    "ownerId": "gid://shopify/Order/148977776",
    "first": 10,
    "sortKey": "PINNED_POSITION"
  }'
  ```

  #### Response

  ```json
  {
    "order": {
      "metafieldDefinitions": {
        "edges": [
          {
            "node": {
              "name": "Delivery Instructions",
              "namespace": "my_fields",
              "key": "delivery_instructions",
              "type": {
                "name": "single_line_text_field"
              }
            }
          },
          {
            "node": {
              "name": "Purchase Order",
              "namespace": "my_fields",
              "key": "purchase_order",
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

* ### Retrieve shipping lines for an order

  #### Description

  This query retrieves the first 10 shipping lines for an \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order), including lines removed during order edits. The example uses \`includeRemovals: true\` on the \[\`shippingLines\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order#field-shippingLines) object to return both active and removed shipping lines. The \`isRemoved\` field indicates which lines were removed.

  #### Query

  ```graphql
  query shippingLinesByOrder($id: ID!) {
    order(id: $id) {
      shippingLines(first: 10, includeRemovals: true) {
        edges {
          node {
            id
            title
            isRemoved
          }
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/Order/816964372"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query shippingLinesByOrder($id: ID!) { order(id: $id) { shippingLines(first: 10, includeRemovals: true) { edges { node { id title isRemoved } } } } }",
   "variables": {
      "id": "gid://shopify/Order/816964372"
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
    query shippingLinesByOrder($id: ID!) {
      order(id: $id) {
        shippingLines(first: 10, includeRemovals: true) {
          edges {
            node {
              id
              title
              isRemoved
            }
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Order/816964372"
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
    query shippingLinesByOrder($id: ID!) {
      order(id: $id) {
        shippingLines(first: 10, includeRemovals: true) {
          edges {
            node {
              id
              title
              isRemoved
            }
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Order/816964372"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query shippingLinesByOrder($id: ID!) {
        order(id: $id) {
          shippingLines(first: 10, includeRemovals: true) {
            edges {
              node {
                id
                title
                isRemoved
              }
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Order/816964372"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query shippingLinesByOrder($id: ID!) {
    order(id: $id) {
      shippingLines(first: 10, includeRemovals: true) {
        edges {
          node {
            id
            title
            isRemoved
          }
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Order/816964372"
  }'
  ```

  #### Response

  ```json
  {
    "order": {
      "shippingLines": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/ShippingLine/816964372",
              "title": "Ground Service",
              "isRemoved": true
            }
          },
          {
            "node": {
              "id": "gid://shopify/ShippingLine/1072814005",
              "title": "Some shipping charge",
              "isRemoved": false
            }
          }
        ]
      }
    }
  }
  ```

* ### Retrieve tax information for an order

  #### Description

  This query retrieves comprehensive tax information for an \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order), including settings, totals, and line-specific details. The example uses nested \`taxLines\` available on \[\`LineItem\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/LineItem) and \[\`ShippingLine\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/ShippingLine) objects to display the applied taxes.

  #### Query

  ```graphql
  query {
    order(id: "gid://shopify/Order/53613399") {
      id
      createdAt
      currencyCode
      currentSubtotalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      currentTotalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      currentTotalTaxSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      name
      subtotalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      taxExempt
      taxLines {
        rate
        title
        priceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
      }
      taxesIncluded
      subtotalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      totalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      totalShippingPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      totalTaxSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      updatedAt
      lineItems(first: 250) {
        nodes {
          unfulfilledQuantity
          fulfillmentService {
            serviceName
          }
          fulfillmentStatus
          variant {
            id
            title
          }
          id
          originalUnitPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          quantity
          requiresShipping
          sku
          title
          name
          vendor
          customAttributes {
            key
            value
          }
          taxable
          taxLines {
            rate
            title
            channelLiable
            priceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
          }
        }
      }
      shippingAddress {
        address1
        address2
        city
        country
        phone
        province
        zip
        provinceCode
        countryCodeV2
      }
      shippingLines(first: 50) {
        nodes {
          code
          originalPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          taxLines {
            rate
            title
            priceSet {
              shopMoney {
                amount
                currencyCode
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
  "query": "query { order(id: \"gid://shopify/Order/53613399\") { id createdAt currencyCode currentSubtotalPriceSet { shopMoney { amount currencyCode } } currentTotalPriceSet { shopMoney { amount currencyCode } } currentTotalTaxSet { shopMoney { amount currencyCode } } name subtotalPriceSet { shopMoney { amount currencyCode } } taxExempt taxLines { rate title priceSet { shopMoney { amount currencyCode } } } taxesIncluded subtotalPriceSet { shopMoney { amount currencyCode } } totalPriceSet { shopMoney { amount currencyCode } } totalShippingPriceSet { shopMoney { amount currencyCode } } totalTaxSet { shopMoney { amount currencyCode } } updatedAt lineItems(first: 250) { nodes { unfulfilledQuantity fulfillmentService { serviceName } fulfillmentStatus variant { id title } id originalUnitPriceSet { shopMoney { amount currencyCode } } quantity requiresShipping sku title name vendor customAttributes { key value } taxable taxLines { rate title channelLiable priceSet { shopMoney { amount currencyCode } } } } } shippingAddress { address1 address2 city country phone province zip provinceCode countryCodeV2 } shippingLines(first: 50) { nodes { code originalPriceSet { shopMoney { amount currencyCode } } taxLines { rate title priceSet { shopMoney { amount currencyCode } } } } } } }"
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
      order(id: "gid://shopify/Order/53613399") {
        id
        createdAt
        currencyCode
        currentSubtotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        currentTotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        currentTotalTaxSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        name
        subtotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        taxExempt
        taxLines {
          rate
          title
          priceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
        }
        taxesIncluded
        subtotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        totalShippingPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        totalTaxSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        updatedAt
        lineItems(first: 250) {
          nodes {
            unfulfilledQuantity
            fulfillmentService {
              serviceName
            }
            fulfillmentStatus
            variant {
              id
              title
            }
            id
            originalUnitPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            quantity
            requiresShipping
            sku
            title
            name
            vendor
            customAttributes {
              key
              value
            }
            taxable
            taxLines {
              rate
              title
              channelLiable
              priceSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
        shippingAddress {
          address1
          address2
          city
          country
          phone
          province
          zip
          provinceCode
          countryCodeV2
        }
        shippingLines(first: 50) {
          nodes {
            code
            originalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            taxLines {
              rate
              title
              priceSet {
                shopMoney {
                  amount
                  currencyCode
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
      order(id: "gid://shopify/Order/53613399") {
        id
        createdAt
        currencyCode
        currentSubtotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        currentTotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        currentTotalTaxSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        name
        subtotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        taxExempt
        taxLines {
          rate
          title
          priceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
        }
        taxesIncluded
        subtotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        totalShippingPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        totalTaxSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        updatedAt
        lineItems(first: 250) {
          nodes {
            unfulfilledQuantity
            fulfillmentService {
              serviceName
            }
            fulfillmentStatus
            variant {
              id
              title
            }
            id
            originalUnitPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            quantity
            requiresShipping
            sku
            title
            name
            vendor
            customAttributes {
              key
              value
            }
            taxable
            taxLines {
              rate
              title
              channelLiable
              priceSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
        shippingAddress {
          address1
          address2
          city
          country
          phone
          province
          zip
          provinceCode
          countryCodeV2
        }
        shippingLines(first: 50) {
          nodes {
            code
            originalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            taxLines {
              rate
              title
              priceSet {
                shopMoney {
                  amount
                  currencyCode
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
      order(id: "gid://shopify/Order/53613399") {
        id
        createdAt
        currencyCode
        currentSubtotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        currentTotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        currentTotalTaxSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        name
        subtotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        taxExempt
        taxLines {
          rate
          title
          priceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
        }
        taxesIncluded
        subtotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        totalShippingPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        totalTaxSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        updatedAt
        lineItems(first: 250) {
          nodes {
            unfulfilledQuantity
            fulfillmentService {
              serviceName
            }
            fulfillmentStatus
            variant {
              id
              title
            }
            id
            originalUnitPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            quantity
            requiresShipping
            sku
            title
            name
            vendor
            customAttributes {
              key
              value
            }
            taxable
            taxLines {
              rate
              title
              channelLiable
              priceSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
        shippingAddress {
          address1
          address2
          city
          country
          phone
          province
          zip
          provinceCode
          countryCodeV2
        }
        shippingLines(first: 50) {
          nodes {
            code
            originalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            taxLines {
              rate
              title
              priceSet {
                shopMoney {
                  amount
                  currencyCode
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
    order(id: "gid://shopify/Order/53613399") {
      id
      createdAt
      currencyCode
      currentSubtotalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      currentTotalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      currentTotalTaxSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      name
      subtotalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      taxExempt
      taxLines {
        rate
        title
        priceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
      }
      taxesIncluded
      subtotalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      totalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      totalShippingPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      totalTaxSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      updatedAt
      lineItems(first: 250) {
        nodes {
          unfulfilledQuantity
          fulfillmentService {
            serviceName
          }
          fulfillmentStatus
          variant {
            id
            title
          }
          id
          originalUnitPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          quantity
          requiresShipping
          sku
          title
          name
          vendor
          customAttributes {
            key
            value
          }
          taxable
          taxLines {
            rate
            title
            channelLiable
            priceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
          }
        }
      }
      shippingAddress {
        address1
        address2
        city
        country
        phone
        province
        zip
        provinceCode
        countryCodeV2
      }
      shippingLines(first: 50) {
        nodes {
          code
          originalPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          taxLines {
            rate
            title
            priceSet {
              shopMoney {
                amount
                currencyCode
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
    "order": {
      "id": "gid://shopify/Order/53613399",
      "createdAt": "2025-04-08T14:52:51Z",
      "currencyCode": "USD",
      "currentSubtotalPriceSet": {
        "shopMoney": {
          "amount": "1.0",
          "currencyCode": "USD"
        }
      },
      "currentTotalPriceSet": {
        "shopMoney": {
          "amount": "11.0",
          "currencyCode": "USD"
        }
      },
      "currentTotalTaxSet": {
        "shopMoney": {
          "amount": "0.0",
          "currencyCode": "USD"
        }
      },
      "name": "#9563",
      "subtotalPriceSet": {
        "shopMoney": {
          "amount": "15.0",
          "currencyCode": "USD"
        }
      },
      "taxExempt": false,
      "taxLines": [
        {
          "rate": 0.06,
          "title": "GST",
          "priceSet": {
            "shopMoney": {
              "amount": "0.6",
              "currencyCode": "USD"
            }
          }
        }
      ],
      "taxesIncluded": false,
      "totalPriceSet": {
        "shopMoney": {
          "amount": "16.2",
          "currencyCode": "USD"
        }
      },
      "totalShippingPriceSet": {
        "shopMoney": {
          "amount": "10.0",
          "currencyCode": "USD"
        }
      },
      "totalTaxSet": {
        "shopMoney": {
          "amount": "1.2",
          "currencyCode": "USD"
        }
      },
      "updatedAt": "2025-04-08T14:52:51Z",
      "lineItems": {
        "nodes": [
          {
            "unfulfilledQuantity": 1,
            "fulfillmentService": {
              "serviceName": "Manual"
            },
            "fulfillmentStatus": "fulfilled",
            "variant": null,
            "id": "gid://shopify/LineItem/1035841997",
            "originalUnitPriceSet": {
              "shopMoney": {
                "amount": "1.0",
                "currencyCode": "USD"
              }
            },
            "quantity": 1,
            "requiresShipping": true,
            "sku": null,
            "title": "POS sale",
            "name": "POS sale",
            "vendor": null,
            "customAttributes": [],
            "taxable": true,
            "taxLines": []
          }
        ]
      },
      "shippingAddress": {
        "address1": "511 Foothill Road",
        "address2": "",
        "city": "Bevery Hills",
        "country": "United States",
        "phone": "+1(613)555-1212",
        "province": "California",
        "zip": "90210",
        "provinceCode": "CA",
        "countryCodeV2": "US"
      },
      "shippingLines": {
        "nodes": [
          {
            "code": "Local Delivery",
            "originalPriceSet": {
              "shopMoney": {
                "amount": "10.0",
                "currencyCode": "USD"
              }
            },
            "taxLines": [
              {
                "rate": 0.06,
                "title": "GST",
                "priceSet": {
                  "shopMoney": {
                    "amount": "0.6",
                    "currencyCode": "USD"
                  }
                }
              }
            ]
          }
        ]
      }
    }
  }
  ```

* ### Retrieve the first 10 sales agreements for a modified order

  #### Description

  This query retrieves the first 10 \[sales agreements]\(https://shopify.dev/docs/api/admin-graphql/latest/interfaces/SalesAgreement) for a modified \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order). This example retrieves sale records with negative quantities, indicating items that were removed during edits. This allows you to monitor both the original purchases and any subsequent modifications.

  #### Query

  ```graphql
  query {
    order(id: "gid://shopify/Order/116757651") {
      agreements(first: 10) {
        edges {
          node {
            id
            happenedAt
            sales(first: 10) {
              edges {
                node {
                  actionType
                  lineType
                  quantity
                  totalAmount {
                    shopMoney {
                      amount
                    }
                  }
                  ... on ProductSale {
                    lineItem {
                      id
                      name
                    }
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
  "query": "query { order(id: \"gid://shopify/Order/116757651\") { agreements(first: 10) { edges { node { id happenedAt sales(first: 10) { edges { node { actionType lineType quantity totalAmount { shopMoney { amount } } ... on ProductSale { lineItem { id name } } } } } } } } } }"
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
      order(id: "gid://shopify/Order/116757651") {
        agreements(first: 10) {
          edges {
            node {
              id
              happenedAt
              sales(first: 10) {
                edges {
                  node {
                    actionType
                    lineType
                    quantity
                    totalAmount {
                      shopMoney {
                        amount
                      }
                    }
                    ... on ProductSale {
                      lineItem {
                        id
                        name
                      }
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
      order(id: "gid://shopify/Order/116757651") {
        agreements(first: 10) {
          edges {
            node {
              id
              happenedAt
              sales(first: 10) {
                edges {
                  node {
                    actionType
                    lineType
                    quantity
                    totalAmount {
                      shopMoney {
                        amount
                      }
                    }
                    ... on ProductSale {
                      lineItem {
                        id
                        name
                      }
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
      order(id: "gid://shopify/Order/116757651") {
        agreements(first: 10) {
          edges {
            node {
              id
              happenedAt
              sales(first: 10) {
                edges {
                  node {
                    actionType
                    lineType
                    quantity
                    totalAmount {
                      shopMoney {
                        amount
                      }
                    }
                    ... on ProductSale {
                      lineItem {
                        id
                        name
                      }
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
    order(id: "gid://shopify/Order/116757651") {
      agreements(first: 10) {
        edges {
          node {
            id
            happenedAt
            sales(first: 10) {
              edges {
                node {
                  actionType
                  lineType
                  quantity
                  totalAmount {
                    shopMoney {
                      amount
                    }
                  }
                  ... on ProductSale {
                    lineItem {
                      id
                      name
                    }
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
    "order": {
      "agreements": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/SalesAgreement/621397082",
              "happenedAt": "2019-04-15T15:57:11Z",
              "sales": {
                "edges": [
                  {
                    "node": {
                      "actionType": "ORDER",
                      "lineType": "PRODUCT",
                      "quantity": 3,
                      "totalAmount": {
                        "shopMoney": {
                          "amount": "31.05"
                        }
                      },
                      "lineItem": {
                        "id": "gid://shopify/LineItem/114976433",
                        "name": "Wall Climber - 158cm"
                      }
                    }
                  },
                  {
                    "node": {
                      "actionType": "ORDER",
                      "lineType": "PRODUCT",
                      "quantity": 2,
                      "totalAmount": {
                        "shopMoney": {
                          "amount": "20.7"
                        }
                      },
                      "lineItem": {
                        "id": "gid://shopify/LineItem/763128379",
                        "name": "Hill Zipper - 151cm"
                      }
                    }
                  },
                  {
                    "node": {
                      "actionType": "ORDER",
                      "lineType": "SHIPPING",
                      "quantity": null,
                      "totalAmount": {
                        "shopMoney": {
                          "amount": "5.0"
                        }
                      }
                    }
                  }
                ]
              }
            }
          },
          {
            "node": {
              "id": "gid://shopify/SalesAgreement/731429684",
              "happenedAt": "2019-04-16T11:52:10Z",
              "sales": {
                "edges": [
                  {
                    "node": {
                      "actionType": "ORDER",
                      "lineType": "PRODUCT",
                      "quantity": 2,
                      "totalAmount": {
                        "shopMoney": {
                          "amount": "38.28"
                        }
                      },
                      "lineItem": {
                        "id": "gid://shopify/LineItem/1001351938",
                        "name": "Custom Zebra"
                      }
                    }
                  },
                  {
                    "node": {
                      "actionType": "RETURN",
                      "lineType": "PRODUCT",
                      "quantity": -2,
                      "totalAmount": {
                        "shopMoney": {
                          "amount": "-20.7"
                        }
                      },
                      "lineItem": {
                        "id": "gid://shopify/LineItem/114976433",
                        "name": "Wall Climber - 158cm"
                      }
                    }
                  },
                  {
                    "node": {
                      "actionType": "ORDER",
                      "lineType": "PRODUCT",
                      "quantity": 2,
                      "totalAmount": {
                        "shopMoney": {
                          "amount": "20.7"
                        }
                      },
                      "lineItem": {
                        "id": "gid://shopify/LineItem/763128379",
                        "name": "Hill Zipper - 151cm"
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

* ### Retrieve the first 10 sales agreements for an order

  #### Description

  This query retrieves the first 10 \[sales agreements]\(https://shopify.dev/docs/api/admin-graphql/latest/interfaces/SalesAgreement) for an \[order]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/Order). The example uses inline fragments, \`...on ProductSale\` and \`...on ShippingLineSale\`, to return type-specific fields for product purchases and shipping charges.

  #### Query

  ```graphql
  query {
    order(id: "gid://shopify/Order/816964372") {
      agreements(first: 10) {
        edges {
          node {
            id
            happenedAt
            sales(first: 10) {
              edges {
                node {
                  actionType
                  lineType
                  quantity
                  totalAmount {
                    shopMoney {
                      amount
                    }
                  }
                  ... on ProductSale {
                    lineItem {
                      id
                      name
                    }
                  }
                  ... on ShippingLineSale {
                    shippingLine {
                      id
                    }
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
  "query": "query { order(id: \"gid://shopify/Order/816964372\") { agreements(first: 10) { edges { node { id happenedAt sales(first: 10) { edges { node { actionType lineType quantity totalAmount { shopMoney { amount } } ... on ProductSale { lineItem { id name } } ... on ShippingLineSale { shippingLine { id } } } } } } } } } }"
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
      order(id: "gid://shopify/Order/816964372") {
        agreements(first: 10) {
          edges {
            node {
              id
              happenedAt
              sales(first: 10) {
                edges {
                  node {
                    actionType
                    lineType
                    quantity
                    totalAmount {
                      shopMoney {
                        amount
                      }
                    }
                    ... on ProductSale {
                      lineItem {
                        id
                        name
                      }
                    }
                    ... on ShippingLineSale {
                      shippingLine {
                        id
                      }
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
      order(id: "gid://shopify/Order/816964372") {
        agreements(first: 10) {
          edges {
            node {
              id
              happenedAt
              sales(first: 10) {
                edges {
                  node {
                    actionType
                    lineType
                    quantity
                    totalAmount {
                      shopMoney {
                        amount
                      }
                    }
                    ... on ProductSale {
                      lineItem {
                        id
                        name
                      }
                    }
                    ... on ShippingLineSale {
                      shippingLine {
                        id
                      }
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
      order(id: "gid://shopify/Order/816964372") {
        agreements(first: 10) {
          edges {
            node {
              id
              happenedAt
              sales(first: 10) {
                edges {
                  node {
                    actionType
                    lineType
                    quantity
                    totalAmount {
                      shopMoney {
                        amount
                      }
                    }
                    ... on ProductSale {
                      lineItem {
                        id
                        name
                      }
                    }
                    ... on ShippingLineSale {
                      shippingLine {
                        id
                      }
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
    order(id: "gid://shopify/Order/816964372") {
      agreements(first: 10) {
        edges {
          node {
            id
            happenedAt
            sales(first: 10) {
              edges {
                node {
                  actionType
                  lineType
                  quantity
                  totalAmount {
                    shopMoney {
                      amount
                    }
                  }
                  ... on ProductSale {
                    lineItem {
                      id
                      name
                    }
                  }
                  ... on ShippingLineSale {
                    shippingLine {
                      id
                    }
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
    "order": {
      "agreements": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/SalesAgreement/466882664",
              "happenedAt": "2005-07-31T15:57:11Z",
              "sales": {
                "edges": [
                  {
                    "node": {
                      "actionType": "ORDER",
                      "lineType": "SHIPPING",
                      "quantity": null,
                      "totalAmount": {
                        "shopMoney": {
                          "amount": "5.0"
                        }
                      },
                      "shippingLine": {
                        "id": "gid://shopify/ShippingLine/816964372"
                      }
                    }
                  },
                  {
                    "node": {
                      "actionType": "ORDER",
                      "lineType": "PRODUCT",
                      "quantity": 3,
                      "totalAmount": {
                        "shopMoney": {
                          "amount": "30.0"
                        }
                      },
                      "lineItem": {
                        "id": "gid://shopify/LineItem/406313524",
                        "name": "Draft - 151cm"
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
