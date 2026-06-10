---
title: metaobjectBulkDelete - GraphQL Admin
description: Asynchronously delete metaobjects and their associated metafields in bulk.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metaobjectBulkDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/metaobjectBulkDelete.md
---

# metaobject​Bulk​Delete

mutation

Requires `write_metaobjects` access scope.

Asynchronously delete metaobjects and their associated metafields in bulk.

## Arguments

* where

  [Metaobject​Bulk​Delete​Where​Condition!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetaobjectBulkDeleteWhereCondition)

  required

  Specifies the condition by which metaobjects are deleted. Exactly one field of input is required.

***

## Metaobject​Bulk​Delete​Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job that deletes the metaobjects.

* user​Errors

  [\[Metaobject​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetaobjectUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Delete metaobjects and their associated fields in bulk by IDs

  #### Description

  To delete metaobjects and their associated metafields in bulk, use the \`metaobjectBulkDelete\` mutation. Note that this operation happens asynchronously, so the mutation will return immediately with a \`job\` object. You can use the \`job\` object to check the status of the operation. The following example deletes 2 "Lookbook" metaobjects and their metafields using the IDs of the metaobjects to delete.

  #### Query

  ```graphql
  mutation DeleteMetaobjects($where: MetaobjectBulkDeleteWhereCondition!) {
    metaobjectBulkDelete(where: $where) {
      job {
        id
        done
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "where": {
      "ids": [
        "gid://shopify/Metaobject/515107504",
        "gid://shopify/Metaobject/129678104"
      ]
    }
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation DeleteMetaobjects($where: MetaobjectBulkDeleteWhereCondition!) { metaobjectBulkDelete(where: $where) { job { id done } } }",
   "variables": {
      "where": {
        "ids": [
          "gid://shopify/Metaobject/515107504",
          "gid://shopify/Metaobject/129678104"
        ]
      }
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
    mutation DeleteMetaobjects($where: MetaobjectBulkDeleteWhereCondition!) {
      metaobjectBulkDelete(where: $where) {
        job {
          id
          done
        }
      }
    }`,
    {
      variables: {
          "where": {
              "ids": [
                  "gid://shopify/Metaobject/515107504",
                  "gid://shopify/Metaobject/129678104"
              ]
          }
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
    mutation DeleteMetaobjects($where: MetaobjectBulkDeleteWhereCondition!) {
      metaobjectBulkDelete(where: $where) {
        job {
          id
          done
        }
      }
    }
  QUERY

  variables = {
    "where": {
      "ids": [
        "gid://shopify/Metaobject/515107504",
        "gid://shopify/Metaobject/129678104"
      ]
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation DeleteMetaobjects($where: MetaobjectBulkDeleteWhereCondition!) {
        metaobjectBulkDelete(where: $where) {
          job {
            id
            done
          }
        }
      }`,
      "variables": {
          "where": {
              "ids": [
                  "gid://shopify/Metaobject/515107504",
                  "gid://shopify/Metaobject/129678104"
              ]
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation DeleteMetaobjects($where: MetaobjectBulkDeleteWhereCondition!) {
    metaobjectBulkDelete(where: $where) {
      job {
        id
        done
      }
    }
  }' \
  --variables \
  '{
    "where": {
      "ids": [
        "gid://shopify/Metaobject/515107504",
        "gid://shopify/Metaobject/129678104"
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjectBulkDelete": {
      "job": {
        "id": "gid://shopify/Job/4d5319b7-71de-482e-b3c5-d11321c9ffca",
        "done": false
      }
    }
  }
  ```

* ### Delete metaobjects and their associated fields in bulk by type

  #### Description

  Along with using ids to delete metaobjects, you can also delete metaobjects by type. Note that you must use either \`ids\` or \`type\` but not both as they are mutually exclusive. The following example deletes all the "LookBook" metaobjects by using the "lookbook" \`type\` argument.

  #### Query

  ```graphql
  mutation DeleteMetaobjects($where: MetaobjectBulkDeleteWhereCondition!) {
    metaobjectBulkDelete(where: $where) {
      job {
        id
        done
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "where": {
      "type": "lookbook"
    }
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation DeleteMetaobjects($where: MetaobjectBulkDeleteWhereCondition!) { metaobjectBulkDelete(where: $where) { job { id done } } }",
   "variables": {
      "where": {
        "type": "lookbook"
      }
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
    mutation DeleteMetaobjects($where: MetaobjectBulkDeleteWhereCondition!) {
      metaobjectBulkDelete(where: $where) {
        job {
          id
          done
        }
      }
    }`,
    {
      variables: {
          "where": {
              "type": "lookbook"
          }
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
    mutation DeleteMetaobjects($where: MetaobjectBulkDeleteWhereCondition!) {
      metaobjectBulkDelete(where: $where) {
        job {
          id
          done
        }
      }
    }
  QUERY

  variables = {
    "where": {
      "type": "lookbook"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation DeleteMetaobjects($where: MetaobjectBulkDeleteWhereCondition!) {
        metaobjectBulkDelete(where: $where) {
          job {
            id
            done
          }
        }
      }`,
      "variables": {
          "where": {
              "type": "lookbook"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation DeleteMetaobjects($where: MetaobjectBulkDeleteWhereCondition!) {
    metaobjectBulkDelete(where: $where) {
      job {
        id
        done
      }
    }
  }' \
  --variables \
  '{
    "where": {
      "type": "lookbook"
    }
  }'
  ```

  #### Response

  ```json
  {
    "metaobjectBulkDelete": {
      "job": {
        "id": "gid://shopify/Job/e439ccf6-01c1-49df-9411-985def30b4f8",
        "done": false
      }
    }
  }
  ```

* ### metaobjectBulkDelete reference
