"""Tests for AI Coach conversation memory helpers."""

from modules.coach_memory import compress_conversation, has_reference_to_past


def test_empty_conversation_returns_empty_string():
    assert compress_conversation([]) == ""


def test_single_user_message_formats_correctly():
    messages = [{"role": "user", "content": "How is my health?"}]

    assert compress_conversation(messages) == "User: How is my health?"


def test_user_and_assistant_pair_formats_correctly():
    messages = [
        {"role": "user", "content": "How is my health?"},
        {"role": "assistant", "content": "Your health looks stable."},
    ]

    assert compress_conversation(messages) == (
        "User: How is my health?\n\n"
        "Coach: Your health looks stable."
    )


def test_more_than_max_turns_keeps_only_latest_messages():
    messages = []
    for index in range(7):
        messages.append({"role": "user", "content": f"Question {index}"})
        messages.append({"role": "assistant", "content": f"Answer {index}"})

    result = compress_conversation(messages, max_turns=5)

    assert "Question 0" not in result
    assert "Answer 1" not in result
    assert "Question 2" in result
    assert "Answer 6" in result
    assert result.startswith("User: Question 2")


def test_long_content_truncated_to_150_characters():
    long_text = "a" * 200

    result = compress_conversation([{"role": "user", "content": long_text}])

    assert result == f"User: {'a' * 150}"


def test_malformed_messages_ignored_safely():
    messages = [
        None,
        "bad",
        {"role": "system", "content": "Ignore me"},
        {"role": "user", "content": None},
        {"role": "assistant", "content": "Valid answer"},
    ]

    assert compress_conversation(messages) == "Coach: Valid answer"


def test_english_keyword_detection():
    assert has_reference_to_past("As mentioned before, what should I do?")
    assert has_reference_to_past("Last time you said sleep matters.")


def test_chinese_keyword_detection():
    assert has_reference_to_past("刚才你说过我需要改善睡眠。")
    assert has_reference_to_past("上次的建议还适合我吗？")


def test_unrelated_text_returns_false():
    assert not has_reference_to_past("What should I eat tomorrow?")

