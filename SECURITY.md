# Security and privacy

By Jason Stys. Offline synthetic timing only. No host-clock changes, accounts, ads, telemetry, external sources, uploads, secrets or hardware control. The read-only loopback service is not intended for public hosting or hostile-local-client resource isolation.

Fixed native process paths, numeric/size/time envelopes, independent reference gates, static-file confinement, Host/Origin checks, restrictive CSP and escaped/text-only output reduce risk. Rust forbids unsafe code and checks release overflow; C++ validates before arithmetic and has sanitizer coverage. These are controls, not a universal security guarantee. Do not replace reviewed binaries or expose the service publicly.

Local SQLite/report files are unencrypted and not protected from users with OS file access. Content hashes detect changes but do not authenticate authorship or provide trusted timestamps. No automatic pruning/deletion/backups. Do not commit personal or operational traces.

Use [GitHub private vulnerability reporting](https://github.com/JasonStys/mission-clock-integrity-lab/security/advisories/new) if available, or contact [Jason Stys](https://github.com/JasonStys) with a non-sensitive description first. Public issues should contain only synthetic reproductions. Respect OS warnings on unsigned portable applications; never disable endpoint protection to run them.
