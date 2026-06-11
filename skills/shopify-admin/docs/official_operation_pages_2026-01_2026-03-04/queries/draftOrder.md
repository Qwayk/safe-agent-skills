---
title: draftOrder - GraphQL Admin
description: >-
  Retrieves a [draft
  order](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder)
  by its ID.

  A draft order is an order created by a merchant on behalf of their

  customers. Draft orders contain all necessary order details (products,
  pricing, customer information)

  but require payment to be accepted before they can be converted into

  [completed
  orders](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderComplete).


  Use the `draftOrder` query to retrieve information associated with the
  following workflows:


  - Creating orders for phone, in-person, or chat sales

  - Sending invoices to customers with secure checkout links

  - Managing custom items and additional costs

  - Selling products at discount or wholesale rates

  - Processing pre-orders and saving drafts for later completion


  A draft order is associated with a

  [customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

  and contains multiple [line
  items](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrderLineItem).

  Each draft order has a
  [status](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder#field-DraftOrder.fields.status),

  which indicates its progress through the sales workflow.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/draftOrder'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/draftOrder.md'
---

# draft​Order

query

Retrieves a [draft order](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder) by its ID. A draft order is an order created by a merchant on behalf of their customers. Draft orders contain all necessary order details (products, pricing, customer information) but require payment to be accepted before they can be converted into [completed orders](https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderComplete).

Use the `draftOrder` query to retrieve information associated with the following workflows:

* Creating orders for phone, in-person, or chat sales
* Sending invoices to customers with secure checkout links
* Managing custom items and additional costs
* Selling products at discount or wholesale rates
* Processing pre-orders and saving drafts for later completion

A draft order is associated with a [customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer) and contains multiple [line items](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrderLineItem). Each draft order has a [status](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder#field-DraftOrder.fields.status), which indicates its progress through the sales workflow.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `DraftOrder` to return.

***

## Possible returns

* Draft​Order

  [Draft​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder)

  An order that a merchant creates on behalf of a customer. Draft orders are useful for merchants that need to do the following tasks:

  * Create new orders for sales made by phone, in person, by chat, or elsewhere. When a merchant accepts payment for a draft order, an order is created.
  * Send invoices to customers to pay with a secure checkout link.
  * Use custom items to represent additional costs or products that aren't displayed in a shop's inventory.
  * Re-create orders manually from active sales channels.
  * Sell products at discount or wholesale rates.
  * Take pre-orders.

  For draft orders in multiple currencies `presentment_money` is the main reference for what a customer is going to be charged and `shop_money` is an estimate of what the merchant might receive in their shop currency.

  **Caution:** Only use this data if it's required for your app's functionality. Shopify will restrict [access to scopes](https://shopify.dev/api/usage/access-scopes) for apps that don't have a legitimate use for the associated data.

  Draft orders created on or after April 1, 2025 will be automatically purged after one year of inactivity.

  * accept​Automatic​Discounts

    [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    Whether or not to accept automatic discounts on the draft order during calculation. If false, only discount codes and custom draft order discounts (see `appliedDiscount`) will be applied. If true, eligible automatic discounts will be applied in addition to discount codes and custom draft order discounts.

  * allow​Discount​Codes​In​Checkout

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether discount codes are allowed during checkout of this draft order.

  * all​Variant​Prices​Overridden

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether all variant prices have been overridden.

  * any​Variant​Prices​Overridden

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether any variant prices have been overridden.

  * applied​Discount

    [Draft​Order​Applied​Discount](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrderAppliedDiscount)

    The custom order-level discount applied.

  * billing​Address

    [Mailing​Address](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress)

    The billing address of the customer.

  * billing​Address​Matches​Shipping​Address

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the billing address matches the shipping address.

  * completed​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time when the draft order was converted to a new order, and had it's status changed to **Completed**.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the draft order was created in Shopify.

  * currency​Code

    [Currency​Code!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CurrencyCode)

    non-null

    The shop currency used for calculation.

  * custom​Attributes

    [\[Attribute!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Attribute)

    non-null

    The custom information added to the draft order on behalf of the customer.

  * customer

    [Customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

    The customer who will be sent an invoice.

  * default​Cursor

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    A default [cursor](https://shopify.dev/api/usage/pagination-graphql) that returns the single next record, sorted ascending by ID.

  * discount​Codes

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    All discount codes applied.

  * email

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The email address of the customer, which is used to send notifications.

  * events

    [Event​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/EventConnection)

    non-null

    The list of events associated with the draft order.

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

  * has​Timeline​Comment

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the merchant has added timeline comments to the draft order.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * invoice​Email​Template​Subject

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The subject defined for the draft invoice email template.

  * invoice​Sent​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The date and time when the invoice was last emailed to the customer.

  * invoice​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    The link to the checkout, which is sent to the customer in the invoice email.

  * legacy​Resource​Id

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The ID of the corresponding resource in the REST Admin API.

  * line​Items

    [Draft​Order​Line​Item​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/DraftOrderLineItemConnection)

    non-null

    The list of the line items in the draft order.

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

  * line​Items​Subtotal​Price

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    A subtotal of the line items and corresponding discounts, excluding shipping charges, shipping discounts, taxes, or order discounts.

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

    The identifier for the draft order, which is unique within the store. For example, *#D1223*.

  * note2

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The text from an optional note attached to the draft order.

  * order

    [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

    The order that was created from the draft order.

  * payment​Terms

    [Payment​Terms](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentTerms)

    The associated payment terms for this draft order.

  * phone

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The assigned phone number.

  * platform​Discounts

    [\[Draft​Order​Platform​Discount!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrderPlatformDiscount)

    non-null

    The list of platform discounts applied.

  * po​Number

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The purchase order number.

  * presentment​Currency​Code

    [Currency​Code!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CurrencyCode)

    non-null

    The payment currency used for calculation.

  * purchasing​Entity

    [Purchasing​Entity](https://shopify.dev/docs/api/admin-graphql/latest/unions/PurchasingEntity)

    The purchasing entity.

  * ready

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the draft order is ready and can be completed. Draft orders might have asynchronous operations that can take time to finish.

  * reserve​Inventory​Until

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The time after which inventory will automatically be restocked.

  * shipping​Address

    [Mailing​Address](https://shopify.dev/docs/api/admin-graphql/latest/objects/MailingAddress)

    The shipping address of the customer.

  * shipping​Line

    [Shipping​Line](https://shopify.dev/docs/api/admin-graphql/latest/objects/ShippingLine)

    The line item containing the shipping information and costs.

  * status

    [Draft​Order​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/DraftOrderStatus)

    non-null

    The status of the draft order.

  * subtotal​Price​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The subtotal, of the line items and their discounts, excluding shipping charges, shipping discounts, and taxes.

  * tags

    [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The comma separated list of tags associated with the draft order. Updating `tags` overwrites any existing tags that were previously added to the draft order. To add new tags without overwriting existing tags, use the [tagsAdd](https://shopify.dev/api/admin-graphql/latest/mutations/tagsadd) mutation.

  * taxes​Included

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the line item prices include taxes.

  * tax​Exempt

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the draft order is tax exempt.

  * tax​Lines

    [\[Tax​Line!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TaxLine)

    non-null

    The list of of taxes lines charged for each line item and shipping line.

  * total​Discounts​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    Total discounts.

  * total​Line​Items​Price​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    Total price of line items, excluding discounts.

  * total​Price​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total price, includes taxes, shipping charges, and discounts.

  * total​Quantity​Of​Line​Items

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The sum of individual line item quantities. If the draft order has bundle items, this is the sum containing the quantities of individual items in the bundle.

  * total​Shipping​Price​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total shipping price.

  * total​Tax​Set

    [Money​Bag!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MoneyBag)

    non-null

    The total tax.

  * total​Weight

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    The total weight in grams of the draft order.

  * transformer​Fingerprint

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    Fingerprint of the current cart. In order to have bundles work, the fingerprint must be passed to each request as it was previously returned, unmodified.

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    The date and time when the draft order was last changed. The format is YYYY-MM-DD HH:mm:ss. For example, 2016-02-05 17:04:01.

  * visible​To​Customer

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the draft order will be visible to the customer on the self-serve portal.

  * warnings

    [\[Draft​Order​Warning!\]!](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/DraftOrderWarning)

    non-null

    The list of warnings raised while calculating.

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

  * market​Name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-nullDeprecated

  * market​Region​Country​Code

    [Country​Code!](https://shopify.dev/docs/api/admin-graphql/latest/enums/CountryCode)

    non-nullDeprecated

  * subtotal​Price

    [Money!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    non-nullDeprecated

  * total​Price

    [Money!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    non-nullDeprecated

  * total​Shipping​Price

    [Money!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    non-nullDeprecated

  * total​Tax

    [Money!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Money)

    non-nullDeprecated

***

## Examples

* ### Get a draft order by ID

  #### Description

  The following query retrieves a draft order by ID and returns the draft order name.

  #### Query

  ```graphql
  query {
    draftOrder(id: "gid://shopify/DraftOrder/276395349") {
      name
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
  "query": "query { draftOrder(id: \"gid://shopify/DraftOrder/276395349\") { name } }"
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
      draftOrder(id: "gid://shopify/DraftOrder/276395349") {
        name
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
      draftOrder(id: "gid://shopify/DraftOrder/276395349") {
        name
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
      draftOrder(id: "gid://shopify/DraftOrder/276395349") {
        name
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    draftOrder(id: "gid://shopify/DraftOrder/276395349") {
      name
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrder": {
      "name": "#D1"
    }
  }
  ```

* ### Get a list of draft orders by ID and GraphQL alias

  #### Description

  The following query retrieves a list of draft orders by ID and GraphQL alias and returns the name for each draft order.

  #### Query

  ```graphql
  query {
    draftOrder1: draftOrder(id: "gid://shopify/DraftOrder/276395349") {
      name
    }
    draftOrder2: draftOrder(id: "gid://shopify/DraftOrder/221448317") {
      name
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
  "query": "query { draftOrder1: draftOrder(id: \"gid://shopify/DraftOrder/276395349\") { name } draftOrder2: draftOrder(id: \"gid://shopify/DraftOrder/221448317\") { name } }"
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
      draftOrder1: draftOrder(id: "gid://shopify/DraftOrder/276395349") {
        name
      }
      draftOrder2: draftOrder(id: "gid://shopify/DraftOrder/221448317") {
        name
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
      draftOrder1: draftOrder(id: "gid://shopify/DraftOrder/276395349") {
        name
      }
      draftOrder2: draftOrder(id: "gid://shopify/DraftOrder/221448317") {
        name
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
      draftOrder1: draftOrder(id: "gid://shopify/DraftOrder/276395349") {
        name
      }
      draftOrder2: draftOrder(id: "gid://shopify/DraftOrder/221448317") {
        name
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    draftOrder1: draftOrder(id: "gid://shopify/DraftOrder/276395349") {
      name
    }
    draftOrder2: draftOrder(id: "gid://shopify/DraftOrder/221448317") {
      name
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrder1": {
      "name": "#D1"
    },
    "draftOrder2": {
      "name": "#D7"
    }
  }
  ```

* ### Get a list of line item names for a draft order

  #### Description

  The following query retrieves the first 5 line items for a draft order and returns the name of each line item.

  #### Query

  ```graphql
  query {
    draftOrder(id: "gid://shopify/DraftOrder/276395349") {
      lineItems(first: 5) {
        edges {
          node {
            name
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
  "query": "query { draftOrder(id: \"gid://shopify/DraftOrder/276395349\") { lineItems(first: 5) { edges { node { name } } } } }"
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
      draftOrder(id: "gid://shopify/DraftOrder/276395349") {
        lineItems(first: 5) {
          edges {
            node {
              name
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
      draftOrder(id: "gid://shopify/DraftOrder/276395349") {
        lineItems(first: 5) {
          edges {
            node {
              name
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
      draftOrder(id: "gid://shopify/DraftOrder/276395349") {
        lineItems(first: 5) {
          edges {
            node {
              name
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
    draftOrder(id: "gid://shopify/DraftOrder/276395349") {
      lineItems(first: 5) {
        edges {
          node {
            name
          }
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "draftOrder": {
      "lineItems": {
        "edges": [
          {
            "node": {
              "name": "Boots - Default"
            }
          }
        ]
      }
    }
  }
  ```

* ### Get a metafield attached to a draft order

  #### Description

  Get the metafield value identified by \`my\_fields.purchase\_order\` on a specific draft order.

  #### Query

  ```graphql
  query DraftOrderMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
    draftOrder(id: $ownerId) {
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
    "ownerId": "gid://shopify/DraftOrder/276395349"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query DraftOrderMetafield($namespace: String!, $key: String!, $ownerId: ID!) { draftOrder(id: $ownerId) { purchaseOrder: metafield(namespace: $namespace, key: $key) { value } } }",
   "variables": {
      "namespace": "my_fields",
      "key": "purchase_order",
      "ownerId": "gid://shopify/DraftOrder/276395349"
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
    query DraftOrderMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
      draftOrder(id: $ownerId) {
        purchaseOrder: metafield(namespace: $namespace, key: $key) {
          value
        }
      }
    }`,
    {
      variables: {
          "namespace": "my_fields",
          "key": "purchase_order",
          "ownerId": "gid://shopify/DraftOrder/276395349"
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
    query DraftOrderMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
      draftOrder(id: $ownerId) {
        purchaseOrder: metafield(namespace: $namespace, key: $key) {
          value
        }
      }
    }
  QUERY

  variables = {
    "namespace": "my_fields",
    "key": "purchase_order",
    "ownerId": "gid://shopify/DraftOrder/276395349"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query DraftOrderMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
        draftOrder(id: $ownerId) {
          purchaseOrder: metafield(namespace: $namespace, key: $key) {
            value
          }
        }
      }`,
      "variables": {
          "namespace": "my_fields",
          "key": "purchase_order",
          "ownerId": "gid://shopify/DraftOrder/276395349"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query DraftOrderMetafield($namespace: String!, $key: String!, $ownerId: ID!) {
    draftOrder(id: $ownerId) {
      purchaseOrder: metafield(namespace: $namespace, key: $key) {
        value
      }
    }
  }' \
  --variables \
  '{
    "namespace": "my_fields",
    "key": "purchase_order",
    "ownerId": "gid://shopify/DraftOrder/276395349"
  }'
  ```

  #### Response

  ```json
  {
    "draftOrder": {
      "purchaseOrder": {
        "value": "123"
      }
    }
  }
  ```

* ### Get metafields attached to a draft order

  #### Description

  Get a page of metafields attached to a specific draft order.

  #### Query

  ```graphql
  query DraftOrderMetafields($ownerId: ID!) {
    draftOrder(id: $ownerId) {
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
    "ownerId": "gid://shopify/DraftOrder/276395349"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query DraftOrderMetafields($ownerId: ID!) { draftOrder(id: $ownerId) { metafields(first: 3) { edges { node { namespace key value } } } } }",
   "variables": {
      "ownerId": "gid://shopify/DraftOrder/276395349"
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
    query DraftOrderMetafields($ownerId: ID!) {
      draftOrder(id: $ownerId) {
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
          "ownerId": "gid://shopify/DraftOrder/276395349"
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
    query DraftOrderMetafields($ownerId: ID!) {
      draftOrder(id: $ownerId) {
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
    "ownerId": "gid://shopify/DraftOrder/276395349"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query DraftOrderMetafields($ownerId: ID!) {
        draftOrder(id: $ownerId) {
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
          "ownerId": "gid://shopify/DraftOrder/276395349"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query DraftOrderMetafields($ownerId: ID!) {
    draftOrder(id: $ownerId) {
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
    "ownerId": "gid://shopify/DraftOrder/276395349"
  }'
  ```

  #### Response

  ```json
  {
    "draftOrder": {
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

* ### Receive a single DraftOrder

  #### Query

  ```graphql
  query DraftOrder($id: ID!) {
    draftOrder(id: $id) {
      id
      note2
      email
      taxesIncluded
      currencyCode
      invoiceSentAt
      createdAt
      updatedAt
      taxExempt
      completedAt
      name
      status
      lineItems(first: 10) {
        edges {
          node {
            id
            variant {
              id
              title
            }
            product {
              id
            }
            name
            sku
            vendor
            quantity
            requiresShipping
            taxable
            isGiftCard
            fulfillmentService {
              type
            }
            weight {
              unit
              value
            }
            taxLines {
              title
              source
              rate
              ratePercentage
              priceSet {
                presentmentMoney {
                  amount
                  currencyCode
                }
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
            appliedDiscount {
              title
              value
              valueType
            }
            name
            custom
            id
          }
        }
      }
      shippingAddress {
        firstName
        address1
        phone
        city
        zip
        province
        country
        lastName
        address2
        company
        latitude
        longitude
        name
        country
        countryCodeV2
        provinceCode
      }
      billingAddress {
        firstName
        address1
        phone
        city
        zip
        province
        country
        lastName
        address2
        company
        latitude
        longitude
        name
        country
        countryCodeV2
        provinceCode
      }
      invoiceUrl
      appliedDiscount {
        title
        value
        valueType
      }
      order {
        id
        customAttributes {
          key
          value
        }
      }
      shippingLine {
        id
        title
        carrierIdentifier
        custom
        code
        deliveryCategory
        source
        discountedPriceSet {
          presentmentMoney {
            amount
            currencyCode
          }
          shopMoney {
            amount
            currencyCode
          }
        }
      }
      taxLines {
        channelLiable
        priceSet {
          presentmentMoney {
            amount
            currencyCode
          }
          shopMoney {
            amount
            currencyCode
          }
        }
        rate
        ratePercentage
        source
        title
      }
      tags
      customer {
        id
        email
        smsMarketingConsent {
          consentCollectedFrom
          consentUpdatedAt
          marketingOptInLevel
          marketingState
        }
        emailMarketingConsent {
          consentUpdatedAt
          marketingOptInLevel
          marketingState
        }
        createdAt
        updatedAt
        firstName
        lastName
        state
        amountSpent {
          amount
          currencyCode
        }
        lastOrder {
          id
          name
          currencyCode
        }
        note
        verifiedEmail
        multipassIdentifier
        taxExempt
        tags
        phone
        taxExemptions
        defaultAddress {
          id
          firstName
          lastName
          company
          address1
          address2
          city
          province
          country
          zip
          phone
          name
          provinceCode
          countryCodeV2
        }
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/DraftOrder/221448317"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query DraftOrder($id: ID!) { draftOrder(id: $id) { id note2 email taxesIncluded currencyCode invoiceSentAt createdAt updatedAt taxExempt completedAt name status lineItems(first: 10) { edges { node { id variant { id title } product { id } name sku vendor quantity requiresShipping taxable isGiftCard fulfillmentService { type } weight { unit value } taxLines { title source rate ratePercentage priceSet { presentmentMoney { amount currencyCode } shopMoney { amount currencyCode } } } appliedDiscount { title value valueType } name custom id } } } shippingAddress { firstName address1 phone city zip province country lastName address2 company latitude longitude name country countryCodeV2 provinceCode } billingAddress { firstName address1 phone city zip province country lastName address2 company latitude longitude name country countryCodeV2 provinceCode } invoiceUrl appliedDiscount { title value valueType } order { id customAttributes { key value } } shippingLine { id title carrierIdentifier custom code deliveryCategory source discountedPriceSet { presentmentMoney { amount currencyCode } shopMoney { amount currencyCode } } } taxLines { channelLiable priceSet { presentmentMoney { amount currencyCode } shopMoney { amount currencyCode } } rate ratePercentage source title } tags customer { id email smsMarketingConsent { consentCollectedFrom consentUpdatedAt marketingOptInLevel marketingState } emailMarketingConsent { consentUpdatedAt marketingOptInLevel marketingState } createdAt updatedAt firstName lastName state amountSpent { amount currencyCode } lastOrder { id name currencyCode } note verifiedEmail multipassIdentifier taxExempt tags phone taxExemptions defaultAddress { id firstName lastName company address1 address2 city province country zip phone name provinceCode countryCodeV2 } } } }",
   "variables": {
      "id": "gid://shopify/DraftOrder/221448317"
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
    query DraftOrder($id: ID!) {
      draftOrder(id: $id) {
        id
        note2
        email
        taxesIncluded
        currencyCode
        invoiceSentAt
        createdAt
        updatedAt
        taxExempt
        completedAt
        name
        status
        lineItems(first: 10) {
          edges {
            node {
              id
              variant {
                id
                title
              }
              product {
                id
              }
              name
              sku
              vendor
              quantity
              requiresShipping
              taxable
              isGiftCard
              fulfillmentService {
                type
              }
              weight {
                unit
                value
              }
              taxLines {
                title
                source
                rate
                ratePercentage
                priceSet {
                  presentmentMoney {
                    amount
                    currencyCode
                  }
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
              }
              appliedDiscount {
                title
                value
                valueType
              }
              name
              custom
              id
            }
          }
        }
        shippingAddress {
          firstName
          address1
          phone
          city
          zip
          province
          country
          lastName
          address2
          company
          latitude
          longitude
          name
          country
          countryCodeV2
          provinceCode
        }
        billingAddress {
          firstName
          address1
          phone
          city
          zip
          province
          country
          lastName
          address2
          company
          latitude
          longitude
          name
          country
          countryCodeV2
          provinceCode
        }
        invoiceUrl
        appliedDiscount {
          title
          value
          valueType
        }
        order {
          id
          customAttributes {
            key
            value
          }
        }
        shippingLine {
          id
          title
          carrierIdentifier
          custom
          code
          deliveryCategory
          source
          discountedPriceSet {
            presentmentMoney {
              amount
              currencyCode
            }
            shopMoney {
              amount
              currencyCode
            }
          }
        }
        taxLines {
          channelLiable
          priceSet {
            presentmentMoney {
              amount
              currencyCode
            }
            shopMoney {
              amount
              currencyCode
            }
          }
          rate
          ratePercentage
          source
          title
        }
        tags
        customer {
          id
          email
          smsMarketingConsent {
            consentCollectedFrom
            consentUpdatedAt
            marketingOptInLevel
            marketingState
          }
          emailMarketingConsent {
            consentUpdatedAt
            marketingOptInLevel
            marketingState
          }
          createdAt
          updatedAt
          firstName
          lastName
          state
          amountSpent {
            amount
            currencyCode
          }
          lastOrder {
            id
            name
            currencyCode
          }
          note
          verifiedEmail
          multipassIdentifier
          taxExempt
          tags
          phone
          taxExemptions
          defaultAddress {
            id
            firstName
            lastName
            company
            address1
            address2
            city
            province
            country
            zip
            phone
            name
            provinceCode
            countryCodeV2
          }
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/DraftOrder/221448317"
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
    query DraftOrder($id: ID!) {
      draftOrder(id: $id) {
        id
        note2
        email
        taxesIncluded
        currencyCode
        invoiceSentAt
        createdAt
        updatedAt
        taxExempt
        completedAt
        name
        status
        lineItems(first: 10) {
          edges {
            node {
              id
              variant {
                id
                title
              }
              product {
                id
              }
              name
              sku
              vendor
              quantity
              requiresShipping
              taxable
              isGiftCard
              fulfillmentService {
                type
              }
              weight {
                unit
                value
              }
              taxLines {
                title
                source
                rate
                ratePercentage
                priceSet {
                  presentmentMoney {
                    amount
                    currencyCode
                  }
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
              }
              appliedDiscount {
                title
                value
                valueType
              }
              name
              custom
              id
            }
          }
        }
        shippingAddress {
          firstName
          address1
          phone
          city
          zip
          province
          country
          lastName
          address2
          company
          latitude
          longitude
          name
          country
          countryCodeV2
          provinceCode
        }
        billingAddress {
          firstName
          address1
          phone
          city
          zip
          province
          country
          lastName
          address2
          company
          latitude
          longitude
          name
          country
          countryCodeV2
          provinceCode
        }
        invoiceUrl
        appliedDiscount {
          title
          value
          valueType
        }
        order {
          id
          customAttributes {
            key
            value
          }
        }
        shippingLine {
          id
          title
          carrierIdentifier
          custom
          code
          deliveryCategory
          source
          discountedPriceSet {
            presentmentMoney {
              amount
              currencyCode
            }
            shopMoney {
              amount
              currencyCode
            }
          }
        }
        taxLines {
          channelLiable
          priceSet {
            presentmentMoney {
              amount
              currencyCode
            }
            shopMoney {
              amount
              currencyCode
            }
          }
          rate
          ratePercentage
          source
          title
        }
        tags
        customer {
          id
          email
          smsMarketingConsent {
            consentCollectedFrom
            consentUpdatedAt
            marketingOptInLevel
            marketingState
          }
          emailMarketingConsent {
            consentUpdatedAt
            marketingOptInLevel
            marketingState
          }
          createdAt
          updatedAt
          firstName
          lastName
          state
          amountSpent {
            amount
            currencyCode
          }
          lastOrder {
            id
            name
            currencyCode
          }
          note
          verifiedEmail
          multipassIdentifier
          taxExempt
          tags
          phone
          taxExemptions
          defaultAddress {
            id
            firstName
            lastName
            company
            address1
            address2
            city
            province
            country
            zip
            phone
            name
            provinceCode
            countryCodeV2
          }
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/DraftOrder/221448317"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query DraftOrder($id: ID!) {
        draftOrder(id: $id) {
          id
          note2
          email
          taxesIncluded
          currencyCode
          invoiceSentAt
          createdAt
          updatedAt
          taxExempt
          completedAt
          name
          status
          lineItems(first: 10) {
            edges {
              node {
                id
                variant {
                  id
                  title
                }
                product {
                  id
                }
                name
                sku
                vendor
                quantity
                requiresShipping
                taxable
                isGiftCard
                fulfillmentService {
                  type
                }
                weight {
                  unit
                  value
                }
                taxLines {
                  title
                  source
                  rate
                  ratePercentage
                  priceSet {
                    presentmentMoney {
                      amount
                      currencyCode
                    }
                    shopMoney {
                      amount
                      currencyCode
                    }
                  }
                }
                appliedDiscount {
                  title
                  value
                  valueType
                }
                name
                custom
                id
              }
            }
          }
          shippingAddress {
            firstName
            address1
            phone
            city
            zip
            province
            country
            lastName
            address2
            company
            latitude
            longitude
            name
            country
            countryCodeV2
            provinceCode
          }
          billingAddress {
            firstName
            address1
            phone
            city
            zip
            province
            country
            lastName
            address2
            company
            latitude
            longitude
            name
            country
            countryCodeV2
            provinceCode
          }
          invoiceUrl
          appliedDiscount {
            title
            value
            valueType
          }
          order {
            id
            customAttributes {
              key
              value
            }
          }
          shippingLine {
            id
            title
            carrierIdentifier
            custom
            code
            deliveryCategory
            source
            discountedPriceSet {
              presentmentMoney {
                amount
                currencyCode
              }
              shopMoney {
                amount
                currencyCode
              }
            }
          }
          taxLines {
            channelLiable
            priceSet {
              presentmentMoney {
                amount
                currencyCode
              }
              shopMoney {
                amount
                currencyCode
              }
            }
            rate
            ratePercentage
            source
            title
          }
          tags
          customer {
            id
            email
            smsMarketingConsent {
              consentCollectedFrom
              consentUpdatedAt
              marketingOptInLevel
              marketingState
            }
            emailMarketingConsent {
              consentUpdatedAt
              marketingOptInLevel
              marketingState
            }
            createdAt
            updatedAt
            firstName
            lastName
            state
            amountSpent {
              amount
              currencyCode
            }
            lastOrder {
              id
              name
              currencyCode
            }
            note
            verifiedEmail
            multipassIdentifier
            taxExempt
            tags
            phone
            taxExemptions
            defaultAddress {
              id
              firstName
              lastName
              company
              address1
              address2
              city
              province
              country
              zip
              phone
              name
              provinceCode
              countryCodeV2
            }
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/DraftOrder/221448317"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query DraftOrder($id: ID!) {
    draftOrder(id: $id) {
      id
      note2
      email
      taxesIncluded
      currencyCode
      invoiceSentAt
      createdAt
      updatedAt
      taxExempt
      completedAt
      name
      status
      lineItems(first: 10) {
        edges {
          node {
            id
            variant {
              id
              title
            }
            product {
              id
            }
            name
            sku
            vendor
            quantity
            requiresShipping
            taxable
            isGiftCard
            fulfillmentService {
              type
            }
            weight {
              unit
              value
            }
            taxLines {
              title
              source
              rate
              ratePercentage
              priceSet {
                presentmentMoney {
                  amount
                  currencyCode
                }
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
            appliedDiscount {
              title
              value
              valueType
            }
            name
            custom
            id
          }
        }
      }
      shippingAddress {
        firstName
        address1
        phone
        city
        zip
        province
        country
        lastName
        address2
        company
        latitude
        longitude
        name
        country
        countryCodeV2
        provinceCode
      }
      billingAddress {
        firstName
        address1
        phone
        city
        zip
        province
        country
        lastName
        address2
        company
        latitude
        longitude
        name
        country
        countryCodeV2
        provinceCode
      }
      invoiceUrl
      appliedDiscount {
        title
        value
        valueType
      }
      order {
        id
        customAttributes {
          key
          value
        }
      }
      shippingLine {
        id
        title
        carrierIdentifier
        custom
        code
        deliveryCategory
        source
        discountedPriceSet {
          presentmentMoney {
            amount
            currencyCode
          }
          shopMoney {
            amount
            currencyCode
          }
        }
      }
      taxLines {
        channelLiable
        priceSet {
          presentmentMoney {
            amount
            currencyCode
          }
          shopMoney {
            amount
            currencyCode
          }
        }
        rate
        ratePercentage
        source
        title
      }
      tags
      customer {
        id
        email
        smsMarketingConsent {
          consentCollectedFrom
          consentUpdatedAt
          marketingOptInLevel
          marketingState
        }
        emailMarketingConsent {
          consentUpdatedAt
          marketingOptInLevel
          marketingState
        }
        createdAt
        updatedAt
        firstName
        lastName
        state
        amountSpent {
          amount
          currencyCode
        }
        lastOrder {
          id
          name
          currencyCode
        }
        note
        verifiedEmail
        multipassIdentifier
        taxExempt
        tags
        phone
        taxExemptions
        defaultAddress {
          id
          firstName
          lastName
          company
          address1
          address2
          city
          province
          country
          zip
          phone
          name
          provinceCode
          countryCodeV2
        }
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/DraftOrder/221448317"
  }'
  ```

  #### Response

  ```json
  {
    "draftOrder": {
      "id": "gid://shopify/DraftOrder/221448317",
      "note2": "gift",
      "email": "bobsemail@shopify.com",
      "taxesIncluded": false,
      "currencyCode": "USD",
      "invoiceSentAt": null,
      "createdAt": "2017-01-01T00:00:00Z",
      "updatedAt": "2021-12-01T12:43:00Z",
      "taxExempt": false,
      "completedAt": null,
      "name": "#D7",
      "status": "OPEN",
      "lineItems": {
        "edges": [
          {
            "node": {
              "id": "gid://shopify/DraftOrderLineItem/227425250",
              "variant": {
                "id": "gid://shopify/ProductVariant/330284860",
                "title": "Default"
              },
              "product": {
                "id": "gid://shopify/Product/558169081"
              },
              "name": "Unpublished Boots - Default",
              "sku": "unpublished_boots-12",
              "vendor": "Greedy Boot Maker",
              "quantity": 5,
              "requiresShipping": true,
              "taxable": true,
              "isGiftCard": false,
              "fulfillmentService": {
                "type": "MANUAL"
              },
              "weight": {
                "unit": "GRAMS",
                "value": 10
              },
              "taxLines": [
                {
                  "title": "GST",
                  "source": "Shopify",
                  "rate": 0.07,
                  "ratePercentage": 7,
                  "priceSet": {
                    "presentmentMoney": {
                      "amount": "42.53",
                      "currencyCode": "USD"
                    },
                    "shopMoney": {
                      "amount": "42.53",
                      "currencyCode": "USD"
                    }
                  }
                },
                {
                  "title": "PST",
                  "source": "Shopify",
                  "rate": 0.08,
                  "ratePercentage": 8,
                  "priceSet": {
                    "presentmentMoney": {
                      "amount": "48.6",
                      "currencyCode": "USD"
                    },
                    "shopMoney": {
                      "amount": "48.6",
                      "currencyCode": "USD"
                    }
                  }
                }
              ],
              "appliedDiscount": null,
              "custom": false
            }
          },
          {
            "node": {
              "id": "gid://shopify/DraftOrderLineItem/446166744",
              "variant": {
                "id": "gid://shopify/ProductVariant/445365074",
                "title": "Medium"
              },
              "product": {
                "id": "gid://shopify/Product/910489600"
              },
              "name": "Crafty Shoes - Green",
              "sku": "crappy_shoes_green",
              "vendor": "Crappy Cobbler",
              "quantity": 2,
              "requiresShipping": false,
              "taxable": true,
              "isGiftCard": false,
              "fulfillmentService": {
                "type": "MANUAL"
              },
              "weight": {
                "unit": "GRAMS",
                "value": 10
              },
              "taxLines": [
                {
                  "title": "PST",
                  "source": "Shopify",
                  "rate": 0.08,
                  "ratePercentage": 8,
                  "priceSet": {
                    "presentmentMoney": {
                      "amount": "13.68",
                      "currencyCode": "USD"
                    },
                    "shopMoney": {
                      "amount": "13.68",
                      "currencyCode": "USD"
                    }
                  }
                },
                {
                  "title": "GST",
                  "source": "Shopify",
                  "rate": 0.07,
                  "ratePercentage": 7,
                  "priceSet": {
                    "presentmentMoney": {
                      "amount": "11.97",
                      "currencyCode": "USD"
                    },
                    "shopMoney": {
                      "amount": "11.97",
                      "currencyCode": "USD"
                    }
                  }
                }
              ],
              "appliedDiscount": {
                "title": null,
                "value": 5,
                "valueType": "FIXED_AMOUNT"
              },
              "custom": false
            }
          },
          {
            "node": {
              "id": "gid://shopify/DraftOrderLineItem/654123718",
              "variant": null,
              "product": null,
              "name": "Fingerless wool gloves",
              "sku": "fingerless_wool_gloves",
              "vendor": "Bear Hands",
              "quantity": 2,
              "requiresShipping": true,
              "taxable": true,
              "isGiftCard": false,
              "fulfillmentService": {
                "type": "MANUAL"
              },
              "weight": {
                "unit": "GRAMS",
                "value": 50
              },
              "taxLines": [
                {
                  "title": "PST",
                  "source": "Shopify",
                  "rate": 0.08,
                  "ratePercentage": 8,
                  "priceSet": {
                    "presentmentMoney": {
                      "amount": "10.8",
                      "currencyCode": "USD"
                    },
                    "shopMoney": {
                      "amount": "10.8",
                      "currencyCode": "USD"
                    }
                  }
                },
                {
                  "title": "GST",
                  "source": "Shopify",
                  "rate": 0.07,
                  "ratePercentage": 7,
                  "priceSet": {
                    "presentmentMoney": {
                      "amount": "9.45",
                      "currencyCode": "USD"
                    },
                    "shopMoney": {
                      "amount": "9.45",
                      "currencyCode": "USD"
                    }
                  }
                }
              ],
              "appliedDiscount": null,
              "custom": true
            }
          }
        ]
      },
      "shippingAddress": {
        "firstName": "Bob",
        "address1": "123 Amoebobacterieae St",
        "phone": "+1(613)555-1212",
        "city": "Ottawa",
        "zip": "K2P0V6",
        "province": "Ontario",
        "country": "Canada",
        "lastName": "Bobsen",
        "address2": "",
        "company": "",
        "latitude": 45.41634,
        "longitude": -75.6868,
        "name": "Bob Bobsen",
        "countryCodeV2": "CA",
        "provinceCode": "ON"
      },
      "billingAddress": {
        "firstName": "Bob",
        "address1": "123 Amoebobacterieae St",
        "phone": "+1(613)555-1212",
        "city": "Ottawa",
        "zip": "K2P0V6",
        "province": "Ontario",
        "country": "Canada",
        "lastName": "Bobsen",
        "address2": "",
        "company": "",
        "latitude": 45.41634,
        "longitude": -75.6868,
        "name": "Bob Bobsen",
        "countryCodeV2": "CA",
        "provinceCode": "ON"
      },
      "invoiceUrl": "https://www.snowdevil.ca/26371970/invoices/ba8dcf6c022ccad3d47e3909e378e22f",
      "appliedDiscount": {
        "title": "Custom",
        "value": 10,
        "valueType": "PERCENTAGE"
      },
      "order": null,
      "shippingLine": {
        "id": "gid://shopify/ShippingLine/671422168?type=draft_order",
        "title": "custom shipping",
        "carrierIdentifier": null,
        "custom": true,
        "code": "custom",
        "deliveryCategory": "shipping",
        "source": "shopify",
        "discountedPriceSet": {
          "presentmentMoney": {
            "amount": "12.25",
            "currencyCode": "USD"
          },
          "shopMoney": {
            "amount": "12.25",
            "currencyCode": "USD"
          }
        }
      },
      "taxLines": [
        {
          "channelLiable": null,
          "priceSet": {
            "presentmentMoney": {
              "amount": "73.08",
              "currencyCode": "USD"
            },
            "shopMoney": {
              "amount": "73.08",
              "currencyCode": "USD"
            }
          },
          "rate": 0.08,
          "ratePercentage": 8,
          "source": null,
          "title": "PST"
        },
        {
          "channelLiable": null,
          "priceSet": {
            "presentmentMoney": {
              "amount": "63.95",
              "currencyCode": "USD"
            },
            "shopMoney": {
              "amount": "63.95",
              "currencyCode": "USD"
            }
          },
          "rate": 0.07,
          "ratePercentage": 7,
          "source": null,
          "title": "GST"
        }
      ],
      "tags": [
        "High priority",
        "Wholesale"
      ],
      "customer": {
        "id": "gid://shopify/Customer/544365967",
        "email": "bob@example.com",
        "smsMarketingConsent": {
          "consentCollectedFrom": "OTHER",
          "consentUpdatedAt": "2021-06-16T17:31:44Z",
          "marketingOptInLevel": "SINGLE_OPT_IN",
          "marketingState": "SUBSCRIBED"
        },
        "emailMarketingConsent": {
          "consentUpdatedAt": "2005-06-16T15:00:11Z",
          "marketingOptInLevel": "SINGLE_OPT_IN",
          "marketingState": "SUBSCRIBED"
        },
        "createdAt": "2005-06-15T15:57:11Z",
        "updatedAt": "2005-06-16T15:57:11Z",
        "firstName": "Bob",
        "lastName": "Bobsen",
        "state": "ENABLED",
        "amountSpent": {
          "amount": "8305.6",
          "currencyCode": "USD"
        },
        "lastOrder": null,
        "note": null,
        "verifiedEmail": true,
        "multipassIdentifier": null,
        "taxExempt": false,
        "tags": [
          "Bob",
          "Canadian",
          "Léon",
          "Noël"
        ],
        "phone": "+13125551212",
        "taxExemptions": [],
        "defaultAddress": {
          "id": "gid://shopify/MailingAddress/544365967?model_name=CustomerAddress",
          "firstName": "Bob",
          "lastName": "Bobsen",
          "company": "",
          "address1": "123 Amoebobacterieae St",
          "address2": "",
          "city": "Ottawa",
          "province": "Ontario",
          "country": "Canada",
          "zip": "K2P0V6",
          "phone": "+1(613)555-1212",
          "name": "Bob Bobsen",
          "provinceCode": "ON",
          "countryCodeV2": "CA"
        }
      }
    }
  }
  ```
