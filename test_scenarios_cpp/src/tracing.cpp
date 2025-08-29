#include "tracing.hpp"

#include <iostream>
#include <sstream>
#include <thread>

#include "string_utils.hpp"

using namespace tracing;

namespace {

std::string minify_json(const std::string& input) {
    bool in_str = false;
    std::stringstream ss;
    for (auto it = input.begin(); it != input.end(); ++it) {
        auto c{*it};
        if (c == '\n') {
            // Skip newlines.
        } else if (!in_str && (c == ' ' || c == '\t')) {
            // Skip whitespace outside of strings.
        } else if (c == '"' && (it == input.begin() || *(it - 1) != '\\')) {
            // Flip inside of string flag.
            in_str = !in_str;
            ss << c;
        } else {
            ss << c;
        }
    }
    return ss.str();
}

}  // namespace

std::string tracing::level_to_string(const Level& level) {
    switch (level) {
        case Level::Trace:
            return "TRACE";
        case Level::Debug:
            return "DEBUG";
        case Level::Info:
            return "INFO";
        case Level::Warn:
            return "WARN";
        case Level::Error:
            return "ERROR";
        default:
            throw std::runtime_error{"Invalid level"};
    }
}

Subscriber::Subscriber(Level max_level, bool thread_ids)
    : max_level_{max_level}, thread_ids_{thread_ids} {}

void Subscriber::handle_event(const std::optional<std::string>& target, const Level& level,
                              score::json::Object&& fields) const {
    using namespace score::json;

    // Drop handling if below max level.
    if (level < max_level_) {
        return;
    }

    Object event;

    // Add timestamp.
    event.emplace("timestamp", timer_.format_time());

    // Add level.
    event.emplace("level", level_to_string(level));

    // Add fields.
    event.emplace("fields", std::move(fields));

    // Add target.
    if (target.has_value()) {
        event.emplace("target", *target);
    }

    // Add thread id.
    if (thread_ids_) {
        auto thread_id{std::this_thread::get_id()};
        std::stringstream ss;
        ss << "ThreadId(" << thread_id << ")";
        event.emplace("threadId", ss.str());
    }

    // Make JSON string.
    JsonWriter writer;
    auto buffer_result{writer.ToBuffer(event)};
    if (!buffer_result) {
        throw std::runtime_error{"Failed to stringify JSON"};
    }

    // Minify JSON and add "\n".
    // "\n" + 'std::flush' is used instead of 'std::endl'.
    // This is to avoid message mangling in multithreaded scenarios.
    std::stringstream ss;
    ss << minify_json(*buffer_result) << "\n";

    // Print output.
    std::cout << ss.str() << std::flush;
}

const Subscriber& tracing::global_subscriber() {
    static std::unique_ptr<Subscriber> subscriber{nullptr};
    if (!subscriber) {
        const bool kThreadIds = true;
        subscriber = std::make_unique<Subscriber>(Level::Trace, kThreadIds);
    }
    return *subscriber;
}
