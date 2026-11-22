# P6: Stretched penile length from birth to 18 years: a meta-analysis of reference data and an open calculator

**Status:** project opened on 2026-11-22. No manuscript text exists yet.

**Owner:** the project agent `spl-meta-analysis` (`.claude/agents/spl-meta-analysis.md`). In Claude Code, ask for it by name, for example "use the spl-meta-analysis agent to …".

## What this paper is

It is the methods-and-results paper for the SPL Z-Score Calculator (`spl_reference_tool/`). The paper covers four things:

- a systematic review of published SPL reference data, 0–18 y;
- a random-effects meta-regression of ln(mean) and ln(SD) on age, which is exactly the model the calculator runs;
- separate pubertal references on three scales: genital stage, pubic-hair stage and testis-volume class;
- an optional population (WHO-region) layer.

P1 (newborns) supplies the term-newborn rows. P4 supplies the measurement-error argument behind the second-examiner rule.

## Single sources of truth (shared with the calculator)

| What | File |
|---|---|
| Extracted data, each value with its verbatim source | `spl_reference_tool/data/age_extraction.csv`, `tanner_extraction*.csv`; newborns: `spl_manuscripts/P1_newborn_SPL_meta/data/all_rows_with_flags.csv` |
| **Every post-inclusion decision** (exclude, shown-not-pooled, scale handling), with date, reason category and who decided | `spl_reference_tool/data/decision_log.csv` |
| Rules the calculator actually applies | `spl_reference_tool/data/tool_curation.csv`. It must agree with the register; `code/check_decisions.py` enforces this and the build fails otherwise. |
| Screening decisions (PRISMA) | `spl_reference_tool/data/screening_log.csv`. It holds the age search (710 records); the Tanner and newborn searches have not yet been transcribed. |
| Model and outputs | `spl_reference_tool/code/build_model.py` → `app/model.json`, `figures/pooled_curve.png` |

## Decisions confirmed by the author

Do not reopen these.

1. **Fat-pad rule** (2026-11-18). Studies that document a non-depressed fat pad are not pooled.
   - Tomova 2010 is shown, not pooled.
   - Gabrich 2007's staging system is unknown, so it is never pooled by stage.
2. **Wang 2018, Bhat 2015 and Puri 2017 are visible but not pooled** (2026-11-22, revised). Their reasons are in the register.
3. **Pubertal scales** (2026-11-22). Genital stage, pubic-hair stage and testis-volume class are pooled and reported separately and never mapped onto one another. The G reference is labelled single-study. Rows with a measurement concern are not pooled by stage.
4. **Headline** (2026-11-22). When puberty data are entered, the calculator shows both the age z-score and the best-supported puberty z-score.
5. **Population layer** (2026-11-22). Region is optional and secondary: it is where a study was done, not ancestry.

## Open decisions for the author

The agent raises these; it does not settle them.

- **Measurement-concern rows.** In P1's primary analysis they are **included** (excluded only in sensitivity). In the calculator they are **never pooled**. P6 must pick one primary rule and use the other as a sensitivity analysis. **Proposed rule (M1):** exclude documented concerns from the primary analysis, keep unreported technique, and run three sensitivity analyses. The full text and rationale are in `review/README.md`.
- **Human dual review.** The blinded pack is in `review/`: 2,835 screening records, 67 studies to curate, 228 extracted rows and 9 methods decisions. Run `reconcile.py` when both copies are done.
- **Review of curation rules.** 41 of the 53 register entries are AI-proposed and await author review. For the paper they need two independent reviewers.
- **Registration.** Either register in PROSPERO retrospectively, or declare the review unregistered.
- **Population analysis.** Choose a pre-specified subgroup or meta-regression plan for region, and the minimum number of studies needed to report a region.
