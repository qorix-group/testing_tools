use crate::monotonic_clock::MonotonicClock;
use crate::test_context::TestContext;
use std::sync::Once;
use tracing::Level;
use tracing_subscriber::FmtSubscriber;

/// Tracing subscriber should be initialized only once.
static TRACING_SUBSCRIBER_INIT: Once = Once::new();

fn init_tracing_subscriber() {
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::TRACE)
        .with_thread_ids(true)
        .with_timer(MonotonicClock::new())
        .json()
        .finish();

    tracing::subscriber::set_global_default(subscriber)
        .expect("Setting default subscriber failed!");
}

/// Test scenario arguments.
#[derive(Default)]
struct ScenarioArguments {
    /// Test scenario name.
    name: Option<String>,

    /// Test scenario input.
    input: Option<String>,
}

/// CLI arguments.
#[derive(Default)]
struct CliArguments {
    /// Test scenario arguments.
    scenario_arguments: ScenarioArguments,

    /// List scenarios.
    list_scenarios: bool,

    /// Show help.
    help: bool,
}

/// Parse CLI arguments.
///
/// * `raw_arguments` - Collected arguments from `std::env::args()`.
fn parse_cli_arguments(raw_arguments: &[String]) -> CliArguments {
    let mut cli_arguments = CliArguments::default();

    // Process arguments.
    // First argument (executable name) is skipped.
    let mut args_it = raw_arguments.iter().skip(1);
    while let Some(arg) = args_it.next() {
        match arg.as_str() {
            "-n" | "--name" => {
                if let Some(value) = args_it.next() {
                    cli_arguments.scenario_arguments.name = Some(value.clone());
                } else {
                    panic!("Failed to read name parameter");
                }
            }
            "-i" | "--input" => {
                if let Some(value) = args_it.next() {
                    cli_arguments.scenario_arguments.input = Some(value.clone());
                } else {
                    panic!("Failed to read input parameter")
                }
            }
            "-l" | "--list-scenarios" => {
                cli_arguments.list_scenarios = true;
            }
            "-h" | "--help" => {
                cli_arguments.help = true;
            }
            _ => {
                panic!("Unknown argument provided");
            }
        }
    }

    cli_arguments
}

/// Runs CLI application based on provided arguments and test context.
///
/// * `raw_arguments` - Collected arguments from `std::env::args()`.
/// * `test_context` - Test context to use.
///
/// # Examples
///
/// ```rust
/// use test_scenarios_rust::test_context::TestContext;
/// use test_scenarios_rust::scenario::ScenarioGroupImpl;
/// use test_scenarios_rust::cli::run_cli_app;
///
/// let raw_arguments = Vec::from(["example".to_string(), "--list-scenarios".to_string()]);
/// let root_group = ScenarioGroupImpl::new("root", Vec::new(), Vec::new());
/// let test_context = TestContext::new(Box::new(root_group));
///
/// run_cli_app(&raw_arguments, &test_context);
/// ```
pub fn run_cli_app(raw_arguments: &[String], test_context: &TestContext) {
    // Parse CLI arguments.
    let cli_arguments = parse_cli_arguments(raw_arguments);

    // Show help and return.
    if cli_arguments.help {
        eprintln!("Test scenario runner");
        eprintln!("'-n', '--name' - test scenario name");
        eprintln!("'-i', '--input' - test scenario input");
        eprintln!("'-l', '--list-scenarios' - list available scenarios");
        eprintln!("'-h', '--help' - show help");
        return;
    }

    // List scenarios and return.
    if cli_arguments.list_scenarios {
        let scenario_names = test_context.list_scenarios();
        for scenario_name in scenario_names {
            println!("{scenario_name}");
        }
        return;
    }

    // Find scenario.
    let scenario = cli_arguments.scenario_arguments;
    if scenario.name.is_none() || scenario.name.clone().is_some_and(|n| n.is_empty()) {
        panic!("Test scenario name must be provided");
    }

    // Initialize tracing subscriber.
    TRACING_SUBSCRIBER_INIT.call_once(|| {
        init_tracing_subscriber();
    });

    test_context
        .run(scenario.name.unwrap().as_str(), scenario.input)
        .unwrap();
}

#[cfg(test)]
mod tests {
    use crate::cli::{parse_cli_arguments, run_cli_app};
    use crate::scenario::{Scenario, ScenarioGroupImpl};
    use crate::test_context::TestContext;

    struct ScenarioStub {
        name: String,
    }

    impl ScenarioStub {
        fn new(name: &str) -> Self {
            Self {
                name: name.to_string(),
            }
        }
    }

    impl Scenario for ScenarioStub {
        fn name(&self) -> &str {
            &self.name
        }

