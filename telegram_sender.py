import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

def get_or_detect_chat_id() -> str:
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if chat_id and chat_id.strip():
        return chat_id.strip()

    print("[*] Polling Telegram bot updates to find your chat ID...")
    res = requests.get(f"{API_URL}/getUpdates").json()
    if res.get("ok") and res.get("result"):
        # Get the latest message's chat ID
        latest = res["result"][-1]
        if "message" in latest:
            found_id = str(latest["message"]["chat"]["id"])
            print(f"[+] Found Chat ID: {found_id}")
            
            # Save to .env
            env_path = os.path.abspath(".env")
            with open(env_path, "r") as f:
                content = f.read()
            if "TELEGRAM_CHAT_ID=" in content:
                content = content.replace("TELEGRAM_CHAT_ID=", f"TELEGRAM_CHAT_ID={found_id}")
            else:
                content += f"\nTELEGRAM_CHAT_ID={found_id}\n"
            with open(env_path, "w") as f:
                f.write(content)
            print("[+] Saved TELEGRAM_CHAT_ID to .env")
            return found_id

    return None

def send_message(chat_id: str, text: str):
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    res = requests.post(url, json=payload).json()
    return res

def send_photo(chat_id: str, photo_path: str, caption: str = ""):
    url = f"{API_URL}/sendPhoto"
    with open(photo_path, "rb") as f:
        files = {"photo": f}
        data = {"chat_id": chat_id, "caption": caption}
        res = requests.post(url, data=data, files=files).json()
    return res

def send_video(chat_id: str, video_path: str, caption: str = "", thumb_path: str = None):
    url = f"{API_URL}/sendVideo"
    with open(video_path, "rb") as f_vid:
        files = {"video": f_vid}
        if thumb_path and os.path.exists(thumb_path):
            with open(thumb_path, "rb") as f_thumb:
                files["thumbnail"] = f_thumb
                data = {
                    "chat_id": chat_id,
                    "caption": caption[:1024],  # Telegram max caption limit
                    "supports_streaming": True
                }
                res = requests.post(url, data=data, files=files).json()
                return res
        data = {
            "chat_id": chat_id,
            "caption": caption[:1024],
            "supports_streaming": True
        }
        res = requests.post(url, data=data, files=files).json()
    return res

def deliver_latest_reel_package():
    chat_id = get_or_detect_chat_id()
    if not chat_id:
        print("[!] No Chat ID found yet. Please send a message (like /start) to https://t.me/ASMR_Automateon_Bot first!")
        return False

    video_path = os.path.abspath("output/rendered/FINAL_SCENE1_ASMR_PERFECT_PHYSICS.mp4")
    cover_path = os.path.abspath("output/rendered/reel_cover.jpg")
    pfp_path = os.path.abspath("output/profile_pic.jpg")

    caption_text = """0% to 100% Soft Gold Physics ✨ Which level felt the most satisfying? 👇

0% SOFT - Rigid ricochet
25% SOFT - Stiff compression
50% SOFT - Silicone flex & squish
75% SOFT - Stretchy jelly glide
100% SOFT - Pure molten liquid gold

🎧 Put on headphones for 3D ASMR Foley audio.

#asmr #3dasmr #oddlysatisfying #satisfying #blender3d #satisfyingvideos #physics #cyclesrender #asmrsounds #gold #relaxing #reelsviral #explorepage"""

    print("[*] Sending Status Notification...")
    send_message(chat_id, "🚀 *New 3D ASMR Reel Ready For Review & Upload!*")

    if os.path.exists(pfp_path):
        print("[*] Sending Profile Picture...")
        send_photo(chat_id, pfp_path, caption="✨ New Channel Profile Picture (Logo)")

    if os.path.exists(cover_path):
        print("[*] Sending Reel Cover...")
        send_photo(chat_id, cover_path, caption="🖼️ Reel Cover Thumbnail (High Curiosity Framing)")

    if os.path.exists(video_path):
        print(f"[*] Sending 1080p 60fps ASMR Video ({os.path.getsize(video_path)} bytes)...")
        send_video(chat_id, video_path, caption=caption_text, thumb_path=cover_path)

    print("[*] Sending ready-to-copy caption block...")
    send_message(chat_id, f"📋 *Copy-Paste Caption & Hashtags:*\n\n`{caption_text}`")

    print("[SUCCESS] Complete ASMR package sent to your Telegram!")
    return True

if __name__ == "__main__":
    deliver_latest_reel_package()
