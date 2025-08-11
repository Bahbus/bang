"""Generate the SHA256 checksum for ``bang.msi``.

This script computes the checksum for ``dist/bang.msi`` and writes it to
``dist/SHA256SUMS``. The output file is overwritten and contains a single line in
the form ``<hash>  bang.msi``.
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
    """Write ``dist/SHA256SUMS`` for ``bang.msi`` only."""
    dist_dir = Path("dist")
    msi_path = dist_dir / "bang.msi"
    if not msi_path.is_file():
        msg = "dist/bang.msi not found"
        raise FileNotFoundError(msg)

    entry = f"{compute_sha256(msi_path)}  {msi_path.name}"
    if entry.count("  ") != 1 or "\n" in entry:
        msg = f"Malformed checksum entry: {entry!r}"
        raise ValueError(msg)

    sums_path = dist_dir / "SHA256SUMS"
    with sums_path.open("w", newline="\n") as handle:
        handle.write(f"{entry}\n")


if __name__ == "__main__":
    main()
