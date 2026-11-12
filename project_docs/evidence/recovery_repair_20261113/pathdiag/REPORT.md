# s382 propagated-clock critical-path diagnosis

Two bounded OpenSTA diagnostics read the copied CONTROL/RECOVERY_V2 final netlists and their own newly extracted SPEFs. The original propagated-clock setup is unchanged. Each run completed with rc0 in approximately 0.469 seconds; the outer wrapper completed in 5 seconds. There was no routing or source modification. `report_checks` help confirmed all requested options; setup top10 and hold top5 paths were reported. The existing unconnected tap-cell black-box warning remains.

## Measured aggregate changes

| Metric (ns) | CONTROL | RECOVERY_V2 | Recovery minus control |
|---|---:|---:|---:|
| Setup WNS | -0.8484588032153795 | -0.858430437844504 | -0.0099716346291245 |
| Hold WNS | 0.4636368511334865 | 0.46361825489782404 | -0.00001859623566246 |
| Setup TNS (9 digits) | -13.422542572 | -13.735190392 | -0.312647820 |

The worst endpoint moves from `DFF_11/_0_` to `DFF_16/_0_`. The latter's same-startpoint path is `DFF_20/_0_ -> _057_ -> _059_ -> _060_ -> _084_ -> DFF_16/_0_`, with no intersection with the 13 archived swaps. It worsens from -0.840638 to -0.858430 ns (17.792 ps). Data arrival increases 16.118 ps, required time decreases 1.674 ps. Launch-clock arrival increases only 0.526 ps and capture-clock arrival increases 0.138 ps; data delay measured after the launch-clock pin increases 15.592 ps. Numbers derived from path tables have six-decimal ns report precision.

## Load/slew evidence on the new worst path

All four listed nets have identical named pin connectivity and endpoint cell types across arms. Their wire capacitances nevertheless increase in the extracted SPEFs (`C_UNIT 1 PF`, `PIN_CAP NONE`).

| Driver | Net | CONTROL wire C (pF) | RECOVERY wire C (pF) | Stage delay change (ps) |
|---|---|---:|---:|---:|
| `_057_/X` | `_015_` | 0.00744248 | 0.00819139 | +2.203 |
| `_059_/Y` | `_017_` | 0.00160986 | 0.00173940 | +2.409 |
| `_060_/Y` | `_018_` | 0.00549392 | 0.00605640 | +3.472 |
| `_084_/Y` | `UC_19VD` | 0.00116579 | 0.00149502 | +7.969 |

`_084_` output slew increases 146.721 -> 154.859 ps. Its delay grows 202.595 -> 210.564 ps. Clock changes are much smaller than this data-chain change. The table's stage delays are STA report increments; this report does not separate intrinsic cell delay from incoming interconnect delay.

## Direct intersections with swaps

Only two of the ten endpoint paths intersect swaps: `DFF_18/_0_` crosses `_096_`, and `DFF_3/_0_` crosses `_079_/_081_` in CONTROL and `_054_/_079_/_081_` in RECOVERY_V2. Their endpoint slacks worsen 33.764 ps and 45.980 ps respectively. The selected path to DFF3 changes, so its endpoint difference is not a fixed-path arc comparison. The other eight reported endpoint paths cross no swapped instance; DFF20 improves by 4.539 ps.

At DFF18, downsized `_096_` (`nor4_2 -> nor4_1`) output slew grows 195.619 -> 245.251 ps and its report delay increases 255.451 -> 279.977 ps. Arrival increases 22.630 ps and required time falls 11.134 ps, while capture-clock change is +0.475 ps. This is direct evidence of a cell/load/slew interaction; it does not isolate sizing from rerouting.

## Interpretation and limits

Measured evidence identifies data-path load/slew/delay changes as the dominant new-worst-path loss, with changed wire capacitance on unchanged logical connections. This supports a rerouting/parasitic mechanism beyond the swapped cells themselves. It does not prove one particular swap caused that rerouting, or isolate resistance versus capacitance: no crossed-netlist/SPEF or frozen-placement counterfactual was run. Top10 endpoint paths are a diagnostic subset, not all paths. TNS remains a full report quantity. No scientific acceptance or functional-equivalence gate is closed by this diagnosis.

Raw Tcl/logs, SHA-bound input manifest, parsed paths (`analysis.json`) and named-net SPEF comparisons (`spef_pathnets.json`) accompany this report. The `run_diag.py` file records the executed scratch workflow; use the archived Tcl files directly to reproduce each diagnostic against the copied inputs.
