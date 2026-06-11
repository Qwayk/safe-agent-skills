---
title: staffMember - GraphQL Admin
description: >-
  Retrieves a [staff
  member](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember)
  by ID. If no ID is provided, the query returns the staff member that's making
  the request. A staff member is a user who can access the Shopify admin to
  manage store operations.


  Provides staff member details such as email, name, and shop owner status. When
  querying the current user (with or without an ID), additional [private
  data](https://shopify.dev/docs/api/admin-graphql/latest/queries/staffMember#returns-StaffMember.fields.privateData)
  becomes available.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/staffMember'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/staffMember.md'
---

# staff​Member

query

Retrieves a [staff member](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember) by ID. If no ID is provided, the query returns the staff member that's making the request. A staff member is a user who can access the Shopify admin to manage store operations.

Provides staff member details such as email, name, and shop owner status. When querying the current user (with or without an ID), additional [private data](https://shopify.dev/docs/api/admin-graphql/latest/queries/staffMember#returns-StaffMember.fields.privateData) becomes available.

## Arguments

* id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the staff member to return. If no ID is provided, then the staff member making the query (if any) is returned.

***

## Possible returns

* Staff​Member

  [Staff​Member](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMember)

  A user account that can access the Shopify admin to manage store operations. Includes personal information and account status.

  You can assign staff members to [`CompanyLocation`](https://shopify.dev/docs/api/admin-graphql/latest/objects/CompanyLocation) objects for [B2B operations](https://shopify.dev/docs/apps/build/b2b), limiting their actions to those locations.

  * account​Type

    [Account​Type](https://shopify.dev/docs/api/admin-graphql/latest/enums/AccountType)

    The type of account the staff member has.

  * active

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the staff member is active.

  * avatar

    [Image!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Image)

    non-null

    The image used as the staff member's avatar in the Shopify admin.

    * max​Width

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      Deprecated

      ### Arguments

    * max​Height

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      Deprecated

    * fallback

      [Staff​Member​Default​Image](https://shopify.dev/docs/api/admin-graphql/latest/enums/StaffMemberDefaultImage)

      Default:DEFAULT

      The default image returned if the staff member has no avatar.

    ***

  * email

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The staff member's email address.

  * exists

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the staff member's account exists.

  * first​Name

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The staff member's first name.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * initials

    [\[String!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The staff member's initials, if available.

  * is​Shop​Owner

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the staff member is the shop owner.

  * last​Name

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The staff member's last name.

  * locale

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The staff member's preferred locale. Locale values use the format `language` or `language-COUNTRY`, where `language` is a two-letter language code, and `COUNTRY` is a two-letter country code. For example: `en` or `en-US`

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The staff member's full name.

  * phone

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The staff member's phone number.

  * private​Data

    [Staff​Member​Private​Data!](https://shopify.dev/docs/api/admin-graphql/latest/objects/StaffMemberPrivateData)

    non-null

    The data used to customize the Shopify admin experience for the staff member.

***

## Examples

* ### Retrieves a single user

  #### Query

  ```graphql
  query StaffMember($id: ID!) {
    staffMember(id: $id) {
      active
      avatar {
        url
      }
      email
      exists
      firstName
      id
      initials
      isShopOwner
      lastName
      locale
      name
      phone
    }
  }
  ```

  #### Variables

  ```json
  {
    "id": "gid://shopify/StaffMember/902541635"
  }
  ```

  #### cURL

  ```bash
  curl -X POST \
  https://your-development-store.myshopify.com/admin/api/2026-01/graphql.json \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Access-Token: {access_token}' \
  -d '{
  "query": "query StaffMember($id: ID!) { staffMember(id: $id) { active avatar { url } email exists firstName id initials isShopOwner lastName locale name phone } }",
   "variables": {
      "id": "gid://shopify/StaffMember/902541635"
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
    query StaffMember($id: ID!) {
      staffMember(id: $id) {
        active
        avatar {
          url
        }
        email
        exists
        firstName
        id
        initials
        isShopOwner
        lastName
        locale
        name
        phone
      }
    }`,
    {
      variables: {
          "id": "gid://shopify/StaffMember/902541635"
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
    query StaffMember($id: ID!) {
      staffMember(id: $id) {
        active
        avatar {
          url
        }
        email
        exists
        firstName
        id
        initials
        isShopOwner
        lastName
        locale
        name
        phone
      }
    }
  QUERY

  variables = {
    "id": "gid://shopify/StaffMember/902541635"
  }

  response = client.query(query: query, variables: variables)
  ```

  #### Node.js

  ```javascript
  const client = new shopify.clients.Graphql({session});
  const data = await client.query({
    data: {
      "query": `query StaffMember($id: ID!) {
        staffMember(id: $id) {
          active
          avatar {
            url
          }
          email
          exists
          firstName
          id
          initials
          isShopOwner
          lastName
          locale
          name
          phone
        }
      }`,
      "variables": {
          "id": "gid://shopify/StaffMember/902541635"
      },
    },
  });
  ```

  #### Shopify CLI

  ```bash
  shopify app execute \
  --query \
  'query StaffMember($id: ID!) {
    staffMember(id: $id) {
      active
      avatar {
        url
      }
      email
      exists
      firstName
      id
      initials
      isShopOwner
      lastName
      locale
      name
      phone
    }
  }' \
  --variables \
  '{
    "id": "gid://shopify/StaffMember/902541635"
  }'
  ```

  #### Response

  ```json
  {
    "staffMember": {
      "active": true,
      "avatar": {
        "url": "https://cdn.shopify.com/s/files/1/2637/1970/users/foo.jpg?v=1731443626"
      },
      "email": "bob@example.com",
      "exists": true,
      "firstName": "bob",
      "id": "gid://shopify/StaffMember/902541635",
      "initials": [
        "b",
        "b"
      ],
      "isShopOwner": true,
      "lastName": "bobsen",
      "locale": "en",
      "name": "bob bobsen",
      "phone": null
    }
  }
  ```

* ### Retrieves the currently logged-in user

  #### Query

  ```graphql
  query {
    staffMember {
      active
      avatar {
        url
      }
      email
      exists
      firstName
      id
      initials
      isShopOwner
      lastName
      locale
      name
      phone
      privateData {
        accountSettingsUrl
        createdAt
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
  "query": "query { staffMember { active avatar { url } email exists firstName id initials isShopOwner lastName locale name phone privateData { accountSettingsUrl createdAt } } }"
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
      staffMember {
        active
        avatar {
          url
        }
        email
        exists
        firstName
        id
        initials
        isShopOwner
        lastName
        locale
        name
        phone
        privateData {
          accountSettingsUrl
          createdAt
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
      staffMember {
        active
        avatar {
          url
        }
        email
        exists
        firstName
        id
        initials
        isShopOwner
        lastName
        locale
        name
        phone
        privateData {
          accountSettingsUrl
          createdAt
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
      staffMember {
        active
        avatar {
          url
        }
        email
        exists
        firstName
        id
        initials
        isShopOwner
        lastName
        locale
        name
        phone
        privateData {
          accountSettingsUrl
          createdAt
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
    staffMember {
      active
      avatar {
        url
      }
      email
      exists
      firstName
      id
      initials
      isShopOwner
      lastName
      locale
      name
      phone
      privateData {
        accountSettingsUrl
        createdAt
      }
    }
  }'
  ```

  #### Response

  ```json
  {
    "staffMember": {
      "active": true,
      "avatar": {
        "url": "https://cdn.shopify.com/s/files/1/2637/1970/users/foo.jpg?v=1731443626"
      },
      "email": "bob@example.com",
      "exists": true,
      "firstName": "bob",
      "id": "gid://shopify/StaffMember/902541635",
      "initials": [
        "b",
        "b"
      ],
      "isShopOwner": true,
      "lastName": "bobsen",
      "locale": "en",
      "name": "bob bobsen",
      "phone": null,
      "privateData": {
        "accountSettingsUrl": "https://www.snowdevil.ca/admin/settings/account/902541635",
        "createdAt": "2005-01-01T00:00:00Z"
      }
    }
  }
  ```
