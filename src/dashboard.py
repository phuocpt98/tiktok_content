"""Dashboard — visual statistics for channels, series, and content."""
import json
from datetime import datetime
from src.database import (
    list_channels, get_channel, get_channel_stats,
    list_series, get_series_stats,
    list_projects, search_assets
)


def _n(val):
    """Convert None to 0 for numeric formatting."""
    return val if val is not None else 0


def generate_dashboard() -> str:
    """Generate full dashboard as formatted text."""
    lines = []
    lines.append("=" * 60)
    lines.append("  TIKTOK CONTENT DASHBOARD")
    lines.append(f"  Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)

    channels = list_channels()
    if not channels:
        lines.append("\n  (Chua co kenh nao. Tao kenh dau tien!)")
        return "\n".join(lines)

    for ch in channels:
        stats = get_channel_stats(ch["id"])
        total = _n(stats.get("total_projects"))
        pub = _n(stats.get("published"))
        drafts = _n(stats.get("drafts"))
        review = _n(stats.get("in_review"))
        views = _n(stats.get("total_views"))
        likes = _n(stats.get("total_likes"))
        comments = _n(stats.get("total_comments"))

        lines.append("")
        lines.append(f"  KENH: {ch['name']} ({ch['platform']})")
        lines.append(f"  @{ch['username']}  |  Niche: {ch['niche']}")
        lines.append(f"  Stage: {ch['stage']}  |  Followers: {ch['followers']:,}")
        lines.append(f"  Content:  {total} total | {pub} published | {drafts} drafts | {review} review")
        lines.append(f"  Reach:    {views:,} views | {likes:,} likes | {comments:,} comments")
        lines.append("")

        # Series under this channel
        channel_series = list_series(channel_id=ch["id"])
        if channel_series:
            lines.append("  -- Series --")
            for s in channel_series:
                ss = get_series_stats(s["id"])
                eps = _n(ss.get("total_episodes"))
                sv = _n(ss.get("total_views"))
                status_mark = "[ON]" if s["status"] == "active" else "[OFF]"
                chars = json.loads(s["characters"]) if s["characters"] else []
                char_str = ", ".join(chars[:3]) if chars else "-"
                lines.append(f"  {status_mark} {s['name']}  |  {eps} eps  |  {sv:,} views  |  Characters: {char_str}")
        else:
            lines.append("  (Chua co series)")

        lines.append("-" * 60)

    # Asset summary
    lines.append("")
    lines.append("-- ASSET LIBRARY --")
    for asset_type in ["image", "video", "audio", "text"]:
        items = search_assets(asset_type=asset_type, limit=1000)
        lines.append(f"  {asset_type:6s}: {len(items)} files")

    # Recent projects
    recent = list_projects(limit=5)
    if recent:
        lines.append("")
        lines.append("-- RECENT CONTENT --")
        for p in recent:
            status_map = {"draft": "[D]", "in_progress": "[W]", "review": "[R]", "published": "[P]"}
            icon = status_map.get(p["status"], "[?]")
            ch_name = ""
            if p.get("channel_id"):
                c = get_channel(p["channel_id"])
                ch_name = f" [{c['name']}]" if c else ""
            lines.append(f"  {icon} #{p['id']} {p['title'][:40]}{ch_name}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def generate_series_detail(series_id: int) -> str:
    """Generate detailed view for a specific series."""
    from src.database import get_series
    s = get_series(series_id)
    if not s:
        return f"Series #{series_id} not found"

    stats = get_series_stats(series_id)
    chars = json.loads(s["characters"]) if s["characters"] else []
    projects = list_projects(limit=50)
    series_projects = [p for p in projects if p.get("series_id") == series_id]

    lines = []
    lines.append(f"=== SERIES: {s['name']} ===")
    lines.append(f"Theme: {s['theme']}")
    lines.append(f"Status: {s['status']}  |  Episodes: {_n(stats.get('total_episodes'))}")
    lines.append(f"Views: {_n(stats.get('total_views')):,}  |  Likes: {_n(stats.get('total_likes')):,}")
    lines.append(f"Characters: {', '.join(chars) if chars else 'None'}")
    lines.append("")

    if series_projects:
        lines.append("Episodes:")
        for p in sorted(series_projects, key=lambda x: x.get("episode_num") or 0):
            ep = p.get("episode_num") or "?"
            lines.append(f"  EP{ep:>3}  {p['title'][:40]}  |  {p['status']}  |  {_n(p.get('views')):,} views")
    else:
        lines.append("(No episodes yet)")

    return "\n".join(lines)
