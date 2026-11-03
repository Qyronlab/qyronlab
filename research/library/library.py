#!/usr/bin/env python3
"""Shared download registry of the two arms. Standard library only; run with `python3 -I`.

  python3 library.py check                       validate downloads.tsv (format, duplicate sha256 / url)
  python3 library.py find <text>                 rows whose url, sha256 or title contain <text>   (run BEFORE downloading)
  python3 library.py add --arm A|B --url URL --file PATH --title "..." [--note "..."]
                                                 sha256 + byte count from the local file, refuses duplicates, appends one row
  python3 library.py add --arm A|B --url URL --fail --bytes N --title "..." --note "what came back"
                                                 record a failed attempt so the other arm does not repeat it
  correction: append a row with status `fix`, the SAME sha256 as the existing ok row and the corrected fields; it is not a
  download and is exempt from the duplicate check (only ok rows are counted). Write it by hand, then run `check`.
Exit code 0 = fine / found, 1 = problem / not found. Rows are append-only; never edit another arm's row, add a `fix` row.
Exception: a placeholder row Arm A entered on Arm B's behalf (note "entered by A from B's channel row") is Arm A's own row and
Arm A completes its `-` fields in place from B's later data, saying so in `note`; git history keeps the earlier state.
"""
import argparse, csv, datetime, hashlib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, "downloads.tsv")
COLS = ["date_utc", "arm", "status", "sha256", "bytes", "url", "title", "note"]
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
CTRL_RE = re.compile(r"[\x00-\x1f\x7f]")


def file_problems():
    """Arm B #146: the file itself is checked before its rows — header, trailing newline, emptiness."""
    raw = open(TSV, "rb").read()
    if not raw:
        return ["file empty: missing header line '" + "\t".join(COLS) + "'"]
    p = []
    first = raw.split(b"\n", 1)[0].decode("utf-8", "replace")
    if first != "\t".join(COLS):
        p.append("header mismatch: expected '" + "\t".join(COLS) + "'")
    if not raw.endswith(b"\n"):
        p.append("file does not end with a newline (an append would glue onto the last row)")
    return p


