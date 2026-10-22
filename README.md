# King of AEO measurement

Method and raw data for the King of AEO experiment: four frozen questions asked of ChatGPT, Perplexity, Claude and Gemini through the DataForSEO LLM Responses API with web search on, plus Google organic and AI Overview pulls for the matching keywords, on three dates between 2026-09-30 and 2026-10-21. The question under test was whether a new entrant (Stephane Morera, EVOIX) gets named by the engines, and which pages get cited when he does.

Maintained by Stephane Morera, founder of EVOIX (evoix.io).

Related reading: the experiment write-up at https://evoix.io/blog/who-is-the-king-of-aeo-dark-horse-entry and the standing page at https://stephanemorera.com/king-of-aeo/. The scripts that ran the pulls are published in https://github.com/stephanemorera88-spec/evoix-aeo-tools.

Everything in `data/` is the raw record as written at pull time. Nothing has been edited, re-scored or removed, including failed calls, transport errors and a one-off "queen of AEO" probe. The tables in this README are counts computed from the files by a script; they do not interpret the results.

## The four frozen questions

| Key | Question string (verbatim) |
|---|---|
| Q1 head | `Who is the king of AEO (answer engine optimization)?` |
| Q2 contenders | `Who are the contenders for the King of AEO title?` |
| QFL | `Who is the King of AEO in Florida?` |
| QCFL | `Who is the King of AEO in Central Florida?` |

In the 9/30 and 10/2 files the key is stored as `query_key` with the values `Q1`, `Q2`, `QFL`, `QCFL`. In the 10/21 files it is stored as `label` with the values `Q1-head` and `Q2-contenders` (only Q1 and Q2 were run on 10/21). The 9/30 files also carry one extra row per engine with key `QUEEN`, a one-off probe of a "queen of AEO" question whose exact wording differs by engine (see the `query` and `query_note` fields in those rows).

## Engines and models

| Engine | DataForSEO engine name | Model requested | Served |
|---|---|---|---|
| ChatGPT | `chat_gpt` | `gpt-5.4-2026-03-05` | same, on every row that records it |
| Perplexity | `perplexity` | `sonar-pro` | same |
| Claude | `claude` | `claude-sonnet-5` | same |
| Gemini | `gemini` | `gemini-3.5-flash` | `gemini-3.6-flash` on all six 10/21 rows (the `model` field); the 9/30 rows record only the requested string |

Endpoint: DataForSEO `ai_optimization/<engine>/llm_responses/live` with `web_search: true`, `max_output_tokens: 1500`, one task per run.

Google: DataForSEO `serp/google/organic/live/advanced`, United States, desktop, English, depth 10, AI Overview loaded asynchronously. The 10/21 Google rows record this on each row in the `tool` and `params` fields (`DFS serp_organic_live_advanced`, `US desktop en depth10 load_async_ai_overview`). The 9/30 and 10/2 Google rows do not carry a params field; the method for those dates is as recorded in the lab notes, not in the file.

## Pull dates

All timestamps in the files are UTC.

| File date label | Experiment id | UTC window of the rows | Note |
|---|---|---|---|
| 2026-09-30 | EXP-002 | 2026-09-30 19:38 to 19:49 | 4 engines + Google; 10 runs each for Q2, QFL, QCFL, 3 runs for Q1, 1 queen probe |
| 2026-10-02 | EXP-007 | 2026-10-02 05:56 to 06:01 | 4 engines + Google; same run counts; Gemini returned three 50301 rate-limit failures and no answers |
| 2026-10-02 | EXP-009 | 2026-10-02 06:35 to 06:36 | "post-page top-up": 7 extra Q1 runs on ChatGPT, Claude and Perplexity after a page went live |
| 2026-10-21 | EXP-009 | 2026-10-22 03:02 to 03:11 | the evening of 10/21 in US Eastern time; 3 runs each of Q1 and Q2 on 4 engines, plus Google. The Google rows label themselves "EXP-009 (EXP-007 day-19 read, late)" |

## Files and field meanings

There are two generations of file layout. The 9/30 and 10/2 rows were written by hand after reading each engine answer (the `named`, `included`, `named_quote`, `rank_or_context` and `other_names` fields are human coding of the answer text). The 10/21 rows were written mechanically by `scripts/dfs_llm_probe.py` (the `named_*` and `*_cited` fields are regex and substring matches on the answer text and cited URLs).

### Generation A, engine files (EXP-002-2026-09-30-*, EXP-007-2026-10-02-*, EXP-009-2026-10-02-*)

