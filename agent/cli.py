"""Simplified CLI for Shorts: TTS + Render utilities."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

from .cartesia_tts import CartesiaTTS
from .debug_overlay import inject_debug_overlay
from .renderer import render_mp4

# Configuration
CARTESIA_VOICE_ID = "0ad65e7f-006c-47cf-bd31-52279d487913"


def get_cartesia_api_key() -> Optional[str]:
    return os.getenv("CARTESIA_API_KEY")


def get_shorts_dir() -> Path:
    """Get the Shorts directory (parent of agent/)."""
    return Path(__file__).resolve().parent.parent


def cmd_tts(args) -> int:
    """Generate TTS audio + word-level timestamps."""
    
    shorts_dir = get_shorts_dir()
    runs_dir = shorts_dir / "runs" / args.id
    renders_dir = shorts_dir / "renders"
    runs_dir.mkdir(parents=True, exist_ok=True)
    renders_dir.mkdir(parents=True, exist_ok=True)
    
    # Load audio script
    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"ERROR: Audio script not found: {audio_path}", file=sys.stderr)
        return 1
    
    audio_script = audio_path.read_text(encoding="utf-8")
    
    # Save audio script to run dir
    (runs_dir / "audio_script.md").write_text(audio_script, encoding="utf-8")
    
    # Get API key
    cartesia_key = get_cartesia_api_key()
    if not cartesia_key:
        print("ERROR: CARTESIA_API_KEY not set", file=sys.stderr)
        return 1
    
    # Generate TTS
    print(f"Generating TTS for {args.id}...")
    try:
        tts = CartesiaTTS(api_key=cartesia_key)
        wav_path = renders_dir / f"{args.id}.wav"
        
        word_timestamps = tts.synthesize_with_timestamps(
            text=audio_script,
            voice_id=CARTESIA_VOICE_ID,
            out_wav_path=wav_path,
            speed=args.speed,
        )
        
        print(f"  -> Saved WAV to {wav_path}")
        
        # Save word-level timestamps
        tts_words_path = runs_dir / "tts_words.json"
        tts_words_path.write_text(
            json.dumps([w.__dict__ for w in word_timestamps], indent=2),
            encoding="utf-8",
        )
        print(f"  -> Saved timestamps to {tts_words_path}")
        print(f"  -> {len(word_timestamps)} words, duration: {word_timestamps[-1].end_ms}ms")
        
    except Exception as e:
        print(f"ERROR: TTS failed: {e}", file=sys.stderr)
        return 1
    
    print(f"\n✓ TTS complete! Outputs in {runs_dir}")
    return 0


def cmd_render(args) -> int:
    """Render MP4 from scene.html + WAV."""
    
    shorts_dir = get_shorts_dir()
    runs_dir = shorts_dir / "runs" / args.id
    renders_dir = shorts_dir / "renders"
    
    # Check for scene.html
    scene_path = runs_dir / "scene.html"
    if not scene_path.exists():
        print(f"ERROR: {scene_path} not found", file=sys.stderr)
        print("Create scene.html manually in the run directory first.", file=sys.stderr)
        return 1
    
    # Check for WAV
    wav_path = renders_dir / f"{args.id}.wav"
    if not wav_path.exists():
        wav_path = None
        print("WARNING: No WAV file found, rendering without audio")
    
    # Read scene.html for debug overlay injection
    scene_html = scene_path.read_text(encoding="utf-8")
    
    # Inject debug overlay if requested
    if args.debug:
        tts_words_path = runs_dir / "tts_words.json"
        if tts_words_path.exists():
            tts_words = json.loads(tts_words_path.read_text(encoding="utf-8"))
            # Convert word timestamps to segments for display
            voiceover_segments = []
            for w in tts_words:
                voiceover_segments.append({
                    "start_ms": w["start_ms"],
                    "end_ms": w["end_ms"],
                    "text": w["word"],
                })
            scene_html = inject_debug_overlay(scene_html, voiceover_segments)
            print("  -> Injected debug overlay")
        else:
            print("WARNING: No tts_words.json found, skipping debug overlay")
    
    # Write modified scene.html for rendering
    render_scene_path = runs_dir / "scene_render.html"
    render_scene_path.write_text(scene_html, encoding="utf-8")
    
    # Determine duration
    duration_ms = args.duration * 1000
    if wav_path:
        # Get actual duration from WAV
        import wave
        with wave.open(str(wav_path), 'rb') as w:
            frames = w.getnframes()
            rate = w.getframerate()
            wav_duration_ms = int((frames / rate) * 1000)
            duration_ms = max(duration_ms, wav_duration_ms)
    
    print(f"Rendering MP4 from {scene_path}...")
    print(f"  Duration: {duration_ms}ms, FPS: {args.fps}")
    
    try:
        result = render_mp4(
            html_path=render_scene_path,
            output_dir=runs_dir,
            duration_ms=duration_ms,
            fps=args.fps,
            wav_path=wav_path,
        )
        
        # Copy final MP4 to renders/
        final_mp4 = result.final_mp4_path or result.mp4_path
        output_mp4 = renders_dir / f"{args.id}.mp4"
        output_mp4.write_bytes(final_mp4.read_bytes())
        print(f"  -> Saved MP4 to {output_mp4}")
        print(f"  -> Captured {result.frame_count} frames")
        
    except Exception as e:
        print(f"ERROR: Render failed: {e}", file=sys.stderr)
        return 1
    
    print(f"\n✓ Render complete!")
    return 0


def cmd_run(args) -> int:
    """Full pipeline: TTS + Render (scene.html must exist)."""
    
    shorts_dir = get_shorts_dir()
    runs_dir = shorts_dir / "runs" / args.id
    
    # First, run TTS
    tts_result = cmd_tts(args)
    if tts_result != 0:
        return tts_result
    
    # Check if scene.html exists
    scene_path = runs_dir / "scene.html"
    if not scene_path.exists():
        print(f"\nWARNING: {scene_path} not found")
        print("Create scene.html manually, then run: shorts render --id " + args.id)
        return 0
    
    # Run render
    return cmd_render(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shorts",
        description="Shorts: TTS + Render utilities for animated videos",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # TTS subcommand
    tts_parser = subparsers.add_parser("tts", help="Generate TTS audio + word timestamps")
    tts_parser.add_argument("--id", required=True, help="Unique ID for this run")
    tts_parser.add_argument("--audio", required=True, help="Path to audio script markdown file")
    tts_parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (e.g., 1.2 = 20%% faster)")
    tts_parser.set_defaults(func=cmd_tts)
    
    # Render subcommand
    render_parser = subparsers.add_parser("render", help="Render MP4 from scene.html + WAV")
    render_parser.add_argument("--id", required=True, help="Run ID to render")
    render_parser.add_argument("--duration", type=int, default=60, help="Min duration in seconds (default: 60)")
    render_parser.add_argument("--fps", type=int, default=30, help="Render FPS (default: 30)")
    render_parser.add_argument("--debug", action="store_true", default=True, help="Add debug overlay (default: on)")
    render_parser.add_argument("--no-debug", dest="debug", action="store_false", help="Disable debug overlay")
    render_parser.set_defaults(func=cmd_render)
    
    # Run subcommand (TTS + Render)
    run_parser = subparsers.add_parser("run", help="Run TTS then render (scene.html must exist)")
    run_parser.add_argument("--id", required=True, help="Unique ID for this run")
    run_parser.add_argument("--audio", required=True, help="Path to audio script markdown file")
    run_parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (e.g., 1.2 = 20%% faster)")
    run_parser.add_argument("--duration", type=int, default=60, help="Min duration in seconds (default: 60)")
    run_parser.add_argument("--fps", type=int, default=30, help="Render FPS (default: 30)")
    run_parser.add_argument("--debug", action="store_true", default=True, help="Add debug overlay (default: on)")
    run_parser.add_argument("--no-debug", dest="debug", action="store_false", help="Disable debug overlay")
    run_parser.set_defaults(func=cmd_run)
    
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
