import json
import os
import re
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from groq import Groq
except ImportError:
    Groq = None

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_PATH = BASE_DIR / "data" / "knowledge_base.json"
PROJECTS_PATH = BASE_DIR / "data" / "projects.json"

# Keep the API configuration in ONE place. For public deployment, set GROQ_API_KEY
# as a server environment variable and never expose it to browser JavaScript.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
client = Groq(api_key=GROQ_API_KEY) if Groq and GROQ_API_KEY else None

SYSTEM_PROMPT = """
You are Electronics Assistant, an educational AI for students studying Electronics,
ECE subjects, Arduino & IoT, and Computer Software.

IMPORTANT RESPONSE STYLE:
Advanced Mode should be more intelligent and technically capable than Basic Mode,
but it MUST keep the same clean, simple, student-friendly presentation style.
Do NOT write textbook chapters, long essays, or unnecessarily elaborate guides.
Give the answer directly first, then explain only what is useful.

Formatting rules:
- Return HTML only because the website inserts your answer directly into the chat.
- Use <strong> for important words/headings and <br> for line breaks.
- Use short bullet lists with <ul><li>...</li></ul> when useful.
- Use <code>...</code> for short code, formulas, variables, or commands.
- For longer code, use <pre><code>...</code></pre>.
- Do NOT use Markdown headings (#), Markdown tables, LaTeX delimiters, or Markdown
  bold/italic syntax.
- Avoid giant sections such as 'Summary Checklist' unless the user asks for a detailed
  explanation.
- Normally keep an answer around 80-250 words. Go longer only when the problem truly
  requires calculations, debugging, derivation, or step-by-step reasoning.
- Prefer this natural structure when appropriate:
  <strong>Answer</strong><br>Direct answer.<br><br>
  <strong>Why / How</strong><br>Short explanation.<br><br>
  <strong>Example</strong><br>Simple example.<br><br>
  <strong>Key point</strong><br>One useful takeaway.
- For a numerical: show <strong>Formula</strong>, <strong>Substitution</strong>, and
  <strong>Answer</strong> with units, without unnecessary theory.
- For code debugging: show <strong>Problem</strong>, <strong>Corrected Code</strong>,
  and <strong>Why</strong>. Keep the explanation focused.
- For hardware troubleshooting: show <strong>Likely causes</strong> and
  <strong>What to check</strong>. Do not pretend to see a circuit or wiring that was not
  provided.
- If the user asks a simple definition, answer simply even in Advanced Mode. Advanced
  Mode means deeper capability, not automatically a longer answer.
- If the user asks for a deep topic, increase technical depth while preserving the
  same clean, readable style.
- If a supplied knowledge-base context is relevant, prefer it and expand on it.
- The three main domains are Electronics, Arduino & IoT, and Computer Software.

Examples of the desired style:
Simple concept:
<strong>What is a transistor?</strong><br>A transistor is a semiconductor device used
mainly for switching and amplification.<br><br><strong>In simple terms:</strong><br>It can
control a larger current using a smaller input signal.<br><br><strong>Common uses:</strong>
<ul><li>Switching</li><li>Amplification</li><li>Signal processing</li></ul>

Numerical:
<strong>Given:</strong> V = 10 V, R = 2 kΩ<br><br><strong>Formula:</strong> I = V / R<br>
<strong>Substitution:</strong> I = 10 / 2000<br><strong>Answer:</strong> I = 5 mA

The response should feel like a helpful engineering tutor, not a generated textbook.
"""


def load_json(path: Path, fallback):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return fallback


def load_knowledge():
    return load_json(KNOWLEDGE_PATH, {"knowledge": []})


def normalize(text):
    text = (text or "").lower()
    return re.sub(r"[^a-z0-9+.#\-*/= ]+", " ", text).strip()


def tokenize(text):
    return set(re.findall(r"[a-z0-9+#.]+", normalize(text)))


def search_knowledge(query, limit=4):
    data = load_knowledge()
    q = normalize(query)
    q_tokens = tokenize(query)
    scored = []
    for item in data.get("knowledge", []):
        haystack = normalize(" ".join([
            item.get("question", ""),
            " ".join(item.get("keywords", [])),
            item.get("answer", ""),
            item.get("topic", ""),
            item.get("subcategory", ""),
        ]))
        score = 0
        if q and q in haystack:
            score += 10
        for token in q_tokens:
            if token in haystack.split():
                score += 2
            elif token in haystack:
                score += 1
        if normalize(item.get("question", "")) == q:
            score += 15
        if score:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for score, item in scored[:limit] if score >= 2]


