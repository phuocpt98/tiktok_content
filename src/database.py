"""SQLite database for asset management and project tracking."""
import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from src.config import DB_PATH


@contextmanager
def get_connection():
    """Get database connection as context manager (auto-close)."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript("""
            -- Channels: multi-channel support
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platform TEXT DEFAULT 'tiktok',
                username TEXT DEFAULT '',
                description TEXT DEFAULT '',
                niche TEXT DEFAULT '',
                stage TEXT DEFAULT 'growth',
                followers INTEGER DEFAULT 0,
                total_views INTEGER DEFAULT 0,
                total_likes INTEGER DEFAULT 0,
                videos_posted INTEGER DEFAULT 0,
                avatar_path TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT
            );

            -- Series: content series per channel
            CREATE TABLE IF NOT EXISTS series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                theme TEXT DEFAULT '',
                characters TEXT DEFAULT '[]',
                episode_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                color TEXT DEFAULT '#FF6B00',
                created_at TEXT NOT NULL,
                FOREIGN KEY (channel_id) REFERENCES channels(id)
            );

            -- Assets
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                tags TEXT DEFAULT '[]',
                source TEXT DEFAULT '',
                prompt TEXT DEFAULT '',
                cost REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                project_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );

            -- Projects: now linked to channel + series
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                mode TEXT DEFAULT 'viral',
                status TEXT DEFAULT 'draft',
                script TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                channel_id INTEGER,
                series_id INTEGER,
                episode_num INTEGER,
                created_at TEXT NOT NULL,
                published_at TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                FOREIGN KEY (channel_id) REFERENCES channels(id),
                FOREIGN KEY (series_id) REFERENCES series(id)
            );

            CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type);
            CREATE INDEX IF NOT EXISTS idx_assets_tags ON assets(tags);
            CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
            CREATE INDEX IF NOT EXISTS idx_projects_channel ON projects(channel_id);
            CREATE INDEX IF NOT EXISTS idx_projects_series ON projects(series_id);
            CREATE INDEX IF NOT EXISTS idx_series_channel ON series(channel_id);
        """)


# --- Asset operations ---

def add_asset(asset_type: str, name: str, file_path: str,
              tags: list = None, source: str = "", prompt: str = "",
              cost: float = 0.0, project_id: int = None) -> int:
    """Add asset to database. Returns asset ID."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO assets (type, name, file_path, tags, source, prompt, cost, created_at, project_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (asset_type, name, file_path, json.dumps(tags or []),
             source, prompt, cost, datetime.now().isoformat(), project_id)
        )
        return cursor.lastrowid


def search_assets(asset_type: str = None, tags: list = None,
                  keyword: str = None, project_id: int = None,
                  limit: int = 20) -> list[dict]:
    """Search assets by type, tags, keyword, or project."""
    with get_connection() as conn:
        query = "SELECT * FROM assets WHERE 1=1"
        params = []

        if asset_type:
            query += " AND type = ?"
            params.append(asset_type)
        if project_id is not None:
            query += " AND project_id = ?"
            params.append(project_id)
        if keyword:
            query += " AND (name LIKE ? OR tags LIKE ? OR prompt LIKE ?)"
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw])
        if tags:
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f'"{tag}"')

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


# --- Project operations ---

