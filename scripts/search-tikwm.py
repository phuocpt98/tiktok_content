#!/usr/bin/env python3
import urllib.parse
import urllib.request
import json
import argparse
import time
from collections import defaultdict

def tikwm_search(keyword, count=30):
    params = urllib.parse.urlencode({"keywords": keyword, "count": count})
    req = urllib.request.Request(
        f"https://www.tikwm.com/api/feed/search?{params}",
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
            if data.get("code") != 0:
                print(f"Error from tikwm: {data.get('msg')}")
                return []
            return data.get("data", {}).get("videos", [])
    except Exception as e:
        print(f"Request failed: {e}")
        return []

def rank_authors(videos):
    author_stats = defaultdict(lambda: {
        "unique_id": "",
        "nickname": "",
        "video_count": 0,
        "total_views": 0,
        "max_views": 0,
        "top_video_id": "",
        "top_video_caption": ""
    })
    
    for v in videos:
        author = v.get("author", {})
        uid = author.get("unique_id")
        if not uid: continue
        
        stats = author_stats[uid]
        stats["unique_id"] = uid
        stats["nickname"] = author.get("nickname", "")
        stats["video_count"] += 1
        
        views = v.get("play_count", 0)
        stats["total_views"] += views
        if views > stats["max_views"]:
            stats["max_views"] = views
            stats["top_video_id"] = v.get("video_id", "")
            stats["top_video_caption"] = v.get("title", "")
            
    # Sort by total views descending
    ranked = sorted(author_stats.values(), key=lambda x: x["total_views"], reverse=True)
    return ranked

def main():
    parser = argparse.ArgumentParser(description="Search TikTok via tikwm and rank top authors by engagement.")
    parser.add_argument("keywords", nargs="+", help="Keywords to search for")
    parser.add_argument("--count", type=int, default=50, help="Number of videos to fetch per keyword")
    parser.add_argument("--limit", type=int, default=10, help="Number of top authors to display")
    args = parser.parse_args()
    
    all_videos = []
    seen_ids = set()
    
    for kw in args.keywords:
        print(f"Searching for: '{kw}'...")
        videos = tikwm_search(kw, count=args.count)
        print(f"  Found {len(videos)} videos")
        for v in videos:
            vid = v.get("video_id")
            if vid and vid not in seen_ids:
                all_videos.append(v)
                seen_ids.add(vid)
        time.sleep(1.5) # Rate limit respect
        
    if not all_videos:
        print("No videos found.")
        return
        
    ranked_authors = rank_authors(all_videos)
    
    print(f"\nTop {args.limit} Authors for keywords {args.keywords}:")
    print("-" * 80)
    for i, auth in enumerate(ranked_authors[:args.limit], 1):
        print(f"{i}. @{auth['unique_id']} ({auth['nickname']})")
        print(f"   Videos in results: {auth['video_count']}")
        print(f"   Total Views: {auth['total_views']:,}")
        print(f"   Top Video: {auth['max_views']:,} views - {auth['top_video_id']}")
        print(f"   Caption: {auth['top_video_caption'][:80]}...")
        print("-" * 80)

if __name__ == "__main__":
    main()
