---
title: customers - GraphQL Admin
description: >-
  Returns a list of
  [customers](https://shopify.dev/api/admin-graphql/latest/objects/Customer) in
  your Shopify store, including key information such as name, email, location,
  and purchase history.

  Use this query to segment your audience, personalize marketing campaigns, or
  analyze customer behavior by applying filters based on location, order
  history, marketing preferences and tags.

  The `customers` query supports
  [pagination](https://shopify.dev/api/usage/pagination-graphql) and
  [sorting](https://shopify.dev/api/admin-graphql/latest/enums/CustomerSortKeys).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/customers'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/customers.md'
---

# customers

query

Returns a list of [customers](https://shopify.dev/api/admin-graphql/latest/objects/Customer) in your Shopify store, including key information such as name, email, location, and purchase history. Use this query to segment your audience, personalize marketing campaigns, or analyze customer behavior by applying filters based on location, order history, marketing preferences and tags. The `customers` query supports [pagination](https://shopify.dev/api/usage/pagination-graphql) and [sorting](https://shopify.dev/api/admin-graphql/latest/enums/CustomerSortKeys).

## CustomerConnection arguments

[CustomerConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CustomerConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * * default

      string

    * accepts\_marketing

      boolean

    * country

      string

    * customer\_date

      time

    * email

      string

    * first\_name

      string

    * id

      id

    * last\_abandoned\_order\_date

      time

    * last\_name

      string

    * order\_date

      time

    * orders\_count

      integer

    * phone

      string

    * state

      string

    * tag

      string

    * tag\_not

      string

    * total\_spent

      float

    * updated\_at

      time

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:

      * `query=Bob Norman`
      * `query=title:green hoodie`

      Filter by whether a customer has consented to receive marketing material.

    - Example:

      * `accepts_marketing:true`

      Filter by the country associated with the customer's address. Use either the country name or the two-letter country code.

    - Example:

      * `country:Canada`
      * `country:JP`

      Filter by the date and time when the customer record was created. This query parameter filters by the [`createdAt`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer#field-createdAt) field.

    - Example:

      * `customer_date:'2024-03-15T14:30:00Z'`
      * `customer_date: >='2024-01-01'`

      The customer's email address, used to communicate information about orders and for the purposes of email marketing campaigns. You can use a wildcard value to filter the query by customers who have an email address specified. Please note that *email* is a tokenized field: To retrieve exact matches, quote the email address (*phrase query*) as described in [Shopify API search syntax](https://shopify.dev/docs/api/usage/search-syntax).

    - Example:

      * `email:gmail.com`
      * `email:"bo.wang@example.com"`
      * `email:*`

      Filter by the customer's first name.

    - Example:

      * `first_name:Jane`

      Filter by `id` range.

    - Example:

      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

      Filter by the date and time of the customer's most recent abandoned checkout. An abandoned checkout occurs when a customer adds items to their cart, begins the checkout process, but leaves the site without completing their purchase.

    - Example:

      * `last_abandoned_order_date:'2024-04-01T10:00:00Z'`
      * `last_abandoned_order_date: >='2024-01-01'`

      Filter by the customer's last name.

    - Example:

      * `last_name:Reeves`

      Filter by the date and time that the order was placed by the customer. Use this query filter to check if a customer has placed at least one order within a specified date range.

    - Example:

      * `order_date:'2024-02-20T00:00:00Z'`
      * `order_date: >='2024-01-01'`
      * `order_date:'2024-01-01..2024-03-31'`

      Filter by the total number of orders a customer has placed.

    - Example:

      * `orders_count:5`

      The phone number of the customer, used to communicate information about orders and for the purposes of SMS marketing campaigns. You can use a wildcard value to filter the query by customers who have a phone number specified.

    - Example:

      * `phone:+18005550100`
      * `phone:*`

      Filter by the [state](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer#field-state) of the customer's account with the shop. This filter is only valid when [Classic Customer Accounts](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerAccountsV2#field-customerAccountsVersion) is active.

    - Example:

      * `state:ENABLED`
      * `state:INVITED`
      * `state:DISABLED`
      * `state:DECLINED`

      Filter by the tags that are associated with the customer. This query parameter accepts multiple tags separated by commas.

    - Example:

      * `tag:'VIP'`
      * `tag:'Wholesale,Repeat'`

      Filter by the tags that aren't associated with the customer. This query parameter accepts multiple tags separated by commas.

    - Example:

      * `tag_not:'Prospect'`
      * `tag_not:'Test,Internal'`

      Filter by the total amount of money a customer has spent across all orders.

    - Example:

      * `total_spent:100.50`
      * `total_spent:50.00`
      * `total_spent:>100.50`
      * `total_spent:>50.00`

      The date and time, matching a whole day, when the customer's information was last updated.

      Example:

      * `updated_at:2024-01-01T00:00:00Z`
      * `updated_at:<now`
      * `updated_at:<=2024`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Customer​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/CustomerSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Customer​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Customer!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

  non-null

  A list of nodes that are contained in CustomerEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### Retrieve detailed information for a list of customers

  #### Description

  This query retrieves a comprehensive set of fields for the first 50 \[customer]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/customer) records using an extended \[\`nodes\`]\(https://shopify.dev/docs/api/admin-graphql/latest/queries/customers#field-nodes) selection. The query demonstrates how to retrieve various details in a single request.

  #### Query

  ```graphql
  query CustomerList {
    customers(first: 50) {
      nodes {
        id
        firstName
        lastName
        defaultEmailAddress {
          emailAddress
          marketingState
        }
        defaultPhoneNumber {
          phoneNumber
          marketingState
          marketingCollectedFrom
        }
        createdAt
        updatedAt
        numberOfOrders
        state
        amountSpent {
          amount
          currencyCode
        }
        verifiedEmail
        taxExempt
        tags
        addresses {
          id
          firstName
          lastName
          address1
          city
          province
          country
          zip
          phone
          name
          provinceCode
          countryCodeV2
        }
        defaultAddress {
          id
          address1
          city
          province
          country
          zip
          phone
          provinceCode
          countryCodeV2
        }
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
  "query": "query CustomerList { customers(first: 50) { nodes { id firstName lastName defaultEmailAddress { emailAddress marketingState } defaultPhoneNumber { phoneNumber marketingState marketingCollectedFrom } createdAt updatedAt numberOfOrders state amountSpent { amount currencyCode } verifiedEmail taxExempt tags addresses { id firstName lastName address1 city province country zip phone name provinceCode countryCodeV2 } defaultAddress { id address1 city province country zip phone provinceCode countryCodeV2 } } } }"
  }'
  ```

  #### React Router

  ```javascript
  import { authenticate } from "../shopify.server";

  export const loader = async ({request}) => {
    const { admin } = await authenticate.admin(request);
    const response = await admin.graphql(
      `#graphql
    query CustomerList {
      customers(first: 50) {
        nodes {
          id
          firstName
          lastName
          defaultEmailAddress {
            emailAddress
            marketingState
          }
          defaultPhoneNumber {
            phoneNumber
            marketingState
            marketingCollectedFrom
          }
          createdAt
          updatedAt
          numberOfOrders
          state
          amountSpent {
            amount
            currencyCode
          }
          verifiedEmail
          taxExempt
          tags
          addresses {
            id
            firstName
            lastName
            address1
            city
            province
            country
            zip
            phone
            name
            provinceCode
            countryCodeV2
          }
          defaultAddress {
            id
            address1
            city
            province
            country
            zip
            phone
            provinceCode
            countryCodeV2
          }
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
    query CustomerList {
      customers(first: 50) {
        nodes {
          id
          firstName
          lastName
          defaultEmailAddress {
            emailAddress
            marketingState
          }
          defaultPhoneNumber {
            phoneNumber
            marketingState
            marketingCollectedFrom
          }
          createdAt
          updatedAt
          numberOfOrders
          state
          amountSpent {
            amount
            currencyCode
          }
          verifiedEmail
          taxExempt
          tags
          addresses {
            id
            firstName
            lastName
            address1
            city
            province
            country
            zip
            phone
            name
            provinceCode
            countryCodeV2
          }
          defaultAddress {
            id
            address1
            city
            province
            country
            zip
            phone
            provinceCode
            countryCodeV2
          }
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
    data: `query CustomerList {
      customers(first: 50) {
        nodes {
          id
          firstName
          lastName
          defaultEmailAddress {
            emailAddress
            marketingState
          }
          defaultPhoneNumber {
            phoneNumber
            marketingState
            marketingCollectedFrom
          }
          createdAt
          updatedAt
          numberOfOrders
          state
          amountSpent {
            amount
            currencyCode
          }
          verifiedEmail
          taxExempt
          tags
          addresses {
            id
            firstName
            lastName
            address1
            city
            province
            country
            zip
            phone
            name
            provinceCode
            countryCodeV2
          }
          defaultAddress {
            id
            address1
            city
            province
            country
            zip
            phone
            provinceCode
            countryCodeV2
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query CustomerList {
    customers(first: 50) {
      nodes {
        id
        firstName
        lastName
        defaultEmailAddress {
          emailAddress
          marketingState
        }
        defaultPhoneNumber {
          phoneNumber
          marketingState
          marketingCollectedFrom
        }
        createdAt
        updatedAt
        numberOfOrders
        state
        amountSpent {
          amount
          currencyCode
        }
        verifiedEmail
        taxExempt
        tags
        addresses {
          id
          firstName
          lastName
          address1
          city
          province
          country
          zip
          phone
          name
          provinceCode
          countryCodeV2
        }
        defaultAddress {
          id
          address1
          city
          province
          country
          zip
          phone
          provinceCode
          countryCodeV2
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "customers": {
      "nodes": [
        {
          "id": "gid://shopify/Customer/56501169",
          "firstName": "Jenny",
          "lastName": "Test",
          "defaultEmailAddress": {
            "emailAddress": "jennytest@b2b.example.com",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+13125551219",
            "marketingState": "NOT_SUBSCRIBED",
            "marketingCollectedFrom": null
          },
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "DISABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [],
          "defaultAddress": null
        },
        {
          "id": "gid://shopify/Customer/105906728",
          "firstName": "John",
          "lastName": "Smith",
          "defaultEmailAddress": {
            "emailAddress": "johnsmith@example.com",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+16134504532",
            "marketingState": "NOT_SUBSCRIBED",
            "marketingCollectedFrom": "OTHER"
          },
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "DISABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [
            {
              "id": "gid://shopify/MailingAddress/105906728?model_name=CustomerAddress",
              "firstName": "John",
              "lastName": "Smith",
              "address1": "124 Big Green St",
              "city": "Ottawa",
              "province": "Ontario",
              "country": "Canada",
              "zip": "K2H7A8",
              "phone": "+1(613)555-1212",
              "name": "John Smith",
              "provinceCode": "ON",
              "countryCodeV2": "CA"
            }
          ],
          "defaultAddress": {
            "id": "gid://shopify/MailingAddress/105906728?model_name=CustomerAddress",
            "address1": "124 Big Green St",
            "city": "Ottawa",
            "province": "Ontario",
            "country": "Canada",
            "zip": "K2H7A8",
            "phone": "+1(613)555-1212",
            "provinceCode": "ON",
            "countryCodeV2": "CA"
          }
        },
        {
          "id": "gid://shopify/Customer/305367469",
          "firstName": "Test",
          "lastName": "Customer",
          "defaultEmailAddress": null,
          "defaultPhoneNumber": null,
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "DISABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [],
          "defaultAddress": null
        },
        {
          "id": "gid://shopify/Customer/317070273",
          "firstName": "Bob",
          "lastName": "Norman",
          "defaultEmailAddress": null,
          "defaultPhoneNumber": {
            "phoneNumber": "+16134504538",
            "marketingState": "SUBSCRIBED",
            "marketingCollectedFrom": "OTHER"
          },
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "DISABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [
            {
              "id": "gid://shopify/MailingAddress/317070273?model_name=CustomerAddress",
              "firstName": null,
              "lastName": null,
              "address1": "Chestnut Street 92",
              "city": "Louisville",
              "province": "KY",
              "country": "US",
              "zip": "40202",
              "phone": "555-625-1199",
              "name": "",
              "provinceCode": "KY",
              "countryCodeV2": "US"
            }
          ],
          "defaultAddress": {
            "id": "gid://shopify/MailingAddress/317070273?model_name=CustomerAddress",
            "address1": "Chestnut Street 92",
            "city": "Louisville",
            "province": "KY",
            "country": "US",
            "zip": "40202",
            "phone": "555-625-1199",
            "provinceCode": "KY",
            "countryCodeV2": "US"
          }
        },
        {
          "id": "gid://shopify/Customer/324586928",
          "firstName": "B2B",
          "lastName": "Customer",
          "defaultEmailAddress": {
            "emailAddress": "b2b@example.com",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+13125551213",
            "marketingState": "NOT_SUBSCRIBED",
            "marketingCollectedFrom": null
          },
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "1",
          "state": "ENABLED",
          "amountSpent": {
            "amount": "32.4",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [],
          "defaultAddress": null
        },
        {
          "id": "gid://shopify/Customer/352184960",
          "firstName": "Jenny",
          "lastName": "Doe",
          "defaultEmailAddress": {
            "emailAddress": "jennydoe@b2bmigration.com",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": null,
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "DISABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [],
          "defaultAddress": null
        },
        {
          "id": "gid://shopify/Customer/408913340",
          "firstName": "John",
          "lastName": "Doe",
          "defaultEmailAddress": {
            "emailAddress": "john@doe.com",
            "marketingState": "SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+16134504534",
            "marketingState": "SUBSCRIBED",
            "marketingCollectedFrom": null
          },
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "DISABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [
            {
              "id": "gid://shopify/MailingAddress/408913340?model_name=CustomerAddress",
              "firstName": "John",
              "lastName": "Doe",
              "address1": "123 Amoebobacterieae St",
              "city": "Ottawa",
              "province": "Ontario",
              "country": "Canada",
              "zip": "K2P0V6",
              "phone": "+16134504534",
              "name": "John Doe",
              "provinceCode": "ON",
              "countryCodeV2": "CA"
            }
          ],
          "defaultAddress": {
            "id": "gid://shopify/MailingAddress/408913340?model_name=CustomerAddress",
            "address1": "123 Amoebobacterieae St",
            "city": "Ottawa",
            "province": "Ontario",
            "country": "Canada",
            "zip": "K2P0V6",
            "phone": "+16134504534",
            "provinceCode": "ON",
            "countryCodeV2": "CA"
          }
        },
        {
          "id": "gid://shopify/Customer/529223679",
          "firstName": "Bob",
          "lastName": "Marketing",
          "defaultEmailAddress": {
            "emailAddress": "email_marketing_pending_customer@example.com",
            "marketingState": "PENDING"
          },
          "defaultPhoneNumber": null,
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "DISABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [],
          "defaultAddress": null
        },
        {
          "id": "gid://shopify/Customer/544365967",
          "firstName": "Bob",
          "lastName": "Bobsen",
          "defaultEmailAddress": {
            "emailAddress": "bob@example.com",
            "marketingState": "SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+13125551212",
            "marketingState": "NOT_SUBSCRIBED",
            "marketingCollectedFrom": "OTHER"
          },
          "createdAt": "2005-06-15T15:57:11Z",
          "updatedAt": "2005-06-16T15:57:11Z",
          "numberOfOrders": "25",
          "state": "ENABLED",
          "amountSpent": {
            "amount": "8305.6",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [
            "Bob",
            "Canadian",
            "Léon",
            "Noël"
          ],
          "addresses": [
            {
              "id": "gid://shopify/MailingAddress/544365967?model_name=CustomerAddress",
              "firstName": "Bob",
              "lastName": "Bobsen",
              "address1": "123 Amoebobacterieae St",
              "city": "Ottawa",
              "province": "Ontario",
              "country": "Canada",
              "zip": "K2P0V6",
              "phone": "+1(613)555-1212",
              "name": "Bob Bobsen",
              "provinceCode": "ON",
              "countryCodeV2": "CA"
            }
          ],
          "defaultAddress": {
            "id": "gid://shopify/MailingAddress/544365967?model_name=CustomerAddress",
            "address1": "123 Amoebobacterieae St",
            "city": "Ottawa",
            "province": "Ontario",
            "country": "Canada",
            "zip": "K2P0V6",
            "phone": "+1(613)555-1212",
            "provinceCode": "ON",
            "countryCodeV2": "CA"
          }
        },
        {
          "id": "gid://shopify/Customer/554122808",
          "firstName": "Bob",
          "lastName": "Bobsen",
          "defaultEmailAddress": {
            "emailAddress": "test_remove@example.com",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+13125551212",
            "marketingState": "NOT_SUBSCRIBED",
            "marketingCollectedFrom": "OTHER"
          },
          "createdAt": "2005-06-15T15:57:11Z",
          "updatedAt": "2005-06-16T15:57:11Z",
          "numberOfOrders": "0",
          "state": "ENABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [],
          "defaultAddress": {
            "id": "gid://shopify/MailingAddress/544365967?model_name=CustomerAddress",
            "address1": "123 Amoebobacterieae St",
            "city": "Ottawa",
            "province": "Ontario",
            "country": "Canada",
            "zip": "K2P0V6",
            "phone": "+1(613)555-1212",
            "provinceCode": "ON",
            "countryCodeV2": "CA"
          }
        },
        {
          "id": "gid://shopify/Customer/554456816",
          "firstName": "test",
          "lastName": "test",
          "defaultEmailAddress": null,
          "defaultPhoneNumber": null,
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "DISABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [
            {
              "id": "gid://shopify/MailingAddress/568874073?model_name=CustomerAddress",
              "firstName": "test",
              "lastName": "test",
              "address1": "1005 Jervis St",
              "city": "Ottawa",
              "province": "Ontario",
              "country": "Canada",
              "zip": "V2E 3T1",
              "phone": "+1(613)555-1212",
              "name": "test test",
              "provinceCode": "ON",
              "countryCodeV2": "CA"
            },
            {
              "id": "gid://shopify/MailingAddress/768736626?model_name=CustomerAddress",
              "firstName": "test",
              "lastName": "test",
              "address1": "620 King Street West",
              "city": "Toronto",
              "province": "Ontario",
              "country": "Canada",
              "zip": "M5V 1M6",
              "phone": "+1(613)555-1212",
              "name": "test test",
              "provinceCode": "ON",
              "countryCodeV2": "CA"
            }
          ],
          "defaultAddress": {
            "id": "gid://shopify/MailingAddress/568874073?model_name=CustomerAddress",
            "address1": "1005 Jervis St",
            "city": "Ottawa",
            "province": "Ontario",
            "country": "Canada",
            "zip": "V2E 3T1",
            "phone": "+1(613)555-1212",
            "provinceCode": "ON",
            "countryCodeV2": "CA"
          }
        },
        {
          "id": "gid://shopify/Customer/567375318",
          "firstName": "Jane",
          "lastName": "Smith",
          "defaultEmailAddress": {
            "emailAddress": "janesmith@b2b.example.com",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+13125551217",
            "marketingState": "NOT_SUBSCRIBED",
            "marketingCollectedFrom": null
          },
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "DISABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [],
          "defaultAddress": null
        },
        {
          "id": "gid://shopify/Customer/624407574",
          "firstName": "Bob",
          "lastName": "Bobsen Jr.",
          "defaultEmailAddress": {
            "emailAddress": "tobi.leetsoft@example.com",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": null,
          "createdAt": "2005-06-15T15:57:11Z",
          "updatedAt": "2005-06-16T15:57:11Z",
          "numberOfOrders": "2",
          "state": "ENABLED",
          "amountSpent": {
            "amount": "32.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [
            {
              "id": "gid://shopify/MailingAddress/624407574?model_name=CustomerAddress",
              "firstName": null,
              "lastName": null,
              "address1": "124 Amoebobacterieae St",
              "city": "Ottawa",
              "province": "Ontario",
              "country": "Canada",
              "zip": "K2P0V7",
              "phone": "+1(613)555-1212",
              "name": "",
              "provinceCode": "ON",
              "countryCodeV2": "CA"
            }
          ],
          "defaultAddress": {
            "id": "gid://shopify/MailingAddress/624407574?model_name=CustomerAddress",
            "address1": "124 Amoebobacterieae St",
            "city": "Ottawa",
            "province": "Ontario",
            "country": "Canada",
            "zip": "K2P0V7",
            "phone": "+1(613)555-1212",
            "provinceCode": "ON",
            "countryCodeV2": "CA"
          }
        },
        {
          "id": "gid://shopify/Customer/649400230",
          "firstName": "Bob",
          "lastName": "Bobsen",
          "defaultEmailAddress": {
            "emailAddress": "bob_exempt@example.com",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+13125551226",
            "marketingState": "NOT_SUBSCRIBED",
            "marketingCollectedFrom": null
          },
          "createdAt": "2005-06-15T15:57:11Z",
          "updatedAt": "2005-06-16T15:57:11Z",
          "numberOfOrders": "0",
          "state": "ENABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": true,
          "tags": [],
          "addresses": [],
          "defaultAddress": {
            "id": "gid://shopify/MailingAddress/544365967?model_name=CustomerAddress",
            "address1": "123 Amoebobacterieae St",
            "city": "Ottawa",
            "province": "Ontario",
            "country": "Canada",
            "zip": "K2P0V6",
            "phone": "+1(613)555-1212",
            "provinceCode": "ON",
            "countryCodeV2": "CA"
          }
        },
        {
          "id": "gid://shopify/Customer/649509010",
          "firstName": "Bob",
          "lastName": "Bobsen",
          "defaultEmailAddress": {
            "emailAddress": "email@example.com",
            "marketingState": "SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+13125551215",
            "marketingState": "NOT_SUBSCRIBED",
            "marketingCollectedFrom": null
          },
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "ENABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [
            {
              "id": "gid://shopify/MailingAddress/649509010?model_name=CustomerAddress",
              "firstName": "Bob",
              "lastName": "Bobsen",
              "address1": "",
              "city": "Ottawa",
              "province": "",
              "country": "",
              "zip": "",
              "phone": "+1(613)555-1212",
              "name": "Bob Bobsen",
              "provinceCode": null,
              "countryCodeV2": null
            }
          ],
          "defaultAddress": {
            "id": "gid://shopify/MailingAddress/649509010?model_name=CustomerAddress",
            "address1": "",
            "city": "Ottawa",
            "province": "",
            "country": "",
            "zip": "",
            "phone": "+1(613)555-1212",
            "provinceCode": null,
            "countryCodeV2": null
          }
        },
        {
          "id": "gid://shopify/Customer/657584747",
          "firstName": "Jane",
          "lastName": "Deletable",
          "defaultEmailAddress": {
            "emailAddress": "jane_deletable@b2b.example.com",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+13125551218",
            "marketingState": "NOT_SUBSCRIBED",
            "marketingCollectedFrom": null
          },
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "DISABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [],
          "defaultAddress": null
        },
        {
          "id": "gid://shopify/Customer/681865419",
          "firstName": "Signup",
          "lastName": "Bot",
          "defaultEmailAddress": {
            "emailAddress": "bot@suppression.com",
            "marketingState": "SUBSCRIBED"
          },
          "defaultPhoneNumber": null,
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "DISABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [],
          "defaultAddress": null
        },
        {
          "id": "gid://shopify/Customer/839649557",
          "firstName": "Bob",
          "lastName": "Bobsen",
          "defaultEmailAddress": {
            "emailAddress": "test_example@example.com",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+16136120709",
            "marketingState": "NOT_SUBSCRIBED",
            "marketingCollectedFrom": null
          },
          "createdAt": "2005-06-15T15:57:11Z",
          "updatedAt": "2005-06-16T15:57:11Z",
          "numberOfOrders": "0",
          "state": "ENABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [],
          "defaultAddress": {
            "id": "gid://shopify/MailingAddress/544365967?model_name=CustomerAddress",
            "address1": "123 Amoebobacterieae St",
            "city": "Ottawa",
            "province": "Ontario",
            "country": "Canada",
            "zip": "K2P0V6",
            "phone": "+1(613)555-1212",
            "provinceCode": "ON",
            "countryCodeV2": "CA"
          }
        },
        {
          "id": "gid://shopify/Customer/880980251",
          "firstName": "Danny",
          "lastName": "Doe",
          "defaultEmailAddress": {
            "emailAddress": "dannydoe@b2bmigration.com",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+14155483921",
            "marketingState": "NOT_SUBSCRIBED",
            "marketingCollectedFrom": null
          },
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "DISABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [
            {
              "id": "gid://shopify/MailingAddress/420236291?model_name=CustomerAddress",
              "firstName": "Danny",
              "lastName": "Doe",
              "address1": "1005 Jervis St",
              "city": "Ottawa",
              "province": "British Columbia",
              "country": "Canada",
              "zip": "V2E3T1",
              "phone": "16135551212",
              "name": "Danny Doe",
              "provinceCode": "BC",
              "countryCodeV2": "CA"
            }
          ],
          "defaultAddress": {
            "id": "gid://shopify/MailingAddress/420236291?model_name=CustomerAddress",
            "address1": "1005 Jervis St",
            "city": "Ottawa",
            "province": "British Columbia",
            "country": "Canada",
            "zip": "V2E3T1",
            "phone": "16135551212",
            "provinceCode": "BC",
            "countryCodeV2": "CA"
          }
        },
        {
          "id": "gid://shopify/Customer/912646312",
          "firstName": "Bob",
          "lastName": "Bulk",
          "defaultEmailAddress": {
            "emailAddress": "bobbulk@example.com",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": null,
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "INVITED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [],
          "defaultAddress": null
        },
        {
          "id": "gid://shopify/Customer/953307753",
          "firstName": "Adam",
          "lastName": "Felix",
          "defaultEmailAddress": {
            "emailAddress": "b2b@example.com",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+13125551213",
            "marketingState": "NOT_SUBSCRIBED",
            "marketingCollectedFrom": null
          },
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "0",
          "state": "DISABLED",
          "amountSpent": {
            "amount": "0.0",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [],
          "addresses": [],
          "defaultAddress": null
        },
        {
          "id": "gid://shopify/Customer/1018520244",
          "firstName": "Bob",
          "lastName": "Bobsen",
          "defaultEmailAddress": {
            "emailAddress": "bob@example.org",
            "marketingState": "NOT_SUBSCRIBED"
          },
          "defaultPhoneNumber": {
            "phoneNumber": "+13125551216",
            "marketingState": "NOT_SUBSCRIBED",
            "marketingCollectedFrom": "OTHER"
          },
          "createdAt": "2025-04-15T19:26:33Z",
          "updatedAt": "2025-04-15T19:26:33Z",
          "numberOfOrders": "12",
          "state": "ENABLED",
          "amountSpent": {
            "amount": "100122.5",
            "currencyCode": "USD"
          },
          "verifiedEmail": true,
          "taxExempt": false,
          "tags": [
            "A+ Marketing",
            "Canadian"
          ],
          "addresses": [
            {
              "id": "gid://shopify/MailingAddress/1018520244?model_name=CustomerAddress",
              "firstName": null,
              "lastName": null,
              "address1": "123 Amoebobacterieae St",
              "city": "Ottawa",
              "province": "Ontario",
              "country": "Canada",
              "zip": "K2P0V6",
              "phone": "+1(613)555-1212",
              "name": "",
              "provinceCode": "ON",
              "countryCodeV2": "CA"
            }
          ],
          "defaultAddress": {
            "id": "gid://shopify/MailingAddress/1018520244?model_name=CustomerAddress",
            "address1": "123 Amoebobacterieae St",
            "city": "Ottawa",
            "province": "Ontario",
            "country": "Canada",
            "zip": "K2P0V6",
            "phone": "+1(613)555-1212",
            "provinceCode": "ON",
            "countryCodeV2": "CA"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the first 10 customers updated after December 1, 2019

  #### Description

  This query retrieves the customer ID and last updated timestamp for the first 10 \[customer]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/customer) records that have been updated after December 1, 2019. The example demonstrates how to use the \[\`updated\_at\`]\(https://shopify.dev/docs/api/admin-graphql/latest/queries/customers#argument-query-filter-updated\_at) parameter to filter results for a specific day when customer information was last modified.

  #### Query

  ```graphql
  query {
    customers(first: 10, query: "updated_at:>2019-12-01") {
      edges {
        node {
          id
          firstName
          lastName
          updatedAt
        }
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
  "query": "query { customers(first: 10, query: \"updated_at:>2019-12-01\") { edges { node { id firstName lastName updatedAt } } } }"
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
      customers(first: 10, query: "updated_at:>2019-12-01") {
        edges {
          node {
            id
            firstName
            lastName
            updatedAt
          }
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
    query {
      customers(first: 10, query: "updated_at:>2019-12-01") {
        edges {
          node {
            id
            firstName
            lastName
            updatedAt
          }
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
    data: `query {
      customers(first: 10, query: "updated_at:>2019-12-01") {
        edges {
          node {
            id
            firstName
            lastName
            updatedAt
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    customers(first: 10, query: "updated_at:>2019-12-01") {
      edges {
        node {
          id
          firstName
          lastName
          updatedAt
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "customers": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Customer/56501169",
            "firstName": "Jenny",
            "lastName": "Test",
            "updatedAt": "2025-04-15T19:26:33Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/105906728",
            "firstName": "John",
            "lastName": "Smith",
            "updatedAt": "2025-04-15T19:26:33Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/305367469",
            "firstName": "Test",
            "lastName": "Customer",
            "updatedAt": "2025-04-15T19:26:33Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/317070273",
            "firstName": "Bob",
            "lastName": "Norman",
            "updatedAt": "2025-04-15T19:26:33Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/324586928",
            "firstName": "B2B",
            "lastName": "Customer",
            "updatedAt": "2025-04-15T19:26:33Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/352184960",
            "firstName": "Jenny",
            "lastName": "Doe",
            "updatedAt": "2025-04-15T19:26:33Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/408913340",
            "firstName": "John",
            "lastName": "Doe",
            "updatedAt": "2025-04-15T19:26:33Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/529223679",
            "firstName": "Bob",
            "lastName": "Marketing",
            "updatedAt": "2025-04-15T19:26:33Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/554456816",
            "firstName": "test",
            "lastName": "test",
            "updatedAt": "2025-04-15T19:26:33Z"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/567375318",
            "firstName": "Jane",
            "lastName": "Smith",
            "updatedAt": "2025-04-15T19:26:33Z"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the first 10 customers using pagination

  #### Description

  example.description = <<\~DESC This query retrieves the first 10 \[customer]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/customer) records using \[forward pagination]\(https://shopify.dev/docs/api/usage/pagination-graphql#forward-pagination). For each customer, it fetches the \`edge\` containing its \`cursor\` and \`node\`. It also retrieves the \[\`pageInfo\`]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo) object, requesting \`hasNextPage\` to check if more pages follow and \`endCursor\` for last customer in this set.

  #### Query

  ```graphql
  query {
    customers(first: 10) {
      edges {
        cursor
        node {
          id
          firstName
          lastName
          defaultEmailAddress {
            emailAddress
          }
          defaultPhoneNumber {
            phoneNumber
          }
          createdAt
          updatedAt
          numberOfOrders
          state
        }
      }
      pageInfo {
        hasNextPage
        endCursor
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
  "query": "query { customers(first: 10) { edges { cursor node { id firstName lastName defaultEmailAddress { emailAddress } defaultPhoneNumber { phoneNumber } createdAt updatedAt numberOfOrders state } } pageInfo { hasNextPage endCursor } } }"
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
      customers(first: 10) {
        edges {
          cursor
          node {
            id
            firstName
            lastName
            defaultEmailAddress {
              emailAddress
            }
            defaultPhoneNumber {
              phoneNumber
            }
            createdAt
            updatedAt
            numberOfOrders
            state
          }
        }
        pageInfo {
          hasNextPage
          endCursor
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
    query {
      customers(first: 10) {
        edges {
          cursor
          node {
            id
            firstName
            lastName
            defaultEmailAddress {
              emailAddress
            }
            defaultPhoneNumber {
              phoneNumber
            }
            createdAt
            updatedAt
            numberOfOrders
            state
          }
        }
        pageInfo {
          hasNextPage
          endCursor
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
    data: `query {
      customers(first: 10) {
        edges {
          cursor
          node {
            id
            firstName
            lastName
            defaultEmailAddress {
              emailAddress
            }
            defaultPhoneNumber {
              phoneNumber
            }
            createdAt
            updatedAt
            numberOfOrders
            state
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    customers(first: 10) {
      edges {
        cursor
        node {
          id
          firstName
          lastName
          defaultEmailAddress {
            emailAddress
          }
          defaultPhoneNumber {
            phoneNumber
          }
          createdAt
          updatedAt
          numberOfOrders
          state
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "customers": {
      "edges": [
        {
          "cursor": "eyJsYXN0X2lkIjo1NjUwMTE2OSwibGFzdF92YWx1ZSI6IjU2NTAxMTY5In0=",
          "node": {
            "id": "gid://shopify/Customer/56501169",
            "firstName": "Jenny",
            "lastName": "Test",
            "defaultEmailAddress": {
              "emailAddress": "jennytest@b2b.example.com"
            },
            "defaultPhoneNumber": {
              "phoneNumber": "+13125551219"
            },
            "createdAt": "2025-04-15T19:26:33Z",
            "updatedAt": "2025-04-15T19:26:33Z",
            "numberOfOrders": "0",
            "state": "DISABLED"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjoxMDU5MDY3MjgsImxhc3RfdmFsdWUiOiIxMDU5MDY3MjgifQ==",
          "node": {
            "id": "gid://shopify/Customer/105906728",
            "firstName": "John",
            "lastName": "Smith",
            "defaultEmailAddress": {
              "emailAddress": "johnsmith@example.com"
            },
            "defaultPhoneNumber": {
              "phoneNumber": "+16134504532"
            },
            "createdAt": "2025-04-15T19:26:33Z",
            "updatedAt": "2025-04-15T19:26:33Z",
            "numberOfOrders": "0",
            "state": "DISABLED"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjozMDUzNjc0NjksImxhc3RfdmFsdWUiOiIzMDUzNjc0NjkifQ==",
          "node": {
            "id": "gid://shopify/Customer/305367469",
            "firstName": "Test",
            "lastName": "Customer",
            "defaultEmailAddress": null,
            "defaultPhoneNumber": null,
            "createdAt": "2025-04-15T19:26:33Z",
            "updatedAt": "2025-04-15T19:26:33Z",
            "numberOfOrders": "0",
            "state": "DISABLED"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjozMTcwNzAyNzMsImxhc3RfdmFsdWUiOiIzMTcwNzAyNzMifQ==",
          "node": {
            "id": "gid://shopify/Customer/317070273",
            "firstName": "Bob",
            "lastName": "Norman",
            "defaultEmailAddress": null,
            "defaultPhoneNumber": {
              "phoneNumber": "+16134504538"
            },
            "createdAt": "2025-04-15T19:26:33Z",
            "updatedAt": "2025-04-15T19:26:33Z",
            "numberOfOrders": "0",
            "state": "DISABLED"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjozMjQ1ODY5MjgsImxhc3RfdmFsdWUiOiIzMjQ1ODY5MjgifQ==",
          "node": {
            "id": "gid://shopify/Customer/324586928",
            "firstName": "B2B",
            "lastName": "Customer",
            "defaultEmailAddress": {
              "emailAddress": "b2b@example.com"
            },
            "defaultPhoneNumber": {
              "phoneNumber": "+13125551213"
            },
            "createdAt": "2025-04-15T19:26:33Z",
            "updatedAt": "2025-04-15T19:26:33Z",
            "numberOfOrders": "1",
            "state": "ENABLED"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjozNTIxODQ5NjAsImxhc3RfdmFsdWUiOiIzNTIxODQ5NjAifQ==",
          "node": {
            "id": "gid://shopify/Customer/352184960",
            "firstName": "Jenny",
            "lastName": "Doe",
            "defaultEmailAddress": {
              "emailAddress": "jennydoe@b2bmigration.com"
            },
            "defaultPhoneNumber": null,
            "createdAt": "2025-04-15T19:26:33Z",
            "updatedAt": "2025-04-15T19:26:33Z",
            "numberOfOrders": "0",
            "state": "DISABLED"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjo0MDg5MTMzNDAsImxhc3RfdmFsdWUiOiI0MDg5MTMzNDAifQ==",
          "node": {
            "id": "gid://shopify/Customer/408913340",
            "firstName": "John",
            "lastName": "Doe",
            "defaultEmailAddress": {
              "emailAddress": "john@doe.com"
            },
            "defaultPhoneNumber": {
              "phoneNumber": "+16134504534"
            },
            "createdAt": "2025-04-15T19:26:33Z",
            "updatedAt": "2025-04-15T19:26:33Z",
            "numberOfOrders": "0",
            "state": "DISABLED"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjo1MjkyMjM2NzksImxhc3RfdmFsdWUiOiI1MjkyMjM2NzkifQ==",
          "node": {
            "id": "gid://shopify/Customer/529223679",
            "firstName": "Bob",
            "lastName": "Marketing",
            "defaultEmailAddress": {
              "emailAddress": "email_marketing_pending_customer@example.com"
            },
            "defaultPhoneNumber": null,
            "createdAt": "2025-04-15T19:26:33Z",
            "updatedAt": "2025-04-15T19:26:33Z",
            "numberOfOrders": "0",
            "state": "DISABLED"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjo1NDQzNjU5NjcsImxhc3RfdmFsdWUiOiI1NDQzNjU5NjcifQ==",
          "node": {
            "id": "gid://shopify/Customer/544365967",
            "firstName": "Bob",
            "lastName": "Bobsen",
            "defaultEmailAddress": {
              "emailAddress": "bob@example.com"
            },
            "defaultPhoneNumber": {
              "phoneNumber": "+13125551212"
            },
            "createdAt": "2005-06-15T15:57:11Z",
            "updatedAt": "2005-06-16T15:57:11Z",
            "numberOfOrders": "25",
            "state": "ENABLED"
          }
        },
        {
          "cursor": "eyJsYXN0X2lkIjo1NTQxMjI4MDgsImxhc3RfdmFsdWUiOiI1NTQxMjI4MDgifQ==",
          "node": {
            "id": "gid://shopify/Customer/554122808",
            "firstName": "Bob",
            "lastName": "Bobsen",
            "defaultEmailAddress": {
              "emailAddress": "test_remove@example.com"
            },
            "defaultPhoneNumber": {
              "phoneNumber": "+13125551212"
            },
            "createdAt": "2005-06-15T15:57:11Z",
            "updatedAt": "2005-06-16T15:57:11Z",
            "numberOfOrders": "0",
            "state": "ENABLED"
          }
        }
      ],
      "pageInfo": {
        "hasNextPage": true,
        "endCursor": "eyJsYXN0X2lkIjo1NTQxMjI4MDgsImxhc3RfdmFsdWUiOiI1NTQxMjI4MDgifQ=="
      }
    }
  }
  ```

* ### Retrieve the first 10 customers with an enabled customer account

  #### Description

  This query retrieves basic information for the first 10 \[customer]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/customer) records who have enabled their customer account. The query demonstrates filtering using the \[\`state\`]\(https://shopify.dev/docs/api/admin-graphql/latest/queries/customers#argument-query-filter-state) parameter, and also requests the \`state\` field in the response to show the resulting account status.

  #### Query

  ```graphql
  query {
    customers(first: 10, query: "state:'ENABLED'") {
      edges {
        node {
          id
          firstName
          lastName
          defaultEmailAddress {
            emailAddress
          }
          state
        }
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
  "query": "query { customers(first: 10, query: \"state:'\''ENABLED'\''\") { edges { node { id firstName lastName defaultEmailAddress { emailAddress } state } } } }"
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
      customers(first: 10, query: "state:'ENABLED'") {
        edges {
          node {
            id
            firstName
            lastName
            defaultEmailAddress {
              emailAddress
            }
            state
          }
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
    query {
      customers(first: 10, query: "state:'ENABLED'") {
        edges {
          node {
            id
            firstName
            lastName
            defaultEmailAddress {
              emailAddress
            }
            state
          }
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
    data: `query {
      customers(first: 10, query: "state:'ENABLED'") {
        edges {
          node {
            id
            firstName
            lastName
            defaultEmailAddress {
              emailAddress
            }
            state
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    customers(first: 10, query: "state:'ENABLED'") {
      edges {
        node {
          id
          firstName
          lastName
          defaultEmailAddress {
            emailAddress
          }
          state
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "customers": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Customer/324586928",
            "firstName": "B2B",
            "lastName": "Customer",
            "defaultEmailAddress": {
              "emailAddress": "b2b@example.com"
            },
            "state": "ENABLED"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/544365967",
            "firstName": "Bob",
            "lastName": "Bobsen",
            "defaultEmailAddress": {
              "emailAddress": "bob@example.com"
            },
            "state": "ENABLED"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/554122808",
            "firstName": "Bob",
            "lastName": "Bobsen",
            "defaultEmailAddress": {
              "emailAddress": "test_remove@example.com"
            },
            "state": "ENABLED"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/624407574",
            "firstName": "Bob",
            "lastName": "Bobsen Jr.",
            "defaultEmailAddress": {
              "emailAddress": "tobi.leetsoft@example.com"
            },
            "state": "ENABLED"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/649400230",
            "firstName": "Bob",
            "lastName": "Bobsen",
            "defaultEmailAddress": {
              "emailAddress": "bob_exempt@example.com"
            },
            "state": "ENABLED"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/649509010",
            "firstName": "Bob",
            "lastName": "Bobsen",
            "defaultEmailAddress": {
              "emailAddress": "email@example.com"
            },
            "state": "ENABLED"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/839649557",
            "firstName": "Bob",
            "lastName": "Bobsen",
            "defaultEmailAddress": {
              "emailAddress": "test_example@example.com"
            },
            "state": "ENABLED"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/1018520244",
            "firstName": "Bob",
            "lastName": "Bobsen",
            "defaultEmailAddress": {
              "emailAddress": "bob@example.org"
            },
            "state": "ENABLED"
          }
        }
      ]
    }
  }
  ```

* ### Retrieve the first five customers in Canada

  #### Description

  This query retrieves basic information, such as first name and last name for the first five \[customer]\(https://shopify.dev/docs/api/admin-graphql/latest/objects/customer) records located in Canada. Use the \[\`country\`]\(https://shopify.dev/docs/api/admin-graphql/latest/queries/customers#argument-query-filter-country) filter to specify the country.

  #### Query

  ```graphql
  query {
    customers(first: 5, query: "country:canada") {
      edges {
        node {
          id
          firstName
          lastName
        }
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
  "query": "query { customers(first: 5, query: \"country:canada\") { edges { node { id firstName lastName } } } }"
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
      customers(first: 5, query: "country:canada") {
        edges {
          node {
            id
            firstName
            lastName
          }
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
    query {
      customers(first: 5, query: "country:canada") {
        edges {
          node {
            id
            firstName
            lastName
          }
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
    data: `query {
      customers(first: 5, query: "country:canada") {
        edges {
          node {
            id
            firstName
            lastName
          }
        }
      }
    }`,
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query {
    customers(first: 5, query: "country:canada") {
      edges {
        node {
          id
          firstName
          lastName
        }
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "customers": {
      "edges": [
        {
          "node": {
            "id": "gid://shopify/Customer/105906728",
            "firstName": "John",
            "lastName": "Smith"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/408913340",
            "firstName": "John",
            "lastName": "Doe"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/544365967",
            "firstName": "Bob",
            "lastName": "Bobsen"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/554456816",
            "firstName": "test",
            "lastName": "test"
          }
        },
        {
          "node": {
            "id": "gid://shopify/Customer/624407574",
            "firstName": "Bob",
            "lastName": "Bobsen Jr."
          }
        }
      ]
    }
  }
  ```
