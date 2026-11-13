"""Run the current complete suite with the documented same-byte Yosys mirror."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot():
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / "code").rglob("*.py"))
            if "__pycache__" not in p.parts}


if __name__ == "__main__":
    receipt = ROOT / "scratch/packaged_yosys/receipt.json"
    for row in json.loads(receipt.read_text())["files"]:
        if sha(Path(row["source"])) != row["source_sha256"] or sha(Path(row["destination"])) != row["destination_sha256"]:
            raise ValueError("Yosys mirror differs from its original installation")
    before = snapshot()
    env = dict(os.environ)
    env["PATH"] = str(receipt.parent / "bin") + os.pathsep + "C:/Program Files/Git/bin" + os.pathsep + env["PATH"]
    command = [sys.executable, "-m", "pytest", "-q", "code/tests"]
    start = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, env=env, timeout=540)
    unchanged = before == snapshot()
    data = {"command": command, "timeout_s": 540, "returncode": result.returncode,
            "elapsed_s": time.monotonic() - start, "code_sha256": before,
            "code_unchanged": unchanged, "mirror_receipt_sha256": sha(receipt),
            "mirror_path": str(receipt.parent), "runner_sha256": sha(Path(__file__))}
    (HERE / "REGRESSION_RECEIPT.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf8", newline="\n")
    raise SystemExit(result.returncode if unchanged else 1)
