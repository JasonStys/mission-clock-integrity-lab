// Deterministic clock phase/holdover simulator by Jason Stys. Exact symbols:
// docs/CODE_INDEX.md.
#include "core.hpp"
#include <algorithm>
#include <cstdlib>
#include <stdexcept>
namespace clocklab {
// Enforce ranges before absolute values/products; even hostile CLI integers
// cannot trigger overflow.
void validate(const Config &c, const std::vector<Node> &nodes) {
  if (c.duration < 1 || c.duration > 600 || c.period < 1 || c.period > 60 ||
      c.holdover < 1 || c.holdover > 600 || c.slew < 0 || c.slew > 1 ||
      c.slew_rate < 1 || c.slew_rate > 1000000 || c.max_delay < 0 ||
      c.max_delay > 100000000 || c.gap_start < 0 || c.gap_start > 601 ||
      c.gap_end < c.gap_start || c.gap_end > 601 || c.fault_time < 1 ||
      c.fault_time > 601 || c.jump < -5000000000LL || c.jump > 5000000000LL ||
      c.drift_change < -10000000 || c.drift_change > 10000000 ||
      nodes.empty() || nodes.size() > 4)
    throw std::invalid_argument("Unsupported configuration");
  for (const auto &n : nodes) {
    if (n.initial < -5000000000LL || n.initial > 5000000000LL ||
        n.drift < -1000000 || n.drift > 1000000 || n.tolerance < 0 ||
        n.tolerance > 10000000 || n.delay < 0 || n.delay > 100000000 ||
        n.bias < -50000000 || n.bias > 50000000 ||
        std::abs(n.bias) > n.delay / 2)
      throw std::invalid_argument("Unsupported clock");
  }
}
// O(nodes*ticks) state evolution; a rate in ppb contributes exactly that many
// ns per one-second tick.
std::vector<Sample> simulate(const Config &c, const std::vector<Node> &nodes) {
  validate(c, nodes);
  std::vector<Sample> out;
  out.reserve(nodes.size() * static_cast<std::size_t>(c.duration + 1));
  for (std::size_t k = 0; k < nodes.size(); ++k) {
    const auto &n = nodes[k];
    Int offset = n.initial, remaining = 0, last = -1, previous = 0;
    for (Int t = 0; t <= c.duration; ++t) {
      if (t > 0) {
        offset +=
            n.drift + ((k == 0 && t >= c.fault_time) ? c.drift_change : 0);
        if (k == 0 && t == c.fault_time)
          offset += c.jump;
        if (c.slew) {
          const Int adjustment =
              std::clamp(remaining, -c.slew_rate, c.slew_rate);
          offset -= adjustment;
          remaining -= adjustment;
        }
      }
      const bool available = !(t >= c.gap_start && t < c.gap_end);
      const bool accepted =
          (t % c.period == 0 && available && n.delay <= c.max_delay);
      if (accepted) {
        const Int measurement = offset + n.bias;
        if (c.slew)
          remaining = measurement;
        else
          offset -= measurement;
        last = t;
      }
      const Int age = (last < 0) ? t : t - last;
      const Int bound = (last < 0 ? 5000000000LL : n.delay / 2 + 1000) +
                        age * n.tolerance + (c.slew ? std::abs(remaining) : 0);
      const bool within = std::abs(offset) <= bound;
      const bool trusted = last >= 0 && age <= c.holdover && within;
      const int mode =
          (last < 0)
              ? 0
              : (!within ? 4
                         : (age > c.holdover
                                ? 3
                                : (!available || age >= c.period ? 2 : 1)));
      const Int wall = t * 1000000000LL + offset;
      out.push_back({t, static_cast<Int>(k), wall, offset, bound, age,
                     remaining, accepted, within, trusted,
                     t > 0 && wall < previous, mode});
      previous = wall;
    }
  }
  return out;
}
} // namespace clocklab
