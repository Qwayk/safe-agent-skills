---
title: appRevokeAccessScopes - GraphQL Admin
description: >-
  Revokes previously granted access scopes from an app installation, allowing
  merchants to reduce an app's permissions without completely uninstalling it.
  This provides granular control over what data and functionality apps can
  access.


  For example, if a merchant no longer wants an app to access customer
  information but still wants to use its inventory features, they can revoke the
  customer-related scopes while keeping inventory permissions active.


  Use the `appRevokeAccessScopes` mutation to:

  - Remove specific permissions from installed apps

  - Maintain app functionality while minimizing data exposure


  The mutation returns details about which scopes were successfully revoked and
  any errors that prevented certain permissions from being removed.


  Learn more about [managing app
  permissions](https://shopify.dev/docs/apps/build/authentication-authorization/app-installation/manage-access-scopes#revoke-granted-scopes-dynamically).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/appRevokeAccessScopes
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/appRevokeAccessScopes.md
---

# app​Revoke​Access​Scopes

mutation

Requires This mutation can only be run on the current app.

Revokes previously granted access scopes from an app installation, allowing merchants to reduce an app's permissions without completely uninstalling it. This provides granular control over what data and functionality apps can access.

For example, if a merchant no longer wants an app to access customer information but still wants to use its inventory features, they can revoke the customer-related scopes while keeping inventory permissions active.

Use the `appRevokeAccessScopes` mutation to:

* Remove specific permissions from installed apps
* Maintain app functionality while minimizing data exposure

The mutation returns details about which scopes were successfully revoked and any errors that prevented certain permissions from being removed.

Learn more about [managing app permissions](https://shopify.dev/docs/apps/build/authentication-authorization/app-installation/manage-access-scopes#revoke-granted-scopes-dynamically).

## Arguments

* scopes

  [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The list of scope handles to revoke.

***

## App​Revoke​Access​Scopes​Payload returns

* revoked

  [\[Access​Scope!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/AccessScope)

  The list of scope handles that have been revoked.

* user​Errors

  [\[App​Revoke​Access​Scopes​App​Revoke​Scope​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppRevokeAccessScopesAppRevokeScopeError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### appRevokeAccessScopes reference
