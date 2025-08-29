use std::fmt;
use tracing_subscriber::fmt::format::Writer;
use tracing_subscriber::fmt::time::FormatTime;

/// Timestamp provider using monotonic clock.
pub struct MonotonicClock {
    start: std::time::Instant,
}

impl MonotonicClock {
    pub fn new() -> Self {
        Self {
            start: std::time::Instant::now(),
        }
    }
}

impl FormatTime for MonotonicClock {
    fn format_time(&self, w: &mut Writer<'_>) -> fmt::Result {
        let elapsed = std::time::Instant::now() - self.start;
        write!(w, "{}", elapsed.as_micros())
    }
}
