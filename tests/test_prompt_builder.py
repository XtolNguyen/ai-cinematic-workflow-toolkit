from ai_cinematic_workflow import Camera, Scene
from ai_cinematic_workflow.prompt_builder import build_cinematic_prompt


def test_build_cinematic_prompt():
    """A valid scene should generate a structured cinematic prompt."""

    scene = Scene(
        scene_id=1,
        duration_seconds=15,
        location="Rainy neon city street",
        camera=Camera(
            shot="close-up",
            movement="slow push in",
            lens="85mm",
        ),
        characters=["Lead performer"],
        performance="Natural emotional performance",
        lighting="Soft neon cinematic lighting",
        mood="Dramatic and reflective",
        dialogue_or_vocals="Emotional vocal performance",
        continuity={
            "wardrobe": "black cinematic outfit",
            "weather": "light rain",
        },
        negative_constraints=[
            "distorted face",
            "extra fingers",
            "camera jitter",
        ],
    )

    result = build_cinematic_prompt(scene)

    assert "Scene 1: Rainy neon city street." in result.prompt
    assert "Characters: Lead performer." in result.prompt
    assert "Performance: Natural emotional performance." in result.prompt

    assert (
        "Camera: close-up, slow push in, 85mm."
        in result.prompt
    )

    assert (
        "Lighting: Soft neon cinematic lighting."
        in result.prompt
    )

    assert "Mood: Dramatic and reflective." in result.prompt

    assert (
        "Dialogue/Vocals: Emotional vocal performance."
        in result.prompt
    )

    assert "wardrobe: black cinematic outfit" in result.prompt
    assert "weather: light rain" in result.prompt

    assert result.negative_prompt == (
        "distorted face, extra fingers, camera jitter"
    )


def test_prompt_builder_rejects_invalid_scene():
    """Invalid scene data should be rejected before prompt generation."""

    scene = Scene(
        scene_id=1,
        duration_seconds=0,
        location="Studio",
        camera=Camera(
            shot="medium shot",
        ),
    )

    try:
        build_cinematic_prompt(scene)
    except ValueError as error:
        assert "duration_seconds must be greater than 0" in str(error)
    else:
        raise AssertionError(
            "Expected build_cinematic_prompt to reject an invalid scene"
        )
