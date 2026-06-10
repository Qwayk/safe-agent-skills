---
title: sellingPlanGroupUpdate - GraphQL Admin
description: Update a Selling Plan Group.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/sellingPlanGroupUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/sellingPlanGroupUpdate.md
---

# selling​Plan​Group​Update

mutation

Requires `write_products` access scope as well as any of `write_own_subscription_contracts`, `write_purchase_options` access scopes. Also: The user must have `manage_orders_information` permissions.

Update a Selling Plan Group.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The Selling Plan Group to update.

* input

  [Selling​Plan​Group​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SellingPlanGroupInput)

  required

  The properties of the Selling Plan Group to update.

***

## Selling​Plan​Group​Update​Payload returns

* deleted​Selling​Plan​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The IDs of the deleted Subscription Plans.

* selling​Plan​Group

  [Selling​Plan​Group](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroup)

  The updated Selling Plan Group.

* user​Errors

  [\[Selling​Plan​Group​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroupUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Update a selling plan group and its metafields

  #### Query

  ```graphql
  mutation sellingPlanGroupUpdate($id: ID!, $input: SellingPlanGroupInput!) {
    sellingPlanGroupUpdate(id: $id, input: $input) {
      sellingPlanGroup {
        id
        sellingPlans(first: 1) {
          edges {
            node {
              id
              metafields(first: 1) {
                edges {
                  node {
                    id
                    namespace
                    key
                    value
                  }
                }
              }
            }
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/SellingPlanGroup/964742479",
    "input": {
      "sellingPlansToUpdate": [
        {
          "id": "gid://shopify/SellingPlan/563068713",
          "metafields": [
            {
              "value": "waterproof",
              "type": "single_line_text_field",
              "key": "test_key",
              "namespace": "example-selling-plan"
            }
          ]
        }
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
  "query": "mutation sellingPlanGroupUpdate($id: ID!, $input: SellingPlanGroupInput!) { sellingPlanGroupUpdate(id: $id, input: $input) { sellingPlanGroup { id sellingPlans(first: 1) { edges { node { id metafields(first: 1) { edges { node { id namespace key value } } } } } } } userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/SellingPlanGroup/964742479",
      "input": {
        "sellingPlansToUpdate": [
          {
            "id": "gid://shopify/SellingPlan/563068713",
            "metafields": [
              {
                "value": "waterproof",
                "type": "single_line_text_field",
                "key": "test_key",
                "namespace": "example-selling-plan"
              }
            ]
          }
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
    mutation sellingPlanGroupUpdate($id: ID!, $input: SellingPlanGroupInput!) {
      sellingPlanGroupUpdate(id: $id, input: $input) {
        sellingPlanGroup {
          id
          sellingPlans(first: 1) {
            edges {
              node {
                id
                metafields(first: 1) {
                  edges {
                    node {
                      id
                      namespace
                      key
                      value
                    }
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/SellingPlanGroup/964742479",
          "input": {
              "sellingPlansToUpdate": [
                  {
                      "id": "gid://shopify/SellingPlan/563068713",
                      "metafields": [
                          {
                              "value": "waterproof",
                              "type": "single_line_text_field",
                              "key": "test_key",
                              "namespace": "example-selling-plan"
                          }
                      ]
                  }
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
    mutation sellingPlanGroupUpdate($id: ID!, $input: SellingPlanGroupInput!) {
      sellingPlanGroupUpdate(id: $id, input: $input) {
        sellingPlanGroup {
          id
          sellingPlans(first: 1) {
            edges {
              node {
                id
                metafields(first: 1) {
                  edges {
                    node {
                      id
                      namespace
                      key
                      value
                    }
                  }
                }
              }
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/SellingPlanGroup/964742479",
    "input": {
      "sellingPlansToUpdate": [
        {
          "id": "gid://shopify/SellingPlan/563068713",
          "metafields": [
            {
              "value": "waterproof",
              "type": "single_line_text_field",
              "key": "test_key",
              "namespace": "example-selling-plan"
            }
          ]
        }
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
      "query": `mutation sellingPlanGroupUpdate($id: ID!, $input: SellingPlanGroupInput!) {
        sellingPlanGroupUpdate(id: $id, input: $input) {
          sellingPlanGroup {
            id
            sellingPlans(first: 1) {
              edges {
                node {
                  id
                  metafields(first: 1) {
                    edges {
                      node {
                        id
                        namespace
                        key
                        value
                      }
                    }
                  }
                }
              }
            }
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/SellingPlanGroup/964742479",
          "input": {
              "sellingPlansToUpdate": [
                  {
                      "id": "gid://shopify/SellingPlan/563068713",
                      "metafields": [
                          {
                              "value": "waterproof",
                              "type": "single_line_text_field",
                              "key": "test_key",
                              "namespace": "example-selling-plan"
                          }
                      ]
                  }
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
  'mutation sellingPlanGroupUpdate($id: ID!, $input: SellingPlanGroupInput!) {
    sellingPlanGroupUpdate(id: $id, input: $input) {
      sellingPlanGroup {
        id
        sellingPlans(first: 1) {
          edges {
            node {
              id
              metafields(first: 1) {
                edges {
                  node {
                    id
                    namespace
                    key
                    value
                  }
                }
              }
            }
          }
        }
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/SellingPlanGroup/964742479",
    "input": {
      "sellingPlansToUpdate": [
        {
          "id": "gid://shopify/SellingPlan/563068713",
          "metafields": [
            {
              "value": "waterproof",
              "type": "single_line_text_field",
              "key": "test_key",
              "namespace": "example-selling-plan"
            }
          ]
        }
      ]
    }
  }'
  ```

  #### Response

  ```json
  {
    "sellingPlanGroupUpdate": {
      "sellingPlanGroup": {
        "id": "gid://shopify/SellingPlanGroup/964742479",
        "sellingPlans": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/SellingPlan/563068713",
                "metafields": {
                  "edges": [
                    {
                      "node": {
                        "id": "gid://shopify/Metafield/616145134",
                        "namespace": "example-selling-plan",
                        "key": "test_key",
                        "value": "waterproof"
                      }
                    }
                  ]
                }
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### sellingPlanGroupUpdate reference
