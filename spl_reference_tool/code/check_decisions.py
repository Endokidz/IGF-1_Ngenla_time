"""Keep the decision register (data/decision_log.csv) and the calculator's rules (data/tool_curation.csv) in step.

Every exclude/flag rule the calculator applies must have one ACTIVE register entry with the same study, rows and
action, and vice versa. Every entry needs a date, a reason category from the controlled list, and who decided.
Run directly (exit 1 on any problem) or via build_model.py, which calls check() before building.
"""
import os
import sys

import pandas as pd

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
CATEGORIES = {
    "not_stretched_length", "fat_pad_not_depressed", "gentle_stretch_or_trimmed_data", "duplicate_or_overlapping_cohort",
    "secondhand_data", "superseded_by_full_text", "not_age_specific", "insufficient_reporting", "unsuitable_sample",
    "internal_inconsistency", "handled_in_newborn_dataset", "mixed_gestational_age", "measurement_concern",
    "staging_system_unknown", "different_staging_scale", "rule_application"}
DECISIONS_CALC = {"exclude": "exclude", "shown_not_pooled": "flag"}
REQUIRED = ["decision_id", "date", "study_id", "rows", "applies_to", "decision", "reason_category", "reason", "decided_by",
            "recorded_in", "status"]


def check(verbose=False):
    log = pd.read_csv(os.path.join(DATA, "decision_log.csv"), dtype=str).fillna("")
    cur = pd.read_csv(os.path.join(DATA, "tool_curation.csv"), dtype=str).fillna("")
    problems = []
    for c in REQUIRED:
        if c not in log:
            problems.append(f"decision_log.csv lacks column {c}")
    if problems:
        return problems
    if log.decision_id.duplicated().any():
        problems.append(f"duplicate decision_id: {log.decision_id[log.decision_id.duplicated()].tolist()}")
    for _, r in log.iterrows():
        for c in ("date", "study_id", "decision", "reason", "decided_by", "status"):
            if not r[c]:
                problems.append(f"{r.decision_id}: empty {c}")
        if r.reason_category not in CATEGORIES:
            problems.append(f"{r.decision_id}: reason_category '{r.reason_category}' not in the controlled list")
        if r.status not in ("active", "superseded"):
            problems.append(f"{r.decision_id}: status must be active or superseded")
        if r.supersedes and r.supersedes not in set(log.decision_id):
            problems.append(f"{r.decision_id}: supersedes unknown {r.supersedes}")
    act = log[(log.status == "active") & log.applies_to.str.contains("calculator; SPL reference meta-analysis", regex=False)
              & log.decision.isin(DECISIONS_CALC)]
    key = lambda sid, rows, action: (sid, "" if rows == "all rows" else rows, action)
    logged = {key(r.study_id, r.rows, DECISIONS_CALC[r.decision]) for _, r in act.iterrows()}
    rules = {key(r.study_id, r.label_contains, r.action) for _, r in cur.iterrows()}
    for k in sorted(rules - logged):
        problems.append(f"tool_curation rule with no active decision_log entry: {k}")
    for k in sorted(logged - rules):
        problems.append(f"active decision_log entry not applied in tool_curation.csv: {k}")
    if verbose:
        print(f"decision_log: {len(log)} entries ({(log.status == 'active').sum()} active); "
              f"{len(rules)} calculator rules all matched" if not problems else "")
    return problems


if __name__ == "__main__":
    p = check(verbose=True)
    for x in p:
        print("PROBLEM:", x)
    sys.exit(1 if p else 0)
