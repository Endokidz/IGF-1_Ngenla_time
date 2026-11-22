"""P6 project-to-manuscript task list: 10-15 min bits for the PI, 1-hour bits for the resident, AI work in between.

    python3 build_tasks.py            -> writes tasks.csv and prints the calendar simulation
Scheduling assumptions (edit SCENARIOS): PI does N bits per day on every day; resident does M one-hour bits per
weekday; AI/agent steps take 1 calendar day; external waits as listed in WAITS. A task starts only when all its
dependencies are done (plus any wait). The PI always takes the earliest-ready task, so writing Introduction/Methods
fills the days when screening work sits with the resident.
"""
import csv, datetime as dt, os

HERE = os.path.dirname(os.path.abspath(__file__))
T = []          # (id, phase, owner, minutes, title, what_to_do, done_when, depends)


def add(i, ph, own, mins, title, what, done, dep=()):
    T.append(dict(id=i, phase=ph, owner=own, minutes=mins, title=title, what_to_do=what, done_when=done, depends_on=";".join(dep)))


# ---- Phase 0: decide and build the team --------------------------------------------------------------------------
add("PI-01", "0 Team", "PI", 15, "Read the 1-page guide; confirm roles", "Read GUIDE_first_meta_analysis.md. Confirm: resident = Reviewer A, AI = Reviewer B, you = adjudicator.", "Roles confirmed in chat")
add("PI-02", "0 Team", "PI", 10, "Decide M1 (doubtful-measurement rule)", "Agent shows a 5-line brief; answer approve/edit.", "M1 answered", ["PI-01"])
add("PI-03", "0 Team", "PI", 10, "Decide M2, M5, M6", "Apply M1 to P1? Screen the 753 T19 records? Abstract-only data in primary?", "Answered", ["PI-02"])
add("PI-04", "0 Team", "PI", 10, "Decide M7, M8", "Testis volume as primary pubertal covariate? Region reported only with >= 3 studies?", "Answered", ["PI-03"])
add("PI-05", "0 Team", "PI", 15, "Approve screening criteria (M10)", "Read the criteria block in review/AI_SCREENING_PROTOCOL.md; approve or edit.", "Criteria frozen", ["PI-04"])
add("PI-06", "0 Team", "PI", 10, "Invite the resident", "Send the agent-drafted invitation (role, ~48 h over ~3 months, co-authorship).", "Resident agreed", ["PI-01"])
add("PI-07", "0 Team", "PI", 10, "Invite a methodologist/statistician co-author", "Send the agent-drafted email (2-3 h of review at protocol and results stage).", "Sent", ["PI-01"])
add("PI-08", "0 Team", "PI", 15, "Choose the target journal", "Pick from the Q1 shortlist in SUBMISSION_PLAN.md (fit, TAU rules, APC cover).", "Journal fixed", ["PI-01"])
add("PI-09", "0 Team", "PI", 10, "Authorship and CRediT", "Approve the agent-drafted author order and CRediT roles.", "Approved", ["PI-06", "PI-07"])
# ---- Phase 1: protocol + registration ----------------------------------------------------------------------------
add("AI-01", "1 Protocol", "AI", 0, "Draft PRISMA-P protocol", "Agent drafts the protocol from README, M1-M10 and the criteria.", "Draft in plan/", ["PI-05"])
for k, sec in enumerate(["question and eligibility", "search, selection and extraction", "analysis, sensitivity analyses and appraisal tool"], start=10):
    add(f"PI-{k}", "1 Protocol", "PI", 15, f"Approve protocol: {sec}", f"Read the protocol section on {sec}; approve or mark edits.", "Section approved", [f"PI-{k-1}" if k > 10 else "AI-01"])