        fn run(&self, input: Option<String>) -> Result<(), String> {
            if let Some(input) = input {
                match input.as_str() {
                    "ok" => Ok(()),
                    "error" => Err("Requested error".to_string()),
                    _ => Err("Unknown value".to_string()),
                }
            } else {
                Err("Missing input".to_string())
            }
        }
    }

    #[test]
    fn test_parse_cli_arguments_empty() {
        let raw_arguments = vec![];
        let cli_arguments = parse_cli_arguments(&raw_arguments);

        // Default values are expected.
        assert!(cli_arguments.scenario_arguments.name.is_none());
        assert!(cli_arguments.scenario_arguments.input.is_none());
        assert!(!cli_arguments.list_scenarios);
        assert!(!cli_arguments.help);
    }

    #[test]
    fn test_parse_cli_arguments_executable_name_only() {
        let exe_name = "exe_name".to_string();
        let raw_arguments = vec![exe_name];
        let cli_arguments = parse_cli_arguments(&raw_arguments);

        // Default values are expected.
        assert!(cli_arguments.scenario_arguments.name.is_none());
        assert!(cli_arguments.scenario_arguments.input.is_none());
        assert!(!cli_arguments.list_scenarios);
        assert!(!cli_arguments.help);
    }

    #[test]
    fn test_parse_cli_arguments_name_ok() {
        let exe_name = "exe_name".to_string();
        for arg in ["-n", "--name"] {
            let example_name = "example_name".to_string();
            let raw_arguments = vec![exe_name.clone(), arg.to_string(), example_name.clone()];
            let cli_arguments = parse_cli_arguments(&raw_arguments);

            assert!(cli_arguments
                .scenario_arguments
                .name
                .is_some_and(|n| n == example_name));
            assert!(cli_arguments.scenario_arguments.input.is_none());
            assert!(!cli_arguments.list_scenarios);
            assert!(!cli_arguments.help);
        }
    }

    #[test]
    #[should_panic(expected = "Failed to read name parameter")]
    fn test_parse_cli_arguments_name_missing() {
        let exe_name = "exe_name".to_string();
        let raw_arguments = [exe_name, "--name".to_string()];
        let _ = parse_cli_arguments(&raw_arguments);
    }

    #[test]
    fn test_parse_cli_arguments_input_ok() {
        for arg in ["-i", "--input"] {
            let exe_name = "exe_name".to_string();
            let example_input = "example_input".to_string();
            let raw_arguments = [exe_name.clone(), arg.to_string(), example_input.clone()];
            let cli_arguments = parse_cli_arguments(&raw_arguments);

            assert!(cli_arguments.scenario_arguments.name.is_none());
            assert!(cli_arguments
                .scenario_arguments
                .input
                .is_some_and(|n| n == example_input));
            assert!(!cli_arguments.list_scenarios);
            assert!(!cli_arguments.help);
        }
    }

    #[test]
    #[should_panic(expected = "Failed to read input parameter")]
    fn test_parse_cli_arguments_input_missing() {
        let exe_name = "exe_name".to_string();
        let raw_arguments = [exe_name, "--input".to_string()];
        let _ = parse_cli_arguments(&raw_arguments);
    }

    #[test]
    fn test_parse_cli_arguments_list_scenarios() {
        let exe_name = "exe_name".to_string();
        for arg in ["-l", "--list-scenarios"] {
            let raw_arguments = [exe_name.clone(), arg.to_string()];
            let cli_arguments = parse_cli_arguments(&raw_arguments);

            assert!(cli_arguments.scenario_arguments.name.is_none());
            assert!(cli_arguments.scenario_arguments.input.is_none());
            assert!(cli_arguments.list_scenarios);
            assert!(!cli_arguments.help);
        }
    }

    #[test]
    fn test_parse_cli_arguments_help() {
        let exe_name = "exe_name".to_string();
        for arg in ["-h", "--help"] {
            let raw_arguments = [exe_name.clone(), arg.to_string()];
            let cli_arguments = parse_cli_arguments(&raw_arguments);

            assert!(cli_arguments.scenario_arguments.name.is_none());
            assert!(cli_arguments.scenario_arguments.input.is_none());
            assert!(!cli_arguments.list_scenarios);
            assert!(cli_arguments.help);
        }
    }

    #[test]
    #[should_panic(expected = "Unknown argument provided")]
    fn test_parse_cli_arguments_unknown_argument() {
        let exe_name = "exe_name".to_string();
        let raw_arguments = [exe_name, "--invalid-arg".to_string()];
        let _ = parse_cli_arguments(&raw_arguments);
    }

