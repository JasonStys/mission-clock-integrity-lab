# Release and local operations runbook

Maintained by Jason Stys. This ships an offline civilian education app, not a production timing service.

1. Inspect live Actions artifacts and available billing storage; distinguish accumulated usage and the separate cache allowance. Report limits. Fresh approval and verified private backups are required before any cleanup; no automatic deletion or retention changes.
2. Review model limits, inputs, scientific claims, security boundaries and notices. Run all README checks, native sanitizer/coverage jobs and actual browser QA. Fix causes rather than updating baselines or suppressing warnings.
3. Require all ten Validation jobs and all three CodeQL analyses on the exact reviewed main SHA. Query open CodeQL findings separately. Pending/account/infrastructure failures are not passes. Confirm clean source and current exact-line/file inventories.
4. Dispatch Portable release on main with a new digits.digits.digits version. Preparation checks successful exact-SHA Validation/CodeQL and creates a draft only. Three OS jobs build both native workers and production UI, freeze/smoke the real app, and upload ZIP/checksum pairs directly to the draft. No Actions artifacts/caches or automatic publication.
5. Download all six new draft assets into a new task-owned folder. Verify SHA-256 against both checksum files and GitHub asset metadata, ZIP CRCs/confinement, native/runtime notices and required workers/resources. Do not execute archived Actions evidence.
6. Run the freshly built reviewed downloaded Windows app, actual CLI custom input/history/exports, and all browser flows against its server. Keep private evidence outside Git. Record exact SHA, completed job links, test counts/coverage, audits, measured limits, ZIP digests and actual download tests in release notes.
7. Recheck main/tag/accepted runs, then publish the existing verified draft. Do not overwrite public assets silently. Confirm the public page and leave its download link available.

## Operation, teardown and rollback

The app binds only IPv4 loopback and never adjusts clocks or sends timing packets. Closing a tab does not stop its server. Ctrl+C in its console stops it; stop only owned preview/test processes and verify their ports. Do not kill broad process names, unrelated services or other labs. Source preview should be readiness-checked, visually inspected and captured without manipulating screenshots.

Failure of numerical, privacy, digest, native-runtime or key UI checks blocks release. Preserve evidence, correct source and produce a fresh version; do not silently replace existing public files. No background updater, automatic prune or migration touches user histories. Download bundles are unsigned/unnotarized; respect OS protections. Linux/macOS extraction may require executable permission. Cross-platform CI confirms its runner environment, not every OS distribution.

SQLite and user exports are unencrypted local data. Back them up privately and keep them out of issues/source/release uploads. Do not expose the loopback service via tunnels or treat a larger profile as authorized real timing infrastructure. New hardware/network capabilities need explicit scope, authorization and qualified engineering review.
