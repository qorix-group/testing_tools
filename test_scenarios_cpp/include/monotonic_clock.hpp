#pragma once

#include <chrono>
#include <string>

/// @brief Timestamp provider using monotonic clock.
class MonotonicClock {
   public:
    MonotonicClock();

    /// @brief Measure and write out the current time.
    /// @return Timestamp as string.
    std::string format_time() const;

   private:
    using ClockT = std::chrono::high_resolution_clock;
    using TimePointT = std::chrono::time_point<ClockT>;

    TimePointT start_;
};
