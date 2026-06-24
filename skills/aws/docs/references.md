# References

These are the official AWS and local sources behind the main claims in the AWS skill: how identity is checked, how local credentials and regions are found, and why coverage is tied to the pinned Botocore package.

Prefer official docs. If a capability depends on a specific documented behavior, link the exact page.

## Official sources

| Source | Why it matters | Last verified (UTC) |
| --- | --- | --- |
| [STS GetCallerIdentity](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html) | Proves which AWS account and role the CLI is using | 2026-06-24 |
| [Boto3 low-level clients](https://docs.aws.amazon.com/boto3/latest/guide/clients.html) | Explains how Boto3 clients expose AWS service operations | 2026-06-24 |
| [Botocore loaders](https://docs.aws.amazon.com/botocore/latest/reference/loaders.html) | Explains how Botocore loads service model data | 2026-06-24 |
| [Boto3 configuration guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) | Explains region and config lookup order | 2026-06-24 |
| [Boto3 credentials guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) | Explains the credential chain the CLI follows | 2026-06-24 |
| [AWS shared config and credentials files](https://docs.aws.amazon.com/sdkref/latest/guide/file-format.html) | Explains the local config files used by AWS SDKs and tools | 2026-06-24 |

## Local sources

| Source | Why it matters | Last verified (UTC) |
| --- | --- | --- |
| `docs/_generated/aws_botocore_inventory.json` | Pinned Botocore service model inventory used by the CLI | 2026-06-24 |
| `docs/api_coverage.md` | Human-readable coverage counts and selected service-model versions | 2026-06-24 |
| `src/aws_safe_agent_cli/aws_runtime.py` | Parser, risk classification, safety gates, and write flow | 2026-06-24 |
| `tests/` | Local proof for refusal behavior, mocked apply, redaction, generated coverage, and docs contracts | 2026-06-24 |

## Notes

- Never include secrets in this file.
- Update this file when the runtime changes in a way that depends on an AWS doc, Boto3 behavior, Botocore behavior, or generated model source.
