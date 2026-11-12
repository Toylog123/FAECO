"""Mirror pinned Windows Yosys with DLLs beside the executables.

Packaged Windows processes can ignore PATH for DLL lookup. Keep the installed
suite untouched and put the printed bin directory first on PATH for test runs.
The fixed dependency list was verified for OSS CAD Suite 2026-08-04, Yosys
0.67+146 (468ba27d9). This is an environment helper, not a toolchain upgrade.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


EXECUTABLES = ("yosys.exe", "yosys-abc.exe")
DLLS = (
    "libreadline8.dll", "libtermcap-0.dll", "libstdc++-6.dll",
    "libwinpthread-1.dll", "libgcc_s_seh-1.dll", "zlib1.dll",
    "tcl86.dll", "libffi-8.dll",
)


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def prepare(suite: Path, output: Path) -> Path:
    suite, output = suite.resolve(), output.resolve()
    if suite == output or suite in output.parents or output in suite.parents:
        raise ValueError("Source and output directories must not overlap")
    pairs = [(suite / "bin" / name, output / "bin" / name)
             for name in EXECUTABLES]
    pairs += [(suite / "lib" / name, output / "bin" / name) for name in DLLS]
    share = suite / "share" / "yosys"
    shared_files = sorted(path for path in share.rglob("*") if path.is_file())
    if not shared_files:
        raise ValueError(f"Missing or empty Yosys support directory: {share}")
    pairs += [(path, output / "share" / "yosys" / path.relative_to(share))
              for path in shared_files]

    # Preflight everything before copying: a collision never silently overwrites.
    records = []
    for source, destination in pairs:
        if not destination.resolve().is_relative_to(output):
            raise ValueError(f"Output path escapes through a link: {destination}")
        digest = sha256(source)
        if destination.exists() and sha256(destination) != digest:
            raise ValueError(f"Refusing mismatched existing file: {destination}")
        records.append({"source": str(source), "destination": str(destination),
                        "source_sha256": digest, "destination_sha256": digest})
    receipt = output / "receipt.json"
    if not receipt.resolve().is_relative_to(output):
        raise ValueError(f"Receipt escapes through a link: {receipt}")
    payload = (json.dumps({"suite": str(suite), "output": str(output),
                           "files": records}, indent=2) + "\n").encode("utf-8")
    if receipt.exists() and receipt.read_bytes() != payload:
        raise ValueError(f"Refusing mismatched existing receipt: {receipt}")

    for (source, destination), record in zip(pairs, records):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            with source.open("rb") as reader, destination.open("xb") as writer:
                shutil.copyfileobj(reader, writer)
        if sha256(destination) != record["source_sha256"]:
            raise ValueError(f"Copy verification failed: {destination}")
    if not receipt.exists():
        with receipt.open("xb") as stream:
            stream.write(payload)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path,
                        default=Path("C:/oss-cad-suite-build/oss-cad-suite"))
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parents[2]
                        / "scratch" / "packaged_yosys")
    args = parser.parse_args()
    try:
        receipt = prepare(args.suite, args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Preparation failed: {error}\n")
    print(f"Verified mirror; receipt: {receipt}")
    print(f"Prepend to PATH: {receipt.parent / 'bin'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
