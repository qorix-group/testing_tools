"""
Utilities for interacting with Cargo.
"""

__all__ = ["cargo_metadata", "find_bin_path", "select_bin_path", "cargo_build"]

import json
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Any

from pytest import Config, UsageError


def cargo_metadata(metadata_timeout: float = 10.0) -> dict[str, Any]:
    """
    Read Cargo metadata and return as dict.
    CWD must be inside Cargo project.

    Parameters
    ----------
    metadata_timeout : float
        "cargo metadata" timeout in seconds.
    """
    # Run command.
    command = ["cargo", "metadata", "--format-version", "1"]
    with Popen(command, stdout=PIPE, text=True) as p:
        stdout, _ = p.communicate(timeout=metadata_timeout)
        if p.returncode != 0:
            raise RuntimeError(f"Failed to read Cargo metadata, returncode: {p.returncode}")

    # Load stdout as JSON data.
    return json.loads(stdout)


def find_bin_path(bin_name: str, expect_exists: bool = True, metadata_timeout: float = 10.0) -> Path:
    """
    Find path to executable.
    Target directory is taken from Cargo metadata.
    "debug" configuration is used.

    Returns path to executable.

    Parameters
    ----------
    bin_name : str
        Executable name.
    expect_exists : bool
        Check that executable exists.
    metadata_timeout : float
        "cargo metadata" timeout in seconds.
    """
    # Read metadata.
    metadata = cargo_metadata(metadata_timeout=metadata_timeout)

    # Read target directory.
    target_directory = Path(metadata["target_directory"]).resolve()

    # Check expected file exists.
    bin_path = target_directory / "debug" / bin_name
    if expect_exists and not bin_path.exists():
        raise RuntimeError(f"Executable not found: {bin_path}")

    return bin_path


def select_bin_path(config: Config, expect_exists: bool = True, metadata_timeout: float = 10.0) -> Path:
    """
    Select executable path based on "--bin-path" and "--bin-name" options.
    Execution order is following:
    - if "--bin-path" is set - use it
    - if "--bin-path" not set - search for an executable named "--bin-name"
    - if "--bin-name" not set - error

    Parameters
    ----------
    config : Config
        Pytest config object.
    expect_exists : bool
        Check that executable exists.
    metadata_timeout : float
        "cargo metadata" timeout in seconds.
        Used only when "--bin-name" is set.
    """
    # Types are ignored due to 'default' being incorrectly set to 'notset' type.
    if option_bin_path := config.getoption("--bin-path", default=None):  # type: ignore
        # Check path is valid.
        if not isinstance(option_bin_path, Path):
            raise UsageError(f"Invalid executable path type: {type(option_bin_path)}")
        if expect_exists and not option_bin_path.is_file():
            raise UsageError(f"Invalid executable path: {option_bin_path}")

        return option_bin_path

    if option_bin_name := config.getoption("--bin-name", default=None):  # type: ignore
        # Check name type is valid.
        if not isinstance(option_bin_name, str):
            raise UsageError(f"Invalid executable name type: {type(option_bin_name)}")
        # Find path, rethrow as 'UsageError' on errors.
        # Timeouts are rethrowed as 'TimeoutExpired'.
        try:
            return find_bin_path(option_bin_name, expect_exists, metadata_timeout)
        except TimeoutExpired as e:
            raise e
        except Exception as e:
            raise UsageError from e

    raise UsageError('Either "--bin-path" or "--bin-name" must be set')


def cargo_build(bin_name: str, metadata_timeout: float = 10.0, build_timeout: float = 180.0) -> Path:
    """
    Run build.
    Manifest path is taken from Cargo metadata.
    "debug" configuration" is built.

    Returns path to executable.

    Parameters
    ----------
    bin_name : str
        Executable name.
    metadata_timeout : float
        "cargo metadata" timeout in seconds.
    build_timeout : float
        "cargo build" timeout in seconds.
    """
    # Read metadata.
    metadata = cargo_metadata(metadata_timeout)

    # Read manifest path from metadata.
    pkg_entries = list(filter(lambda x: x["name"] == bin_name, metadata["packages"]))
    if len(pkg_entries) < 1:
        raise RuntimeError(f"No data found for {bin_name}")
    if len(pkg_entries) > 1:
        raise RuntimeError(f"Multiple data found for {bin_name}")
    pkg_entry = pkg_entries[0]

    manifest_path = Path(pkg_entry["manifest_path"]).resolve()

    # Run build.
    command = ["cargo", "build", "--manifest-path", manifest_path]
    with Popen(command, text=True) as p:
        _, _ = p.communicate(timeout=build_timeout)
        if p.returncode != 0:
            raise RuntimeError(f"Failed to run build, returncode: {p.returncode}")

    return find_bin_path(bin_name, metadata_timeout)
