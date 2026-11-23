# Amazon Creators

Search Amazon for products, compare editions of a book, or look up the variations of an item. The tool can also show where a product category sits in Amazon's catalog.

Try asking, "Find books about home coffee roasting in the US," or "Which formats does Amazon show for this book?" Your agent shows you the search, marketplace, and tracking tag before it sends the request. After you approve it, the agent calls Amazon and gives you the results, product links, and any errors.

## Start here first

- [Connect your Amazon Creators account](docs/onboarding.md)
- [Run your first search](docs/quickstart.md)
- [See more things you can ask](docs/use_cases.md)

## What access this tool needs

You need your Creators API Credential ID, Credential Secret, the version Amazon issued, and an Associates tracking tag for the marketplace you want to search. A working token confirms sign-in. Amazon checks catalog access when you send a search or lookup.

## Install and first run

Ask your agent to install the `amazon-creators` skill from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@amazon-creators -g -y
```

Follow [Quickstart](docs/quickstart.md) to install the Python command and run a search from a new folder.

## Limits

The four catalog commands read from Amazon. Use the returned product links and format information in the context of the marketplace and date you checked. If a book lookup shows print and Kindle editions only, check Amazon or Audible before drawing a conclusion about an audiobook.

Amazon replaced Product Advertising API 5.0 with Creators API. Use the credentials issued for Creators API. [Amazon's migration guide](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/migrating-to-creatorsapi-from-paapi)

## Helpful docs

- [Guide index](docs/README.md)
- [Command guide](docs/command_reference.md)
- [How the tool handles account information and requests](docs/safety_model.md)
- [What was tested](docs/proof.md)
- [API coverage](docs/api_coverage.md)
