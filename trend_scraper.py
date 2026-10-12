import os
import json
import hashlib
from typing import List, Dict, Any
import yt_dlp

class TrendScraper:
    """
    Searches and discovers top viral 3D ASMR and oddly satisfying videos
    using yt-dlp (YouTube Shorts / Creative Commons / Viral Satisfying Trends).
    No API keys or payment required.
    """

    DEFAULT_QUERIES = [
        "3d asmr oddly satisfying blender render shorts",
        "satisfying 3d animation simulation shorts",
        "kinetic sand 3d asmr shorts",
        "soft body physics satisfying 3d shorts"
    ]

    def __init__(self, history_file: str = "history.json"):
        self.history_file = history_file
        self.history = self._load_history()

    def _load_history(self) -> set:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return set(data.get("seen_ids", []))
            except Exception:
                return set()
        return set()

    def save_history(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump({"seen_ids": list(self.history)}, f, indent=2)

    def is_duplicate(self, video_id: str, title: str) -> bool:
        """Check if video was already scheduled, processed, or uploaded."""
        title_hash = hashlib.md5(title.strip().lower().encode('utf-8')).hexdigest()
        return video_id in self.history or title_hash in self.history

    def mark_seen(self, video_id: str, title: str):
        self.history.add(video_id)
        self.history.add(hashlib.md5(title.strip().lower().encode('utf-8')).hexdigest())
        self.save_history()

    def search_viral_trends(self, count: int = 7) -> List[Dict[str, Any]]:
        """
        Searches for top trending short videos and filters out any duplicates.
        """
        discovered = []
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "default_search": "ytsearch20",
        }

        print(f"[*] Discovering viral 3D ASMR trends (target: {count} unique videos)...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for query in self.DEFAULT_QUERIES:
                if len(discovered) >= count:
                    break
                try:
                    result = ydl.extract_info(f"ytsearch15:{query}", download=False)
                    if not result or "entries" not in result:
                        continue

                    for entry in result["entries"]:
                        if not entry:
                            continue

                        vid_id = entry.get("id")
                        title = entry.get("title", "")
                        url = entry.get("url") or f"https://www.youtube.com/watch?v={vid_id}"
                        duration = entry.get("duration") or 0

                        # We target vertical shorts / reels length (between 5 and 60 seconds)
                        if duration and (duration > 65 or duration < 4):
                            continue

                        # Strict anti-duplicate check
                        if self.is_duplicate(vid_id, title):
                            print(f"[-] Skipping duplicate: {title}")
                            continue

                        discovered.append({
                            "video_id": vid_id,
                            "title": title,
                            "url": url,
                            "duration": duration
                        })
                        self.mark_seen(vid_id, title)

                        print(f"[+] Found unique trend ({len(discovered)}/{count}): {title}")
                        if len(discovered) >= count:
                            break

                except Exception as e:
                    print(f"[-] Search error for query '{query}': {e}")

        return discovered
