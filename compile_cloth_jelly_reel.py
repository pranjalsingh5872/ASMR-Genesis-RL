import os
import subprocess
import shutil

frames_dir = os.path.abspath("output/cloth_jelly_60fps_frames")
audio_file = os.path.abspath("output/rendered/cloth_jelly_60fps_foley.wav")
output_mp4 = os.path.abspath("output/rendered/FINAL_60FPS_CLOTH_JELLY_ASMR.mp4")
cover_jpg = os.path.abspath("output/rendered/FINAL_60FPS_CLOTH_JELLY_ASMR_cover.jpg")

ffmpeg_exe = shutil.which("ffmpeg")
if not ffmpeg_exe:
    # Check default common paths or environment
    potential_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\ProgramData\chocolatey\bin\ffmpeg.exe",
        r"C:\Users\priya\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe",
    ]
    for p in potential_paths:
        if os.path.exists(p):
            ffmpeg_exe = p
            break

if not ffmpeg_exe:
    ffmpeg_exe = "ffmpeg"

print(f"[*] Using FFmpeg: {ffmpeg_exe}")

# Check frames count
frames = [f for f in os.listdir(frames_dir) if f.endswith(".png")]
print(f"[*] Found {len(frames)} frames in {frames_dir}")

if len(frames) == 0:
    print("[!] No frames found to compile!")
    exit(1)

# Frame pattern: frame_%04d.png
input_pattern = os.path.join(frames_dir, "frame_%04d.png")

# Compile command: 60 FPS, high quality H.264, AAC audio
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

print(f"[*] Encoding 60 FPS Video with FFmpeg...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print(f"[!] FFmpeg error:\n{res.stderr}")
    exit(1)

print(f"[SUCCESS] Video compiled: {output_mp4}")

# Extract frame 38 as thumbnail cover
cover_src = os.path.join(frames_dir, "frame_0038.png")
if os.path.exists(cover_src):
    shutil.copyfile(cover_src, cover_jpg)
    print(f"[SUCCESS] Reel cover generated: {cover_jpg}")
else:
    print(f"[*] Frame 38 not found, extracting frame from MP4...")
    cmd_cover = [
        ffmpeg_exe,
        "-y",
        "-ss", "00:00:00.600",
        "-i", output_mp4,
        "-vframes", "1",
        "-q:v", "2",
        cover_jpg
    ]
    subprocess.run(cmd_cover, capture_output=True)
    print(f"[SUCCESS] Cover extracted: {cover_jpg}")
