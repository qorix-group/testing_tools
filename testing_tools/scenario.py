"""
Utilities for defining and running test scenarios.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Any

import pytest
from pytest import FixtureRequest

from .cargo_tools import select_bin_path
from .log_container import LogContainer
from .result_entry import ResultEntry


@dataclass
class ScenarioResult:
    """
    Test scenario executable result.
    """

    stdout: str
    stderr: str
    return_code: int | None
    hang: bool


class Scenario(ABC):
    """
    Base test scenario definition.
    """

    @pytest.fixture(scope="class")
    @abstractmethod
    def scenario_name(self) -> str:
        """
        Name of a test scenario to run.
        """
        pass

    @pytest.fixture(scope="class")
    @abstractmethod
    def test_config(self) -> dict[str, Any]:
        """
        Test configuration.
        """
        pass

    @pytest.fixture(scope="class")
    def execution_timeout(self, request: FixtureRequest) -> float:
        """
        Test execution timeout in seconds.

        Parameters
        ----------
        request : FixtureRequest
            Test request built-in fixture.
        """
        timeout = request.config.getoption("--default-execution-timeout")
        if isinstance(timeout, float):
            return timeout
        else:
            return 5.0

    @pytest.fixture(scope="class")
    def bin_path(self, request: FixtureRequest) -> Path:
        """
        Return path to test scenario executable.

        Parameters
        ----------
        request : FixtureRequest
            Test request built-in fixture.
        """
        return select_bin_path(request.config)

    @pytest.fixture(scope="class")
    def results(
        self, bin_path: Path | str, scenario_name: str, test_config: dict[str, Any], execution_timeout: float
    ) -> ScenarioResult:
        """
        Execute test scenario executable and return results.

        Parameters
        ----------
        bin_path : Path | str
            Path to test scenarios executable.
        scenario_name : str
            Name of a test scenario to run.
        test_config : dict[str, Any]
            Test configuration.
        execution_timeout : float
            Test execution timeout in seconds.
        """
        # Dump test configuration to string.
        test_config_str = json.dumps(test_config)

        # Run scenario.
        hang = False

        command = [bin_path, "--name", scenario_name]
        # TODO: check if stderr must be passed to PIPE.
        # Maybe it can be shown during execution.
        p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
        try:
            stdout, stderr = p.communicate(test_config_str, execution_timeout)
        except TimeoutExpired:
            hang = True
            p.kill()
            stdout, stderr = p.communicate()

        return ScenarioResult(stdout, stderr, p.returncode, hang)

    @pytest.fixture(scope="class")
    def logs(self, results: ScenarioResult) -> LogContainer:
        """
        Execute test scenario executable and return logs.

        Parameters
        ----------
        results : ScenarioResult
            Scenario results fixture.
        """
        # Split into lines.
        text_lines = results.stdout.strip().split("\n")

        # Filter out non-JSON messages.
        messages = filter(lambda m: m.startswith("{") and m.endswith("}"), text_lines)
        messages = list(map(lambda m: json.loads(m), messages))

        # Convert timestamp from microseconds to timedelta.
        for msg in messages:
            msg["timestamp"] = timedelta(microseconds=int(msg["timestamp"]))

        # Sort messages into chronological order.
        messages.sort(key=lambda m: m["timestamp"])

        # Convert messages to list of ResultEntry and create log container.
        result_entries = [ResultEntry(msg) for msg in messages]
        return LogContainer(result_entries)
