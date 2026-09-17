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

#include <cli.hpp>
#include <scenario.hpp>
#include <test_context.hpp>

#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

namespace {

constexpr int kMinMajor = 8;
constexpr int kMinMinor = 6;
constexpr int kMinPatch = 0;

std::tuple<int, int, int> parse_version(const std::string& input) {
    int major = 0;
    int minor = 0;
    int patch = 0;
    char dot1 = 0;
    char dot2 = 0;
    std::istringstream iss{input};
    iss >> major >> dot1 >> minor >> dot2 >> patch;
    if (iss.fail() || dot1 != '.' || dot2 != '.' || !iss.eof()) {
        throw std::runtime_error{"'" + input + "' is not a valid major.minor.patch version"};
    }
    return {major, minor, patch};
}

// Parses "major.minor.patch" and reports the components.
class ParseScenario final : public Scenario {
   public:
    std::string name() const override { return "parse"; }

    void run(const std::string& input) const override {
        auto [major, minor, patch] = parse_version(input);
        std::cout << "major=" << major << " minor=" << minor << " patch=" << patch << std::endl;
    }
};

// Fails if the input version is below the minimum supported version.
class SatisfiesMinimumScenario final : public Scenario {
   public:
    std::string name() const override { return "satisfies_minimum"; }

    void run(const std::string& input) const override {
        const std::tuple<int, int, int> version{parse_version(input)};
        const std::tuple<int, int, int> minimum{kMinMajor, kMinMinor, kMinPatch};
        if (version < minimum) {
            throw std::runtime_error{"'" + input + "' is below the minimum supported version 8.6.0"};
        }
        std::cout << "'" << input << "' satisfies the minimum supported version 8.6.0" << std::endl;
    }
};

}  // namespace

int main(int argc, char* argv[]) {
    std::vector<std::string> raw_arguments{argv, argv + argc};

    ScenarioGroup::Ptr version_group{new ScenarioGroupImpl{
        "version",
        std::vector<Scenario::Ptr>{std::make_shared<ParseScenario>(),
                                    std::make_shared<SatisfiesMinimumScenario>()},
        std::vector<ScenarioGroup::Ptr>{}}};
    ScenarioGroup::Ptr root_group{new ScenarioGroupImpl{
        "root", std::vector<Scenario::Ptr>{}, std::vector<ScenarioGroup::Ptr>{version_group}}};
    TestContext test_context{root_group};

    try {
        run_cli_app(raw_arguments, test_context);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }
}
