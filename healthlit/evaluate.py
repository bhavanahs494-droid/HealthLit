"""Run: python evaluate.py  (uses offline mode so results are repeatable)."""
import json, os
os.environ["HEALTHLIT_PROVIDER"] = "offline"
from healthlit.assistant import ask
from healthlit.retriever import DATA

cases = json.loads((DATA / "eval.json").read_text(encoding="utf-8"))
status_ok = doc_ok = doc_total = 0
fails = []
for c in cases:
    r = ask(c["q"])
    ok = r["status"] == c["status"]
    status_ok += ok
    if "doc" in c:
        doc_total += 1
        hit = bool(r["sources"]) and r["sources"][0]["id"] == c["doc"]
        doc_ok += hit
        ok = ok and hit
    if not ok:
        fails.append(f"{c['q']} -> {r['status']} {[s['id'] for s in r['sources']]}")
print(f"Status accuracy : {status_ok}/{len(cases)}")
print(f"Top-1 retrieval : {doc_ok}/{doc_total}")
print("Failures        :", fails or "none")
