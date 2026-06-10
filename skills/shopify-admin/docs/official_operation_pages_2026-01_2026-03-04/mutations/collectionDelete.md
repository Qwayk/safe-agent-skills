---
title: collectionDelete - GraphQL Admin
description: >-
  Deletes a collection and removes it permanently from the store. This operation
  cannot be undone and will remove the collection from all sales channels where
  it was published.


  For example, when merchants discontinue seasonal promotions or reorganize
  their catalog structure, they can delete outdated collections like "Back to
  School 2023" to keep their store organized.


  Use `CollectionDelete` to:

  - Remove outdated or unused collections from stores

  - Clean up collection structures during catalog reorganization

  - Implement collection management tools with deletion capabilities


  Products within the deleted collection remain in the store but are no longer
  grouped under that collection.


  Learn more about [collection
  management](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionDelete'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionDelete.md
---

# collection​Delete

mutation

Requires `write_products` access scope. Also: The store must not be on the Starter or Retail plans and user must have a permission to delete collection.

Deletes a collection and removes it permanently from the store. This operation cannot be undone and will remove the collection from all sales channels where it was published.

For example, when merchants discontinue seasonal promotions or reorganize their catalog structure, they can delete outdated collections like "Back to School 2023" to keep their store organized.

Use `CollectionDelete` to:

* Remove outdated or unused collections from stores
* Clean up collection structures during catalog reorganization
* Implement collection management tools with deletion capabilities

Products within the deleted collection remain in the store but are no longer grouped under that collection.

Learn more about [collection management](https://shopify.dev/docs/api/admin-graphql/latest/objects/Collection).

## Arguments

* input

  [Collection​Delete​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CollectionDeleteInput)

  required

  The collection to delete.

***

## Collection​Delete​Payload returns

* deleted​Collection​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the collection that was deleted. Returns `null` if the collection doesn't exist.

* shop

  [Shop!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Shop)

  non-null

  The shop associated with the collection.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Delete a collection

  #### Description

  Deletes the collection with the specified ID.

  #### Query

  ```graphql
  mutation collectionDelete($input: CollectionDeleteInput!) {
    collectionDelete(input: $input) {
      deletedCollectionId
      shop {
        id
        name
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
    "input": {
      "id": "gid://shopify/Collection/1009501285"
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
  "query": "mutation collectionDelete($input: CollectionDeleteInput!) { collectionDelete(input: $input) { deletedCollectionId shop { id name } userErrors { field message } } }",
   "variables": {
      "input": {
        "id": "gid://shopify/Collection/1009501285"
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
    mutation collectionDelete($input: CollectionDeleteInput!) {
      collectionDelete(input: $input) {
        deletedCollectionId
        shop {
          id
          name
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "id": "gid://shopify/Collection/1009501285"
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
    mutation collectionDelete($input: CollectionDeleteInput!) {
      collectionDelete(input: $input) {
        deletedCollectionId
        shop {
          id
          name
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "id": "gid://shopify/Collection/1009501285"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation collectionDelete($input: CollectionDeleteInput!) {
        collectionDelete(input: $input) {
          deletedCollectionId
          shop {
            id
            name
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "id": "gid://shopify/Collection/1009501285"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation collectionDelete($input: CollectionDeleteInput!) {
    collectionDelete(input: $input) {
      deletedCollectionId
      shop {
        id
        name
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "id": "gid://shopify/Collection/1009501285"
    }
  }'
  ```

  #### Response

  ```json
  {
    "collectionDelete": {
      "deletedCollectionId": "gid://shopify/Collection/1009501285",
      "shop": {
        "id": "gid://shopify/Shop/26371970",
        "name": "Snowdevil"
      },
      "userErrors": []
    }
  }
  ```

* ### Delete a collection that doesn't exist

  #### Description

  If a collection with the specified ID doesn't exist, then the mutation returns an error.

  #### Query

  ```graphql
  mutation collectionDelete($input: CollectionDeleteInput!) {
    collectionDelete(input: $input) {
      deletedCollectionId
      shop {
        id
        name
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
    "input": {
      "id": "gid://shopify/Collection/-1"
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
  "query": "mutation collectionDelete($input: CollectionDeleteInput!) { collectionDelete(input: $input) { deletedCollectionId shop { id name } userErrors { field message } } }",
   "variables": {
      "input": {
        "id": "gid://shopify/Collection/-1"
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
    mutation collectionDelete($input: CollectionDeleteInput!) {
      collectionDelete(input: $input) {
        deletedCollectionId
        shop {
          id
          name
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "id": "gid://shopify/Collection/-1"
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
    mutation collectionDelete($input: CollectionDeleteInput!) {
      collectionDelete(input: $input) {
        deletedCollectionId
        shop {
          id
          name
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "id": "gid://shopify/Collection/-1"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation collectionDelete($input: CollectionDeleteInput!) {
        collectionDelete(input: $input) {
          deletedCollectionId
          shop {
            id
            name
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "id": "gid://shopify/Collection/-1"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation collectionDelete($input: CollectionDeleteInput!) {
    collectionDelete(input: $input) {
      deletedCollectionId
      shop {
        id
        name
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "id": "gid://shopify/Collection/-1"
    }
  }'
  ```

  #### Response

  ```json
  {
    "collectionDelete": {
      "deletedCollectionId": null,
      "shop": {
        "id": "gid://shopify/Shop/26371970",
        "name": "Snowdevil"
      },
      "userErrors": [
        {
          "field": [
            "id"
          ],
          "message": "Collection does not exist"
        }
      ]
    }
  }
  ```

* ### Delete collection fails if call to CollectionsAccess returns false

  #### Description

  Restrict ability to delete a collection if the Shop is on Starter Plan.

  #### Query

  ```graphql
  mutation collectionDelete($input: CollectionDeleteInput!) {
    collectionDelete(input: $input) {
      deletedCollectionId
      shop {
        id
        name
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
    "input": {
      "id": "gid://shopify/Collection/1009501285"
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
  "query": "mutation collectionDelete($input: CollectionDeleteInput!) { collectionDelete(input: $input) { deletedCollectionId shop { id name } userErrors { field message } } }",
   "variables": {
      "input": {
        "id": "gid://shopify/Collection/1009501285"
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
    mutation collectionDelete($input: CollectionDeleteInput!) {
      collectionDelete(input: $input) {
        deletedCollectionId
        shop {
          id
          name
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "input": {
              "id": "gid://shopify/Collection/1009501285"
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
    mutation collectionDelete($input: CollectionDeleteInput!) {
      collectionDelete(input: $input) {
        deletedCollectionId
        shop {
          id
          name
        }
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "id": "gid://shopify/Collection/1009501285"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation collectionDelete($input: CollectionDeleteInput!) {
        collectionDelete(input: $input) {
          deletedCollectionId
          shop {
            id
            name
          }
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "input": {
              "id": "gid://shopify/Collection/1009501285"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation collectionDelete($input: CollectionDeleteInput!) {
    collectionDelete(input: $input) {
      deletedCollectionId
      shop {
        id
        name
      }
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "id": "gid://shopify/Collection/1009501285"
    }
  }'
  ```

  #### Response

  ```json
  {
    "collectionDelete": null
  }
  ```

* ### Deletes a custom collection

  #### Query

  ```graphql
  mutation CollectionDelete($id: ID!) {
    collectionDelete(input: {id: $id}) {
      deletedCollectionId
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
    "id": "gid://shopify/Collection/1009501285"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation CollectionDelete($id: ID!) { collectionDelete(input: {id: $id}) { deletedCollectionId userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/1009501285"
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
    mutation CollectionDelete($id: ID!) {
      collectionDelete(input: {id: $id}) {
        deletedCollectionId
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Collection/1009501285"
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
    mutation CollectionDelete($id: ID!) {
      collectionDelete(input: {id: $id}) {
        deletedCollectionId
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Collection/1009501285"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CollectionDelete($id: ID!) {
        collectionDelete(input: {id: $id}) {
          deletedCollectionId
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Collection/1009501285"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CollectionDelete($id: ID!) {
    collectionDelete(input: {id: $id}) {
      deletedCollectionId
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Collection/1009501285"
  }'
  ```

  #### Response

  ```json
  {
    "collectionDelete": {
      "deletedCollectionId": "gid://shopify/Collection/1009501285",
      "userErrors": []
    }
  }
  ```

* ### Removes a smart collection

  #### Query

  ```graphql
  mutation CollectionDelete($id: ID!) {
    collectionDelete(input: {id: $id}) {
      deletedCollectionId
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
    "id": "gid://shopify/Collection/1009501285"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation CollectionDelete($id: ID!) { collectionDelete(input: {id: $id}) { deletedCollectionId userErrors { field message } } }",
   "variables": {
      "id": "gid://shopify/Collection/1009501285"
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
    mutation CollectionDelete($id: ID!) {
      collectionDelete(input: {id: $id}) {
        deletedCollectionId
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/Collection/1009501285"
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
    mutation CollectionDelete($id: ID!) {
      collectionDelete(input: {id: $id}) {
        deletedCollectionId
        userErrors {
          field
          message
        }
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/Collection/1009501285"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CollectionDelete($id: ID!) {
        collectionDelete(input: {id: $id}) {
          deletedCollectionId
          userErrors {
            field
            message
          }
        }
      }`,
      "variables": {
          "id": "gid://shopify/Collection/1009501285"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CollectionDelete($id: ID!) {
    collectionDelete(input: {id: $id}) {
      deletedCollectionId
      userErrors {
        field
        message
      }
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/Collection/1009501285"
  }'
  ```

  #### Response

  ```json
  {
    "collectionDelete": {
      "deletedCollectionId": "gid://shopify/Collection/1009501285",
      "userErrors": []
    }
  }
  ```

* ### collectionDelete reference
