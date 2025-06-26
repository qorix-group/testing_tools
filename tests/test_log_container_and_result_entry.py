from datetime import timedelta

from testing_tools.log_container import LogContainer
from testing_tools.result_entry import ResultEntry


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
    assert log.message == "Debug message"

    log = lc.find_log("level", "INFO")
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
    [*logs] = lc.get_logs_by_field("level", "DEBUG")
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
