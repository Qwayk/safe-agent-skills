# Authentication

Authentication means proving which AWS account, role or user, and region the tool is using before it touches your account.

For AWS, authentication is meant to be local. The CLI follows the normal AWS credential chain through Boto3. If `AWS_PROFILE` is set, the tool uses that named profile. Otherwise it follows the default AWS lookup order on the machine. The rule is simple: do not paste secrets into chat; keep access keys, secret keys, session tokens, and local profile files on the machine.

A good first auth check is: run `auth check`, confirm the account id, caller ARN, user id, region, and allowlist status, then stop if any target looks wrong.

## Safe check

- `auth check` calls STS `GetCallerIdentity`.
- The response shows the account, ARN, and user id that AWS sees.
- The tool checks the selected region.
- Optional account and region allowlists can block the wrong target.
- Secret values are redacted before output or logging.

## What to set up

- Put `AWS_DEFAULT_REGION` in `.env`.
- Add `AWS_PROFILE` if you use a named local profile.
- Add `AWS_ALLOWED_ACCOUNTS` when you want a hard account guardrail.
- Add `AWS_ALLOWED_REGIONS` when you want a hard region guardrail.

Do not put AWS access keys, secret keys, or session tokens into chat. Use the local AWS profile, SSO login, role, or credential setup your AWS account already uses.

For first review work, a read-only or audit role is usually better than a broad admin role. If your team uses AWS SSO, sign in locally first and let the profile handle the session.

## What success looks like

- `auth check` returns `ok: true`.
- The account id is the account you expected.
- The ARN matches the intended user or assumed role.
- The region is the intended region.
- The allowlist status matches the account and region you expected.

## What can fail

- `NoCredentialsError` usually means the machine does not have AWS credentials yet.
- An expired SSO or role session can make a previously working profile fail.
- A bad or missing profile usually means the AWS profile name is wrong or incomplete.
- A region error usually means `AWS_DEFAULT_REGION` is missing or not allowed.
- An account or region refusal usually means the allowlist is doing its job.

When authentication fails, nothing useful changed in AWS. Fix the local profile, SSO session, region, or allowlist before trying another service command.