def load():
    with open(TSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    return rows


def check(rows):
    problems = []
    seen_sha, seen_url, eff = {}, {}, {}
    for i, r in enumerate(rows, start=2):
        if list(r.keys()) != COLS or any(v is None for v in r.values()):
            problems.append(f"line {i}: wrong column count")
            continue
        empties = [c for c in COLS if r[c] == ""]       # Arm B #140: only '-' means "not given"; an empty field is an error
        if empties:
            problems.append(f"line {i}: empty field(s) {empties}; use '-' for a field not given")
        ctrl = [c for c in COLS if CTRL_RE.search(r[c])]
        if ctrl:
            problems.append(f"line {i}: control character in field(s) {ctrl}")
        if r["arm"] not in ("A", "B"):
            problems.append(f"line {i}: arm must be A or B")
        if r["status"] not in ("ok", "fail", "fix"):
            problems.append(f"line {i}: status must be ok, fail or fix")
        if r["status"] in ("ok", "fix") and not SHA_RE.match(r["sha256"]):
            problems.append(f"line {i}: {r['status']} row needs a 64-hex sha256")
        if r["bytes"] != "-" and not (r["bytes"].isdigit() and int(r["bytes"]) > 0):   # Arm B #134: bytes must be a count
            problems.append(f"line {i}: bytes must be a positive integer or '-'")
        if r["status"] == "fix":                        # Arm B #131: a fix must bind to an EARLIER ok row with the same sha256
            if r["sha256"] not in seen_sha:
                problems.append(f"line {i}: fix row has no earlier ok row with this sha256")
            else:
                cur = eff[r["sha256"]]                  # Arm B #134/#137: EVERY given fix field must differ from the effective row
                given = [c for c in ("bytes", "url", "title") if r[c] != "-"]
                same = [c for c in given if r[c] == cur[c]]
                if not given:
                    problems.append(f"line {i}: fix row gives no field to correct (bytes, url, title all '-')")
                for c in same:
                    problems.append(f"line {i}: fix field '{c}' repeats the effective value (line {seen_sha[r['sha256']]})")
                for c in given:
                    cur[c] = r[c]
        if r["status"] == "ok":
            if r["sha256"] in seen_sha:
                problems.append(f"line {i}: duplicate sha256 (first on line {seen_sha[r['sha256']]})")
            seen_sha.setdefault(r["sha256"], i)
            eff.setdefault(r["sha256"], dict(r))
    # Arm B #134: url uniqueness is checked on the EFFECTIVE view (after fixes), not only on the raw ok rows
    for sha, e in eff.items():
        if e["url"] != "-":
            if e["url"] in seen_url:
                problems.append(f"effective url duplicate: line {seen_sha[sha]} and line {seen_url[e['url']]} resolve to the same url")
            seen_url.setdefault(e["url"], seen_sha[sha])
    return problems


def effective(rows):
    """The effective view: each ok row with its later fix rows applied (a fix field that is not '-' overrides);
    fail rows pass through. Fix rows themselves are not listed; the note says which lines were applied."""
    out, by_sha = [], {}
    for i, r in enumerate(rows, start=2):
        if r["status"] == "ok":
            e = dict(r); e["_line"] = i; e["_fixes"] = []
            by_sha[r["sha256"]] = e; out.append(e)
        elif r["status"] == "fix" and r["sha256"] in by_sha:
            e = by_sha[r["sha256"]]
            for c in ("bytes", "url", "title"):
                if r[c] != "-":
                    e[c] = r[c]
            e["_fixes"].append(i)
            e["note"] = e["note"] + f" | fix line {i} ({r['arm']}): {r['note']}"
        elif r["status"] == "fail":
            e = dict(r); e["_line"] = i; e["_fixes"] = []; out.append(e)
    return out


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("cmd", choices=["check", "find", "add"])
    ap.add_argument("text", nargs="?")
    ap.add_argument("--arm"); ap.add_argument("--url"); ap.add_argument("--file"); ap.add_argument("--title")
    ap.add_argument("--note", default=""); ap.add_argument("--fail", action="store_true"); ap.add_argument("--bytes")
    ap.add_argument("--raw", action="store_true", help="find: print raw rows (ok, fail and fix) instead of the effective view")
    a = ap.parse_args()
    fp = file_problems()
    rows = load() if not fp else []
    if fp and a.cmd != "check":
        print(f"registry file invalid, {a.cmd} refused:"); print("\n".join(fp)); sys.exit(1)
    if a.cmd == "add" and check(rows):               # Arm B #143: no append onto an already invalid registry
        print("registry invalid, add refused:"); print("\n".join(check(rows))); sys.exit(1)
    if a.cmd == "check":
        p = fp + check(rows)
        print("\n".join(p) if p else f"ok: {len(rows)} rows, no duplicate sha256/url, every fix bound to an earlier ok row")
        sys.exit(1 if p else 0)
    if a.cmd == "find":
        p = check(rows)                              # Arm B #143: find must refuse an invalid registry, not apply its bad rows
        if p:
            print("registry invalid, find refused:"); print("\n".join(p)); sys.exit(1)
        t = (a.text or "").lower()
        pool = rows if a.raw else effective(rows)
        hits = [r for r in pool if t and (t in r["url"].lower() or t in r["sha256"] or t in r["title"].lower())]
        for r in hits:
            tag = "" if a.raw else f"\t[effective; line {r['_line']}" + (f", fixes applied: {r['_fixes']}" if r["_fixes"] else "") + "]"
            print("\t".join(r[c] for c in COLS) + tag)
        if not hits:
            print("not in library")
        sys.exit(0 if hits else 1)
    # add
    if not (a.arm in ("A", "B") and a.url and a.title):
        sys.exit("add needs --arm A|B --url --title and either --file or --fail --bytes")
    if a.fail:
        sha, n, status = "-", a.bytes or "-", "fail"
    else:
        if not a.file:
            sys.exit("add needs --file (or --fail)")
        data = open(a.file, "rb").read()
        sha, n, status = hashlib.sha256(data).hexdigest(), str(len(data)), "ok"
        dup = [r for r in rows if r["sha256"] == sha or (r["status"] == "ok" and r["url"] == a.url)]
        if dup:
            print("already in library:"); [print("\t".join(r[c] for c in COLS)) for r in dup]; sys.exit(1)
    row = {"date_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"), "arm": a.arm, "status": status,
           "sha256": sha, "bytes": n, "url": a.url, "title": a.title, "note": a.note or "-"}
    for c in COLS:
        if CTRL_RE.search(row[c]):                   # Arm B #149: CR (and any other control character) refused before writing
            sys.exit(f"refused, nothing written: field {c} contains a control character (tab, CR, LF, ...)")
    p = check(rows + [row])                          # Arm B #143: validate the candidate on the effective view BEFORE writing
    if p:
        print("refused, nothing written:"); print("\n".join(p)); sys.exit(1)
    import fcntl                                     # Arm B #147/#149: one writer at a time on this host
    with open(TSV, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        if file_problems() or check(load() + [row]):   # re-check under the lock: another writer may have appended meanwhile
            sys.exit("refused, nothing written: registry changed under the lock, rerun add")
        f.write("\t".join(row[c] for c in COLS) + "\n")
        f.flush()
        fcntl.flock(f, fcntl.LOCK_UN)
    p = check(load())
    print("\n".join(p) if p else "added:\n" + "\t".join(row[c] for c in COLS))
    sys.exit(1 if p else 0)


if __name__ == "__main__":
    main()
