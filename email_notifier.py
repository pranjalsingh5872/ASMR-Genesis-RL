import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

class EmailNotifier:
    """Sends preview videos directly to Gmail for human review and approval."""

    @staticmethod
    def send_video_preview(to_email: str, video_path: str, title: str, notes: str = "") -> bool:
        sender_email = os.getenv("GMAIL_SENDER") or to_email
        sender_password = os.getenv("GMAIL_APP_PASSWORD")

        if not sender_password:
            print("[EmailNotifier] GMAIL_APP_PASSWORD is not set in .env.")
            print(f"[EmailNotifier] Please set GMAIL_APP_PASSWORD to enable email previews.")
            return False

        print(f"[EmailNotifier] Preparing email to {to_email}...")
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = f"🎬 New ASMR Video Ready for Approval: {title}"

        body = f"""Hello!

A new 3D ASMR video has been rendered in 1080p and is ready for your approval:

Video Title: {title}
Local File: {video_path}
{notes}

Please review the attached video sample. Once approved, reply or trigger the upload command to publish to Instagram (@asmr3dofficiall).
"""
        msg.attach(MIMEText(body, "plain"))

        # Attach MP4
        if os.path.exists(video_path):
            with open(video_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(video_path)}"',
            )
            msg.attach(part)
        else:
            print(f"[EmailNotifier] Video file not found: {video_path}")
            return False

        try:
            print("[EmailNotifier] Connecting to Gmail SMTP server...")
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            server.quit()
            print(f"[EmailNotifier] Video successfully emailed to {to_email}!")
            return True
        except Exception as e:
            print(f"[EmailNotifier] Failed to send email: {e}")
            return False
