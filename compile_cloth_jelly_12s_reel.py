import os
import subprocess
import shutil

frames_dir = os.path.abspath("output/cloth_jelly_12s_60fps_frames")
audio_file = os.path.abspath("output/rendered/cloth_jelly_12s_60fps_foley.wav")
output_mp4 = os.path.abspath("output/rendered/FINAL_12S_60FPS_CLOTH_JELLY_ASMR.mp4")
cover_jpg = os.path.abspath("output/rendered/FINAL_12S_60FPS_CLOTH_JELLY_ASMR_cover.jpg")

ffmpeg_exe = shutil.which("ffmpeg")
if not ffmpeg_exe:
    potential_paths = [
        r"C:\Users\priya\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.EXE",
        r"C:\ffmpeg\bin\ffmpeg.exe",
    ]
    for p in potential_paths:
        if os.path.exists(p):
            ffmpeg_exe = p
            break

if not ffmpeg_exe:
    ffmpeg_exe = "ffmpeg"

print(f"[*] Using FFmpeg: {ffmpeg_exe}")

frames = [f for f in os.listdir(frames_dir) if f.endswith(".png")]
print(f"[*] Found {len(frames)} frames in {frames_dir}")

if len(frames) == 0:
    print("[!] No frames found to compile!")
    exit(1)

input_pattern = os.path.join(frames_dir, "frame_%04d.png")

cmd = [
    ffmpeg_exe,
    "-y",
    "-framerate", "60",
    "-i", input_pattern,
    "-i", audio_file,
    "-c:v", "libx264",
    "-profile:v", "high",
    "-level", "4.2",
    "-pix_fmt", "yuv420p",
    "-crf", "17",
    "-c:a", "aac",
    "-b:a", "320k",
    "-shortest",
    output_mp4
]

print(f"[*] Encoding 12.0s 60 FPS Video with FFmpeg...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print(f"[!] FFmpeg error:\n{res.stderr}")
    exit(1)

print(f"[SUCCESS] 12.0s Video compiled: {output_mp4}")

# Extract frame 252 (peak pancake squish of drop 2) as cover thumbnail
cover_src = os.path.join(frames_dir, "frame_0252.png")
if os.path.exists(cover_src):
    shutil.copyfile(cover_src, cover_jpg)
    print(f"[SUCCESS] Reel cover generated: {cover_jpg}")
else:
    cover_src = os.path.join(frames_dir, "frame_0038.png")
    if os.path.exists(cover_src):
        shutil.copyfile(cover_src, cover_jpg)
        print(f"[SUCCESS] Fallback cover generated: {cover_jpg}")
