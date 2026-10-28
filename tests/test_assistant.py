"""Unit tests that do not call Slack or the Anthropic API."""

from __future__ import annotations

import json
import logging
import os
import tempfile
import unittest
from pathlib import Path

import assistant
import app
from slack_bolt import App
from tests.run_eval import load_cases


class _Block:
    def __init__(self, text: str) -> None:
        self.text = text


class _Response:
    def __init__(self, text: str) -> None:
        self.content = [_Block(text)]


class _Messages:
    def __init__(self, text: str | None = None, error: Exception | None = None) -> None:
        self.text = text
        self.error = error
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return _Response(self.text or "")


class _Client:
    def __init__(self, text: str | None = None, error: Exception | None = None) -> None:
        self.messages = _Messages(text, error)


class KnowledgeTests(unittest.TestCase):
    def test_prompt_sections_and_uploaded_knowledge(self) -> None:
        prompt = assistant.load_system_prompt()
        self.assertIn("# BEHAVIOR", prompt)
        self.assertIn("# DECISION ENGINE", prompt)
        self.assertIn("# KNOWLEDGE BASE", prompt)
        self.assertTrue(prompt.endswith(assistant.NO_SPECULATION))
        self.assertIn("## 01_portal_basics.md", prompt)
        self.assertIn("## 10_example_replies.md", prompt)
        self.assertLess(
            prompt.index("## 01_portal_basics.md"),
            prompt.index("## 09_routing_directory.md"),
        )
        self.assertIn("Tell us about wrong data!", prompt)
        self.assertIn("#executive_order_14117-support", prompt)
        self.assertIn("PLC-LCK00002", prompt)
        self.assertIn("KO105426", prompt)

    def test_cached_prompt_matches_loader(self) -> None:
        self.assertEqual(assistant.get_system_prompt(), assistant.load_system_prompt())


class SplitTests(unittest.TestCase):
    def test_short_reply_is_unchanged(self) -> None:
        self.assertEqual(assistant.split_reply("Hi :wave:"), ["Hi :wave:"])

    def test_long_reply_stays_within_limit_and_keeps_every_character(self) -> None:
        text = ("line\n" * 1500) + ("x" * 5000)
        chunks = assistant.split_reply(text)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= assistant.REPLY_LIMIT for chunk in chunks))
        self.assertEqual("".join(chunks), text)

    def test_hard_split_without_newlines(self) -> None:
        text = "a" * 9001
        chunks = assistant.split_reply(text)
        self.assertEqual([len(chunk) for chunk in chunks], [4000, 4000, 1001])
        self.assertEqual("".join(chunks), text)


class AnswerTests(unittest.TestCase):
    def test_answer_sends_cached_system_prompt_and_thread_context(self) -> None:
        client = _Client("Hi :wave:\nUpdate the TL in My Product Portal.")
        result = assistant.answer(
            "How do I update the TL?",
            ["The PM left last week"],
            client=client,
        )
        self.assertEqual(result, "Hi :wave:\nUpdate the TL in My Product Portal.")
        call = client.messages.calls[0]
        self.assertEqual(call["max_tokens"], 800)
        self.assertEqual(call["model"], os.environ.get("MODEL") or assistant.DEFAULT_MODEL)
        system = call["system"][0]
        self.assertEqual(system["cache_control"], {"type": "ephemeral"})
        self.assertIn("# DECISION ENGINE", system["text"])
        self.assertIn("The PM left last week", call["messages"][0]["content"])
        self.assertNotIn("The PM left last week", system["text"])

    def test_api_error_returns_apology_without_logging_the_question(self) -> None:
        question = "secret user question about product 12345"
        client = _Client(error=RuntimeError(question))
        with self.assertLogs("assistant", level="ERROR") as captured:
            result = assistant.answer(question, client=client)
        self.assertEqual(result, assistant.ERROR_REPLY)
        logged = "\n".join(captured.output)
        self.assertIn("RuntimeError", logged)
        self.assertNotIn(question, logged)
        self.assertNotIn("12345", logged)

    def test_empty_model_text_returns_apology(self) -> None:
        self.assertEqual(assistant.answer("Hi", client=_Client("  ")), assistant.ERROR_REPLY)


