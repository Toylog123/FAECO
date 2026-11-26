"""Exercise the archived TCAD SEC launcher under the physical runner's deadline."""

import json
import os
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import time
import unittest


EVIDENCE = Path(__file__).resolve().parents[2] / "project_docs/evidence/tcad_ibex_20261123"
TIMED_RUNNER = EVIDENCE.parent / "tcad_wallclock_schedule_20261125"


@unittest.skipUnless(sys.platform == "linux" and shutil.which("timeout"), "requires Linux GNU timeout")
class SecProcessGroupTest(unittest.TestCase):
    def test_cutoff_stops_tool_as_well_as_wrapper(self):
        sys.path.insert(0, str(TIMED_RUNNER))
        try:
            from raw_timed_process import run_process
        finally:
            sys.path.remove(str(TIMED_RUNNER))

        with TemporaryDirectory() as work:
            root = Path(work)
            started, finished = root / "started", root / "finished"
            fake = root / "mock_yosys"
            fake.write_text(
                f"#!{sys.executable}\n"
                "import os, time\n"
                "from pathlib import Path\n"
                f"Path({str(started)!r}).write_text(str(os.getpgrp()))\n"
                "time.sleep(1.8)\n"
                f"Path({str(finished)!r}).touch()\n",
                encoding="utf-8",
            )
            fake.chmod(0o700)
            launcher = root / "sec_launcher.py"
            launcher.write_text(
                "import os, sys\n"
                "from pathlib import Path\n"
                f"sys.path.insert(0, {str(EVIDENCE)!r})\n"
                "import prove_ibex\n"
                f"Path({str(root / 'wrapper_group')!r}).write_text(str(os.getpgrp()))\n"
                f"prove_ibex.YOSYS = Path({str(fake)!r})\n"
                "raise SystemExit(prove_ibex.main())\n",
                encoding="utf-8",
            )
            design, liberty = root / "design.v", root / "model.lib"
            design.write_text("module ibex_core; endmodule\n", encoding="utf-8")
            liberty.write_text("library(dummy) {}\n", encoding="utf-8")
            result = run_process(
                [sys.executable, "-B", str(launcher), str(design), str(design), str(root / "sec")],
                root / "wrapper.log", 0.8,
                env=os.environ | {"FAECO_SEC_LIBRARIES": json.dumps([str(liberty)])},
            )
            self.assertIsNone(result.returncode)
            self.assertTrue(started.is_file(), "test did not reach the proof subprocess")
            time.sleep(1.9)
            self.assertFalse(finished.exists(), "proof subprocess outlived its wall cutoff")
            self.assertEqual(started.read_bytes(), (root / "wrapper_group").read_bytes())
            self.assertFalse((root / "sec/receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
