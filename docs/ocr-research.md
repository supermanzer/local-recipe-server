# OCR Strategy Research: Mixed Text & Multi-Column Layouts

Research conducted 2026-07-19 in support of the long-term OCR recipe-import goal (see `.claude/CLAUDE.md`). This is analysis only — no code was implemented as part of this research. It's intended as a starting point for later hands-on experimentation, not a spec.

## 1. Executive Summary

Both problems named — fraction misrecognition and multi-column layout confusion — are well-documented, well-understood failure modes, not edge cases. Both have established mitigations that are cheap to test, in roughly increasing order of effort:

1. **Configuration/preprocessing tuning** of the OCR engine already provisioned (Tesseract) — cheapest, fastest to try.
2. **Swapping engines** for a layout-aware one (PaddleOCR, or a cloud document-intelligence API) — moderate effort, likely bigger accuracy jump.
3. **LLM-based post-correction** — feeding raw OCR output (or the image itself, for multimodal models) to an LLM to clean up and structure the result — currently the most effective single lever in the research literature, and arguably the best fit for this project since it already has an LLM-assisted dev workflow.

## 2. Problem 1: Mixed Alphanumeric Text & Fraction Misrecognition

### What's happening
Tesseract (and OCR engines generally) segment and classify glyph-by-glyph using statistical models trained on typical prose. A slash-delimited fraction like "1/2" is visually ambiguous — the engine may segment "1", "/", "2" as three separate low-confidence glyphs and snap them to whatever full-character shapes score highest against its training set (hence "y2"-style garbage). Superscript/subscript fraction numerators and single-character Unicode fractions (½, ¼, ¾) are flagged in Tesseract's own documentation as needing special handling — they aren't reliably recognized by default ("Improving the Quality of the Output").

### Findings
- **Character whitelisting** (`tessedit_char_whitelist`) restricts the recognizer's candidate set for a region, acting as a real recognition clue, not just a post-filter — useful when you can isolate a region (e.g., an ingredients column) that should only contain digits, fraction slashes, unit abbreviations, and known ingredient words (Whitelisting and Blacklisting Characters with Tesseract and Python).
- Tesseract also supports **blacklisting**, and "unblacklisting" specific glyphs like case fractions when you need the engine to specifically look for them (Improving the Quality of the Output).
- Whitelisting reliably works on Tesseract engine 3 and 4.1+, but **not on 4.0** — worth confirming your installed Tesseract's version behavior before relying on it (PyImageSearch, "Whitelisting and Blacklisting...").
- For lines that are known to be short numeric/fraction fragments, **`--psm 7`** (treat the region as a single line of text) or **`--psm 6`** (single uniform block) outperform the default automatic segmentation, because the default mode's layout heuristics get confused by short, isolated tokens ("OCR for digits only," Tesseract docs).
- Use **`--oem 3`** (LSTM + legacy engine combined) explicitly rather than relying on defaults, for best compatibility with whitelisting across versions.
- **Unicode vulgar fraction characters** (½ U+00BD, ¼ U+00BC, ¾ U+00BE, and the extended set through U+215E) are a distinct, narrow character class. Some OCR training pipelines apply **NFC Unicode normalization** to improve consistency, but per available research this is "an understudied area" — expect inconsistent recognition of the single-character fraction glyphs specifically, separate from the ASCII "1/2" case (Compart, "List of Unicode Characters..."; general Unicode-OCR literature).
- Fonts matter directly: **`tessdata_best`** trained models are slower but meaningfully more accurate than `tessdata_fast`/`tessdata_legacy` for exactly this kind of visually ambiguous glyph work ("Improving the Quality of the Output").

### Actionable steps to test
1. Grab 5–10 real recipe photos/PDFs with varied fonts (the more "designed" cookbook fonts first — these are your worst case).
2. Run each through Tesseract with default settings and record raw output as a baseline.
3. Re-run with `--oem 3 --psm 6` (and separately `--psm 7` on cropped ingredient-line snippets) and diff against baseline.
4. Switch to the `tessdata_best` traineddata file and re-run step 3 — measure the delta.
5. For the ingredients column specifically, try `tessedit_char_whitelist` with a character set of `0123456789/½¼¾⅓⅔⅛⅜⅝⅞.,- ` plus the alphabet, and compare fraction-specific error rates.
6. Build a small "ground truth" text file per test image and compute a simple error rate (word-level is fine — no need for formal CER/WER tooling in this exploratory phase) so improvements are measurable, not just eyeballed.

## 3. Problem 2: Multi-Column Layout Parsing

### What's happening
Tesseract's default mode (`--psm 3`, fully automatic page segmentation) tries to infer reading order itself and frequently merges text across column boundaries — reading straight across a page instead of down one column, then the next ("Tesseract Page Segmentation Modes (PSMs) Explained"). This is a layout-detection problem, not a character-recognition problem, and it's a known, structural weakness of classic OCR engines.