class SlackHelperTests(unittest.TestCase):
    def test_strip_mentions(self) -> None:
        self.assertEqual(
            app.strip_mentions("<@U123> <@W999|mpp> how do I update the TL?"),
            "how do I update the TL?",
        )

    def test_ignore_bots_edits_and_subtypes(self) -> None:
        self.assertTrue(app.should_ignore_message({"bot_id": "B1", "text": "hi"}))
        self.assertTrue(app.should_ignore_message({"subtype": "message_changed", "text": "hi"}))
        self.assertTrue(app.should_ignore_message({"subtype": "message_deleted"}))
        self.assertTrue(app.should_ignore_message({"edited": {"ts": "1"}, "text": "edited"}))
        self.assertFalse(app.should_ignore_message({"text": "hi", "user": "U1", "channel_type": "im"}))
        self.assertFalse(
            app.should_ignore_message({"subtype": "file_share", "text": "see the screenshot", "user": "U1"})
        )

    def test_claim_event_dedupes_message_ts(self) -> None:
        self.assertTrue(app.claim_event("111.222"))
        self.assertFalse(app.claim_event("111.222"))
        self.assertTrue(app.claim_event(None))

    def test_plan_messages_adds_feedback_and_respects_section_limit(self) -> None:
        short = app.plan_messages("Hi :wave:", answer_id="abc")
        self.assertEqual(len(short), 1)
        self.assertEqual(short[0]["blocks"][1]["elements"][0]["action_id"], "feedback_helpful")
        self.assertEqual(short[0]["blocks"][1]["elements"][1]["value"], "abc")

        long = app.plan_messages("b" * 3500, answer_id="abc")
        self.assertEqual(long[0]["blocks"], None)
        self.assertEqual(len(long[0]["text"]), 3500)
        self.assertEqual(long[1]["text"], app.HELPFUL_PROMPT)
        self.assertIn("feedback_not_helpful", json.dumps(long[1]["blocks"]))

    def test_plan_draft_prefix_and_limit(self) -> None:
        chunks = app.plan_draft("c" * 5000)
        self.assertTrue(chunks[0].startswith(app.DRAFT_PREFIX))
        self.assertTrue(all(len(chunk) <= assistant.REPLY_LIMIT for chunk in chunks))
        self.assertEqual("".join(chunks), app.DRAFT_PREFIX + ("c" * 5000))

    def test_feedback_log_has_no_message_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback.jsonl"
            app.append_feedback("C123", "ans-1", "not_helpful", path)
            record = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            set(record),
            {"timestamp", "channel", "answer_id", "rating"},
        )
        self.assertEqual(record["channel"], "C123")
        self.assertEqual(record["answer_id"], "ans-1")
        self.assertEqual(record["rating"], "not_helpful")
        self.assertTrue(record["timestamp"].endswith("Z"))

    def test_thread_context_skips_bots_and_the_current_message(self) -> None:
        class _Replies:
            def conversations_replies(self, **kwargs):
                self.kwargs = kwargs
                return {
                    "messages": [
                        {"ts": "1", "text": "<@UBOT> earlier question"},
                        {"ts": "2", "bot_id": "B1", "text": "bot reply"},
                        {"ts": "3", "subtype": "message_changed", "text": "edited"},
                        {"ts": "4", "text": "current mention"},
                    ]
                }

        client = _Replies()
        lines = app.thread_context(client, "C1", "1", "4")
        self.assertEqual(lines, ["earlier question"])
        self.assertEqual(client.kwargs["channel"], "C1")

    def test_thread_context_failure_returns_empty_and_does_not_log_text(self) -> None:
        class _Boom:
            def conversations_replies(self, **kwargs):
                raise RuntimeError("private thread text")

        with self.assertLogs("app", level="ERROR") as captured:
            lines = app.thread_context(_Boom(), "C1", "1", "4")
        self.assertEqual(lines, [])
        logged = "\n".join(captured.output)
        self.assertIn("RuntimeError", logged)
        self.assertNotIn("private thread text", logged)


class _Recorder:
    def __init__(self) -> None:
        self.posts: list[dict] = []
        self.updates: list[dict] = []
        self.ephemeral: list[dict] = []

    def chat_postMessage(self, **kwargs):
        self.posts.append(kwargs)
        return {"ts": "placeholder"}

    def chat_update(self, **kwargs):
        self.updates.append(kwargs)
        return kwargs

    def chat_postEphemeral(self, **kwargs):
        self.ephemeral.append(kwargs)
        return kwargs

    def conversations_replies(self, **kwargs):
        return {"messages": [{"ts": "parent", "text": "earlier question"}]}


