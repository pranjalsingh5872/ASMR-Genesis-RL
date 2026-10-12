import os
import json
from dotenv import load_dotenv
from instagram_publisher import InstagramPublisher

load_dotenv()

video_path = os.path.abspath("output/rendered/FINAL_60FPS_CLOTH_JELLY_ASMR.mp4")
thumbnail_path = os.path.abspath("output/rendered/FINAL_60FPS_CLOTH_JELLY_ASMR_cover.jpg")

if not os.path.exists(video_path):
    print(f"[!] Error: Target video does not exist: {video_path}")
    exit(1)

caption = """100% Organic Cloth Pressure Jelly in 60 FPS ✨ Liquid 24K Gold on Italian Verde Alpi Marble 🌿

Vertex-level soft-body physics simulation with hydrostatic volume conservation & harmonic jiggle resonance. 

🎧 Wear headphones for binaural 3D ASMR Foley audio!
Which moment felt the most satisfying? The initial drop or the pancake squish? 👇

#asmr #satisfying #oddlysatisfying #blender3d #cyclesrender #60fps #softbody #jelly #asmrcommunity #satisfyingvideos #3danimation #asmrsounds #gold"""

print(f"[*] Initializing Instagram Publisher for 60 FPS Cloth Jelly Reel...")
print(f"[*] Target Video: {video_path}")
print(f"[*] Thumbnail: {thumbnail_path}")

frames_dir = os.path.abspath("output/cloth_jelly_60fps_frames")
wav_path = os.path.abspath("output/rendered/cloth_jelly_60fps_foley.wav")

publisher = InstagramPublisher()
result = publisher.publish_reel(
    video_path=video_path,
    caption=caption,
    thumbnail_path=thumbnail_path,
    auto_cleanup=True,
    associated_paths=[frames_dir, wav_path]
)

print("\n" + "="*50)
print("[SUCCESS] 60 FPS Cloth Jelly Reel published successfully to Instagram!")
print(f"Media PK: {result.get('pk')}")
print(f"Media ID: {result.get('id')}")
code = result.get('code')
if code:
    print(f"Reel URL: https://www.instagram.com/reel/{code}/")
print("="*50)

# Save upload result log
with open("output/rendered/last_upload_result.json", "w") as f:
    clean_res = {k: str(v) for k, v in result.items() if not k.startswith("_")}
    json.dump(clean_res, f, indent=2)
