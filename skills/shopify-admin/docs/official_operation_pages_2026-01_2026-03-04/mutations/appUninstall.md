---
title: appUninstall - GraphQL Admin
description: >-
  Uninstalls an
  [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App) from a
  shop. Apps use this mutation to uninstall themselves programmatically,
  removing their
  [`AppInstallation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation)
  from the merchant's store.


  When an app uninstalls, Shopify automatically performs cleanup tasks, such as
  deleting
  [`WebhookSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebhookSubscription)
  objects and [admin
  links](https://shopify.dev/docs/apps/build/admin/admin-links) associated with
  the app.


  Learn more about [app lifecycle
  management](https://shopify.dev/docs/apps/build/authentication-authorization/app-installation/uninstall-app-api-request).


  > Caution:

  > This action is irreversible. You can't restore an uninstalled app's
  configuration or data. Before you uninstall an app, make sure that you no
  longer need to make API calls for the store in which the app has been
  installed.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/appUninstall'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/appUninstall.md'
---

# app​Uninstall

mutation

Requires This mutation can only be used by apps to uninstall themselves.

Uninstalls an [`App`](https://shopify.dev/docs/api/admin-graphql/latest/objects/App) from a shop. Apps use this mutation to uninstall themselves programmatically, removing their [`AppInstallation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation) from the merchant's store.

When an app uninstalls, Shopify automatically performs cleanup tasks, such as deleting [`WebhookSubscription`](https://shopify.dev/docs/api/admin-graphql/latest/objects/WebhookSubscription) objects and [admin links](https://shopify.dev/docs/apps/build/admin/admin-links) associated with the app.

Learn more about [app lifecycle management](https://shopify.dev/docs/apps/build/authentication-authorization/app-installation/uninstall-app-api-request).

***

**Caution:** This action is irreversible. You can\&#39;t restore an uninstalled app\&#39;s configuration or data. Before you uninstall an app, make sure that you no longer need to make API calls for the store in which the app has been installed.

***

## App​Uninstall​Payload returns

* app

  [App](https://shopify.dev/docs/api/admin-graphql/latest/objects/App)

  The uninstalled app.

* user​Errors

  [\[App​Uninstall​App​Uninstall​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AppUninstallAppUninstallError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### appUninstall reference
