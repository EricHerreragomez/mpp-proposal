"""Load MPP knowledge and answer questions through the Anthropic Messages API."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"
REPLY_LIMIT = 4000
DEFAULT_MODEL = "claude-sonnet-5-5"
ERROR_REPLY = "Sorry, I couldn't process that. Please try again or ask in the channel."
NO_SPECULATION = (
    "If the knowledge provided does not cover the question, say so and do not speculate."
)

_system_prompt: str | None = None


def load_system_prompt(knowledge_dir: Path | None = None) -> str:
    """Combine behavior, the decision engine, and every kb markdown file."""
    root = knowledge_dir or KNOWLEDGE_DIR
    behavior = (root / "system_prompt.md").read_text(encoding="utf-8").strip()
    engine = (root / "decision_engine.md").read_text(encoding="utf-8").strip()
    kb_dir = root / "kb"
    sections: list[str] = []
    if kb_dir.is_dir():
        for path in sorted(kb_dir.glob("*.md")):
            body = path.read_text(encoding="utf-8").strip()
            sections.append(f"## {path.name}\n\n{body}")
    knowledge = "\n\n".join(sections)
    return (
        "# BEHAVIOR\n\n"
        f"{behavior}\n\n"
        "# DECISION ENGINE\n\n"
        f"{engine}\n\n"
        "# KNOWLEDGE BASE\n\n"
        f"{knowledge}\n\n"
        f"{NO_SPECULATION}"
    )


def get_system_prompt() -> str:
    global _system_prompt
    if _system_prompt is None:
        _system_prompt = load_system_prompt()
    return _system_prompt


def split_reply(text: str, limit: int = REPLY_LIMIT) -> list[str]:
    """Split a reply into chunks of at most `limit` characters without dropping text."""
    if limit < 1:
        raise ValueError("limit must be positive")
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    rest = text
    while len(rest) > limit:
        window = rest[:limit]
        split_at = window.rfind("\n")
        if split_at < limit // 2:
            split_at = limit
        chunks.append(rest[:split_at])
        rest = rest[split_at:]
    if rest:
        chunks.append(rest)
    return chunks


def build_user_message(question: str, thread_context: list[str] | None) -> str:
    parts: list[str] = []
    if thread_context:
        parts.append("Earlier messages in this thread (oldest first):")
        for index, message in enumerate(thread_context, start=1):
            parts.append(f"{index}. {message}")
        parts.append("")
    parts.append(question.strip())
    return "\n".join(parts)


def _response_text(response: object) -> str:
    parts: list[str] = []
    for block in getattr(response, "content", []) or []:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "".join(parts).strip()


def answer(
    question: str,
    thread_context: list[str] | None = None,
    *,
    client: object | None = None,
) -> str:
    """Answer one MPP question. Thread context is prior Slack text, not a knowledge source."""
    from anthropic import Anthropic

    api = client if client is not None else Anthropic()
    model = os.environ.get("MODEL") or DEFAULT_MODEL
    try:
        response = api.messages.create(  # type: ignore[attr-defined]
            model=model,
            max_tokens=800,
            system=[
                {
                    "type": "text",
                    "text": get_system_prompt(),
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": build_user_message(question, thread_context),
                }
            ],
        )
    except Exception as exc:
        logger.error("Claude API call failed: %s", type(exc).__name__)
        return ERROR_REPLY
    text = _response_text(response)
    return text or ERROR_REPLY
