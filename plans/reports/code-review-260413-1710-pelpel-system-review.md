# Code Review: Tạp Hóa Pel Pel - TikTok Content Production System

**Date:** 2026-04-13 | **Reviewer:** code-reviewer | **Scope:** Full system (10 modules + skill + docs)
**LOC:** ~750 (src/) | **Status:** Early-stage, functional skeleton

---

## Overall Assessment

Solid foundation for a Claude-operated content pipeline. Module separation is clean, naming is descriptive, code is readable. However, several **critical bugs** and **missing features** would break real end-to-end usage. The system is ~60% complete for production use.

---

## CRITICAL Issues

### C1. API Keys Hardcoded in `.env.example`
- **File:** `.env.example` (line 2-3)
- **Impact:** Real Gemini API keys committed in plaintext. `.env.example` should contain placeholder values only.
- **Fix:** Replace with `GEMINI_API_KEY=your-key-here`. Move real keys to `.env` (already gitignored).

### C2. `config.py` Loads `.env.example` Instead of `.env`
- **File:** `src/config.py` (line 8)
- **Code:** `load_dotenv(PROJECT_ROOT / ".env.example")`
- **Impact:** Should load `.env` first, fall back to `.env.example`. Current behavior loads example file which may overwrite real `.env` values or expose keys.
- **Fix:**
  ```python
  env_path = PROJECT_ROOT / ".env"
  if not env_path.exists():
      env_path = PROJECT_ROOT / ".env.example"
  load_dotenv(env_path)
  ```

### C3. DB Name Typo
- **File:** `src/config.py` (line 21)
- **Code:** `DB_PATH = PROJECT_ROOT / "pelple.db"` — should be `pelpel.db`
- **Impact:** Cosmetic but inconsistent with project name everywhere else.

---

## HIGH Priority

### H1. Missing API Key Rotation (SKILL.md promises it, code doesn't implement)
- **File:** `src/gemini-client.py`, `src/config.py`
- SKILL.md says "2 API keys available, auto-rotate when key 1 hits rate limit"
- Code only loads `GEMINI_API_KEY`, ignores `GEMINI_API_KEY_2`
- **Fix:** Add key rotation logic in `gemini-client.py`:
  ```python
  KEYS = [k for k in [GEMINI_API_KEY, os.getenv("GEMINI_API_KEY_2", "")] if k]
  current_key_idx = 0
  ```

### H2. No Error Handling for Gemini JSON Parsing
- **File:** `src/gemini-client.py` (lines 51-55)
- `json.loads(text)` will crash on malformed LLM output (common with Gemini)
- No retry logic for API failures or rate limits
- **Fix:** Wrap in try/except, add retry with backoff, validate JSON schema

### H3. Database Connections Never Use Context Managers
- **File:** `src/database.py` — all functions
- Pattern: `conn = get_connection()` ... `conn.close()` — if exception between, connection leaks
- **Fix:** Use `with get_connection() as conn:` or try/finally

### H4. `search_assets` Tag Search Is Fragile
- **File:** `src/database.py` (line 90-91)
- Tags stored as JSON array string, searched with `LIKE %tag%`
- Searching for tag "oil" would match "foil", "soil", etc.
- **Fix:** Use JSON functions or structured tag table

### H5. Missing `edge-tts` and `python-dotenv` in `requirements.txt`
- Both are installed but not listed in requirements.txt
- **Fix:** Add `edge-tts>=6.0.0` and `python-dotenv>=1.0.0`

### H6. `assemble` Command Doesn't Filter Assets by Project
- **File:** `src/cli.py` (lines 216-225)
- `search_assets(asset_type="image", keyword=None)` fetches ALL images, then filters by project_id in Python
- But `search_assets` doesn't filter by `project_id` at all — no parameter for it
- **Fix:** Add `project_id` filter to `search_assets` in database.py

### H7. Text Overlay `fill` Parameter Expects Tuple, Gets String
- **File:** `src/text-overlay.py` (line 80)
- `draw.text(..., fill=text_color)` where `text_color="#FFFFFF"` — Pillow accepts hex strings for RGB images but may fail for RGBA overlay
- Should parse hex to tuple for RGBA: `(255, 255, 255, 255)`

---

## MEDIUM Priority

### M1. No `__init__.py` Exports
- `src/__init__.py` is empty — fine for now but means all imports require full paths or the `_import()` hack in cli.py

### M2. Kebab-Case Filenames Cause Import Pain
- Files like `gemini-client.py`, `tts-engine.py` can't use standard Python imports
- cli.py has custom `_import()` function as workaround
- **Trade-off:** Naming convention says kebab-case, but Python modules conventionally use underscores. Consider `gemini_client.py` etc.

### M3. No Cleanup / Garbage Collection for Assets
- Generated files accumulate in `assets/` and `output/` forever
- No `delete_asset`, no disk usage tracking
- **Suggest:** Add `cleanup` CLI command, soft-delete in DB

### M4. `_get_duration` Silently Falls Back to 30s
- **File:** `src/video-assembler.py` (line 105)
- If ffprobe fails, assumes 30s — could produce very wrong timing
- Should at least warn/log

