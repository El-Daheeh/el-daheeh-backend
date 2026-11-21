"""
El-Daheeh Backend — باك إند الدحيح
==================================
Tiny HTTP server (Python standard library ONLY — no installs) that
connects the El-Daheeh demo website's chat to the real model router
(router.py in this same folder). The website used to answer with
canned keyword replies; now POST /chat classifies the student's
message and calls router.route() — a REAL free model answers.

Run:
    python3 server.py            # listens on http://localhost:8791

Endpoints:
    GET  /health  -> {"ok": true}
    POST /chat    -> body {"message": "..."}
                     returns {"agent": "...", "model": "...", "text": "..."}

CORS is wide open (Access-Control-Allow-Origin: *) so the static
demo page can call it from any origin during local testing.

NOTE: API keys are never handled here — router.py calls the
connector helpers, which read keys from the Secure Vault.
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import router  # noqa: E402  (the real model router, same folder)

PORT = 8791

SYSTEM = ("أنت وكيل متخصص في منصة «الدحيح» التعليمية. رد بالعربية الواضحة "
          "وبشكل عملي ومباشر، ونفّذ طلب الطالب كاملًا (لو طلب عددًا معينًا "
          "من الأسئلة أو الخطوات فالتزم بالعدد). "
          "سياق المنصة الحالي: الطالب يدرس مقرر مستودعات البيانات "
          "(Data Warehousing) — معمارية Medallion بطبقات Bronze وSilver "
          "وGold، والـ Star Schema، وPower BI. كلمات Bronze وSilver وGold "
          "في كلامه يقصد بها طبقات Medallion وليس المعادن، و«الأسئلة» يقصد "
          "بها أسئلة الكويز عن هذه المواضيع، ما لم يقل صراحة غير ذلك. "
          "لو طلب خطة مذاكرة دون تفاصيل كافية، ابنِ خطة افتراضية عملية "
          "واذكر افتراضاتك، بدل أن تكتفي بطلب معلومات.")

# ------------------------------------------------------------ classify
# Rules mirror the website's agents. ORDER MATTERS: explain first.
RULES: list[tuple[tuple[str, ...], str, str]] = [
    (("اشرح", "يعني إيه", "يعني ايه", "وضح", "مش فاهم"), "explain", "💡 [وكيل الشرح والفهم]"),
    (("أسئلة", "اسئلة", "سؤال", "كويز", "امتحان"), "quiz", "❓ [وكيل مولِّد الأسئلة]"),
    (("كود", "sql", "استعلام"), "code", "💻 [وكيل الكود]"),
    (("لخص", "ملخص", "تلخيص"), "summarize", "📝 [وكيل الملخِّص]"),
    (("خطة", "جدول"), "plan", "📅 [وكيل مخطط المذاكرة]"),
]
DEFAULT = ("chat", "🤖 [راوتر الدحيح]")


def classify(message: str) -> tuple[str, str]:
    t = message.lower()
    for keywords, task, agent in RULES:
        if any(k in t for k in keywords):
            return task, agent
    return DEFAULT


# -------------------------------------------------------------- server

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # CORS preflight from the browser
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        if self.path.rstrip("/") in ("/health", ""):
            self._json(200, {"ok": True, "service": "el-daheeh-backend"})
        else:
            self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/chat":
            self._json(404, {"ok": False, "error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
            message = str(data.get("message", "")).strip()
        except Exception as e:
            self._json(400, {"ok": False, "error": f"bad request: {e}"})
            return
        if not message:
            self._json(400, {"ok": False, "error": "empty message"})
            return

        task, agent = classify(message)
        res = router.route(task, message, system=SYSTEM)
        if not res.get("ok"):
            self._json(502, {"ok": False, "agent": agent, "task": task,
                             "errors": res.get("errors", ["router failed"])})
            return
        self._json(200, {"ok": True, "agent": agent, "task": task,
                         "model": res.get("model", ""),
                         "text": res.get("text", "")})

    def log_message(self, fmt, *args):  # keep the console readable
        sys.stderr.write("[backend] %s\n" % (fmt % args))


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"El-Daheeh backend on http://localhost:{PORT}  "
          f"(GET /health, POST /chat)")
    srv.serve_forever()
