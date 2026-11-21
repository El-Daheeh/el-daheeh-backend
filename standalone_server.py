#!/usr/bin/env python3
"""El-Daheeh standalone backend — runs ANYWHERE (laptop, Render, HF Spaces...).

Reads API keys from environment variables (never hardcode keys here):
  GEMINI_API_KEY      - Google AI Studio key (base model: explanation)
  GROQ_API_KEY        - Groq key (fast quizzes)
  OPENROUTER_API_KEY  - OpenRouter key (code + planning, free models)

Run:
  PORT=8791 python3 standalone_server.py
Endpoints:
  GET  /health  -> {"ok": true, "service": "el-daheeh-backend-standalone"}
  POST /chat    -> {"message": "..."}  returns {"agent", "model", "text"}

Routing mirrors the Muse-side router: intent is classified in Arabic/English,
explain goes to Gemini, quiz to Groq, code/plan to OpenRouter, with a fallback
chain across whichever providers have keys configured.
"""
import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SYSTEM = (
    "You are a study agent inside El-Daheeh (StudyLeague), an Arabic study-competition "
    "platform for university students. The current course context is Data Warehousing: "
    "Medallion architecture (Bronze = raw data as-is, Silver = cleaned/modelled, "
    "Gold = star schema for reporting/Power BI). 'gold/silver/bronze' in user messages "
    "refer to these layers, NOT metals. Answer in Arabic unless asked otherwise. "
    "Be concrete and complete: if asked for N questions, produce exactly N questions."
)

KEYS = {
    "gemini": os.environ.get("GEMINI_API_KEY", ""),
    "groq": os.environ.get("GROQ_API_KEY", ""),
    "openrouter": os.environ.get("OPENROUTER_API_KEY", ""),
}


def call_gemini(prompt):
    body = json.dumps({
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"parts": [{"text": prompt}]}],
    }).encode()
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent",
        data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("x-goog-api-key", KEYS["gemini"])
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode())
    return "Gemini (gemini-3.5-flash-lite)", data["candidates"][0]["content"]["parts"][0]["text"]


def call_openai_style(url, key, model, prompt, ua=False):
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
    }).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {key}")
    if ua:
        req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) ElDaheehStandalone/1.0")
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode())
    return data.get("model", model), data["choices"][0]["message"]["content"]


def call_groq(prompt):
    return call_openai_style("https://api.groq.com/openai/v1/chat/completions",
                             KEYS["groq"], "openai/gpt-oss-120b", prompt, ua=True)


def call_openrouter(prompt):
    return call_openai_style("https://openrouter.ai/api/v1/chat/completions",
                             KEYS["openrouter"], "openrouter/free", prompt, ua=True)


PROVIDERS = {"gemini": call_gemini, "groq": call_groq, "openrouter": call_openrouter}

# task -> (agent label, provider preference order)
ROUTES = {
    "explain":   ("وكيل الشرح والفهم", ["gemini", "groq", "openrouter"]),
    "quiz":      ("وكيل مولّد الأسئلة", ["groq", "gemini", "openrouter"]),
    "code":      ("وكيل الكود", ["openrouter", "groq", "gemini"]),
    "plan":      ("وكيل مخطط المذاكرة", ["openrouter", "gemini", "groq"]),
    "summarize": ("وكيل التلخيص", ["gemini", "openrouter", "groq"]),
    "chat":      ("وكيل المحادثة", ["gemini", "groq", "openrouter"]),
}


def classify(text):
    t = text.lower()
    if any(w in t for w in ["اشرح", "يعني ايه", "يعني إيه", "وضح", "مش فاهم", "explain"]):
        return "explain"
    if any(w in t for w in ["أسئلة", "اسئلة", "كويز", "quiz", "اختبار"]):
        return "quiz"
    if any(w in t for w in ["كود", "sql", "code", "برمج"]):
        return "code"
    if any(w in t for w in ["لخص", "ملخص", "summarize", "summary"]):
        return "summarize"
    if any(w in t for w in ["خطة", "جدول", "plan", "مذاكرة"]):
        return "plan"
    return "chat"


def route(message):
    task = classify(message)
    agent, order = ROUTES[task]
    errors = []
    for name in order:
        if not KEYS.get(name):
            continue
        try:
            model, text = PROVIDERS[name](message)
            return {"agent": agent, "model": f"{name}: {model}", "text": text}
        except Exception as exc:  # keep trying the fallback chain
            errors.append(f"{name}: {exc}")
    raise RuntimeError("No provider succeeded. " + " | ".join(errors) if errors
                       else "No API keys configured — set GEMINI_API_KEY / GROQ_API_KEY / OPENROUTER_API_KEY.")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path.rstrip("/") in ("/health", ""):
            configured = [k for k, v in KEYS.items() if v]
            self._send(200, {"ok": True, "service": "el-daheeh-backend-standalone",
                             "providers_configured": configured})
        else:
            self._send(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        if self.path.rstrip("/") != "/chat":
            self._send(404, {"ok": False, "error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode() or "{}")
            message = (data.get("message") or "").strip()
            if not message:
                self._send(400, {"ok": False, "error": "message is required"})
                return
            self._send(200, {"ok": True, **route(message)})
        except Exception as exc:
            self._send(502, {"ok": False, "error": str(exc)[:400]})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8791"))
    print(f"El-Daheeh standalone backend on :{port} — providers: "
          f"{[k for k, v in KEYS.items() if v] or 'NONE (set API keys!)'}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
