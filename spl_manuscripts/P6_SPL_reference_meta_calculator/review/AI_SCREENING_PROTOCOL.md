# Protocol: one human reviewer plus one independent AI reviewer

**Status:** draft. It must be approved by the author and frozen (OSF) **before** either reviewer starts.

## Why this design

Every systematic review needs two independent screenings of every record, so that one reviewer's mistakes are caught by the other. The 2025 joint position statement of Cochrane, Campbell, JBI and CEE permits AI in that role on four conditions:

1. the use is justified;
2. its performance is shown on this review;
3. a human stays accountable;
4. everything is reported (tool, version, dates, which stages it affected).

Two AI passes cannot count as two reviewers. They are the same kind of model, so their mistakes are correlated, and no human would have judged anything. The design is therefore:

| Role | Who |
|---|---|
| Reviewer A | the author (human), screening every record |
| Reviewer B | a fresh AI run: a different model from the one that ran the original searches, blinded to every earlier decision, using only the frozen criteria below |
| Adjudicator | a human colleague. They decide only where A and B disagree, usually 5–10% of records. |

## Eligibility criteria for title/abstract screening (to approve)

**Include** a record if all of the following apply. When unsure, include: this stage is deliberately generous, and the full text decides.

- **Population:** boys aged 0–18 y. Clinical studies count only if they report a healthy or untreated comparison group.
- **Measure:** penile length is measured. At this stage, stretched, not stated, or unclear technique all count.
- **Data:** it reports, or probably reports, penile-length summaries by age or pubertal stage (mean ± SD, centiles, a nomogram or reference values).
- **Design:** any primary observational study (cross-sectional or cohort), or the control arm of a trial.

**Exclude** a record if any of the following apply:

- adults only;
- only boys with genital, endocrine or DSD conditions, with no healthy group;
- no penile length measured (for example anogenital distance only, or imaging only);
- fetal or ultrasound data only;
- reviews, editorials or letters with no new data;
- case reports;
- not human.

## Full-text stage

Two reviewers again: the author and the AI. Apply the title/abstract criteria plus:

- the numbers can be extracted;
- the study is not a duplicate of another cohort;
- the main-analysis rule M1 (`README.md`): documented measurement problems are **shown, not pooled**.

## How the AI reviewer is run

- **Fresh session.** The prompt contains only the frozen criteria above and one record (title plus abstract). The AI has no access to the repository, the earlier logs, `review_key.csv` or the other reviewer's answers.
- **Output per record:** decision (include / exclude / unsure), a reason code from the workbook list, and a one-line justification. These go into a copy of the workbook, `review_AI.xlsx`.
- **What is recorded:** model ID, run date, and the exact prompt text, which is stored in this folder before the run.

## Showing the AI is good enough (calibration)

1. The author screens a calibration set of 200 records first. It contains every study that has been used so far (about 45), with the rest drawn at random.
2. The AI screens the same 200 records.
3. **Threshold:** the AI must find at least 95% of the records the author includes. If it does not, the prompt is revised once and re-tested. If it still fails, the AI is not used as Reviewer B.
4. Report: sensitivity, specificity, and Cohen's κ with the author.

## Afterwards

Run `reconcile.py review_author.xlsx review_AI.xlsx`. The adjudicator resolves the conflicts. The `spl-meta-analysis` agent then updates the registers with `decided_by` set to "human (author) + AI (model, date); adjudicated by …".
