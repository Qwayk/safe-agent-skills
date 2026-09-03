# Use cases

Ask for the outcome, not an endpoint. Name the voice, file, language, agent, phone number, or account area when it matters. The agent reads first and plans work that can spend credits, change content, or affect someone outside ElevenLabs.

## Voice and audio production

- “List my voices and models, then recommend one for a calm product walkthrough.”
- “Turn this approved script into an MP3 using `<voice-id>` and save it to `./out/walkthrough.mp3`; show me the plan first.”
- “Create a two-speaker dialogue from this script and keep the audio file out of chat.”
- “Design three preview voices for a documentary narrator, but do not persist one yet.”
- “Isolate the speaker from this recording and save the result locally.”
- “Check my usage before generating the next batch of narration.”

## Transcription, dubbing, and music

- “Transcribe `./interview.mp3` to `./out/interview.json` and tell me what approval the job needs.”
- “Create a Spanish dubbing project for this video, show the language and spend plan, and stop before apply.”
- “Review the dubbing transcript and identify segments that need correction.”
- “Compose a short background track from this brief and save the audio to a file.”
- “Separate stems from this approved track and keep the output file-only.”

These jobs may require paid features, source files, language settings, or account fixtures. A dry-run plan is not proof that the provider will accept the live request.

## ElevenAgents and conversations

- “List my ElevenAgents and tell me which one handled the most conversations yesterday.”
- “Create a draft ElevenAgent for this support use case; show every setting before anything live changes.”
- “Create and run a test for agent `<agent-id>` using this scenario, then save the test result.”
- “Review the conversation transcript, summary, audio, and analytics for conversation `<conversation-id>`.”
- “Find conversations containing this customer issue and export the sensitive results to `./out/conversations.json`.”
- “Check current live conversation counts and LLM usage before we change the agent.”

Conversation, transcript, audio, and analytics data may be sensitive; use file output where required.

## Twilio and calling

- “Show the available ElevenLabs phone numbers and stop before assigning one.”
- “Prepare a plan to assign this Twilio number to agent `<agent-id>`.”
- “Place an outbound call to the approved destination using agent `<agent-id>`, but wait for confirmation after showing the number, cost risk, and recovery limit.”
- “Review inbound and outbound call conversations, their audio, summaries, and analytics.”

Calls can reach real people and may incur provider or telephony charges. Never guess a number or destination.

## What the agent should return

For reads, say what was found and what is account- or plan-limited. For writes, show the target, spend or external-action risk, file path, `before_state`, recovery contract, required approvals, and verification. After apply, report the receipt or precise provider limitation.