add("PI-13", "1 Protocol", "PI", 15, "Register on OSF", "Log in to OSF (your account), paste the agent-prepared registration, submit; send the DOI to the agent.", "OSF DOI recorded", ["PI-12"])
# ---- Phase 2: search ---------------------------------------------------------------------------------------------
add("AI-02", "2 Search", "AI", 0, "Draft search strategies", "MeSH + text-word strategies for PubMed, Embase, Scopus, Web of Science, LILACS; citation chasing incl. Negri 2026.", "Strategies in plan/", ["PI-12"])
add("PI-14", "2 Search", "PI", 10, "Ask the TAU librarian", "Send the agent-drafted email: database access, PRESS peer review of the strategies, Negri 2026 supplement (included-study list).", "Sent", ["AI-02"])
add("PI-15", "2 Search", "PI", 10, "Approve final strategies", "Read librarian comments as summarised by the agent; approve.", "Approved", ["PI-14"], )
add("R-01", "1 Protocol", "Resident", 60, "Orientation and practice", "Read GUIDE, protocol, criteria; screen 20 practice records with the agent's feedback.", "Practice done", ["PI-12", "PI-06"])
add("R-02", "2 Search", "Resident", 60, "Run Embase search and export", "Run the approved Embase strategy via TAU access; export RIS; upload to the repo folder the agent names.", "Export uploaded", ["PI-15", "R-01"])
add("R-03", "2 Search", "Resident", 60, "Run Scopus + Web of Science and export", "Same as R-02 for Scopus and WoS (and LILACS if time).", "Exports uploaded", ["R-02"])
add("AI-03", "2 Search", "AI", 0, "De-duplicate and build the screening set", "Merge with the PubMed re-run; de-duplicate; PRISMA identification counts; Rayyan import file.", "Screening set ready", ["R-03"])
add("R-04", "2 Search", "Resident", 60, "Set up Rayyan (blind mode)", "Create the Rayyan review, import the file, switch blinding on, invite the PI; set the exclusion reasons list.", "Rayyan ready", ["AI-03"])
# ---- Phase 3: title/abstract screening ---------------------------------------------------------------------------
add("R-05", "3 Screening", "Resident", 60, "Calibration: screen 200 records", "Screen the 200-record calibration set in Rayyan (blind).", "200 screened", ["R-04", "PI-13"])
add("AI-04", "3 Screening", "AI", 0, "AI screens calibration set; computes sensitivity", "Fresh blinded AI run on the same 200; sensitivity, specificity, kappa.", "Report ready", ["R-05"])
add("PI-16", "3 Screening", "PI", 10, "Go/no-go on the AI reviewer", "Read the calibration report: AI must find >= 95% of the resident's includes.", "Decision recorded", ["AI-04"])
prev = "PI-16"
for j in range(9):
    add(f"R-{6+j:02d}", "3 Screening", "Resident", 60, f"Screen titles/abstracts, batch {j+1} of 9", "Screen the next ~450 records in Rayyan (blind).", "Batch screened", [prev if j == 0 else f"R-{5+j:02d}"])
for j in range(8):
    add(f"PI-{17+j}", "3 Screening", "PI", 15, f"Adjudicate screening conflicts, batch {j+1} of 8", "Agent lists ~35 records where resident and AI disagree; decide each (include if in doubt).", "Batch adjudicated", [f"R-{6+j:02d}"])
add("PI-25", "3 Screening", "PI", 10, "Approve screening counts", "Check the PRISMA numbers the agent computed.", "Approved", ["PI-24", "R-14"])
# ---- Phase 4: full text, extraction, appraisal -------------------------------------------------------------------
for j in range(4):
    add(f"R-{15+j}", "4 Full text", "Resident", 60, f"Retrieve full texts, batch {j+1} of 4", "Download ~30 PDFs via TAU library / interlibrary loan; place them in the private folder the agent names (never in the public repo).", "Batch retrieved", ["PI-25" if j == 0 else f"R-{14+j}"])
for j in range(10):
    add(f"R-{19+j}", "4 Full text", "Resident", 60, f"Full-text eligibility, batch {j+1} of 10", "Assess ~12 full texts against the criteria in the workbook (blind to the AI).", "Batch assessed", [f"R-{18+j}" if j else "R-18"])
for j in range(6):
    add(f"PI-{26+j}", "4 Full text", "PI", 15, f"Adjudicate full-text conflicts, batch {j+1} of 6", "Agent shows 3 disputed studies with the key sentences; decide each.", "Batch adjudicated", [f"R-{20+round(j*1.6)}"])
add("AI-05", "4 Full text", "AI", 0, "Extract data from newly included studies", "Verbatim-sourced extraction; update the register and rebuild.", "Extraction done", ["PI-31", "R-28"])
for j in range(10):
    add(f"R-{29+j}", "4 Full text", "Resident", 60, f"Verify extraction, batch {j+1} of 10", "Check ~40 extracted values against the PDFs (sheet 3).", "Batch verified", ["AI-05" if j == 0 else f"R-{28+j}"])