### Findings
- **`--psm 4`** ("assume a single column of text of variable sizes") is the standard low-effort fix when you can pre-crop or pre-split the image into individual columns before OCR ("Tesseract Page Segmentation Modes (PSMs) Explained"; DeepWiki PSM docs).
- Tesseract has a tab-stop detection mode for column-consistent text, but community reporting is mixed — fine-tuning PSM choice on the specific input tends to matter more than relying on automatic column detection (arXiv, "Mining Spatio-temporal Data...").
- **This is the area where Tesseract is weakest relative to newer tools.** Purpose-built layout-analysis systems and modern vision-language OCR models (PaddleOCR-VL, DeepSeek-OCR, OlmOCR-2, MinerU 2.5) are reported to "significantly outperform Tesseract" specifically on multi-column, mixed-content documents, because they jointly model layout detection and reading order instead of bolting a heuristic on top of a character recognizer (E2E Networks, "7 Best Open-Source OCR Models 2025"; arXiv, "Qianfan-OCR").
- Among more traditional engines, a 2025 benchmark found **Tesseract fastest but PaddleOCR notably more precise** on structured/layout-heavy documents (invoices, receipts, forms) — recall was lower for PaddleOCR in that same benchmark, so the right choice depends on whether you'd rather miss text or misplace it (CodeSOTA, "PaddleOCR vs Tesseract vs EasyOCR").
- Among cloud document-intelligence APIs, reported accuracy on complex table/line-item extraction: **AWS Textract ~84.8%**, **Azure Document Intelligence ~87%** on line items specifically, with Azure reported as giving "richer semantic output" and confidence-scored layout maps useful for building a custom validation layer (invoicedataextraction.com, "AWS Textract vs Google Document AI vs Azure Document Intelligence").

### Actionable steps to test
1. On the same test image set, manually crop 2–3 test images into their individual columns and OCR each crop separately with `--psm 4` — compare against running the whole page through default `--psm 3`. This isolates "is column-splitting itself the fix" from "is the engine the problem."
2. If crop-then-OCR meaningfully improves accuracy, that's a cheap, permanent pipeline shape worth keeping regardless of which engine is chosen.
3. Install PaddleOCR locally (Python-installable, no cloud account needed) and run it against the same uncropped multi-column images, diffing reading order against Tesseract's output.
4. If budget allows, run 3–5 of the hardest test images through one cloud API's free tier (Google Cloud Vision, AWS Textract, or Azure Document Intelligence all have free trial quotas) as an accuracy ceiling reference point — useful even without using it in production, since it shows how much headroom exists.

## 4. A Third Lever Worth Testing: LLM Post-Correction

This wasn't one of the two originally named problems, but it showed up strongly enough in the research that it's worth flagging as possibly the highest-leverage option, given this project's existing tooling:

- Multiple 2024–2025 studies report OCR + LLM post-correction pipelines reaching **character error rates as low as 1.5%**, with GPT-based correction cutting character error rate by **over 60%** on difficult (historical) datasets (MarkTechPost, "Large Language Models (LLMs) for OCR Post-Correction"; ResearchGate, "Opportunities and Challenges of LLMs as Post-OCR Correctors").
- **Multimodal LLMs that see the image directly** (not just raw OCR text) do meaningfully better than text-only correction — one study reports Gemini 2.0 Flash combined with a print-OCR engine hit **sub-1% normalized character error rate**, without any image preprocessing, because the model can cross-reference the visual glyph shape against context (e.g., "this is obviously a fraction in an ingredient list, not the letter y") (arXiv, "OCR Error Post-Correction with LLMs in Historical Documents").
- The known failure mode: LLM correctors can produce **fluent, plausible-looking hallucinations** — a "corrected" ingredient amount that reads naturally but is simply wrong, without the tell-tale garbled spelling that flags classic OCR errors (arXiv, same source). This matters a lot for a recipe app — a hallucinated "2 cups" instead of "½ cup" is a worse failure than an obviously broken string, because it won't look broken.
- This approach is also directly relevant to the stated OCR goal, since Mistral's Document AI and comparable tools are already being used elsewhere specifically for structured recipe extraction — title, ingredients, instructions — from images/PDFs (Microsoft Tech Community, "Mistral Document AI... Structured OCR & Recipe Extraction").

### Actionable steps to test
1. Take the Tesseract baseline output from Problem 1's tests and, as a separate experiment, feed the raw (uncorrected) OCR text plus the recipe image to a multimodal LLM with a targeted prompt ("extract structured ingredients as {name, amount, unit}; the source is OCR output and may contain fraction errors"). Compare accuracy against the raw OCR and against tuned-Tesseract results.
2. Specifically stress-test the hallucination risk: deliberately include a test case with an ambiguous/garbled fraction and check whether the LLM's correction is verifiably right or just plausible-sounding. Don't trust fluency as a proxy for correctness.
3. If this direction looks promising, the natural target shape for parsed output is the same one already used by `RecipeManageSerializer` — `{name, ingredients: [{name, amount, unit}], steps: [{order, step, component, ingredients}]}` — so a future implementation wouldn't need a second data path into the database.

