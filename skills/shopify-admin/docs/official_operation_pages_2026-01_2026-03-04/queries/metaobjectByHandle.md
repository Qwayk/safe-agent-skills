---
title: metaobjectByHandle - GraphQL Admin
description: >-
  Retrieves a
  [`Metaobject`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject)
  by its handle and type. Handles are unique identifiers within a metaobject
  type.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/metaobjectByHandle'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/metaobjectByHandle.md
---

# metaobject​By​Handle

query

Requires `read_metaobjects` access scope.

Retrieves a [`Metaobject`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject) by its handle and type. Handles are unique identifiers within a metaobject type.

## Arguments

* handle

  [Metaobject​Handle​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetaobjectHandleInput)

  required

  The identifier of the metaobject to return.

***

## Possible returns

* Metaobject

  [Metaobject](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject)

  An instance of custom structured data defined by a [`MetaobjectDefinition`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition). [Metaobjects](https://shopify.dev/docs/apps/build/custom-data#what-are-metaobjects) store reusable data that extends beyond Shopify's standard resources, such as product highlights, size charts, or custom content sections.

  Each metaobject includes fields that match the field types and validation rules specified in its definition, which also determines the metaobject's capabilities, such as storefront visibility, publishing and translation support. [`Metafields`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metafield) can reference metaobjects to connect custom data with [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) objects, [`Collection`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection) objects, and other Shopify resources.

  * capabilities

    [Metaobject​Capability​Data!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectCapabilityData)

    non-null

    Metaobject capabilities for this Metaobject.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    When the object was created.

  * created​By

    [App!](https://shopify.dev/docs/api/admin-graphql/latest/objects/App)

    non-null

    The app used to create the object.

  * created​By​App

    [App!](https://shopify.dev/docs/api/admin-graphql/latest/objects/App)

    non-null

    The app used to create the object.

  * created​By​Staff

    [Staff​Member](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember)

    The staff member who created the metaobject.

  * definition

    [Metaobject​Definition!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition)

    non-null

    The MetaobjectDefinition that models this object type.

  * display​Name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The preferred display name field value of the metaobject.

  * field

    [Metaobject​Field](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectField)

    The field for an object key, or null if the key has no field definition.

    * key

      [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      required

      ### Arguments

      The metaobject key to access.

    ***

  * fields

    [\[Metaobject​Field!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectField)

    non-null

    All ordered fields of the metaobject with their definitions and values.

  * handle

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The unique handle of the object, useful as a custom ID.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * referenced​By

    [Metafield​Relation​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MetafieldRelationConnection)

    non-null

    List of back references metafields that belong to the resource.

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

  * thumbnail​Field

    [Metaobject​Field](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectField)

    The recommended field to visually represent this metaobject. May be a file reference or color field.

  * type

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The type of the metaobject.

  * updated​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    When the object was last updated.

  * staff​Member

    [Staff​Member](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember)

    Deprecated

***

## Examples

* ### metaobjectByHandle reference
