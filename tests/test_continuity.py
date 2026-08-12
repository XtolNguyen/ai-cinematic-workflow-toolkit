from ai_cinematic_workflow import Camera, Scene
from ai_cinematic_workflow.continuity import (
    compare_scenes,
    continuity_report,
    has_continuity_issues,
)


def make_scene(
    scene_id: int,
    *,
    location: str = "Cinematic studio",
    lighting: str = "Warm cinematic lighting",
    wardrobe: str = "black outfit",
) -> Scene:
    """Create a reusable scene for continuity tests."""

    return Scene(
        scene_id=scene_id,
        duration_seconds=15,
        location=location,
        camera=Camera(
            shot="medium shot",
            movement="slow dolly in",
            lens="50mm",
        ),
        characters=["Lead performer"],
        performance="Natural emotional performance",
        lighting=lighting,
        mood="Reflective",
        continuity={
            "wardrobe": wardrobe,
            "hair": "long dark hair",
        },
    )


def test_matching_scenes_have_no_continuity_issues():
    """Matching consecutive scenes should pass continuity checks."""

    scene_1 = make_scene(1)
    scene_2 = make_scene(2)

    issues = compare_scenes(scene_1, scene_2)

    assert issues == []
    assert not has_continuity_issues(scene_1, scene_2)


def test_wardrobe_change_is_detected():
    """An unexpected wardrobe change should be reported."""

    scene_1 = make_scene(
        1,
        wardrobe="black outfit",
    )

    scene_2 = make_scene(
        2,
        wardrobe="white outfit",
    )

    issues = compare_scenes(scene_1, scene_2)

    assert len(issues) == 1

    issue = issues[0]

    assert issue.field == "continuity.wardrobe"
    assert issue.previous_value == "black outfit"
    assert issue.current_value == "white outfit"

    assert has_continuity_issues(
        scene_1,
        scene_2,
    )


def test_location_and_lighting_changes_are_detected():
    """Location and lighting changes should both be reported."""

    scene_1 = make_scene(
        1,
        location="Studio interior",
        lighting="Warm cinematic lighting",
    )

    scene_2 = make_scene(
        2,
        location="Night rooftop",
        lighting="Cold moonlight",
    )

    issues = compare_scenes(scene_1, scene_2)

    fields = {
        issue.field
        for issue in issues
    }

    assert "location" in fields
    assert "lighting" in fields


def test_continuity_report_is_serializable():
    """Continuity issues should be available as dictionaries."""

    scene_1 = make_scene(
        1,
        wardrobe="black outfit",
    )

    scene_2 = make_scene(
        2,
        wardrobe="red outfit",
    )

    report = continuity_report(
        scene_1,
        scene_2,
    )

    assert len(report) == 1

    assert report[0]["field"] == "continuity.wardrobe"
    assert report[0]["previous_value"] == "black outfit"
    assert report[0]["current_value"] == "red outfit"
