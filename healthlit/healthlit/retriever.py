"""TF-IDF retrieval (the 'R' in RAG), standard library only."""
import json, math, re
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
STOP = set("a an and are as at be by can do does for from have how i if in is it my of on or so the to what when which who with you your me should get has common".split())
SYNONYMS = {"tb": "tuberculosis", "sugar": "diabetes", "bp": "pressure", "diarrhea": "diarrhoea",
            "cure": "curable", "cured": "curable", "avoid": "prevent", "prevention": "prevent",
            "signs": "symptom", "treated": "treatment", "treat": "treatment"}

def tokenize(text):
    out = []
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        if w in STOP:
            continue
        w = SYNONYMS.get(w, w)
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(SYNONYMS.get(w, w))
    return out

# A question must name a covered subject, otherwise generic words ("symptoms") cause wrong matches.
SUBJECTS = set(tokenize("dengue mosquito diabetes hypertension blood pressure diarrhoea ORS dehydration tuberculosis"))

class Retriever:
    def __init__(self, path=DATA / "knowledge.json"):
        self.docs = json.loads(Path(path).read_text(encoding="utf-8"))
        # Topic words are repeated so that they weigh more than body words.
        toks = [tokenize((d["topic"] + " ") * 2 + d["text"]) for d in self.docs]
        df = Counter(t for ts in toks for t in set(ts))
        self.idf = {t: math.log((1 + len(toks)) / (1 + n)) + 1 for t, n in df.items()}
        self.vectors = [self._vector(ts) for ts in toks]

    def _vector(self, tokens):
        # Unknown words get a high weight, which lowers scores for off-topic questions.
        v = {t: c * self.idf.get(t, 3.0) for t, c in Counter(tokens).items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1
        return {t: x / norm for t, x in v.items()}

    def search(self, query, k=3, min_score=0.15):
        words = tokenize(query)
        if not SUBJECTS & set(words):
            return []
        q = self._vector(words)
        scored = [(sum(w * v.get(t, 0) for t, w in q.items()), d) for v, d in zip(self.vectors, self.docs)]
        scored.sort(key=lambda x: -x[0])
        return [dict(d, score=round(s, 3)) for s, d in scored[:k] if s >= min_score]
