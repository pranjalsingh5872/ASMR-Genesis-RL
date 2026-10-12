import os
import shutil
import time
from typing import Optional, List

class InstagramPublisher:
    """Publishes Reels to Instagram using Instagrapi with automatic post-upload disk cleanup."""

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

    @staticmethod
    def cleanup_post_upload(video_path: str, associated_paths: Optional[List[str]] = None):
        """
        Deletes the uploaded video file and heavy intermediate rendered frames/caches
        from local storage immediately after successful publication to free disk space.
        """
        print("\n" + "=" * 50)
        print("[*] POST-UPLOAD DISK CLEANUP (AUTO-PURGE)")
        print("=" * 50)
        freed_bytes = 0

        # 1. Delete uploaded MP4 file
        if os.path.exists(video_path):
            try:
                size = os.path.getsize(video_path)
                os.remove(video_path)
                freed_bytes += size
                print(f"[Cleanup] Deleted uploaded video file: {video_path} ({size / (1024*1024):.2f} MB)")
            except Exception as e:
                print(f"[Cleanup] Warning: could not delete video file {video_path}: {e}")

        # 2. Delete heavy frame caches and intermediate assets
        if associated_paths:
            for p in associated_paths:
                if not os.path.exists(p):
                    continue
                try:
                    if os.path.isdir(p):
                        dir_size = sum(
                            os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, dirnames, filenames in os.walk(p)
                            for filename in filenames
                        )
                        shutil.rmtree(p)
                        freed_bytes += dir_size
                        print(f"[Cleanup] Purged heavy frame directory: {p} ({dir_size / (1024*1024):.2f} MB)")
                    elif os.path.isfile(p):
                        size = os.path.getsize(p)
                        os.remove(p)
                        freed_bytes += size
                        print(f"[Cleanup] Deleted intermediate asset: {p} ({size / (1024*1024):.2f} MB)")
                except Exception as e:
                    print(f"[Cleanup] Warning: could not remove path {p}: {e}")

        print(f"[SUCCESS] Total disk space freed: {freed_bytes / (1024*1024):.2f} MB")
        print("=" * 50 + "\n")

    def publish_reel(
        self,
        video_path: str,
        caption: str,
        thumbnail_path: Optional[str] = None,
        auto_cleanup: bool = True,
        associated_paths: Optional[List[str]] = None
    ) -> dict:
        """
        Uploads video as an Instagram Reel and automatically deletes local video
        and frame caches upon confirmation.
        """
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

        # Execute automatic disk cleanup once upload succeeds
        if auto_cleanup:
            self.cleanup_post_upload(video_path, associated_paths)

        return media.dict()
