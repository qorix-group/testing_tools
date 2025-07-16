"""
Tests for "log_container" module.
"""

from datetime import timedelta

import pytest

from testing_utils import LogContainer, ResultEntry


def test_log_container_add_and_get_logs():
    lc = LogContainer()
    lc.add_log(
        ResultEntry(
            {
                "timestamp": "0:00:01.000100",
                "level": "DEBUG",
                "fields": {"message": "Debug message"},
                "target": "target::DEBUG_message",
                "threadId": "ThreadId(1)",
            }
        )
    )
    lc.add_log(
        ResultEntry(
            {
                "timestamp": "0:00:01.000101",
                "level": "INFO",
                "target": "target::INFO_message",
                "threadId": "ThreadId(2)",
            }
        )
    )
    logs = lc.get_logs()
    assert len(logs) == 2

    assert logs[0].timestamp == str(timedelta(microseconds=1000100))
    assert logs[0].level == "DEBUG"
    assert logs[0].message == "Debug message"
    assert logs[0].target == "target::DEBUG_message"
    assert logs[0].thread_id == "ThreadId(1)"

    assert logs[1].timestamp == str(timedelta(microseconds=1000101))
    assert logs[1].level == "INFO"
    assert logs[1].target == "target::INFO_message"
    assert logs[1].thread_id == "ThreadId(2)"


def test_log_container_add_multiple_logs():
    lc = LogContainer()
    lc.add_log(
        [
            ResultEntry(
                {
                    "timestamp": "0:00:01.000100",
                    "level": "DEBUG",
                    "fields": {"message": "Debug message"},
                    "target": "target::DEBUG_message",
                    "threadId": "ThreadId(1)",
                }
            ),
            ResultEntry(
                {
                    "timestamp": "0:00:01.000101",
                    "level": "INFO",
                    "target": "target::INFO_message",
                    "threadId": "ThreadId(2)",
                }
            ),
        ]
    )
    logs = lc.get_logs()
    assert len(logs) == 2

    assert logs[0].timestamp == str(timedelta(microseconds=1000100))
    assert logs[0].level == "DEBUG"
    assert logs[0].message == "Debug message"
    assert logs[0].target == "target::DEBUG_message"
    assert logs[0].thread_id == "ThreadId(1)"

    assert logs[1].timestamp == str(timedelta(microseconds=1000101))
    assert logs[1].level == "INFO"
    assert logs[1].target == "target::INFO_message"
    assert logs[1].thread_id == "ThreadId(2)"


def test_log_container_add_raw_string():
    lc = LogContainer()
    with pytest.raises(TypeError):
        lc.add_log("raw_string_example")  # type: ignore


def test_log_container_find_log():
    lc = LogContainer()
    lc.add_log(
        ResultEntry(
            {
                "timestamp": "0:01:01.000100",
                "level": "DEBUG",
                "fields": {"message": "Debug message"},
                "target": "target::DEBUG_message",
                "threadId": "ThreadId(1)",
            }
        )
    )
    lc.add_log(
        ResultEntry(
            {
                "timestamp": "0:01:01.000100",
                "level": "INFO",
                "target": "target::INFO_message",
                "threadId": "ThreadId(2)",
            }
        )
    )
    log = lc.find_log("target", "target::DEBUG*")
    assert log
    assert log.message == "Debug message"

    log = lc.find_log("level", "INFO")
    assert log
    assert log.target == "target::INFO_message"


def test_log_container_get_logs_by_field():
    lc = LogContainer()
    lc.add_log(
        ResultEntry(
            {
                "timestamp": "0:01:01.000100",
                "level": "DEBUG",
                "fields": {"message": "Debug message 1"},
                "target": "target::DEBUG_message",
                "threadId": "ThreadId(1)",
            }
        )
    )
    lc.add_log(
        ResultEntry(
            {
                "timestamp": "0:01:01.000100",
                "level": "DEBUG",
                "fields": {"message": "Debug message 2"},
                "target": "target::DEBUG_message",
                "threadId": "ThreadId(2)",
            }
        )
    )
    logs = lc.get_logs_by_field("level", "DEBUG")
    assert len(list(logs)) == 2
    assert logs[0].message == "Debug message 1"
    assert logs[1].message == "Debug message 2"


def test_log_container_clear_logs():
    lc = LogContainer()
    lc.add_log(
        ResultEntry(
            {
                "timestamp": "0:00:01.000100",
                "level": "INFO",
                "fields": {"message": "Info message"},
                "target": "target::INFO_message",
                "threadId": "ThreadId(2)",
            }
        )
    )
    lc.clear_logs()
    assert lc.get_logs() == []


def test_log_container_groups():
    lc = LogContainer()
    lc.add_log(
        ResultEntry(
            {
                "timestamp": "0:00:00.000001",
                "level": "INFO",
                "fields": {"message": "Info message 1"},
                "target": "target::INFO_message",
                "threadId": "ThreadId(2)",
            }
        )
    )
    lc.add_log(
        ResultEntry(
            {
                "timestamp": "0:00:00.000002",
                "level": "INFO",
                "fields": {"message": "Info message 2"},
                "target": "target::INFO_message",
                "threadId": "ThreadId(1)",
            }
        )
    )
    lc.add_log(
        ResultEntry(
            {
                "timestamp": "0:00:00.000003",
                "level": "INFO",
                "fields": {"message": "Info message 3"},
                "target": "target::INFO_message",
                "threadId": "ThreadId(2)",
            }
        )
    )
    groups = lc.group_by("thread_id")
    assert len(groups) == 2
    assert len(groups["ThreadId(1)"]) == 1
    assert len(groups["ThreadId(2)"]) == 2
    assert groups["ThreadId(1)"][0].message == "Info message 2"
    assert groups["ThreadId(2)"][0].message == "Info message 1"
    assert groups["ThreadId(2)"][1].message == "Info message 3"


