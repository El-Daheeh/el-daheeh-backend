// El-Daheeh backend — Deno Deploy port (free tier, no card).
// Same routing as standalone_server.py. Keys come from environment variables
// set in the Deno Deploy project settings (never hardcode):
//   GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY
// Endpoints: GET /health -> {ok:true} ; POST /chat {message} -> {agent, model, text}

const SYSTEM =
  "You are a study agent inside El-Daheeh (StudyLeague), an Arabic study-competition " +
  "platform for university students. The current course context is Data Warehousing: " +
  "Medallion architecture (Bronze = raw data as-is, Silver = cleaned/modelled, " +
  "Gold = star schema for reporting/Power BI). 'gold/silver/bronze' in user messages " +
  "refer to these layers, NOT metals. Answer in Arabic unless asked otherwise. " +
  "Be concrete and complete: if asked for N questions, produce exactly N questions. " +
  "If asked for a study plan and details are missing, build a sensible plan and state your assumptions.";

const KEYS = {
  gemini: Deno.env.get("GEMINI_API_KEY") ?? "",
  groq: Deno.env.get("GROQ_API_KEY") ?? "",
  openrouter: Deno.env.get("OPENROUTER_API_KEY") ?? "",
};

function classify(t: string): string {
  const s = t.toLowerCase();
  if (/اشرح|يعني إيه|يعنى ايه|وضح|مش فاهم|explain/.test(s)) return "explain";
  if (/أسئلة|اسئلة|كويز|quiz|اختبار/.test(s)) return "quiz";
  if (/كود|sql|code|برمج/.test(s)) return "code";
  if (/لخص|ملخص|summar/.test(s)) return "summarize";
  if (/خطة|خطه|جدول|plan/.test(s)) return "plan";
  return "chat";
}

// task -> ordered provider chain (first keyed provider that answers wins)
const CHAINS: Record<string, string[]> = {
  explain: ["gemini", "openrouter", "groq"],
  summarize: ["gemini", "openrouter", "groq"],
  quiz: ["groq", "openrouter", "gemini"],
  code: ["openrouter", "groq", "gemini"],
  plan: ["openrouter", "gemini", "groq"],
  chat: ["gemini", "groq", "openrouter"],
};

async function callGemini(prompt: string): Promise<[string, string]> {
  const r = await fetch(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent",
    {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-goog-api-key": KEYS.gemini },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: SYSTEM }] },
        contents: [{ parts: [{ text: prompt }] }],
      }),
    },
  );
  if (!r.ok) throw new Error("gemini " + r.status);
  const d = await r.json();
  return ["Gemini (gemini-3.5-flash-lite)", d.candidates[0].content.parts[0].text];
}

async function callOpenAIStyle(url: string, key: string, model: string, label: string, prompt: string): Promise<[string, string]> {
  const r = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + key,
      "User-Agent": "Mozilla/5.0 ElDaheehRouter/1.0",
    },
    body: JSON.stringify({
      model,
      messages: [
        { role: "system", content: SYSTEM },
        { role: "user", content: prompt },
      ],
    }),
  });
  if (!r.ok) throw new Error(label + " " + r.status);
  const d = await r.json();
  return [label + " (" + (d.model ?? model) + ")", d.choices[0].message.content];
}

const PROVIDERS: Record<string, (p: string) => Promise<[string, string]>> = {
  gemini: callGemini,
  groq: (p) => callOpenAIStyle("https://api.groq.com/openai/v1/chat/completions", KEYS.groq, "openai/gpt-oss-120b", "Groq", p),
  openrouter: (p) => callOpenAIStyle("https://openrouter.ai/api/v1/chat/completions", KEYS.openrouter, "openrouter/free", "OpenRouter", p),
};

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

Deno.serve(async (req: Request) => {
  const url = new URL(req.url);
  if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
  if (url.pathname === "/health") {
    return Response.json({
      ok: true,
      service: "el-daheeh-backend-deno",
      providers: Object.fromEntries(Object.entries(KEYS).map(([k, v]) => [k, !!v])),
    }, { headers: CORS });
  }
  if (url.pathname === "/chat" && req.method === "POST") {
    const { message } = await req.json().catch(() => ({ message: "" }));
    if (!message) return Response.json({ error: "empty message" }, { status: 400, headers: CORS });
    const task = classify(message);
    const errors: string[] = [];
    for (const name of CHAINS[task] ?? CHAINS.chat) {
      if (!KEYS[name as keyof typeof KEYS]) continue;
      try {
        const [model, text] = await PROVIDERS[name](message);
        return Response.json({ agent: task, model, text }, { headers: CORS });
      } catch (e) {
        errors.push(name + ": " + (e as Error).message);
      }
    }
    return Response.json({ error: "all providers failed", details: errors }, { status: 502, headers: CORS });
  }
  return new Response("El-Daheeh backend", { headers: CORS });
});
