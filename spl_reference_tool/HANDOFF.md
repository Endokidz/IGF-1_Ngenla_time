# Handoff: SPL reference tool

This file lets a fresh session pick up the work from where it stopped.

## Where things stand (2026-11-18)

- **Branch:** `ccr-9c847be6-w5ygtk`, draft PR #1. **Do not merge.** `main` serves the live IGF-1 calculator.
- **Calculator:** `spl_reference_tool/app/index.html`. It is published as a private artifact at **https://claude.ai/artifact/1LzawkWzmcg7g5YQSLHdRo**. To keep that URL, republish with `url` set to it.
- **Pipeline:**

  ```
  cd spl_reference_tool
  python3 code/build_model.py
  python3 code/build_app.py
  ```

  This needs `pip install scipy statsmodels matplotlib`.
- **Data:**
  - `data/age_extraction.csv`: 24 studies, 119 rows.
  - `data/tanner_extraction*.csv`: Sotos 2017 and Jaiswal 2019.
  - Newborn rows come from `../spl_manuscripts/P1_newborn_SPL_meta/data/all_rows_with_flags.csv`.
  - `data/tool_curation.csv` holds every exclude/flag rule and its reason. Add rules there; never edit the model to drop data.
- **Model:** pooled REML spline meta-regression of ln(mean) and ln(SD) on ln(age + 0.25). Its current fit is 60 rows from 22 studies, with τ_log = 0.087.
  - The weakest ages are 2–18 y, where only 1–3 studies contribute.
  - Tanner stages are pooled provisionally with equal weights.
- **Digitiser:** `digitizer/digitize.py`, validated in `digitizer/README.md`. Point error is 0.02 cm; bin means are within 0.12 cm; curves are within 0.006 cm.


## Batch 1 (2026-11-18): received and processed

| File | Status |
|---|---|
| Tomova 2010 (21135345) | Table extracted (20 rows, n = 310 each). **Flagged, not pooled**: the fat pad is not depressed (pubopenile skin junction). This is pending the author's decision; if pooled, tau_log rises from 0.135 to 0.150. Kumanov 2007 is excluded as a duplicate of its 0-y stratum. |
| Gabrich 2007 (17676248) | Tabela 2 has 19 age rows, with n from Tabela 1. Tabela 3 gives Tanner 2-5, but the staging system is not stated, so these rows are excluded from the genital model by the fixed regex. The second-hand quotes stay excluded. |
| Ishii 2014 (25471079) | 10 LMS rows, one per raw age band, with n from Table 1. The birth row is excluded (newborn; overlaps Matsuo 2014). |
| De Win 2026 (43023809), the "Gunter 2026" of the download list | Table 1 healthy controls by **pubic-hair** stage. Flagged: implausible SDs, fat pad not depressed. Fig. 2E is not digitised. |
| Schonfeld 1942 | The upload contains only p. 759 (title page and references), with no data. The remaining pages (760-777) are still needed. |

- **Model now:** 87 rows from 23 studies, n = 14,053, tau_log = 0.135.
- **k_local** rises by 1-2 at every age; ages 9-17 y now have 3 studies, or 2 at 17 y.
- **Tanner model:** still provisional. Soydan 2012 has not been received. Gunter/De Win is pubic-hair staged. Gabrich's staging system is unspecified, and Sotos and Jaiswal give no n.
- **Code fix:** in `build_model.py`, the Tanner-system filter `contains("G|genital", case=False)` matched any letter "g". It is now anchored to `^(genital|G\b)`.


## Batch 2 (2026-11-18): Fok 2005

- **Fok 2005 (15665508)** is added to `P1_newborn_SPL_meta/data/term_extraction.csv`: n = 4,628, 3.0 ± 0.4 cm, pubic ramus, within 48 h. P1 `analysis.py`, `within_country.py` and the figures have been re-run.
  - Pooled mean: 3.20 → 3.19 cm.
  - −2.5 SD threshold: 2.26 → 2.25 cm.
  - WPR subgroup: n goes from 766 to 5,394.
