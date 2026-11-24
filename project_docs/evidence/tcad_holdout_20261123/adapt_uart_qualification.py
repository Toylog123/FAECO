#!/usr/bin/env python3
"""Expose UART's hash-bound RVT library paths to the matched search runner."""

from argparse import ArgumentParser
from hashlib import file_digest
import json
from pathlib import Path


def binding(path):
    path = path.absolute()
    with path.open("rb") as stream:
        return {"path": str(path), "bytes": path.stat().st_size,
                "sha256": file_digest(stream, "sha256").hexdigest()}


def adapt(source):
    row = json.loads(source.read_bytes())
    if (row.get("top"), row.get("platform"), row.get("status")) != ("uart", "asap7", "hold_qualified"):
        raise ValueError("expected hold-qualified ASAP7 UART")
    if "library_paths" in row:
        raise ValueError("qualification already contains a library path table")
    groups = row["view_liberty_groups"]
    if set(groups) != {"FF", "TT", "SS"} or any(len(group) != 5 for group in groups.values()):
        raise ValueError("expected all three five-library RVT groups")
    for item in (ref for group in groups.values() for ref in group):
        if binding(Path(item["path"])) != item:
            raise ValueError(f"library no longer matches qualification: {item['path']}")
    row["library_paths"] = {corner: [item["path"] for item in group] for corner, group in groups.items()}
    row["adapted_qualification"] = {"source": binding(source), "producer": binding(Path(__file__))}
    return row


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    row = adapt(args.source)
    with args.destination.open("x", encoding="utf-8") as stream:
        json.dump(row, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
