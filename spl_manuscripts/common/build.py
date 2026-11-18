"""
Compile manuscripts: resolve [@Key; @Key2] citations into numbered Vancouver
references (order of first appearance), substitute [@REFLIST], and render .docx
via pandoc. Fails loudly on any citation key not present in the verified or
manual reference tables, so that no unverified reference can slip through.

Usage: python3 build.py path/to/manuscript.md [more.md ...]
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLES = [os.path.join(HERE, "references_verified.md"), os.path.join(HERE, "references_verified_extra.md"), os.path.join(HERE, "references_included_P3P4.md"), os.path.join(HERE, "references_included_P1.md"), os.path.join(HERE, "references_manual.md")]
EXTRA_TABLES = []  # per-paper tables may be appended via --refs


def load_refs(paths):
    refs = {}
    for p in paths:
        if not os.path.exists(p):
            continue
        in_table = False
        for line in open(p, encoding="utf-8"):
            if line.startswith("| key |"):
                in_table = True
                continue
            if in_table and line.startswith("|---"):
                continue
            if in_table and line.startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 4 and re.match(r"^[A-Za-z][\w]*$", cells[0]):
                    key = cells[0]
                    cit = cells[-1]
                    pmid = cells[1]
                    if key in refs:
                        raise SystemExit(f"Duplicate reference key {key} in {p}")
                    refs[key] = (cit, pmid)
            elif in_table and not line.strip():
                in_table = False
    return refs


CITE = re.compile(r"\[(@[A-Za-z][\w]*(?:\s*;\s*@[A-Za-z][\w]*)*)\]")


def compile_md(path, refs):
    text = open(path, encoding="utf-8").read()
    order = []
    missing = set()

    def repl(m):
        keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
        nums = []
        for k in keys:
            if k == "REFLIST":
                return m.group(0)
            if k not in refs:
                missing.add(k)
                continue
            if k not in order:
                order.append(k)
            nums.append(order.index(k) + 1)
        nums = sorted(set(nums))
        # compress ranges
        out, i = [], 0
        while i < len(nums):
            j = i
            while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
                j += 1
            out.append(f"{nums[i]}–{nums[j]}" if j - i >= 2 else (f"{nums[i]},{nums[j]}" if j > i else f"{nums[i]}"))
            i = j + 1
        return "[" + ",".join(out) + "]"

    body = CITE.sub(repl, text)
    if missing:
        raise SystemExit(f"{path}: unresolved citation keys: {sorted(missing)}")
    lines = []
    for i, k in enumerate(order, 1):
        cit, pmid = refs[k]
        pm = f" PMID: {pmid}." if pmid and pmid not in ("—", "-", "") else ""
        lines.append(f"{i}. {cit}{pm}")
    body = body.replace("[@REFLIST]", "\n".join(lines))
    out_md = path.replace(".md", "_compiled.md")
    open(out_md, "w", encoding="utf-8").write(body)
    out_docx = path.replace(".md", ".docx")
    res_path = os.path.dirname(os.path.abspath(path))
    subprocess.run(["pandoc", out_md, "-o", out_docx, "--resource-path", res_path,
                    "-f", "markdown+pipe_tables+superscript+subscript+yaml_metadata_block"], check=True)
    return out_md, out_docx, len(order)


if __name__ == "__main__":
    args = sys.argv[1:]
    extra = []
    if "--refs" in args:
        i = args.index("--refs")
        extra = args[i + 1].split(",")
        args = args[:i] + args[i + 2:]
    refs = load_refs(TABLES + extra)
    for p in args:
        md, dx, n = compile_md(p, refs)
        print(f"OK  {os.path.basename(p)} -> {os.path.basename(dx)}  ({n} references)")
