// *******************************************************************************
// Copyright (c) 2026 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache License Version 2.0 which is available at
// https://www.apache.org/licenses/LICENSE-2.0
//
// SPDX-License-Identifier: Apache-2.0
// *******************************************************************************

use std::process::ExitCode;

use test_scenarios_rust::cli::run_cli_app;
use test_scenarios_rust::scenario::{Scenario, ScenarioGroupImpl};
use test_scenarios_rust::test_context::TestContext;

const MIN_VERSION: (u32, u32, u32) = (8, 6, 0);

fn parse_version(input: &str) -> Result<(u32, u32, u32), String> {
    let parts: Vec<&str> = input.split('.').collect();
    let err = || format!("'{input}' is not a valid major.minor.patch version");
    if parts.len() != 3 {
        return Err(err());
    }
    let mut numbers = [0u32; 3];
    for (i, part) in parts.iter().enumerate() {
        numbers[i] = part.parse::<u32>().map_err(|_| err())?;
    }
    Ok((numbers[0], numbers[1], numbers[2]))
}

/// Parses "major.minor.patch" and reports the components.
struct ParseScenario;

impl Scenario for ParseScenario {
    fn name(&self) -> &str {
        "parse"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let (major, minor, patch) = parse_version(input)?;
        println!("major={major} minor={minor} patch={patch}");
        Ok(())
    }
}

/// Fails if the input version is below the minimum supported version.
struct SatisfiesMinimumScenario;

impl Scenario for SatisfiesMinimumScenario {
    fn name(&self) -> &str {
        "satisfies_minimum"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let version = parse_version(input)?;
        if version < MIN_VERSION {
            return Err(format!("'{input}' is below the minimum supported version 8.6.0"));
        }
        println!("'{input}' satisfies the minimum supported version 8.6.0");
        Ok(())
    }
}

fn main() -> ExitCode {
    let raw_arguments: Vec<String> = std::env::args().collect();

    let version_group = ScenarioGroupImpl::new(
        "version",
        vec![Box::new(ParseScenario), Box::new(SatisfiesMinimumScenario)],
        Vec::new(),
    );
    let root_group = ScenarioGroupImpl::new("root", Vec::new(), vec![Box::new(version_group)]);
    let test_context = TestContext::new(Box::new(root_group));

    match run_cli_app(&raw_arguments, &test_context) {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("{e}");
            ExitCode::FAILURE
        }
    }
}
