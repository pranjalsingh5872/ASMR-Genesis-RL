import os
import time
from typing import Optional

class InstagramPublisher:
    """Publishes Reels to Instagram using Instagrapi or Meta Graph API."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.username = username or os.getenv("INSTAGRAM_USERNAME")
        self.password = password or os.getenv("INSTAGRAM_PASSWORD")
        self.cl = None

    def _login(self):
        if not self.username or not self.password:
            raise ValueError(
                "Instagram credentials missing. Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env"
            )

        from instagrapi import Client
        self.cl = Client()
        session_file = "ig_session.json"

        if os.path.exists(session_file):
            try:
                print("[InstagramPublisher] Loading saved session...")
                self.cl.load_settings(session_file)
                self.cl.login(self.username, self.password)
                return
            except Exception as e:
                print(f"[InstagramPublisher] Session expired or invalid: {e}")

        print(f"[InstagramPublisher] Logging in as {self.username}...")
        self.cl.login(self.username, self.password)
        self.cl.dump_settings(session_file)
        print("[InstagramPublisher] Login successful and session saved.")

    def publish_reel(self, video_path: str, caption: str, thumbnail_path: Optional[str] = None) -> dict:
        """Uploads video as an Instagram Reel."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if not self.cl:
            self._login()

        print(f"[InstagramPublisher] Uploading Reel: {video_path}...")
        media = self.cl.clip_upload(
            path=video_path,
            caption=caption,
            thumbnail=thumbnail_path
        )
        print(f"[InstagramPublisher] Reel published! Media ID: {media.pk}")
        return media.dict()
