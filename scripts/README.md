# Reproducing one run

`dfs_llm_probe.py` is the exact script that produced the 2026-10-21 files in `data/` (the 9/30 and 10/2 files were produced by hand-run calls to the same DataForSEO endpoint and hand-coded, see the main README). It calls DataForSEO's `ai_optimization/<engine>/llm_responses/live` endpoint with `web_search: true` and `max_output_tokens: 1500`, once per run, and appends one JSON line per run.

Credentials are read from the environment only: `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD`. Nothing in this repository stores or reads a credential file. Each run is billed to your DataForSEO account (the `cost` field in every output row records the charge; the 10/21 runs cost between about 0.01 and 0.05 USD each).

```bash
export DATAFORSEO_LOGIN="you@example.com"
export DATAFORSEO_PASSWORD="your-api-password"
mkdir -p runs
cat > runs/plan.json <<'JSON'
[{"exp": "EXP-009", "label": "Q1-head", "query": "Who is the king of AEO (answer engine optimization)?", "n": 3},
 {"exp": "EXP-009", "label": "Q2-contenders", "query": "Who are the contenders for the King of AEO title?", "n": 3}]
JSON
python3 scripts/dfs_llm_probe.py chat_gpt runs/EXP-009-$(date +%F)-chat_gpt.jsonl runs/plan.json
```

Engine names are DataForSEO's: `chat_gpt`, `perplexity`, `claude`, `gemini`. Pinned models are in the `MODELS` dict (`gpt-5.4-2026-03-05`, `sonar-pro`, `claude-sonnet-5`, `gemini-3.5-flash`); override one with `DFS_MODEL_<ENGINE>` if DataForSEO retires it. The `model` field in each output row records what was actually served, which is how the 10/21 files show `gemini-3.6-flash` served for a `gemini-3.5-flash` request.

The output row format is the "generation B" layout described in the main README (`exp`, `label`, `query`, `engine`, `model_requested`, `run`, `ts`, `task_id`, `status`, `cost`, `model`, `money_spent`, `fan_out`, `named_morera`, `named_evoix`, `evoix_cited`, `stephanemorera_cited`, `cited_urls`, `answer_chars`, `answer_head`). The two regexes in the script decide `named_morera` and `named_evoix`; change them to measure a different name.

For the Google side, the pulls used DataForSEO `serp/google/organic/live/advanced` with a body like the one below (US desktop, English, depth 10, AI Overview loaded asynchronously). The `dfs.sh` wrapper in https://github.com/stephanemorera88-spec/evoix-aeo-tools sends it; a plain `curl -u "$DATAFORSEO_LOGIN:$DATAFORSEO_PASSWORD"` POST to `https://api.dataforseo.com/v3/serp/google/organic/live/advanced` does the same.

```json
[{"keyword": "king of aeo", "location_code": 2840, "language_code": "en", "device": "desktop", "depth": 10, "load_async_ai_overview": true}]
```

`runs/` is gitignored so your own pulls do not land in the published dataset by accident.