def basic_answer(query):
    q = normalize(query)
    if not q:
        return "Please enter a question."
    if q in {"hi", "hello", "hey", "hai"} or q.startswith(("hi ", "hello ", "hey ")):
        return "Hello! I’m Electronics Assistant. Ask me about Electronics, Arduino & IoT, Computer Software, ECE numericals, projects, or troubleshooting."
    if q in {"bye", "goodbye", "exit", "quit"}:
        return "Goodbye! Come back whenever you want to learn or build something."

    calc = solve_common_calculation(query)
    if calc:
        return calc

    matches = search_knowledge(query)
    if matches:
        parts = []
        for item in matches[:3]:
            title = item.get("question") or item.get("topic") or "Answer"
            answer = item.get("answer", "")
            related = item.get("related_topics", [])
            block = f"<strong>{title}</strong><br>{answer}"
            if related:
                block += "<br><br><strong>Related:</strong> " + ", ".join(related[:5])
            parts.append(block)
        return "<br><br>".join(parts)

    return ("I couldn’t find a close match in the Basic Mode knowledge base. "
            "Try a clearer question or switch to <strong>Advanced Mode</strong> for a deeper AI answer.")


def solve_common_calculation(query):
    q = normalize(query)
    # Ohm's law from any two of V, I, R.
    patterns = {
        "voltage": r"(?:v|voltage)\s*=\s*([0-9.]+)\s*(m|k)?\s*(?:a|amp|amps|ampere)\s*[x*]\s*([0-9.]+)\s*(m|k)?\s*(?:ohm|Ω|r)",
    }
    m = re.search(r"(?:v|voltage)\s*=?\s*([0-9.]+)\s*(mv|v)\b.*?(?:i|current)\s*=?\s*([0-9.]+)\s*(ma|a)\b", q)
    if m:
        v = float(m.group(1)) * (0.001 if m.group(2) == "mv" else 1)
        i = float(m.group(3)) * (0.001 if m.group(4) == "ma" else 1)
        if i:
            r = v / i
            return f"<strong>Ohm’s Law</strong><br>R = V / I<br>R = {v:g} / {i:g}<br><strong>R = {r:g} Ω</strong>"
    m = re.search(r"(?:i|current)\s*=?\s*([0-9.]+)\s*(ma|a)\b.*?(?:r|resistance)\s*=?\s*([0-9.]+)\s*(k|m|ohm|ohms)?", q)
    if m:
        i = float(m.group(1)) * (0.001 if m.group(2) == "ma" else 1)
        r = float(m.group(3)) * ({"k": 1000, "m": 1e6}.get(m.group(4), 1) if m.group(4) else 1)
        return f"<strong>Ohm’s Law</strong><br>V = I × R<br>V = {i:g} × {r:g}<br><strong>V = {i*r:g} V</strong>"
    m = re.search(r"(?:v|voltage)\s*=?\s*([0-9.]+)\s*(mv|v)\b.*?(?:r|resistance)\s*=?\s*([0-9.]+)\s*(k|m|ohm|ohms)?", q)
    if m:
        v = float(m.group(1)) * (0.001 if m.group(2) == "mv" else 1)
        r = float(m.group(3)) * ({"k": 1000, "m": 1e6}.get(m.group(4), 1) if m.group(4) else 1)
        if r:
            return f"<strong>Ohm’s Law</strong><br>I = V / R<br>I = {v:g} / {r:g}<br><strong>I = {v/r:g} A</strong>"
    return None


def build_context(query, page_context=""):
    matches = search_knowledge(query, limit=5)
    snippets = []
    for item in matches:
        snippets.append(
            f"Q: {item.get('question','')}\nA: {item.get('answer','')}\n"
            f"Category: {item.get('category','')} / {item.get('subcategory','')} / {item.get('level','')}"
        )
    return "\n\n".join(snippets) + (f"\n\nCurrent page/context: {page_context}" if page_context else "")


def ask_groq(user_question, page_context="", chat_history=None):
    if not user_question or not user_question.strip():
        return "Please enter a question."
    if client is None:
        return ("Advanced AI is not configured on this server. Set GROQ_API_KEY on the server "
                "and restart Electronics Assistant. Basic Mode is still available.")

    context = build_context(user_question, page_context)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        messages.append({"role": "system", "content": "Relevant Electronics Assistant knowledge:\n" + context})
    if chat_history:
        for item in chat_history[-8:]:
            role = "assistant" if item.get("role") == "assistant" else "user"
            content = str(item.get("content", ""))[:3000]
            if content:
                messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_question.strip()})

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.35,
        max_tokens=1200,
    )
    answer = response.choices[0].message.content
    return str(answer) if answer is not None else "Sorry, I could not generate an answer."