add("PI-32", "4 Full text", "PI", 15, "Spot-check extraction (1/2)", "Check 10 random values the agent picks against the PDF.", "Done", ["R-31"])
add("PI-33", "4 Full text", "PI", 15, "Spot-check extraction (2/2)", "Same for another 10 values.", "Done", ["R-35"])
add("AI-06", "4 Full text", "AI", 0, "Draft appraisal (risk of bias / applicability) for every study", "Pre-specified domains: sampling, health status, technique, examiner training, reporting.", "Drafts ready", ["R-38"])
for j in range(5):
    add(f"R-{39+j}", "4 Full text", "Resident", 60, f"Verify appraisal, batch {j+1} of 5", "Check ~14 study appraisals; change where you disagree.", "Batch verified", ["AI-06" if j == 0 else f"R-{38+j}"])
add("PI-34", "4 Full text", "PI", 15, "Adjudicate appraisal disagreements (1/2)", "Decide disputed domains.", "Done", ["R-41"])
add("PI-35", "4 Full text", "PI", 15, "Adjudicate appraisal disagreements (2/2)", "Decide disputed domains.", "Done", ["R-43"])
# ---- Phase 5: analysis ---------------------------------------------------------------------------------------------
add("AI-07", "5 Analysis", "AI", 0, "Run final analyses", "Primary model, S1-S3, year x technique (the 'decline' question), stage and population results, figures.", "Results pack ready", ["PI-35", "R-38"])
for k, what in enumerate(["main age curve and table", "sensitivity analyses", "the 'secular decline' test (year vs technique)", "pubertal and population results"], start=36):
    add(f"PI-{k}", "5 Analysis", "PI", 15, f"Review results: {what}", f"Agent shows one figure/table on {what} with 3 lines of interpretation; accept or question.", "Reviewed", [f"PI-{k-1}" if k > 36 else "AI-07"])
add("PI-40", "5 Analysis", "PI", 10, "Send results to the methodologist; pre-submission inquiry", "Send the agent-drafted email to the methodologist and the 150-word inquiry to the target editor.", "Sent", ["PI-39"])
# ---- Phase 6: writing (agent drafts each section first) ------------------------------------------------------------
W = [("Introduction", 2, ["PI-12"]), ("Methods", 4, ["PI-15"]), ("Results", 4, ["PI-39"]), ("Discussion", 5, ["PI-36+R"]),
     ("Abstract, title, key points", 2, ["DISC"]), ("Figures", 3, ["PI-39"]), ("Supplement (search strings, excluded studies, appraisal table)", 2, ["PI-35"]),
     ("PRISMA 2020 checklist", 2, ["RES"]), ("Declarations (funding, conflicts, AI-use statement, data/code DOI)", 1, ["PI-09"]), ("Cover letter", 1, ["ABS"])]
k, last = 41, {}
for sec, nb, dep in W:
    for b in range(nb):
        d = {"PI-36+R": [last.get("Results", "PI-39")], "DISC": [last.get("Discussion")], "RES": [last.get("Results")], "ABS": [last.get("Abstract, title, key points")]}.get(dep[0], dep)
        add(f"PI-{k}", "6 Writing", "PI", 15, f"Edit {sec} ({b+1}/{nb})", f"Agent drafts {sec.lower()} to the target journal's format; you edit one part per bit.", "Part approved", [f"PI-{k-1}"] if b else d)
        last[sec] = f"PI-{k}"; k += 1