def test_log_container_init_entries_default_not_referenced() -> None:
    lc1 = LogContainer()
    lc1.add_log(ResultEntry({}))
    lc2 = LogContainer()
    lc2.add_log(ResultEntry({}))

    assert len(lc1.get_logs()) == 1
    assert len(lc2.get_logs()) == 1


def test_log_container_init_entries_copied_not_referenced() -> None:
    logs1 = [ResultEntry({})]
    lc1 = LogContainer(logs1)
    lc1.add_log(ResultEntry({}))
    lc2 = LogContainer()
    lc2.add_log(ResultEntry({}))

    assert len(logs1) == 1
    assert len(lc1.get_logs()) == 2
    assert len(lc2.get_logs()) == 1


def test_log_container_single_add_log_copied_not_referenced() -> None:
    logs = [ResultEntry({})]
    lc = LogContainer(logs)
    lc.add_log(ResultEntry({}))

    assert len(logs) == 1
    assert len(lc.get_logs()) == 2


def test_log_container_many_add_log_copied_not_referenced() -> None:
    logs1 = [ResultEntry({}), ResultEntry({})]
    lc = LogContainer(logs1)
    logs2 = [ResultEntry({}), ResultEntry({}), ResultEntry({})]
    lc.add_log(logs2)

    assert len(logs1) == 2
    assert len(logs2) == 3
    assert len(lc.get_logs()) == 5


def test_log_container_get_logs_by_field_str():
    lc = LogContainer()
    lc.add_log(
        [
            ResultEntry({"level": "DEBUG"}),
            ResultEntry({"level": "INFO"}),
            ResultEntry({"level": "WARN"}),
        ]
    )
    logs = lc.get_logs_by_field("level", r"WARN|INFO")
    assert len(logs) == 2
    assert logs[0].level == "INFO"
    assert logs[1].level == "WARN"


def test_log_container_get_logs_by_field_int():
    lc = LogContainer()
    lc.add_log(
        [
            ResultEntry({"someId": 1}),
            ResultEntry({"someId": 2}),
            ResultEntry({"someId": 3}),
            ResultEntry({"someId": 1}),
            ResultEntry({"someId": 1}),
        ]
    )
    logs = lc.get_logs_by_field("some_id", 1)
    assert len(logs) == 3
    assert all(log.some_id == 1 for log in logs)


def test_log_container_get_logs_by_field_none():
    lc = LogContainer()
    lc.add_log(
        [
            ResultEntry({"level": "DEBUG", "someId": 1}),
            ResultEntry({"level": "DEBUG", "someId": 2}),
            ResultEntry({"level": "INFO", "someId": None}),
            ResultEntry({"level": "WARN", "someId": 2}),
            ResultEntry({"level": "INFO", "someId": 1}),
        ]
    )
    logs = lc.get_logs_by_field("some_id", None)
    assert len(logs) == 1
    assert logs[0].some_id is None


def test_log_container_get_logs_by_field_filter_type():
    lc = LogContainer()
    lc.add_log(
        [
            ResultEntry({"level": "DEBUG", "someId": "0"}),
            ResultEntry({"level": "DEBUG", "someId": 0}),
        ]
    )
    logs = lc.get_logs_by_field("some_id", "0")
    assert len(logs) == 1
    assert logs[0].some_id == "0"

    logs = lc.get_logs_by_field("some_id", 0)
    assert len(logs) == 1
    assert logs[0].some_id == 0


def test_log_container_get_logs_by_field_invalid_key():
    lc = LogContainer()
    lc.add_log(
        [
            ResultEntry({"level": "DEBUG"}),
            ResultEntry({"level": "INFO"}),
            ResultEntry({"level": "WARN"}),
        ]
    )
    logs = lc.get_logs_by_field("invalid_entry", "invalid_pattern")
    assert len(logs) == 0


def test_log_container_get_logs_by_field_invalid_pattern_str():
    lc = LogContainer()
    lc.add_log(
        [
            ResultEntry({"level": "DEBUG"}),
            ResultEntry({"level": "INFO"}),
            ResultEntry({"level": "WARN"}),
        ]
    )
    logs = lc.get_logs_by_field("level", "invalid_pattern")
    assert len(logs) == 0


def test_log_container_get_logs_by_field_invalid_pattern_int():
    lc = LogContainer()
    lc.add_log(
        [
            ResultEntry({"someId": 1}),
            ResultEntry({"someId": 2}),
            ResultEntry({"someId": 3}),
            ResultEntry({"someId": 1}),
            ResultEntry({"someId": 1}),
        ]
    )
    logs = lc.get_logs_by_field("some_id", 10)
    assert len(logs) == 0


def test_log_container_remove_logs_str():
    lc = LogContainer()
    lc.add_log(
        [
            ResultEntry({"level": "DEBUG"}),
            ResultEntry({"level": "INFO"}),
            ResultEntry({"level": "WARN"}),
        ]
    )
    lc.remove_logs("level", r"WARN|INFO")

    logs = lc.get_logs()
    assert len(logs) == 1
    assert logs[0].level == "DEBUG"


def test_log_container_remove_logs_int():
    lc = LogContainer()
    lc.add_log(
        [
            ResultEntry({"someId": 1}),
            ResultEntry({"someId": 2}),
            ResultEntry({"someId": 3}),
            ResultEntry({"someId": 1}),
            ResultEntry({"someId": 1}),
        ]
    )
    lc.remove_logs("some_id", 1)

    logs = lc.get_logs()
    assert len(logs) == 2
    assert logs[0].some_id == 2
    assert logs[1].some_id == 3
