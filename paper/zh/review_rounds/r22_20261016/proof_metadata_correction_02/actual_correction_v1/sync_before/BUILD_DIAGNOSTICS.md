# English draft build and verification

Rebuilt and checked on 16 October 2026 after correcting clock-period metadata. The English manuscript is a complete reviewable draft, with author inputs and journal-specific requirements pending.

The source is `../manuscript/FAECO.tex`; the compiled output is `../build/FAECO.pdf`. It contains the full Introduction, Related work, Method, experimental results and Conclusion, with 14 tables, seven English vector figures and all 14 source references. The numerical result set is r21. Later factual corrections include the actual PicoRV32 periods (core 5 ns, multiplier 2 ns, register bank 0.5 ns) and the distinction between 3363 B-family candidate evaluation records and 2994 independently traceable candidate STA results. This count does not certify the complete historical launch total. See `source_binding.json` for input hashes and evidence.

Compilation used LuaHBTeX 1.21.0, TeX Live 2025 and `elsarticle` 3.4c (2025/01/11), in preprint 12-point layout. Run twice from `paper/en/manuscript`:

```powershell
& 'C:\Program Files\Git\bin\bash.exe' -c 'bash ../../../code/scripts/run_with_timeout.sh 120 d:/APP/texlive/2025/bin/windows/lualatex.exe -interaction=nonstopmode -halt-on-error -output-directory=../build FAECO.tex'
```

The latest build exits successfully and produces 26 pages. The final log has zero overfull boxes, no undefined references/citations, no missing characters and no LaTeX/package warnings. Ten underfull-box diagnostics occur in narrow text columns and one retained reference; their rendered output was inspected. They are spacing diagnostics, not clipping. `build_metrics.json` records the final PDF checksum and diagnostics. An initial invocation passed through PowerShell split an unquoted native argument at `=`; the reproducible invocation above runs the fixed command inside Bash.

All 26 pages were rendered at 100 dpi using the locally available Poppler renderer and inspected in contact sheets, with detail checks on figures, equations, tables and the final section/declarations. The last layout change prevents remaining experimental floats from interrupting the Conclusion. No clipped content, overlapping table cells or missing glyphs were observed. Native figure previews were also examined separately panel by panel. Poppler emitted warnings about optional Bulgarian, Greek and Thai `nameToUnicode` resource paths under the local non-ASCII user directory; rendering still exited zero and produced all pages. These warnings did not alter the inspected English output.

`scripts/check_draft.py` passes: all nine experimental numeric table bodies match the Chinese source, bibliography content and keys are unchanged, every citation resolves, and the figure-4/5/6/7 numeric CSV rows and figure-5 count audit match the Chinese r21 outputs. It checks preservation and structure, not scientific validity or submission approval. Five highlights contain 75, 76, 64, 72 and 68 characters respectively. The retained source abstract has 251 whitespace-separated words; the Integration abstract limit remains unverified.

Figure preparation uses Python only. Seven PDF/SVG/600 dpi PNG sets, quantitative CSVs and the input SHA256 manifest are included. All seven exported figure PDFs pass the 5-point glyph audit; their smallest text runs are 7 points. The source preflight has zero failures and two reviewed warnings: TIFF is absent because the deliverable is editable vector artwork plus PNG previews, and a static width heuristic treats the literal `170/25.4` as inches although the actual exported PDF width is 170 mm. Journal-specific sizing/upload rules still need confirmation.

The official journal guide could not be retrieved; publisher-wide instructions are documented in `GUIDE_VERIFICATION.md`. The author, correspondence, funding, interests, contributions, data-access, exclusive-submission and AI-tool/version placeholders remain conspicuous. AI disclosure covers known research software, evidence audit and figure preparation as well as manuscript assistance. The manuscript has not been submitted. Current scientific evidence repair follows the r22 claim-to-evidence map.

The 16 October metadata correction preserves all 14 numerical table bodies and seven figure references. All 38 pages across the Chinese and English drafts were rendered, with detailed inspection of the changed setting and figure-4 caption pages. Exact receipts, prior PDFs and edit snapshots are retained in the r22 metadata-correction evidence package.
