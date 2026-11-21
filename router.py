"""
El-Daheeh Model Router v2 — راوتر الدحيح
=========================================
One router agent in front of every free model Weza connected on
2026-11-21. Calls go through the connector helpers in
~/workspace/custom-connectors/*/bin/chat.py (keys live in the Secure
Vault; this file never sees a key).

Weza's routing decisions (2026-11-21):
  - Gemini  = the base (he has Gemini Pro)
  - ChatGPT = explanation  -> NOT connected yet (paid API); Gemini
    covers explanation until then. Marked PENDING below.
  - DeepSeek = quizzes + code -> no free DeepSeek variant exists on
    OpenRouter right now; Qwen/GPT-OSS cover quizzes+code until a
    direct DeepSeek key is added. Marked PENDING below.

Everything else was pulled live from the providers' own model lists
on 2026-11-21/22 — "take every model you can get" (Weza).
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

CONNECTORS = Path.home() / "workspace/custom-connectors"


@dataclass
class Model:
    display: str
    provider: str          # connector folder suffix
    model_id: str          # exact id the provider expects
    strengths: tuple[str, ...]
    note: str = ""

    @property
    def helper(self) -> Path:
        return CONNECTORS / f"custom.{self.provider}" / "bin" / "chat.py"


# ------------------------------------------------- registry (all free)
MODELS: list[Model] = [
    # Google Gemini — the base
    Model("Gemini Flash Lite", "google-gemini", "gemini-3.5-flash-lite",
          ("base", "explain", "summarize", "plan", "chat"), "base model, verified live"),
    # Groq — fast open models
    Model("GPT-OSS 120B (Groq)", "groq", "openai/gpt-oss-120b",
          ("quiz", "chat"), "verified live — made a correct Arabic MCQ"),
    Model("GPT-OSS 20B (Groq)", "groq", "openai/gpt-oss-20b",
          ("chat", "quiz"), "smaller/faster sibling"),
    Model("Qwen 3.8 27B (Groq)", "groq", "qwen/qwen3.8-27b",
          ("quiz", "code"), "stands in for DeepSeek on quizzes+code for now"),
    Model("ALLAM 2 7B (Groq)", "groq", "allam-2-7b",
          ("arabic", "chat"), "Arabic-first model"),
    # OpenRouter — one key, many free models
    Model("Nemotron 3 Ultra 550B (OR)", "openrouter", "nvidia/nemotron-3-ultra-550b-a55b:free",
          ("reasoning", "code"), "biggest free reasoner on the list"),
    Model("Nemotron Nano Reasoning (OR)", "openrouter", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
          ("reasoning", "quiz")),
    Model("Gemma 4 31B (OR)", "openrouter", "google/gemma-4-31b-it:free",
          ("explain", "summarize")),
    Model("Gemma 4 26B (OR)", "openrouter", "google/gemma-4-26b-a4b-it:free",
          ("chat", "explain")),
    Model("Ling 3.2 Flash (OR)", "openrouter", "inclusionai/ling-3.2-flash:free",
          ("chat", "summarize")),
    Model("ERNIE 5.5 Flash (OR)", "openrouter", "baidu/ernie-5.5-flash-preview:free",
          ("chat",)),
    Model("OpenRouter Auto-Free", "openrouter", "openrouter/free",
          ("chat",), "auto-picks a free model; verified $0"),
    # Added from the live Models-page catalogue (checked 2026-11-22 ~00:03 EET)
    Model("Nemotron 3.5 Super VL (OR)", "openrouter", "nvidia/nemotron-3.5-super-vl:free",
          ("chat", "summarize"), "multimodal, 1M context"),
    Model("Nemotron 3.5 Lightning (OR)", "openrouter", "nvidia/nemotron-3.5-lightning:free",
          ("chat",), "fast, 1M context"),
    Model("Particle-1 (OR)", "openrouter", "particle-ai/particle-1:free",
          ("code",), "agentic coding, post-trained on DeepSeek V4.1"),
    Model("Flint v1.0 (OR)", "openrouter", "recursive/flint-v1.0:free",
          ("code",), "MoE coding agent"),
    Model("LFM 3 1.7B (OR)", "openrouter", "liquid/lfm-3-1.7b:free",
          ("chat",), "compact, tool calling"),
]

# PENDING (Weza, 2026-11-22: "we'll come back to ChatGPT and DeepSeek later")
PENDING = {
    "explain_first_choice": "ChatGPT (OpenAI API) — not connected; Gemini covers it",
    "quiz_code_first_choice": "DeepSeek — no :free variant on OpenRouter; Qwen covers it",
}

# task -> ordered candidate displays (cheapest capable first, all $0)
ROUTING: dict[str, list[str]] = {
    "quiz":      ["Qwen 3.8 27B (Groq)", "GPT-OSS 120B (Groq)", "Nemotron Nano Reasoning (OR)"],
    "code":      ["Qwen 3.8 27B (Groq)", "Nemotron 3 Ultra 550B (OR)"],
    "explain":   ["Gemini Flash Lite", "Gemma 4 31B (OR)"],          # ChatGPT pending
    "summarize": ["Gemini Flash Lite", "Gemma 4 31B (OR)", "Ling 3.2 Flash (OR)"],
    "plan":      ["Gemini Flash Lite", "Nemotron 3 Ultra 550B (OR)"],
    "reasoning": ["Nemotron 3 Ultra 550B (OR)", "Gemini Flash Lite"],
    "arabic":    ["ALLAM 2 7B (Groq)", "Gemini Flash Lite"],
    "chat":      ["Gemini Flash Lite", "GPT-OSS 20B (Groq)", "OpenRouter Auto-Free"],
}


# ------------------------------------------------------------- calling

def call_model(model: Model, prompt: str, system: str | None = None) -> dict:
    cmd = [sys.executable, str(model.helper), "--prompt", prompt,
           "--model", model.model_id]
    if system:
        cmd += ["--system", system]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    try:
        data = json.loads(out.stdout.strip().splitlines()[-1])
    except Exception:
        return {"ok": False, "model": model.display,
                "error": (out.stdout + out.stderr)[-300:]}
    data["model"] = model.display
    return data


def route(task: str, prompt: str, system: str | None = None) -> dict:
    """Try candidates in order; first success wins. All routes are $0."""
    by_name = {m.display: m for m in MODELS}
    errors = []
    for name in ROUTING.get(task, ROUTING["chat"]):
        res = call_model(by_name[name], prompt, system)
        if res.get("ok"):
            res["task"] = task
            res["fallbacks_tried"] = errors
            return res
        errors.append(f"{name}: {res.get('error', 'failed')}")
    return {"ok": False, "task": task, "errors": errors}


# ---------------------------------------------------------------- demo

if __name__ == "__main__":
    tests = [
        ("quiz", "اعمل سؤال اختيار من متعدد واحد عن طبقة Silver في مستودع البيانات، واكتب الإجابة الصحيحة."),
        ("explain", "اشرح الـ Star Schema في سطرين بالعربي."),
        ("code", "Write a one-line SQL query that counts rows in a table named Transactions."),
    ]
    for task, prompt in tests:
        r = route(task, prompt)
        print(f"\n### {task} -> {r.get('model', 'FAILED')}")
        print(r.get("text", r.get("errors", "")))
        if r.get("usage"):
            print("usage:", r["usage"])
