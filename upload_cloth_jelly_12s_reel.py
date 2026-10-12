import os
import json
from dotenv import load_dotenv
from instagram_publisher import InstagramPublisher

load_dotenv()

video_path = os.path.abspath("output/rendered/FINAL_12S_60FPS_CLOTH_JELLY_ASMR.mp4")
thumbnail_path = os.path.abspath("output/rendered/FINAL_12S_60FPS_CLOTH_JELLY_ASMR_cover.jpg")

if not os.path.exists(video_path):
    print(f"[!] Error: Target video does not exist: {video_path}")
    exit(1)

caption = """12s of Pure 100% Organic Cloth Pressure Jelly in 60 FPS ✨ Liquid 24K Gold on Italian Verde Alpi Emerald Marble 🌿

Triple cascading soft-body physics simulation with real vertex-level squish, hydrostatic volume conservation & harmonic jiggle waves. 

🎧 Wear headphones for binaural 3D ASMR Foley audio!
Which drop felt the most satisfying? Drop 1, 2, or 3? 👇

#asmr #satisfying #oddlysatisfying #blender3d #cyclesrender #60fps #softbody #jelly #asmrcommunity #satisfyingvideos #3danimation #asmrsounds #gold"""

print(f"[*] Initializing Instagram Publisher for 12.0s 60 FPS Cloth Jelly Reel...")
print(f"[*] Target Video: {video_path}")
print(f"[*] Thumbnail: {thumbnail_path}")

publisher = InstagramPublisher()
result = publisher.publish_reel(
    video_path=video_path,
    caption=caption,
    thumbnail_path=thumbnail_path
)

print("\n" + "="*50)
print("[SUCCESS] 12.0s 60 FPS Cloth Jelly Reel published successfully to Instagram!")
print(f"Media PK: {result.get('pk')}")
print(f"Media ID: {result.get('id')}")
code = result.get('code')
if code:
    print(f"Reel URL: https://www.instagram.com/reel/{code}/")
print("="*50)

with open("output/rendered/last_12s_upload_result.json", "w") as f:
    clean_res = {k: str(v) for k, v in result.items() if not k.startswith("_")}
    json.dump(clean_res, f, indent=2)
