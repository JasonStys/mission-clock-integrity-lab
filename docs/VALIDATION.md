# Verification evidence and strategy

Prepared by Jason Stys. Software verification is not physical clock calibration, UTC traceability or flight qualification.

## Executed local evidence

Windows x64; Python 3.14.6, Node 24.18.1, MSVC 19.51, pinned Rust 1.98.1:

| Check                                     | Executed result                                                                                                                      |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Python tests                              | 332 passed, warnings treated as errors                                                                                               |
| Combined Python statement/branch coverage | 98.14%; minimum gate 90%                                                                                                             |
| Finite UI space                           | All 216 experiments require exact C++/Python and Rust/Python agreement                                                               |
| Generated models                          | One Hypothesis test with 60 examples, not 60 separately counted pytest tests                                                         |
| C++                                       | Release warning-as-error build and analytical CTest passed; assertions remain active via explicit throws                             |
| Rust                                      | Three unit tests passed; rustfmt and clippy warnings-as-errors passed; dependency-free, unsafe forbidden, checked release arithmetic |
| TypeScript                                | Nine unit tests, strict type check and production build passed                                                                       |
| Dependency audits                         | Python hashed development graph and npm graph reported no known vulnerabilities at execution                                         |
| Numerical contracts                       | All six reviewed case summaries passed exact integer comparison                                                                      |

Browser results and final exact-commit hosted/release evidence are recorded after execution in release notes. Workflow definitions are not proof of completion. Three-browser checks cover actual native service results, steps/slew, acquisition rejection, interval overlap, reordered arrival, invalid envelopes, all exports, stale/error/hostile evidence, unique IDs, mobile keyboard use and axe. No failed check is called a pass.

The initial development benchmark measured approximately 70 ms median and 825 KB traced Python peak for 3 clocks ×241 ticks, 27 event observations and 351 pairs, including both native process launches and independent Python verification. This is not worker RSS, total application memory, a hard timing guarantee or a fair cross-machine comparison. The benchmark prints fresh timings but does not refresh reviewed numerical summaries without explicit `--write`.

All **27 browser checks** passed across Chromium, Firefox and WebKit, including the keyboard-scroll regression. Review also added a generation guard and delayed-response test: a completed old request cannot resurrect evidence after controls have changed. Rendering failures explicitly hide any partial evidence. Screenshot QA corrected a clipped final x-axis label without changing the analytical data.

## Analytical and boundary oracles

- Hand-derived 2,000 ppb drift over 120 seconds gives exactly 240,000 ns; its reference-delay/tolerance envelope is 1,241,000 ns.
- Path bias, capped pending correction, inclusive delay/holdover bounds, no accepted reference, backward steps and out-of-envelope disturbances are separated.
- Closed intervals with equal endpoints are ambiguous; negative times, unqualified inputs, reversed pairs and source-sequence regressions have literal known answers.
- Every native range is exercised independently by sending invalid wire requests, not only relying on Python's validation. Truncated, extra, floating, canonical-integer, overflow, duplicate, non-ASCII and oversized inputs fail without execution of arbitrary code.
- Maximum native profile exercises four clocks ×601 samples and 84 events. Reports require exact disjoint pair accounting and zero definite claims contradicting synthetic source seconds.
- JSON limits, duplicate keys, wrong types including booleans, custom-input replay, all exports, full-content identity, immutable/idempotent/full SQL history, explicit connection closure and create-only files are tested.
- Real HTTP checks exercise Host/Origin/Fetch Metadata, query limits, traversal/static confinement, no mutation, restrictive headers and private failure messages.

## Issues found and corrected

Initial harness-only failures were distinguished from application defects: locked Cargo initially lacked its generated lock, Visual Studio's SDK lookup needed ordinary host registry access, Python's sandbox temp path needed a task-owned directory, pytest required materialized parametrization collections/short IDs, and Unicode malformed-wire tests needed explicit UTF-8 bytes on Windows. No OS protection or parser gate was weakened. A unit-runner boundary was added so Vitest does not collect Playwright acceptance files. The status test now targets its unique element instead of matching both the result status and the slider's semantic output.

Browser axe found a real accessibility defect: the horizontally scrollable event table was not keyboard-focusable. The region now has a name and tabindex, with an explicit focus regression and unchanged accessibility gate. These findings did not justify suppressing warnings or ignoring browser failures.

The first hosted GCC coverage run measured **98.4% C++ core/CLI line coverage (121/123 lines)** and **74.7% branches (233/312)**. The native gate is line coverage ≥90%, not a falsely claimed 90% branch gate. Actual Clang ASan/UBSan analytical and 200-request checks passed. The first CodeQL analysis completed but reported a low-severity test-code import-consistency note; imports were made consistent and the exact candidate was revalidated rather than dismissing the finding.

The initial hosted browser job passed 26/27 checks but Linux WebKit timed out awaiting an attachment download. Links now explicitly declare HTML download intent (in addition to the server's attachment headers); the test asserts that attribute and logs each format, while retaining actual download-event and file-content checks. The release still requires the full three-engine job to pass; no engine or download check is skipped.

## Hosted checks, traceability and gaps

Validation defines four OS/Python model jobs, a three-browser job, three portable-native jobs, actual Clang ASan/UBSan unit/200-request checks, and GCC native line coverage. The coverage job runs the real Python/native tests against instrumented C++ before requiring ≥90% C++ core/CLI line coverage. Rust tests/clippy run in every ordinary worker build. CodeQL analyzes C++, Python and JS/TS; open alerts are queried separately from successful analysis. Rust is checked by its own compiler/lints/tests, not falsely claimed analyzed by CodeQL.

| Requirement                                  | Primary evidence                                                                            |
| -------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Bounded deterministic clock evolution        | CTest, 216 combinations, 60 generated examples, independent Python oracle                   |
| Drift/blackout/steps/holdover interpretation | Analytic cases and actual scenario browser flows                                            |
| Honest interval ordering                     | Rust endpoint/sequence tests, Python oracle, synthetic truth gate                           |
| Safe boundaries and privacy                  | Native/schema malformed tests, HTTP/SQL/CLI integration and source review                   |
| Useful accessible instrument                 | Three-engine UI/exports/error/mobile/keyboard/axe tests plus visual inspection              |
| Reproducible delivery                        | Exact-SHA gates, native bundles/notices, checksum/API/CRC checks, downloaded-app acceptance |

Limits: no physical calibration/mission ground truth; no UTC/leap-second conversion; no NTP/PTP protocol/security conformance; no stochastic/relativistic noise; no reboot/wrap model; no real device control; no causality inference; no public multiuser service; no universal OS/signing guarantee. Shared specification errors can survive independently structured code. Passing security tools does not prove absence of vulnerabilities.
