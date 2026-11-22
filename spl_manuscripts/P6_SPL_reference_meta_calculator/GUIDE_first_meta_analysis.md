# Your first meta-analysis: the rules, in one page

**PRISMA is a reporting checklist (27 items) plus a flow diagram. It is not a method.** It asks you to report honestly what you did: how many records you found, who screened them, whether they worked independently, which tools (including AI) you used, and why each study was excluded. The methods themselves come from the Cochrane Handbook. Below are the eight steps, and where P6 stands on each.

| # | Step | The rule | P6 status | Who does it |
|---|---|---|---|---|
| 1 | Protocol | Write the question, eligibility criteria and analysis plan **before** screening, and register them with a timestamp. | Drafted (`review/README.md` M1, `review/AI_SCREENING_PROTOCOL.md`). Not frozen. | **You approve it.** I post it to OSF with you; PROSPERO is closed to us because extraction has already been done. |
| 2 | Search | Search several databases with a reproducible strategy, and save the exact queries and dates. | PubMed only, keyword searches (logged and re-runnable: 2,835 records). Embase, Scopus, CNKI and LILACS are missing. | Ideally a librarian. Otherwise I draft the strategies and you run the searches where you have access. |
| 3 | Screening | **Two independent reviewers** for every record, at title/abstract and again at full text. Disagreements go to a third person. | Only a single AI reviewer so far, and its decisions are not recorded for most records. | **You (A) + fresh AI (B) + a colleague for the disagreements.** |
| 4 | Data extraction | Two people extract, or one extracts and a second verifies every number. | AI extracted everything, each value with its verbatim quote. | **You verify the 228 values** (sheet 3), about one day. |
| 5 | Risk of bias / quality | Appraise every study with a named tool. | Not done. | AI drafts it and you check it. I will propose a tool suited to reference-value studies. |
| 6 | Analysis | Pre-specified model, heterogeneity (τ, I²), sensitivity analyses, and small-study bias where it makes sense. | Model done: it is the calculator. Sensitivity plan drafted (M1). | AI runs it; you interpret it with me. |
| 7 | Certainty | GRADE, or an explicit statement of the main limitations. | Not done. | Together. |
| 8 | Report | Fill the PRISMA checklist, include the flow diagram, and disclose AI use (tool, version, dates, stages). | Not started. | The `spl-meta-analysis` agent drafts it; you own it. |

## What referees will look for in a first-time author's review

Most often: a methodologist or statistician co-author, a registered protocol, dual screening, and transparent AI use.

A fellow or resident who joins as adjudicator and co-author covers the human side cheaply. Cochrane-style rules accept the AI as second screener only with the calibration test (`AI_SCREENING_PROTOCOL.md`).

## Your time, honestly

- Approve the protocol: 30 min.
- Calibration screening: 200 records, about 1 h.
- Full title/abstract screening: 2,835 records, mostly obviously irrelevant titles. About 10–15 h for a first-timer, spread over sessions.
- Full texts: about 70 studies, 1–2 days.
- Checking the extracted values: about 1 day.

Everything else is done by the AI, but you sign off on it.
