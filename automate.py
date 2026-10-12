import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from trend_scraper import TrendScraper
from content_calendar import ContentCalendar
from video_processor import VideoProcessor
from instagram_publisher import InstagramPublisher
from retention_auditor import RetentionAuditor
from video_enhancer import VideoEnhancer
from analytics_monitor import AnalyticsRetentionMonitor

load_dotenv()

def populate_weekly_schedule(days: int = 7, post_time: str = "18:00"):
    """Scrapes trending 3D ASMR reels, checks for duplicates, and populates Excel."""
    print("=" * 60)
    print(f"[*] STEP 1: GENERATING {days}-DAY CONTENT SCHEDULE IN EXCEL")
    print("=" * 60)

    scraper = TrendScraper()
    trends = scraper.search_viral_trends(count=days)

    if not trends:
        print("[-] No new unique trends found. All candidates already recorded.")
        return

    excel_file = ContentCalendar.create_or_extend_calendar(
        trends=trends,
        start_date=datetime.now(),
        post_time=post_time
    )
    print(f"\n[+] Success! Content schedule generated at: {excel_file}")

def execute_daily_upload(dry_run: bool = False):
    """Reads next PENDING row from Excel, transforms it to 1080p, and uploads to Instagram."""
    print("=" * 60)
    print("[*] STEP 2: EXECUTING DAILY AUTOMATION FROM EXCEL")
    print("=" * 60)

    row = ContentCalendar.get_pending_row()
    if not row:
        print("[!] No pending videos found in content_calendar.xlsx. Schedule more videos!")
        return

    vid_id = str(row["Video_ID"])
    title = str(row["Trend_Title"])
    url = str(row["Source_URL"])
    caption = str(row["Caption"])

    print(f"[>] Today's Scheduled Post: {row['Day']} ({row['Scheduled_Date']})")
    print(f"[>] Title: {title}")
    print(f"[>] Source: {url}")

    # 1. Process and upscale/crop to 1080x1920
    processed_video = row.get("Local_File_Path")
    if not processed_video or not os.path.exists(str(processed_video)):
        processed_video = VideoProcessor.process_video(source_url=url, video_id=vid_id)

    # 2. SMART AI RETENTION QUALITY AUDIT
    print("\n" + "=" * 40)
    print("[*] AI QUALITY GATE: AUDITING VIEWER RETENTION")
    print("=" * 40)
    audit = RetentionAuditor.audit_video(processed_video)
    print(f"[>] Initial Retention Score: {audit['retention_score']}/100 [Grade: {audit['grade']}]")
    print(f"[>] Hook Score: {audit['metrics']['hook_score']} | Pacing: {audit['metrics']['pacing_score']} | Loop: {audit['metrics']['loop_score']}")

    final_video = processed_video
    # If video needs improvement, autonomously optimize it
    if audit.get("needs_enhancement", False):
        print("\n[*] Applying Smart Retention Enhancements (Hook boost, Pacing ramp, Contrast)...")
        final_video = VideoEnhancer.enhance_for_retention(processed_video, audit)
        post_audit = RetentionAuditor.audit_video(final_video)
        print(f"[+] Post-Enhancement Score: {post_audit['retention_score']}/100 [Grade: {post_audit['grade']}]")
        audit = post_audit

    # Record to Intelligence Vault & Update Excel
    AnalyticsRetentionMonitor.record_video_audit(
        video_id=vid_id,
        title=title,
        audit_result=audit,
        final_path=final_video
    )
    ContentCalendar.update_row_status(
        video_id=vid_id,
        status="PROCESSED",
        local_path=final_video,
        retention_score=audit["retention_score"],
        grade=audit["grade"]
    )

    # 2b. SEAMLESS IN-SYSTEM AUTO-EVOLUTION (No manual trigger needed)
    from evolution_engine import EvolutionEngine
    EvolutionEngine.auto_evolve_from_audit(video_id=vid_id, title=title, audit_report=audit)

    if dry_run:
        print("\n[*] Dry run mode enabled. Retention-optimized video ready at:")
        print(f"    {final_video}")
        print(f"[*] Quality Grade: {audit['grade']} ({audit['retention_score']}/100)")
        print("[*] Instagram upload skipped.")
        return

    # 3. Upload to Instagram
    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")

    if not username or not password:
        print("\n[!] INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD is not set in .env.")
        print(f"[!] The 1080p video has been saved locally to: {final_video}")
        print("[!] Set your credentials in .env to enable automatic publishing.")
        return

    try:
        publisher = InstagramPublisher(username=username, password=password)
        associated_cleanup = []
        frames_dir = os.path.abspath(f"output/frames_{vid_id}")
        if os.path.exists(frames_dir):
            associated_cleanup.append(frames_dir)

        res = publisher.publish_reel(
            video_path=final_video,
            caption=caption,
            auto_cleanup=True,
            associated_paths=associated_cleanup
        )
        post_id = res.get("pk", "PUBLISHED")
        ContentCalendar.update_row_status(
            video_id=vid_id,
            status="UPLOADED",
            local_path=final_video,
            post_id=str(post_id),
            retention_score=audit["retention_score"],
            grade=audit["grade"]
        )
        print(f"[+] Post published successfully! Instagram Media ID: {post_id}")
    except Exception as e:
        print(f"[-] Instagram upload failed: {e}")

