#!/usr/bin/env python3
"""DataForSEO LLM Responses probes, one engine per process. Writes one JSON line per run.
Usage: dfs_llm_probe.py <engine> <out.jsonl> <plan.json>
  engine    one of chat_gpt, perplexity, claude, gemini (DataForSEO ai_optimization engine names)
  out.jsonl appended to, one line per run
  plan.json = [{"exp": "...", "label": "...", "query": "...", "n": 3}, ...]
Credentials come from the environment: DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD (never printed,
never read from a file in this repo). Models can be overridden with DFS_MODEL_<ENGINE>, e.g.
DFS_MODEL_GEMINI=gemini-3.5-flash."""
import json, sys, time, re, os, base64, urllib.request
LOGIN, PASSWORD = os.environ.get("DATAFORSEO_LOGIN"), os.environ.get("DATAFORSEO_PASSWORD")
if not LOGIN or not PASSWORD:
    sys.exit("dfs_llm_probe.py: set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD in the environment")
if len(sys.argv) != 4:
    sys.exit("usage: dfs_llm_probe.py <engine> <out.jsonl> <plan.json>")
engine, out, plan = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
MODELS = {"chat_gpt": "gpt-5.4-2026-03-05", "perplexity": "sonar-pro", "claude": "claude-sonnet-5", "gemini": "gemini-3.5-flash"}
for k in MODELS:
    MODELS[k] = os.environ.get(f"DFS_MODEL_{k.upper()}", MODELS[k])
AUTH = "Basic " + base64.b64encode(f"{LOGIN}:{PASSWORD}".encode()).decode()

def call(query):
    body = json.dumps([{"user_prompt": query, "model_name": MODELS[engine], "web_search": True, "max_output_tokens": 1500}]).encode()
    req = urllib.request.Request(f"https://api.dataforseo.com/v3/ai_optimization/{engine}/llm_responses/live", data=body,
                                 headers={"Authorization": AUTH, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read().decode("utf-8"))

with open(out, "a") as f:
    for p in plan:
        for i in range(1, p["n"] + 1):
            row = {"exp": p["exp"], "label": p["label"], "query": p["query"], "engine": engine, "model_requested": MODELS[engine], "run": i, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            try:
                d = call(p["query"]); t = d["tasks"][0]
                row.update({"task_id": t.get("id"), "status": t.get("status_message"), "cost": t.get("cost")})
                res = (t.get("result") or [None])[0]
                if res:
                    text, urls = [], []
                    for it in res.get("items") or []:
                        for s in it.get("sections") or []:
                            if s.get("text"): text.append(s["text"])
                            for a in s.get("annotations") or []:
                                if a.get("url"): urls.append(a["url"])
                    txt = "\n".join(text)
                    row.update({"model": res.get("model_name"), "money_spent": res.get("money_spent"), "fan_out": res.get("fan_out_queries"),
                                "named_morera": bool(re.search(r"morera", txt, re.I)), "named_evoix": bool(re.search(r"evoix", txt, re.I)),
                                "evoix_cited": any("evoix.io" in u for u in urls), "stephanemorera_cited": any("stephanemorera.com" in u for u in urls),
                                "cited_urls": urls, "answer_chars": len(txt), "answer_head": txt[:900]})
                else:
                    row["error"] = json.dumps(t)[:300]
            except Exception as e:
                row["error"] = f"{type(e).__name__}: {str(e)[:200]}"
            f.write(json.dumps(row) + "\n"); f.flush()
            print(f"{engine} {p['label']} run {i}: morera={row.get('named_morera')} evoix={row.get('named_evoix')} cited={row.get('evoix_cited')} cost={row.get('cost')} {row.get('error','')[:80]}", flush=True)
