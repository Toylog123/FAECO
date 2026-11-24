# English manuscript

The active [IEEEtran working draft](manuscript/FAECO_postroute_recovery.tex) follows the Chinese post-route manuscript at `c8b9e0fd` and incorporates the subsequently verified ASAP7 UART search. The [eight-page PDF](build/FAECO_postroute_recovery_tcad_20261125.pdf) is the local preview.

| Result | Evidence |
| --- | --- |
| SKY130HD AES routing diagnosis × schedule and matched online greedy comparison | [Factorial](../../project_docs/evidence/tcad_ibex_20261123/AES_FACTORIAL_REPORT.md), [online greedy](../../project_docs/evidence/tcad_ibex_20261123/AES_ONLINE_GREEDY_REPORT.md) |
| Ten SKY130 endpoints aligned across timing views and s713/s832 joint searches | [Endpoint binding and joint searches](../../project_docs/evidence/sky130_joint_constraints_20261123/REPORT.md) |
| Historical nominal baselines, including sensitivity-ranked greedy | [Matched baseline data](../../project_docs/evidence/postroute_strong_baselines_20261122/) |
| ASAP7 Ibex and UART recovery, and the SKY130HD JPEG qualification result | [Ibex serial comparison](../../project_docs/evidence/tcad_ibex_20261123/ASAP7_SERIAL_REPORT.md), [UART reference qualification](../../project_docs/evidence/tcad_holdout_20261123/UART_CONTROL_RUN.md), [UART online comparison](../../project_docs/evidence/tcad_holdout_20261123/UART_ONLINE_REPORT.md), [JPEG qualification](../../project_docs/evidence/tcad_holdout_20261123/JPEG_CONTROL_REPORT.md) |

The draft reuses the six [ImageGen illustrations](../zh/figures/imagegen_20261123/) with their original labels and English captions. The relevant usage appears in Acknowledgments with the disclosure for AI-assisted prose.

For a local build, run pdfLaTeX twice from `paper/en/manuscript/` with a separate output directory. The English [change log](CHANGELOG.md) records the draft and its validation.

Other TeX files in `manuscript/` and the files under `submission/` document earlier manuscript lines. The existing `FAECO_postroute_recovery.pdf` copies predate the source revision.
