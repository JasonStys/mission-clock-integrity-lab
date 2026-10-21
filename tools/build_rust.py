"""Build and lint the fixed dependency-free Rust worker by Jason Stys. Variables: docs/CODE_INDEX.md."""

import subprocess


def main() -> None:
    """Require exact pinned toolchain, locked local graph, formatting, all tests and clippy warnings."""
    for arguments in (
        ["fmt", "--check"],
        ["test", "--locked"],
        ["clippy", "--locked", "--all-targets", "--", "-D", "warnings"],
        ["build", "--release", "--locked"],
    ):
        command = ["cargo", arguments[0], "--manifest-path", "auditor/Cargo.toml", *arguments[1:]]
        subprocess.run(command, check=True, timeout=180)


if __name__ == "__main__":
    main()