class HandlerTests(unittest.TestCase):
    def test_ignores_bots_channel_messages_and_edits(self) -> None:
        client = _Recorder()
        app.handle_dm({"channel_type": "channel", "text": "hi", "channel": "C", "ts": "dm-channel"}, client)
        app.handle_dm(
            {"channel_type": "im", "bot_id": "B", "text": "hi", "channel": "D", "ts": "dm-bot"},
            client,
        )
        app.handle_mention({"subtype": "message_changed", "text": "<@U> hi", "channel": "C", "ts": "edit"}, client)
        self.assertEqual(client.posts, [])

    def test_mention_answers_in_thread_and_updates_placeholder(self) -> None:
        client = _Recorder()
        seen: dict = {}

        def fake_answer(question: str, thread_context: list[str] | None = None) -> str:
            seen["question"] = question
            seen["context"] = thread_context
            return "Hi :wave:\nUpdate the TL in My Product Portal."

        original = assistant.answer
        assistant.answer = fake_answer
        try:
            app.handle_mention(
                {
                    "text": "<@UBOT> How do I update the TL?",
                    "channel": "C1",
                    "ts": "200.2",
                    "thread_ts": "parent",
                    "user": "U1",
                },
                client,
            )
        finally:
            assistant.answer = original
        self.assertEqual(seen["question"], "How do I update the TL?")
        self.assertEqual(seen["context"], ["earlier question"])
        self.assertEqual(client.posts[0]["text"], app.PLACEHOLDER)
        self.assertEqual(client.posts[0]["thread_ts"], "parent")
        self.assertEqual(client.updates[0]["ts"], "placeholder")
        self.assertIn("Update the TL", client.updates[0]["text"])
        self.assertEqual(client.updates[0]["blocks"][1]["elements"][0]["action_id"], "feedback_helpful")

    def test_duplicate_event_is_not_answered_twice(self) -> None:
        client = _Recorder()
        original = assistant.answer
        assistant.answer = lambda question, thread_context=None: "Hi"
        try:
            event = {"text": "hello", "channel": "D1", "ts": "300.3", "channel_type": "im", "user": "U1"}
            app.handle_dm(event, client)
            app.handle_dm(dict(event), client)
        finally:
            assistant.answer = original
        self.assertEqual(len(client.posts), 1)

    def test_draft_is_ephemeral_and_prefixed(self) -> None:
        client = _Recorder()
        original = assistant.answer
        assistant.answer = lambda question, thread_context=None: "Draft body"
        acked = {"n": 0}
        try:
            app.handle_draft(
                lambda: acked.__setitem__("n", acked["n"] + 1),
                {
                    "user": {"id": "U9"},
                    "channel": {"id": "C9"},
                    "message": {"text": "Can I change the AL?", "ts": "400.4"},
                },
                client,
            )
            app.handle_draft(
                lambda: None,
                {
                    "user": {"id": "U9"},
                    "channel": {"id": "C9"},
                    "message": {"text": "In a thread", "ts": "400.5", "thread_ts": "400.0"},
                },
                client,
            )
        finally:
            assistant.answer = original
        self.assertEqual(acked["n"], 1)
        self.assertEqual(len(client.posts), 0)
        self.assertTrue(client.ephemeral[0]["text"].startswith(app.DRAFT_PREFIX))
        self.assertIn("Draft body", client.ephemeral[0]["text"])
        self.assertEqual(client.ephemeral[0]["user"], "U9")
        self.assertNotIn("thread_ts", client.ephemeral[0])
        self.assertEqual(client.ephemeral[1]["thread_ts"], "400.0")


class RegistrationTests(unittest.TestCase):
    def test_listeners_register_without_calling_slack(self) -> None:
        application = App(token="xoxb-test", token_verification_enabled=False)
        app.register(application)
        self.assertGreaterEqual(len(application._listeners), 4)


class EvalCaseTests(unittest.TestCase):
    def test_ten_cases_parse(self) -> None:
        cases = load_cases(Path(__file__).resolve().parent / "test_cases.md")
        self.assertEqual(len(cases), 10)
        questions = [question for question, _ in cases]
        self.assertIn("How do I update the TL on my product?", questions)
        self.assertIn("What's the cafeteria menu today?", questions)
        self.assertTrue(all(expected for _, expected in cases))


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    unittest.main()
