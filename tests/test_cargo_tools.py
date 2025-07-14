"""
Tests for "cargo_tools" module.
"""

import os
from contextlib import contextmanager
from pathlib import Path
from subprocess import Popen, TimeoutExpired
from typing import Any, Generator

from pytest import UsageError, fixture, raises

from testing_tools import cargo_tools


@contextmanager
def cwd(new_cwd: Path | str) -> Generator[None, None, None]:
    """
    Temporarily change working directory.

    Parameters
    ----------
    new_cwd : Path
        Directory to set as CWD.
    """
    prev_cwd = os.getcwd()
    os.chdir(new_cwd)
    yield
    os.chdir(prev_cwd)


@fixture
def tmp_project(tmp_path: Path) -> tuple[str, Path]:
    """
    Create temporary binary project using Cargo.
    Returns binary name and path to project directory.

    Parameters
    ----------
    tmp_path : Path
        Temporary directory path.
    """
    # Binary name and path to project.
    bin_name = "project"
    project_path = tmp_path / bin_name

    # Create binary project.
    command = ["cargo", "new", "--bin", project_path]
    with Popen(command, text=True) as p:
        _, _ = p.communicate(timeout=30.0)
        if p.returncode != 0:
            raise RuntimeError("Failed to create temporary binary project")

    return (bin_name, project_path)


@fixture
def built_tmp_project(tmp_project: tuple[str, Path]) -> tuple[str, Path]:
    """
    Create and build temporary binary project using Cargo.
    Returns binary name and path to project directory.

    Parameters
    ----------
    tmp_project : Path
        Path to temporary project directory.
    """
    bin_name, path = tmp_project
    with cwd(path):
        _ = cargo_tools.cargo_build(bin_name)
        return tmp_project


# region cargo_metadata tests


def test_cargo_metadata_ok(tmp_project: tuple[str, Path]) -> None:
    _, path = tmp_project
    with cwd(path):
        metadata = cargo_tools.cargo_metadata()

        # Check on "target_directory" if valid.
        act_target_dir = Path(metadata["target_directory"])
        exp_target_dir = path / "target"
        assert act_target_dir == exp_target_dir


def test_cargo_metadata_timeout(tmp_project: tuple[str, Path]) -> None:
    _, path = tmp_project
    with cwd(path), raises(TimeoutExpired):
        timeout = 0.00000001
        _ = cargo_tools.cargo_metadata(timeout)


# endregion

# region cargo_build tests


def test_cargo_build_ok(tmp_project: tuple[str, Path]) -> None:
    bin_name, path = tmp_project
    with cwd(path):
        bin_path = cargo_tools.cargo_build(bin_name)

        # Check executable exists.
        assert bin_path.exists()


def test_cargo_build_metadata_timeout(tmp_project: tuple[str, Path]) -> None:
    bin_name, path = tmp_project
    with cwd(path), raises(TimeoutExpired):
        metadata_timeout = 0.00000001
        _ = cargo_tools.cargo_build(bin_name, metadata_timeout=metadata_timeout)


def test_cargo_build_build_timeout(tmp_project: tuple[str, Path]) -> None:
    bin_name, path = tmp_project
    with cwd(path), raises(TimeoutExpired):
        build_timeout = 0.00000001
        _ = cargo_tools.cargo_build(bin_name, build_timeout=build_timeout)


def test_cargo_build_invalid_bin_name(tmp_project: tuple[str, Path]) -> None:
    _, path = tmp_project
    with cwd(path), raises(RuntimeError):
        invalid_bin_name = "xyz"
        _ = cargo_tools.cargo_build(invalid_bin_name)


def test_cargo_build_invalid_cwd(tmp_project: tuple[str, Path]) -> None:
    bin_name, _ = tmp_project
    invalid_project_path = "/tmp"
    with cwd(invalid_project_path), raises(RuntimeError):
        _ = cargo_tools.cargo_build(bin_name)


# endregion


# region find_bin_path tests


def test_find_bin_path_ok(built_tmp_project: tuple[str, Path]) -> None:
    bin_name, path = built_tmp_project
    with cwd(path):
        act_bin_path = cargo_tools.find_bin_path(bin_name)

        # Check executable exists at expected path.
        exp_bin_path = path / "target" / "debug" / bin_name
        assert act_bin_path == exp_bin_path


def test_find_bin_path_timeout(built_tmp_project: tuple[str, Path]) -> None:
    bin_name, path = built_tmp_project
    with cwd(path), raises(TimeoutExpired):
        metadata_timeout = 0.00000001
        _ = cargo_tools.find_bin_path(bin_name, metadata_timeout=metadata_timeout)


