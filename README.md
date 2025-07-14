# `testing-tools`

Test framework tools and helpers for performance stack project.

## Overview

This package provides utility classes and functions to assist with test automation, log handling, and result parsing.
It is designed to be used as a helper library for test frameworks or custom test runners.

## Features

- **Cargo tools**: Utilities for interacting with Cargo.
- **Log container**: A container for storing and querying logs.
- **`ResultEntry`** and subclasses: Structured representation of test log entries.
- **Scenario**: Utilities for defining and running test scenarios.

## Installation

`virtualenv` usage is recommended:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install `testing_tools`:

```bash
pip install .
```

Install `testing_tools` in editable mode with additional dev dependencies:

```bash
pip install -e .[dev]
```

## Usage

### Cargo tools

#### Get Cargo metadata

Cargo metadata is obtained using "cargo metadata" command.
CWD must be set to Cargo project.

```python
from typing import Any
from testing_tools import cargo_metadata

metadata: dict[str, Any] = cargo_metadata()
```

#### Find executable path

Path is obtained from Cargo metadata.
CWD must be set to Cargo project.

```python
from pathlib import Path
from testing_tools import find_bin_path

bin_name = "executable_name"
bin_path: Path = find_bin_path(bin_name)
...
```

#### Select executable

This feature is to ensure flexible usage in pytest context.
Additional configuration is required.

Add options to `conftest.py`:

```python
from pathlib import Path

def pytest_addoption(parser):
    parser.addoption(
        "--bin-path",
        type=Path,
        help="Path to test scenarios executable. Search is performed by default.",
    )
    parser.addoption(
        "--bin-name",
        type=str,
        default="rust_test_scenarios",
        help='Test scenario executable name. Overwritten by "--bin-path".',
    )
```

Usage:

```python
from pathlib import Path
from pytest import FeatureRequest
from testing_tools import select_bin_path

def test_example(request: FeatureRequest) -> None:
    bin_path: Path = select_bin_path(request.config)
    ...
```

#### Run Cargo build

Run build based on manifest located in CWD.
CWD must be set to Cargo project.

```python
from testing_tools import cargo_build

bin_name = "rust_executable"
bin_path: Path = cargo_build(bin_name)
...
```

### Log container and `ResultEntry` example

Usage as container:

```python
from testing_tools import LogContainer, ResultEntry

lc = LogContainer()
lc.add_log(
    ResultEntry({
        "timestamp": "2025-06-05T07:46:11.796134Z",
        "level": "DEBUG",
        "fields": {"message": "Debug message"},
        "target": "target::DEBUG_message",
        "threadId": "ThreadId(1)",
    })
)
logs = lc.get_logs()
# Output: debug message.
print(logs[0].message)
```

Usage as JSON log trace parser:

```python
from testing_tools import LogContainer, ResultEntry

# "messages" is a list of JSON logs.
logs = [ResultEntry(msg) for msg in messages]
lc = LogContainer(logs)
lc.contains_log(field="message", pattern="SomeExampleAction")  # True
```

Usage as log filter:

```python
from testing_tools import LogContainer, ResultEntry

# "messages" is a list of JSON logs.
logs = [ResultEntry(msg) for msg in messages]
lc = LogContainer(logs)
lc_only_info = lc.get_logs_by_field(field="level", pattern="INFO")
```

### Scenario example

`Scenario` is a base class containing basic test behavior.
Test execution results are provided using two fixtures:

- `results` - executable run results
- `logs` - logs from run

`scenario_name` and `test_config` are marked as abstract and must be implemented.

Example implementation:

```python
from testing_tools import Scenario, ScenarioResult, LogContainer

class TestExample(Scenario):
    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "example_scenario_name"

    @pytest.fixture(scope="class")
    def test_config(self) -> dict[str, Any]:
        return {"runtime": {"task_queue_size": 256, "workers": 1}}

    def test_example(self, results: ScenarioResult, logs: LogContainer) -> None:
        ...
```

Execution timeout uses `"--default-execution-timeout"` set in `conftest.py`, or is set to 5 seconds by default.

`stderr` is shown, but not captured default.
To capture `stderr` use:

```python
class TestExample(Scenario):
    def capture_stderr(self) -> bool:
        return True

    ...
```

## Development

- Python 3.12+ required.
- Code style is enforced with [ruff](https://github.com/astral-sh/ruff).

To run the tests, use:

```bash
pytest -vs .
```
