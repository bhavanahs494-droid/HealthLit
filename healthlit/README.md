# HealthLit: plain-language health information assistant

Student prototype using retrieval-augmented generation (RAG). Not a medical device.

## How to run (step by step)

**1. Install Python 3.9 or newer** from https://www.python.org/downloads/
(on Windows, tick "Add Python to PATH").

**2. Unzip** `healthlit.zip`.

**3. Open a terminal in the `healthlit` folder** (the one containing `app.py`).
- Windows: open the folder, type `cmd` in the address bar, press Enter.
- Mac/Linux: open Terminal and `cd` to the folder.

**4. Check Python.** Windows: `python --version`. Mac/Linux: `python3 --version`.
Use whichever works in the commands below.

**5. Start the app:** `python app.py`

**6. Open** http://127.0.0.1:8000 in a browser.

**7. Try:**
- `What are the warning signs of severe dengue?`
- `What dose of insulin should I take?` (refused)
- `I have chest pain` (emergency message)
- Paste `Patient has hypertension and pyrexia.` and click **Explain medical words**

**8. Stop** with Ctrl+C.

**9. Test and evaluate:**

    python -m unittest discover -s tests -t .
    python evaluate.py

No `pip install` is needed.

## Turn on the LLM (needed to demonstrate generation)

The default **offline mode uses no LLM**: it quotes the best matching passage.

### Option A: Ollama (free, runs on your computer)
Install from https://ollama.com, then run `ollama pull llama3.2`. In the project terminal:

- Windows (cmd): `set HEALTHLIT_PROVIDER=ollama` then `python app.py`
- Windows (PowerShell): `$env:HEALTHLIT_PROVIDER="ollama"` then `python app.py`
- Mac/Linux: `HEALTHLIT_PROVIDER=ollama python3 app.py`

### Option B: Anthropic API (paid, needs a key)
Set `HEALTHLIT_PROVIDER=anthropic` and `ANTHROPIC_API_KEY=your-key` the same way, then start the app.
Never put the key in the code. Optional: `HEALTHLIT_MODEL` changes the model.

Under each answer, **Mode** shows `ollama` or `anthropic` when the LLM wrote it.
`offline fallback` means the call or the citation check failed.

## Problems
| Problem | Fix |
|---|---|
| `python` not found | Use `python3` or `py`, or reinstall with PATH ticked |
| `can't open file app.py` | You are in the wrong folder |
| Port already in use | Set `PORT=8080` and open port 8080 |
| `offline fallback (URLError)` | Start Ollama, or check your internet connection |

## Files
    app.py              web server
    healthlit/          guardrails, retriever, LLM client, pipeline
    data/               knowledge base, glossary, evaluation questions
    web/index.html      user interface
    tests/, evaluate.py
    docs/REPORT.md      project report
