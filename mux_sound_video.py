import os
import subprocess
import imageio_ffmpeg

video_in = os.path.abspath("output/rendered/scene1_visuals.mp4")
audio_in = os.path.abspath("output/MASTER_SCENE1_ASMR_SOUNDTRACK.wav")
video_out = os.path.abspath("output/rendered/FINAL_SCENE1_ASMR_PERFECT_PHYSICS.mp4")

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

cmd = [
    ffmpeg_exe,
    "-y",
    "-i", video_in,
    "-i", audio_in,
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    video_out
]

print("[*] Muxing synchronized ASMR audio track into 1080p video...")
subprocess.run(cmd, check=True)
print(f"[+] Final Video with Sound is ready: {video_out}")
