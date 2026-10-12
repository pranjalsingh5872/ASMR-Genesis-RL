import os
import subprocess
from typing import Optional

class VideoComposer:
    """Formats videos into Instagram Reels standard (1080x1920, 9:16 vertical ratio)."""

    @staticmethod
    def format_reel(input_video_path: str, output_video_path: str, audio_path: Optional[str] = None) -> str:
        """
        Processes video to ensure 1080x1920 9:16 vertical resolution, optimal bitrate,
        and optionally adds/layers audio.
        Uses moviepy/imageio-ffmpeg under the hood.
        """
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip

            print(f"[VideoComposer] Loading {input_video_path}...")
            clip = VideoFileClip(input_video_path)

            # Ensure 9:16 ratio (1080x1920)
            target_w, target_h = 1080, 1920
            clip_w, clip_h = clip.size

            # Resize keeping aspect ratio or cropping to fit 9:16
            scale = max(target_w / clip_w, target_h / clip_h)
            new_w, new_h = int(clip_w * scale), int(clip_h * scale)
            clip = clip.resize((new_w, new_h))

            # Crop to exact 1080x1920 centered
            x1 = (new_w - target_w) // 2
            y1 = (new_h - target_h) // 2
            clip = clip.crop(x1=x1, y1=y1, width=target_w, height=target_h)

            if audio_path and os.path.exists(audio_path):
                print(f"[VideoComposer] Attaching ASMR audio from {audio_path}...")
                audio = AudioFileClip(audio_path).subclip(0, min(clip.duration, AudioFileClip(audio_path).duration))
                clip = clip.set_audio(audio)

            os.makedirs(os.path.dirname(os.path.abspath(output_video_path)), exist_ok=True)
            clip.write_videofile(
                output_video_path,
                codec="libx264",
                audio_codec="aac",
                fps=60,
                threads=4,
                preset="fast"
            )
            clip.close()
            print(f"[VideoComposer] Final reel exported to {output_video_path}")
            return output_video_path

        except Exception as e:
            print(f"[VideoComposer] Error processing video: {e}")
            raise
