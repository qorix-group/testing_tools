import json
from datetime import timedelta
from pathlib import Path
from functools import cache
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Any
from .log_container import LogContainer
from .result_entry import ResultEntry


def execute(
    rust_scenario_bin_path: Path | str,
    scenario_name: str,
    test_config: dict[str, Any],
    execution_timeout_s: float | None = None,
) -> LogContainer:
    """
    Execute test scenario and return results.

    Parameters
    ----------
    rust_scenario_bin_path : Path | str
        Path to test scenarios executable.
    scenario_name : str
        Scenario name.
    test_config : dict[str, Any]
        Test configuration.
    execution_timeout_s : float | None
        Execution timeout in seconds.
        Default: 5.0
    """
    # Set timeout.
    execution_timeout = execution_timeout_s or 5.0

    # Dump test configuration to string.
    test_config_str = json.dumps(test_config)

    # Run scenario.
    hang = False
    command = [rust_scenario_bin_path, "--name", scenario_name]
    p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
    try:
        stdout, _ = p.communicate(test_config_str, execution_timeout)
    except TimeoutExpired:
        hang = True
        p.kill()
        stdout, _ = p.communicate()

    # Read messages from stdout.
    raw_messages = stdout.strip().split("\n")
    # Filter non-JSON messages.
    raw_messages = [message for message in raw_messages if message.startswith("{") and message.endswith("}")]
    messages = [json.loads(message) for message in raw_messages]

    # Convert timestamp from microseconds to timedelta.
    messages = list(
        map(lambda message: {**message, "timestamp": timedelta(microseconds=int(message["timestamp"]))}, messages)
    )

    # Sort messages into chronological order.
    messages.sort(key=lambda m: m["timestamp"])

    # Convert to list of ResultEntry.
    result_entries = [ResultEntry(msg) for msg in messages]

    # Return results as LogContainer.
    return LogContainer(result_entries, p.returncode, hang)


@cache
def _read_cargo_metadata(cargo_metadata_timeout_s: float | None = None) -> dict[str, Any]:
    """
    Read Cargo metadata and return as dict.
    CWD must be inside Cargo project.
    Result is cached and assumed to remain persistent during execution.

    Parameters
    ----------
    cargo_metadata_timeout_s : float | None
        "cargo metadata" timeout in seconds.
        Default: 10.0
    """
    # Set default timeout.
    metadata_timeout = cargo_metadata_timeout_s or 10.0

    # Run command.
    cmd = "cargo metadata --format-version 1"
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, text=True, shell=True)
    stdout, stderr = p.communicate(timeout=metadata_timeout)
    if p.returncode != 0:
        raise RuntimeError(
            f"Failed to read Cargo metadata, returncode: {p.returncode}, stdout: {stdout}, stderr: {stderr}"
        )

    # Load stdout as JSON data.
    return json.loads(stdout)


def find_test_scenarios_bin(
    rust_scenarios_bin_name: str | None = None, cargo_metadata_timeout_s: float | None = None
) -> Path:
    """
    Find path to test scenarios executable.
    Target directory is taken from Cargo metadata.
    "debug" configuration is used.

    Returns path to executable.

    Parameters
    ----------
    rust_scenarios_bin_name : str | None
        Scenarios executable name.
        Default: "rust_test_scenarios"
    cargo_metadata_timeout_s : float | None
        "cargo metadata" timeout in seconds.
        Default: 10.0
    """
    # Set default name.
    bin_name = rust_scenarios_bin_name or "rust_test_scenarios"

    # Read metadata.
    metadata = _read_cargo_metadata(cargo_metadata_timeout_s)

    # Read target directory.
    target_directory = Path(metadata["target_directory"]).resolve()

    # Check expected file exists.
    bin_path = target_directory / "debug" / bin_name
    if not bin_path.exists():
        raise RuntimeError("Rust scenarios executable not found")

    return bin_path


def build_test_scenarios(
    rust_scenarios_bin_name: str | None = None,
    cargo_metadata_timeout_s: float | None = None,
    cargo_build_timeout_s: float | None = None,
) -> Path:
    """
    Build Rust test scenarios.
    Manifest path is taken from Cargo metadata.
    "debug" configuration is built.

    Returns path to executable.

    Parameters
    ----------
    rust_scenarios_bin_name : str | None
        Scenarios executable name.
        Default: "rust_test_scenarios"
    cargo_metadata_timeout_s : float | None
        "cargo metadata" timeout in seconds.
        Default: 10.0
    cargo_build_timeout_s : float | None
        "cargo build" timeout in seconds.
        Default: 180.0
    """
    # Set default name.
    bin_name = rust_scenarios_bin_name or "rust_test_scenarios"

    # Set default build timeout.
    build_timeout = cargo_build_timeout_s or 180.0

    # Read metadata.
    metadata = _read_cargo_metadata(cargo_metadata_timeout_s)

    # Read manifest path from metadata.
    pkg_entries = list(filter(lambda x: x["name"] == bin_name, metadata["packages"]))
    if len(pkg_entries) < 1:
        raise RuntimeError(f"No data found for {bin_name}")
    elif len(pkg_entries) > 1:
        raise RuntimeError(f"Multiple data found for {bin_name}")
    pkg_entry = pkg_entries[0]

    manifest_path = Path(pkg_entry["manifest_path"]).resolve()

    # Run build.
    build_cmd = f"cargo build --manifest-path {manifest_path}"
    p = Popen(build_cmd, stdout=PIPE, stderr=PIPE, text=True, shell=True)
    stdout, stderr = p.communicate(timeout=build_timeout)

    if p.returncode != 0:
        raise RuntimeError(
            f"Failed to build test scenarios, returncode: {p.returncode}, stdout: {stdout}, stderr: {stderr}"
        )

    return find_test_scenarios_bin()
