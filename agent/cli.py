"""CLI orchestrator for Shorts pipeline."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

from .cartesia_tts import CartesiaTTS
from .config import (
    CARTESIA_VOICE_ID,
    get_cartesia_api_key,
    get_openrouter_api_key,
)
from .openrouter_client import OpenRouterClient
from .renderer import render_mp4
from .stages import (
    StoryboardResult,
    DetailResult,
    SceneBuildResult,
    load_animation_library,
    load_audio_script,
    load_base_html,
    load_component_library,
    stage_detail_pass,
    stage_scene_builder,
    stage_storyboard,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="shorts",
        description="Generate animated shorts from audio scripts",
    )
    p.add_argument("--id", required=True, help="Unique ID for this run")
    p.add_argument("--audio", help="Path to audio script markdown file")
    p.add_argument("--topic", help="Topic to generate audio script from (not implemented yet)")
    p.add_argument("--skip-tts", action="store_true", help="Skip TTS generation")
    p.add_argument("--skip-render", action="store_true", help="Skip frame capture and MP4 render")
    p.add_argument("--render-only", action="store_true", help="Only render MP4 from existing scene.html")
    p.add_argument("--duration", type=int, default=60, help="Target duration in seconds")
    return p


def get_shorts_dir() -> Path:
    """Get the Shorts directory (parent of agent/)."""
    return Path(__file__).resolve().parent.parent


def run_pipeline(
    *,
    run_id: str,
    audio_script_path: Optional[Path],
    topic: Optional[str],
    skip_tts: bool,
    skip_render: bool,
    duration_s: int,
) -> int:
    """Run the full pipeline."""
    
    shorts_dir = get_shorts_dir()
    runs_dir = shorts_dir / "runs" / run_id
    renders_dir = shorts_dir / "renders"
    runs_dir.mkdir(parents=True, exist_ok=True)
    renders_dir.mkdir(parents=True, exist_ok=True)
    
    # Load API keys
    openrouter_key = get_openrouter_api_key()
    if not openrouter_key:
        print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
        return 1
    
    cartesia_key = get_cartesia_api_key()
    if not cartesia_key and not skip_tts:
        print("ERROR: CARTESIA_API_KEY not set (use --skip-tts to skip)", file=sys.stderr)
        return 1
    
    # Initialize clients
    openrouter = OpenRouterClient(api_key=openrouter_key)
    
    # Stage A: Load or generate audio script
    if audio_script_path:
        print(f"Loading audio script from {audio_script_path}")
        audio_script = load_audio_script(audio_script_path)
    elif topic:
        print("ERROR: Topic-to-script generation not implemented yet. Use --audio instead.")
        return 1
    else:
        print("ERROR: Must provide --audio or --topic", file=sys.stderr)
        return 1
    
    # Save audio script to run dir
    (runs_dir / "audio_script.md").write_text(audio_script, encoding="utf-8")
    
    # Stage B: Storyboard (audio script -> timeline)
    print("Stage B: Generating video script and timeline...")
    try:
        storyboard: StoryboardResult = stage_storyboard(
            client=openrouter,
            audio_script=audio_script,
            duration_hint_s=duration_s,
        )
    except Exception as e:
        print(f"ERROR in storyboard stage: {e}", file=sys.stderr)
        return 1
    
    # Save storyboard outputs
    (runs_dir / "video_script.md").write_text(storyboard.video_script_md, encoding="utf-8")
    (runs_dir / "timeline.json").write_text(
        json.dumps(storyboard.timeline, indent=2), encoding="utf-8"
    )
    print(f"  -> Saved video_script.md and timeline.json to {runs_dir}")
    
    # Stage B2: Detail pass (polish with visual specs)
    print("Stage B2: Adding detailed visual descriptions...")
    try:
        detail_result: DetailResult = stage_detail_pass(
            client=openrouter,
            video_script=storyboard.video_script_md,
            timeline=storyboard.timeline,
        )
        # Use refined timeline for scene building
        final_timeline = detail_result.refined_timeline
    except Exception as e:
        print(f"WARNING: Detail pass failed ({e}), using original timeline", file=sys.stderr)
        detail_result = None
        final_timeline = storyboard.timeline
    
    # Save detail pass outputs
    if detail_result:
        (runs_dir / "detailed_script.md").write_text(detail_result.detailed_script_md, encoding="utf-8")
        (runs_dir / "refined_timeline.json").write_text(
            json.dumps(detail_result.refined_timeline, indent=2), encoding="utf-8"
        )
        print(f"  -> Saved detailed_script.md and refined_timeline.json to {runs_dir}")
    
    # Stage C: Scene builder (timeline -> HTML)
    print("Stage C: Building HTML scene...")
    try:
        base_html = load_base_html(shorts_dir)
        animation_lib = load_animation_library(shorts_dir)
        component_lib = load_component_library(shorts_dir)
        
        scene_result: SceneBuildResult = stage_scene_builder(
            client=openrouter,
            timeline=final_timeline,
            base_html=base_html,
            animation_library=animation_lib,
            component_library=component_lib,
            detailed_script=detail_result.detailed_script_md if detail_result else "",
        )
    except Exception as e:
        print(f"ERROR in scene builder stage: {e}", file=sys.stderr)
        return 1
    
    # Save scene outputs
    scene_path = runs_dir / "scene.html"
    scene_path.write_text(scene_result.html, encoding="utf-8")
    (runs_dir / "scene_spec.json").write_text(
        json.dumps(scene_result.scene_spec, indent=2), encoding="utf-8"
    )
    print(f"  -> Saved scene.html and scene_spec.json to {runs_dir}")
    
    # Stage D: TTS (audio script -> WAV)
    wav_path: Optional[Path] = None
    if not skip_tts and cartesia_key:
        print("Stage D: Generating voiceover...")
        try:
            tts = CartesiaTTS(api_key=cartesia_key)
            wav_path = renders_dir / f"{run_id}.wav"
            tts.synthesize_wav(
                text=audio_script,
                voice_id=CARTESIA_VOICE_ID,
                out_wav_path=wav_path,
            )
            print(f"  -> Saved voiceover to {wav_path}")
        except Exception as e:
            print(f"WARNING: TTS failed: {e}", file=sys.stderr)
            wav_path = None
    
    # Stage E: Render (HTML + WAV -> MP4)
    if not skip_render:
        print("Stage E: Rendering MP4...")
        try:
            duration_ms = final_timeline.get("duration_ms", duration_s * 1000)
            result = render_mp4(
                html_path=scene_path,
                output_dir=runs_dir,
                duration_ms=duration_ms,
                fps=30,
                wav_path=wav_path,
            )
            
            # Copy final MP4 to renders/
            final_mp4 = result.final_mp4_path or result.mp4_path
            output_mp4 = renders_dir / f"{run_id}.mp4"
            output_mp4.write_bytes(final_mp4.read_bytes())
            print(f"  -> Saved MP4 to {output_mp4}")
            print(f"  -> Captured {result.frame_count} frames")
        except Exception as e:
            print(f"ERROR in render stage: {e}", file=sys.stderr)
            return 1
    
    print(f"\n✓ Pipeline complete! Outputs in {runs_dir}")
    return 0


def run_render_only(*, run_id: str, duration_s: int, skip_tts: bool) -> int:
    """Render MP4 from existing scene.html in a run directory."""
    
    shorts_dir = get_shorts_dir()
    runs_dir = shorts_dir / "runs" / run_id
    renders_dir = shorts_dir / "renders"
    
    scene_path = runs_dir / "scene.html"
    if not scene_path.exists():
        print(f"ERROR: {scene_path} not found", file=sys.stderr)
        return 1
    
    # Load timeline for duration
    timeline_path = runs_dir / "refined_timeline.json"
    if not timeline_path.exists():
        timeline_path = runs_dir / "timeline.json"
    
    if timeline_path.exists():
        timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
        duration_ms = timeline.get("duration_ms", duration_s * 1000)
    else:
        duration_ms = duration_s * 1000
    
    # Check for existing WAV
    wav_path = renders_dir / f"{run_id}.wav"
    if not wav_path.exists():
        wav_path = None
    
    # TTS if needed
    if not skip_tts and not wav_path:
        cartesia_key = get_cartesia_api_key()
        audio_script_path = runs_dir / "audio_script.md"
        if cartesia_key and audio_script_path.exists():
            print("Generating voiceover...")
            tts = CartesiaTTS(api_key=cartesia_key)
            wav_path = renders_dir / f"{run_id}.wav"
            tts.synthesize_wav(
                text=audio_script_path.read_text(encoding="utf-8"),
                voice_id=CARTESIA_VOICE_ID,
                out_wav_path=wav_path,
            )
            print(f"  -> Saved voiceover to {wav_path}")
    
    print(f"Rendering MP4 from {scene_path}...")
    print(f"  Duration: {duration_ms}ms, WAV: {wav_path or 'none'}")
    
    try:
        result = render_mp4(
            html_path=scene_path,
            output_dir=runs_dir,
            duration_ms=duration_ms,
            fps=30,
            wav_path=wav_path,
        )
        
        final_mp4 = result.final_mp4_path or result.mp4_path
        output_mp4 = renders_dir / f"{run_id}.mp4"
        output_mp4.write_bytes(final_mp4.read_bytes())
        print(f"  -> Saved MP4 to {output_mp4}")
        print(f"  -> Captured {result.frame_count} frames")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    
    print(f"\n✓ Render complete!")
    return 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    
    # Render-only mode
    if args.render_only:
        return run_render_only(
            run_id=args.id,
            duration_s=args.duration,
            skip_tts=args.skip_tts,
        )
    
    audio_path = Path(args.audio) if args.audio else None
    
    return run_pipeline(
        run_id=args.id,
        audio_script_path=audio_path,
        topic=args.topic,
        skip_tts=args.skip_tts,
        skip_render=args.skip_render,
        duration_s=args.duration,
    )


if __name__ == "__main__":
    raise SystemExit(main())
