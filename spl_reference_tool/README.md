# SPL Z-Score Calculator

**What it does.** You enter age, Tanner genital stage and stretched penile length (SPL). The calculator returns:

- **Pooled reference:** mean ± SD from the collated, random-effects reference.
- **Tanner-stage reference:** mean ± SD for the entered stage.
- **Per-study results:** each published study's own mean ± SD, with this child's z-score (SDS) and centile against it.
- **SDS colour scale:** marks abnormal results. Red is below −2.5 SD (micropenis range), amber is −2.5 to −2 SD, green is −2 to +2 SD and blue is above +2 SD.

**Live preview (private):** https://claude.ai/artifact/1LzawkWzmcg7g5YQSLHdRo

`app/index.html` is a single self-contained file, so it can also be served from GitHub Pages.

## Data

Every value is taken from a published study and stored with its verbatim source (`data/*_extraction.csv`).

- **Pooled age model:** 60 age-group rows from 22 studies, n = 11,087.
  - Term-newborn data come from the newborn meta-analysis (Paper 1).
  - Childhood and adolescent data come from 24 studies extracted for this tool.
- **Tanner model:** provisional, from 2 studies (Sotos 2017, Jaiswal 2019).
- **Curation:** every inclusion and exclusion rule, with its reason, is in `data/tool_curation.csv`.

Rows are excluded for second-hand quotation, suspected duplicate data, pooling across ages, or non-stretched measurement. Rows with a measurement concern are shown in the app but not pooled.

## Methods

- **Conversion to mean/SD** (`code/build_model.py`). Each row is converted from whatever the paper reported: mean/SD, SE, symmetric percentile pairs, LMS, or median with IQR or range.
- **Skew from published SD lines.** Where a study published smoothed −2 to +2 SD lines, an LMS triplet is fitted to them. That study's z-scores are then skew-correct.
- **Age model.** A random-effects REML meta-regression of ln(mean) on a natural cubic spline of ln(age + 0.25), with Knapp–Hartung adjustment. ln(SD) is modelled on a simpler spline.
- **Between-study heterogeneity.** τ is about 8.7% of the mean. The app turns it into a range of z-scores across plausible populations.
- **Data density.** A per-age count of contributing studies is stored, and the app warns when it is 2 or fewer.

## Known gaps

From 2 to 15 years only 2–3 studies contribute, and above 16 years only one. The two main mid-childhood studies disagree on spread: their coefficients of variation are 10–15% and 17–20%.

The largest missing references are paywalled and are listed in `DOWNLOAD_LIST.md`:

- Tomova 2010: n = 6,200, ages 0–19 y.
- Gabrich 2007: n = 2,010, with and without fat-pad compression.
- Soydan 2012: n = 1,539, by Tanner stage.
- Wang 2018: centile chart for ages 0–17 y.

## Rebuild

```
python3 code/build_model.py && python3 code/build_app.py
```

Digitised figures go in `data/digitized_*_bins.csv` and are picked up automatically. See `digitizer/README.md` for the validated digitisation workflow.