One JSON object per line, one line per run.

| Field | Meaning |
|---|---|
| `run_id` | DataForSEO task id for the call |
| `query_key` | `Q1`, `Q2`, `QFL`, `QCFL` or `QUEEN` |
| `query` / `query_string` | the question text (present on most rows; the 9/30 ChatGPT rows carry `query_string`) |
| `run_n` | run number within that question on that date |
| `datetime_utc` | when the call was made |
| `model_string` | the model string sent to DataForSEO |
| `named` | `true` if the answer text names Stephane Morera (hand-coded) |
| `included` | `true` if evoix.io or stephanemorera.com appears in `sources` (source-set inclusion). Checked against every row that carries the field: it matches that rule on all 257 rows |
| `named_quote` | the sentence from the answer that names him, or `null` |
| `rank_or_context` | where in the answer the name sits (position in a list, framing), free text |
| `sources` | list of URLs the engine cited (a JSON-encoded string on a few rows) |
| `other_names` | other people the answer names as claimants or contenders |
| `cost` | DataForSEO charge for the call, USD |
| `fan_out_queries` / `fan_out` | the web searches the engine ran to answer, when DataForSEO returned them |
| `stephanemorera_cited` | 10/2 files only: whether stephanemorera.com is in the sources; `null` where not evaluated |
| `phase`, `stack_urls_cited`, `stack_pieces_cited` | EXP-009 10/2 rows only: the top-up phase label and which of the experiment's own pages, if any, were cited |
| `note`, `run_note`, `query_note`, `error`, `status`, `attempt`, `tier` | free-text annotations and failure records. The 9/30 Claude file has one `error` row (a 502 from the API transport, retried as the following row). The 10/2 Gemini file has three rows with `status` starting `FAILED 50301` and `named: null` |
| `queen_named`, `stunt_framing` | 9/30 Claude and Gemini rows only: who the queen probe named, and whether the answer framed the title as a stunt or meme (hand-coded) |

### Generation A, Google files (EXP-002-2026-09-30-google, EXP-007-2026-10-02-google)

One line per SERP pull.

| Field | Meaning |
|---|---|
| `query` | the Google keyword (these are search phrasings, not the four questions: `king of aeo`, `who is the king of aeo`, `king of aeo contenders`, `who is the king of aeo in florida`; 10/2 also has one `site:stephanemorera.com` check) |
| `pull_n`, `datetime_utc`, `task_id` | pull number, time, DataForSEO task id |
| `evoix_rank_group`, `evoix_rank_absolute`, `evoix_url`, `evoix_title` | organic position of the evoix.io result if present (`null` when absent) |
| `stephanemorera_rank` | 10/2 only: organic position of a stephanemorera.com result |
| `top10` | JSON-encoded list of the organic results (rank, domain, url, title) |
| `organic_slots` | 10/2 only: how many organic results came back |
| `aio_present`, `aio_async` | whether an AI Overview was on the page, and whether it loaded asynchronously (text not captured when `true` and `aio_names` is empty) |
| `aio_names`, `aio_sources` | names and source URLs read from the AI Overview text when captured |
| `aio_morera_present` (9/30) / `aio_morera` (10/2) | whether the AI Overview text names Morera; absent or `null` when the text was not captured |
| `other_features` | other SERP features present |
| `new_claimant_domains` | domains claiming the title that had not been seen on an earlier pull |
| `note` | free-text observation about the pull |

### Generation B, engine files (EXP-009-2026-10-21-chat_gpt, -claude, -gemini, -perplexity)

Written by `scripts/dfs_llm_probe.py`. One line per run.

| Field | Meaning |
|---|---|
| `exp`, `label`, `query` | experiment id, question key (`Q1-head`, `Q2-contenders`), question text |
| `engine`, `model_requested`, `model` | DataForSEO engine name, model string sent, model string DataForSEO reports as served |
| `run`, `ts` | run number, UTC timestamp |
| `task_id`, `status`, `cost`, `money_spent` | DataForSEO task id, status message, charge for the task, charge reported inside the result |
| `fan_out` | the engine's web search queries |
| `named_morera`, `named_evoix` | case-insensitive regex match of `morera` and `evoix` in the answer text |
| `evoix_cited`, `stephanemorera_cited` | whether any cited URL contains `evoix.io` or `stephanemorera.com` |
| `cited_urls` | every annotation URL in the answer, in order, duplicates kept |
| `answer_chars`, `answer_head` | length of the answer text and its first 900 characters |

