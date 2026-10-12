import subprocess
import os

blender_exe = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
test_frames = [24, 110, 250, 520, 740]
os.makedirs("output/test_preview_frames", exist_ok=True)

for f in test_frames:
    print(f"[*] Rendering test frame {f}...")
    cmd = [
        blender_exe,
        "-b",
        "-P", "build_physics_scene1.py",
        "-o", os.path.abspath(f"output/test_preview_frames/frame_{f:04d}"),
        "-f", str(f)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[+] Frame {f} rendered successfully.")
    else:
        print(f"[!] Frame {f} failed: {res.stderr}")

print("[*] All preview frames rendered.")
