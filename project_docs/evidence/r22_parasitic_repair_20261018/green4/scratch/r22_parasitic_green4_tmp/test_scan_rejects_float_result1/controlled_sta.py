from pathlib import Path
import sys
diagnostic='Warning 1647: baseline.spef line 310, pin u0:SLEEP not found.'
if diagnostic: print(diagnostic, file=sys.stderr)
physical=False
for line in Path(sys.argv[-1]).read_text().splitlines():
 if line.startswith('read_spef '): physical=True
 value=-0.9 if physical else -0.1
 if line.startswith('report_checks '): print(f'{value:.2f} slack (VIOLATED)')
 elif line.startswith('report_worst_slack -max'): print(f'worst slack max {value:.2f}')
 elif line.startswith('report_worst_slack -min'): print('worst slack min 0.20')
 elif line=='report_tns': print(f'tns max {value:.2f}')
sys.exit(0)
