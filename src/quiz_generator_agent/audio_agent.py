
import wave
from pathlib import Path

import quiz_generator_agent.config

from google import genai
from google.genai import types
from google.adk.agents.llm_agent import Agent
import logging

logger = logging.getLogger(__name__)
client = genai.Client()

AUDIO_ROOT = Path("outputs/audio_cache")


def _write_pcm_to_wav(
    filename: Path,
    pcm_data: bytes,
    channels: int = 1,
    rate: int = 24000,
    sample_width: int = 2,
) -> str:
    filename.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(filename), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)
    return str(filename)


def _create_silent_audio(filename: Path, duration: float = 2.0) -> str:
    """Create a silent WAV file with the specified duration."""
    filename.parent.mkdir(parents=True, exist_ok=True)

    # Audio parameters for silent WAV
    sample_rate = 44100
    channels = 1  # mono
    sample_width = 2  # 16-bit
    num_samples = int(sample_rate * duration)

    # Create silent PCM data (all zeros)
    silent_data = b'\x00\x00' * num_samples

    with wave.open(str(filename), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(silent_data)

    return str(filename)


def _create_timer_audio(filename: Path, duration: float = 3.0) -> str:
    """Create a simple timer sound effect with ticking/beeping."""
    filename.parent.mkdir(parents=True, exist_ok=True)

    # Audio parameters
    sample_rate = 44100
    channels = 1  # mono
    sample_width = 2  # 16-bit

    # Timer parameters
    tick_duration = 0.1  # 100ms per tick
    pause_duration = 0.9  # 900ms pause between ticks
    ticks = max(1, int(duration / (tick_duration + pause_duration)))  # Number of ticks

    import math

    audio_data = []

    for tick in range(ticks):
        # Generate tick sound (short beep)
        tick_samples = int(sample_rate * tick_duration)
        for i in range(tick_samples):
            # Create a 1000Hz sine wave for the tick
            t = float(i) / sample_rate
            # Fade in/out to avoid clicks
            fade_samples = int(tick_samples * 0.1)
            if i < fade_samples:
                amplitude = i / fade_samples
            elif i > tick_samples - fade_samples:
                amplitude = (tick_samples - i) / fade_samples
            else:
                amplitude = 1.0

            sample = int(amplitude * 32767 * 0.3 * math.sin(2 * math.pi * 1000 * t))
            audio_data.append(sample.to_bytes(2, signed=True, byteorder='little'))

        # Add pause (silence)
        pause_samples = int(sample_rate * pause_duration)
        for _ in range(pause_samples):
            audio_data.append((0).to_bytes(2, signed=True, byteorder='little'))

    # Write the WAV file
    with wave.open(str(filename), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(audio_data))

    return str(filename)


def synthesize_audio(
    text: str,
    output_dir: str,
    scene_id: str,
    voice_name: str = "Kore",
) -> str:
    """Convert voiceover text to speech via Gemini 2.5 Flash Preview TTS and save as WAV. Uses timer sound effects for countdown."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if text.strip().upper() == "TIMER_COUNTDOWN":
        AUDIO_ROOT.mkdir(parents=True, exist_ok=True)
        shared_path = AUDIO_ROOT / "timer_countdown.wav"
        if shared_path.exists():
            return str(shared_path)

        # Create timer sound effect instead of TTS voiceover
        logger.info("Creating timer sound effect...")
        return _create_timer_audio(shared_path, duration=3.0)

    wav_path = output_dir / f"{scene_id}.wav"
    if wav_path.exists():
        return str(wav_path)

    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                http_options=quiz_generator_agent.config.RETRY_CONFIG,
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name
                        )
                    ),
                ),
            ),
        )

        # Check if TTS response is valid
        if not resp.candidates or not resp.candidates[0] or not resp.candidates[0].content:
            logger.warning(f"Gemini TTS returned invalid response for text: '{text}'")
            raise ValueError("TTS model returned invalid response")

        audio_bytes = resp.candidates[0].content.parts[0].inline_data.data
        return _write_pcm_to_wav(wav_path, audio_bytes)
    except Exception as e:
        logger.warning(f"Gemini TTS failed for text '{text}' ({e}), falling back to silent audio")
        # Fallback: Create silent audio file
        return _create_silent_audio(wav_path, duration=max(2.0, len(text.split()) / 150 * 60))


audio_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="audio_generation_agent",
    description="Generates speech audio files from voiceover text using Gemini 2.5 Flash Preview TTS, with timer sound effects.",
    instruction=(
        "You only generate audio files from text.\n"
        "When the 'synthesize_audio' tool is called, use it and return the file path.\n"
        "If the text equals 'TIMER_COUNTDOWN', reuse a shared countdown audio file."
    ),
    tools=[synthesize_audio],
)
