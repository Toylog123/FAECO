# Manuscript Layout Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-typeset the Chinese FAECO manuscript so that the two-column page rhythm, front matter, figures, tables, appendix, and references are visually coherent without changing scientific content.

**Architecture:** Keep the existing A4 two-column XeLaTeX document and fonts. Make layout changes in the manuscript source through consistent float policies, controlled full-width figure/table blocks, tighter front-matter spacing, and explicit section/reference boundaries. Validate the result by compiling and rendering every PDF page, then iterate on any visible defects.

**Tech Stack:** XeLaTeX/latexmk, ctexart, graphicx, caption, booktabs, PDF/Poppler rendering, local visual inspection.

---

### Task 1: Establish the layout controls

**Files:**
- Modify: `D:/BaiduSyncdisk/03_FAECO/paper/zh/manuscript/faeco_paper_jcad.tex` preamble and front matter

- [ ] Add only the float/spacing packages needed for controlled placement and barriers.
- [ ] Normalize page geometry, column separation, section spacing, caption size, and front-matter vertical spacing while preserving the existing fonts and paper size.
- [ ] Keep the title, abstract, keywords, DOI, data, and conclusions unchanged.

### Task 2: Reorganize manuscript floats

**Files:**
- Modify: `D:/BaiduSyncdisk/03_FAECO/paper/zh/manuscript/faeco_paper_jcad.tex` figure/table/algorithm environments

- [ ] Group method overview visuals and prevent Figure 1 from creating a blank column beside Algorithm 1.
- [ ] Use full-width placement only where it materially improves readability; keep small local evidence beside the text that explains it.
- [ ] Reorder or barrier figures/tables so that the physical-validation block follows the experiment narrative and does not form a page-9 patchwork.
- [ ] Make appendix and bibliography transitions explicit so references do not begin beside unfinished appendix content.

### Task 3: Compile and run structural checks

**Files:**
- Generate/update: `D:/BaiduSyncdisk/03_FAECO/paper/zh/manuscript/faeco_paper_jcad.pdf` and normal LaTeX auxiliaries

- [ ] Run `latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error faeco_paper_jcad.tex` from the manuscript directory.
- [ ] Verify there are no fatal errors, overfull boxes, undefined references, or missing figures.
- [ ] Check page count, paper size, and extracted text presence.

### Task 4: Render and visually audit every page

**Files:**
- Create: `D:/BaiduSyncdisk/03_FAECO/paper/zh/manuscript/_review_pages_layout_20260811/`
- Create: `D:/BaiduSyncdisk/03_FAECO/paper/zh/manuscript/layout_audit_round7_20260811.md`

- [ ] Render all PDF pages to PNG at a reviewable resolution.
- [ ] Inspect front matter, every section transition, every figure/table, appendix, and references.
- [ ] If any page still has a dominant blank area, clipped object, unreadable caption, or broken float sequence, patch the source and repeat compilation/rendering.
- [ ] Record final page count and residual layout risks in the audit report.
