"""
Tests for "result_entry" module.
"""

from datetime import timedelta

from testing_tools import ResultEntry


def test_result_entry_creation_and_properties():
    entry = ResultEntry(
        {
            "timestamp": "0:00:00.000001",
            "level": "DEBUG",
            "target": "target::DEBUG_message",
            "threadId": "ThreadId(1)",
        }
    )
    assert entry.timestamp == str(timedelta(microseconds=1))
    assert entry.level == "DEBUG"
    assert entry.target == "target::DEBUG_message"
    assert entry.thread_id == "ThreadId(1)"


def test_result_orchestration_creation_and_properties():
    entry = ResultEntry(
        {
            "timestamp": "0:00:00.000010",
            "level": "DEBUG",
            "fields": {"message": "Debug message"},
            "target": "target::DEBUG_message",
            "threadId": "ThreadId(1)",
        }
    )

    assert entry.timestamp == str(timedelta(microseconds=10))
    assert entry.level == "DEBUG"
    assert entry.message == "Debug message"
    assert entry.target == "target::DEBUG_message"
    assert entry.thread_id == "ThreadId(1)"


def test_result_entry_str():
    entry = ResultEntry(
        {
            "timestamp": "0:00:01.000100",
            "level": "DEBUG",
            "fields": {"message": "Debug message"},
            "target": "target::DEBUG_message",
            "threadId": "ThreadId(1)",
        }
    )
    str_repr = str(entry)
    assert "timestamp=0:00:01.0001" in str_repr
    assert "level=DEBUG" in str_repr
    assert "target=target::DEBUG_message" in str_repr
    assert "thread_id=ThreadId(1)" in str_repr
