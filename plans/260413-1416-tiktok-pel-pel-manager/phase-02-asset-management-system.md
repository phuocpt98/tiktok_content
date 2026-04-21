---
phase: 2
title: "Asset Management System"
status: pending
effort: 8h
priority: P1
depends_on: [1]
---

# Phase 2: Asset Management System

## Context Links
- [SQLite Python docs](https://docs.python.org/3/library/sqlite3.html)
- [Pydantic models](https://docs.pydantic.dev/latest/)

## Overview
Build the core asset storage, tagging, and retrieval system. This is the foundation for cost optimization -- every generated piece (image, audio, video, text) is stored as a reusable asset with metadata and cost tracking.

## Key Insights
- Asset reuse is the #1 cost saver. A product image generated once (~$0.04) can be used in 10+ videos
- Tags enable fuzzy search: "nuoc giat" (detergent) images can be reused across brands
- Cost tracking per asset helps optimize which generation methods to prefer

## Requirements

### Functional
- Store assets with metadata (type, tags, product, cost, creation date)
- Search assets by tag, product name, type
- Track API cost per asset
- Deduplication -- don't regenerate identical content
- Asset versioning (v1, v2 of same product image)
- Export asset usage report

### Non-Functional
- SQLite database (zero setup)
- File-based storage (images/audio/video on disk, paths in DB)
- Sub-second search for <10K assets
- Vietnamese text support (UTF-8)

## Architecture

### Database Schema (SQLite)
```sql
CREATE TABLE assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,           -- 'image', 'audio', 'video', 'text', 'script'
    name TEXT NOT NULL,           -- descriptive name
    file_path TEXT NOT NULL,      -- relative path from data/ dir
    product TEXT,                 -- product name/category
    tags TEXT,                    -- comma-separated tags
    prompt TEXT,                  -- original generation prompt
    model TEXT,                   -- gemini model used
    cost_usd REAL DEFAULT 0,     -- API cost in USD
    duration_sec REAL,           -- for audio/video
    width INTEGER,               -- for images/video
    height INTEGER,              -- for images/video
    file_size_bytes INTEGER,
    usage_count INTEGER DEFAULT 0, -- how many times used in videos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,           -- e.g., "Nuoc giat Omo review"
    product TEXT,
    status TEXT DEFAULT 'draft',  -- draft, in_progress, published
    script TEXT,                  -- generated script/narration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE project_assets (
    project_id INTEGER,
    asset_id INTEGER,
    role TEXT,                    -- 'thumbnail', 'background', 'voiceover', etc.
    sequence_order INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);

CREATE TABLE cost_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,
    api_call TEXT,                -- 'imagen', 'veo', 'flash-tts', etc.
    cost_usd REAL,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);

CREATE INDEX idx_assets_tags ON assets(tags);
CREATE INDEX idx_assets_product ON assets(product);
CREATE INDEX idx_assets_type ON assets(type);
```

### Asset Manager API (Python)
```python
class AssetManager:
    def save_asset(type, name, file_path, tags, prompt, model, cost) -> Asset
    def search(query, type=None, product=None, limit=20) -> list[Asset]
    def find_similar(prompt, type, threshold=0.7) -> list[Asset]
    def get_by_product(product_name) -> list[Asset]
    def increment_usage(asset_id) -> None
    def get_cost_report(days=30) -> CostReport
    def get_reusable_assets(product, type) -> list[Asset]
```

### Search Strategy (cost-first)
1. Exact match: same product + same type
2. Tag match: overlapping tags + same type
3. Prompt similarity: simple keyword overlap (no embeddings needed -- YAGNI)
4. If no match found --> generate new via API

## Related Code Files
- **Create**: `src/assets/models.py` -- Pydantic models for Asset, Project, CostLog
- **Create**: `src/assets/manager.py` -- AssetManager class with all CRUD + search
- **Create**: `src/assets/db.py` -- SQLite connection, schema init, migrations

## Implementation Steps

1. **Create Pydantic models** (`models.py`)
   - Asset, Project, ProjectAsset, CostLog dataclasses
   - Validation for file paths, tag formats

2. **Create database layer** (`db.py`)
   - `init_db()` -- create tables if not exist
   - `get_connection()` -- return sqlite3 connection
   - Use context manager for transactions

3. **Implement AssetManager** (`manager.py`)
   - `save_asset()` -- insert + copy file to organized dir
   - `search()` -- SQL LIKE on tags, name, product
   - `find_similar()` -- keyword overlap scoring on prompts
   - `get_by_product()` -- filter by product
   - `get_reusable_assets()` -- main cost-saving method
   - `increment_usage()` -- track reuse count
   - `get_cost_report()` -- aggregate costs by type, date range

4. **File organization logic**
   - Auto-organize: `data/images/{product_slug}/{timestamp}.png`
   - Auto-organize: `data/audio/{product_slug}/{timestamp}.wav`
   - Slugify Vietnamese product names for folder names

5. **CLI commands** (add to `cli.py`)
   - `pel assets list [--type] [--product]`
   - `pel assets search <query>`
   - `pel assets cost-report [--days 30]`
   - `pel assets import <file>` -- manually add existing assets

6. **Write tests**
   - Test save/search/retrieve cycle
   - Test cost tracking accuracy
   - Test Vietnamese text in tags and names
   - Test duplicate detection

## Todo List
- [ ] Create Pydantic models (Asset, Project, CostLog)
- [ ] Create db.py with schema init
- [ ] Implement AssetManager.save_asset()
- [ ] Implement AssetManager.search() with tag matching
- [ ] Implement AssetManager.find_similar() with keyword overlap
- [ ] Implement AssetManager.get_reusable_assets()
- [ ] Implement cost tracking (save + report)
- [ ] Add file organization logic with slugified paths
- [ ] Add CLI commands for asset management
- [ ] Write unit tests
- [ ] Test with Vietnamese product names

## Success Criteria
- Can save an asset and retrieve it by product/tag/type
- Cost report shows total spend by category
- Search returns relevant results for Vietnamese queries
- File organization creates clean folder structure
- All tests pass

## Risk Assessment
- **SQLite concurrent access**: Not an issue -- single user local app
- **Vietnamese text slugification**: Use `unidecode` library for safe folder names
- **Large asset files**: Keep originals on disk, only metadata in DB
