---
title: companyCreate - GraphQL Admin
description: >-
  Creates a
  [`Company`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Company)
  for B2B commerce. This mutation creates the company and can optionally create
  an initial
  [`CompanyContact`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyContact)
  and
  [`CompanyLocation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation)
  in a single operation. Company contacts are people who place orders on behalf
  of the company. Company locations are branches or offices with their own
  billing and shipping addresses.


  > Note: Creating a company without a `name` [returns an
  error](https://shopify.dev/docs/api/admin-graphql/latest/mutations/companycreate?example=creating-a-company-without-a-name-returns-an-error).


  Learn more about [creating companies for
  B2B](https://shopify.dev/docs/apps/build/b2b/start-building#step-1-create-a-company).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyCreate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/companyCreate.md'
---

# company​Create

mutation

Requires `write_customers` access scope or `write_companies` access scope. Also: The API client must be installed on a Shopify Plus store.

Creates a [`Company`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Company) for B2B commerce. This mutation creates the company and can optionally create an initial [`CompanyContact`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyContact) and [`CompanyLocation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation) in a single operation. Company contacts are people who place orders on behalf of the company. Company locations are branches or offices with their own billing and shipping addresses.

***

**Note:** Creating a company without a \<code>name\</code> \<a href="https://shopify.dev/docs/api/admin-graphql/latest/mutations/companycreate?example=creating-a-company-without-a-name-returns-an-error">returns an error\</a>.

***

