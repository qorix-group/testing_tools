#include "monotonic_clock.hpp"

#include <sstream>

MonotonicClock::MonotonicClock() : start_{ClockT::now()} {}

std::string MonotonicClock::format_time() const {
    auto elapsed{ClockT::now() - start_};
    auto elapsed_us{std::chrono::duration_cast<std::chrono::microseconds>(elapsed)};
    return std::to_string(elapsed_us.count());
}
