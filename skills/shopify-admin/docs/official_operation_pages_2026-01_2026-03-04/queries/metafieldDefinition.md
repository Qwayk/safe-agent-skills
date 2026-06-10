---
title: metafieldDefinition - GraphQL Admin
description: >-
  Retrieves a
  [`MetafieldDefinition`](/docs/api/admin-graphql/2026-01/objects/MetafieldDefinition)
  by its identifier. You can identify a definition using either its owner type,
  namespace, and key, or its global ID.


  Use this query to inspect a definition's configuration, including its data
  type, validations, access settings, and the count of
  [metafields](/docs/api/admin-graphql/2026-01/objects/Metafield) using it.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/metafieldDefinition
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/metafieldDefinition.md
---

# metafield​Definition

query

Requires API client to have access to the resource type associated with the metafield definition.

Retrieves a [`MetafieldDefinition`](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/MetafieldDefinition) by its identifier. You can identify a definition using either its owner type, namespace, and key, or its global ID.

Use this query to inspect a definition's configuration, including its data type, validations, access settings, and the count of [metafields](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/Metafield) using it.

## Arguments

* identifier

  [Metafield​Definition​Identifier​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MetafieldDefinitionIdentifierInput)

  The identifier of the MetafieldDefinition to return.

* id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  Deprecated

***

## Possible returns

* Metafield​Definition

  [Metafield​Definition](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinition)

  Defines the structure, validation rules, and permissions for [`Metafield`](https://shopify.dev/docs/api/admin-graphql/2026-01/objects/Metafield) objects attached to a specific owner type. Each definition establishes a schema that metafields must follow, including the data type and validation constraints.

  The definition controls access permissions across different APIs, determines whether the metafield can be used for filtering or as a collection condition, and can be constrained to specific resource subtypes.

  * access

    [Metafield​Access!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldAccess)

    non-null

    The access settings associated with the metafield definition.

  * capabilities

    [Metafield​Capabilities!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldCapabilities)

    non-null

    The capabilities of the metafield definition.

  * constraints

    [Metafield​Definition​Constraints](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinitionConstraints)

    The [constraints](https://shopify.dev/apps/build/custom-data/metafields/conditional-metafield-definitions) that determine what subtypes of resources a metafield definition applies to.

  * description

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The description of the metafield definition.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * key

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The unique identifier for the metafield definition within its namespace.

  * metafields

    [Metafield​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/MetafieldConnection)

    non-null

    The metafields that belong to the metafield definition.

    * validation​Status

      [Metafield​Validation​Status](https://shopify.dev/docs/api/admin-graphql/latest/enums/MetafieldValidationStatus)

      Default:ANY

      ### Arguments

      Returns the metafields filtered by the validation status.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * metafields​Count

    [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    non-null

    The count of the metafields that belong to the metafield definition.

    * validation​Status

      [Metafield​Validation​Status](https://shopify.dev/docs/api/admin-graphql/latest/enums/MetafieldValidationStatus)

      ### Arguments

      The current validation status.

    ***

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The human-readable name of the metafield definition.

  * namespace

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The container for a group of metafields that the metafield definition is associated with.

  * owner​Type

    [Metafield​Owner​Type!](https://shopify.dev/docs/api/admin-graphql/latest/enums/MetafieldOwnerType)

    non-null

    The resource type that the metafield definition is attached to.

  * pinned​Position

    [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    The position of the metafield definition in the pinned list.

  * standard​Template

    [Standard​Metafield​Definition​Template](https://shopify.dev/docs/api/admin-graphql/latest/objects/StandardMetafieldDefinitionTemplate)

    The standard metafield definition template associated with the metafield definition.

  * type

    [Metafield​Definition​Type!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinitionType)

    non-null

    The type of data that each of the metafields that belong to the metafield definition will store. Refer to the list of [supported types](https://shopify.dev/apps/metafields/types).

  * use​As​Collection​Condition

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the metafield definition can be used as a collection condition.

  * validations

    [\[Metafield​Definition​Validation!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/MetafieldDefinitionValidation)

    non-null

    A list of [validation options](https://shopify.dev/apps/metafields/definitions/validation) for the metafields that belong to the metafield definition. For example, for a metafield definition with the type `date`, you can set a minimum date validation so that each of the metafields that belong to it can only store dates after the specified minimum.

  * validation​Status

    [Metafield​Definition​Validation​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/MetafieldDefinitionValidationStatus)

    non-null

    The validation status for the metafields that belong to the metafield definition.

***

## Examples

* ### Retrieve a count of a resource's metafields.

  #### Query

  ```graphql
  query MetafieldsCount($metafieldDefinitionId: ID!) {
    metafieldDefinition(id: $metafieldDefinitionId) {
      id
      metafieldsCount
    }
  }
  ```

  #### Variables

  ```json
  {
    "metafieldDefinitionId": "gid://shopify/MetafieldDefinition/1071456212"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query MetafieldsCount($metafieldDefinitionId: ID!) { metafieldDefinition(id: $metafieldDefinitionId) { id metafieldsCount } }",
   "variables": {
      "metafieldDefinitionId": "gid://shopify/MetafieldDefinition/1071456212"
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
    query MetafieldsCount($metafieldDefinitionId: ID!) {
      metafieldDefinition(id: $metafieldDefinitionId) {
        id
        metafieldsCount
      }
    }`,
    {
      variables: {
          "metafieldDefinitionId": "gid://shopify/MetafieldDefinition/1071456212"
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
    query MetafieldsCount($metafieldDefinitionId: ID!) {
      metafieldDefinition(id: $metafieldDefinitionId) {
        id
        metafieldsCount
      }
    }
  QUERY

  variables = {
    "metafieldDefinitionId": "gid://shopify/MetafieldDefinition/1071456212"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query MetafieldsCount($metafieldDefinitionId: ID!) {
        metafieldDefinition(id: $metafieldDefinitionId) {
          id
          metafieldsCount
        }
      }`,
      "variables": {
          "metafieldDefinitionId": "gid://shopify/MetafieldDefinition/1071456212"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query MetafieldsCount($metafieldDefinitionId: ID!) {
    metafieldDefinition(id: $metafieldDefinitionId) {
      id
      metafieldsCount
    }
  }' \
  --variables \
  '{
    "metafieldDefinitionId": "gid://shopify/MetafieldDefinition/1071456212"
  }'
  ```

  #### Response

  ```json
  {
    "metafieldDefinition": {
      "id": "gid://shopify/MetafieldDefinition/1071456212",
      "metafieldsCount": 0
    }
  }
  ```

* ### Retrieve a metafield definition

  #### Description

  To retrieve a single metafield definition, use the \`metafieldDefinition\` query with its ID. The following example shows how to retrieve a metafield definition.

  #### Query

  ```graphql
  query {
    metafieldDefinition(id: "gid://shopify/MetafieldDefinition/1071456211") {
      name
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
  "query": "query { metafieldDefinition(id: \"gid://shopify/MetafieldDefinition/1071456211\") { name } }"
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
      metafieldDefinition(id: "gid://shopify/MetafieldDefinition/1071456211") {
        name
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
      metafieldDefinition(id: "gid://shopify/MetafieldDefinition/1071456211") {
        name
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
      metafieldDefinition(id: "gid://shopify/MetafieldDefinition/1071456211") {
        name
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    metafieldDefinition(id: "gid://shopify/MetafieldDefinition/1071456211") {
      name
    }
  }'
  ```

  #### Response

  ```json
  {
    "metafieldDefinition": {
      "name": "ingredients"
    }
  }
  ```
