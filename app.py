"""Slack Bolt handlers for the MPP Support Assistant (Socket Mode)."""

from __future__ import annotations

import json
import logging
import os
import re
import threading
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import assistant

logger = logging.getLogger(__name__)

PLACEHOLDER = "Looking into it… :mag:"
DRAFT_PREFIX = "Draft (only you can see this):\n"
EMPTY_QUESTION = "Please include your MPP question."
EMPTY_DRAFT = "That message has no text to draft from."
HELPFUL_PROMPT = "Was this helpful?"
SECTION_LIMIT = 3000
FEEDBACK_PATH = Path(__file__).resolve().parent / "feedback.jsonl"

_MENTION = re.compile(r"<@[A-Z0-9]+(?:\|[^>]+)?>")
_SEEN_LIMIT = 500
_seen: set[str] = set()
_seen_order: deque[str] = deque()
_seen_lock = threading.Lock()


def strip_mentions(text: str) -> str:
    return _MENTION.sub("", text or "").strip()


_IGNORED_SUBTYPES = {
    "bot_message",
    "message_changed",
    "message_deleted",
    "message_replied",
    "channel_join",
    "channel_leave",
    "channel_topic",
    "channel_purpose",
    "channel_name",
    "channel_archive",
    "channel_unarchive",
    "pinned_item",
    "unpinned_item",
}


def should_ignore_message(event: dict) -> bool:
    """Ignore bots, edits, deletes, and channel bookkeeping. User file shares still count."""
    if event.get("bot_id") or event.get("bot_profile"):
        return True
    if event.get("subtype") in _IGNORED_SUBTYPES:
        return True
    if event.get("edited"):
        return True
    return False


def claim_event(ts: str | None) -> bool:
    """Return False when this message ts was already handled (mention + DM overlap)."""
    if not ts:
        return True
    with _seen_lock:
        if ts in _seen:
            return False
        _seen.add(ts)
        _seen_order.append(ts)
        while len(_seen_order) > _SEEN_LIMIT:
            _seen.discard(_seen_order.popleft())
        return True


def feedback_blocks(answer_id: str) -> list[dict]:
    return [
        {
            "type": "actions",
            "block_id": f"feedback_{answer_id}",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "👍 Helpful"},
                    "action_id": "feedback_helpful",
                    "value": answer_id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "👎 Not helpful"},
                    "action_id": "feedback_not_helpful",
                    "value": answer_id,
                },
            ],
        }
    ]


def section_with_feedback(text: str, answer_id: str) -> list[dict]:
    return [
        {"type": "section", "text": {"type": "mrkdwn", "text": text}},
        *feedback_blocks(answer_id),
    ]


def plan_messages(text: str, *, answer_id: str) -> list[dict]:
    """Split a reply for Slack. Buttons sit on the last chunk, or a follow-up if it is too long for a section block."""
    chunks = assistant.split_reply(text)
    plans: list[dict] = []
    last = len(chunks) - 1
    for index, chunk in enumerate(chunks):
        if index != last:
            plans.append({"text": chunk, "blocks": None})
            continue
        if len(chunk) <= SECTION_LIMIT:
            plans.append({"text": chunk, "blocks": section_with_feedback(chunk, answer_id)})
        else:
            plans.append({"text": chunk, "blocks": None})
            plans.append(
                {
                    "text": HELPFUL_PROMPT,
                    "blocks": section_with_feedback(HELPFUL_PROMPT, answer_id),
                }
            )
    return plans


def plan_draft(text: str) -> list[str]:
    return assistant.split_reply(DRAFT_PREFIX + text)


def thread_context(client: object, channel: str, thread_ts: str, exclude_ts: str | None) -> list[str]:
    try:
        response = client.conversations_replies(channel=channel, ts=thread_ts, limit=200)  # type: ignore[attr-defined]
    except Exception as exc:
        logger.error("Failed to fetch thread history: %s", type(exc).__name__)
        return []
    lines: list[str] = []
    for message in response.get("messages", []):
        if message.get("ts") == exclude_ts:
            continue
        if message.get("bot_id") or message.get("subtype"):
            continue
        text = strip_mentions(message.get("text") or "")
        if text:
            lines.append(text)
    return lines[-30:]


def append_feedback(
    channel: str | None,
    answer_id: str | None,
    rating: str,
    path: Path = FEEDBACK_PATH,
) -> None:
    record = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "channel": channel,
        "answer_id": answer_id,
        "rating": rating,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _slack_id(value: object) -> str | None:
    if isinstance(value, dict):
        raw = value.get("id")
        return str(raw) if raw else None
    if isinstance(value, str) and value:
        return value
    return None


