# API coverage

The tool covers stock search, asset checks, previews and approved licensed downloads. See the [provider's Stock API docs](https://docs.magnific.com/api-reference/resources/images-and-templates-api) for the full API.

| API request | When the tool uses it |
| --- | --- |
| `GET /resources` | Check the key, search photos and images, or find related assets. |
| `GET /resources/{resource_id}` | Read details, find previews and groups, check AI flags, or prepare a download preview. |
| `GET /resources/{resource_id}/download` | Request an approved download with an image size. |
| `GET /resources/{resource_id}/download/{format}` | Request an approved download by format. |

It can also fetch the file from a URL Freepik gives it and save inventory rows. The tool has no commands for account setup, image generation, or reversing a license. See [download approvals](safety_model.md) and [what was tested](proof.md).
