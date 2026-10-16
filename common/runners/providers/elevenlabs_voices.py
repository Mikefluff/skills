"""ElevenLabs voices and dialogue — design a voice, keep it, add an actor from the Voice Library, read a scene.
Vendor: ElevenLabs (Voice Design, Voice Library, Text to Dialogue).

Split from `elevenlabs.py`, which holds the providers the batch runner drives
(music, TTS, sound effects); these are plain calls the drama runners make.
"""

from __future__ import annotations

import base64
import os
from typing import Any

from ..errors import ProviderError
from . import _http


def design_voice(description: str, text: str, *, seed: int | None = None) -> bytes:
    """A new voice from a description, speaking `text` (100-1000 characters) — POST /v1/text-to-voice/design.

    Returns the first preview as MP3. A drama gives each character one such
    sample and hands it to every scene as that character's voice reference, so
    the same person does not sound different from scene to scene.
    """
    return designed_voice(description, text, seed=seed)[0]


def designed_voice(description: str, text: str, *, seed: int | None = None) -> tuple[bytes, str]:
    """The first preview of a designed voice and its generated_voice_id, which `save_voice` keeps."""
    body: dict[str, Any] = {"voice_description": description, "text": text, "model_id": "eleven_multilingual_ttv_v2"}
    if seed is not None:
        body["seed"] = seed
    resp = _http.post(
        "eleven-tts",
        "https://api.elevenlabs.io/v1/text-to-voice/design?output_format=mp3_44100_128",
        json=body,
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
        timeout=180,
    )
    previews = resp.json().get("previews") or []
    if not previews:
        raise ProviderError("eleven-tts", None, "voice design returned no preview")
    return base64.b64decode(previews[0]["audio_base_64"]), previews[0]["generated_voice_id"]


def save_voice(name: str, description: str, generated_voice_id: str) -> str:
    """Keep a designed voice in the account — POST /v1/text-to-voice; returns the voice_id TTS takes."""
    resp = _http.post(
        "eleven-tts",
        "https://api.elevenlabs.io/v1/text-to-voice",
        json={"voice_name": name, "voice_description": description[:1000], "generated_voice_id": generated_voice_id},
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
        timeout=120,
    )
    return resp.json()["voice_id"]


def add_library_voice(owner_id: str, voice_id: str, name: str) -> str:
    """Add a Voice Library voice to the account — POST /v1/voices/add/{owner}/{voice}; returns its voice_id here.

    Voice Library voices are recorded actors; Eleven v4 performs audio tags far
    better on them than on Voice Design voices, which its own docs call less performative.
    """
    resp = _http.post(
        "eleven-tts",
        f"https://api.elevenlabs.io/v1/voices/add/{owner_id}/{voice_id}",
        json={"new_name": name[:100]},
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
        timeout=60,
    )
    return resp.json().get("voice_id") or voice_id


def dialogue(inputs: list[dict[str, str]], *, stability: float = 0.0, language: str | None = None,
             model_id: str = "eleven_v4", effects: dict[str, Any] | None = None) -> tuple[bytes, list[dict[str, Any]]]:
    """Several speakers in one take — POST /v1/text-to-dialogue/with-timestamps (Eleven v4 by default).

    `inputs` are {"text", "voice_id"} in order; the text may carry v3 audio tags
    ("[sarcastic] Percent?"). One take gives real turn-taking — each line reacts
    to the one before it — which lines read one by one never do. Returns the MP3
    and the voice segments {start_time_seconds, end_time_seconds, dialogue_input_index}.
    """
    body: dict[str, Any] = {"inputs": inputs, "model_id": model_id, "settings": {"stability": stability}}
    if language:
        body["language_code"] = language
    if effects:
        # {"environment_id": "small_room", "filter_preset_id": "phone", "distance": 0.2, ...}; ids from
        # GET /v1/audio-effects/catalog. The room the scene is in, heard in the voice itself.
        body["audio_effects"] = effects
    resp = _http.post(
        "eleven-tts",
        "https://api.elevenlabs.io/v1/text-to-dialogue/with-timestamps?output_format=mp3_44100_128",
        json=body,
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
        timeout=300,
    )
    data = resp.json()
    return base64.b64decode(data["audio_base64"]), data.get("voice_segments") or []
