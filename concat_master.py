import os
import subprocess
import imageio_ffmpeg

v1 = os.path.abspath("output/rendered/scene1_full_softness_demo.mp4")
v2 = os.path.abspath("output/rendered/scene2_full_softness_demo.mp4")
v3 = os.path.abspath("output/rendered/scene3_full_softness_demo.mp4")

concat_file = os.path.abspath("output/rendered/concat_list.txt")
final_master = os.path.abspath("output/rendered/MASTER_ASMR_3D_FULL_VIDEO.mp4")

with open(concat_file, "w", encoding="utf-8") as f:
    f.write(f"file '{v1}'\n")
    f.write(f"file '{v2}'\n")
    f.write(f"file '{v3}'\n")

print("[*] Concatenating Scene 1, Scene 2, and Scene 3 into Master Video...")
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

cmd = [
    ffmpeg_exe,
    "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", concat_file,
    "-c", "copy",
    final_master
]

subprocess.run(cmd, check=True)
print(f"[+] Master 74-second 1080p ASMR Video created successfully: {final_master}")
