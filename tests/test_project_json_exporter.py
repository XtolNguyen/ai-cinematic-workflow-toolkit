import json

import pytest

from ai_cinematic_workflow import Camera, Scene
from ai_cinematic_workflow.exporters.project_json_exporter import (
    project_to_dict,
    project_to_json,
    save_project_json,
)
from ai_cinematic_workflow.project import (
    CinematicProject,
    ProjectMetadata,
)


def make_scene(
    scene_id: int,
    *,
    wardrobe: str = "black outfit",
    duration_seconds: float = 15,
) -> Scene:
    """Create a reusable scene for project exporter tests."""

    return Scene(
        scene_id=scene_id,
        duration_seconds=duration_seconds,
        location="Cinematic performance stage",
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
            "Extra Fingers",
            "Camera Jitter",
            "distorted face",
        ],
    )


def make_project() -> CinematicProject:
    """Create a three-scene cinematic project."""

    metadata = ProjectMetadata(
        title="Project Export Test",
        project_type="music-video",
        description="End-to-end JSON export test",
        language="en",
        target_platform="AI video",
        aspect_ratio="16:9",
        frame_rate=24,
    )

    return CinematicProject(
        metadata=metadata,
        scenes=[
            make_scene(
                1,
                wardrobe="black outfit",
            ),
            make_scene(
                2,
                wardrobe="white outfit",
            ),
            make_scene(
                3,
                wardrobe="white outfit",
            ),
        ],
    )


def test_project_to_dict():
    """A complete project should produce structured workflow data."""

    project = make_project()

    data = project_to_dict(project)

    assert data["project"]["metadata"]["title"] == (
        "Project Export Test"
    )

    assert data["project"]["summary"]["scene_count"] == 3

    assert (
        data["project"]["summary"]["total_duration_seconds"]
        == 45
    )

    workflow = data["workflow"]

    assert len(workflow["scene_results"]) == 3

    assert workflow["summary"]["processed_scenes"] == 3
    assert workflow["summary"]["valid_scenes"] == 3

    assert (
        workflow["summary"]["scenes_with_continuity_issues"]
        == 1
    )

    assert (
        workflow["summary"]["scenes_with_negative_warnings"]
        == 0
    )


def test_project_json_contains_scene_prompts():
    """Every processed scene should contain a generated prompt."""

    project = make_project()

    content = project_to_json(project)
    data = json.loads(content)

    results = data["workflow"]["scene_results"]

    assert len(results) == 3

    assert "Scene 1:" in results[0]["prompt"]
    assert "Scene 2:" in results[1]["prompt"]
    assert "Scene 3:" in results[2]["prompt"]

    assert results[0]["negative_prompt"] == (
        "distorted face, extra fingers, camera jitter"
    )


def test_project_json_detects_wardrobe_continuity_change():
    """The exporter should preserve continuity warnings."""

    project = make_project()

    data = project_to_dict(project)

    scene_2_result = data["workflow"]["scene_results"][1]

    issue_fields = {
        issue["field"]
        for issue in scene_2_result["continuity_issues"]
    }

    assert "continuity.wardrobe" in issue_fields

    assert (
        data["workflow"]["scene_results"][2][
            "continuity_issues"
        ]
        == []
    )


def test_save_project_json(tmp_path):
    """A complete project should save to a real JSON file."""

    project = make_project()

    output_path = (
        tmp_path
        / "exports"
        / "cinematic_project.json"
    )

    saved_path = save_project_json(
        project,
        output_path,
    )

    assert saved_path == output_path
    assert saved_path.exists()

    data = json.loads(
        saved_path.read_text(
            encoding="utf-8"
        )
    )

    assert data["project"]["metadata"]["title"] == (
        "Project Export Test"
    )

    assert data["project"]["summary"]["scene_count"] == 3


def test_invalid_project_cannot_be_exported():
    """Invalid projects should be rejected before JSON export."""

    invalid_project = CinematicProject(
        metadata=ProjectMetadata(
            title="",
        ),
        scenes=[],
    )

    with pytest.raises(
        ValueError,
        match="Project validation failed",
    ):
        project_to_json(
            invalid_project
        )