def test_find_bin_path_invalid_bin_name(built_tmp_project: tuple[str, Path]) -> None:
    _, path = built_tmp_project
    with cwd(path), raises(RuntimeError):
        invalid_bin_name = "invalid_bin_name"
        _ = cargo_tools.find_bin_path(invalid_bin_name)


def test_find_bin_path_invalid_cwd(built_tmp_project: tuple[str, Path]) -> None:
    bin_name, _ = built_tmp_project
    invalid_project_path = "/tmp"
    with cwd(invalid_project_path), raises(RuntimeError):
        _ = cargo_tools.find_bin_path(bin_name)


# endregion

# region select_bin_path tests


class Notset:
    def __repr__(self):
        return "<NOTSET>"


notset = Notset()


class MockConfig:
    """
    "Config" object mock.
    """

    def __init__(self, options: dict[str, Any]) -> None:
        self._options = options

    def getoption(self, name: str, default: Any = notset) -> Any:
        value = self._options.get(name, default)
        if value is notset:
            raise ValueError()
        return value


def test_select_bin_path_bin_path_set_ok(built_tmp_project: tuple[str, Path]) -> None:
    bin_name, path = built_tmp_project
    with cwd(path):
        # Find executable path.
        exp_bin_path = cargo_tools.find_bin_path(bin_name)

        # Create mock.
        cfg = MockConfig({"--bin-path": exp_bin_path})

        # Run.
        act_bin_path = cargo_tools.select_bin_path(cfg)  # type: ignore

        # Check executable exists at expected path.
        assert act_bin_path == exp_bin_path


def test_select_bin_path_bin_path_set_invalid_type(built_tmp_project: tuple[str, Path]) -> None:
    bin_name, path = built_tmp_project
    with cwd(path), raises(UsageError):
        # Find executable path.
        exp_bin_path = cargo_tools.find_bin_path(bin_name)

        # Create mock.
        cfg = MockConfig({"--bin-path": str(exp_bin_path)})

        # Run.
        _ = cargo_tools.select_bin_path(cfg)  # type: ignore


def test_select_bin_path_bin_path_set_invalid_value(built_tmp_project: tuple[str, Path]) -> None:
    _, path = built_tmp_project
    with cwd(path), raises(UsageError):
        # Create mock.
        invalid_bin_path = Path("/invalid/path")
        cfg = MockConfig({"--bin-path": invalid_bin_path})

        # Run.
        _ = cargo_tools.select_bin_path(cfg)  # type: ignore


def test_select_bin_path_bin_name_set_ok(built_tmp_project: tuple[str, Path]) -> None:
    bin_name, path = built_tmp_project
    with cwd(path):
        # Find executable path.
        exp_bin_path = cargo_tools.find_bin_path(bin_name)

        # Create mock.
        cfg = MockConfig({"--bin-name": bin_name})

        # Run.
        act_bin_path = cargo_tools.select_bin_path(cfg)  # type: ignore

        # Check executable exists at expected path.
        assert act_bin_path == exp_bin_path


def test_select_bin_path_bin_name_set_invalid_type(built_tmp_project: tuple[str, Path]) -> None:
    bin_name, path = built_tmp_project
    with cwd(path), raises(UsageError):
        # Create mock.
        cfg = MockConfig({"--bin-name": Path(bin_name)})

        # Run.
        _ = cargo_tools.select_bin_path(cfg)  # type: ignore


def test_select_bin_path_bin_name_set_invalid_value(built_tmp_project: tuple[str, Path]) -> None:
    _, path = built_tmp_project
    with cwd(path), raises(UsageError):
        # Create mock.
        invalid_bin_name = "invalid_bin_name"
        cfg = MockConfig({"--bin-name": invalid_bin_name})

        # Run.
        _ = cargo_tools.select_bin_path(cfg)  # type: ignore


def test_select_bin_path_bin_name_timeout(built_tmp_project: tuple[str, Path]) -> None:
    bin_name, path = built_tmp_project
    with cwd(path), raises(TimeoutExpired):
        # Create mock.
        cfg = MockConfig({"--bin-name": bin_name})

        # Run.
        metadata_timeout = 0.00000001
        _ = cargo_tools.select_bin_path(cfg, metadata_timeout=metadata_timeout)  # type: ignore


def test_select_bin_path_params_unset(built_tmp_project: tuple[str, Path]) -> None:
    _, path = built_tmp_project
    with cwd(path), raises(UsageError):
        # Create mock.
        cfg = MockConfig({})

        # Run.
        _ = cargo_tools.select_bin_path(cfg)  # type: ignore


# endregion
