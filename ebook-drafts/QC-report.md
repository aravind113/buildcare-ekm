# QC report — Indian & Kerala Economy eBook (draft)

Build: 528 pages, A5, one PDF, embedded Unicode Malayalam fonts (Noto Sans Malayalam), clickable table of contents (38 links), continuous page numbers (cover unnumbered).

## Counts
- 20 chapters, 563 chapter MCQs (25–32 per chapter) + 10 model tests × 50 = 500 test MCQs. Total 1,063 MCQs, each with answer and explanation underneath.
- Answer-key spread over all 1,063: A 273, B 265, C 262, D 263 (Test 1 is slightly uneven: A 16, B 14, C 9, D 11).
- Glossary: 550 merged Malayalam–English terms. Abbreviations: 22. Formulas: 13.
- `[VERIFY]` flags: 114 lines (see `verify-checklist.md`).

## What was verified, and against what
Facts were checked only against documents you supplied:
- Union Budget 2026-27 (Budget at a Glance); RBI Annual Report 2025-26; Kerala Economic Review 2025 (Vol I, II); Kerala MTFP 2026-27 to 2028-29 (January 2026, original); Kerala Revised Citizens' Guide to Budget 2026-27 (June 2026); Economic Survey 2025-26 (full volume and Highlights); PIB release on the 57th GST Council meeting (8 Oct 2026); Kerala PSC Degree Level Preliminary syllabus.
- Every statistic carries a year. Provisional/revised/final/budget figures are labelled; Kerala January (original) and June (revised) budget figures are kept separate in Chapter 18.
- Calculation questions: answer keys were recomputed while writing (several wrong keys were caught and fixed). Test questions were checked by their authors; I spot-checked a sample, not all 500.

## What was NOT verified
- No outside fact-check (no web sources). Anything not in the documents above is flagged `[VERIFY]` or left out.
- Malayalam spelling/grammar has not been proofread by a native editor; shaping was checked visually on sampled pages (cover, chapter pages, tables, tests, glossary), not page by page.
- The revised June 2026 MTFP was never received (the file uploaded was identical to the January version), so Chapter 18 is cross-checked against the Revised Citizens' Guide only.
- Questions are original practice questions, not previous-year questions, and are labelled so in the book.

## Known remaining issues
1. Near-duplicate questions (same fact, different wording or numbers) remain in: Chapter 17 Q15 / Chapter 20 Q5 (KINFRA year); Chapter 18 Q14 / Chapter 19 Q17 (welfare pension); Test 2 Q33 / Test 4 Q30 area (MSME classification, now different numbers). Five test duplicates (Tests 4, 5, 8) were rewritten into different questions on the same facts. Several numerical questions reuse a chapter question's structure with different numbers.
2. Two source inconsistencies were avoided rather than resolved: Vizhinjam VGF share (9.32% stated vs about 9.4% computed) and the Kerala ration-card category sum (94.62 vs 94.92 lakh); the revised-budget debt ratio (33.44%) does not reproduce from the stated figures.
3. Cover is a vector recreation using cropped artwork from the supplied image (low resolution); a flat high-resolution cover image would replace it.
4. The GST rate effective date, consumer commission limits, Navratna list, SDG ranks, MSME limits and payment limits remain `[VERIFY]`.
5. File size is 8.4 MB; not compressed (compression tools can damage Malayalam text and links).

## Source files
`ebook-source/` holds chapter text, tests, fonts, cover assets and the build scripts (`build.py`, `cover.py`, `compile.py`). Run `python3 compile.py` to rebuild (needs Chromium and poppler tools).