### Generation B, Google file (EXP-009-2026-10-21-google)

| Field | Meaning |
|---|---|
| `exp`, `tool`, `params` | experiment label, endpoint, request parameters |
| `query`, `pull`, `task_id`, `status`, `datetime` | keyword, pull number, task id, DataForSEO status message, UTC time (`null` on the five pulls that returned `Internal SE Server Error.`) |
| `evoix_rank`, `stephanemorera_rank` | organic rank of each domain if present, else `null` |
| `organic` | JSON-encoded list of organic results (rank, domain, url) |
| `aio_present`, `aio_text`, `aio_refs` | whether an AI Overview was returned, its text, its reference URLs |
| `aio_names_morera`, `aio_first_name` | whether the AI Overview text names Morera, and the first person it names |
| `features` | SERP feature list |

## Results, counts only

Computed from the files in `data/` by the tally described below. "Valid runs" excludes rows that record an API error or a `FAILED` status. "Named Morera" counts rows where `named` (generation A) or `named_morera` (generation B) is `true`. No interpretation is attached to these numbers.

### Engine answers

| Date (file label) | File | Engine | Query | Valid runs | Named Morera | Error rows |
|---|---|---|---|---|---|---|
| 2026-09-30 | EXP-002-2026-09-30-chatgpt.jsonl | ChatGPT | Q1 head | 3 | 0 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-chatgpt.jsonl | ChatGPT | Q2 contenders | 10 | 10 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-chatgpt.jsonl | ChatGPT | QFL | 10 | 10 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-chatgpt.jsonl | ChatGPT | QCFL | 10 | 10 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-chatgpt.jsonl | ChatGPT | QUEEN (one-off) | 1 | 0 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-claude.jsonl | Claude | Q1 head | 3 | 0 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-claude.jsonl | Claude | Q2 contenders | 10 | 9 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-claude.jsonl | Claude | QFL | 10 | 10 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-claude.jsonl | Claude | QCFL | 10 | 10 | 1 |
| 2026-09-30 | EXP-002-2026-09-30-claude.jsonl | Claude | QUEEN (one-off) | 1 | 1 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-gemini.jsonl | Gemini | Q1 head | 3 | 0 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-gemini.jsonl | Gemini | Q2 contenders | 10 | 10 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-gemini.jsonl | Gemini | QFL | 10 | 10 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-gemini.jsonl | Gemini | QCFL | 10 | 10 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-gemini.jsonl | Gemini | QUEEN (one-off) | 1 | 0 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-perplexity.jsonl | Perplexity | Q1 head | 3 | 0 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-perplexity.jsonl | Perplexity | Q2 contenders | 10 | 10 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-perplexity.jsonl | Perplexity | QFL | 10 | 10 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-perplexity.jsonl | Perplexity | QCFL | 10 | 10 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-perplexity.jsonl | Perplexity | QUEEN (one-off) | 1 | 0 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-chatgpt.jsonl | ChatGPT | Q1 head | 3 | 1 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-chatgpt.jsonl | ChatGPT | Q2 contenders | 10 | 10 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-chatgpt.jsonl | ChatGPT | QFL | 10 | 10 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-chatgpt.jsonl | ChatGPT | QCFL | 10 | 10 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-claude.jsonl | Claude | Q1 head | 3 | 0 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-claude.jsonl | Claude | Q2 contenders | 10 | 9 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-claude.jsonl | Claude | QFL | 10 | 10 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-claude.jsonl | Claude | QCFL | 10 | 10 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-gemini.jsonl | Gemini | Q2 contenders | 0 | 0 | 3 |
| 2026-10-02 | EXP-007-2026-10-02-perplexity.jsonl | Perplexity | Q1 head | 3 | 0 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-perplexity.jsonl | Perplexity | Q2 contenders | 10 | 10 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-perplexity.jsonl | Perplexity | QFL | 10 | 10 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-perplexity.jsonl | Perplexity | QCFL | 10 | 10 | 0 |
| 2026-10-02 | EXP-009-2026-10-02-chatgpt.jsonl | ChatGPT | Q1 head | 7 | 0 | 0 |
| 2026-10-02 | EXP-009-2026-10-02-claude.jsonl | Claude | Q1 head | 7 | 0 | 0 |
| 2026-10-02 | EXP-009-2026-10-02-perplexity.jsonl | Perplexity | Q1 head | 7 | 0 | 0 |
| 2026-10-21 | EXP-009-2026-10-21-chat_gpt.jsonl | ChatGPT | Q1 head | 3 | 1 | 0 |
| 2026-10-21 | EXP-009-2026-10-21-chat_gpt.jsonl | ChatGPT | Q2 contenders | 3 | 2 | 0 |
| 2026-10-21 | EXP-009-2026-10-21-claude.jsonl | Claude | Q1 head | 3 | 0 | 0 |
| 2026-10-21 | EXP-009-2026-10-21-claude.jsonl | Claude | Q2 contenders | 3 | 3 | 0 |
| 2026-10-21 | EXP-009-2026-10-21-gemini.jsonl | Gemini | Q1 head | 3 | 3 | 0 |
| 2026-10-21 | EXP-009-2026-10-21-gemini.jsonl | Gemini | Q2 contenders | 3 | 3 | 0 |
| 2026-10-21 | EXP-009-2026-10-21-perplexity.jsonl | Perplexity | Q1 head | 3 | 0 | 0 |
| 2026-10-21 | EXP-009-2026-10-21-perplexity.jsonl | Perplexity | Q2 contenders | 3 | 3 | 0 |

