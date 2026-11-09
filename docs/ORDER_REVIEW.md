# Review qualified timestamp order

The partial-order panel lists minimal strict-order edges, dependency readiness frontiers and each qualified event's before/after/unordered relationships. An edge `E0 → E2` means E0's closed timestamp interval ends strictly before E2's starts. Touching intervals are unordered; unqualified evidence is excluded, not assigned a guessed position.

Minimal edges remove redundant transitive relationships while preserving every guaranteed path. Readiness frontiers are a presentation of dependencies, **not total-order ranks**: events in different frontiers can still be unordered when no edge/path connects them. The relationship detail is the definitive list. Arrival order, source-sequence disorder and backward wall steps retain their separate existing reports. Timestamp order never proves causality.

The same derived review is part of the content-hashed JSON/HTML, strict CLI input analysis and local history. Each edge is checked against its qualified closed bounds before release. Native C++ clock evolution and Rust pair audits still must match their independent Python references exactly. These clocks are fictional elapsed-time models; no host-clock changes, NTP/PTP exchanges, real mission timing or operational assurance is provided.
