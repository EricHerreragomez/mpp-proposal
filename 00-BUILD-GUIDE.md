# MPP Slack Assistant — Build Guide

## Why this architecture

One giant system prompt works in a chat playground but breaks down in production because:

- **Behavior** (tone, format, escalation defaults) gets tangled with **business logic** (decision trees), which gets tangled with **reference facts** (links, sync times).
- Every time a policy changes (e.g. a new charge code rule), you have to re-read and re-test the whole prompt instead of editing one line in one file.
- Long single prompts are harder for the model to apply consistently — decision trees buried in prose get missed.

Splitting into three layers fixes this:

| Layer | File | Purpose | Changes how often |
|---|---|---|---|
| **Behavior** | `01-system-prompt.md` | Tone, response format, self-service-first rule, "never guess" style | Rarely |
| **Business logic** | `02-decision-engine.md` | Product vs Project, Charge Code, Accountable Leader routing, IRP, escalation routing | Occasionally (policy changes) |
| **Reference knowledge** | `03-knowledge-base.md` | Links, sync timings, tag names, service offering definitions | Occasionally (facts change) |

At request time, the bot assembles: `system-prompt + decision-engine + knowledge-base + user question` and sends it to Claude. This is "context stuffing" — good enough at this size (all three docs are a few KB, well under context limits). If the knowledge base grows past ~50 pages, upgrade to retrieval (see "Scaling to RAG" at the bottom).

---

## Repo layout

```
mpp-slack-bot/
├── docs/
│   ├── 01-system-prompt.md
│   ├── 02-decision-engine.md
│   └── 03-knowledge-base.md
├── src/
│   └── app.js
├── package.json
├── .env.example
└── README.md
```

---

## Step 1 — Create the Slack App

1. Go to https://api.slack.com/apps → **Create New App** → **From scratch**.
2. Name it (e.g. "MPP Assistant"), pick your McKinsey Slack workspace.
   - **Important**: internal bots handling product/security/governance data will typically need sign-off from your workspace admin / Tech Risk before install. Loop them in early.
3. **Socket Mode**: turn on. Generate an app-level token with scope `connections:write`. Save it as `SLACK_APP_TOKEN`.
4. **OAuth & Permissions** → add Bot Token Scopes:
   - `app_mentions:read`
   - `chat:write`
   - `channels:history`
   - `im:history`
   - `im:write`
   - `users:read`
5. **Event Subscriptions** → subscribe to:
   - `app_mention`
   - `message.im` (for DMs)
6. **Install App to Workspace** → copy the **Bot User OAuth Token** → save as `SLACK_BOT_TOKEN`.
7. Copy the **Signing Secret** from Basic Information → save as `SLACK_SIGNING_SECRET`.

---

## Step 2 — Use Cursor to scaffold the code

Cursor is a code editor, not the Slack bot itself — you use it to *write* `src/app.js` and the supporting files quickly. Don't confuse Cursor's own coding-agent instructions with the bot's system prompt; they're separate things.

1. Open Cursor → **Open Folder** → select `mpp-slack-bot/`.
2. Add a `.cursorrules` file (optional but recommended) so Cursor's AI stays consistent while you iterate:

   ```
   This repo is a Slack bot that answers My Product Portal (MPP) support
   questions using the Anthropic API. Business logic lives in
   docs/02-decision-engine.md and must never be duplicated or reworded
   inside src/ code — code should only load and pass these docs as
   context, never hardcode governance rules in JS.
   ```
3. In Cursor's chat/composer, paste the contents of this guide's "Step 3" code below and ask Cursor to generate `src/app.js`, `package.json`, and `.env.example` matching it. Iterate by asking Cursor to add features one at a time (e.g. "add a Slack slash command `/mpp-escalate` that always routes to the wrong-data flow").
4. Keep the three `docs/*.md` files as the single source of truth. When McKinsey Tech Risk changes a policy, edit the doc — not the code.

---

## Step 3 — The bot code (Node.js + Slack Bolt + Anthropic API)

See `src/app.js` in this package. Key design points:

- Loads all three docs from disk at startup into memory.
- On every `app_mention` or DM, sends: system prompt + decision engine + knowledge base + conversation so far to Claude.
- Uses `claude-sonnet-4-6` model, low `max_tokens` isn't needed here (Slack answers are short) — keep `max_tokens` around 800–1000.
- Posts the reply back into the same channel/thread.

Install and run:

```bash
cd mpp-slack-bot
npm install
cp .env.example .env   # fill in your tokens
node src/app.js
```

---

## Step 4 — Test cases to run before rollout

Run these through the bot and confirm it matches the governance rules exactly:

1. "How do I register a new product?" → self-service flow, MPP link, decision rule questions.
2. "My PM is inactive and I can't edit the product." → "Tell us about wrong data!" flow, not a ServiceNow incident.
3. "I need help with US DSO." → routes to `#executive_order_14117-support`, not MPP.
4. "Can I change the Accountable Leader manually?" → "No, this is determined automatically," explains selection logic.
5. "I need a Product ID showing up in QA." → explains QA sync is occasional, routes to PCIS team.
6. Ambiguous case: "I built a script for my own analysis, should I register it as a product?" → Project Workspace recommendation, using the three-question test.

---

## Step 5 — Deployment

Options (pick based on what McKinsey infra approves):

- **Internal PaaS** (preferred for an enterprise tool touching governance data) — check with your Platform McKinsey / Tech Risk contacts for the approved internal hosting path before using an external cloud.
- If externally hosted for a prototype only: Render, Railway, or Fly.io all support long-running Socket Mode Node processes on a free/low tier.
- Store `ANTHROPIC_API_KEY`, `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, `SLACK_APP_TOKEN` as encrypted secrets/environment variables — never commit them.

Before going live in a shared channel, get this reviewed the same way you would any internal tool that gives governance guidance — accuracy matters here because people will act on "escalate to X" instructions.

---

## Scaling to RAG (only if needed later)

If `03-knowledge-base.md` grows large (many product catalogs, service offering trees, etc.), switch from "paste whole doc into context" to retrieval:

1. Chunk the knowledge base into sections (by `##` heading).
2. Embed chunks (Voyage AI or similar) into a vector store.
3. On each user question, embed the question, retrieve top-k relevant chunks, and inject only those into the prompt alongside the always-included system prompt + decision engine (decision trees are small enough to always include in full — don't retrieve-chunk your decision logic, or you risk missing a branch).

This keeps responses fast and cheap even as the knowledge base grows, while the decision engine (the part that must never be inconsistent) stays fully present in every call.
