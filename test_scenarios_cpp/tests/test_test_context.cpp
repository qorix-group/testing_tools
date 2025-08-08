#include <gtest/gtest.h>

#include "common.hpp"
#include "scenario.hpp"
#include "test_context.hpp"

namespace {

ScenarioGroup::Ptr init_group() {
    Scenario::Ptr scenario_inner{new ScenarioStub{"inner_scenario"}};
    std::vector<Scenario::Ptr> scenarios_inner{scenario_inner};
    std::vector<ScenarioGroup::Ptr> groups_inner;
    ScenarioGroup::Ptr group_inner{
        new ScenarioGroupImpl{"inner_group", scenarios_inner, groups_inner}};

    Scenario::Ptr scenario_outer{new ScenarioStub{"outer_scenario"}};
    std::vector<Scenario::Ptr> scenarios_outer{scenario_outer};
    std::vector<ScenarioGroup::Ptr> groups_outer{group_inner};
    ScenarioGroup::Ptr group_outer{
        new ScenarioGroupImpl{"outer_group", scenarios_outer, groups_outer}};

    return group_outer;
}

}  // namespace

TEST(test_context, run_none_input_err) {
    auto root_group{init_group()};
    TestContext context{root_group};
    SHOULD_THROW_RE(context.run("inner_group.inner_scenario", {}), "Missing input");
}

TEST(test_context, run_some_input_ok) {
    auto root_group{init_group()};
    TestContext context{root_group};
    context.run("inner_group.inner_scenario", {"ok"});
}

TEST(test_context, run_some_input_err) {
    auto root_group{init_group()};
    TestContext context{root_group};
    SHOULD_THROW_RE(context.run("inner_group.inner_scenario", {"error"}), "Requested error");
}

TEST(test_context, run_not_found) {
    auto root_group{init_group()};
    TestContext context{root_group};
    SHOULD_THROW_RE(context.run("some_scenario", {}), "Scenario some_scenario not found");
}

TEST(test_context, list_scenarios_ok) {
    auto root_group{init_group()};
    TestContext context{root_group};
    auto result{context.list_scenarios()};

    ASSERT_EQ(result.size(), 2);
    ASSERT_EQ(result[0], "inner_group.inner_scenario");
    ASSERT_EQ(result[1], "outer_scenario");
}

TEST(test_context, list_scenarios_empty) {
    std::vector<Scenario::Ptr> scenarios;
    std::vector<ScenarioGroup::Ptr> groups;
    ScenarioGroup::Ptr root_group{new ScenarioGroupImpl{"root", scenarios, groups}};
    TestContext context{root_group};
    auto result{context.list_scenarios()};

    ASSERT_EQ(result.size(), 0);
}

#undef SHOULD_THROW_RE
#undef SHOULD_THROW
