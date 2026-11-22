# P6: from project to submitted manuscript

**Paper:** "Stretched penile length from birth to 18 years: a meta-analysis of reference data with an open z-score calculator". It is an **original article** (a meta-analysis), not a review.

## 1. Why it can be accepted (the positioning)

The only competing paper is Negri et al., *BJU Int* 2026 (doi 10.1111/bju.70356). It covers prepubertal boys only, pools in four coarse age bands, and claims SPL fell 16–26% over two decades. P6 is different in five ways:

1. It covers **0–18 years including puberty**, with separate references by testis volume, pubic-hair stage and genital stage.
2. It fits a **continuous age model**, so it gives a z-score at any age instead of four bands.
3. It shows that **measurement technique, not time, explains most of the heterogeneity.** In P1, a time trend among newborns is absent (−0.05 cm per decade, 95% CI −0.26 to 0.16), and removing the doubtful-measurement rows cuts the between-population τ from 0.38 to 0.28 cm. P6 tests Negri's "decline" against technique directly. This is the paper's hook.
4. It comes with an **open, versioned calculator** that shows between-population uncertainty, along with the second-examiner rule.
5. Methods are **transparent**: a registered protocol, human plus validated-AI dual review, and every decision logged.

**What referees will check, and how we answer each:**

| Check | Our answer |
|---|---|
| Registered protocol | OSF, before the human review |
| Two databases or more | PubMed, Embase, Scopus, WoS, LILACS, plus citation chasing (including Negri's included-study list) |
| Dual screening and extraction | Resident + validated AI; PI adjudicates |
| Named appraisal tool | Pre-specified domains |
| Sensitivity analyses | S1–S3 |
| AI disclosure | Tool, version, dates, stages |
| Open data and code | Zenodo DOI |
| Experienced co-author | Methodologist |

## 2. Target journal

### How TAU judges a journal

Sources: Faculty of Medicine instructions (2025) and the medical library's publication-list service.

- Metrics are JCR (Web of Science) only. The journal's quartile is taken for the year of publication, in whichever of its categories scores highest.
- Q1–Q4 is credited for **original articles only**; reviews are listed separately.
- There is no top-10% tier and no Scimago/SJR. No list of excluded publishers was found.

### The trap: Web of Science "Review" indexing

Web of Science indexes a paper as a **Review** in either of two cases:

- the journal publishes it in a review section;
- the title contains "systematic review" or "review", and the term appears again in the abstract or introduction.

So we need both of the following:

- a journal that publishes meta-analyses as **original articles**;
- a title that presents the paper as what it genuinely is: **a meta-analytic reference construction with a calculator**. For example: *"Stretched penile length from birth to 18 years: meta-analytic centiles and a validated z-score calculator"*. The abstract still says "systematic review and meta-analysis", as PRISMA requires.

Adding **original data** (external validation on your clinic's measurements) settles the question beyond doubt: the paper becomes a development-and-validation study.

### Shortlist (cascade)

Quartiles marked ✱ must be verified in JCR (bit PI-08).

| Order | Journal | Why | Main risk | Cost to you |
|---|---|---|---|---|
| **1 (recommended)** | **Journal of Pediatrics**: Q1 Pediatrics ✱, JIF ~3.6 | Publishes paediatric reference curves and requires PRISMA; meta-analyses run as Original Articles; the readership uses the tool | 4,000-word limit including the abstract; article type to be confirmed with the editorial office | Nothing on the subscription route; open access under the TAU–Elsevier agreement (quota) |
| 2 | **European Journal of Endocrinology**: Q1 Endocrinology & Metabolism, JIF ~5–6 ✱ | Best fit for paediatric endocrinology | Has its own "Systematic Review and Meta-Analysis" type, which may count as neither. Submit as an **Original Research Article** only if external validation data are included | OUP hybrid; open access under the TAU–OUP agreement (quota runs out mid-year) |
| 3 | **Human Reproduction**: Q1 Ob/Gyn (5/143) ✱, JIF ~6.8 | Publishes meta-analyses in the original-research format, including genital-development ones | Scope fit is moderate | OUP hybrid; open access under the TAU–OUP agreement |
| Stretch (optional) | **JAMA Pediatrics**: Q1, JIF ~17 | Meta-analyses are published as *Original Investigation*, the cleanest fit with TAU | Low acceptance odds without external validation; a desk rejection costs about 1–2 weeks | No fee; no TAU agreement needed |

**Excluded:**

- JCEM, Hormone Research in Paediatrics, Pediatrics and Frontiers in Endocrinology: they publish meta-analyses as reviews or a separate type.
- Journal of Pediatric Urology and Endocrine Connections: not Q1.
- BJU International: it published Negri, so a second meta-analysis would likely look redundant.
- Human Reproduction Update: it publishes reviews only.

## 3. How the work is split

- **PI: 76 bits of 10–15 minutes** (about 18 hours in total). You decide, adjudicate and edit; you never start from a blank page.
- **Resident: 48 one-hour sessions**: searches, blind screening, full-text eligibility, and checking every extracted number.
- **AI: the bulk work between bits.** That covers protocol and section drafts, search strategies, the independent AI review, extraction, analysis and mock peer review.

The full list, with dependencies, is `plan/tasks.csv` (rebuild and re-simulate with `python3 plan/build_tasks.py`).

**Daily routine.** Open Claude Code in this repository and say **"today's bit"** (or **"resident session"**). The `spl-meta-analysis` agent serves the next ready task, with everything prepared, and records it as done.

| Phase | PI bits | Resident hours | Base-case days |
|---|---|---|---|
| 0 Team and decisions (M1–M10, resident, methodologist, journal, CRediT) | 9 | – | 0–8 |
| 1 Protocol + OSF registration | 4 | 1 | 5–14 |
| 2 Search (librarian, Embase/Scopus/WoS exports, Rayyan) | 2 | 3 | 12–21 |
| 3 Screening (calibration, then about 4,000 records) | 10 | 10 | 22–38 |
| 4 Full texts, extraction check, appraisal | 10 | 29 | 39–82 |
| 5 Analysis review | 5 | – | 83–88 |
| 6 Writing (Introduction and Methods are written early, while screening runs) | 26 | 4 | 14–106 |
| 7 Co-authors (14-day wait), mock peer review, submission | 10 | 1 | 107–127 |

## 4. How long

These figures come from a simulation of the actual task dependencies, starting 23 Nov 2026.

| Pace | Days to submission | Date |
|---|---|---|
| PI 1 bit/day, resident 1 h per weekday (**base**) | **128** | ~31 Mar 2027 |
| PI 2 bits/day, resident 1 h per weekday | 107 | ~10 Mar 2027 |
| PI 1 bit/day, resident 2 h per weekday | 104 | ~7 Mar 2027 |
| PI 2 bits/day, resident 2 h per weekday | 83 | ~14 Feb 2027 |

Add about 25% for holidays and slow replies, which makes the realistic base case about 160 days (early May 2027). The full-text phase is the longest, and it is the resident's work.

**Not included in these figures:** an external validation of the calculator on your clinic's own measurements. It is the strongest single boost to acceptance, but it needs Helsinki committee approval (usually 1–3 months). Either start the application now, in parallel, or make it the follow-up paper.

## 5. Main risks

| Risk | Mitigation |
|---|---|
| The editor sees the paper as redundant after Negri | Lead with the hook (technique vs "decline"), the puberty references and the tool. Send a pre-submission inquiry (bit PI-40). |
| Scepticism about AI-assisted methods | Calibration statistics, a human adjudicator, a full disclosure statement. |
| Thin adolescent data | Obtain Saleh 2018 and Largo & Prader 1983. State the limits honestly, and make P5 (SPL-REF) the forward plan. |
| Searches find many new studies | Built into the timeline as screening plus full-text hours. If more than about 40 new studies are found, full text grows by about 1 week per 12 studies. |
