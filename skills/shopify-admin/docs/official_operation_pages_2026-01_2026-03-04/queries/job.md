---
title: job - GraphQL Admin
description: >-
  Returns a Job resource by ID. Used to check the status of internal jobs and
  any applicable changes.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/job'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/job.md'
---

# job

query

Returns a Job resource by ID. Used to check the status of internal jobs and any applicable changes.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  ID of the job to query.

***

## Possible returns

* Job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  A job corresponds to some long running task that the client should poll for status.

  * done

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    This indicates if the job is still queued or has been run.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID that's returned when running an asynchronous mutation.

  * query

    [Query​Root](https://shopify.dev/docs/api/admin-graphql/latest/objects/QueryRoot)

    This field will only resolve once the job is done. Can be used to ask for object(s) that have been changed by the job.

***

## Examples

* ### Get the status of a queued collectionUpdate job

  #### Description

  The following query retrieves the status of a queued collectionUpdate job.

  #### Query

  ```graphql
  query {
    job(id: "gid://shopify/Job/dc9b2604-c73b-45c6-8942-e235bac987e8") {
      id
      done
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
  "query": "query { job(id: \"gid://shopify/Job/dc9b2604-c73b-45c6-8942-e235bac987e8\") { id done } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query {
      job(id: "gid://shopify/Job/dc9b2604-c73b-45c6-8942-e235bac987e8") {
        id
        done
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
    query {
      job(id: "gid://shopify/Job/dc9b2604-c73b-45c6-8942-e235bac987e8") {
        id
        done
      }
    }
  QUERY

  response = client.query(query: query)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: `query {
      job(id: "gid://shopify/Job/dc9b2604-c73b-45c6-8942-e235bac987e8") {
        id
        done
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    job(id: "gid://shopify/Job/dc9b2604-c73b-45c6-8942-e235bac987e8") {
      id
      done
    }
  }'
  ```

  #### Response

  ```json
  {
    "job": {
      "id": "gid://shopify/Job/dc9b2604-c73b-45c6-8942-e235bac987e8",
      "done": false
    }
  }
  ```
