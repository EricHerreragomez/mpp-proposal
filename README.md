# MPP Slack Assistant

Slack bot for My Product Portal (MPP) support. It answers from the files in `knowledge/` and does not encode business rules in Python.

- Mention `@MPP Assistant` in a channel, or send it a DM. The reply is posted in the thread.
- The **Draft MPP reply** message shortcut sends a private draft to the person who triggered it.
- After a posted answer, **Helpful** / **Not helpful** buttons append a line to `feedback.jsonl` (timestamp, channel, answer id, rating). Message text is not logged.

## Slack app

Create an app at [api.slack.com/apps](https://api.slack.com/apps) from this manifest, then generate an app-level token with the `connections:write` scope (`xapp-...`) and install the app to copy the bot token (`xoxb-...`). Invite the bot to a test channel.

```yaml
display_information:
  name: MPP Assistant
  description: My Product Portal support assistant
features:
  bot_user:
    display_name: MPP Assistant
    always_online: true
  shortcuts:
    - name: Draft MPP reply
      type: message
      callback_id: draft_mpp_reply
      description: Draft a governance-aligned reply to this message
oauth_config:
  scopes:
    bot:
      - app_mentions:read
      - chat:write
      - channels:history
      - groups:history
      - im:history
      - im:write
      - commands
settings:
  event_subscriptions:
    bot_events:
      - app_mention
      - message.im
  interactivity:
    is_enabled: true
  socket_mode_enabled: true
```

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, and `ANTHROPIC_API_KEY`. `MODEL` defaults to `claude-sonnet-5-5`.

```bash
python app.py
```

Socket Mode does not need a public URL. Keep tokens in the host secret manager, not in the image.

Before a shared or long-lived deployment, confirm the bot matches your Tech Risk data-classification policy: https://techrisk.intranet.mckinsey.com/data-classification-model

## Knowledge

| File | Role |
|---|---|
| `knowledge/system_prompt.md` | Tone, Slack format, self-service first |
| `knowledge/decision_engine.md` | Routing and decision trees |
| `knowledge/kb/*.md` | Portal reference, loaded in filename order |

New rule: edit `decision_engine.md`. New reference: add a `.md` file under `knowledge/kb/`. Restart the process so the system prompt reloads. The model is instructed not to speculate past these files.

## Tests

```bash
python -m unittest tests.test_assistant
```

That suite checks prompt assembly, reply splitting, error handling, mention stripping, and feedback logging. It does not call Slack or Claude.

With a key in `.env`, regression-print every case:

```bash
python tests/run_eval.py
```

Cases live in `tests/test_cases.md`.

## Container

```bash
docker build -t mpp-slack-assistant .
docker run --env-file .env mpp-slack-assistant
```
