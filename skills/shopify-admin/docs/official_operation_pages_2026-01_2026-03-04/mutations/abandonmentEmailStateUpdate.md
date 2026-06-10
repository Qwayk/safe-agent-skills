---
title: abandonmentEmailStateUpdate - GraphQL Admin
description: Updates the email state value for an abandonment.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/abandonmentEmailStateUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/abandonmentEmailStateUpdate.md
---

# abandonment​Email​State​Update

mutation

Requires `write_marketing_events` access scope.

Deprecated. Use [abandonmentUpdateActivitiesDeliveryStatuses](https://shopify.dev/docs/api/admin-graphql/latest/mutations/abandonmentUpdateActivitiesDeliveryStatuses) instead.

Updates the email state value for an abandonment.

## Arguments

* email​Sent​At

  [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

  The date and time for when the email was sent, if that is the case.

* email​State

  [Abandonment​Email​State!](https://shopify.dev/docs/api/admin-graphql/latest/enums/AbandonmentEmailState)

  required

  The new email state of the abandonment.

* email​State​Change​Reason

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The reason why the email was or was not sent.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the abandonment that needs to be updated.

***

## Abandonment​Email​State​Update​Payload returns

* abandonment

  [Abandonment](https://shopify.dev/docs/api/admin-graphql/latest/objects/Abandonment)

  The updated abandonment.

* user​Errors

  [\[Abandonment​Email​State​Update​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/AbandonmentEmailStateUpdateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### abandonmentEmailStateUpdate reference
