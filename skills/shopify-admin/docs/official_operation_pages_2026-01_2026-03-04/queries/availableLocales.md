---
title: availableLocales - GraphQL Admin
description: >-
  Returns all locales that Shopify supports. Each
  [`Locale`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Locale)
  includes an ISO code and human-readable name. Use this query to discover which
  locales you can enable on a shop with the
  [`shopLocaleEnable`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/shopLocaleEnable)
  mutation.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/availableLocales'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/availableLocales.md
---

# available​Locales

query

Returns all locales that Shopify supports. Each [`Locale`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Locale) includes an ISO code and human-readable name. Use this query to discover which locales you can enable on a shop with the [`shopLocaleEnable`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/shopLocaleEnable) mutation.

## Possible returns

* Locale

  [\[Locale!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Locale)

  A locale.

  * iso​Code

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    Locale ISO code.

  * name

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    Human-readable locale name.

***

## Examples

* ### Retrieve a list of available locales

  #### Description

  The following query retrieves a list of locales that you can enable for a shop, including their ISO country code and name.

  #### Query

  ```graphql
  query {
    availableLocales {
      isoCode
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
  "query": "query { availableLocales { isoCode name } }"
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
      availableLocales {
        isoCode
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
      availableLocales {
        isoCode
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
      availableLocales {
        isoCode
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
    availableLocales {
      isoCode
      name
    }
  }'
  ```

  #### Response

  ```json
  {
    "availableLocales": [
      {
        "isoCode": "af",
        "name": "Afrikaans"
      },
      {
        "isoCode": "ak",
        "name": "Akan"
      },
      {
        "isoCode": "sq",
        "name": "Albanian"
      },
      {
        "isoCode": "am",
        "name": "Amharic"
      },
      {
        "isoCode": "ar",
        "name": "Arabic"
      },
      {
        "isoCode": "hy",
        "name": "Armenian"
      },
      {
        "isoCode": "as",
        "name": "Assamese"
      },
      {
        "isoCode": "az",
        "name": "Azerbaijani"
      },
      {
        "isoCode": "bm",
        "name": "Bambara"
      },
      {
        "isoCode": "bn",
        "name": "Bangla"
      },
      {
        "isoCode": "eu",
        "name": "Basque"
      },
      {
        "isoCode": "be",
        "name": "Belarusian"
      },
      {
        "isoCode": "bs",
        "name": "Bosnian"
      },
      {
        "isoCode": "br",
        "name": "Breton"
      },
      {
        "isoCode": "bg",
        "name": "Bulgarian"
      },
      {
        "isoCode": "my",
        "name": "Burmese"
      },
      {
        "isoCode": "ca",
        "name": "Catalan"
      },
      {
        "isoCode": "ckb",
        "name": "Central Kurdish"
      },
      {
        "isoCode": "ce",
        "name": "Chechen"
      },
      {
        "isoCode": "zh-CN",
        "name": "Chinese (Simplified)"
      },
      {
        "isoCode": "zh-TW",
        "name": "Chinese (Traditional)"
      },
      {
        "isoCode": "kw",
        "name": "Cornish"
      },
      {
        "isoCode": "hr",
        "name": "Croatian"
      },
      {
        "isoCode": "cs",
        "name": "Czech"
      },
      {
        "isoCode": "da",
        "name": "Danish"
      },
      {
        "isoCode": "nl",
        "name": "Dutch"
      },
      {
        "isoCode": "dz",
        "name": "Dzongkha"
      },
      {
        "isoCode": "en",
        "name": "English"
      },
      {
        "isoCode": "eo",
        "name": "Esperanto"
      },
      {
        "isoCode": "et",
        "name": "Estonian"
      },
      {
        "isoCode": "ee",
        "name": "Ewe"
      },
      {
        "isoCode": "fo",
        "name": "Faroese"
      },
      {
        "isoCode": "fil",
        "name": "Filipino"
      },
      {
        "isoCode": "fi",
        "name": "Finnish"
      },
      {
        "isoCode": "fr",
        "name": "French"
      },
      {
        "isoCode": "ff",
        "name": "Fulah"
      },
      {
        "isoCode": "gl",
        "name": "Galician"
      },
      {
        "isoCode": "lg",
        "name": "Ganda"
      },
      {
        "isoCode": "ka",
        "name": "Georgian"
      },
      {
        "isoCode": "de",
        "name": "German"
      },
      {
        "isoCode": "el",
        "name": "Greek"
      },
      {
        "isoCode": "gu",
        "name": "Gujarati"
      },
      {
        "isoCode": "ha",
        "name": "Hausa"
      },
      {
        "isoCode": "he",
        "name": "Hebrew"
      },
      {
        "isoCode": "hi",
        "name": "Hindi"
      },
      {
        "isoCode": "hu",
        "name": "Hungarian"
      },
      {
        "isoCode": "is",
        "name": "Icelandic"
      },
      {
        "isoCode": "ig",
        "name": "Igbo"
      },
      {
        "isoCode": "id",
        "name": "Indonesian"
      },
      {
        "isoCode": "ia",
        "name": "Interlingua"
      },
      {
        "isoCode": "ga",
        "name": "Irish"
      },
      {
        "isoCode": "it",
        "name": "Italian"
      },
      {
        "isoCode": "ja",
        "name": "Japanese"
      },
      {
        "isoCode": "jv",
        "name": "Javanese"
      },
      {
        "isoCode": "kl",
        "name": "Kalaallisut"
      },
      {
        "isoCode": "kn",
        "name": "Kannada"
      },
      {
        "isoCode": "ks",
        "name": "Kashmiri"
      },
      {
        "isoCode": "kk",
        "name": "Kazakh"
      },
      {
        "isoCode": "km",
        "name": "Khmer"
      },
      {
        "isoCode": "ki",
        "name": "Kikuyu"
      },
      {
        "isoCode": "rw",
        "name": "Kinyarwanda"
      },
      {
        "isoCode": "ko",
        "name": "Korean"
      },
      {
        "isoCode": "ku",
        "name": "Kurdish"
      },
      {
        "isoCode": "ky",
        "name": "Kyrgyz"
      },
      {
        "isoCode": "lo",
        "name": "Lao"
      },
      {
        "isoCode": "lv",
        "name": "Latvian"
      },
      {
        "isoCode": "ln",
        "name": "Lingala"
      },
      {
        "isoCode": "lt",
        "name": "Lithuanian"
      },
      {
        "isoCode": "lu",
        "name": "Luba-Katanga"
      },
      {
        "isoCode": "lb",
        "name": "Luxembourgish"
      },
      {
        "isoCode": "mk",
        "name": "Macedonian"
      },
      {
        "isoCode": "mg",
        "name": "Malagasy"
      },
      {
        "isoCode": "ms",
        "name": "Malay"
      },
      {
        "isoCode": "ml",
        "name": "Malayalam"
      },
      {
        "isoCode": "mt",
        "name": "Maltese"
      },
      {
        "isoCode": "gv",
        "name": "Manx"
      },
      {
        "isoCode": "mr",
        "name": "Marathi"
      },
      {
        "isoCode": "mn",
        "name": "Mongolian"
      },
      {
        "isoCode": "mi",
        "name": "Māori"
      },
      {
        "isoCode": "ne",
        "name": "Nepali"
      },
      {
        "isoCode": "nd",
        "name": "North Ndebele"
      },
      {
        "isoCode": "se",
        "name": "Northern Sami"
      },
      {
        "isoCode": "no",
        "name": "Norwegian"
      },
      {
        "isoCode": "nb",
        "name": "Norwegian (Bokmål)"
      },
      {
        "isoCode": "nn",
        "name": "Norwegian Nynorsk"
      },
      {
        "isoCode": "or",
        "name": "Odia"
      },
      {
        "isoCode": "om",
        "name": "Oromo"
      },
      {
        "isoCode": "os",
        "name": "Ossetic"
      },
      {
        "isoCode": "ps",
        "name": "Pashto"
      },
      {
        "isoCode": "fa",
        "name": "Persian"
      },
      {
        "isoCode": "pl",
        "name": "Polish"
      },
      {
        "isoCode": "pt-BR",
        "name": "Portuguese (Brazil)"
      },
      {
        "isoCode": "pt-PT",
        "name": "Portuguese (Portugal)"
      },
      {
        "isoCode": "pa",
        "name": "Punjabi"
      },
      {
        "isoCode": "qu",
        "name": "Quechua"
      },
      {
        "isoCode": "ro",
        "name": "Romanian"
      },
      {
        "isoCode": "rm",
        "name": "Romansh"
      },
      {
        "isoCode": "rn",
        "name": "Rundi"
      },
      {
        "isoCode": "ru",
        "name": "Russian"
      },
      {
        "isoCode": "sg",
        "name": "Sango"
      },
      {
        "isoCode": "sa",
        "name": "Sanskrit"
      },
      {
        "isoCode": "sc",
        "name": "Sardinian"
      },
      {
        "isoCode": "gd",
        "name": "Scottish Gaelic"
      },
      {
        "isoCode": "sr",
        "name": "Serbian"
      },
      {
        "isoCode": "sn",
        "name": "Shona"
      },
      {
        "isoCode": "ii",
        "name": "Sichuan Yi"
      },
      {
        "isoCode": "sd",
        "name": "Sindhi"
      },
      {
        "isoCode": "si",
        "name": "Sinhala"
      },
      {
        "isoCode": "sk",
        "name": "Slovak"
      },
      {
        "isoCode": "sl",
        "name": "Slovenian"
      },
      {
        "isoCode": "so",
        "name": "Somali"
      },
      {
        "isoCode": "es",
        "name": "Spanish"
      },
      {
        "isoCode": "su",
        "name": "Sundanese"
      },
      {
        "isoCode": "sw",
        "name": "Swahili"
      },
      {
        "isoCode": "sv",
        "name": "Swedish"
      },
      {
        "isoCode": "tg",
        "name": "Tajik"
      },
      {
        "isoCode": "ta",
        "name": "Tamil"
      },
      {
        "isoCode": "tt",
        "name": "Tatar"
      },
      {
        "isoCode": "te",
        "name": "Telugu"
      },
      {
        "isoCode": "th",
        "name": "Thai"
      },
      {
        "isoCode": "bo",
        "name": "Tibetan"
      },
      {
        "isoCode": "ti",
        "name": "Tigrinya"
      },
      {
        "isoCode": "to",
        "name": "Tongan"
      },
      {
        "isoCode": "tr",
        "name": "Turkish"
      },
      {
        "isoCode": "tk",
        "name": "Turkmen"
      },
      {
        "isoCode": "uk",
        "name": "Ukrainian"
      },
      {
        "isoCode": "ur",
        "name": "Urdu"
      },
      {
        "isoCode": "ug",
        "name": "Uyghur"
      },
      {
        "isoCode": "uz",
        "name": "Uzbek"
      },
      {
        "isoCode": "vi",
        "name": "Vietnamese"
      },
      {
        "isoCode": "cy",
        "name": "Welsh"
      },
      {
        "isoCode": "fy",
        "name": "Western Frisian"
      },
      {
        "isoCode": "wo",
        "name": "Wolof"
      },
      {
        "isoCode": "xh",
        "name": "Xhosa"
      },
      {
        "isoCode": "yi",
        "name": "Yiddish"
      },
      {
        "isoCode": "yo",
        "name": "Yoruba"
      },
      {
        "isoCode": "zu",
        "name": "Zulu"
      }
    ]
  }
  ```
