import json

from ai_cinematic_workflow import Camera, Scene
from ai_cinematic_workflow.exporters import scene_to_json


def test_valid_scene():
    """A correctly configured scene should pass validation."""

    scene = Scene(
        scene_id=1,
        duration_seconds=15,
        location="Cinematic studio",
        camera=Camera(
            shot="medium shot",
            movement="slow dolly in",
            lens="50mm",
        ),
        characters=["Singer"],
        performance="Natural emotional performance",
        lighting="Soft cinematic lighting",
        mood="Emotional",
    )

    assert scene.is_valid()
    assert scene.validate() == []


def test_invalid_scene_duration():
    """A scene with zero duration should fail validation."""

    scene = Scene(
        scene_id=1,
        duration_seconds=0,
        location="Cinematic studio",
        camera=Camera(
            shot="medium shot",
        ),
    )

    errors = scene.validate()

    assert not scene.is_valid()
    assert "duration_seconds must be greater than 0" in errors


def test_scene_json_export():
    """A valid scene should export to structured JSON."""

    scene = Scene(
        scene_id=1,
        duration_seconds=15,
        location="Night city street",
        camera=Camera(
            shot="close-up",
            movement="slow push in",
            lens="85mm",
        ),
        characters=["Lead performer"],
        lighting="Neon cinematic lighting",
        mood="Dramatic",
        negative_constraints=[
            "distorted face",
            "extra fingers",
            "camera jitter",
        ],
    )

    result = scene_to_json(scene)
    data = json.loads(result)

    assert data["scene_id"] == 1
    assert data["duration_seconds"] == 15
    assert data["location"] == "Night city street"

    assert data["camera"]["shot"] == "close-up"
    assert data["camera"]["movement"] == "slow push in"
    assert data["camera"]["lens"] == "85mm"

    assert "distorted face" in data["negative_constraints"]