add("R-44", "6 Writing", "Resident", 60, "Reference check (1/3)", "Check every citation against the claim it supports (agent lists them).", "Done", [last["Discussion"]])
add("R-45", "6 Writing", "Resident", 60, "Reference check (2/3)", "Continue.", "Done", ["R-44"])
add("R-46", "6 Writing", "Resident", 60, "Reference check (3/3) + formatting", "Finish; check journal formatting.", "Done", ["R-45"])
add("R-47", "6 Writing", "Resident", 60, "Cross-check PRISMA checklist", "Confirm each checklist item points to the right page/line.", "Done", [last["PRISMA 2020 checklist"]])
# ---- Phase 7: co-authors, mock review, submission --------------------------------------------------------------------
add(f"PI-{k}", "7 Submit", "PI", 10, "Send the full draft to co-authors", "Send the agent-drafted email with a 2-week deadline.", "Sent", [f"PI-{k-1}", "R-46", "R-47", "PI-40"]); send = f"PI-{k}"; k += 1
mock = []
for b in range(4):
    add(f"PI-{k}", "7 Submit", "PI", 15, f"Mock peer review ({b+1}/4)", "Agent runs 3 adversarial referee reports + editor summary; you accept/reject fixes for one report per bit.", "Fixes decided", [f"PI-{k-1}" if b else send]); mock.append(f"PI-{k}"); k += 1
integ = []
for b in range(3):
    add(f"PI-{k}", "7 Submit", "PI", 15, f"Integrate co-author comments ({b+1}/3)", "Agent merges comments; you decide the contested ones.", "Integrated", [f"PI-{k-1}" if b else "WAIT-COAUTH"]); integ.append(f"PI-{k}"); k += 1
add("R-48", "7 Submit", "Resident", 60, "Assemble the submission package", "Files, figure formats, checklist, ORCID ids of all authors.", "Package ready", [integ[-1]])
add(f"PI-{k}", "7 Submit", "PI", 15, "Suggested and excluded reviewers", "Pick 4 suggested reviewers from the agent's list (no conflicts).", "Chosen", [mock[-1]]); k += 1
add(f"PI-{k}", "7 Submit", "PI", 15, "Final read and SUBMIT", "Read abstract and cover letter once more; submit in the journal portal.", "Submitted", [f"PI-{k-1}", "R-48"])
WAITS = {"PI-15": ("PI-14", 3), "WAIT-COAUTH": (send, 14), "PI-36": None}


def simulate(pi_per_day, res_per_weekday, start=dt.date(2026, 11, 23), ai_lag=1):
    done, day = {}, 0
    tasks = {t["id"]: t for t in T}
    wait_done = lambda w: (WAITS[w][0] in done and day >= done[WAITS[w][0]] + WAITS[w][1])
    def ready(t):
        for d in filter(None, t["depends_on"].split(";")):
            if d.startswith("WAIT"):
                if not wait_done(d): return False
            elif d not in done: return False
            elif done[d] == day and tasks[d]["owner"] != t["owner"]: return False   # hand-offs between people take a day; one person may chain bits
            elif tasks[d]["owner"] == "AI" and day < done[d] + ai_lag: return False
        w = WAITS.get(t["id"])
        if w and not (w[0] in done and day >= done[w[0]] + w[1]): return False
        return True
    while len(done) < len(T) and day < 1000:
        weekday = (start + dt.timedelta(days=day)).weekday() < 5
        for t in T:                                 # AI steps finish the day they become ready
            if t["owner"] == "AI" and t["id"] not in done and ready(t): done[t["id"]] = day
        for own, cap in (("PI", pi_per_day), ("Resident", res_per_weekday if weekday else 0)):
            for _ in range(cap):
                nxt = next((t for t in T if t["owner"] == own and t["id"] not in done and ready(t)), None)
                if nxt: done[nxt["id"]] = day
        day += 1
    return day, start + dt.timedelta(days=day)


if __name__ == "__main__":
    with open(os.path.join(HERE, "tasks.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(T[0]) + ["status"]); w.writeheader()
        for t in T: w.writerow({**t, "status": "todo"})
    n = {o: sum(1 for t in T if t["owner"] == o) for o in ("PI", "Resident", "AI")}
    print(f"bits: PI {n['PI']} (~{sum(t['minutes'] for t in T if t['owner']=='PI')/60:.1f} h), resident {n['Resident']} h, AI steps {n['AI']}")
    for lab, p, r in [("base: PI 1 bit/day, resident 1 h/weekday", 1, 1), ("PI 2 bits/day, resident 1 h/weekday", 2, 1),
                      ("PI 1 bit/day, resident 2 h/weekday", 1, 2), ("PI 2 bits/day, resident 2 h/weekday", 2, 2)]:
        d, end = simulate(p, r)
        print(f"{lab:45s} -> {d:3d} days, submission ~{end:%d %b %Y}")
