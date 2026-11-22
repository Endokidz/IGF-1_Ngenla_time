"""Build the blinded dual-review pack for the SPL reference meta-analysis (P6) and the calculator.

Inputs: review/screening_records.csv (from rerun_searches.py), spl_reference_tool/data/{decision_log,tool_curation,
age_extraction,tanner_extraction*,reference_rows,screening_log}.csv, P1 all_rows_with_flags.csv.
Outputs (review/):
  reviewer_workbook_TEMPLATE.xlsx  one copy per reviewer; NO current decisions inside (blinded)
  review_key.csv                   current AI/author decision per item; reviewers must not open it
Run from the repository root:  python3 spl_manuscripts/P6_SPL_reference_meta_calculator/review/build_review_pack.py
"""
import os
import sys

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
T = os.path.join(ROOT, "spl_reference_tool")
sys.path.insert(0, os.path.join(T, "code"))
from check_decisions import CATEGORIES  # noqa: E402

rd = lambda p: pd.read_csv(p, dtype=str).fillna("")
SCREEN_DEC = ["Include for full text", "Exclude", "Unsure"]
SCREEN_WHY = ["Not stretched penile length", "No healthy/reference group", "Adults only", "Disease or treatment cohort only",
              "Review/editorial/letter", "Case report/series", "Not human", "Duplicate record", "Other (comment)"]
CUR_DEC = ["Pool all rows", "Pool some rows (say which)", "Show, do not pool", "Exclude", "Unsure"]
EXT_DEC = ["Matches source", "Error (give correct value)", "Cannot check (no full text)"]
HDR = PatternFill("solid", fgColor="DDE7EE")
REV = PatternFill("solid", fgColor="FFF5D6")


