---
title: deliveryProfile - GraphQL Admin
description: >-
  Retrieves a
  [`DeliveryProfile`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryProfile)
  by ID. Delivery profiles group shipping settings for specific
  [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)
  objects that ship from selected
  [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)
  objects to [delivery
  zones](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryZone
  with defined rates.


  Learn more about [delivery
  profiles](https://shopify.dev/docs/apps/build/purchase-options/deferred/delivery-and-deferment#whats-a-delivery-profile).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryProfile'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryProfile.md'
---

# delivery​Profile

query

Retrieves a [`DeliveryProfile`](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryProfile) by ID. Delivery profiles group shipping settings for specific [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) objects that ship from selected [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location) objects to \[delivery zones]\(<https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryZone> with defined rates.

Learn more about [delivery profiles](https://shopify.dev/docs/apps/build/purchase-options/deferred/delivery-and-deferment#whats-a-delivery-profile).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the DeliveryProfile to return.

***

## Possible returns

* Delivery​Profile

  [Delivery​Profile](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryProfile)

  A shipping profile that defines shipping rates for specific [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) objects and [`ProductVariant`](https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant) objects. Delivery profiles determine which products can ship from which [`Location`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location) objects to which zones, and at what rates.

  Profiles can associate with [`SellingPlanGroup`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroup) objects to provide custom shipping rules for subscriptions, such as free shipping or restricted delivery zones. The default profile applies to all products that aren't assigned to other profiles.

  Learn more about [building delivery profiles](https://shopify.dev/apps/build/purchase-options/deferred/delivery-and-deferment/build-delivery-profiles).

  * active​Method​Definitions​Count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The number of active shipping rates for the profile.

  * default

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether this is the default profile.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * locations​Without​Rates​Count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The number of locations without rates defined.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The name of the delivery profile.

  * origin​Location​Count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The number of active origin locations for the profile.

  * product​Variants​Count

    [Count](https://shopify.dev/docs/api/admin-graphql/latest/objects/Count)

    How many product variants are in this profile.

  * profile​Items

    [Delivery​Profile​Item​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/DeliveryProfileItemConnection)

    non-null

    The products and variants associated with this profile.

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

      [Profile​Item​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/ProfileItemSortKeys)

      DeprecatedDefault:ID

    ***

  * profile​Location​Groups

    [\[Delivery​Profile​Location​Group!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryProfileLocationGroup)

    non-null

    The location groups and associated zones using this profile.

    * location​Group​Id

      [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

      ### Arguments

      Filter the location groups of the profile by location group ID.

    ***

  * selling​Plan​Groups

    [Selling​Plan​Group​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SellingPlanGroupConnection)

    non-null

    Selling plan groups associated with the specified delivery profile.

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

  * unassigned​Locations

    [\[Location!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)

    non-null

    List of locations that haven't been assigned to a location group for this profile.

  * unassigned​Locations​Paginated

    [Location​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/LocationConnection)

    non-null

    List of locations that have not been assigned to a location group for this profile.

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

  * version

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The version of the delivery profile.

  * zone​Country​Count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The number of countries with active rates to deliver to.

  * legacy​Mode

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-nullDeprecated (removal date set)

  * product​Variants​Count​V2

    [Delivery​Product​Variants​Count!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryProductVariantsCount)

    non-nullDeprecated

***

## Examples

* ### deliveryProfile reference
