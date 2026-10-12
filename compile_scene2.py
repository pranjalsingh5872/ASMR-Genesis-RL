import os
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

frames_dir = "output/scene2_frames"
overlay_dir = "output/scene2_annotated"
os.makedirs(overlay_dir, exist_ok=True)
os.makedirs("output/rendered", exist_ok=True)

final_video = "output/rendered/scene2_full_softness_demo.mp4"

# Timeline for Scene 2 (660 frames / 22 seconds):
# 0%   (00:00 - 00:02): f1   to f75
# 25%  (00:03 - 00:06): f76  to f195
# 50%  (00:07 - 00:09): f196 to f285
# 75%  (00:10 - 00:17): f286 to f525
# 100% (00:18 - 00:22): f526 to f660

def get_label_for_frame(f: int) -> str:
    if f <= 75:
        return "0% SOFT"
    elif f <= 195:
        return "25% SOFT"
    elif f <= 285:
        return "50% SOFT"
    elif f <= 525:
        return "75% SOFT"
    else:
        return "100% SOFT"

try:
    font = ImageFont.truetype("arialbd.ttf", 95)
except Exception:
    font = ImageFont.load_default()

print("[*] Annotating Scene 2 frames with softness indicators...")
for i in range(1, 661):
    f_name = f"frame_{i:04d}.png"
    in_path = os.path.join(frames_dir, f_name)
    out_path = os.path.join(overlay_dir, f_name)

    if not os.path.exists(in_path):
        continue

    img = Image.open(in_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    text = get_label_for_frame(i)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    x = (1080 - text_w) // 2
    y = 180

    draw.text((x + 4, y + 4), text, font=font, fill=(40, 40, 40, 180))
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    img.convert("RGB").save(out_path)

print("[*] Encoding Scene 2 1080p MP4...")
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [
    ffmpeg_exe, "-y",
    "-framerate", "30",
    "-i", os.path.join(overlay_dir, "frame_%04d.png"),
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
    final_video
]
subprocess.run(cmd, check=True)
print(f"[+] Scene 2 encoded: {final_video}")
