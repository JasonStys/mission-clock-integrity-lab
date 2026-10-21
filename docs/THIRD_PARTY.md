# Third-party notices and provenance

Maintained by Jason Stys. Project source is MIT (`LICENSE`). All timing profiles are synthetic; no real satellite/clock telemetry or copied standards code is bundled. Primary research links are in MODEL, not implied endorsements.

Portable bundles contain CPython (PSF notice in `licenses/PYTHON.txt`), PyInstaller's GPL exception-enabled bootloader (actual distribution COPYING bundled), compiled Rust standard-library runtime (MIT/Apache notices in `licenses/RUST-MIT.txt` and `RUST-APACHE.txt`) and bundled Vite helper/runtime notices from the installed pinned distribution. Python has no third-party runtime packages; Rust auditor has no external crates. Development tools retain their own licenses and hash-locked dependency graph; they are not all runtime components.

Windows uses static Microsoft C++ runtime settings; distribution is subject to its toolchain redistribution terms. Linux PyInstaller may collect GCC runtimes: the actual runner's libstdc++/libgcc copyright files and GPL-3 text accompany collected libraries. macOS system libraries remain subject to platform terms. Inspect complete `_internal/licenses` after extracting the entire portable folder. A project MIT license does not relicense the compiler/runtime notices.

NIST/RFC documents inform terminology and the distinction between phase/frequency/holdover. No RFC skeleton/code components were copied, and no NTP/PTP, UTC, agency or mission certification is asserted.
