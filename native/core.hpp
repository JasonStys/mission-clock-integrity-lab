// Integer simulated clock contracts by Jason Stys. Functions/fields:
// docs/CODE_INDEX.md.
#pragma once
#include <cstdint>
#include <vector>
namespace clocklab {
using Int = std::int64_t;
// Config contains elapsed seconds, ns/second frequency errors and bounded
// synthetic disturbances.
struct Config {
  Int duration = 240, period = 30, holdover = 120, slew = 0, slew_rate = 100000;
  Int max_delay = 5000000, gap_start = 60, gap_end = 181, fault_time = 61;
  Int jump = 0, drift_change = 0;
};
// Node holds initial phase ns, fractional frequency ppb (equal ns/s), tolerance
// ppb and path ns.
struct Node {
  Int initial, drift, tolerance, delay, bias;
};
// Sample records truth, wall time, bounded phase uncertainty and explicit
// qualification flags.
struct Sample {
  Int second, node, wall, offset, bound, age, remaining;
  bool accepted, within, trusted, regression;
  int mode;
};
// Validate before arithmetic/allocation; inputs are bounded so every
// intermediate fits signed 64-bit.
void validate(const Config &config, const std::vector<Node> &nodes);
// Advance fixed one-second ticks; corrections precede observations and never
// change host time.
std::vector<Sample> simulate(const Config &config,
                             const std::vector<Node> &nodes);
} // namespace clocklab
