"""Rule-based safety checks that run BEFORE any LLM call."""
import re

CRISIS = r"\b(suicid\w*|kill(ing)? myself|end(ing)? my life|want to die|self[- ]?harm|hurt(ing)? myself|kill(ing)? my self|(don'?t|do not) want to live)\b"
RED_FLAGS = r"(chest pain|can ?not breathe|can'?t breathe|difficulty breathing|trouble breathing|unconscious|not waking|faint(ed|ing)|seizure|convuls|vomit\w* blood|blood in (the )?(vomit|stool)|heavy bleeding|stroke|poison|overdos|snake ?bite|not breathing|stopped breathing|having (a )?fits|bleeding (heavily|a lot)|slurred speech|face (is )?droop)"
PERSONAL = r"\b(i|i'm|im|me|my|he|she|his|her|we|our|someone|baby|child)\b"
DOSING = r"\b(can (i|we) (take|give)|should (i|we) (take|give)|dose|dosage|how (much|many)\b.*\b(take|give|tablets?|pills?|mg|ml)|how much (paracetamol|ibuprofen|insulin|metformin|medicine|antibiotic)|\d+\s?(mg|ml))\b"
DIAGNOSIS = r"\b(do i have|have i got|diagnose|is (this|it) (cancer|dengue|diabetes|tb)|what (disease|illness) do i have)\b"

MESSAGES = {
 "crisis": "I'm really sorry you are feeling this way. You deserve support right now. In India, call Tele-MANAS on 14416 (free, 24x7) or 112 if you are in immediate danger. Please also tell someone near you and ask them to stay with you. Outside India, call your local emergency number.",
 "emergency": "This may be an emergency. Call 112 (or 108 for an ambulance where available) or go to the nearest hospital now. Do not wait for an online answer.",
 "refused": "I can't diagnose illness or advise medicine doses. Please ask a doctor or pharmacist, who can consider age, weight, other conditions and other medicines. I can share general health information.",
}

def check(text):
    """Return 'crisis', 'emergency', 'refused' or None."""
    t = text.lower().replace("’", "'")
    if re.search(CRISIS, t):
        return "crisis"
    if re.search(RED_FLAGS, t):
        general = re.match(r"\s*(what|which|how|why)\b", t) and not re.search(PERSONAL, t)
        if not general:
            return "emergency"
    if re.search(DOSING, t) or re.search(DIAGNOSIS, t):
        return "refused"
    return None

def redact(text):
    """Remove obvious personal identifiers before text leaves the computer."""
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[email]", text)
    text = re.sub(r"\b\d{4}\s?\d{4}\s?\d{4}\b", "[id-number]", text)
    return re.sub(r"(?<!\d)(\+91[\s-]?)?[6-9]\d{9}(?!\d)", "[phone]", text)
