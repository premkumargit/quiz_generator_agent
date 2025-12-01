
import quiz_generator_agent.config

import gradio as gr
from typing import Tuple, Dict, Any
import json

from .main import orchestrate_quiz_video
from .orchestrator_agent import orchestrator_agent


def run_quiz_generator_agent(
    topic: str,
    num_questions: int,
    difficulty: str,
) -> Tuple[str, Dict[str, Any], str]:
    if not topic.strip():
        raise gr.Error("Please enter a topic.")

    result = orchestrate_quiz_video(
        topic=topic,
        difficulty=difficulty,
        num_questions=num_questions,
        debug=True,
    )

    final_path = result["final_video"]
    storyboard = result["storyboard"]
    topic_out = result["topic"]
    num_q = result["num_questions"]
    output_dir = result["output_dir"]
    diff = result["difficulty"]

    summary_lines = [
        f"✅ Topic: {topic_out}",
        f"✅ Difficulty: {diff}",
        f"✅ Number of questions: {num_q}",
        f"📂 Output directory: `{output_dir}`",
        f"🎬 Final video: `{final_path}`",
    ]

    return final_path, storyboard, "\n".join(summary_lines)


def run_orchestrator_flow(
    topic: str,
    num_questions: int,
    difficulty: str,
):
    if not topic.strip():
        raise gr.Error("Please enter a topic.")

    # For now, use the direct orchestration function
    # TODO: Implement proper ADK agent invocation when API stabilizes
    result = orchestrate_quiz_video(
        topic=topic,
        difficulty=difficulty,
        num_questions=num_questions,
        debug=True,
    )

    final_video = result["final_video"]
    output_dir = result["output_dir"]
    topic_out = result["topic"]
    diff_out = result["difficulty"]
    num_q_out = result["num_questions"]

    summary_lines = [
        f"🤖 Orchestrator flow (direct)",
        f"✅ Topic: {topic_out}",
        f"✅ Difficulty: {diff_out}",
        f"✅ Number of questions: {num_q_out}",
        f"📂 Output directory: `{output_dir}`",
        f"🎬 Final video: `{final_video}`",
    ]

    return final_video, "\n".join(summary_lines)


def create_interface() -> gr.Blocks:
    with gr.Blocks(title="Agentic Quiz Video Agent") as demo:
        gr.Markdown(
            """
            # 🤖 Agentic Quiz Generator Agent

            Workflow:
            1. Quiz Agent – designs a multiple-choice quiz (Gemini 2.5 Flash).  
            2. Storyboard Agent – turns the quiz into scenes with voiceover text.  
            3. Audio Agent – uses Gemini 2.5 Flash Preview TTS for questions, timer sound effects for countdown.  
            4. Video Agent – renders scenes with MoviePy and stitches them into a final video.  
            """
        )

        with gr.Row():
            topic = gr.Textbox(
                label="Topic",
                value="Fractions",
                placeholder="e.g. US National Parks, Fractions for 3rd graders, Photosynthesis...",
            )
        with gr.Row():
            num_questions = gr.Slider(
                minimum=1,
                maximum=10,
                value=3,
                step=1,
                label="Number of questions",
            )
            difficulty = gr.Dropdown(
                choices=["easy", "medium", "hard"],
                value="easy",
                label="Difficulty",
            )

        generate_btn = gr.Button("🚀 Generate Quiz Video", variant="primary")

        with gr.Row():
            final_video = gr.Video(label="Final quiz video")
        with gr.Row():
            storyboard_json = gr.JSON(label="Storyboard JSON")
        with gr.Row():
            summary = gr.Markdown(label="Run summary")

        generate_btn.click(
            fn=run_quiz_generator_agent,
            inputs=[topic, num_questions, difficulty],
            outputs=[final_video, storyboard_json, summary],
        )

        gr.Markdown("""---\n### Orchestrator Agent Flow""")
        orch_btn = gr.Button("🧠 Run Orchestrator Agent", variant="secondary")
        with gr.Row():
            orch_video = gr.Video(label="Final quiz video (orchestrator)")
        with gr.Row():
            orch_summary = gr.Markdown(label="Orchestrator summary")

        orch_btn.click(
            fn=run_orchestrator_flow,
            inputs=[topic, num_questions, difficulty],
            outputs=[orch_video, orch_summary],
        )

    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
