# Handoff: SPL reference tool

## START HERE (fresh session, last updated 2026-11-18 at the end of session 3)

**Decisions confirmed by the author (do not reopen):**

1. **Tomova 2010 is not pooled.** The fat pad was not depressed. It stays visible in the per-study table.
2. **Gabrich 2007 Tanner staging is unknown.** Its Tanner rows stay out of the genital-stage model.
3. The same rule as Sotos 2017 applies to any study that documents a non-depressed fat pad.

**Still missing:**

| Group | Items |
|---|---|
| Tier 1 | Schonfeld 1942 pp. 760-777 (only p. 759 was received) |
| Tier 2 | Boas 2006 (16382001); Saleh 2018 (30411390); Tomova 2015 (25781529), to be checked for overlap with Tomova 2010; Romano-Riquer 2007 (17439530); Feldman 1975 (1113226) |
| Addendum | 24145175; 21682766; 38761403; 28082769. Titles are unknown: no addendum section exists in DOWNLOAD_LIST.md. |
| Figures | Wang 2018 Fig 1; Bhat 2015 Fig 3; Puri 2017 Fig 4a; Jaiswal 2019 Fig 1 |
| Manuscripts | Avril 2023 (36724045) for P2; Chen 2015 (25894960) for P2; Mancini 2021 (34283215) for P3 |

**Already received; do not re-extract.** Soydan 2012, Tomova 2010, Gabrich 2007, Ishii 2014, De Win 2026, Fok 2005, and Schonfeld p. 759. Uploads are matched by md5: repeat uploads of Ishii and Fok were byte-identical.

**Open tasks, in order:**

1. Process new PDFs as they arrive, following "Rules for each PDF" below.
2. **Tanner model: still provisional, now an author decision.** Soydan 2012 did NOT unblock it (see Batch 3).
   - No study with known n reports SPL by Marshall-Tanner *genital* stage. The only such data come from Sotos and Jaiswal, and neither gives n.
   - The large n-known staged data are all **pubic-hair** staged: Soydan PH1-5 (n = 1,539), De Win (flagged) and possibly Gabrich.
   - Options to put to the author:
     - (a) add a pubic-hair-stage reference, which needs a new app input; or
     - (b) keep the genital-stage reference provisional; or
     - (c) map Soydan's testis-volume classes to genital stages. This is not recommended: it conflates two different scales.
3. **P1 manuscript text is STALE** since Fok 2005 was added (see Batch 2). Once Boas, Romano-Riquer and Feldman are in:
   - re-run `code/analysis.py`, `code/within_country.py` and `code/fig_within_country.py`;
   - update every hard-coded number in `manuscript_P1_newborn_SPL_meta.md` against `data/results.json`;
   - rebuild with `python3 common/build.py`.
4. **P2 and P3** wait on Avril, Chen and Mancini.

**After each batch:**

1. Rebuild the model and the app.
2. Check `figures/pooled_curve.png` and `k_local`.
3. Read the artifact, then republish it with `url`.
4. Update this file.
5. Commit and push. Never commit PDFs or figure images.

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
  - `data/age_extraction.csv`: 26 studies, 168 rows. This includes the originals of Tomova 2010 and Gabrich 2007, and Ishii 2014.
  - `data/tanner_extraction*.csv`: Sotos 2017 and Jaiswal 2019 (genital stage); Gabrich 2007 (staging system unknown, excluded from the genital model); De Win 2026 (pubic-hair stage, flagged).
  - Newborn rows come from `../spl_manuscripts/P1_newborn_SPL_meta/data/all_rows_with_flags.csv`.
  - `data/tool_curation.csv` holds every exclude/flag rule and its reason. Add rules there; never edit the model to drop data.
- **Model:** pooled REML spline meta-regression of ln(mean) and ln(SD) on ln(age + 0.25). Its current fit is 88 rows from 24 studies, n = 18,681, with τ_log = 0.135.
  - The weakest ages are above 13 y, where 2–3 studies contribute and Gabrich (high) and Jaiswal/Wang (low) disagree by about 4 cm.
  - Tanner stages are still pooled provisionally with equal weights, using Sotos and Jaiswal only, neither of which reports n.
- **Digitiser:** `digitizer/digitize.py`, validated in `digitizer/README.md`. Point error is 0.02 cm; bin means are within 0.12 cm; curves are within 0.006 cm.


## Batch 1 (2026-11-18): received and processed

| File | Status |
|---|---|
| Tomova 2010 (21135345) | Table extracted (20 rows, n = 310 each). **Flagged, not pooled**: the fat pad is not depressed (pubopenile skin junction). The author confirmed this on 2026-11-18; if pooled, tau_log rises from 0.135 to 0.150. Kumanov 2007 is excluded as a duplicate of its 0-y stratum. |
| Gabrich 2007 (17676248) | Tabela 2 has 19 age rows, with n from Tabela 1. Tabela 3 gives Tanner 2-5, but the staging system is not stated (the author confirmed it is unknown), so these rows are excluded from the genital model by the fixed regex. The second-hand quotes stay excluded. |
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

## Batch 3 (2026-11-18): Soydan 2012 (22902017), full text

- **Table 1 is not Marshall–Tanner genital staging.** Its "genital stage" is a testis-volume class: 1-3.9, 4-11.9, 12-20 and >20 mL are stages 1-4.
  - Stored as `stratum_type=testis_volume_class`. The fixed regex excludes these rows from the genital model.
- **Table 2 is Tanner–Marshall pubic hair (PH1-5),** stored with `tanner_system` = pubic hair. It is not pooled into the genital model.
- **Totals.** Each stratum's mean and SD are computed exactly by combining its per-age cells. This reproduces every published total mean, and also the reported −2.5 SD row.
  - The printed SEs are slightly inconsistent; for example, the 12-20 mL class prints 0.04 where the cells give 0.049.
- **Age rows.** Three rows were added to `age_extraction.csv` (13, 14 and 15 y; n = 52, 1,329 and 158), each combining that age's cells across strata.
  - The footnote's age-specific "−2 SD" limits (5.4, 6.4 and 7.5 cm) are about 1 cm lower than the table data imply (6.4, 7.3 and 8.4). The cause is unexplained; this is noted, not acted on.
- Technique: from the symphysis pubis (fat pad implied depressed). The degree of stretch is not stated.
- Sample: selected, non-obese, healthy military-school applicants.
- The abstract-only rows (labelled "13-15 y") stay excluded.
- **Model now:** 91 rows from 25 studies, n = 20,220, tau_log = 0.136. k_local at 12-15 y is now 4.

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
