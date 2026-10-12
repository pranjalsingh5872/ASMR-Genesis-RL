import os
import sys
import time
from dotenv import load_dotenv

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()
from instagram_publisher import InstagramPublisher

videos_to_upload = [
    {
        "path": os.path.abspath("output/rendered/MASTER_ASMR_3D_FULL_VIDEO.mp4"),
        "caption": "0% SOFT vs 100% SOFT 🤯✨ (Blender 3D Physics ASMR)\n\nWhich stage was the most satisfying? 🎧 Drop your favorite below!\n\n#ASMRVerse3D #3DASMR #Blender3D #OddlySatisfying #Satisfying3D #SoftBody #Physics #Reels #Explore"
    },
    {
        "path": os.path.abspath("output/rendered/scene1_full_softness_demo.mp4"),
        "caption": "Curved Glass Funnel & Gold Capsule 🧪✨ (0% to 100% Softness)\n\nWatch till the end 🎧\n\n#3danimation #blenderrender #asmr #oddlysatisfying #satisfyingvideo #reelsinstagram"
    },
    {
        "path": os.path.abspath("output/rendered/scene2_full_softness_demo.mp4"),
        "caption": "Marble Snowman vs Golden Ring 🪐✨ Pure relaxation.\n\n🎧 Wear headphones!\n\n#asmrcommunity #satisfying #blenderart #3dphysics #trendingreels #reels"
    },
    {
        "path": os.path.abspath("output/rendered/scene3_full_softness_demo.mp4"),
        "caption": "3 Marble Stairs into Glass Tubes 🌊✨ 0% vs 100% Softness!\n\nCan't stop watching this loop 🤯\n\n#blender3d #physicsanimation #satisfyingposts #asmrvideos #explorepage"
    },
    {
        "path": os.path.abspath("output/processed/reel_LStudgWrJ4Q.mp4"),
        "caption": "Fluid FX in 3D ✨ Oddly satisfying liquid simulation.\n\n🎧 Sound ON!\n\n#satisfying #3dsimulation #blendershorts #asmr #reels"
    },
    {
        "path": os.path.abspath("output/processed/reel_4XaY3CPE5mU.mp4"),
        "caption": "Soft Body 3D Bliss ✨ Perfect loop.\n\nSave this for later 📌\n\n#oddlysatisfying #3d #asmr #reelsinstagram #viralreels"
    },
    {
        "path": os.path.abspath("output/processed/reel_QdS0QRh53RA.mp4"),
        "caption": "Satisfying 3D Physics 🤤✨ Relax your mind.\n\n#relaxingvideos #3danimation #asmrloop #blender3d #explore"
    }
]

print("=" * 60)
print(f"[*] BATCH UPLOADER: {len(videos_to_upload)} Videos Scheduled for Instagram")
print("=" * 60)

publisher = InstagramPublisher()

for idx, item in enumerate(videos_to_upload, 1):
    video_path = item["path"]
    caption = item["caption"]

    if not os.path.exists(video_path):
        print(f"[-] Video not found, skipping: {video_path}")
        continue

    print(f"\n[{idx}/{len(videos_to_upload)}] Uploading: {os.path.basename(video_path)}...")
    try:
        res = publisher.publish_reel(video_path=video_path, caption=caption)
        print(f"[+] SUCCESS! Media ID: {res.get('pk')}")
    except Exception as e:
        print(f"[-] Upload failed for {os.path.basename(video_path)}: {e}")

    # Wait 30 seconds between uploads to respect Instagram rate limits
    if idx < len(videos_to_upload):
        print("[*] Cooling down for 30s to stay within Instagram safety limits...")
        time.sleep(30)

print("\n🎉 Batch upload complete!")
