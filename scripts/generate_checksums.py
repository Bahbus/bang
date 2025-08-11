"""Generate SHA256 checksums for build artifacts.

This script scans the ``dist`` directory for files and writes their SHA256 hashes to
``dist/SHA256SUMS``. It should be executed after the build process creates the final
artifacts.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def compute_sha256(path: Path) -> str:
    """Return the SHA256 hash for ``path``."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8192), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    """Write ``SHA256SUMS`` for all files in ``dist``."""
    dist_dir = Path("dist")
    sums_path = dist_dir / "SHA256SUMS"

    with sums_path.open("w", newline="\n") as handle:
        for artifact in sorted(dist_dir.iterdir()):
            if artifact.name == "SHA256SUMS" or not artifact.is_file():
                continue
            entry = f"{compute_sha256(artifact)}  {artifact.name}"
            if entry.count("  ") != 1 or "\n" in entry:
                msg = f"Malformed checksum entry: {entry!r}"
                raise ValueError(msg)
            handle.write(f"{entry}\n")


if __name__ == "__main__":
    main()
