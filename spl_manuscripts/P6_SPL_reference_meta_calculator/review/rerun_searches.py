"""Re-run every logged PubMed keyword query of the three AI searches, limited to records in PubMed on the search date,
to reconstruct the complete record set for blinded human dual screening.

Usage (from repo root; needs network access to eutils.ncbi.nlm.nih.gov):
    python3 spl_manuscripts/P6_SPL_reference_meta_calculator/review/rerun_searches.py
Writes review/search_rerun.csv (query-level: logged vs re-run hits) and review/screening_records.csv (one row per PMID).
Similar-article (related citations) actions are not reproducible exactly and are listed, not re-run.
"""
import csv, json, os, re, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LOGS = {"age 1 mo-18 y": "spl_reference_tool/data/search_log_age.md",
        "puberty/Tanner": "spl_reference_tool/data/search_log_tanner.md",
        "newborn (P1)": "spl_manuscripts/P1_newborn_SPL_meta/data/search_log.md"}
EU = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
MAXDATE = "2026/11/18"
TOOL = "spl-reference-review-pack"


def get(url, **params):
    params.update(tool=TOOL)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(EU + url + "?" + urllib.parse.urlencode(params), timeout=60) as r:
                data = r.read()
            time.sleep(0.4)                      # stay under NCBI's 3 requests/second without an API key
            return data
        except Exception:
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"eutils failed: {url} {params.get('term', '')[:60]}")


def queries(path):
    out = []
    for line in open(os.path.join(ROOT, path), encoding="utf-8"):
        m = re.match(r"^\|\s*([A-Za-z]?\d+)\s*\|(.*)$", line)
        if not m or "`" not in line:
            continue
        cells = [c.strip() for c in m.group(2).split("|")]
        q = next((c.strip("`") for c in cells if c.startswith("`") and c.endswith("`")), None)
        nums = [int(c.replace(",", "")) for c in cells if re.fullmatch(r"[\d,]+", c)]
        if q:
            out.append((m.group(1), q, nums[0] if nums else None))
    return out


def main():
    rerun, records = [], {}
    for search, path in LOGS.items():
        for qid, q, logged in queries(path):
            if re.search(r"similar|related|elink", q, re.I):
                rerun.append(dict(search=search, query_id=qid, query=q, logged_hits=logged, rerun_hits="", note="similar-article action: not re-run"))
                continue
            js = json.loads(get("esearch.fcgi", db="pubmed", term=q, retmax=10000, retmode="json",
                                datetype="edat", mindate="1800/01/01", maxdate=MAXDATE))
            ids = js["esearchresult"].get("idlist", [])
            rerun.append(dict(search=search, query_id=qid, query=q, logged_hits=logged, rerun_hits=len(ids),
                              note="" if logged in (None, len(ids)) else "differs from log"))
            for pmid in ids:
                records.setdefault(pmid, set()).add(f"{search}#{qid}")
    with open(os.path.join(HERE, "search_rerun.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rerun[0])); w.writeheader(); w.writerows(rerun)
    # titles, journal and year only (abstracts are not stored in this public repository)
    pmids = sorted(records, key=int)
    meta = {}
    for i in range(0, len(pmids), 200):
        js = json.loads(get("esummary.fcgi", db="pubmed", id=",".join(pmids[i:i + 200]), retmode="json"))
        for p in pmids[i:i + 200]:
            d = js["result"].get(p, {})
            meta[p] = (d.get("title", ""), d.get("source", ""), (d.get("pubdate", "") or "")[:4])
    with open(os.path.join(HERE, "screening_records.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["pmid", "title", "journal", "year", "found_by"])
        for p in pmids:
            w.writerow([p, *meta[p], "; ".join(sorted(records[p]))])
    n_q = sum(1 for r in rerun if r["rerun_hits"] != "")
    same = sum(1 for r in rerun if r["rerun_hits"] != "" and r["logged_hits"] == r["rerun_hits"])
    print(f"{n_q} queries re-run ({same} reproduce the logged hit count exactly); {len(pmids)} unique records")


if __name__ == "__main__":
    main()
