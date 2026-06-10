---
title: marketingActivitiesDeleteAllExternal - GraphQL Admin
description: >-
  Deletes all external marketing activities. Deletion is performed by a
  background job, as it may take a bit of time to complete if a large number of
  activities are to be deleted. Attempting to create or modify external
  activities before the job has completed will result in the
  create/update/upsert mutation returning an error.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketingActivitiesDeleteAllExternal
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/marketingActivitiesDeleteAllExternal.md
---

# marketing​Activities​Delete​All​External

mutation

Requires `write_marketing_events` access scope.

Deletes all external marketing activities. Deletion is performed by a background job, as it may take a bit of time to complete if a large number of activities are to be deleted. Attempting to create or modify external activities before the job has completed will result in the create/update/upsert mutation returning an error.

## Marketing​Activities​Delete​All​External​Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job that performs the deletion. The status of the job may be used to determine when it's safe again to create new activities.

* user​Errors

  [\[Marketing​Activity​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MarketingActivityUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Enqueues a job to delete all external activities

  #### Query

  ```graphql
  mutation marketingActivitiesDeleteAllExternal {
    marketingActivitiesDeleteAllExternal {
      job {
        id
      }
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
  "query": "mutation marketingActivitiesDeleteAllExternal { marketingActivitiesDeleteAllExternal { job { id } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    mutation marketingActivitiesDeleteAllExternal {
      marketingActivitiesDeleteAllExternal {
        job {
          id
        }
      }
    }`,
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
    mutation marketingActivitiesDeleteAllExternal {
      marketingActivitiesDeleteAllExternal {
        job {
          id
        }
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `mutation marketingActivitiesDeleteAllExternal {
      marketingActivitiesDeleteAllExternal {
        job {
          id
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation marketingActivitiesDeleteAllExternal {
    marketingActivitiesDeleteAllExternal {
      job {
        id
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "marketingActivitiesDeleteAllExternal": {
      "job": {
        "id": "gid://shopify/Job/d778213f-460c-467c-b35b-f040b7812c82"
      }
    }
  }
  ```

* ### marketingActivitiesDeleteAllExternal reference
