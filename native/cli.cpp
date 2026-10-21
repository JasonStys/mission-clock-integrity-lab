// Fixed numeric stdin protocol by Jason Stys; no filenames, shell or clock
// APIs. Index: docs/CODE_INDEX.md.
#include "core.hpp"
#include <charconv>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
// Parse canonical decimal integers, rejecting signs-plus, floats, overflows and
// trailing data.
clocklab::Int number(std::istringstream &stream) {
  std::string token;
  if (!(stream >> token) || token.size() > 20)
    throw std::invalid_argument("Expected integer");
  clocklab::Int value = 0;
  const auto result =
      std::from_chars(token.data(), token.data() + token.size(), value);
  if (result.ec != std::errc{} || result.ptr != token.data() + token.size() ||
      std::to_string(value) != token)
    throw std::invalid_argument("Expected canonical integer");
  return value;
}
// Bound the complete request before parsing; produce only deterministic numeric
// JSON records.
int main() {
  try {
    std::string text;
    char ch = 0;
    while (std::cin.get(ch)) {
      if (text.size() >= 4096)
        throw std::invalid_argument("Request too large");
      text += ch;
    }
    std::istringstream stream(text);
    std::string magic;
    stream >> magic;
    if (magic != "CLOCK1")
      throw std::invalid_argument("Unsupported protocol");
    clocklab::Config c;
    c.duration = number(stream);
    c.period = number(stream);
    c.holdover = number(stream);
    c.slew = number(stream);
    c.slew_rate = number(stream);
    c.max_delay = number(stream);
    c.gap_start = number(stream);
    c.gap_end = number(stream);
    c.fault_time = number(stream);
    c.jump = number(stream);
    c.drift_change = number(stream);
    const auto count = number(stream);
    if (count < 1 || count > 4)
      throw std::invalid_argument("Clock count");
    std::vector<clocklab::Node> nodes;
    for (clocklab::Int i = 0; i < count; ++i)
      nodes.push_back({number(stream), number(stream), number(stream),
                       number(stream), number(stream)});
    std::string extra;
    if (stream >> extra)
      throw std::invalid_argument("Trailing input");
    const auto samples = clocklab::simulate(c, nodes);
    std::cout << "[";
    bool first = true;
    for (const auto &s : samples) {
      if (!first)
        std::cout << ",";
      first = false;
      std::cout << "[" << s.second << "," << s.node << "," << s.wall << ","
                << s.offset << "," << s.bound << "," << s.age << ","
                << s.remaining << "," << s.accepted << "," << s.within << ","
                << s.trusted << "," << s.regression << "," << s.mode << "]";
    }
    std::cout << "]\n";
    return 0;
  } catch (const std::exception &) {
    std::cerr << "Invalid bounded clock request\n";
    return 2;
  }
}
