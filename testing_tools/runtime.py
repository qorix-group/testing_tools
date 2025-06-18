import json
import os
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired

TEST_BIN_ENV_VAR = "TEST_BINARY_PATH"
EXECUTE_TIMEOUT_S = 5
BUILD_TIMEOUT_S = 180


def execute(test_config, test_case_name):
    hang = False
    test_binary_path = os.environ[TEST_BIN_ENV_VAR]
    test_config_json = json.dumps(test_config)

    command = [test_binary_path, "--name", test_case_name]
    p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
    try:
        outs, errs = p.communicate(test_config_json, EXECUTE_TIMEOUT_S)
    except TimeoutExpired:
        hang = True
        p.kill()
        outs, errs = p.communicate()

    return outs, errs, hang, p.returncode


def execute_and_parse(test_config, test_case_name, expect_hang):
    outs, errs, hang, return_code = execute(test_config, test_case_name)

    if expect_hang and not hang:
        raise RuntimeError(f"Expecting hang, but test finished! stdout: {outs}; stderr: {errs}")
    elif not expect_hang and hang:
        raise RuntimeError(f"Execution hanged! stdout: {outs}; stderr: {errs}")

    # TODO: Check return code for hang and accept non-zero return code for this case
    if return_code != 0:
        raise RuntimeError(f"Execution failed with return code {return_code}. stdout: {outs}; stderr: {errs}")

    raw_messages = outs.strip().split("\n")
    # Filter non-json messages
    raw_messages = [message for message in raw_messages if message.startswith("{") and message.endswith("}")]

    # Messages may not be in the chronological order
    messages = [json.loads(message) for message in raw_messages]
    messages.sort(key=lambda m: m["timestamp"])

    return messages


def build_rust_scenarios(path_to_scenarios: Path | str) -> Path:
    """
    Build the rust test scenarios from the given path.
    """
    if not isinstance(path_to_scenarios, Path):
        path_to_scenarios = Path(path_to_scenarios)
    path_to_scenarios.resolve()

    path_to_manifest = path_to_scenarios / "Cargo.toml"
    if not path_to_manifest.exists():
        raise FileNotFoundError(
            f"Cargo.toml not found at {path_to_manifest}. Please provide a valid path to the rust test scenarios."
        )

    command = ["cargo", "build", "--manifest-path", path_to_manifest]
    p = Popen(command, stdout=PIPE, stderr=PIPE, text=True)

    outs, errs = p.communicate(timeout=BUILD_TIMEOUT_S)

    if p.returncode != 0:
        raise RuntimeError(f"Building rust test scenarios failed with {p.returncode}! stdout: {outs}; stderr: {errs}")

    return path_to_scenarios / "target" / "debug" / "rust_test_scenarios"
