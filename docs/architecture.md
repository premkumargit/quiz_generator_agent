
# Architecture Overview

```mermaid
flowchart TD
    U[User / Gradio UI] -->|topic, difficulty, num_questions| ORCH[Orchestrator Agent]

    subgraph Agents & Tools
        ORCH -->|tool: design_quiz| QA[Quiz Agent\ndesign_quiz()]
        QA -->|quiz JSON| ORCH

        ORCH -->|tool: build_storyboard| SB[Storyboard Agent\nbuild_storyboard()]
        SB -->|storyboard JSON| ORCH

        ORCH -->|tool: render_video_from_storyboard| VA[Video Agent\nrender_video_from_storyboard()]

        subgraph Audio
            VA -->|uses tool: synthesize_audio per scene| AA[Audio Agent\nsynthesize_audio()]
            AA -->|WAV files| VA
        end

        VA -->|final_video, output_dir| ORCH
    end

    ORCH -->|JSON: final_video, output_dir| U
    U -->|plays video| V[Gradio Video Player]
```

## Components

- Gradio UI: Collects user input (topic, difficulty, number of questions) and displays the final MP4.
- Orchestrator Agent: High-level planner that calls tools from the specialized agents and returns a strict JSON summary.
- Quiz Agent: Creates a structured quiz JSON using Gemini 2.5 Flash.
- Storyboard Agent: Converts quiz JSON into an ordered sequence of scenes with type, text, duration_sec, and voiceover.
- Audio Agent: Uses Gemini 2.5 Flash Preview TTS for questions, timer sound effects for countdown (with a reusable countdown clip).
- Video Agent: Generates all audio in parallel, renders slides with MoviePy, and stitches everything into quiz_video_local.mp4.
