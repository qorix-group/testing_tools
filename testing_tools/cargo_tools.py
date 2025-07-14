"""
Utilities for interacting with Cargo.
"""

__all__ = ["cargo_metadata", "find_bin_path", "select_bin_path", "cargo_build"]

import json
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Any

from pytest import Config, UsageError


def cargo_metadata(metadata_timeout: float | None = None) -> dict[str, Any]:
    """
    Read Cargo metadata and return as dict.
    CWD must be inside Cargo project.

    Parameters
    ----------
    metadata_timeout : float | None
        "cargo metadata" timeout in seconds.
        Default: 10.0
    """
    metadata_timeout = metadata_timeout or 10.0

    # Run command.
    command = ["cargo", "metadata", "--format-version", "1"]
    with Popen(command, stdout=PIPE, text=True) as p:
        stdout, _ = p.communicate(timeout=metadata_timeout)
        if p.returncode != 0:
            raise RuntimeError(f"Failed to read Cargo metadata, returncode: {p.returncode}")

    # Load stdout as JSON data.
    return json.loads(stdout)


def find_bin_path(bin_name: str, metadata_timeout: float | None = None) -> Path:
    """
    Find path to executable.
    Target directory is taken from Cargo metadata.
    "debug" configuration is used.

    Returns path to executable.

    Parameters
    ----------
    bin_name : str
        Executable name.
    metadata_timeout : float | None
        "cargo metadata" timeout in seconds.
        Default: 10.0
    """
    # Read metadata.
    metadata = cargo_metadata(metadata_timeout)

    # Read target directory.
    target_directory = Path(metadata["target_directory"]).resolve()

    # Check expected file exists.
    bin_path = target_directory / "debug" / bin_name
    if not bin_path.exists():
        raise RuntimeError(f"Executable not found: {bin_path}")

    return bin_path


def select_bin_path(config: Config, metadata_timeout: float | None = None) -> Path:
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
    metadata_timeout : float | None
        "cargo metadata" timeout in seconds.
        Used only when "--bin-name" is set.
        Default: 10.0
    """
    # Types are ignored due to 'default' being incorrectly set to 'notset' type.
    if option_bin_path := config.getoption("--bin-path", default=None):  # type: ignore
        # Check path is valid.
        if not isinstance(option_bin_path, Path):
            raise UsageError(f"Invalid executable path type: {type(option_bin_path)}")
        if not option_bin_path.is_file():
            raise UsageError(f"Invalid executable path: {option_bin_path}")

        return option_bin_path

    if option_bin_name := config.getoption("--bin-name", default=None):  # type: ignore
        # Check name type is valid.
        if not isinstance(option_bin_name, str):
            raise UsageError(f"Invalid executable name type: {type(option_bin_name)}")
        # Find path, rethrow as 'UsageError' on errors.
        # Timeouts are rethrowed as 'TimeoutExpired'.
        try:
            return find_bin_path(option_bin_name, metadata_timeout)
        except TimeoutExpired as e:
            raise e
        except Exception as e:
            raise UsageError from e

    raise UsageError('Either "--bin-path" or "--bin-name" must be set')


def cargo_build(bin_name: str, metadata_timeout: float | None = None, build_timeout: float | None = None) -> Path:
    """
    Run build.
    Manifest path is taken from Cargo metadata.
    "debug" configuration" is built.

    Returns path to executable.

    Parameters
    ----------
    bin_name : str
        Executable name.
    metadata_timeout : float | None
        "cargo metadata" timeout in seconds.
        Default: 10.0
    build_timeout : float | None
        "cargo build" timeout in seconds.
        Default: 180.0
    """
    build_timeout = build_timeout or 180.0

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
