# MPP Slack Assistant

A Slack bot that answers My Product Portal (MPP) support questions using a 3-layer prompt
architecture (behavior / business logic / reference knowledge) and the Anthropic API.

See `00-BUILD-GUIDE.md` for full setup instructions, including:
- Creating the Slack app and required scopes
- Using Cursor to scaffold and iterate on this code
- Running locally
- Test cases to validate before rollout
- Deployment notes
- How to scale the knowledge base to retrieval (RAG) later

## Quick start

```bash
npm install
cp .env.example .env   # fill in tokens
npm start
```

## Editing behavior vs. policy

- Tone/format changes → `docs/01-system-prompt.md`
- Policy/routing changes → `docs/02-decision-engine.md`
- Fact/link/timing changes → `docs/03-knowledge-base.md`

Never hardcode governance logic in `src/app.js` — it should only ever load and forward these docs.

## Before shipping

See [`PRE-SHIP-CHECKLIST.md`](PRE-SHIP-CHECKLIST.md) — Tech Risk sign-off, IRP definition, and private-channel test cases must pass before shared-channel rollout.
