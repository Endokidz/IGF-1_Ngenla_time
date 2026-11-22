# Human dual review for P6 and the calculator

Every screening, curation and extraction decision so far was made by a single AI reviewer, or by the author alone. A publishable review needs two independent human reviewers and an adjudicator. This folder holds everything they need.

| File | What it is |
|---|---|
| `reviewer_workbook_TEMPLATE.xlsx` | One copy per reviewer, blinded: it contains no current decisions. Sheets: **1 Screening** (2,835 records), **2 Curation** (67 studies), **3 Extraction** (228 rows), **4 Methods** (9 decisions, author only). |
| `review_key.csv` | The current AI or author decision for every item. **Reviewers must not open it** until they have finished. |
| `reconcile.py` | Compares two completed copies and writes `reconciliation.xlsx`, containing: percent agreement and Cohen's κ per sheet; conflicts for the adjudicator; and "overturns", where both humans agree but differ from the current record, so the register must change. |
| `rerun_searches.py`, `search_rerun.csv`, `screening_records.csv` | Every logged PubMed keyword query re-run, limited to records in PubMed on 18 Nov 2026. |
| `build_review_pack.py` | Rebuilds the workbook and the key from the repository data. |

**How the record set was rebuilt.** 91 of 94 keyword queries reproduce their logged hit count exactly. The other three now return more hits than logged, which is consistent with records indexed since the search. The six similar-article actions cannot be re-run exactly, so they are listed but not re-run.

## Order of work

1. **Author first:** settle sheet 4, at least M1 (the rule below), M3 (registration) and M9 (who reviews). Then freeze the protocol on OSF.
2. **Reviewers A and B, independently:** sheets 1–3.
   - For screening, Rayyan with blinding on is easier than Excel: paste the PMIDs from `screening_records.csv` into PubMed, choose *Send to → Citation manager*, and import the `.nbib` file.
   - Do tier A first: 2,082 records from the screened queries.
   - Tier B (753 records) comes only from the over-broad query T19, which the AI never screened.
3. **Reconcile:** `python3 reconcile.py review_A.xlsx review_B.xlsx`. The adjudicator resolves the conflicts.
4. **Update the record.** The `spl-meta-analysis` agent applies the overturns to `decision_log.csv` and `tool_curation.csv`, with `decided_by` set to "dual human review (A, B; adjudicator C), date". `check_decisions.py` keeps the two files in step.

## M1. Proposed main-analysis rule for doubtful-measurement rows

The author has not yet approved this rule.

**Primary analysis:** technique-concordant rows. Pool rows from healthy reference samples measured as stretched length from the pubic bone, including rows whose technique is simply **not reported**.

**Shown, not pooled:** any row with a **documented** concern of one of these kinds:

1. **Technique deviation:** fat pad not depressed (measured from the skin junction), gentle or partial stretch, non-stretched length, or measurement under anaesthesia.
2. **Distribution altered before summary:** trimmed means, or outliers deleted.
3. **Implausible dispersion:** an SD below 0.5× or above 2× the pooled within-population SD at that age, with n ≥ 50. Also any internal inconsistency that the full text cannot resolve.
4. **Unsuitable sample:** hospitalised or acutely ill children, surgical patients, or children referred for a genital concern.
5. **Newborns only:** mixed gestational age.

**Sensitivity analyses:**

- **S1:** all rows, as published. This is P1's current primary analysis.
- **S2:** full-text rows with the technique confirmed only.
- **S3:** leave one study out.

For each, report τ, the pooled mean and the −2.5 SD threshold.

**Why.** The estimand is SPL measured to bone at maximal stretch in healthy boys, and documented deviations estimate a different quantity.

- In P1, removing the 6 concern rows lowers the between-population τ from 0.38 to 0.28 cm and raises the mean from 3.19 to 3.29 cm. The concern rows are systematically short, not merely noisy.
- Excluding every row whose technique is unreported as well would discard most newborn populations. That is better done as a sensitivity analysis (S2) than as the primary rule.

**Honest caveat.** The thresholds in item 3 are being set after the data have been seen. Freeze them on OSF before the human review, and declare this in the paper.
