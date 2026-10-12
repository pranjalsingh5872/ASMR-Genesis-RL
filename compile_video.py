import os
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

frames_dir = "output/frames"
overlay_dir = "output/overlay_frames"
os.makedirs(overlay_dir, exist_ok=True)

# Process frames and add bold "0% SOFT" 3D-style text overlay
frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith(".png")])
print(f"[*] Adding '0% SOFT' text overlay to {len(frame_files)} frames...")

# Try loading standard Windows font or default
try:
    font = ImageFont.truetype("arialbd.ttf", 90)
except Exception:
    font = ImageFont.load_default()

for f_name in frame_files:
    in_path = os.path.join(frames_dir, f_name)
    out_path = os.path.join(overlay_dir, f_name)

    img = Image.open(in_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    text = "0% SOFT"
    # Text positioning: top center
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    x = (1080 - text_w) // 2
    y = 200

    # Draw drop shadow for 3D effect
    draw.text((x + 4, y + 4), text, font=font, fill=(50, 50, 50, 200))
    # Draw white text
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    img.convert("RGB").save(out_path)

print("[+] All frames annotated with '0% SOFT' text.")

# Compile into final 1080x1920 30fps MP4
os.makedirs("output/rendered", exist_ok=True)
final_video = "output/rendered/sample_0_percent_soft.mp4"
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

cmd = [
    ffmpeg_exe,
    "-y",
    "-framerate", "30",
    "-i", os.path.join(overlay_dir, "frame_%04d.png"),
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "slow",
    "-crf", "18",
    final_video
]

print("[*] Encoding final 1080p MP4...")
subprocess.run(cmd, check=True)
print(f"[+] Final 1080p sample ready: {final_video}")
