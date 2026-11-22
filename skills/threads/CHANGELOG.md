# Changelog

## Unreleased

- Save and check matching plans for creating a draft and publishing it. Check the account before sending and read the published post back when Threads returns an ID.
- Return the processing error in `posts status` and keep sign-in codes and token arguments out of command records.
- Create a usable settings file and make the first post list work with the signed-in account.
- Combine repeated guides and remove the leftover demo and CSV job examples. Keep run history.

## Earlier work in 0.1.0

- Added explicit commands for the documented Threads API, local plans, receipts and the skill.
- Aligned post requests with documented media types, polls, GIFs, spoilers, reply controls and carousel fields. Checked request shapes for public reads, token refresh, search, replies and oEmbed.
- Removed the undocumented ghost-post and user-reply list commands.
- Added the no-snapshot approval check and saved sample refusal output.
