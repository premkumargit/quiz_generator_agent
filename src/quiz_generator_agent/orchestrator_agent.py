
import quiz_generator_agent.config  # ensure GOOGLE_API_KEY is loaded

from typing import Any, Dict

from google.adk.agents.llm_agent import Agent
import logging

logger = logging.getLogger(__name__)

# Import tool functions from specialist agents
from .quiz_agent import design_quiz
from .storyboard_agent import build_storyboard
from .video_agent import render_video_from_storyboard


orchestrator_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="quiz_video_orchestrator",
    description=(
        "Top-level orchestrator that uses quiz, storyboard, audio, and video tools "
        "to create a full quiz video."
    ),
    instruction=(
        "You are an orchestration agent in an agentic system.\n\n"
        "You have access to the following tools (each backed by its own agent):\n"
        "  - design_quiz(topic: str, difficulty: str, num_questions: int) -> quiz JSON\n"
        "  - build_storyboard(quiz_json: dict) -> storyboard JSON\n"
        "  - render_video_from_storyboard(storyboard: dict) "
        "      -> { 'final_video': <path>, 'output_dir': <path> }\n\n"
        "Your overall job:\n"
        "  1. When the user asks for a quiz video, parse the topic, difficulty, and number of questions.\n"
        "  2. Call design_quiz(...) to generate the quiz JSON.\n"
        "  3. Call build_storyboard(...) with that quiz JSON to create scenes + voiceover text.\n"
        "  4. Call render_video_from_storyboard(...) with the storyboard to generate the final stitched video.\n"
        "  5. Respond ONLY with STRICT JSON in this format (no extra commentary):\n"
        "     {\n"
        "       \"topic\": string,\n"
        "       \"difficulty\": string,\n"
        "       \"num_questions\": integer,\n"
        "       \"final_video\": string,\n"
        "       \"output_dir\": string\n"
        "     }\n\n"
        "If a tool call fails, you may retry, but still respond only in the strict JSON format."
    ),
    tools=[
        design_quiz,
        build_storyboard,
        render_video_from_storyboard,
    ],
)
