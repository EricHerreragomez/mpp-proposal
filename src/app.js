/**
 * MPP Slack Assistant
 * Loads the 3-layer doc architecture (system prompt, decision engine, knowledge base)
 * and answers Slack questions via the Anthropic API.
 *
 * Run: node src/app.js
 * Requires env vars: SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, SLACK_APP_TOKEN, ANTHROPIC_API_KEY
 */

const { App } = require("@slack/bolt");
const fs = require("fs");
const path = require("path");
require("dotenv").config();

// ---- Load the 3-layer docs once at startup ----
const DOCS_DIR = path.join(__dirname, "..", "docs");
const systemPrompt = fs.readFileSync(path.join(DOCS_DIR, "01-system-prompt.md"), "utf8");
const decisionEngine = fs.readFileSync(path.join(DOCS_DIR, "02-decision-engine.md"), "utf8");
const knowledgeBase = fs.readFileSync(path.join(DOCS_DIR, "03-knowledge-base.md"), "utf8");

const FULL_SYSTEM_PROMPT = `${systemPrompt}

---

${decisionEngine}

---

${knowledgeBase}`;

// ---- Slack app (Socket Mode) ----
const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
  socketMode: true,
  appToken: process.env.SLACK_APP_TOKEN,
});

// Simple per-thread conversation memory (in-memory; swap for Redis/DB in production)
const threadHistory = new Map();

async function askClaude(threadKey, userText) {
  const history = threadHistory.get(threadKey) || [];
  const messages = [...history, { role: "user", content: userText }];

  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": process.env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: "claude-sonnet-4-6",
      max_tokens: 900,
      system: FULL_SYSTEM_PROMPT,
      messages,
    }),
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Anthropic API error ${response.status}: ${errText}`);
  }

  const data = await response.json();
  const replyText = data.content
    .filter((block) => block.type === "text")
    .map((block) => block.text)
    .join("\n")
    .trim();

  messages.push({ role: "assistant", content: replyText });
  threadHistory.set(threadKey, messages.slice(-10)); // keep last 10 turns

  return replyText;
}

function threadKeyFor(event) {
  return `${event.channel}:${event.thread_ts || event.ts}`;
}

// ---- Handle @mentions in channels ----
app.event("app_mention", async ({ event, say }) => {
  try {
    const cleanText = event.text.replace(/<@[^>]+>/g, "").trim();
    const reply = await askClaude(threadKeyFor(event), cleanText);
    await say({ text: reply, thread_ts: event.thread_ts || event.ts });
  } catch (err) {
    console.error(err);
    await say({
      text: "Hi 👋 Something went wrong on my end pulling that up — please try again in a moment, or use the standard MPP flow directly.",
      thread_ts: event.thread_ts || event.ts,
    });
  }
});

// ---- Handle direct messages ----
app.event("message", async ({ event, say }) => {
  if (event.channel_type !== "im" || event.bot_id) return; // only plain DMs, ignore bot echoes
  try {
    const reply = await askClaude(threadKeyFor(event), event.text);
    await say({ text: reply });
  } catch (err) {
    console.error(err);
    await say(
      "Hi 👋 Something went wrong on my end pulling that up — please try again in a moment, or use the standard MPP flow directly."
    );
  }
});

(async () => {
  await app.start();
  console.log("⚡️ MPP Slack Assistant is running (Socket Mode)");
})();