    #[test]
    fn test_parse_cli_arguments_all() {
        let exe_name = "exe_name".to_string();
        let example_name = "example_name".to_string();
        let example_input = "example_input".to_string();
        let raw_arguments = [
            exe_name,
            "--help".to_string(),
            "--list-scenarios".to_string(),
            "--input".to_string(),
            example_input.clone(),
            "--name".to_string(),
            example_name.clone(),
        ];
        let cli_arguments = parse_cli_arguments(&raw_arguments);

        assert!(cli_arguments
            .scenario_arguments
            .name
            .is_some_and(|n| n == example_name));
        assert!(cli_arguments
            .scenario_arguments
            .input
            .is_some_and(|n| n == example_input));
        assert!(cli_arguments.list_scenarios);
        assert!(cli_arguments.help);
    }

    #[test]
    fn test_run_cli_app_show_help() {
        let exe_name = "exe_name".to_string();
        let raw_arguments = vec![exe_name, "--help".to_string()];
        let root_group = ScenarioGroupImpl::new("root", vec![], vec![]);
        let test_context = TestContext::new(Box::new(root_group));

        run_cli_app(&raw_arguments, &test_context);
        // It's not possible to check stderr without unstable feature.
    }

    #[test]
    fn test_run_cli_app_list_scenarios() {
        let exe_name = "exe_name".to_string();
        let raw_arguments = vec![exe_name, "--list-scenarios".to_string()];
        let root_group = ScenarioGroupImpl::new("root", vec![], vec![]);
        let test_context = TestContext::new(Box::new(root_group));

        run_cli_app(&raw_arguments, &test_context);
        // It's not possible to check stdout without unstable feature.
    }

    #[test]
    fn test_run_cli_app_ok() {
        let exe_name = "exe_name".to_string();
        let scenario_name = "example_scenario";
        let raw_arguments = [
            exe_name,
            "--name".to_string(),
            scenario_name.to_string(),
            "--input".to_string(),
            "ok".to_string(),
        ];
        let scenario = ScenarioStub::new(scenario_name);
        let root_group = ScenarioGroupImpl::new("root", vec![Box::new(scenario)], vec![]);
        let test_context = TestContext::new(Box::new(root_group));

        run_cli_app(&raw_arguments, &test_context);
    }

    #[test]
    #[should_panic(expected = "Requested error")]
    fn test_run_cli_app_error() {
        let exe_name = "exe_name".to_string();
        let scenario_name = "example_scenario";
        let raw_arguments = [
            exe_name,
            "--name".to_string(),
            scenario_name.to_string(),
            "--input".to_string(),
            "error".to_string(),
        ];
        let scenario = ScenarioStub::new(scenario_name);
        let root_group = ScenarioGroupImpl::new("root", vec![Box::new(scenario)], vec![]);
        let test_context = TestContext::new(Box::new(root_group));

        // It's expected that test will fail due to error from `ScenarioStub`, not from `run_cli_app`.
        run_cli_app(&raw_arguments, &test_context);
    }

    #[test]
    #[should_panic(expected = "Missing input")]
    fn test_run_cli_app_missing_input() {
        let exe_name = "exe_name".to_string();
        let scenario_name = "example_scenario";
        let raw_arguments = [exe_name, "--name".to_string(), scenario_name.to_string()];
        let scenario = ScenarioStub::new(scenario_name);
        let root_group = ScenarioGroupImpl::new("root", vec![Box::new(scenario)], vec![]);
        let test_context = TestContext::new(Box::new(root_group));

        // It's expected that test will fail due to error from `ScenarioStub`, not from `run_cli_app`.
        run_cli_app(&raw_arguments, &test_context);
    }

    #[test]
    #[should_panic(expected = "Test scenario name must be provided")]
    fn test_run_cli_app_missing_name() {
        let exe_name = "exe_name".to_string();
        let scenario_name = "example_scenario";
        let raw_arguments = vec![exe_name];
        let scenario = ScenarioStub::new(scenario_name);
        let root_group = ScenarioGroupImpl::new("root", vec![Box::new(scenario)], vec![]);
        let test_context = TestContext::new(Box::new(root_group));

        run_cli_app(&raw_arguments, &test_context);
    }

    #[test]
    #[should_panic(expected = "Scenario invalid_scenario not found")]
    fn test_run_cli_app_invalid_name() {
        let exe_name = "exe_name".to_string();
        let scenario_name = "example_scenario";
        let raw_arguments = [
            exe_name,
            "--name".to_string(),
            "invalid_scenario".to_string(),
        ];
        let scenario = ScenarioStub::new(scenario_name);
        let root_group = ScenarioGroupImpl::new("root", vec![Box::new(scenario)], vec![]);
        let test_context = TestContext::new(Box::new(root_group));

        // It's expected that test will fail due to error from `TestContext`, not from `run_cli_app`.
        run_cli_app(&raw_arguments, &test_context);
    }
}
