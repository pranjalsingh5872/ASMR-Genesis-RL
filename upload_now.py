import os
import json
from dotenv import load_dotenv
from instagram_publisher import InstagramPublisher

load_dotenv()

video_path = os.path.abspath("output/rendered/FINAL_SCENE1_ASMR_PERFECT_PHYSICS.mp4")
thumbnail_path = os.path.abspath("output/rendered/reel_cover.jpg")

caption = """0% to 100% Soft Gold Physics ✨ Which level felt the most satisfying? 👇

0% SOFT - Rigid ricochet
25% SOFT - Stiff compression
50% SOFT - Silicone flex & squish
75% SOFT - Stretchy jelly glide
100% SOFT - Pure molten liquid gold

🎧 Headphones recommended for 3D ASMR Foley audio.

#asmr #3dasmr #satisfying #blender3d #oddlysatisfying #physics #render #satisfyingvideos #asmrsounds #gold #asmrcommunity #cyclesrender"""

print(f"[*] Initializing Instagram Publisher for upload...")
print(f"[*] Video: {video_path}")
print(f"[*] Thumbnail: {thumbnail_path}")

publisher = InstagramPublisher()
result = publisher.publish_reel(
    video_path=video_path,
    caption=caption,
    thumbnail_path=thumbnail_path
)

print("\n" + "="*50)
print("[SUCCESS] Reel published successfully to Instagram!")
print(f"Media PK: {result.get('pk')}")
print(f"Media ID: {result.get('id')}")
code = result.get('code')
if code:
    print(f"Reel URL: https://www.instagram.com/reel/{code}/")
print("="*50)

# Save result log
with open("output/rendered/last_upload_result.json", "w") as f:
    # Handle non-serializable objects cleanly
    clean_res = {k: str(v) for k, v in result.items() if not k.startswith("_")}
    json.dump(clean_res, f, indent=2)
