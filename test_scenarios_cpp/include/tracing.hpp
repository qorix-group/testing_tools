#pragma once

/// Tracing.
/// This module is not a direct replacement to Rust `tracing` library.
/// It is able to display structured traces to stderr.

#include <any>
#include <string>

#include "monotonic_clock.hpp"
#include "score/json/json_writer.h"

#define _TRACING(target, level, fields...)                         \
    do {                                                           \
        tracing::global_subscriber().event(target, level, fields); \
    } while (false)

#define TRACING_TRACE(target, fields...) _TRACING({target}, tracing::Level::Trace, fields)
#define TRACING_DEBUG(target, fields...) _TRACING({target}, tracing::Level::Debug, fields)
#define TRACING_INFO(target, fields...) _TRACING({target}, tracing::Level::Info, fields)
#define TRACING_WARN(target, fields...) _TRACING({target}, tracing::Level::Warn, fields)
#define TRACING_ERROR(target, fields...) _TRACING({target}, tracing::Level::Error, fields)

#define TRACING_TRACE_WO_TARGET(fields...) _TRACING({}, tracing::Level::Trace, fields)
#define TRACING_DEBUG_WO_TARGET(fields...) _TRACING({}, tracing::Level::Debug, fields)
#define TRACING_INFO_WO_TARGET(fields...) _TRACING({}, tracing::Level::Info, fields)
#define TRACING_WARN_WO_TARGET(fields...) _TRACING({}, tracing::Level::Warn, fields)
#define TRACING_ERROR_WO_TARGET(fields...) _TRACING({}, tracing::Level::Error, fields)

namespace tracing {

enum class Level {
    Trace = 0,
    Debug = 1,
    Info = 2,
    Warn = 3,
    Error = 4,
};

std::string level_to_string(const Level& level);

class Subscriber {
   public:
    Subscriber(const Level& max_level, bool thread_ids);

    template <typename... T>
    void event(const std::optional<std::string>& target, const Level& level,
               std::pair<std::string, T>... fields) const {
        using namespace score::json;
        Object fields_object{object_create(fields...)};
        handle_event(target, level, std::move(fields_object));
    }

   private:
    Level max_level_;
    bool thread_ids_;
    MonotonicClock timer_;

    void handle_event(const std::optional<std::string>& target, const Level& level,
                      score::json::Object&& fields) const;

    score::json::Object object_create() const { return score::json::Object{}; }

    template <typename HeadT, typename... TailT>
    score::json::Object object_create(std::pair<std::string, HeadT> field,
                                      std::pair<std::string, TailT>... fields) const {
        auto object{object_create(fields...)};
        object.insert(field);
        return object;
    }
};

const Subscriber& global_subscriber();

}  // namespace tracing
