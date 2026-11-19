# Stretched penile length (SPL) in the paediatric age range: a five-paper manuscript series

**Status:** complete first drafts, not yet submitted.
Each manuscript is provided as editable Markdown (`manuscript_*.md`), as a compiled version with numbered Vancouver references (`*_compiled.md`), and as a Word file (`*.docx`).

## Data integrity

No patient data were invented. Every dataset in this series is one of three kinds:

- **Published data.** These were extracted from PubMed and PubMed Central. Each value is stored next to the verbatim sentence or table cell it came from (`data/*extraction*.csv`).
- **Simulation output.** The simulation is explicitly labelled as such, is fully reproducible (seed 20261118), and was validated against closed-form solutions.
- **A protocol.** It contains design calculations only.

All references were checked against PubMed. `common/build.py` will not compile a manuscript if any citation key fails to resolve to a verified reference. Five references are not indexed in PubMed; they are marked † and must be checked by hand (`common/references_manual.md`).

## The papers

| # | Paper | Type | Key result |
|---|---|---|---|
| P1 | [Newborn SPL across 26 populations](P1_newborn_SPL_meta/manuscript_P1_newborn_SPL_meta.md) | SR + meta-analysis (24 studies, n = 9,788) | Pooled mean 3.20 cm (3.05–3.36). Between-population τ (0.38 cm) equals the within-population SD. 66% of the heterogeneity lies **within** countries. The fixed 2.5 cm cut-off labels between <0.01% and 60% of newborns, depending on the population. |
| P2 | [Hormonal treatment of micropenis](P2_hormonal_therapy_meta/manuscript_P2_hormonal_therapy_meta.md) | SR + meta-analysis (15 arms, n = 378) | Overall +1.50 cm. Infant gonadotropins in CHH give +2.26 cm (a median doubling, durable to adolescence). IM testosterone gives +1.15 cm and oral TU +0.80 cm. No study had a concurrent untreated control. The smallest effects are within the range of regression to the mean. |
| P3 | [Obesity and the apparent micropenis](P3_obesity_SPL_review/manuscript_P3_obesity_SPL_review.md) | SR, SWiM synthesis (22 studies) | With the fat pad depressed, the deficit in obese boys is trivial (−0.18 cm; SMD −0.11). 19–43% of micropenis referrals are not confirmed, with buried penis from obesity a leading cause. |
| P4 | [The right count, the wrong children](P4_measurement_error_simulation/manuscript_P4_measurement_error_simulation.md) | Monte Carlo simulation (ADEMP; 73 scenarios × 4 × 10⁶ boys) | An error SD of half the population SD (≈2 mm in a newborn) doubles apparent prevalence, with a PPV of 34%. Fat-pad bias cannot be averaged away. Regression to the mean is 0.58 SD. |
| P5 | [SPL-REF protocol](P5_SPL_REF_protocol/manuscript_P5_SPL-REF_protocol.md) | Multicentre protocol | GAMLSS centiles 0–18 y, with measurement error quantified and corrected. Sample sizes: n ≈ 4,500, plus 1,000 newborns, a minipuberty cohort of 155, and a reliability study of 240 children, derived from Cole (2021). |

The papers form one argument. P1 shows that published references disagree. P4 shows why that matters at −2.5 SD. P3 and P2 apply the same lens to adiposity and to treatment. P5 is the study that resolves the problem.

## Layout

```
common/      meta.py (validated random-effects engine), prisma.py, build.py, verified reference tables
P1..P5/      manuscript_*.md / .docx, code/, data/ (extractions, search logs, results), figures/
```

To rebuild everything, run the following from `spl_manuscripts/`. It needs Python 3 with numpy, scipy, pandas, matplotlib and statsmodels, plus pandoc.

```
python3 P4_measurement_error_simulation/code/simulate.py && python3 P4_measurement_error_simulation/code/figures.py
python3 P5_SPL_REF_protocol/code/sample_size.py && python3 P5_SPL_REF_protocol/code/schema_figure.py
python3 P1_newborn_SPL_meta/code/analysis.py && python3 P1_newborn_SPL_meta/code/within_country.py && python3 P1_newborn_SPL_meta/code/fig_within_country.py
python3 P2_hormonal_therapy_meta/code/analysis.py
python3 P3_obesity_SPL_review/code/analysis.py
python3 common/build.py P*/manuscript_*[!d].md
```

## Before any submission

These steps are also listed in the "Note to authors" box at the top of each manuscript.

1. **Human verification.** Two independent reviewers must re-screen and verify every extraction in P1–P3. Screening and extraction were AI-assisted, used PubMed only, and had a single extractor.
2. **Wider searches.** Search Embase, Scopus and CNKI/LILACS, and obtain the full texts listed as unavailable in each search log.
3. **Registration.** Register in PROSPERO, or declare each review unregistered.
4. **Placeholders.** Complete authors, affiliations, funding, conflicts of interest and CRediT statements. Write the P5 patient-and-public-involvement statement only after that involvement has taken place.
5. **Disclosure.** Disclose AI assistance as each target journal requires.
6. **Possible duplicate publication.** Verify the flagged concern (P2, Note to authors item 3) before mentioning it in print.
