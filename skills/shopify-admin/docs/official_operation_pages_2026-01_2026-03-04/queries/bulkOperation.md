---
title: bulkOperation - GraphQL Admin
description: Returns a `BulkOperation` resource by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/bulkOperation'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/bulkOperation.md'
---

# bulk​Operation

query

Returns a `BulkOperation` resource by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the `BulkOperation` to return.

***

## Possible returns

* Bulk​Operation

  [Bulk​Operation](https://shopify.dev/docs/api/admin-graphql/latest/objects/BulkOperation)

  An asynchronous operation that exports large datasets or imports data in bulk. Create bulk operations using [bulkOperationRunQuery](https://shopify.dev/docs/api/admin-graphql/latest/mutations/bulkOperationRunQuery) to export data or [bulkOperationRunMutation](https://shopify.dev/docs/api/admin-graphql/latest/mutations/bulkOperationRunMutation) to import data.

  After creation, check the [`status`](https://shopify.dev/docs/api/admin-graphql/latest/objects/BulkOperation#field-BulkOperation.fields.status) field to track progress. When completed, the [`url`](https://shopify.dev/docs/api/admin-graphql/latest/objects/BulkOperation#field-BulkOperation.fields.url) field contains a link to download results in [JSONL](http://jsonlines.org/) format. The [`objectCount`](https://shopify.dev/docs/api/admin-graphql/latest/objects/BulkOperation#field-BulkOperation.fields.objectCount) field shows the running total of processed objects, while [`rootObjectCount`](https://shopify.dev/docs/api/admin-graphql/latest/objects/BulkOperation#field-BulkOperation.fields.rootObjectCount) tracks only root-level objects in nested queries.

  If an operation fails but retrieves partial data, then the [`partialDataUrl`](https://shopify.dev/docs/api/admin-graphql/latest/objects/BulkOperation#field-BulkOperation.fields.partialDataUrl) field provides access to incomplete results.

  ***

  **Note:** \<code>url\</code> and \<code>\<span class="PreventFireFoxApplyingGapToWBR">partial\<wbr/>Data\<wbr/>Url\</span>\</code> values expire after seven days.

  ***

  Learn more about [exporting](https://shopify.dev/docs/api/usage/bulk-operations/queries) and [importing](https://shopify.dev/docs/api/usage/bulk-operations/imports) data in bulk.

  * completed​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    When the bulk operation was successfully completed.

  * created​At

    [Date​Time!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    non-null

    When the bulk operation was created.

  * error​Code

    [Bulk​Operation​Error​Code](https://shopify.dev/docs/api/admin-graphql/latest/enums/BulkOperationErrorCode)

    Error code for failed operations.

  * file​Size

    [Unsigned​Int64](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    File size in bytes of the file in the `url` field.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * object​Count

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    A running count of all the objects processed. For example, when fetching all the products and their variants, this field counts both products and variants. This field can be used to track operation progress.

  * partial​Data​Url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    The URL that points to the partial or incomplete response data (in [JSONL](http://jsonlines.org/) format) that was returned by a failed operation. The URL expires 7 days after the operation fails. Returns `null` when there's no data available.

  * query

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    GraphQL query document specified in `bulkOperationRunQuery`.

  * root​Object​Count

    [Unsigned​Int64!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/UnsignedInt64)

    non-null

    A running count of all the objects that are processed at the root of the query. For example, when fetching all the products and their variants, this field only counts products. This field can be used to track operation progress.

  * status

    [Bulk​Operation​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/BulkOperationStatus)

    non-null

    Status of the bulk operation.

  * type

    [Bulk​Operation​Type!](https://shopify.dev/docs/api/admin-graphql/latest/enums/BulkOperationType)

    non-null

    The bulk operation's type.

  * url

    [URL](https://shopify.dev/docs/api/admin-graphql/latest/scalars/URL)

    The URL that points to the response data in [JSONL](http://jsonlines.org/) format. The URL expires 7 days after the operation completes.

***

## Examples

* ### bulkOperation reference