def sheet(wb, name, cols, rows, reviewer_cols, widths):
    ws = wb.create_sheet(name)
    ws.append(cols + reviewer_cols)
    for c in ws[1]:
        c.font, c.fill, c.alignment = Font(bold=True), HDR, Alignment(wrap_text=True, vertical="top")
    for c in ws[1][len(cols):]:
        c.fill = REV
    for r in rows:
        ws.append(r + [""] * len(reviewer_cols))
    for i, w in enumerate(widths + [22] * len(reviewer_cols), start=1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = w
    ws.freeze_panes = "B2"
    return ws


def dropdown(ws, col_idx, list_ref, n):
    dv = DataValidation(type="list", formula1=list_ref, allow_blank=True)
    ws.add_data_validation(dv)
    L = ws.cell(1, col_idx).column_letter
    dv.add(f"{L}2:{L}{n + 1}")


def main():
    key = []
    # ---------------- 1. screening (titles only; reviewers read abstracts in Rayyan or PubMed) ----------------
    S = rd(os.path.join(HERE, "screening_records.csv"))
    S["tier"] = S.found_by.apply(lambda x: "B: only from over-broad query T19 (never screened)" if x.strip() == "puberty/Tanner#19" else "A: core")
    ai = rd(os.path.join(T, "data", "screening_log.csv")).drop_duplicates("pmid").set_index("pmid")
    s_rows = []
    for _, r in S.iterrows():
        s_rows.append([f"S{len(s_rows) + 1:04d}", r.tier, r.pmid, f"https://pubmed.ncbi.nlm.nih.gov/{r.pmid}/", r.title, r.journal, r.year, r.found_by])
        key.append(dict(item_id=s_rows[-1][0], sheet="1 Screening", ref=r.pmid,
                        current_decision=ai.decision.get(r.pmid, "not recorded at record level"), current_reason=ai.reason.get(r.pmid, ""),
                        decided_by="AI single screener" if r.pmid in ai.index else ""))

    # ---------------- 2. curation: one item per study, with the evidence a reviewer needs ----------------
    A = pd.concat([rd(os.path.join(T, "data", f)).assign(src=f) for f in
                   ("age_extraction.csv", "tanner_extraction.csv", "tanner_extraction_from_age_studies.csv")], ignore_index=True)
    P1 = rd(os.path.join(ROOT, "spl_manuscripts", "P1_newborn_SPL_meta", "data", "all_rows_with_flags.csv"))
    P1 = P1.rename(columns={"ethnicity_or_population": "population", "subgroup_label": "age_bin_label"}).assign(src="P1 newborn")
    P1["age_bin_label"] = "newborn " + P1.age_at_measurement + (" · " + P1.age_bin_label).where(P1.age_bin_label != "", "")
    ALL = pd.concat([A, P1], ignore_index=True, sort=False).fillna("")
    log = rd(os.path.join(T, "data", "decision_log.csv"))
    act = log[log.status == "active"]
    first = lambda g, c: next((v for v in g[c] if v), "") if c in g else ""
    c_rows = []
    for sid, g in ALL.groupby("study_id", sort=True):
        labels = "; ".join(dict.fromkeys(x for x in g.age_bin_label if x))[:600]
        n = pd.to_numeric(g.get("n"), errors="coerce")
        means = pd.to_numeric(g.get("mean_cm"), errors="coerce")
        c_rows.append([f"C{len(c_rows) + 1:03d}", sid, first(g, "first_author"), first(g, "year"), first(g, "pmid"),
                       f"https://pubmed.ncbi.nlm.nih.gov/{first(g, 'pmid')}/" if first(g, "pmid") else "",
                       first(g, "country"), "; ".join(sorted(set(g.src))), first(g, "population")[:500], first(g, "technique")[:700],
                       first(g, "fatpad_depressed"), first(g, "stretch"), first(g, "source_level"), str(len(g)), labels,
                       f"{int(n.min())}–{int(n.max())}" if n.notna().any() else "not reported",
                       f"{means.min():.2f}–{means.max():.2f}" if means.notna().any() else "", first(g, "notes")[:700]])
        d = act[act.study_id == sid]
        key.append(dict(item_id=c_rows[-1][0], sheet="2 Curation", ref=sid,
                        current_decision="; ".join(f"{x.decision} [{x.rows}]" for x in d.itertuples()) or "pooled (no rule)",
                        current_reason=" | ".join(d.reason_category), decided_by=" | ".join(dict.fromkeys(d.decided_by)) or "AI (default)"))

    # ---------------- 3. extraction check: every row the calculator pools or shows ----------------
    R = rd(os.path.join(T, "data", "reference_rows.csv"))
    e_rows = []
    for _, r in R.iterrows():
        stage = f"{r.tanner_system} {r.tanner_stage}".strip() if r.tanner_stage else ""
        e_rows.append([f"E{len(e_rows) + 1:03d}", r.study_id, r.pmid, r.kind, r.age_bin_label, stage, r.n,
                       r["mean"][:6], r.sd[:6], r.derivation, r.verbatim_quote[:900]])
    # ---------------- 4. methods decisions (author only; not blinded) ----------------
    M = [
        ["M1", "Primary rule for rows with a measurement concern",
         "(a) include all in primary, sensitivity without; (b) exclude documented concerns from primary, sensitivity with all; (c) exclude all unclear technique as well",
         "(b)", "The estimand is SPL measured to bone with maximal stretch in healthy boys. Rows with documented deviation estimate a different quantity. "
                "In P1, removing the 6 concern rows lowers tau from 0.38 to 0.28 cm and raises the mean from 3.19 to 3.29 cm, so the concern rows are biased short, not just noisy. "
                "(c) would drop most abstract-only newborn data and is better as a sensitivity analysis."],
        ["M2", "Apply M1 to P1 too", "yes / no", "yes", "One rule across the series. P1's current primary becomes its sensitivity analysis; the message of P1 (published references disagree) survives because tau stays large (0.28 cm)."],
        ["M3", "Registration", "PROSPERO / OSF registration of the protocol before human dual review / declare unregistered",
         "OSF now", "PROSPERO does not accept reviews past data extraction. A time-stamped OSF protocol registered before the human review makes the dual review and analysis prospective."],
        ["M4", "Search for publication", "keep AI PubMed searches / add librarian search (MeSH; Embase, Scopus, CNKI, LILACS)",
         "add librarian search", "The AI searches were keyword-only PubMed with truncated screening on some queries; referees will not accept them as the primary search."],
        ["M5", "Over-broad query T19 (753 records never screened)", "screen them / drop the query and report it",
         "screen them", "Dropping an executed query after seeing its size is hard to defend. About 4 h per reviewer."],
        ["M6", "Abstract-only data", "include in primary with sensitivity full-text-only / exclude from primary", "include + sensitivity",
         "Excluding them would remove most newborn populations; their effect is testable."],
        ["M7", "Primary pubertal covariate", "testis volume / genital stage / pubic hair", "testis volume",
         "Genital stage is partly defined by penile size (circular); testis volume is objective and measured by every endocrinologist."],
        ["M8", "Population (region) results", "report any region with data / only regions with >= 3 studies at that age, else descriptive", ">= 3 studies",
         "With 1-2 studies, region and measurement method cannot be separated."],
        ["M9", "Reviewers and adjudication", "name Reviewer A, Reviewer B and an adjudicator", "", "Required for PRISMA items 8-9."],
    ]
    # ---------------- write workbook ----------------
    wb = Workbook()
    ws0 = wb.active
    ws0.title = "Start here"
    for line in [
        "SPL reference meta-analysis (P6) and calculator: reviewer workbook",
        "",
        "Make your own copy and rename it with your initials, for example review_AB.xlsx. Work INDEPENDENTLY:",
        "do not look at the other reviewer's copy, at review_key.csv, or at the calculator's decision files until you have finished.",
        "",
        "1 Screening: title/abstract screening of every record from the logged PubMed queries. Read abstracts via the link",
        "  (or import screening_records.csv PMIDs into Rayyan with blinding on). Tier A first; tier B is the over-broad query T19.",
        "2 Curation: for each study, decide whether its rows should be pooled, shown but not pooled, or excluded, and why.",
        "  Apply the eligibility rules and the measurement-concern rule in sheet 4 (M1) as approved by the author.",
        "3 Extraction: check each extracted value against the source (verbatim quote given; open the paper where you can).",
        "4 Methods: the author's decisions; reviewers do not fill this sheet.",
        "",
        "Fill only the yellow columns. Use the drop-down lists. When both copies are done, run review/reconcile.py.",
    ]:
        ws0.append([line])
    ws0.column_dimensions["A"].width = 120
    ws0["A1"].font = Font(bold=True, size=13)
    lists = wb.create_sheet("Lists")
    for j, (name, vals) in enumerate([("screen", SCREEN_DEC), ("why", SCREEN_WHY), ("cur", CUR_DEC), ("cat", sorted(CATEGORIES)), ("ext", EXT_DEC)], start=1):
        lists.cell(1, j, name)
        for i, v in enumerate(vals, start=2):
            lists.cell(i, j, v)
    rng = lambda j, n: f"=Lists!${lists.cell(1, j).column_letter}$2:${lists.cell(1, j).column_letter}${n + 1}"

    ws1 = sheet(wb, "1 Screening", ["item_id", "tier", "pmid", "pubmed_link", "title", "journal", "year", "found_by_queries"], s_rows,
                ["decision", "exclusion_reason", "comment"], [8, 14, 10, 30, 80, 20, 6, 24])
    dropdown(ws1, 9, rng(1, len(SCREEN_DEC)), len(s_rows)); dropdown(ws1, 10, rng(2, len(SCREEN_WHY)), len(s_rows))
    ws2 = sheet(wb, "2 Curation", ["item_id", "study_id", "first_author", "year", "pmid", "pubmed_link", "country", "source_files", "population",
                                   "technique (verbatim)", "fat_pad_coded", "stretch_coded", "source_level", "n_rows", "rows (age/stage labels)",
                                   "n range", "mean range (cm)", "extraction notes"], c_rows,
                ["decision", "reason_category", "rows affected / comment"], [8, 22, 14, 6, 10, 28, 18, 18, 40, 60, 14, 12, 14, 7, 40, 10, 12, 60])
    dropdown(ws2, 19, rng(3, len(CUR_DEC)), len(c_rows)); dropdown(ws2, 20, rng(4, len(CATEGORIES)), len(c_rows))
    ws3 = sheet(wb, "3 Extraction", ["item_id", "study_id", "pmid", "kind", "age/row label", "stage", "n", "mean (cm)", "sd (cm)",
                                     "derivation", "verbatim source quote"], e_rows,
                ["check", "correct n", "correct mean", "correct SD", "comment"], [8, 22, 10, 9, 28, 14, 7, 8, 8, 24, 90])
    dropdown(ws3, 12, rng(5, len(EXT_DEC)), len(e_rows))
    sheet(wb, "4 Methods (author)", ["id", "decision", "options", "recommended", "why"], M, ["author choice", "notes"], [5, 34, 60, 16, 90])
    lists.sheet_state = "hidden"
    for ws in (ws1, ws2, ws3, wb["4 Methods (author)"]):
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
    wb.save(os.path.join(HERE, "reviewer_workbook_TEMPLATE.xlsx"))
    pd.DataFrame(key).to_csv(os.path.join(HERE, "review_key.csv"), index=False)
    print(f"screening {len(s_rows)} | curation {len(c_rows)} studies | extraction {len(e_rows)} rows | methods {len(M)}")


if __name__ == "__main__":
    main()