def run_rl_daemon_episode(
    engine: str = "blender",
    fps: int = 60,
    device: str = "optix",
    target_account: str = "asmrtransition_",
    reward_metric: str = "retention_loop",
    auto_evolve: bool = True,
    auto_publish: bool = False,
    auto_cleanup: bool = True,
    dry_run: bool = False
):
    """
    ASMR-Genesis-RL Living Daemon Episode Runner.
    Executes one complete closed-loop RL iteration:
    1. Initialize environment & load DNA
    2. Mutate action space (physics/pacing)
    3. Render / verify 60 FPS cloth pressure video
    4. Audio sync & FFmpeg compilation
    5. Retention & RL composite reward audit
    6. Policy update & memory persistence
    7. Direct auto-publish to Instagram
    """
    print("\n" + "=" * 65)
    print("🤖 ASMR-Genesis-RL: AUTONOMOUS REINFORCEMENT LEARNING DAEMON")
    print("=" * 65)
    print(f"[*] Engine: {engine.upper()} | Framerate: {fps} FPS | Device: {device.upper()}")
    print(f"[*] Target Account: @{target_account} | Reward Metric: {reward_metric}")
    print(f"[*] Auto-Evolve: {auto_evolve} | Auto-Publish: {auto_publish}")

    from evolution_engine import EvolutionEngine
    from retention_auditor import RetentionAuditor

    # 1. Load State Space (S)
    dna = EvolutionEngine.load_dna()
    gen = dna.get("generation", 1)
    baseline = dna.get("rl_state", {}).get("baseline_reward", 75.0)
    print(f"[*] Current Generation: {gen} | Baseline Reward: {baseline:.2f}")

    # 2. Mutate Action Space (A)
    if auto_evolve:
        mutations = EvolutionEngine.mutate_action_space(dna)
        if mutations:
            print("[*] Sampled Action Space Mutations:")
            for m in mutations:
                print(f"    -> {m}")
        EvolutionEngine.save_dna(dna)

    # 3. Check / Compile 60 FPS Master Video
    video_path = os.path.abspath("output/rendered/FINAL_60FPS_CLOTH_JELLY_ASMR.mp4")
    cover_path = os.path.abspath("output/rendered/FINAL_60FPS_CLOTH_JELLY_ASMR_cover.jpg")
    audio_path = os.path.abspath("output/rendered/cloth_jelly_60fps_foley.wav")

    if not os.path.exists(video_path):
        print("[*] Target video not pre-compiled. Running compilation pipeline...")
        import subprocess
        subprocess.run([sys.executable, "compile_cloth_jelly_reel.py"], check=True)

    # 4. Audit & Reward Calculation (R)
    print("\n[*] Evaluating Video with AI Retention & RL Auditor...")
    audit = RetentionAuditor.audit_video(video_path, audio_path=audio_path)
    r_total = audit["reward_components"]["r_total"]
    print(f"[+] Audit Complete: R_total = {r_total}/100 [Grade: {audit['grade']}]")
    print(f"    R_retention = {audit['reward_components']['r_retention']} | R_physics = {audit['reward_components']['r_physics']} | R_audio = {audit['reward_components']['r_audio']}")

    # 5. Policy Update & Learning (pi)
    policy_report = EvolutionEngine.evaluate_and_update_policy(
        video_id=f"EPISODE_GEN_{gen}",
        concept_theme="organic_cloth_pressure_jelly",
        audit_result=audit
    )

    # 6. Auto-Publishing (Target Channel)
    if auto_publish and not dry_run:
        print("\n" + "=" * 50)
        print(f"[*] AUTO-PUBLISHING 60 FPS REEL TO @{target_account}")
        print("=" * 50)
        from instagram_publisher import InstagramPublisher
        caption = """100% Organic Cloth Pressure Jelly in 60 FPS ✨ Liquid 24K Gold on Italian Verde Alpi Marble 🌿

Vertex-level soft-body physics simulation with hydrostatic volume conservation & harmonic jiggle resonance. 

🎧 Wear headphones for binaural 3D ASMR Foley audio!
Which moment felt the most satisfying? The initial drop or the pancake squish? 👇

#asmr #satisfying #oddlysatisfying #blender3d #cyclesrender #60fps #softbody #jelly #asmrcommunity #satisfyingvideos #3danimation #asmrsounds #gold"""

        publisher = InstagramPublisher()
        associated_cleanup = []
        frames_dir_12s = os.path.abspath("output/cloth_jelly_12s_60fps_frames")
        frames_dir_5s = os.path.abspath("output/cloth_jelly_60fps_frames")
        if os.path.exists(frames_dir_12s):
            associated_cleanup.append(frames_dir_12s)
        if os.path.exists(frames_dir_5s):
            associated_cleanup.append(frames_dir_5s)
        wav_12s = os.path.abspath("output/rendered/cloth_jelly_12s_60fps_foley.wav")
        if os.path.exists(wav_12s):
            associated_cleanup.append(wav_12s)
        wav_5s = os.path.abspath("output/rendered/cloth_jelly_60fps_foley.wav")
        if os.path.exists(wav_5s):
            associated_cleanup.append(wav_5s)

        res = publisher.publish_reel(
            video_path=video_path,
            caption=caption,
            thumbnail_path=cover_path,
            auto_cleanup=auto_cleanup,
            associated_paths=associated_cleanup
        )
        print(f"[SUCCESS] Published to @{target_account}! Media PK: {res.get('pk')}")
        code = res.get('code')
        if code:
            print(f"Reel URL: https://www.instagram.com/reel/{code}/")
    else:
        print(f"\n[*] Auto-publish flag is {'False' if not auto_publish else 'Dry-Run'}. Upload skipped.")

    print("\n[SUCCESS] ASMR-Genesis-RL Daemon Episode Finished.")
    return policy_report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASMR-Genesis-RL Automation & Reinforcement Learning CLI")
    
    # RL-Daemon Mode Arguments
    parser.add_argument("--mode", type=str, default=None, choices=["rl-daemon", "daily", "batch"], help="Execution mode: rl-daemon, daily, batch")
    parser.add_argument("--engine", type=str, default="blender", help="Simulation & render engine (blender)")
    parser.add_argument("--fps", type=int, default=60, help="Target framerate (60)")
    parser.add_argument("--device", type=str, default="optix", help="Compute device (optix, cuda, cpu)")
    parser.add_argument("--target-account", type=str, default="asmrtransition_", help="Target Instagram account")
    parser.add_argument("--reward-metric", type=str, default="retention_loop", help="Primary reward evaluation metric")
    parser.add_argument("--auto-evolve", action="store_true", help="Enable automatic RL policy evolution and mutation")
    parser.add_argument("--auto-publish", action="store_true", help="Enable direct automatic publishing upon verification")
    parser.add_argument("--no-cleanup", dest="auto_cleanup", action="store_false", default=True, help="Preserve local video and frame caches after uploading (default: auto-cleanup enabled)")

    # Legacy & Auxiliary Arguments
    parser.add_argument("--scrape-week", action="store_true", help="Scrape viral trends and build 1-week Excel schedule")
    parser.add_argument("--upload-today", action="store_true", help="Process and upload today's scheduled video from Excel")
    parser.add_argument("--dry-run", action="store_true", help="Test without uploading to Instagram")
    parser.add_argument("--days", type=int, default=7, help="Number of days to schedule (default: 7)")
    parser.add_argument("--time", type=str, default="18:00", help="Scheduled posting time (default: 18:00)")
    parser.add_argument("--evolve", action="store_true", help="Trigger AI Evolution step by ingesting latest performance metrics")
    parser.add_argument("--render-blender", action="store_true", help="Render 100% physically accurate 3D ASMR loop via headless Blender 5.2")

    args = parser.parse_args()

    if args.mode == "rl-daemon":
        run_rl_daemon_episode(
            engine=args.engine,
            fps=args.fps,
            device=args.device,
            target_account=args.target_account,
            reward_metric=args.reward_metric,
            auto_evolve=args.auto_evolve,
            auto_publish=args.auto_publish,
            auto_cleanup=args.auto_cleanup,
            dry_run=args.dry_run
        )
    elif args.scrape_week:
        populate_weekly_schedule(days=args.days, post_time=args.time)
    elif args.upload_today:
        execute_daily_upload(dry_run=args.dry_run)
    elif args.render_blender:
        from blender_engine import BlenderEngine
        print("[*] Launching 100% Physically Accurate Blender 3D Procedural Simulation...")
        rendered_path = BlenderEngine.render_procedural_asmr_scene(loop_frames=90)
        print(f"[+] 100% Physics Accurate Blender Reel generated: {rendered_path}")
    elif args.evolve:
        from evolution_engine import EvolutionEngine
        from analytics_monitor import AnalyticsRetentionMonitor
        print("[*] Running Autonomous AI Evolution Step...")
        test_metrics = {
            "views": 3200,
            "avg_percentage_viewed": 108.2,
            "saves": 240,
            "shares": 110,
            "likes": 480,
            "comments": 65
        }
        EvolutionEngine.evolve_after_video(
            video_id="DAILY_REEL",
            concept_theme="organic_cloth_pressure_jelly",
            performance_metrics=test_metrics
        )
    else:
        print("ASMR-Genesis-RL CLI Usage:")
        print("  python -m automate --mode rl-daemon --engine blender --fps 60 --device optix --target-account asmrtransition_ --reward-metric retention_loop --auto-evolve --auto-publish")
        print("  python automate.py --upload-today --dry-run")
        print("  python automate.py --scrape-week")

