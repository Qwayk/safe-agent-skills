---
title: deliveryPromiseParticipantsUpdate - GraphQL Admin
description: >-
  Updates the delivery promise participants by adding or removing owners based
  on a branded promise handle.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliveryPromiseParticipantsUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliveryPromiseParticipantsUpdate.md
---

# delivery​Promise​Participants​Update

mutation

Requires `write_delivery_promises` access scope.

Updates the delivery promise participants by adding or removing owners based on a branded promise handle.

## Arguments

* branded​Promise​Handle

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The branded promise handle to update the delivery promise participants for.

* owners​To​Add

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  Default:\[]

  The owners to add to the delivery promise participants.

* owners​To​Remove

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  Default:\[]

  The owners to remove from the delivery promise participants.

***

## Delivery​Promise​Participants​Update​Payload returns

* promise​Participants

  [\[Delivery​Promise​Participant!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryPromiseParticipant)

  The promise participants that were added.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### deliveryPromiseParticipantsUpdate reference
