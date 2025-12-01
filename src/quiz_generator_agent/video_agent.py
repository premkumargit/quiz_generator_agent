
from pathlib import Path
from typing import Dict, Any, List

import quiz_generator_agent.config

from moviepy import (
    ColorClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    AudioFileClip,
)
from google.adk.agents.llm_agent import Agent
import logging

logger = logging.getLogger(__name__)

from .audio_agent import synthesize_audio


W, H = 1280, 720


def _get_available_font():
    """Get an available font that works across different operating systems."""
    import os
    from moviepy import TextClip

    # Try different font options in order of preference
    font_options = [
        # macOS fonts
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        # Linux fonts (common)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        # Windows fonts
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\calibri.ttf",
        # Fallback - let MoviePy try to find a default
        None
    ]

    for font in font_options:
        try:
            if font is None:
                # Let MoviePy use its default
                TextClip(text="test", font_size=24)
                return None
            elif os.path.exists(font):
                TextClip(text="test", font=font, font_size=24)
                return font
        except:
            continue

    # If nothing works, return None and let MoviePy handle it
    return None


def _scene_bg_color(scene_type: str):
    colors = {
        "intro": (30, 144, 255),
        "question": (34, 139, 34),
        "question_with_timer": (70, 70, 70),
        "answer": (218, 165, 32),
        "fact": (128, 0, 128),
        "thanks": (25, 25, 112),
        "generic": (0, 0, 0),
    }
    return colors.get(scene_type, colors["generic"])


def _render_scene(
    scene: Dict[str, Any],
    scene_index: int,
    audio_dir: Path,
) -> CompositeVideoClip:
    text = scene.get("text", "")
    duration = scene.get("duration_sec", 4)
    scene_type = scene.get("type", "generic")
    voiceover = scene.get("voiceover", "")

    bg_color = _scene_bg_color(scene_type)
    bg = ColorClip(size=(W, H), color=bg_color, duration=duration)

    # Use the available font
    available_font = _get_available_font()

    txt = TextClip(
        text=text,
        font_size=48,
        font=available_font,
        color="white",
        method="caption",
        size=(int(W * 0.9), int(H * 0.8)),
    ).with_duration(duration).with_position("center")

    clip = CompositeVideoClip([bg, txt])

    if voiceover:
        scene_id = f"scene_{scene_index:03d}"
        audio_path = synthesize_audio(
            text=voiceover,
            output_dir=str(audio_dir),
            scene_id=scene_id,
        )
        audio_clip = AudioFileClip(audio_path)

        if audio_clip.duration > duration:
            audio_clip = audio_clip.subclipped(0, duration)

        clip = clip.with_audio(audio_clip)

    return clip


def render_video_from_storyboard(
    storyboard: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Given a storyboard, render scenes to a final stitched video.

    This function chooses an output directory automatically based on
    storyboard['topic'] and a timestamp, under the 'outputs/' folder.
    """
    from datetime import datetime
    import re

    topic = storyboard.get("topic", "quiz")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", topic.strip().lower())
    slug = slug.strip("_") or "quiz"
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    base_output = Path("outputs")
    base_output.mkdir(exist_ok=True)
    out_dir = base_output / f"{slug}_{run_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    audio_dir = out_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    scenes = storyboard["scenes"]
    scene_clips: List[CompositeVideoClip] = []

    for idx, scene in enumerate(scenes):
        clip = _render_scene(scene, scene_index=idx, audio_dir=audio_dir)
        scene_clips.append(clip)

    final_video_path = out_dir / "quiz_video_local.mp4"
    final = concatenate_videoclips(scene_clips, method="compose")
    final.write_videofile(str(final_video_path), fps=24)

    for c in scene_clips:
        if c.audio:
            c.audio.close()
        c.close()
    if final.audio:
        final.audio.close()
    final.close()

    return {
        "final_video": str(final_video_path),
        "output_dir": str(out_dir),
    }


video_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="video_rendering_agent",
    description="Renders a storyboard into a full quiz video using MoviePy and the audio agent.",
    instruction=(
        "You take a storyboard and create a final quiz video.\n"
        "Use the 'render_video_from_storyboard' tool to:\n"
        "  - generate audio via the audio agent for each scene\n"
        "  - render scenes as video clips\n"
        "  - stitch them into one final video.\n"
    ),
    tools=[render_video_from_storyboard],
)

