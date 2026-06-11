---
title: backupRegionUpdate - GraphQL Admin
description: >-
  Update the backup region that is used when we have no better signal of what
  region a buyer is in.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/backupRegionUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/backupRegionUpdate.md
---

# backup​Region​Update

mutation

Requires `read_markets` for queries and both `read_markets` as well as `write_markets` for mutations.

Update the backup region that is used when we have no better signal of what region a buyer is in.

## Arguments

* region

  [Backup​Region​Update​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/BackupRegionUpdateInput)

  Optional input representing the region to be updated. If not provided, the existing regions remain unchanged.

***

## Backup​Region​Update​Payload returns

* backup​Region

  [Market​Region](https://shopify.dev/docs/api/admin-graphql/latest/interfaces/MarketRegion)

  Returns the updated backup region.

* user​Errors

  [\[Market​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### backupRegionUpdate reference