### Google pulls

"AIO text not captured" counts pulls where the AI Overview loaded asynchronously and its text was not recorded, so whether it names anyone is unknown for those pulls. "evoix.io in organic" lists the organic rank on each pull where it appeared.

| Date (file label) | File | Keyword | Valid pulls | AIO present | AIO text names Morera | AIO text not captured | evoix.io in organic (ranks) | stephanemorera.com in organic | Error pulls |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-30 | EXP-002-2026-09-30-google.jsonl | `king of aeo contenders` | 3 | 3 | 0 | 3 | 2 (7, 7) | 0 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-google.jsonl | `king of aeo` | 3 | 3 | 0 | 0 | 0 (none) | 0 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-google.jsonl | `who is the king of aeo` | 3 | 3 | 0 | 2 | 0 (none) | 0 | 0 |
| 2026-09-30 | EXP-002-2026-09-30-google.jsonl | `who is the king of aeo in florida` | 3 | 3 | 0 | 3 | 1 (4) | 0 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-google.jsonl | `king of aeo` | 3 | 3 | 0 | 0 | 1 (4) | 0 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-google.jsonl | `who is the king of aeo` | 3 | 3 | 0 | 0 | 0 (none) | 0 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-google.jsonl | `who is the king of aeo in florida` | 3 | 3 | 0 | 3 | 3 (4, 4, 4) | 0 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-google.jsonl | `king of aeo contenders` | 3 | 3 | 0 | 3 | 3 (9, 6, 7) | 0 | 0 |
| 2026-10-02 | EXP-007-2026-10-02-google.jsonl | `site:stephanemorera.com` | 1 | 0 | 0 | 1 | 0 (none) | 1 | 0 |
| 2026-10-21 | EXP-009-2026-10-21-google.jsonl | `king of aeo` | 3 | 3 | 0 | 0 | 0 (none) | 0 | 0 |
| 2026-10-21 | EXP-009-2026-10-21-google.jsonl | `king of aeo contenders` | 1 | 1 | 0 | 0 | 0 (none) | 0 | 4 |
| 2026-10-21 | EXP-009-2026-10-21-google.jsonl | `who is the king of aeo` | 3 | 3 | 2 | 0 | 2 (7, 8) | 0 | 0 |
| 2026-10-21 | EXP-009-2026-10-21-google.jsonl | `who is the king of aeo in florida` | 3 | 3 | 1 | 0 | 0 (none) | 0 | 2 |

How the tally was made: for each line, a row is "valid" unless it carries an `error` key, a `status` beginning with `FAILED`, or (Google) a `status` other than `Ok.` with no timestamp. Named is `named == true` or `named_morera == true`. For Google, AIO present is `aio_present == true`; "names Morera" is `aio_morera_present`, `aio_morera` or `aio_names_morera` equal to `true`; "not captured" is that field missing or `null`; evoix.io in organic is `evoix_rank_group` or `evoix_rank` not `null`.

## Reproducing a run

See `scripts/README.md`. Short version: set `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD`, write a `plan.json` with the question strings above, and run `python3 scripts/dfs_llm_probe.py <engine> <out.jsonl> plan.json`. Each call is billed to your own DataForSEO account.

## Licence

Code in `scripts/` is MIT (see LICENSE). Data in `data/` is CC BY 4.0 (see DATA-LICENSE and https://creativecommons.org/licenses/by/4.0/). Copyright (c) 2026 Stephane Morera, EVOIX LLC.
