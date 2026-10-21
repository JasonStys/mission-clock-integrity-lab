# Inputs, reports and local API

Maintained by Jason Stys. All coordinates are elapsed synthetic seconds/nanoseconds, never measured UTC.

## Finite browser controls

`scenario`: nominal, reference-loss (default), asymmetric-path, clock-step, oscillator-fault, arrival-disorder. `policy`: 0 step (default), 1 slew. `tolerance`: 1 (default), 2, 4 multipliers of 2,500 ppb. `gate`: 1,000,000; 5,000,000 (default); 50,000,000 ns. `duration`: 240 (default), 600 s. Their Cartesian product is 216 experiments.

- `GET /api/health`: local mode/status.
- `GET /api/catalog`: exact finite cases, choices and defaults.
- `GET /api/run?...`: full verified report JSON. No `format` accepted.
- `GET /api/report?...&format=json|input|csv|html`: fixed-name download for those same accepted controls.
- `/` and exact `/assets/<built-file>` serve only built assets. Other paths are not filesystem access.

Host must be exactly `127.0.0.1:<port>`; Origin absent or that same HTTP origin. Cross-site Fetch Metadata is forbidden. URI ≤1,024 chars, ≤8 query fields, no unknown/duplicate keys. Invalid options: 400; forbidden origins: 403; paths: 404; mutations: 405; excessive target: 414; failed local resources/verification: generic 500. No auth/rate-limit identity or public hosting is implemented; the service is read-only loopback, not an Internet API. Do not expose it with a tunnel.

## Explicit custom JSON

See `examples/blackout.json`. Exact root fields: `schema` integer 1; `name` 1–48 lowercase ASCII alphanumeric/hyphen characters; `config`; `nodes`; `reverse_arrival` boolean. No additional or duplicate fields. Input is read at most 16 KiB; malformed/nested/excessive data rejects without coercing strings, floats or booleans to integer parameters.

| Config field       | Inclusive integer range       | Meaning                                                        |
| ------------------ | ----------------------------- | -------------------------------------------------------------- |
| duration           | 1..600                        | last observation second; includes t=0                          |
| period             | 1..60                         | synthetic reference opportunity spacing, seconds               |
| holdover           | 1..600                        | maximum qualified reference age, seconds                       |
| slew               | 0..1                          | immediate step or capped pending phase correction              |
| slew_rate          | 1..1,000,000                  | maximum correction nanoseconds per tick                        |
| max_delay          | 0..100,000,000                | maximum accepted round-trip delay, ns                          |
| gap_start, gap_end | 0..601, end≥start             | half-open reference blackout                                   |
| fault_time         | 1..601                        | node A disturbance starts here; 601 is outside the maximum run |
| jump               | −5,000,000,000..5,000,000,000 | one-time node A phase jump, ns                                 |
| drift_change       | −10,000,000..10,000,000       | extra node A ns/s at/after fault                               |

`nodes` is 1..4 rows, each exactly `[initial_phase_ns, drift_ppb, tolerance_ppb, round_trip_ns, path_bias_ns]`. Ranges: initial ±5,000,000,000; drift ±1,000,000; tolerance 0..10,000,000; delay 0..100,000,000; bias ±50,000,000 and magnitude ≤ floor(delay/2). A deliberately invalid tolerance can make truth fall outside its assumed envelope; the report labels it rather than certifying it.

Custom input overrides the preset configuration completely. Its report `settings` is null and its supplied input is preserved; preset UI settings are not falsely attached. Config names never select executables or code. Exports create new files only. History is explicit, unencrypted, capped at 100 distinct identities, with no automatic retention operation.

## Native and report contracts

`CLOCK1`, eleven config integers in table order, node count, five integers per node. Whitespace-delimited canonical decimal integers: no `+`, leading zeros, floats, overflow, missing or trailing tokens. C++ independently repeats bounds before products/absolute values. Its JSON is rows of the twelve columns documented in MODEL.

`EVENTS1`, count 1..96, then six integers per event: ID 0..95, stream 0..3, source sequence 0..600, wall ns ±9×10¹², bound 0..2×10¹⁰, qualified flag 0/1. Unique event IDs and `(stream, sequence)` pairs; ASCII and canonical decimals only. Rust output has every `[left_id,right_id,relation_code]` pair in input-pair order, adjacent arrival disorder count, and source-ordered regression ID pairs. No host/network APIs or arbitrary data formats.

Report schema 1 preserves input, settings, units/column labels, samples, events, complete audit, summary and method limitations. Canonical JSON sorts keys, uses compact separators/ASCII escaping, rejects nonfinite values and hashes the entire report excluding `id`. It is not a signature or trusted time-stamp. CSV preserves every sample including mode/quality flags; JSON retains all pair relations; HTML escapes full JSON and contains no scripts. Input JSON allows exact replay under the same model version, not arbitrary physical-model interoperability.
