"""Keep the cold preview upstream of detailed routing and electrical validation."""

import os
from pathlib import Path
import unittest

if not os.environ.get("FAECO_AES_BEFORE_COLD_PREVIEW"):
    from run_aes_cold_online import diagnostic_tcl


class ColdDiagnosticTclTest(unittest.TestCase):
    def test_routed_control_is_swapped_and_direct_wires_cleared_before_drc_only(self):
        prefix = ('read_db control.odb\n$inst swapMaster $target\n'
                  'odb::dbWire_destroy $wire\nputs "IBEX_CLEARED_SIGNAL_WIRES $cleared"\n')
        route = prefix + 'detailed_route\nextract_parasitics\nwrite_db candidate.odb\nexit\n'
        if os.environ.get("FAECO_AES_BEFORE_COLD_PREVIEW"):
            probe = route
        else:
            probe = diagnostic_tcl(route, Path('/tmp/live/full_drc.rpt'))
        self.assertEqual(probe.splitlines()[:4], prefix.splitlines())
        self.assertNotIn('detailed_route', probe)
        self.assertNotIn('extract_parasitics', probe)
        self.assertNotIn('write_db', probe)
        self.assertIn('drt::check_drc -output_file "/tmp/live/full_drc.rpt"', probe)
        self.assertTrue(probe.endswith('exit\n'))

    def test_missing_clear_phase_cannot_accidentally_launch_full_route(self):
        with self.assertRaisesRegex(ValueError, 'direct wire'):
            if not os.environ.get("FAECO_AES_BEFORE_COLD_PREVIEW"):
                diagnostic_tcl('detailed_route\nexit\n', Path('/tmp/live/full_drc.rpt'))


if __name__ == '__main__':
    unittest.main()