def create_project(title: str, description: str = "",
                   mode: str = "viral", channel_id: int = None,
                   series_id: int = None, episode_num: int = None) -> int:
    """Create new content project. Returns project ID."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO projects (title, description, mode, channel_id, series_id, episode_num, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, description, mode, channel_id, series_id, episode_num,
             datetime.now().isoformat())
        )
        return cursor.lastrowid


def update_project(project_id: int, **kwargs):
    """Update project fields."""
    valid_fields = {"title", "description", "mode", "status", "script", "tags", "published_at"}
    updates = {k: v for k, v in kwargs.items() if k in valid_fields}
    if not updates:
        return

    if "tags" in updates and isinstance(updates["tags"], list):
        updates["tags"] = json.dumps(updates["tags"])

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [project_id]
    with get_connection() as conn:
        conn.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", values)


def get_project(project_id: int) -> dict | None:
    """Get project by ID."""
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return dict(row) if row else None


def list_projects(status: str = None, limit: int = 20) -> list[dict]:
    """List projects, optionally filtered by status."""
    with get_connection() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM projects WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM projects ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]


# --- Channel operations ---

def create_channel(name: str, platform: str = "tiktok",
                   username: str = "", niche: str = "",
                   description: str = "") -> int:
    """Create a new channel. Returns channel ID."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO channels (name, platform, username, niche, description, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, platform, username, niche, description, datetime.now().isoformat())
        )
        return cursor.lastrowid


def update_channel(channel_id: int, **kwargs):
    """Update channel fields (followers, views, stage, etc.)."""
    valid = {"name", "platform", "username", "description", "niche", "stage",
             "followers", "total_views", "total_likes", "videos_posted", "avatar_path"}
    updates = {k: v for k, v in kwargs.items() if k in valid}
    if not updates:
        return
    updates["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [channel_id]
    with get_connection() as conn:
        conn.execute(f"UPDATE channels SET {set_clause} WHERE id = ?", values)


def get_channel(channel_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM channels WHERE id = ?", (channel_id,)).fetchone()
        return dict(row) if row else None


def list_channels() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM channels ORDER BY created_at").fetchall()
        return [dict(r) for r in rows]


# --- Series operations ---

def create_series(channel_id: int, name: str, description: str = "",
                  theme: str = "", characters: list = None,
                  color: str = "#FF6B00") -> int:
    """Create a content series under a channel. Returns series ID."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO series (channel_id, name, description, theme, characters, color, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (channel_id, name, description, theme,
             json.dumps(characters or []), color, datetime.now().isoformat())
        )
        return cursor.lastrowid


def list_series(channel_id: int = None) -> list[dict]:
    with get_connection() as conn:
        if channel_id:
            rows = conn.execute(
                "SELECT * FROM series WHERE channel_id = ? ORDER BY created_at", (channel_id,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM series ORDER BY created_at").fetchall()
        return [dict(r) for r in rows]


def get_series(series_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM series WHERE id = ?", (series_id,)).fetchone()
        return dict(row) if row else None


def update_series(series_id: int, **kwargs):
    valid = {"name", "description", "theme", "characters", "episode_count", "status", "color"}
    updates = {k: v for k, v in kwargs.items() if k in valid}
    if not updates:
        return
    if "characters" in updates and isinstance(updates["characters"], list):
        updates["characters"] = json.dumps(updates["characters"])
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [series_id]
    with get_connection() as conn:
        conn.execute(f"UPDATE series SET {set_clause} WHERE id = ?", values)


# --- Stats queries ---

def get_channel_stats(channel_id: int) -> dict:
    """Get aggregated stats for a channel."""
    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*) as total_projects,
                SUM(CASE WHEN status='published' THEN 1 ELSE 0 END) as published,
                SUM(CASE WHEN status='draft' THEN 1 ELSE 0 END) as drafts,
                SUM(CASE WHEN status='review' THEN 1 ELSE 0 END) as in_review,
                SUM(views) as total_views,
                SUM(likes) as total_likes,
                SUM(comments) as total_comments,
                SUM(shares) as total_shares
            FROM projects WHERE channel_id = ?
        """, (channel_id,)).fetchone()
        return dict(row) if row else {}


def get_series_stats(series_id: int) -> dict:
    """Get aggregated stats for a series."""
    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*) as total_episodes,
                SUM(CASE WHEN status='published' THEN 1 ELSE 0 END) as published,
                SUM(views) as total_views,
                SUM(likes) as total_likes
            FROM projects WHERE series_id = ?
        """, (series_id,)).fetchone()
        return dict(row) if row else {}


# Initialize on import
init_db()