def _post(client: object, *, channel: str, thread_ts: str, text: str, blocks: list[dict] | None) -> None:
    kwargs: dict = {"channel": channel, "thread_ts": thread_ts, "text": text}
    if blocks:
        kwargs["blocks"] = blocks
    client.chat_postMessage(**kwargs)  # type: ignore[attr-defined]


def deliver_reply(
    client: object,
    channel: str,
    thread_ts: str,
    placeholder_ts: str | None,
    text: str,
    answer_id: str,
) -> None:
    plans = plan_messages(text, answer_id=answer_id)
    use_update = placeholder_ts is not None
    for plan in plans:
        if use_update:
            try:
                update: dict = {"channel": channel, "ts": placeholder_ts, "text": plan["text"]}
                if plan["blocks"]:
                    update["blocks"] = plan["blocks"]
                client.chat_update(**update)  # type: ignore[attr-defined]
                use_update = False
                continue
            except Exception as exc:
                logger.error("Failed to update placeholder: %s", type(exc).__name__)
                use_update = False
        _post(
            client,
            channel=channel,
            thread_ts=thread_ts,
            text=plan["text"],
            blocks=plan["blocks"],
        )


def _ask(client: object, channel: str, thread_ts: str, question: str, context: list[str] | None) -> None:
    placeholder_ts = None
    try:
        posted = client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=PLACEHOLDER)  # type: ignore[attr-defined]
        placeholder_ts = posted["ts"]
    except Exception as exc:
        logger.error("Failed to post placeholder: %s", type(exc).__name__)
    reply = assistant.answer(question, context)
    try:
        deliver_reply(client, channel, thread_ts, placeholder_ts, reply, uuid.uuid4().hex)
    except Exception as exc:
        logger.error("Failed to post reply: %s", type(exc).__name__)


def _handle_user_turn(event: dict, client: object) -> None:
    if should_ignore_message(event):
        return
    if not claim_event(event.get("ts")):
        return
    question = strip_mentions(event.get("text") or "")
    channel = event["channel"]
    thread_ts = event.get("thread_ts") or event["ts"]
    if not question:
        _post(client, channel=channel, thread_ts=thread_ts, text=EMPTY_QUESTION, blocks=None)
        return
    context = None
    if event.get("thread_ts"):
        context = thread_context(client, channel, event["thread_ts"], event.get("ts"))
    _ask(client, channel, thread_ts, question, context)


def handle_mention(event: dict, client: object) -> None:
    _handle_user_turn(event, client)


def handle_dm(event: dict, client: object) -> None:
    if event.get("channel_type") != "im":
        return
    _handle_user_turn(event, client)


def handle_draft(ack, shortcut: dict, client: object) -> None:
    ack()
    message = shortcut.get("message") or {}
    question = strip_mentions(message.get("text") or "")
    user_id = _slack_id(shortcut.get("user"))
    channel = _slack_id(shortcut.get("channel"))
    # Only thread the ephemeral when the selected message is already a reply.
    # A top-level ts is not a thread parent and Slack will reject it.
    thread_ts = message.get("thread_ts")
    if not user_id or not channel:
        logger.error("Draft shortcut missing user or channel")
        return
    body = question or EMPTY_DRAFT
    try:
        if question:
            body = assistant.answer(question)
        for chunk in plan_draft(body):
            kwargs: dict = {"channel": channel, "user": user_id, "text": chunk}
            if thread_ts:
                kwargs["thread_ts"] = thread_ts
            client.chat_postEphemeral(**kwargs)  # type: ignore[attr-defined]
    except Exception as exc:
        logger.error("Failed to send draft: %s", type(exc).__name__)


def handle_feedback(ack, body: dict, action: dict) -> None:
    ack()
    rating = "helpful" if action.get("action_id") == "feedback_helpful" else "not_helpful"
    channel = (body.get("channel") or {}).get("id")
    try:
        append_feedback(channel, action.get("value"), rating)
    except Exception as exc:
        logger.error("Failed to record feedback: %s", type(exc).__name__)


def register(application: App) -> None:
    application.event("app_mention")(handle_mention)
    application.event("message")(handle_dm)
    application.shortcut("draft_mpp_reply")(handle_draft)
    application.action(re.compile(r"^feedback_"))(handle_feedback)

    def _on_error(error: Exception) -> None:
        logger.error("Slack request failed: %s", type(error).__name__)

    application.error(_on_error)


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    assistant.get_system_prompt()
    application = App(token=os.environ["SLACK_BOT_TOKEN"])
    register(application)
    SocketModeHandler(application, os.environ["SLACK_APP_TOKEN"]).start()


if __name__ == "__main__":
    main()
