# HealthLit: Project Report

## 1. Problem
Health information is often hard to read, and general chatbots can state wrong facts confidently.
HealthLit aims to give short answers tied to a named source and to hand risky questions to people.

## 2. Objectives
Explain common conditions simply; cite sources; escalate emergencies; refuse diagnosis and dosing.

## 3. Architecture
    question -> safety rules -> redact identifiers -> TF-IDF retrieval
             -> LLM (grounded prompt) -> citation check -> answer + sources
Any LLM failure or invalid citation falls back to the retrieved passage.

## 4. GenAI / LLM concepts
| Concept | Where |
|---|---|
| Retrieval-augmented generation | retriever.py, assistant.py |
| System prompt and grounding | llm.py |
| Prompt-injection mitigation | question treated as data, `<` escaped |
| Hallucination control | citation check, NOT_FOUND response |
| Guardrails | guardrails.py |
| Privacy | redaction, no request logging |

## 5. Data
12 short passages paraphrased from WHO material on dengue, diabetes, hypertension, diarrhoeal disease
and tuberculosis, with links (collected from search excerpts, November 2026). Glossary written for this project.
Emergency numbers are India-specific (112, 108, Tele-MANAS 14416).

## 6. Evaluation
`python evaluate.py`, offline mode: status accuracy 20/20, top-1 retrieval 11/11.

**These scores are optimistic.** The questions were written alongside the rules, so they are a regression
check, not an independent test. A second round of 13 new questions exposed missed emergencies (e.g.
"not breathing"), missed crisis wording and wrong answers on uncovered diseases. These were fixed and
partly added to the unit tests, so they are no longer unseen either.

The LLM modes were tested only with simulated responses, not with a live model.

## 7. Limitations
- Keyword safety rules WILL miss some wording, spelling mistakes and negations, and can over-trigger.
- The citation check confirms the id exists, not that the sentence matches the source.
- Small knowledge base, English only. A question naming a covered subject may still get an off-target passage.
- Redaction covers emails, phone and 12-digit ID formats, not names or addresses.
- Not reviewed by a clinician. Not for real medical use.

## 8. Future work
Clinician review, embedding retrieval, Indian languages, LLM-based safety classifier, independent
test set, live-model faithfulness evaluation, user study.

## 9. Student contribution
Describe your own changes, experiments and any AI assistance, as your institution requires.
