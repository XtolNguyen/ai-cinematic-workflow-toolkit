from ai_cinematic_workflow import Camera, Scene
from ai_cinematic_workflow.workflow import (
    process_project,
    process_scene,
)


def make_scene(
    scene_id: int,
    *,
    wardrobe: str = "black outfit",
    location: str = "Cinematic studio",
    duration_seconds: float = 15,
) -> Scene:
    """Create a reusable cinematic scene for workflow tests."""

    return Scene(
        scene_id=scene_id,
        duration_seconds=duration_seconds,
        location=location,
        camera=Camera(
            shot="medium shot",
            movement="slow dolly in",
            lens="50mm",
        ),
        characters=["Lead performer"],
        performance="Natural emotional performance",
        lighting="Soft cinematic lighting",
        mood="Emotional",
        dialogue_or_vocals="Professional vocal performance",
        continuity={
            "wardrobe": wardrobe,
            "hair": "long dark hair",
        },
        negative_constraints=[
            "Distorted Face",
            " extra fingers ",
            "Camera Jitter",
            "distorted face",
        ],
    )


def test_process_single_scene():
    """A valid scene should pass through the complete workflow."""

    scene = make_scene(1)

    result = process_scene(scene)

    assert result.valid
    assert result.validation_errors == []

    assert "Scene 1: Cinematic studio." in result.prompt
    assert "Characters: Lead performer." in result.prompt

    assert result.negative_prompt == (
        "distorted face, extra fingers, camera jitter"
    )

    assert result.continuity_issues == []


def test_invalid_scene_stops_prompt_generation():
    """Invalid scene data should not generate a prompt."""

    scene = make_scene(
        1,
        duration_seconds=0,
    )

    result = process_scene(scene)

    assert not result.valid

    assert (
        "duration_seconds must be greater than 0"
        in result.validation_errors
    )

    assert result.prompt == ""
    assert result.negative_prompt == ""


def test_project_detects_continuity_change():
    """Scene-to-scene wardrobe changes should be reported."""

    scene_1 = make_scene(
        1,
        wardrobe="black outfit",
    )

    scene_2 = make_scene(
        2,
        wardrobe="white outfit",
    )

    results = process_project(
        [
            scene_1,
            scene_2,
        ]
    )

    assert len(results) == 2

    assert results[0].valid
    assert results[1].valid

    assert results[0].continuity_issues == []

    issue_fields = {
        issue["field"]
        for issue in results[1].continuity_issues
    }

    assert "continuity.wardrobe" in issue_fields


def test_multiple_scenes_generate_prompts():
    """Every valid scene should receive its own cinematic prompt."""

    scenes = [
        make_scene(
            1,
            location="Cinematic studio",
        ),
        make_scene(
            2,
            location="Night rooftop",
        ),
        make_scene(
            3,
            location="Rainy city street",
        ),
    ]

    results = process_project(scenes)

    assert len(results) == 3

    assert all(
        result.valid
        for result in results
    )

    assert "Cinematic studio" in results[0].prompt
    assert "Night rooftop" in results[1].prompt
    assert "Rainy city street" in results[2].prompt


def test_workflow_result_is_serializable():
    """Workflow results should convert to structured dictionaries."""

    scene = make_scene(1)

    result = process_scene(scene)
    data = result.to_dict()

    assert data["scene_id"] == 1
    assert data["valid"] is True
    assert isinstance(data["prompt"], str)
    assert isinstance(data["negative_prompt"], str)
    assert isinstance(data["continuity_issues"], list)
