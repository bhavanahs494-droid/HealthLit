"""Pipeline: guardrails -> retrieval -> generation -> citation check."""
import json, re
from . import guardrails, llm
from .retriever import Retriever, DATA

retriever = Retriever()
GLOSSARY = json.loads((DATA / "glossary.json").read_text(encoding="utf-8"))
DISCLAIMER = "General information only, not medical advice."

def _result(status, answer, docs=(), mode="rules"):
    sources = [{k: d[k] for k in ("id", "topic", "source", "url")} for d in docs]
    return {"status": status, "answer": answer, "sources": sources, "mode": mode, "disclaimer": DISCLAIMER}

def cited_correctly(text, docs):
    """True only if there is a citation and every citation is a retrieved source."""
    cited = re.findall(r"\[([a-z]+-\d+)\]", text)
    return bool(cited) and set(cited) <= {d["id"] for d in docs}

def ask(question):
    question = (question or "").strip()[:1000]
    if not question:
        return _result("no_information", "Please type a health question.")
    if any(c.isalpha() and ord(c) > 591 for c in question):
        return _result("no_information", "Sorry, only English is supported. In an emergency, call 112.")
    flag = guardrails.check(question)
    if flag:
        return _result(flag, guardrails.MESSAGES[flag])
    docs = retriever.search(guardrails.redact(question))
    if not docs:
        return _result("no_information", "I don't have trusted information on that. I cover dengue, diabetes, blood pressure, diarrhoea and tuberculosis. Please ask a health worker.")
    top = docs[0]
    extract = f"{top['text']} [{top['id']}]"
    if llm.provider() == "offline":
        return _result("answered", extract, [top], "offline (quoted from knowledge base)")
    try:
        text = llm.generate(llm.build_prompt(guardrails.redact(question), docs)).strip()
    except Exception as e:  # network, key or response-format problems
        return _result("answered", extract, [top], f"offline fallback ({type(e).__name__})")
    if text == "NOT_FOUND":
        return _result("no_information", "The trusted sources do not answer this. Please ask a health worker.", mode=llm.provider())
    if not cited_correctly(text, docs):
        return _result("answered", extract, [top], "offline fallback (citation check failed)")
    used = [d for d in docs if f"[{d['id']}]" in text]
    return _result("answered", text, used, llm.provider())

def simplify(text):
    """Rule-based plain-language helper for medical terms. Sends nothing anywhere."""
    text = (text or "")[:4000]
    flag = guardrails.check(text)
    if flag in ("crisis", "emergency"):
        return _result(flag, guardrails.MESSAGES[flag])
    terms = sorted(GLOSSARY, key=len, reverse=True)
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, terms)) + r")\b", re.I)
    found = []
    def explain(m):
        found.append(m.group(0).lower())
        return f"{m.group(0)} ({GLOSSARY[m.group(0).lower()]})"
    out = pattern.sub(explain, text)
    result = _result("answered" if found else "no_information",
                     out if found else "No terms from the glossary were found.", mode="glossary")
    result["terms"] = sorted(set(found))
    return result
