# Integration author-guide verification

Checked on 14 October 2026. This file records preparation evidence, not submission clearance.

The journal-specific [Integration Guide for Authors](https://www.sciencedirect.com/journal/integration/publish/guide-for-authors) could not be retrieved through the browser tool. Searches restricted to the official ScienceDirect domain did not recover its current full text. The primary task also reported HTTP 403. No third-party template or another journal's instructions were adopted.

| Item | Status | Evidence and consequence |
|---|---|---|
| Journal-specific article types, word/page limits, abstract limit, keyword count, review anonymity, reference style and declarations | UNVERIFIED | Recheck the Integration Guide before submission. The present preprint layout is a working draft. |
| Elsevier LaTeX class | VERIFIED, publisher-wide | The official [LaTeX instructions](https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions) identify `elsarticle`; the local installation contains class version 3.4c dated 2025/01/11. Journal-specific formatting still takes precedence. |
| Highlights | VERIFIED, publisher-wide | The official [highlights instructions](https://www.elsevier.com/researcher/author/tools-and-resources/highlights) specify 3–5 bullets and at most 85 characters per bullet, including spaces. Their current page describes a Word document at the final-files stage. The attached five-bullet text is a draft; journal-specific timing remains unverified. |
| AI disclosure | VERIFIED, publisher-wide | The current [Elsevier AI policy](https://www.elsevier.com/en-gb/about/policies-and-standards/generative-ai-policies-for-journals) separates manuscript preparation from research-process use. Research assistance belongs in Methods; manuscript assistance needs a separate declaration. Tool-assisted explanatory figures need caption-level disclosure. Reproducible data plotting must preserve real observations. Exact tools, versions and human review remain author inputs. |
| Source references | PRESERVED, not journal-style approved | All 14 entries and keys from the Chinese master remain in `../references/references.tex`. The source's publication-type markers and punctuation have not been silently converted to an unverified journal style. |
| Authorship, correspondence, funding, competing interests, contributions and exclusive submission | AUTHOR INPUT REQUIRED | No signed declaration or negative funding/interest assertion has been invented. See `AUTHOR_INPUT_CHECKLIST.md`. |

Use `manuscript/FAECO.tex` and its compiled PDF for author review. This package has not been uploaded, submitted or sent to an editor.
