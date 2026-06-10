---
title: companyContactRevokeRoles - GraphQL Admin
description: Revokes roles on a company contact.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyContactRevokeRoles
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyContactRevokeRoles.md
---

# company​Contact​Revoke​Roles

mutation

Requires `write_customers` access scope or `write_companies` access scope. Also: The API client must be installed on a Shopify Plus store.

Revokes roles on a company contact.

## Arguments

* company​Contact​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The contact whose roles are being revoked.

* revoke​All

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Flag to revoke all roles on the contact.

* role​Assignment​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The current role assignment IDs to revoke.

***

## Company​Contact​Revoke​Roles​Payload returns

* revoked​Role​Assignment​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  A list of role assignment IDs that were removed from the company contact.

* user​Errors

  [\[Business​Customer​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessCustomerUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### companyContactRevokeRoles reference
