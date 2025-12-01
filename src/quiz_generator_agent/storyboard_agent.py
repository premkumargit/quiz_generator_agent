
from typing import Dict, Any, List

from google.adk.agents.llm_agent import Agent
import logging

logger = logging.getLogger(__name__)


def build_storyboard(quiz: Dict[str, Any]) -> Dict[str, Any]:
    """Convert quiz JSON into a storyboard of scenes."""
    topic = quiz.get("topic", "General Knowledge")
    scenes: List[Dict[str, Any]] = []

    scenes.append({
        "type": "intro",
        "duration_sec": 4,
        "text": f"Quiz Time! {topic}",
        "voiceover": f"Welcome to a quick quiz on {topic}.",
    })

    for i, q in enumerate(quiz["questions"], start=1):
        options = q["options"]
        options_text = "\n".join(
            f"{chr(ord('A') + idx)}) {opt}" for idx, opt in enumerate(options)
        )
        answer = options[q["correct_option_index"]]
        fact = q["fact"]

        scenes.append({
            "type": "question",
            "duration_sec": 6,
            "text": f"Question {i}:\n{q['question']}\n\n{options_text}",
            "voiceover": q["question"],
        })

        scenes.append({
            "type": "question_with_timer",
            "duration_sec": 4,
            "text": f"Question {i}:\n{q['question']}\n\n{options_text}",
            "voiceover": "TIMER_COUNTDOWN",
        })

        scenes.append({
            "type": "answer",
            "duration_sec": 4,
            "text": f"Answer: {answer}",
            "voiceover": f"The correct answer is {answer}.",
        })

        scenes.append({
            "type": "fact",
            "duration_sec": 4,
            "text": f"Fun fact: {fact}",
            "voiceover": f"Fun fact: {fact}.",
        })

    scenes.append({
        "type": "thanks",
        "duration_sec": 4,
        "text": "Thanks for watching! 🎉",
        "voiceover": "Thanks for watching this quiz. See you next time!",
    })

    return {
        "topic": topic,
        "scenes": scenes,
    }


storyboard_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="storyboard_agent",
    description="Turns quiz JSON into a storyboard of scenes.",
    instruction=(
        "You convert quiz JSON into a storyboard.\n"
        "Use the 'build_storyboard' tool. Do not redesign the quiz."
    ),
    tools=[build_storyboard],
)
