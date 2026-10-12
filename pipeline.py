import os
import sys
import argparse
from dotenv import load_dotenv

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from prompt_engine import PromptGenerator
from video_generator import VideoGenerator
from video_composer import VideoComposer
from instagram_publisher import InstagramPublisher

load_dotenv()

def run_pipeline(topic: str = None, dry_run: bool = False, auto_publish: bool = False, engine: str = "blender"):
    """
    Executes the 3D ASMR Reel automation:
    1. Generates 3D ASMR prompt concept & caption using Evolved DNA.
    2. Renders via 100% Physics-Accurate Blender Engine OR AI Video (Replicate/MiniMax).
    3. Synthesizes frame-synced ASMR Foley audio.
    4. Audits Retention Quality & optimizes before publishing.
    5. Publishes to Instagram (if configured).
    """
    print("=" * 60)
    print(f"[*] STARTING 3D ASMR REEL AUTOMATION [ENGINE: {engine.upper()}]")
    print("=" * 60)

    # 1. Concept Generation
    prompt_gen = PromptGenerator()
    concept = prompt_gen.get_concept(custom_topic=topic)
    print(f"\n[1/4] Selected Concept: {concept['title']}")
    print(f"Video Prompt: {concept['video_prompt']}")
    print(f"Caption:\n{concept['caption']}\n")

    if dry_run:
        print("Dry run enabled. Skipping video rendering and Instagram upload.")
        return

    # 2. Rendering (Blender 3D Physics OR AI Model)
    final_video_dir = os.path.join("output", "final")
    os.makedirs(final_video_dir, exist_ok=True)
    final_reel_path = os.path.join(final_video_dir, f"reel_{int(os.times().elapsed)}.mp4")

    if engine.lower() == "blender":
        from blender_engine import BlenderEngine
        print("[2/4] Rendering via Headless Blender 5.2 Physics Simulation...")
        rendered_blender = BlenderEngine.render_procedural_asmr_scene(loop_frames=90)
        final_reel_path = rendered_blender or final_reel_path
    else:
        # AI Video Generation (Replicate / MiniMax)
        raw_video_dir = os.path.join("output", "raw")
        os.makedirs(raw_video_dir, exist_ok=True)
        raw_video_path = os.path.join(raw_video_dir, f"raw_{int(os.times().elapsed)}.mp4")

        video_gen = VideoGenerator()
        video_gen.generate_video(
            prompt=concept["video_prompt"],
            output_path=raw_video_path,
            model_name=os.getenv("VIDEO_MODEL", "minimax/video-01")
        )

        VideoComposer.format_reel(
            input_video_path=raw_video_path,
            output_video_path=final_reel_path
        )
    print(f"\n[3/4] Reel formatted successfully: {final_reel_path}")
    print(f"\n[3/4] Reel formatted successfully: {final_reel_path}")

    # 3b. AI Retention Quality Gate & Evolved Enhancer
    from retention_auditor import RetentionAuditor
    from video_enhancer import VideoEnhancer
    print("\n[*] Auditing generated video with AI Retention Quality Gate...")
    audit = RetentionAuditor.audit_video(final_reel_path)
    print(f"[>] Initial Score: {audit['retention_score']}/100 [Grade: {audit['grade']}]")
    if audit.get("needs_enhancement", False):
        final_reel_path = VideoEnhancer.enhance_for_retention(final_reel_path, audit)
        post_audit = RetentionAuditor.audit_video(final_reel_path)
        print(f"[+] Post-Enhancement Score: {post_audit['retention_score']}/100 [Grade: {post_audit['grade']}]")
        audit = post_audit

    # 3c. SEAMLESS IN-SYSTEM AUTO-EVOLUTION (No manual trigger needed)
    from evolution_engine import EvolutionEngine
    EvolutionEngine.auto_evolve_from_audit(
        video_id=f"REEL_{int(os.times().elapsed)}",
        title=concept["title"],
        audit_report=audit
    )

    # 4. Instagram Publishing
    if auto_publish:
        print("\n[4/4] Auto-publishing to Instagram...")
        publisher = InstagramPublisher()
        publisher.publish_reel(
            video_path=final_reel_path,
            caption=concept["caption"]
        )
        print("[+] Reel successfully published to Instagram!")
    else:
        print("\n[4/4] Skipping upload (auto-publish disabled). Video is ready for manual or scheduled review.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Instagram 3D ASMR Reels Automation")
    parser.add_argument("--topic", type=str, default=None, help="Custom theme or concept for the reel")
    parser.add_argument("--dry-run", action="store_true", help="Simulate prompt generation without API calls")
    parser.add_argument("--publish", action="store_true", help="Automatically upload to Instagram")
    parser.add_argument("--engine", type=str, default="blender", choices=["blender", "ai"], help="Rendering engine: 'blender' (100% Physics) or 'ai' (MiniMax/Kling)")

    args = parser.parse_args()
    run_pipeline(topic=args.topic, dry_run=args.dry_run, auto_publish=args.publish, engine=args.engine)