- **The P1 manuscript text is now STALE.** About 40 hard-coded numbers no longer match `results.json`. Update the text in one pass once Boas 2006, Romano-Riquer 2007 and Feldman 1975 arrive. Also remove Fok from the 'not retrievable' list on line 11.
- The duplicate uploads of Ishii 2014 (×2) and Fok 2005 (×2) are byte-identical.

## Next task: add the papers the user supplies

The user has the missing PDFs. These are the PMIDs in `DOWNLOAD_LIST.md` and its addendum:

| Priority | PMIDs |
|---|---|
| Tier 1 | 21135345 Tomova 2010; 17676248 Gabrich 2007; 22902017 Soydan 2012; 43023809 Gunter 2026; Schonfeld 1942 (no PMID) |
| Tier 2 | 16382001; 25471079; 15665508; 30411390; 25781529; 17439530; 1113226 |
| Addendum | 24145175; 21682766; 38761403; 28082769 |
| Figures | Wang 2018 Fig 1 (PMC6219296); Bhat 2015 Fig 3 (PMC4397544); Puri 2017 Fig 4a; Jaiswal 2019 Fig 1 |

### Rules for each PDF

1. **Copyright.** Never commit PDFs or figure images to this repository; it is public. Keep them in the session's upload or scratch area. Only the extracted numbers, with short verbatim source quotes, go into `data/`.
2. **Tables.** Append rows to `data/age_extraction.csv` or `data/tanner_extraction.csv`, using the existing column schema.
   - Fill `verbatim_quote` with the exact table cell or sentence and `table_id`, and set `source_level=fulltext_table`.
   - Record the technique: whether the fat pad was depressed, and maximal versus gentle stretch.
   - Never impute a value.
3. **Figures.** Use `digitizer/digitize.py`: `detect_axes`, then `detect_ticks`, then read the tick labels and `calibrate`, then `marker_mask`/`detect_markers` or `trace_curve`.
   - Save an overlay PNG to scratch and **show it to the user** for verification.
   - Bin the points by age, then write `data/digitized_<study>_bins.csv`, with n taken from the **paper's reported n**.
   - Centile curves (P3–P97) give mean ≈ P50 and SD = (P97 − P3)/3.762.
4. **Second-hand quotes.** These are now replaced by the originals. Remove the corresponding exclude rules for Gabrich2007 and Tomova2010 in `tool_curation.csv` only if the new rows use the same `study_id`. Otherwise leave them in place, so the second-hand quotes stay excluded.
5. **Duplicate cohorts.** Check for overlaps before pooling:
   - Tomova 2015 against Tomova 2010;
   - Kumanov 2007, which is the under-1-year stratum of Tomova 2010;
   - Wang 2018 against Yi 2017.
6. **Rebuild and check.** Rebuild, check `figures/pooled_curve.png`, and confirm that `k_local` increases where expected. Then republish the artifact to the same URL, and commit and push.
7. **Tanner model.** With Soydan, Gabrich and Gunter available, it moves from provisional to n-weighted random effects (this branch already exists in `build_model.py`).

## Manuscripts (spl_manuscripts/)

Papers P1–P5 are complete drafts in `.md` and `.docx`, built with `python3 common/build.py <manuscript.md>`. The build refuses any citation key that isn't verified.

Supplied PDFs also feed these manuscripts:

| Paper | PDF | Data needed |
|---|---|---|
| P2 | Avril 2023 (36724045) | Table 1 and Supplementary Table 2 |
| P2 | Chen 2015 (25894960) | SPL change in the control group |
| P3 | Mancini 2021 (34283215) | Values by BMI group |
| P1 | Tier 2 newborn studies | Extra rows; re-run `code/analysis.py` and `code/within_country.py` |
