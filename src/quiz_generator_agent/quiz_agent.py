
import json
from typing import Dict, Any

import quiz_generator_agent.config

from google import genai
from google.genai import types
from google.adk.agents.llm_agent import Agent
import logging

logger = logging.getLogger(__name__)
client = genai.Client()


def design_quiz(
    topic: str,
    difficulty: str = "easy",
    num_questions: int = 3,
) -> Dict[str, Any]:
    """Create a multiple-choice quiz as strict JSON."""
    prompt = f"""
You are an educational quiz designer.

Create a multiple-choice quiz on the given TOPIC and DIFFICULTY LEVEL.
Return STRICT JSON with this schema:

{{
  "topic": "<topic>",
  "difficulty": "<level>",
  "questions": [
    {{
      "id": <int>,
      "question": "<question>",
      "options": ["A", "B", "C", "D"],
      "correct_option_index": <0-3>,
      "fact": "<one short fun fact about the answer>"
    }}
  ]
}}

NUMBER_OF_QUESTIONS = {num_questions}
Do NOT include any extra text outside JSON.

TOPIC: {topic}
DIFFICULTY: {difficulty}
"""

    resp = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
        config=types.GenerateContentConfig(response_mime_type="application/json",
            http_options=quiz_generator_agent.config.RETRY_CONFIG),
    )

    return json.loads(resp.text)


quiz_agent = Agent(
    model="gemini-2.5-flash",
    name="quiz_designer_agent",
    description="Designs a multiple-choice quiz for a topic.",
    instruction=(
        "You ONLY design quizzes.\n"
        "When the tool 'design_quiz' is called, you MUST call it and return the JSON.\n"
        "Do not chat with the user directly."
    ),
    tools=[design_quiz],
)
