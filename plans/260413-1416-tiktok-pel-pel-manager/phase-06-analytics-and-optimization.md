---
phase: 6
title: "Analytics and Optimization"
status: pending
effort: 5h
priority: P3
depends_on: [5]
---

# Phase 6: Analytics and Optimization

## Overview
Track content performance, optimize generation strategy, and reduce costs over time. This phase is independent and can be built incrementally after the core system works.

## Key Insights
- TikTok analytics available via TikTok Creator Center (manual for now)
- Correlating content attributes (product type, style, time) with views helps refine strategy
- Cost-per-view is the key metric for ROI

## Requirements

### Functional
- Track video performance (views, likes, comments, shares -- manual input initially)
- Cost analysis: cost-per-video, cost-per-view, cost-per-engagement
- Asset ROI: which assets/products generate most views per dollar
- Content strategy recommendations based on data
- A/B tracking: compare different templates, scripts, posting times

### Non-Functional
- Simple SQLite tables for analytics
- CLI reports
- Export to CSV for spreadsheet analysis

## Architecture

### Database Additions
```sql
CREATE TABLE video_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    tiktok_url TEXT,
    posted_at TIMESTAMP,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    followers_gained INTEGER DEFAULT 0,
    affiliate_clicks INTEGER DEFAULT 0,
    affiliate_sales INTEGER DEFAULT 0,
    revenue_usd REAL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### Key Metrics
- **Cost per video**: sum of asset generation costs
- **Cost per 1K views (CPM)**: generation_cost / (views/1000)
- **ROI**: (affiliate_revenue - generation_cost) / generation_cost
- **Asset reuse rate**: reused_assets / total_assets_used
- **Best performing**: products, templates, posting times

## Implementation Steps

### 1. Performance tracking (`src/analytics/tracker.py`)
- `log_performance(project_id, tiktok_url, views, likes, ...)` -- manual input
- `update_performance(project_id, views, likes, ...)` -- update stats
- Bulk import from CSV (if user exports from TikTok analytics)

### 2. Cost analyzer (`src/analytics/cost.py`)
- Per-video cost breakdown (text, images, TTS, video)
- Daily/weekly/monthly spend totals
- Cost trend over time
- Asset reuse savings calculation

### 3. Reports (`src/analytics/reports.py`)
- Top performing videos
- Best products by views/engagement
- Best posting times
- Cost efficiency ranking
- Recommendations (e.g., "Product X gets 3x more views, create more content for it")

### 4. CLI Commands
```bash
pel stats log <project_id> --url <tiktok_url> --views 1000 --likes 50
pel stats update <project_id> --views 5000 --likes 200
pel stats report                    # overall summary
pel stats report --product "Omo"    # per-product report
pel stats cost                      # cost breakdown
pel stats top                       # top performing videos
```

### 5. (Later) TikTok Analytics API integration
- Auto-fetch stats instead of manual input
- Requires API access

## Todo List
- [ ] Create video_performance table
- [ ] Implement performance tracker (manual input)
- [ ] Implement cost analyzer
- [ ] Create summary reports (top videos, best products, costs)
- [ ] Add CLI analytics commands
- [ ] Add CSV export
- [ ] Add simple recommendations engine

## Success Criteria
- Can log and update video performance
- Cost report shows spend breakdown by category
- Top performers report helps identify winning products
- CSV export works for spreadsheet analysis

## Risk Assessment
- **Manual data entry tedious**: Mitigation -- bulk CSV import, minimal required fields
- **Small sample size early on**: Need 20+ videos before analytics become meaningful
- **TikTok metrics delayed**: Views may take 24-48h to stabilize; update after 48h
