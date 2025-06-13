import json
from datetime import datetime

from qtesting_tools.result_entry import ResultEntry, ResultOrchestration


def test_result_entry_creation_and_properties():
    entry = ResultEntry(
        {
            "timestamp": "2025-06-05T07:46:11.796134Z",
            "level": "DEBUG",
            "target": "target::DEBUG_message",
            "threadId": "ThreadId(1)",
        }
    )
    assert entry.timestamp == datetime.fromisoformat("2025-06-05T07:46:11.796134Z")
    assert entry.level == "DEBUG"
    assert entry.target == "target::DEBUG_message"
    assert entry.thread_id == "ThreadId(1)"


def test_result_orchestration_creation_and_properties():
    entry = ResultOrchestration(
        {
            "timestamp": "2025-06-05T07:46:11.796134Z",
            "level": "DEBUG",
            "fields": {"message": "Debug message"},
            "target": "target::DEBUG_message",
            "threadId": "ThreadId(1)",
        }
    )

    assert entry.timestamp == datetime.fromisoformat("2025-06-05T07:46:11.796134Z")
    assert entry.level == "DEBUG"
    assert entry.message == "Debug message"
    assert entry.target == "target::DEBUG_message"
    assert entry.thread_id == "ThreadId(1)"


def test_result_entry_str():
    entry = ResultEntry(
        {
            "timestamp": "2025-06-05T07:46:11.796134Z",
            "level": "DEBUG",
            "fields": {"message": "Debug message"},
            "target": "target::DEBUG_message",
            "threadId": "ThreadId(1)",
        }
    )
    str_repr = str(entry)
    assert "timestamp=2025-06-05 07:46:11.796134+00:00" in str_repr
    assert "level=DEBUG" in str_repr
    assert "target=target::DEBUG_message" in str_repr
    assert "thread_id=ThreadId(1)" in str_repr
