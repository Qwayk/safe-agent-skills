---
title: customerUpdate - GraphQL Admin
description: >-
  Updates a
  [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)'s
  attributes including personal information and [`tax
  exemptions`](https://shopify.dev/docs/api/admin-graphql/latest/enums/TaxExemption).


  Apps using protected customer data must meet Shopify's [protected customer
  data
  requirements](https://shopify.dev/docs/apps/launch/protected-customer-data#requirements).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerUpdate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerUpdate.md
---

# customer​Update

mutation

Requires `write_customers` access scope.

Updates a [`Customer`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)'s attributes including personal information and [`tax exemptions`](https://shopify.dev/docs/api/admin-graphql/latest/enums/TaxExemption).

Apps using protected customer data must meet Shopify's [protected customer data requirements](https://shopify.dev/docs/apps/launch/protected-customer-data#requirements).

## Arguments

* input

  [Customer​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CustomerInput)

  required

  Provides updated fields for the customer. To set marketing consent, use the `customerEmailMarketingConsentUpdate` or `customerSmsMarketingConsentUpdate` mutations instead.

***

## Customer​Update​Payload returns

* customer

  [Customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

  The updated customer.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a new metafield and update another on an existing customer

  #### Description

  Create a new metafield \`my\_field.nickname\` and update an existing metafield \`my\_field.pronouns\` on a specific customer. Alternatively, refer to the \[metafieldsSet]\(https://shopify.dev/api/admin-graphql/latest/mutations/metafieldsset) mutation to create and/or update metafields on customer resources.

  #### Query

  ```graphql
  mutation updateCustomerMetafields($input: CustomerInput!) {
    customerUpdate(input: $input) {
      customer {
        id
        metafields(first: 3) {
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
      userErrors {
        message
        field
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "nickname",
          "type": "single_line_text_field",
          "value": "rob"
        },
        {
          "id": "gid://shopify/Metafield/1069230189",
          "value": "they/them"
        }
      ],
      "id": "gid://shopify/Customer/1018520244"
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
  "query": "mutation updateCustomerMetafields($input: CustomerInput!) { customerUpdate(input: $input) { customer { id metafields(first: 3) { edges { node { id namespace key value } } } } userErrors { message field } } }",
   "variables": {
      "input": {
        "metafields": [
          {
            "namespace": "my_field",
            "key": "nickname",
            "type": "single_line_text_field",
            "value": "rob"
          },
          {
            "id": "gid://shopify/Metafield/1069230189",
            "value": "they/them"
          }
        ],
        "id": "gid://shopify/Customer/1018520244"
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
    mutation updateCustomerMetafields($input: CustomerInput!) {
      customerUpdate(input: $input) {
        customer {
          id
          metafields(first: 3) {
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
        userErrors {
          message
          field
        }
      }
    }`,
    {
      variables: {
          "input": {
              "metafields": [
                  {
                      "namespace": "my_field",
                      "key": "nickname",
                      "type": "single_line_text_field",
                      "value": "rob"
                  },
                  {
                      "id": "gid://shopify/Metafield/1069230189",
                      "value": "they/them"
                  }
              ],
              "id": "gid://shopify/Customer/1018520244"
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
    mutation updateCustomerMetafields($input: CustomerInput!) {
      customerUpdate(input: $input) {
        customer {
          id
          metafields(first: 3) {
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
        userErrors {
          message
          field
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "nickname",
          "type": "single_line_text_field",
          "value": "rob"
        },
        {
          "id": "gid://shopify/Metafield/1069230189",
          "value": "they/them"
        }
      ],
      "id": "gid://shopify/Customer/1018520244"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation updateCustomerMetafields($input: CustomerInput!) {
        customerUpdate(input: $input) {
          customer {
            id
            metafields(first: 3) {
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
          userErrors {
            message
            field
          }
        }
      }`,
      "variables": {
          "input": {
              "metafields": [
                  {
                      "namespace": "my_field",
                      "key": "nickname",
                      "type": "single_line_text_field",
                      "value": "rob"
                  },
                  {
                      "id": "gid://shopify/Metafield/1069230189",
                      "value": "they/them"
                  }
              ],
              "id": "gid://shopify/Customer/1018520244"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation updateCustomerMetafields($input: CustomerInput!) {
    customerUpdate(input: $input) {
      customer {
        id
        metafields(first: 3) {
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
      userErrors {
        message
        field
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "metafields": [
        {
          "namespace": "my_field",
          "key": "nickname",
          "type": "single_line_text_field",
          "value": "rob"
        },
        {
          "id": "gid://shopify/Metafield/1069230189",
          "value": "they/them"
        }
      ],
      "id": "gid://shopify/Customer/1018520244"
    }
  }'
  ```

  #### Response

  ```json
  {
    "customerUpdate": {
      "customer": {
        "id": "gid://shopify/Customer/1018520244",
        "metafields": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/Metafield/1069230189",
                "namespace": "my_field",
                "key": "pronouns",
                "value": "they/them"
              }
            },
            {
              "node": {
                "id": "gid://shopify/Metafield/1069230190",
                "namespace": "my_field",
                "key": "nickname",
                "value": "rob"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Creates a new address for a customer

  #### Query

  ```graphql
  mutation CustomerAddressCreate($customerId: ID!, $addresses: [MailingAddressInput!]) {
    customerUpdate(input: {id: $customerId, addresses: $addresses}) {
      customer {
        id
        addressesV2(first: 10) {
          edges {
            node {
              id
              address1
              city
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
    "customerId": "gid://shopify/Customer/1018520244",
    "addresses": [
      {
        "address1": "123 New Address",
        "city": "New City"
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation CustomerAddressCreate($customerId: ID!, $addresses: [MailingAddressInput!]) { customerUpdate(input: {id: $customerId, addresses: $addresses}) { customer { id addressesV2(first: 10) { edges { node { id address1 city } } } } userErrors { field message } } }",
   "variables": {
      "customerId": "gid://shopify/Customer/1018520244",
      "addresses": [
        {
          "address1": "123 New Address",
          "city": "New City"
        }
      ]
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
    mutation CustomerAddressCreate($customerId: ID!, $addresses: [MailingAddressInput!]) {
      customerUpdate(input: {id: $customerId, addresses: $addresses}) {
        customer {
          id
          addressesV2(first: 10) {
            edges {
              node {
                id
                address1
                city
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
          "customerId": "gid://shopify/Customer/1018520244",
          "addresses": [
              {
                  "address1": "123 New Address",
                  "city": "New City"
              }
          ]
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
    mutation CustomerAddressCreate($customerId: ID!, $addresses: [MailingAddressInput!]) {
      customerUpdate(input: {id: $customerId, addresses: $addresses}) {
        customer {
          id
          addressesV2(first: 10) {
            edges {
              node {
                id
                address1
                city
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
    "customerId": "gid://shopify/Customer/1018520244",
    "addresses": [
      {
        "address1": "123 New Address",
        "city": "New City"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CustomerAddressCreate($customerId: ID!, $addresses: [MailingAddressInput!]) {
        customerUpdate(input: {id: $customerId, addresses: $addresses}) {
          customer {
            id
            addressesV2(first: 10) {
              edges {
                node {
                  id
                  address1
                  city
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
          "customerId": "gid://shopify/Customer/1018520244",
          "addresses": [
              {
                  "address1": "123 New Address",
                  "city": "New City"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CustomerAddressCreate($customerId: ID!, $addresses: [MailingAddressInput!]) {
    customerUpdate(input: {id: $customerId, addresses: $addresses}) {
      customer {
        id
        addressesV2(first: 10) {
          edges {
            node {
              id
              address1
              city
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
    "customerId": "gid://shopify/Customer/1018520244",
    "addresses": [
      {
        "address1": "123 New Address",
        "city": "New City"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "customerUpdate": {
      "customer": {
        "id": "gid://shopify/Customer/1018520244",
        "addressesV2": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/MailingAddress/1053318591?model_name=CustomerAddress",
                "address1": "123 New Address",
                "city": "New City"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Performs bulk operations for multiple customer addresses

  #### Query

  ```graphql
  mutation CustomerAddressSet($customerId: ID!, $addresses: [MailingAddressInput!]) {
    customerUpdate(input: {id: $customerId, addresses: $addresses}) {
      customer {
        id
        addressesV2(first: 10) {
          edges {
            node {
              id
              address1
              city
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
    "customerId": "gid://shopify/Customer/1018520244",
    "addresses": [
      {
        "address1": "123 Main St",
        "city": "Metropolis"
      },
      {
        "address1": "456 Elm St",
        "city": "Gotham"
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation CustomerAddressSet($customerId: ID!, $addresses: [MailingAddressInput!]) { customerUpdate(input: {id: $customerId, addresses: $addresses}) { customer { id addressesV2(first: 10) { edges { node { id address1 city } } } } userErrors { field message } } }",
   "variables": {
      "customerId": "gid://shopify/Customer/1018520244",
      "addresses": [
        {
          "address1": "123 Main St",
          "city": "Metropolis"
        },
        {
          "address1": "456 Elm St",
          "city": "Gotham"
        }
      ]
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
    mutation CustomerAddressSet($customerId: ID!, $addresses: [MailingAddressInput!]) {
      customerUpdate(input: {id: $customerId, addresses: $addresses}) {
        customer {
          id
          addressesV2(first: 10) {
            edges {
              node {
                id
                address1
                city
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
          "customerId": "gid://shopify/Customer/1018520244",
          "addresses": [
              {
                  "address1": "123 Main St",
                  "city": "Metropolis"
              },
              {
                  "address1": "456 Elm St",
                  "city": "Gotham"
              }
          ]
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
    mutation CustomerAddressSet($customerId: ID!, $addresses: [MailingAddressInput!]) {
      customerUpdate(input: {id: $customerId, addresses: $addresses}) {
        customer {
          id
          addressesV2(first: 10) {
            edges {
              node {
                id
                address1
                city
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
    "customerId": "gid://shopify/Customer/1018520244",
    "addresses": [
      {
        "address1": "123 Main St",
        "city": "Metropolis"
      },
      {
        "address1": "456 Elm St",
        "city": "Gotham"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CustomerAddressSet($customerId: ID!, $addresses: [MailingAddressInput!]) {
        customerUpdate(input: {id: $customerId, addresses: $addresses}) {
          customer {
            id
            addressesV2(first: 10) {
              edges {
                node {
                  id
                  address1
                  city
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
          "customerId": "gid://shopify/Customer/1018520244",
          "addresses": [
              {
                  "address1": "123 Main St",
                  "city": "Metropolis"
              },
              {
                  "address1": "456 Elm St",
                  "city": "Gotham"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CustomerAddressSet($customerId: ID!, $addresses: [MailingAddressInput!]) {
    customerUpdate(input: {id: $customerId, addresses: $addresses}) {
      customer {
        id
        addressesV2(first: 10) {
          edges {
            node {
              id
              address1
              city
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
    "customerId": "gid://shopify/Customer/1018520244",
    "addresses": [
      {
        "address1": "123 Main St",
        "city": "Metropolis"
      },
      {
        "address1": "456 Elm St",
        "city": "Gotham"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "customerUpdate": {
      "customer": {
        "id": "gid://shopify/Customer/1018520244",
        "addressesV2": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/MailingAddress/1053318585?model_name=CustomerAddress",
                "address1": "123 Main St",
                "city": "Metropolis"
              }
            },
            {
              "node": {
                "id": "gid://shopify/MailingAddress/1053318586?model_name=CustomerAddress",
                "address1": "456 Elm St",
                "city": "Gotham"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Update a customer with an ID that doesn't exist

  #### Description

  Trying to update a customer that doesn't exist will return an error

  #### Query

  ```graphql
  mutation customerUpdate($input: CustomerInput!) {
    customerUpdate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        firstName
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "id": "gid://shopify/Customer/1",
      "firstName": "Tobi"
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
  "query": "mutation customerUpdate($input: CustomerInput!) { customerUpdate(input: $input) { userErrors { field message } customer { id firstName } } }",
   "variables": {
      "input": {
        "id": "gid://shopify/Customer/1",
        "firstName": "Tobi"
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
    mutation customerUpdate($input: CustomerInput!) {
      customerUpdate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          firstName
        }
      }
    }`,
    {
      variables: {
          "input": {
              "id": "gid://shopify/Customer/1",
              "firstName": "Tobi"
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
    mutation customerUpdate($input: CustomerInput!) {
      customerUpdate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          firstName
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "id": "gid://shopify/Customer/1",
      "firstName": "Tobi"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation customerUpdate($input: CustomerInput!) {
        customerUpdate(input: $input) {
          userErrors {
            field
            message
          }
          customer {
            id
            firstName
          }
        }
      }`,
      "variables": {
          "input": {
              "id": "gid://shopify/Customer/1",
              "firstName": "Tobi"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation customerUpdate($input: CustomerInput!) {
    customerUpdate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        firstName
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "id": "gid://shopify/Customer/1",
      "firstName": "Tobi"
    }
  }'
  ```

  #### Response

  ```json
  {
    "customerUpdate": {
      "userErrors": [
        {
          "field": [
            "id"
          ],
          "message": "Customer does not exist"
        }
      ],
      "customer": null
    }
  }
  ```

* ### Updates a customer's first and last name

  #### Description

  Update a customer's first and last name

  #### Query

  ```graphql
  mutation customerUpdate($input: CustomerInput!) {
    customerUpdate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        firstName
        lastName
      }
    }
  }
  ```

  #### Variables

  ```json
  {
    "input": {
      "id": "gid://shopify/Customer/1018520244",
      "firstName": "Tobi",
      "lastName": "Lutke"
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
  "query": "mutation customerUpdate($input: CustomerInput!) { customerUpdate(input: $input) { userErrors { field message } customer { id firstName lastName } } }",
   "variables": {
      "input": {
        "id": "gid://shopify/Customer/1018520244",
        "firstName": "Tobi",
        "lastName": "Lutke"
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
    mutation customerUpdate($input: CustomerInput!) {
      customerUpdate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          firstName
          lastName
        }
      }
    }`,
    {
      variables: {
          "input": {
              "id": "gid://shopify/Customer/1018520244",
              "firstName": "Tobi",
              "lastName": "Lutke"
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
    mutation customerUpdate($input: CustomerInput!) {
      customerUpdate(input: $input) {
        userErrors {
          field
          message
        }
        customer {
          id
          firstName
          lastName
        }
      }
    }
  QUERY

  variables = {
    "input": {
      "id": "gid://shopify/Customer/1018520244",
      "firstName": "Tobi",
      "lastName": "Lutke"
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation customerUpdate($input: CustomerInput!) {
        customerUpdate(input: $input) {
          userErrors {
            field
            message
          }
          customer {
            id
            firstName
            lastName
          }
        }
      }`,
      "variables": {
          "input": {
              "id": "gid://shopify/Customer/1018520244",
              "firstName": "Tobi",
              "lastName": "Lutke"
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation customerUpdate($input: CustomerInput!) {
    customerUpdate(input: $input) {
      userErrors {
        field
        message
      }
      customer {
        id
        firstName
        lastName
      }
    }
  }' \
  --variables \
  '{
    "input": {
      "id": "gid://shopify/Customer/1018520244",
      "firstName": "Tobi",
      "lastName": "Lutke"
    }
  }'
  ```

  #### Response

  ```json
  {
    "customerUpdate": {
      "userErrors": [],
      "customer": {
        "id": "gid://shopify/Customer/1018520244",
        "firstName": "Tobi",
        "lastName": "Lutke"
      }
    }
  }
  ```

* ### Updates an existing customer address

  #### Query

  ```graphql
  mutation CustomerAddressUpdate($customerId: ID!, $addresses: [MailingAddressInput!]) {
    customerUpdate(input: {id: $customerId, addresses: $addresses}) {
      customer {
        id
        addressesV2(first: 10) {
          edges {
            node {
              id
              address1
              city
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
    "customerId": "gid://shopify/Customer/1018520244",
    "addresses": [
      {
        "address1": "123 New Street",
        "city": "New City"
      }
    ]
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "mutation CustomerAddressUpdate($customerId: ID!, $addresses: [MailingAddressInput!]) { customerUpdate(input: {id: $customerId, addresses: $addresses}) { customer { id addressesV2(first: 10) { edges { node { id address1 city } } } } userErrors { field message } } }",
   "variables": {
      "customerId": "gid://shopify/Customer/1018520244",
      "addresses": [
        {
          "address1": "123 New Street",
          "city": "New City"
        }
      ]
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
    mutation CustomerAddressUpdate($customerId: ID!, $addresses: [MailingAddressInput!]) {
      customerUpdate(input: {id: $customerId, addresses: $addresses}) {
        customer {
          id
          addressesV2(first: 10) {
            edges {
              node {
                id
                address1
                city
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
          "customerId": "gid://shopify/Customer/1018520244",
          "addresses": [
              {
                  "address1": "123 New Street",
                  "city": "New City"
              }
          ]
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
    mutation CustomerAddressUpdate($customerId: ID!, $addresses: [MailingAddressInput!]) {
      customerUpdate(input: {id: $customerId, addresses: $addresses}) {
        customer {
          id
          addressesV2(first: 10) {
            edges {
              node {
                id
                address1
                city
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
    "customerId": "gid://shopify/Customer/1018520244",
    "addresses": [
      {
        "address1": "123 New Street",
        "city": "New City"
      }
    ]
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CustomerAddressUpdate($customerId: ID!, $addresses: [MailingAddressInput!]) {
        customerUpdate(input: {id: $customerId, addresses: $addresses}) {
          customer {
            id
            addressesV2(first: 10) {
              edges {
                node {
                  id
                  address1
                  city
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
          "customerId": "gid://shopify/Customer/1018520244",
          "addresses": [
              {
                  "address1": "123 New Street",
                  "city": "New City"
              }
          ]
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CustomerAddressUpdate($customerId: ID!, $addresses: [MailingAddressInput!]) {
    customerUpdate(input: {id: $customerId, addresses: $addresses}) {
      customer {
        id
        addressesV2(first: 10) {
          edges {
            node {
              id
              address1
              city
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
    "customerId": "gid://shopify/Customer/1018520244",
    "addresses": [
      {
        "address1": "123 New Street",
        "city": "New City"
      }
    ]
  }'
  ```

  #### Response

  ```json
  {
    "customerUpdate": {
      "customer": {
        "id": "gid://shopify/Customer/1018520244",
        "addressesV2": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/MailingAddress/1053318595?model_name=CustomerAddress",
                "address1": "123 New Street",
                "city": "New City"
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### customerUpdate reference
