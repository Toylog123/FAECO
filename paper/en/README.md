# English manuscript

## V5 TCAD submission

Full English adaptation awaits author confirmation. The reviewed V5 Chinese manuscript supplies the current scientific text, embedded English title and abstract, five keywords, five figures and 26 references. The V5 evidence index records the frozen experimental inputs and the offline reproduction commands. [V5 Chinese manuscript](../zh/FAECO_v3_后布局可调预算面积回收.pdf) · [Internal review](../zh/review_rounds/r20261127_v5_tcad/REREVIEW_FINAL.md) · [Evidence index](../../project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md)

The final English PDF needs a separate check against the TCAD Regular Paper requirements. Use the IEEE two-column template with a minimum 10 pt font, a 100–250 word abstract and 4–8 index terms. The 14-page limit includes author photos and biographies on revision. Confirm the author order, affiliations, corresponding author and each author's ORCID with the authors. Also confirm the submission history, exclusivity and acknowledgment wording. The figure audit identifies Google Antigravity's `generate_image` as the tool that produced the schematic illustrations in Figures 1 and 2. The Chinese acknowledgment records how OpenAI Codex was used. Check that the final English acknowledgment names the tools and covers the material actually used in that version. [Figure provenance](../zh/figures/CHANGE_LOG.md) · [IEEE TCAD submission instructions](https://ieee-ceda.org/publications/tcad/tcad-paper-submissions)

## November 25 IEEEtran draft

The [November 25 working draft](manuscript/FAECO_postroute_recovery.tex) follows the Chinese post-route manuscript at `c8b9e0fd` and incorporates the subsequently verified ASAP7 UART search. Its [eight-page preview](build/FAECO_postroute_recovery_tcad_20261125.pdf) documents that revision.

| Result | Evidence |
| --- | --- |
| SKY130HD AES routing diagnosis × schedule and matched online greedy comparison | [Factorial](../../project_docs/evidence/tcad_ibex_20261123/AES_FACTORIAL_REPORT.md), [online greedy](../../project_docs/evidence/tcad_ibex_20261123/AES_ONLINE_GREEDY_REPORT.md) |
| Ten SKY130 endpoints aligned across timing views and s713/s832 joint searches | [Endpoint binding and joint searches](../../project_docs/evidence/sky130_joint_constraints_20261123/REPORT.md) |
| Historical nominal baselines, including sensitivity-ranked greedy | [Matched baseline data](../../project_docs/evidence/postroute_strong_baselines_20261122/) |
| ASAP7 Ibex and UART recovery, and the SKY130HD JPEG qualification result | [Ibex serial comparison](../../project_docs/evidence/tcad_ibex_20261123/ASAP7_SERIAL_REPORT.md), [UART reference qualification](../../project_docs/evidence/tcad_holdout_20261123/UART_CONTROL_RUN.md), [UART online comparison](../../project_docs/evidence/tcad_holdout_20261123/UART_ONLINE_REPORT.md), [JPEG qualification](../../project_docs/evidence/tcad_holdout_20261123/JPEG_CONTROL_REPORT.md) |

The draft reuses the six [ImageGen illustrations](../zh/figures/imagegen_20261123/) with their original labels and English captions. The relevant usage appears in Acknowledgments with the disclosure for AI-assisted prose.

For a local build, run pdfLaTeX twice from `paper/en/manuscript/` with a separate output directory. The English [change log](CHANGELOG.md) records the draft and its validation.

Other TeX files in `manuscript/` and the [October Integration submission package](submission/README.md) document earlier manuscript lines. The existing `FAECO_postroute_recovery.pdf` copies predate the November 25 source revision.
