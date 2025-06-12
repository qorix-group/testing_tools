# testing-tools

Test framework tools and helpers for performance stack project. 

## Overview

This package provides utility classes and functions to assist with test automation, log handling, and result parsing. It is designed to be used as a helper library for test frameworks or custom test runners.

## Features

- **LogContainer**: A container for storing and querying log/result entries.
- **ResultEntry** and subclasses: Structured representations of test log entries.
- **Runtime utilities**: Functions to execute test binaries and parse their output.

## Installation
You can create and activate a virtual environment for the development purposes:
```sh
python -m venv .venv
source .venv/bin/activate
```

You can install the development dependencies using:

```sh
pip install -e .[dev]
```

## Usage

### LogContainer Example

```python
from testing_tools.log_container import LogContainer
from testing_tools.result_entry import ResultOrchestration

lc = LogContainer()
lc.add_log(
    ResultOrchestration({
        "timestamp": "2025-06-05T07:46:11.796134Z",
        "level": "DEBUG",
        "fields": {"message": "Debug message"},
        "target": "target::DEBUG_message",
        "threadId": "ThreadId(1)",
    })
)
logs = lc.get_logs()
print(logs[0].message)  # Output: Debug message
```
LogContainer is used to parse JSON log traces and offers methods to search them.

```python
from testing_tools.log_container import LogContainer
from testing_tools.result_entry import ResultRuntime

logs = [ResultRuntime(msg) for msg in messages]  # messages is a list of JSON logs
lc = LogContainer.from_entries(logs)
lc.contains_log(field="message", pattern="SomeExampleAction")  # True
```

### Running Tests

To run the tests, use:

```sh
python -m pytest
```

## Development

- Python 3.12+ required.
- Code style is enforced with [ruff](https://github.com/astral-sh/ruff).

