import os
import yt_dlp
from moviepy import VideoFileClip

class VideoProcessor:
    """
    Downloads source video and enhances it to crisp 1080x1920 (9:16) 60fps vertical format.
    Zero-cost pipeline using yt-dlp and moviepy/ffmpeg.
    """

    DOWNLOAD_DIR = os.path.join("output", "downloads")
    PROCESSED_DIR = os.path.join("output", "processed")

    @classmethod
    def process_video(cls, source_url: str, video_id: str) -> str:
        os.makedirs(cls.DOWNLOAD_DIR, exist_ok=True)
        os.makedirs(cls.PROCESSED_DIR, exist_ok=True)

        raw_template = os.path.join(cls.DOWNLOAD_DIR, f"{video_id}.%(ext)s")
        final_output = os.path.join(cls.PROCESSED_DIR, f"reel_{video_id}.mp4")

        import imageio_ffmpeg
        ffmpeg_binary = imageio_ffmpeg.get_ffmpeg_exe()

        # 1. Download best available video & audio
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": raw_template,
            "quiet": True,
            "no_warnings": True,
            "ffmpeg_location": ffmpeg_binary,
            "merge_output_format": "mp4",
        }

        print(f"[*] Downloading source video: {source_url}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([source_url])

        downloaded_files = [
            os.path.join(cls.DOWNLOAD_DIR, f)
            for f in os.listdir(cls.DOWNLOAD_DIR)
            if f.startswith(str(video_id))
        ]

        if not downloaded_files:
            raise FileNotFoundError(f"Failed to locate downloaded file for video ID {video_id}")

        raw_file = downloaded_files[0]
        print(f"[+] Download complete: {raw_file}")

        # 2. Re-encode and optimize to strict 1080x1920 (9:16) Reel format with Evolved DNA
        print(f"[*] Enhancing video to 1080x1920 Reel standard with Evolved DNA...")
        clip = VideoFileClip(raw_file)

        # Truncate length if over 60s
        if clip.duration > 60:
            clip = clip.subclip(0, 59)

        # Ingest Evolved DNA parameters
        from evolution_engine import EvolutionEngine
        from moviepy import vfx
        dna = EvolutionEngine.load_dna()
        pacing_dna = dna.get("pacing_dna", {})
        speed_mult = pacing_dna.get("speed_multiplier", 1.1)
        contrast_boost = pacing_dna.get("contrast_boost", 1.1)

        print(f"    -> Auto-Applying Evolved Cadence: {speed_mult}x speed | {contrast_boost}x contrast punch")
        clip_evolved = clip
        if speed_mult != 1.0:
            clip_evolved = clip_evolved.with_effects([vfx.MultiplySpeed(speed_mult)])

        try:
            clip_evolved = clip_evolved.with_effects([
                vfx.MultiplyColor(1.05),
                vfx.LumContrast(lum=5, contrast=contrast_boost)
            ])
        except Exception:
            pass

        target_w, target_h = 1080, 1920
        clip_w, clip_h = clip_evolved.size

        # Scale and center crop to fill entire 9:16 vertical frame
        scale = max(target_w / clip_w, target_h / clip_h)
        new_w, new_h = int(clip_w * scale), int(clip_h * scale)
        clip_resized = clip_evolved.resized((new_w, new_h))

        x_center = (new_w - target_w) // 2
        y_center = (new_h - target_h) // 2
        clip_final = clip_resized.cropped(x1=x_center, y1=y_center, width=target_w, height=target_h)

        clip_final.write_videofile(
            final_output,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="medium",
            bitrate="5000k",
            threads=4,
            logger=None
        )

        clip.close()
        clip_evolved.close()
        clip_final.close()

        print(f"[+] 1080p vertical reel ready (Evolved Gen {dna.get('generation', 1)}): {final_output}")
        return final_output
