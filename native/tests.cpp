// Analytical clock-model contracts by Jason Stys; throws remain active in
// Release. Index: docs/CODE_INDEX.md.
#include "core.hpp"
#include <iostream>
#include <stdexcept>
// Explicit check instead of disabled NDEBUG assertions.
void require(bool okay) {
  if (!okay)
    throw std::runtime_error("Clock contract failed");
}
// Isolate drift, path asymmetry, backward steps, slew monotonicity and invalid
// input.
int main() {
  clocklab::Config c;
  c.duration = 120;
  c.gap_start = 1;
  c.gap_end = 121;
  auto result = clocklab::simulate(c, {{0, 2000, 2000, 2000000, 0}});
  require(result.at(120).offset == 240000 && result.at(120).bound == 1241000);
  result = clocklab::simulate(c, {{0, 0, 0, 2000000, 900000}});
  require(result.at(0).offset == -900000 && result.at(120).within);
  c.gap_start = 0;
  c.gap_end = 0;
  c.jump = 2000000000LL;
  result = clocklab::simulate(c, {{0, 0, 0, 2000000, 0}});
  require(result.at(90).regression && result.at(61).mode == 4);
  c.slew = 1;
  result = clocklab::simulate(c, {{0, 0, 0, 2000000, 0}});
  for (const auto &sample : result)
    require(!sample.regression);
  c.duration = 601;
  bool rejected = false;
  try {
    (void)clocklab::simulate(c, {{0, 0, 0, 0, 0}});
  } catch (const std::invalid_argument &) {
    rejected = true;
  }
  require(rejected);
  std::cout << "Analytical clock contracts passed\n";
}
