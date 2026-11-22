"""Reconcile two independently completed reviewer workbooks.

Usage:  python3 reconcile.py review_AB.xlsx review_CD.xlsx [--out reconciliation.xlsx]
For sheets 1-3 it reports how many items both reviewers completed, percent agreement and Cohen's kappa on the decision
column. It lists:
  * conflicts: Reviewer A and Reviewer B disagree. These go to the adjudicator.
  * overturns: A and B agree, but differ from the current AI/author decision in review_key.csv. The register and the
    calculator's rules must then be updated (decision_log.csv + tool_curation.csv; check_decisions.py enforces it).
Curation and screening decisions are compared on a coarse scale (include / show / exclude / unsure), so wording
differences in the drop-downs cannot create false conflicts.
"""
import argparse
import os
from collections import Counter

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SHEETS = {"1 Screening": ("decision", "exclusion_reason"), "2 Curation": ("decision", "reason_category"),
          "3 Extraction": ("check", "comment")}
COARSE = {"Include for full text": "include", "Pool all rows": "include", "Pool some rows (say which)": "include",
          "Show, do not pool": "show", "Exclude": "exclude", "Unsure": "unsure", "Matches source": "ok",
          "Error (give correct value)": "error", "Cannot check (no full text)": "cannot"}
KEY_COARSE = lambda s: ("exclude" if s.startswith("exclude") else "show" if "shown_not_pooled" in s or "check" in s
                        else "include" if s.startswith(("include", "pooled", "eligible")) else "unknown")


def kappa(a, b):
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / n ** 2
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("--out", default=os.path.join(HERE, "reconciliation.xlsx"))
    o = ap.parse_args()
    key = pd.read_csv(os.path.join(HERE, "review_key.csv"), dtype=str).fillna("").set_index("item_id")
    summary, conflicts, overturns = [], [], []
    for sh, (dcol, why) in SHEETS.items():
        A = pd.read_excel(o.a, sheet_name=sh, dtype=str).fillna("").set_index("item_id")
        B = pd.read_excel(o.b, sheet_name=sh, dtype=str).fillna("").set_index("item_id")
        both = A.index[(A[dcol] != "") & (B.reindex(A.index)[dcol] != "")]
        ca = [COARSE.get(A.at[i, dcol], A.at[i, dcol]) for i in both]
        cb = [COARSE.get(B.at[i, dcol], B.at[i, dcol]) for i in both]
        agree = sum(x == y for x, y in zip(ca, cb))
        summary.append(dict(sheet=sh, items=len(A), completed_by_both=len(both), agreement_pct=round(100 * agree / len(both), 1) if len(both) else None,
                            cohens_kappa=round(kappa(ca, cb), 3) if len(both) else None, conflicts=len(both) - agree))
        for i, x, y in zip(both, ca, cb):
            label = A.at[i, "title"] if "title" in A else A.at[i, "study_id"]
            if x != y:
                conflicts.append(dict(sheet=sh, item_id=i, item=str(label)[:120], reviewer_A=A.at[i, dcol], why_A=A.at[i, why],
                                      reviewer_B=B.at[i, dcol], why_B=B.at[i, why], adjudicated_decision="", adjudicator_note=""))
            elif sh != "3 Extraction" and i in key.index and x != "unsure" and KEY_COARSE(key.at[i, "current_decision"]) not in (x, "unknown"):
                overturns.append(dict(sheet=sh, item_id=i, item=str(label)[:120], consensus=A.at[i, dcol],
                                      current=key.at[i, "current_decision"], current_by=key.at[i, "decided_by"]))
            elif sh == "3 Extraction" and x == "error":
                overturns.append(dict(sheet=sh, item_id=i, item=str(label)[:120], consensus="extraction error confirmed by both",
                                      current=f"n {A.at[i, 'n']} mean {A.at[i, 'mean (cm)']} sd {A.at[i, 'sd (cm)']}",
                                      current_by=f"A: {A.at[i, 'correct n']}/{A.at[i, 'correct mean']}/{A.at[i, 'correct SD']}; "
                                                 f"B: {B.at[i, 'correct n']}/{B.at[i, 'correct mean']}/{B.at[i, 'correct SD']}"))
    with pd.ExcelWriter(o.out) as w:
        pd.DataFrame(summary).to_excel(w, sheet_name="summary", index=False)
        pd.DataFrame(conflicts or [{}]).to_excel(w, sheet_name="conflicts (adjudicate)", index=False)
        pd.DataFrame(overturns or [{}]).to_excel(w, sheet_name="overturns (update register)", index=False)
    print(pd.DataFrame(summary).to_string(index=False))
    print(f"\n{len(conflicts)} conflicts to adjudicate; {len(overturns)} consensus decisions that change the current record -> {o.out}")


if __name__ == "__main__":
    main()
