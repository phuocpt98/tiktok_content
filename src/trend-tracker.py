"""TikTok trend tracker - research and store trending content for niche."""
import json
from datetime import datetime
from pathlib import Path
from src.config import PROJECT_ROOT, TEXT_DIR
from src.database import get_connection

# Trend categories for grocery/household niche
TREND_CATEGORIES = [
    "hashtags",      # Trending hashtags
    "sounds",        # Trending sounds/music
    "formats",       # Trending video formats (duet, stitch, POV, etc.)
    "quotes",        # Trending quotes/text to overlay
    "hooks",         # Trending opening hooks (first 3 seconds)
    "challenges",    # Trending challenges
]


def init_trends_table():
    """Create trends table if not exists."""
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            description TEXT DEFAULT '',
            relevance TEXT DEFAULT 'medium',
            source TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            expires_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_trends_category ON trends(category);
        CREATE INDEX IF NOT EXISTS idx_trends_active ON trends(is_active);
    """)
    conn.commit()
    conn.close()


def add_trend(category: str, content: str, description: str = "",
              relevance: str = "medium", source: str = "",
              expires_at: str = None) -> int:
    """Add a new trend to the database."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO trends (category, content, description, relevance, source, created_at, expires_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (category, content, description, relevance, source,
         datetime.now().isoformat(), expires_at)
    )
    conn.commit()
    trend_id = cursor.lastrowid
    conn.close()
    return trend_id


def get_active_trends(category: str = None, limit: int = 20) -> list[dict]:
    """Get active trends, optionally filtered by category."""
    conn = get_connection()
    if category:
        rows = conn.execute(
            "SELECT * FROM trends WHERE is_active = 1 AND category = ? "
            "ORDER BY created_at DESC LIMIT ?", (category, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM trends WHERE is_active = 1 "
            "ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def deactivate_trend(trend_id: int):
    """Mark a trend as no longer active."""
    conn = get_connection()
    conn.execute("UPDATE trends SET is_active = 0 WHERE id = ?", (trend_id,))
    conn.commit()
    conn.close()


def bulk_add_trends(trends: list[dict]) -> int:
    """Add multiple trends at once. Returns count added."""
    count = 0
    for t in trends:
        add_trend(
            category=t.get("category", "hashtags"),
            content=t["content"],
            description=t.get("description", ""),
            relevance=t.get("relevance", "medium"),
            source=t.get("source", "research"),
        )
        count += 1
    return count


def export_trends_summary() -> str:
    """Export current trends as formatted text for context."""
    trends = get_active_trends(limit=50)
    if not trends:
        return "Chưa có trend nào được lưu."

    lines = ["# Active Trends\n"]
    by_category = {}
    for t in trends:
        cat = t["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(t)

    for cat, items in by_category.items():
        lines.append(f"\n## {cat.title()}")
        for item in items:
            rel = "🔥" if item["relevance"] == "high" else "📌"
            lines.append(f"- {rel} {item['content']}")
            if item["description"]:
                lines.append(f"  → {item['description']}")

    return "\n".join(lines)


# Initialize on import
init_trends_table()
