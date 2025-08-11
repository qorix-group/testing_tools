#include "scenario.hpp"

#include "string_utils.hpp"

Scenario::~Scenario() {}

ScenarioGroup::~ScenarioGroup() {}

ScenarioGroupImpl::ScenarioGroupImpl(const std::string& name,
                                     const std::vector<Scenario::Ptr>& scenarios,
                                     const std::vector<ScenarioGroup::Ptr>& groups)
    : name_{name}, scenarios_{scenarios}, groups_{groups} {}

ScenarioGroupImpl::~ScenarioGroupImpl() {}

std::string ScenarioGroupImpl::name() const { return name_; }

const std::vector<ScenarioGroup::Ptr>& ScenarioGroupImpl::groups() const { return groups_; }

const std::vector<Scenario::Ptr>& ScenarioGroupImpl::scenarios() const { return scenarios_; }

std::optional<Scenario::Ptr> ScenarioGroupImpl::find_scenario(const std::string& name) const {
    auto split{string_utils::split(name, ".")};
    if (split.size() == 1) {
        for (auto&& scenario : scenarios_) {
            if (scenario->name() == name) {
                return {scenario};
            }
        }
    } else {
        for (auto&& group : groups_) {
            if (group->name() == split[0]) {
                std::vector<std::string> parts{split.begin() + 1, split.end()};
                return group->find_scenario(string_utils::join(parts, "."));
            }
        }
    }

    return {};
}
