import logging

logger = logging.getLogger(__name__)

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import quiz_generator_agent.config

from .quiz_agent import design_quiz
from .storyboard_agent import build_storyboard
from .video_agent import render_video_from_storyboard


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    return slug.strip("_") or "quiz"


def orchestrate_quiz_video(
    topic: str,
    difficulty: str = "easy",
    num_questions: int = 3,
    debug: bool = False,
) -> Dict[str, Any]:
    base_output = Path("outputs")
    base_output.mkdir(exist_ok=True)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_slug = _slugify(topic)
    run_dir = base_output / f"{topic_slug}_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    if debug:
        logger.info(f"Created output directory: {run_dir}")

    quiz = design_quiz(topic=topic, difficulty=difficulty, num_questions=num_questions)

    # Always save quiz.json file
    quiz_file = run_dir / "quiz.json"
    quiz_file.write_text(json.dumps(quiz, indent=2, ensure_ascii=False), encoding="utf-8")
    if debug:
        logger.info(f"Saved quiz to: {quiz_file}")

    storyboard = build_storyboard(quiz)

    # Always save storyboard.json file
    storyboard_file = run_dir / "storyboard.json"
    storyboard_file.write_text(json.dumps(storyboard, indent=2, ensure_ascii=False), encoding="utf-8")
    if debug:
        logger.info(f"Saved storyboard to: {storyboard_file}")

    video_result = render_video_from_storyboard(storyboard)

    result = {
        "topic": topic,
        "difficulty": difficulty,
        "num_questions": len(quiz["questions"]),
        "quiz": quiz,
        "storyboard": storyboard,
        "final_video": video_result["final_video"],
        "output_dir": video_result["output_dir"],
    }
    return result


def main(debug: bool = False) -> None:
    topic = input("Enter quiz topic: ")
    difficulty = input("Difficulty (easy/medium/hard, default easy): ") or "easy"
    n_str = input("Number of questions (default 3): ")
    num_q = int(n_str) if n_str.strip() else 3

    res = orchestrate_quiz_video(topic, difficulty, num_q, debug=debug)
    print("\n=== Quiz Video Created ===")
    print("Topic:", res["topic"])
    print("Difficulty:", res["difficulty"])
    print("Questions:", res["num_questions"])
    print("Output dir:", res["output_dir"])
    print("Final video:", res["final_video"])