### M5. No Logging Anywhere
- All modules use print or raise — no structured logging
- Hard to debug pipeline failures
- **Suggest:** Add `logging` module, write to file

### M6. `trend-tracker.py` Has No Auto-Expiry
- `expires_at` column exists but never checked
- Stale trends stay "active" forever
- **Fix:** Add WHERE clause checking `expires_at IS NULL OR expires_at > datetime('now')`

### M7. No Project Deletion
- Can create projects but never delete. No cascade delete for project assets either.

### M8. `ffmpeg-python` in requirements.txt But Never Used
- Code calls ffmpeg via subprocess directly (correct approach)
- Remove unused dependency

---

## LOW Priority

### L1. Emoji in `export_trends_summary()` Output
- Fire/pin emojis may render oddly in some terminals

### L2. Hardcoded Windows Font Paths in `text-overlay.py`
- Won't work on Linux/macOS — acceptable given Windows-only target, but note in docs

### L3. No Type Hints on Return Values for Some Functions
- `update_project`, `deactivate_trend` return None implicitly

---

## Missing Modules / Features for Production Pipeline

| Module | Purpose | Priority |
|--------|---------|----------|
| **Caption Generator** | TikTok caption + hashtags as separate output | High |
| **Photo Mode Exporter** | Export individual slides for TikTok Photo Mode upload (format #1, highest priority) | High |
| **Content Calendar** | Schedule posts, track what's published | Medium |
| **Analytics Tracker** | Track views/engagement per video after posting | Medium |
| **Template System** | Reusable slide layouts (intro, CTA, comparison) | Medium |
| **Gemini TTS Integration** | SKILL.md mentions it, not implemented | Low |
| **Multi-image Generation** | Batch-generate scene images from script | High |

---

## SKILL.md (`/pelpel`) Assessment

**Strengths:**
- Clear agent architecture (Producer/Researcher/Writer/Designer/Editor)
- Good command structure
- Dual-mode (API auto + web manual) well-documented

**Gaps:**
- References `/agent-browser` skill but no instructions on setup/availability
- No error recovery flow (what if Designer fails mid-pipeline?)
- No output format specification (where final files go, naming convention)
- Trend command references "TikTok Creative Center" but no scraping logic exists
- `plan` and `report` commands have no implementation in any module
- Missing: how Claude should handle the Photo Mode format (just export images? what naming?)

---

## Architecture Assessment

**Good:**
- Clean separation: each module handles one concern
- Database as central registry — smart for asset reuse
- Config centralized properly
- CLI serves as both human interface and Claude's tool interface

**Concerns:**
- No pipeline orchestrator module — SKILL.md describes a multi-step pipeline but no code ties steps together programmatically
- Claude is expected to orchestrate via skill instructions, but no validation that steps completed correctly
- No state machine for project lifecycle (draft -> scripted -> assets_ready -> assembled -> review -> published)

---

## Positive Observations

1. Edge TTS choice is excellent — free, unlimited, good Vietnamese quality
2. Dual-mode design (API auto + web manual) is pragmatic for budget constraints
3. Asset database with tagging enables smart reuse
4. Video assembler's zoom/pan effect adds production value cheaply
5. WAL mode on SQLite is good practice
6. .gitignore properly excludes .env and generated assets

---

## Recommended Actions (Priority Order)

1. **[CRITICAL]** Remove real API keys from `.env.example`, replace with placeholders
2. **[CRITICAL]** Fix `config.py` to load `.env` not `.env.example`
3. **[HIGH]** Add `edge-tts` and `python-dotenv` to `requirements.txt`
4. **[HIGH]** Implement API key rotation in `gemini-client.py`
5. **[HIGH]** Add JSON parse error handling + retry in `gemini-client.py`
6. **[HIGH]** Add `project_id` filter to `search_assets` in `database.py`
7. **[HIGH]** Use context managers for all DB connections
8. **[MEDIUM]** Add Photo Mode export module (core format #1)
9. **[MEDIUM]** Add trend expiry logic
10. **[MEDIUM]** Remove unused `ffmpeg-python` from requirements.txt
11. **[LOW]** Consider renaming kebab-case files to underscore for Python convention

---

## Metrics

| Metric | Value |
|--------|-------|
| Type Coverage | ~30% (minimal type hints) |
| Test Coverage | 0% (no tests directory) |
| Linting Issues | ~5 (unused import, missing types) |
| Security Issues | 1 critical (API keys in .env.example) |
| Missing Dependencies | 2 (edge-tts, python-dotenv in requirements.txt) |

---

## Unresolved Questions

1. Is the `.env.example` with real keys intentional for sharing between machines, or an oversight? If intentional, should use a secrets manager or at minimum not call it `.example`.
2. Photo Mode is listed as priority format #1 but has zero implementation — is this expected to be Claude manually saving images, or should there be an export module?
3. `plan` and `report` commands in SKILL.md — are these purely Claude-driven (no code needed) or should they have backing modules?
4. Should the system support concurrent project editing, or is single-project-at-a-time fine?
5. DB typo `pelple.db` — is this intentional or should it be `pelpel.db`?
