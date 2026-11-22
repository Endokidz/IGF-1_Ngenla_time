# SPL Z-Score Calculator

**What it does.** You enter age and stretched penile length (SPL), and optionally the genital stage, the pubic-hair stage and the testis volume. The calculator returns:

- **Pooled age reference:** mean ± SD from a random-effects meta-regression across published studies, with the z-score range across plausible populations.
- **Pubertal references, one per scale:** genital stage (G), pubic-hair stage (PH) and testis-volume class (TV). The scales are never mapped onto one another.
- **Per-study results:** each published study's own mean ± SD, with this child's z-score (SDS) and centile against it.
- **SDS colour scale:** red is below −2.5 SD (micropenis range), amber is −2.5 to −2 SD, green is −2 to +2 SD and blue is above +2 SD.
- **Headline:** the age z-score, plus, when puberty data are entered, the best-supported puberty z-score.
- **Optional population layer:** pools only studies from the selected WHO region that cover the child's age, and says when there are none. Region is where a study was done, not ancestry.
- **Safety alerts** directly under the result, including when the age and pubertal references disagree, a preterm newborn, unconfirmed fat-pad depression, and sparse data.

**Live preview (private):** https://claude.ai/artifact/1LzawkWzmcg7g5YQSLHdRo

`app/index.html` is a single self-contained file, so it can also be served from GitHub Pages.

## Data

Every value is taken from a published study and stored with its verbatim source (`data/*_extraction.csv`). The current counts are printed by `code/build_model.py` and shown in the app's Methods panel, which is generated from `app/model.json`. Counts are deliberately not repeated here, so this file cannot go stale.

- **Term newborns** come from the newborn meta-analysis (Paper 1). The newborn reference is for term boys only, and the app says so for a preterm boy.
- **Childhood and adolescence** come from the studies extracted for this tool.
- **Curation:** every inclusion, exclusion and flag rule, with its reason, is in `data/tool_curation.csv`. The dated register behind those rules (who decided, when, and the reason category) is `data/decision_log.csv`; screening decisions are in `data/screening_log.csv`. `code/check_decisions.py` keeps the register and the rules in step, and the build fails otherwise. Rows with a measurement concern, such as a fat pad not depressed, gentle stretch, trimmed data or a hospitalised sample, are **shown, not pooled**. The same rule applies to the age model and to the pubertal references.

## Methods

- **Conversion to mean/SD** (`code/build_model.py`). Each row is converted from whatever the paper reported: mean/SD, SE, mean ± 2 SD limits, symmetric percentile pairs, LMS, or median with IQR or range.
- **Skew from published SD lines.** Where a study published smoothed −2 to +2 SD lines, an LMS triplet is fitted to them, so that study's z-scores are skew-correct.
- **Age model.** A random-effects REML meta-regression of ln(mean) on a natural cubic spline of ln(age + 0.25), with Knapp–Hartung adjustment. ln(SD) is modelled on a simpler spline.
- **Pubertal references.** Pooled separately within each scale. Random effects are used where every study reports n; otherwise an equal-weight average is labelled provisional. With one study, the app says it is one population's value, not a pooled reference.
- **Data density.** A per-age count of contributing studies is stored, and the app warns when it is 2 or fewer.

## Known gaps

See `DOWNLOAD_LIST.md` ("Current ask") for the papers that would close them.

- **Genital stage:** one usable study (Jaiswal 2019, no n per stage). Its G5 mean (9.8 cm) is well below adult norms, so the G reference can falsely reassure.
- **Minipuberty (about 3 months):** 2 studies.
- **Adolescence:** the n-known studies disagree by about 4 cm (Gabrich and Soydan high; Jaiswal and Park low).

## Rebuild and test

```
python3 code/build_model.py && python3 code/build_app.py
node tests/app.test.js
```

The build needs Python 3 with numpy, scipy, pandas, statsmodels and matplotlib. The tests need Node with Playwright and Chromium. They drive the real page headlessly and check the following:

- z-scores against an independent calculation from `model.json`;
- age-input handling;
- that the staging scales are never conflated;
- that flagged rows are never pooled;
- the safety alerts;
- the generated methods text;
- the layout at phone width.

Digitised figures go in `data/digitized_*_bins.csv` and are picked up automatically. See `digitizer/README.md` for the validated digitisation workflow.
