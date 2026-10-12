import os
from datetime import datetime, timedelta
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

class ContentCalendar:
    """
    Manages the 1-week Excel schedule:
    - Creates or updates content_calendar.xlsx
    - Tracks duplicate hashes and statuses (PENDING, PROCESSED, UPLOADED)
    """

    FILE_NAME = "content_calendar.xlsx"

    COLUMNS = [
        "Day",
        "Scheduled_Date",
        "Scheduled_Time",
        "Video_ID",
        "Trend_Title",
        "Source_URL",
        "Status",
        "Retention_Score",
        "Grade",
        "Caption",
        "Local_File_Path",
        "Instagram_Post_ID"
    ]

    CAPTION_TEMPLATES = [
        "✨ Oddly satisfying 3D simulation.\n🤯 Wait till the very end!\n\n🎧 Wear headphones for full 3D sound.\n\n#ASMRVerse3D #3DASMR #Satisfying #OddlySatisfying #Blender3D #Reels #ExplorePage",
        "Can't stop watching this loop 🌊✨\n\nSound ON 🎧 What do you think of this?\n\n#asmr #satisfyingvideos #3danimation #relaxing #reelsinstagram #viralreels",
        "Pure relaxing ASMR bliss ☁️\n\nSave this for when you need to relax 📌\n\n#oddlysatisfying #3drender #asmrcommunity #reels #satisfaction #loop"
    ]

    @classmethod
    def create_or_extend_calendar(cls, trends: list, start_date: datetime = None, post_time: str = "18:00") -> str:
        start_date = start_date or datetime.now()

        # If file exists, load existing to prevent overwrite
        if os.path.exists(cls.FILE_NAME):
            df = pd.read_excel(cls.FILE_NAME)
        else:
            df = pd.DataFrame(columns=cls.COLUMNS)

        existing_ids = set(df["Video_ID"].dropna().astype(str).tolist())
        new_rows = []

        day_offset = len(df)
        for i, trend in enumerate(trends):
            vid_id = str(trend["video_id"])
            if vid_id in existing_ids:
                continue

            scheduled_date = (start_date + timedelta(days=day_offset + i)).strftime("%Y-%m-%d")
            caption = cls.CAPTION_TEMPLATES[i % len(cls.CAPTION_TEMPLATES)]

            new_rows.append({
                "Day": f"Day {day_offset + i + 1}",
                "Scheduled_Date": scheduled_date,
                "Scheduled_Time": post_time,
                "Video_ID": vid_id,
                "Trend_Title": trend["title"],
                "Source_URL": trend["url"],
                "Status": "PENDING",
                "Caption": caption,
                "Local_File_Path": "",
                "Instagram_Post_ID": ""
            })

        if new_rows:
            new_df = pd.DataFrame(new_rows)
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_excel(cls.FILE_NAME, index=False)
            cls._style_excel(cls.FILE_NAME)
            print(f"[+] Added {len(new_rows)} scheduled posts to {cls.FILE_NAME}")
        else:
            print("[*] Calendar is already up to date. No new unique rows to add.")

        return cls.FILE_NAME

    @classmethod
    def _style_excel(cls, path: str):
        """Format Excel file with clean headers and column widths."""
        wb = load_workbook(path)
        ws = wb.active

        header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        center_align = Alignment(horizontal="center", vertical="center")

        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 40)

        wb.save(path)

    @classmethod
    def get_pending_row(cls) -> dict:
        """Returns the next scheduled row that has not been uploaded."""
        if not os.path.exists(cls.FILE_NAME):
            return None
        df = pd.read_excel(cls.FILE_NAME)
        pending = df[df["Status"] == "PENDING"]
        if pending.empty:
            return None
        return pending.iloc[0].to_dict()

    @classmethod
    def update_row_status(cls, video_id: str, status: str, local_path: str = None, post_id: str = None, retention_score: float = None, grade: str = None):
        """Updates row status in Excel after processing or upload."""
        if not os.path.exists(cls.FILE_NAME):
            return
        df = pd.read_excel(cls.FILE_NAME)
        mask = df["Video_ID"].astype(str) == str(video_id)
        if mask.any():
            df.loc[mask, "Status"] = status
            if local_path:
                df.loc[mask, "Local_File_Path"] = local_path
            if post_id:
                df.loc[mask, "Instagram_Post_ID"] = post_id
            if retention_score is not None:
                df.loc[mask, "Retention_Score"] = retention_score
            if grade is not None:
                df.loc[mask, "Grade"] = grade
            df.to_excel(cls.FILE_NAME, index=False)
            cls._style_excel(cls.FILE_NAME)
            print(f"[+] Updated status for Video {video_id} -> {status} (Score: {retention_score}, Grade: {grade})")
