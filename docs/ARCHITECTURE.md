# Architecture and decisions

Author: Jason Stys. A bounded offline lab with verification before presentation.

```text
Finite browser controls / explicit local CLI JSON
  -> strict schema, types, unit ranges and size validation
  -> C++20 CLOCK1 worker -> integer samples
  -> independent Python model -> exact sample comparison
  -> 30-second event extraction -> Rust EVENTS1 interval audit
  -> independent Python order audit + synthetic truth check
  -> content-addressed evidence -> browser / JSON / CSV / inert HTML
Explicit CLI history option -> verified immutable SQLite record
```

| Decision                       | Benefit                                                                                | Boundary/trade-off                                                                       |
| ------------------------------ | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| C++ integer simulation         | Deterministic portable state evolution and controlled overflow envelope                | Fixed one-second step, not continuous oscillator physics                                 |
| Rust interval/sequence worker  | Bounded memory-safe parser, checked release arithmetic, no external crates/unsafe code | Process startup; pairwise audit intentionally O(E²)                                      |
| Python independent oracles     | Differently structured code checks every sample and relation                           | CPU duplication; cannot validate shared physical assumptions                             |
| TypeScript defensive Canvas UI | Typed bounded evidence and accessible numerical alternatives                           | Automation does not prove universal accessibility                                        |
| Read-only loopback server      | No remote input, account, uploads, clock-control API or telemetry                      | Not a multiuser/public production service or hostile-local-client quota system           |
| Optional SQLite                | Hash identity, idempotence and immutable-record triggers                               | Unencrypted; OS file owners can modify files externally; 100 records is not a byte quota |

## Trust boundaries and failure behavior

Only two allowlisted reviewed binaries are invoked, using argument arrays, fixed paths and bounded stdin—not a shell or user executable. Workers validate independently; startup/exit/parse/timeout/reference failures block evidence rather than falling back to a different unverified implementation. No HTTP option can select a file, command, executable, host or port. Both native programs lack clock/network control code. The CLI accepts only explicit local bounded JSON, never code.

HTTP binds IPv4 loopback, checks exact Host/Origin and cross-site Fetch Metadata, confines static paths including resolved symlinks, uses restrictive CSP, denies all mutation routes, emits no CORS and hides private exception details. There are no service accounts, passwords, ads, third-party scripts or collection endpoints. The UI renders data using text nodes; only its fixed owned template uses HTML. Old results disappear when controls change or verification fails. Closing a tab does not stop its server.

Each report includes the complete input and source/model interpretation. SHA-256 excludes only the `id` field; it detects content changes, not authorship or an authenticated timestamp. SQL uses bound parameters, a transaction and explicit connection closure. No automatic pruning, cleanup or background update exists.

## Bounds and complexity

N≤4 clocks, T≤601 observations per clock: C++ model time/storage O(NT), ≤2,404 rows. Python verification has the same bound. E≤84 from supported profile extraction; the standalone Rust contract permits ≤96 events. Pair comparisons O(E²), ≤4,560 records; BTree identity/sequence validation and source sorting O(E log E). Python follows the same pair bound. Serialization/charting is linear in displayed/stored rows or pairs. Each request launches two short-lived processes with a 10-second timeout and 2 MB accepted-output cap; those are not a hostile-worker isolation guarantee. Trusted workers construct bounded outputs before exit.

CLI JSON ≤16 KiB, native clock stdin ≤4,096 bytes, Rust stdin ≤65,536 bytes plus one rejection sentinel. Frequencies, periods, offsets and products are bounded before arithmetic; Rust additionally checks overflow in release builds. No workload-derived background cache grows over time. Browser summary values remain safe integers; display milliseconds are formatting only, not analytical rounding.

## Growth/non-goals

Real timing interfaces would require authorization, authenticated sources, calibration, physical error budgets and separate qualified review—not a new URL field. Larger traces need streaming storage and a scalable partial-order strategy rather than silently weakening pair semantics. Public hosting needs a different authentication, isolation, TLS and resource-control architecture. No hardware, missions, operational safety or adversarial time-source assurance is claimed.
