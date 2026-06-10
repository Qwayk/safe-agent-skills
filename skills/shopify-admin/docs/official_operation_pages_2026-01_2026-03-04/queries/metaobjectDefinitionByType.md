---
title: metaobjectDefinitionByType - GraphQL Admin
description: >-
  Retrieves a
  [`MetaobjectDefinition`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition)
  by its type. The type serves as a unique identifier that distinguishes one
  metaobject definition from another.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/metaobjectDefinitionByType
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/metaobjectDefinitionByType.md
---

# metaobject​Definition​By​Type

query

Requires `read_metaobject_definitions` access scope.

Retrieves a [`MetaobjectDefinition`](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition) by its type. The type serves as a unique identifier that distinguishes one metaobject definition from another.

## Arguments

* type

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The type of the metaobject definition to return.

***

## Possible returns

* Metaobject​Definition

  [Metaobject​Definition](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition)

  Defines the structure and configuration for a custom data type in Shopify. Each definition specifies the fields, validation rules, and capabilities that apply to all [`Metaobject`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Metaobject) entries created from it.

  The definition includes field definitions that determine what data to store, access controls for [the Shopify admin](https://shopify.dev/docs/apps/build/custom-data/permissions#admin-permissions) and [Storefront](https://shopify.dev/docs/apps/build/custom-data/permissions#storefront-permissions) APIs, and capabilities such as publishability and translatability. You can track which [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App) or [`StaffMember`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember) created the definition and optionally base it on a [`StandardMetaobjectDefinitionTemplate`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StandardMetaobjectDefinitionTemplate).

  * access

    [Metaobject​Access!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectAccess)

    non-null

    Access configuration for the metaobject definition.

  * capabilities

    [Metaobject​Capabilities!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectCapabilities)

    non-null

    The capabilities of the metaobject definition.

  * created​By​App

    [App!](https://shopify.dev/docs/api/admin-graphql/latest/objects/App)

    non-null

    The app used to create the metaobject definition.

  * created​By​Staff

    [Staff​Member](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember)

    The staff member who created the metaobject definition.

  * description

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The administrative description.

  * display​Name​Key

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The key of a field to reference as the display name for each object.

  * field​Definitions

    [\[Metaobject​Field​Definition!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectFieldDefinition)

    non-null

    The fields defined for this object type.

  * has​Thumbnail​Field

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether this metaobject definition has field whose type can visually represent a metaobject with the `thumbnailField`.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * metaobjects

    [Metaobject​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MetaobjectConnection)

    non-null

    A paginated connection to the metaobjects associated with the definition.

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

  * metaobjects​Count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The count of metaobjects created for the definition.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The human-readable name.

  * standard​Template

    [Standard​Metaobject​Definition​Template](https://shopify.dev/docs/api/admin-graphql/latest/objects/StandardMetaobjectDefinitionTemplate)

    The standard metaobject template associated with the definition.

  * type

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The type of the object definition. Defines the namespace of associated metafields.

***

## Examples

* ### metaobjectDefinitionByType reference
