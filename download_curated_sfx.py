import os
import subprocess
import glob
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print(f"[*] Using FFmpeg binary: {ffmpeg_exe}")

os.makedirs("assets/raw_sfx", exist_ok=True)
os.makedirs("assets/curated_sfx", exist_ok=True)

SOUNDS = [
    {"id": "aQ6BLCZOogs", "name": "glass_ping", "start": 0.0, "dur": 2.0},
    {"id": "k_be4Ghyk4g", "name": "marble_drop", "start": 0.5, "dur": 2.5},
    {"id": "M7wmtlDGfBM", "name": "marble_impact", "start": 0.0, "dur": 2.0},
    {"id": "uIKy_BALcoY", "name": "metal_ping", "start": 0.2, "dur": 2.0},
    {"id": "r1AXeHlpx8I", "name": "slime_squish", "start": 0.0, "dur": 2.5},
    {"id": "NRkY5ExbzF8", "name": "slime_stretch", "start": 0.2, "dur": 3.0},
    {"id": "FBOpf0mi0Lw", "name": "water_drip", "start": 0.0, "dur": 2.0},
    {"id": "JC7iPyUScZc", "name": "marbles_collide", "start": 1.0, "dur": 3.0},
]

for item in SOUNDS:
    vid = item["id"]
    name = item["name"]
    wav_target = f"assets/curated_sfx/{name}.wav"
    raw_target = f"assets/raw_sfx/{name}.m4a"

    if os.path.exists(wav_target):
        print(f"[=] Already ready: {wav_target}")
        continue

    url = f"https://www.youtube.com/watch?v={vid}"
    cmd = [
        "yt-dlp",
        "--ffmpeg-location", ffmpeg_exe,
        "-f", "bestaudio[ext=m4a]/bestaudio",
        "-o", f"assets/raw_sfx/{name}.%(ext)s",
        "--no-playlist",
        url
    ]
    print(f"[-] Downloading {name} ({vid})...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] yt-dlp error: {res.stderr}")
    
    # Locate any downloaded file
    files = glob.glob(f"assets/raw_sfx/{name}.*")
    if files:
        downloaded = files[0]
        trim_cmd = [
            ffmpeg_exe, "-y",
            "-ss", str(item["start"]),
            "-i", downloaded,
            "-t", str(item["dur"]),
            "-ac", "2",
            "-ar", "44100",
            wav_target
        ]
        trim_res = subprocess.run(trim_cmd, capture_output=True, text=True)
        if os.path.exists(wav_target):
            print(f"[+] Extracted pristine Foley WAV: {wav_target}")
        else:
            print(f"[!] Trimming failed: {trim_res.stderr}")
    else:
        print(f"[!] No downloaded file found for {name}")

print("[*] All Foley sound effects processed.")
