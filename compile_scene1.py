import os
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

frames_dir = "output/physics_scene1_frames"
overlay_dir = "output/scene1_annotated"
os.makedirs(overlay_dir, exist_ok=True)
os.makedirs("output/rendered", exist_ok=True)

final_video = "output/rendered/scene1_visuals.mp4"

# Timeline mapping (Frame to Stage label at 30 fps)
# 0%   (00:00 - 00:02): f1   to f60
# 25%  (00:02 - 00:05): f61  to f150
# 50%  (00:05 - 00:12): f151 to f360
# 75%  (00:12 - 00:22): f361 to f660
# 100% (00:22 - 00:26): f661 to f780

def get_label_for_frame(frame_num: int) -> str:
    if frame_num <= 60:
        return "0% SOFT"
    elif frame_num <= 150:
        return "25% SOFT"
    elif frame_num <= 360:
        return "50% SOFT"
    elif frame_num <= 660:
        return "75% SOFT"
    else:
        return "100% SOFT"

try:
    font = ImageFont.truetype("arialbd.ttf", 95)
except Exception:
    font = ImageFont.load_default()

print("[*] Annotating all 780 frames with progressive softness indicators...")
for i in range(1, 781):
    f_name = f"frame_{i:04d}.png"
    in_path = os.path.join(frames_dir, f_name)
    out_path = os.path.join(overlay_dir, f_name)

    if not os.path.exists(in_path):
        continue

    img = Image.open(in_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    text = get_label_for_frame(i)

    # Position text top center with soft shadow
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    x = (1080 - text_w) // 2
    y = 180

    # Draw shadow
    draw.text((x + 4, y + 4), text, font=font, fill=(30, 30, 30, 190))
    # Draw crisp white text
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    img.convert("RGB").save(out_path)

print("[+] All 780 frames annotated.")

# Compile into master 1080x1920 30fps MP4
print("[*] Encoding master 1080p MP4...")
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

cmd = [
    ffmpeg_exe,
    "-y",
    "-framerate", "30",
    "-i", os.path.join(overlay_dir, "frame_%04d.png"),
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "medium",
    "-crf", "18",
    final_video
]

subprocess.run(cmd, check=True)
print(f"[+] Complete 26-second demo video rendered to: {final_video}")
