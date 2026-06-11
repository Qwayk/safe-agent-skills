---
title: inventorySetScheduledChanges - GraphQL Admin
description: >-
  Set up scheduled changes of inventory items.


  > Caution:

  > As of 2026-01, this mutation supports an optional idempotency key using the
  `@idempotent` directive.

  > As of 2026-04, the idempotency key is required and must be provided using
  the `@idempotent` directive.

  > For more information, see the [idempotency
  documentation](https://shopify.dev/docs/api/usage/idempotent-requests).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventorySetScheduledChanges
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventorySetScheduledChanges.md
---

# inventory​Set​Scheduled​Changes

mutation

Requires `write_inventory` access scope. Also: The user must have permission to update an inventory.

Deprecated. Scheduled changes will be phased out in a future version.

Set up scheduled changes of inventory items.

***

**Caution:** As of 2026-01, this mutation supports an optional idempotency key using the \<code>@idempotent\</code> directive. As of 2026-04, the idempotency key is required and must be provided using the \<code>@idempotent\</code> directive. For more information, see the \<a href="https://shopify.dev/docs/api/usage/idempotent-requests">idempotency documentation\</a>.

***

## Arguments

* input

  [Inventory​Set​Scheduled​Changes​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/InventorySetScheduledChangesInput)

  required

  The input fields for setting up scheduled changes of inventory items.

***

## Inventory​Set​Scheduled​Changes​Payload returns

* scheduled​Changes

  [\[Inventory​Scheduled​Change!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryScheduledChange)

  The scheduled changes that were created.

* user​Errors

  [\[Inventory​Set​Scheduled​Changes​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventorySetScheduledChangesUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Sets scheduled changes with idempotency enabled (2026-01 onwards)

  #### Query

  ```graphql
  mutation inventorySetScheduledChanges($input: InventorySetScheduledChangesInput!, $idempotencyKey: String!) {
    inventorySetScheduledChanges(input: $input) @idempotent(key: $idempotencyKey) {
      scheduledChanges {
        expectedAt
        fromName
        toName
        quantity
        ledgerDocumentUri
      }
      userErrors {
        field
        message
        code
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "reason": "correction",
      "items": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "ledgerDocumentUri": "app://ledger/1",
          "scheduledChanges": [
            {
              "expectedAt": "2023-09-07T15:50:00Z",
              "fromName": "incoming",
              "toName": "reserved"
            }
          ]
        }
      ],
      "referenceDocumentUri": "app://ledger/1"
    },
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation inventorySetScheduledChanges($input: InventorySetScheduledChangesInput!, $idempotencyKey: String!) { inventorySetScheduledChanges(input: $input) @idempotent(key: $idempotencyKey) { scheduledChanges { expectedAt fromName toName quantity ledgerDocumentUri } userErrors { field message code } } }",
   "variables": {
      "input": {
        "reason": "correction",
        "items": [
          {
            "inventoryItemId": "gid://shopify/InventoryItem/30322695",
            "locationId": "gid://shopify/Location/124656943",
            "ledgerDocumentUri": "app://ledger/1",
            "scheduledChanges": [
              {
                "expectedAt": "2023-09-07T15:50:00Z",
                "fromName": "incoming",
                "toName": "reserved"
              }
            ]
          }
        ],
        "referenceDocumentUri": "app://ledger/1"
      },
      "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
    }
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation inventorySetScheduledChanges($input: InventorySetScheduledChangesInput!, $idempotencyKey: String!) {
      inventorySetScheduledChanges(input: $input) @idempotent(key: $idempotencyKey) {
        scheduledChanges {
          expectedAt
          fromName
          toName
          quantity
          ledgerDocumentUri
        }
        userErrors {
          field
          message
          code
        }
      }
    }`,
    {
      variables: {
          "input": {
              "reason": "correction",
              "items": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "ledgerDocumentUri": "app://ledger/1",
                      "scheduledChanges": [
                          {
                              "expectedAt": "2023-09-07T15:50:00Z",
                              "fromName": "incoming",
                              "toName": "reserved"
                          }
                      ]
                  }
              ],
              "referenceDocumentUri": "app://ledger/1"
          },
          "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
      },
    },
    );
    const json = await response.json();
    return json.data;
  }
  ```

  #### Ruby

  ```ruby
  session = ShopifyAPI::Auth::Session.new(
    shop: "your-development-store.myshopify.com",
    access_token: access_token
  )
  client = ShopifyAPI::Clients::Graphql::Admin.new(
    session: session
  )

  query = <<~QUERY
    mutation inventorySetScheduledChanges($input: InventorySetScheduledChangesInput!, $idempotencyKey: String!) {
      inventorySetScheduledChanges(input: $input) @idempotent(key: $idempotencyKey) {
        scheduledChanges {
          expectedAt
          fromName
          toName
          quantity
          ledgerDocumentUri
        }
        userErrors {
          field
          message
          code
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "reason": "correction",
      "items": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "ledgerDocumentUri": "app://ledger/1",
          "scheduledChanges": [
            {
              "expectedAt": "2023-09-07T15:50:00Z",
              "fromName": "incoming",
              "toName": "reserved"
            }
          ]
        }
      ],
      "referenceDocumentUri": "app://ledger/1"
    },
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation inventorySetScheduledChanges($input: InventorySetScheduledChangesInput!, $idempotencyKey: String!) {
        inventorySetScheduledChanges(input: $input) @idempotent(key: $idempotencyKey) {
          scheduledChanges {
            expectedAt
            fromName
            toName
            quantity
            ledgerDocumentUri
          }
          userErrors {
            field
            message
            code
          }
        }
      }`,
      "variables": {
          "input": {
              "reason": "correction",
              "items": [
                  {
                      "inventoryItemId": "gid://shopify/InventoryItem/30322695",
                      "locationId": "gid://shopify/Location/124656943",
                      "ledgerDocumentUri": "app://ledger/1",
                      "scheduledChanges": [
                          {
                              "expectedAt": "2023-09-07T15:50:00Z",
                              "fromName": "incoming",
                              "toName": "reserved"
                          }
                      ]
                  }
              ],
              "referenceDocumentUri": "app://ledger/1"
          },
          "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation inventorySetScheduledChanges($input: InventorySetScheduledChangesInput!, $idempotencyKey: String!) {
    inventorySetScheduledChanges(input: $input) @idempotent(key: $idempotencyKey) {
      scheduledChanges {
        expectedAt
        fromName
        toName
        quantity
        ledgerDocumentUri
      }
      userErrors {
        field
        message
        code
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "reason": "correction",
      "items": [
        {
          "inventoryItemId": "gid://shopify/InventoryItem/30322695",
          "locationId": "gid://shopify/Location/124656943",
          "ledgerDocumentUri": "app://ledger/1",
          "scheduledChanges": [
            {
              "expectedAt": "2023-09-07T15:50:00Z",
              "fromName": "incoming",
              "toName": "reserved"
            }
          ]
        }
      ],
      "referenceDocumentUri": "app://ledger/1"
    },
    "idempotencyKey": "550e8400-e29b-41d4-a716-446655440000"
  }'
  ```

  #### Response

  ```json
  {
    "inventorySetScheduledChanges": {
      "scheduledChanges": [
        {
          "expectedAt": "2023-09-07T15:50:00Z",
          "fromName": "incoming",
          "toName": "reserved",
          "quantity": 0,
          "ledgerDocumentUri": "app://ledger/1"
        }
      ],
      "userErrors": []
    }
  }
  ```

* ### inventorySetScheduledChanges reference