## 5. Summary Comparison

| Approach | Effort to test | Best for | Caveat |
|---|---|---|---|
| Tesseract config tuning (PSM, whitelist, `tessdata_best`) | Very low | Cheap wins on the engine already installed | Ceiling is limited — Tesseract is structurally weak on layout |
| Crop-then-OCR per column | Low | Multi-column layout, works with any engine | Requires a column-detection or manual-crop step first |
| PaddleOCR / open-source layout-aware engines | Medium | Better precision on structured/multi-column docs | New dependency, GPU helps, mixed recall in benchmarks |
| Cloud document-intelligence APIs | Medium (account setup) | Best out-of-the-box table/layout accuracy | Ongoing per-page cost, external dependency, data leaves your infra |
| Multimodal LLM post-correction (image + OCR text) | Medium | Fraction/context disambiguation, matches the final data shape | Fluent hallucination risk — must be validated, not trusted blindly |

## 6. Suggested Order of Experimentation

Given this is exploratory and no feature work is planned yet, cheapest-first still applies:

1. Build a small (5–10 image) test corpus with hand-typed ground truth now — every experiment below depends on being able to measure "did that help."
2. Tesseract config tuning (PSM/whitelist/`tessdata_best`) — cheapest, uses what's already installed.
3. Crop-then-OCR for columns — cheap, and its lessons transfer to any engine chosen later.
4. PaddleOCR side-by-side comparison — moderate effort, no external account needed.
5. One multimodal-LLM-correction experiment — likely the best accuracy ceiling and the most natural fit for this codebase, but validate the hallucination risk explicitly before trusting it.

---

## Works Cited

Compart. "List of Unicode Characters with Decomposition Mapping 'Vulgar Fraction Form.'" *Compart*, compart.com/en/unicode/decomposition/%3Cfraction%3E. Accessed 19 July 2026.

CodeSOTA. "PaddleOCR vs Tesseract vs EasyOCR: OCR Speed and Accuracy 2026." *CodeSOTA*, codesota.com/ocr/paddleocr-vs-tesseract. Accessed 19 July 2026.

DeepWiki. "Page Segmentation Modes." *tesseract-ocr/tessdoc*, deepwiki.com/tesseract-ocr/tessdoc/6.2-page-segmentation-modes. Accessed 19 July 2026.

DocuClipper. "OCR Preprocessing: How to Improve Extraction Accuracy." *DocuClipper*, docuclipper.com/blog/ocr-preprocessing/. Accessed 19 July 2026.

E2E Networks. "7 Best Open-Source OCR Models 2025: Benchmarks & Cost Comparison." *E2E Networks*, e2enetworks.com/blog/complete-guide-open-source-ocr-models-2025. Accessed 19 July 2026.

Harper, Grant. "recipe-ocr: Optical Character Recognition for Recipes." *GitHub*, github.com/grantharper/recipe-ocr. Accessed 19 July 2026.

Invoice Data Extraction. "AWS Textract vs Google Document AI vs Azure Document Intelligence." *Invoice Data Extraction*, invoicedataextraction.com/blog/aws-textract-vs-google-document-ai-vs-azure-document-intelligence. Accessed 19 July 2026.

MarkTechPost. "Large Language Models (LLMs) for OCR Post-Correction." *MarkTechPost*, 13 Aug. 2024, marktechpost.com/2024/08/13/large-language-models-llms-for-ocr-post-correction/.

Microsoft Tech Community. "Mistral Document AI on Azure Foundry — Structured OCR & Recipe Extraction in TypeScript." *Microsoft Tech Community*, techcommunity.microsoft.com/blog/azuredevcommunityblog/unlock-structured-ocr-in-typescript-with-mistral-document-ai-on-ai-foundry/4466039. Accessed 19 July 2026.

"OCR Error Post-Correction with LLMs in Historical Documents: No Free Lunches." *arXiv*, 2025, arxiv.org/html/2502.01205v1.

"PreP-OCR: A Complete Pipeline for Document Image Restoration and Enhanced OCR Accuracy." *arXiv*, 2025, arxiv.org/pdf/2505.20429.

"Qianfan-OCR: A Unified End-to-End Model for Document Intelligence." *arXiv*, 2026, arxiv.org/html/2603.13398v1.

"Tesseract Page Segmentation Modes (PSMs) Explained: How to Improve Your OCR Accuracy." *PyImageSearch*, 15 Nov. 2021, pyimagesearch.com/2021/11/15/tesseract-page-segmentation-modes-psms-explained-how-to-improve-your-ocr-accuracy/.

Tesseract OCR. "Improving the Quality of the Output." *Tesseract OCR Documentation*, tesseract-ocr.github.io/tessdoc/ImproveQuality.html. Accessed 19 July 2026.

"Whitelisting and Blacklisting Characters with Tesseract and Python." *PyImageSearch*, 6 Sept. 2021, pyimagesearch.com/2021/09/06/whitelisting-and-blacklisting-characters-with-tesseract-and-python/.
