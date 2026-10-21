# Timing model and assumptions

Author: Jason Stys. All inputs are invented. The model is discrete deterministic phase-error bookkeeping, not a timing protocol or calibrated physical oscillator.

## Coordinates and units

`t` is an integer **elapsed simulation second**, starting at zero. Truth is `t × 1,000,000,000 ns`; a wall reading is truth plus phase error `x`. It is not UTC, TAI, TT, GPS time, the OS clock or a measured monotonic source. Frequency error in **ppb** contributes that integer number of nanoseconds per one-second tick. No float is needed; signed-64-bit native bounds and browser-safe integer limits are checked.

The simulator records 12 columns: elapsed second, node index, wall ns, phase-error ns, symmetric bound ns, reference age s, pending correction ns, accepted-reference flag, inside-envelope flag, qualified flag, backward-wall flag, mode (0 acquiring, 1 reference available, 2 holdover, 3 holdover expired, 4 synthetic envelope violation).

## Exact tick sequence

For each clock, observation at `t=0` occurs without elapsed drift. For every later tick:

1. Add its constant frequency error to phase. For node A at/after `fault_time`, also add the configured frequency change. At that exact tick add the configured phase jump once.
2. If slew policy is selected, take `adjustment = clamp(pending, −slew_rate, +slew_rate)`, subtract it from phase and pending. A reference acquired at this tick affects slew on the **next** tick, not retroactively.
3. A synthetic reference opportunity occurs when `t mod period = 0`, outside the half-open blackout `[gap_start, gap_end)`. Accept it only when the configured round-trip delay is **≤** the gate.
4. The invented phase measurement is `phase + path_bias`. Step policy subtracts that immediately. Slew policy replaces pending correction with that measurement. Record this tick as the last accepted reference. There is no frequency estimator, jitter filter or NTP discipline loop.
5. Age is elapsed seconds since last accepted reference; if none exists it is `t`.
6. After an accepted reference exists, assumed bound is `floor(delay_ns/2) + 1,000 ns + age × tolerance_ppb + abs(pending)` for slew, omitting pending for step. Before acquisition, it is the explicit fictional 5-second initial bound plus age-growth and pending. Path-bias magnitude must be ≤ half the path delay; the 1,000 ns term is an invented reference allowance, not measured NIST uncertainty.
7. Compare known simulated phase with the bound. Qualification requires a previous accepted reference, age **≤** holdover limit, and phase within the bound. Missing/expired/invalid evidence cannot establish a qualified event order.

Mode prioritizes never acquired, known envelope violation, holdover expiry, unavailable/overdue reference, then reference available. A backward reading means this one-second sample's wall value is strictly less than the previous sample on that source; equality is not counted. Slew does not guarantee monotonic time under an externally imposed negative phase jump or arbitrary unsupported physics. It removes the demonstrated backward correction in the provided positive-jump case.

**Truth-based qualification is simulation instrumentation.** A real device generally cannot know its true offset to flag an invalid bound this way. This application must not be represented as detecting real clock compromise or certifying operational timestamp accuracy.

## Event observations and ordering

Take each node's samples at `t mod 30 = 0`, retaining node-major baseline batch-arrival order. Event IDs are assigned before any reordering. The reordered case reverses that input list; it does not change source sequence, phase or physical model. These are fictional batch arrivals; there is no modeled transport latency or arrival timestamp.

Each event is `[id, stream, source_second, wall_ns, bound_ns, qualified]`. Source seconds act as sequence IDs in this bounded experiment; they are not inferred from wall time. No reboot/sequence-wrap scenario is modeled.

For closed intervals A=`[wallA−boundA, wallA+boundA]`, B analogously:

- Code 0: both qualified and `upperA < lowerB` (A strictly before B).
- Code 1: both qualified and `upperB < lowerA` (B strictly before A).
- Code 2: both qualified but overlap/touch (ambiguous).
- Code 3: either unqualified (no supported order claim).

Strict temporal ordering does **not** establish a causal relation. No vector clock, happens-before graph, message dependency or linear extension is claimed. The Rust worker separately counts adjacent source-sequence decreases in arrival order, then sorts by `(stream, sequence)` to identify backward wall readings in that event subset. The C++ one-second stream is denser and can reveal a correction absent from the 30-second event subset.

Every pair is retained in full JSON. The UI table shows only the first 18 arrivals with an explicit notice, but the pair selector and exported event audit retain all observations. A pairwise O(E²) audit is intentional and bounded to 96 events (4,560 pairs). No ambiguous pair is silently converted to a total ordering.

## Verification versus physical validity

Python evolves clocks tick-first rather than C++'s node-first loop and independently compares intervals. Exact integer equality is required before publishing a report. An additional truth check rejects a supposedly definite pair that contradicts the supplied synthetic source seconds. Analytical fixtures check known drift, closed endpoints, path bias and corrections. Common specifications and shared input assumptions remain possible common-mode errors. Passing these software checks establishes neither physical accuracy nor a real-world probability of timing failure.

There is no random oscillator noise, aging model, temperature sensitivity, calibration, reference authentication, reference-selection consensus, network packet exchange, leap second, relativistic correction or qualified hardware observation. A deterministic bound is not a confidence interval or Allan-deviation estimate.

## Research/provenance

The design separates phase error from frequency error and reference loss from holdover, informed by primary documentation:

- [NIST holdover glossary](https://csrc.nist.gov/glossary/term/holdover): terminology for a clock continuing with its local oscillator after loss of its controlling reference.
- [RFC 5905](https://www.rfc-editor.org/rfc/rfc5905.html), definitions and performance model: distinct offset, frequency, delay and growing error/dispersion concepts. This project uses its own simplified equations and numeric protocol; it neither copies the RFC skeleton nor claims NTP conformance.
- [How UTC(NIST) works](https://www.nist.gov/pml/time-and-frequency-division/time-services/utcnist-time-scale/how-utcnist-works): real time realization/stability and calibration involve much more than these fictional deterministic examples.

No external dataset or measured mission telemetry is bundled or fetched. All fixture identities are synthetic. No agency/provider endorsement is implied.
