# testing_tools Examples

Example programs demonstrating `test_scenarios_cpp` and `test_scenarios_rust`. C++ examples are
located in [score/test_scenarios_cpp/examples](../score/test_scenarios_cpp/examples), and Rust
examples in [score/test_scenarios_rust/examples](../score/test_scenarios_rust/examples). In this
directory there are Bazel aliases for convenience.

## Running Examples

```bash
bazel run //examples:cpp_basic -- --list-scenarios
bazel run //examples:cpp_basic -- --name version.parse --input 8.6.0
bazel run //examples:cpp_basic -- --name version.satisfies_minimum --input 8.6.0
bazel run //examples:cpp_basic -- --name version.satisfies_minimum --input 8.4.2

bazel run //examples:rust_basic -- --list-scenarios
bazel run //examples:rust_basic -- --name version.parse --input 8.6.0
bazel run //examples:rust_basic -- --name version.satisfies_minimum --input 8.6.0
bazel run //examples:rust_basic -- --name version.satisfies_minimum --input 8.4.2
```

## Available Examples

### basic (C++ and Rust)

A foundational example demonstrating the core building blocks of the library:

- Implementing `Scenario` — `version.parse` parses a `major.minor.patch` string and reports its
  components (failing genuinely on a malformed version); `version.satisfies_minimum` parses the
  input the same way and fails genuinely if it's below this repo's own minimum supported Bazel
  version, `8.6.0` (e.g. `--input 8.4.2` fails, `--input 8.6.0` succeeds)
- Grouping scenarios with `ScenarioGroupImpl`, including a nested group (`version`) to show how
  nesting produces dotted scenario names (`version.parse`, `version.satisfies_minimum`)
- Wiring a `TestContext` and running it through `run_cli_app`, which provides
  `--list-scenarios`, `--name`, and `--input` for free

**Key concepts:** `Scenario`, `ScenarioGroupImpl` (including nested groups), `TestContext`,
`run_cli_app`, CLI argument handling, error propagation