Learn more about [creating companies for B2B](https://shopify.dev/docs/apps/build/b2b/start-building#step-1-create-a-company).

## Arguments

* input

  [Company​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CompanyCreateInput)

  required

  The fields to use when creating the company.

***

## Company​Create​Payload returns

* company

  [Company](https://shopify.dev/docs/api/admin-graphql/latest/objects/Company)

  The created company.

* user​Errors

  [\[Business​Customer​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/BusinessCustomerUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### Create a company

  #### Description

  Create a company with a company contact and company location.

  #### Query

  ```graphql
  mutation CompanyCreate($input: CompanyCreateInput!) {
    companyCreate(input: $input) {
      company {
        id
        name
        externalId
        mainContact {
          id
          customer {
            id
            email
            firstName
            lastName
          }
        }
        contacts(first: 5) {
          edges {
            node {
              id
              customer {
                email
                firstName
                lastName
              }
            }
          }
        }
        contactRoles(first: 5) {
          edges {
            node {
              id
              name
            }
          }
        }
        locations(first: 5) {
          edges {
            node {
              id
              name
              shippingAddress {
                firstName
                lastName
                address1
                city
                province
                zip
                country
              }
            }
          }
        }
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
      "company": {
        "name": "Postal Cards Inc",
        "externalId": "01456606-0001"
      },
      "companyLocation": {
        "name": "Ottawa Postal Cards",
        "shippingAddress": {
          "firstName": "Avery",
          "lastName": "Brown",
          "address1": "150 Elgin Street",
          "address2": "8th Floor",
          "city": "Ottawa",
          "zoneCode": "ON",
          "zip": "K2P 1L4",
          "countryCode": "CA"
        },
        "billingSameAsShipping": true
      },
      "companyContact": {
        "email": "avery.brown@example.com",
        "firstName": "Avery",
        "lastName": "Brown"
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
  "query": "mutation CompanyCreate($input: CompanyCreateInput!) { companyCreate(input: $input) { company { id name externalId mainContact { id customer { id email firstName lastName } } contacts(first: 5) { edges { node { id customer { email firstName lastName } } } } contactRoles(first: 5) { edges { node { id name } } } locations(first: 5) { edges { node { id name shippingAddress { firstName lastName address1 city province zip country } } } } } userErrors { field message code } } }",
   "variables": {
      "input": {
        "company": {
          "name": "Postal Cards Inc",
          "externalId": "01456606-0001"
        },
        "companyLocation": {
          "name": "Ottawa Postal Cards",
          "shippingAddress": {
            "firstName": "Avery",
            "lastName": "Brown",
            "address1": "150 Elgin Street",
            "address2": "8th Floor",
            "city": "Ottawa",
            "zoneCode": "ON",
            "zip": "K2P 1L4",
            "countryCode": "CA"
          },
          "billingSameAsShipping": true
        },
        "companyContact": {
          "email": "avery.brown@example.com",
          "firstName": "Avery",
          "lastName": "Brown"
        }
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
    mutation CompanyCreate($input: CompanyCreateInput!) {
      companyCreate(input: $input) {
        company {
          id
          name
          externalId
          mainContact {
            id
            customer {
              id
              email
              firstName
              lastName
            }
          }
          contacts(first: 5) {
            edges {
              node {
                id
                customer {
                  email
                  firstName
                  lastName
                }
              }
            }
          }
          contactRoles(first: 5) {
            edges {
              node {
                id
                name
              }
            }
          }
          locations(first: 5) {
            edges {
              node {
                id
                name
                shippingAddress {
                  firstName
                  lastName
                  address1
                  city
                  province
                  zip
                  country
                }
              }
            }
          }
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
              "company": {
                  "name": "Postal Cards Inc",
                  "externalId": "01456606-0001"
              },
              "companyLocation": {
                  "name": "Ottawa Postal Cards",
                  "shippingAddress": {
                      "firstName": "Avery",
                      "lastName": "Brown",
                      "address1": "150 Elgin Street",
                      "address2": "8th Floor",
                      "city": "Ottawa",
                      "zoneCode": "ON",
                      "zip": "K2P 1L4",
                      "countryCode": "CA"
                  },
                  "billingSameAsShipping": true
              },
              "companyContact": {
                  "email": "avery.brown@example.com",
                  "firstName": "Avery",
                  "lastName": "Brown"
              }
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
    mutation CompanyCreate($input: CompanyCreateInput!) {
      companyCreate(input: $input) {
        company {
          id
          name
          externalId
          mainContact {
            id
            customer {
              id
              email
              firstName
              lastName
            }
          }
          contacts(first: 5) {
            edges {
              node {
                id
                customer {
                  email
                  firstName
                  lastName
                }
              }
            }
          }
          contactRoles(first: 5) {
            edges {
              node {
                id
                name
              }
            }
          }
          locations(first: 5) {
            edges {
              node {
                id
                name
                shippingAddress {
                  firstName
                  lastName
                  address1
                  city
                  province
                  zip
                  country
                }
              }
            }
          }
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
      "company": {
        "name": "Postal Cards Inc",
        "externalId": "01456606-0001"
      },
      "companyLocation": {
        "name": "Ottawa Postal Cards",
        "shippingAddress": {
          "firstName": "Avery",
          "lastName": "Brown",
          "address1": "150 Elgin Street",
          "address2": "8th Floor",
          "city": "Ottawa",
          "zoneCode": "ON",
          "zip": "K2P 1L4",
          "countryCode": "CA"
        },
        "billingSameAsShipping": true
      },
      "companyContact": {
        "email": "avery.brown@example.com",
        "firstName": "Avery",
        "lastName": "Brown"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CompanyCreate($input: CompanyCreateInput!) {
        companyCreate(input: $input) {
          company {
            id
            name
            externalId
            mainContact {
              id
              customer {
                id
                email
                firstName
                lastName
              }
            }
            contacts(first: 5) {
              edges {
                node {
                  id
                  customer {
                    email
                    firstName
                    lastName
                  }
                }
              }
            }
            contactRoles(first: 5) {
              edges {
                node {
                  id
                  name
                }
              }
            }
            locations(first: 5) {
              edges {
                node {
                  id
                  name
                  shippingAddress {
                    firstName
                    lastName
                    address1
                    city
                    province
                    zip
                    country
                  }
                }
              }
            }
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
              "company": {
                  "name": "Postal Cards Inc",
                  "externalId": "01456606-0001"
              },
              "companyLocation": {
                  "name": "Ottawa Postal Cards",
                  "shippingAddress": {
                      "firstName": "Avery",
                      "lastName": "Brown",
                      "address1": "150 Elgin Street",
                      "address2": "8th Floor",
                      "city": "Ottawa",
                      "zoneCode": "ON",
                      "zip": "K2P 1L4",
                      "countryCode": "CA"
                  },
                  "billingSameAsShipping": true
              },
              "companyContact": {
                  "email": "avery.brown@example.com",
                  "firstName": "Avery",
                  "lastName": "Brown"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CompanyCreate($input: CompanyCreateInput!) {
    companyCreate(input: $input) {
      company {
        id
        name
        externalId
        mainContact {
          id
          customer {
            id
            email
            firstName
            lastName
          }
        }
        contacts(first: 5) {
          edges {
            node {
              id
              customer {
                email
                firstName
                lastName
              }
            }
          }
        }
        contactRoles(first: 5) {
          edges {
            node {
              id
              name
            }
          }
        }
        locations(first: 5) {
          edges {
            node {
              id
              name
              shippingAddress {
                firstName
                lastName
                address1
                city
                province
                zip
                country
              }
            }
          }
        }
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
      "company": {
        "name": "Postal Cards Inc",
        "externalId": "01456606-0001"
      },
      "companyLocation": {
        "name": "Ottawa Postal Cards",
        "shippingAddress": {
          "firstName": "Avery",
          "lastName": "Brown",
          "address1": "150 Elgin Street",
          "address2": "8th Floor",
          "city": "Ottawa",
          "zoneCode": "ON",
          "zip": "K2P 1L4",
          "countryCode": "CA"
        },
        "billingSameAsShipping": true
      },
      "companyContact": {
        "email": "avery.brown@example.com",
        "firstName": "Avery",
        "lastName": "Brown"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "companyCreate": {
      "company": {
        "id": "gid://shopify/Company/1059559575",
        "name": "Postal Cards Inc",
        "externalId": "01456606-0001",
        "mainContact": {
          "id": "gid://shopify/CompanyContact/1059341835",
          "customer": {
            "id": "gid://shopify/Customer/1073339466",
            "email": "avery.brown@example.com",
            "firstName": "Avery",
            "lastName": "Brown"
          }
        },
        "contacts": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/CompanyContact/1059341835",
                "customer": {
                  "email": "avery.brown@example.com",
                  "firstName": "Avery",
                  "lastName": "Brown"
                }
              }
            }
          ]
        },
        "contactRoles": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/CompanyContactRole/1007033458",
                "name": "Location admin"
              }
            },
            {
              "node": {
                "id": "gid://shopify/CompanyContactRole/1007033459",
                "name": "Ordering only"
              }
            }
          ]
        },
        "locations": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/CompanyLocation/966871284",
                "name": "Ottawa Postal Cards",
                "shippingAddress": {
                  "firstName": "Avery",
                  "lastName": "Brown",
                  "address1": "150 Elgin Street",
                  "city": "Ottawa",
                  "province": "Ontario",
                  "zip": "K2P 1L4",
                  "country": "Canada"
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

* ### Create a company with required fields only

  #### Description

  Create a company with no company contact and the default company location.

  #### Query

  ```graphql
  mutation CompanyCreate($input: CompanyCreateInput!) {
    companyCreate(input: $input) {
      company {
        id
        name
        mainContact {
          id
        }
        contactRoles(first: 5) {
          edges {
            node {
              id
              name
            }
          }
        }
        locations(first: 5) {
          edges {
            node {
              id
              name
              shippingAddress {
                firstName
                lastName
                address1
                city
                province
                zip
                country
              }
            }
          }
        }
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
      "company": {
        "name": "Postal Cards Inc"
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
  "query": "mutation CompanyCreate($input: CompanyCreateInput!) { companyCreate(input: $input) { company { id name mainContact { id } contactRoles(first: 5) { edges { node { id name } } } locations(first: 5) { edges { node { id name shippingAddress { firstName lastName address1 city province zip country } } } } } userErrors { field message code } } }",
   "variables": {
      "input": {
        "company": {
          "name": "Postal Cards Inc"
        }
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
    mutation CompanyCreate($input: CompanyCreateInput!) {
      companyCreate(input: $input) {
        company {
          id
          name
          mainContact {
            id
          }
          contactRoles(first: 5) {
            edges {
              node {
                id
                name
              }
            }
          }
          locations(first: 5) {
            edges {
              node {
                id
                name
                shippingAddress {
                  firstName
                  lastName
                  address1
                  city
                  province
                  zip
                  country
                }
              }
            }
          }
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
              "company": {
                  "name": "Postal Cards Inc"
              }
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
    mutation CompanyCreate($input: CompanyCreateInput!) {
      companyCreate(input: $input) {
        company {
          id
          name
          mainContact {
            id
          }
          contactRoles(first: 5) {
            edges {
              node {
                id
                name
              }
            }
          }
          locations(first: 5) {
            edges {
              node {
                id
                name
                shippingAddress {
                  firstName
                  lastName
                  address1
                  city
                  province
                  zip
                  country
                }
              }
            }
          }
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
      "company": {
        "name": "Postal Cards Inc"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CompanyCreate($input: CompanyCreateInput!) {
        companyCreate(input: $input) {
          company {
            id
            name
            mainContact {
              id
            }
            contactRoles(first: 5) {
              edges {
                node {
                  id
                  name
                }
              }
            }
            locations(first: 5) {
              edges {
                node {
                  id
                  name
                  shippingAddress {
                    firstName
                    lastName
                    address1
                    city
                    province
                    zip
                    country
                  }
                }
              }
            }
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
              "company": {
                  "name": "Postal Cards Inc"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CompanyCreate($input: CompanyCreateInput!) {
    companyCreate(input: $input) {
      company {
        id
        name
        mainContact {
          id
        }
        contactRoles(first: 5) {
          edges {
            node {
              id
              name
            }
          }
        }
        locations(first: 5) {
          edges {
            node {
              id
              name
              shippingAddress {
                firstName
                lastName
                address1
                city
                province
                zip
                country
              }
            }
          }
        }
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
      "company": {
        "name": "Postal Cards Inc"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "companyCreate": {
      "company": {
        "id": "gid://shopify/Company/1059559574",
        "name": "Postal Cards Inc",
        "mainContact": null,
        "contactRoles": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/CompanyContactRole/1007033456",
                "name": "Location admin"
              }
            },
            {
              "node": {
                "id": "gid://shopify/CompanyContactRole/1007033457",
                "name": "Ordering only"
              }
            }
          ]
        },
        "locations": {
          "edges": [
            {
              "node": {
                "id": "gid://shopify/CompanyLocation/966871283",
                "name": "Postal Cards Inc",
                "shippingAddress": null
              }
            }
          ]
        }
      },
      "userErrors": []
    }
  }
  ```

* ### Creating a company without a name returns an error

  #### Description

  Create a company with no company contact and the default company location.

  #### Query

  ```graphql
  mutation CompanyCreate($input: CompanyCreateInput!) {
    companyCreate(input: $input) {
      company {
        id
        name
        mainContact {
          id
        }
        contactRoles(first: 5) {
          edges {
            node {
              id
              name
            }
          }
        }
        locations(first: 5) {
          edges {
            node {
              id
              name
              shippingAddress {
                firstName
                lastName
                address1
                city
                province
                zip
                country
              }
            }
          }
        }
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
      "company": {
        "externalId": "123"
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
  "query": "mutation CompanyCreate($input: CompanyCreateInput!) { companyCreate(input: $input) { company { id name mainContact { id } contactRoles(first: 5) { edges { node { id name } } } locations(first: 5) { edges { node { id name shippingAddress { firstName lastName address1 city province zip country } } } } } userErrors { field message code } } }",
   "variables": {
      "input": {
        "company": {
          "externalId": "123"
        }
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
    mutation CompanyCreate($input: CompanyCreateInput!) {
      companyCreate(input: $input) {
        company {
          id
          name
          mainContact {
            id
          }
          contactRoles(first: 5) {
            edges {
              node {
                id
                name
              }
            }
          }
          locations(first: 5) {
            edges {
              node {
                id
                name
                shippingAddress {
                  firstName
                  lastName
                  address1
                  city
                  province
                  zip
                  country
                }
              }
            }
          }
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
              "company": {
                  "externalId": "123"
              }
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
    mutation CompanyCreate($input: CompanyCreateInput!) {
      companyCreate(input: $input) {
        company {
          id
          name
          mainContact {
            id
          }
          contactRoles(first: 5) {
            edges {
              node {
                id
                name
              }
            }
          }
          locations(first: 5) {
            edges {
              node {
                id
                name
                shippingAddress {
                  firstName
                  lastName
                  address1
                  city
                  province
                  zip
                  country
                }
              }
            }
          }
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
      "company": {
        "externalId": "123"
      }
    }
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `mutation CompanyCreate($input: CompanyCreateInput!) {
        companyCreate(input: $input) {
          company {
            id
            name
            mainContact {
              id
            }
            contactRoles(first: 5) {
              edges {
                node {
                  id
                  name
                }
              }
            }
            locations(first: 5) {
              edges {
                node {
                  id
                  name
                  shippingAddress {
                    firstName
                    lastName
                    address1
                    city
                    province
                    zip
                    country
                  }
                }
              }
            }
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
              "company": {
                  "externalId": "123"
              }
          }
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'mutation CompanyCreate($input: CompanyCreateInput!) {
    companyCreate(input: $input) {
      company {
        id
        name
        mainContact {
          id
        }
        contactRoles(first: 5) {
          edges {
            node {
              id
              name
            }
          }
        }
        locations(first: 5) {
          edges {
            node {
              id
              name
              shippingAddress {
                firstName
                lastName
                address1
                city
                province
                zip
                country
              }
            }
          }
        }
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
      "company": {
        "externalId": "123"
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "companyCreate": {
      "company": null,
      "userErrors": [
        {
          "field": [
            "input",
            "company",
            "name"
          ],
          "message": "Name must exist",
          "code": "REQUIRED"
        }
      ]
    }
  }
  ```

* ### companyCreate reference
