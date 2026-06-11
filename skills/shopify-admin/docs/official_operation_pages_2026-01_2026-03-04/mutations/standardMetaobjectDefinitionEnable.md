---
title: standardMetaobjectDefinitionEnable - GraphQL Admin
description: Enables the specified standard metaobject definition from its template.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/standardMetaobjectDefinitionEnable
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/standardMetaobjectDefinitionEnable.md
---

# standard​Metaobject​Definition​Enable

mutation

Requires `write_metaobject_definitions` access scope.

Enables the specified standard metaobject definition from its template.

## Arguments

* type

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The type of the metaobject definition to enable.

***

## Standard​Metaobject​Definition​Enable​Payload returns

* metaobject​Definition

  [Metaobject​Definition](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectDefinition)

  The metaobject definition that was enabled using the standard template.

* user​Errors

  [\[Metaobject​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### standardMetaobjectDefinitionEnable reference
