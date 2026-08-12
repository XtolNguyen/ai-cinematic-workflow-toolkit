"""
Runnable music-video example.

This example creates a three-scene cinematic project, processes it
through the workflow engine, prints generated prompts and continuity
reports, and exports the complete project to JSON.
"""

from pathlib import Path

from ai_cinematic_workflow import (
    Camera,
    CinematicProject,
    ProjectMetadata,
    Scene,
    process_project,
)
from ai_cinematic_workflow.exporters.project_json_exporter import (
    save_project_json,
)


def create_demo_project() -> CinematicProject:
    """Create a small three-scene music-video project."""

    metadata = ProjectMetadata(
        title="Neon Echoes",
        project_type="music-video",
        description=(
            "Demonstration project for the "
            "AI Cinematic Workflow Toolkit."
        ),
        language="en",
        target_platform="AI video",
        aspect_ratio="16:9",
        frame_rate=24,
    )

    common_camera = Camera(
        shot="medium close-up",
        movement="slow dolly in",
        lens="50mm",
    )

    scene_1 = Scene(
        scene_id=1,
        duration_seconds=15,
        location="Neon cinematic performance stage",
        camera=common_camera,
        characters=["Lead performer"],
        performance=(
            "Natural emotional performance "
            "with subtle body movement"
        ),
        lighting="Soft blue and magenta cinematic lighting",
        mood="Reflective",
        dialogue_or_vocals="Professional emotional vocal performance",
        continuity={
            "wardrobe": "black cinematic outfit",
            "hair": "long dark hair",
        },
        negative_constraints=[
            "Distorted Face",
            "Extra Fingers",
            "Camera Jitter",
            "distorted face",
        ],
    )

    scene_2 = Scene(
        scene_id=2,
        duration_seconds=15,
        location="Neon cinematic performance stage",
        camera=Camera(
            shot="close-up",
            movement="slow push in",
            lens="85mm",
        ),
        characters=["Lead performer"],
        performance=(
            "Emotion increases while maintaining "
            "natural professional performance"
        ),
        lighting="Soft blue and magenta cinematic lighting",
        mood="Emotional",
        dialogue_or_vocals="Professional emotional vocal performance",
        continuity={
            "wardrobe": "black cinematic outfit",
            "hair": "long dark hair",
        },
        negative_constraints=[
            "Distorted Face",
            "Extra Fingers",
            "Camera Jitter",
        ],
    )

    scene_3 = Scene(
        scene_id=3,
        duration_seconds=15,
        location="Neon cinematic performance stage",
        camera=Camera(
            shot="medium shot",
            movement="slow orbit",
            lens="50mm",
        ),
        characters=["Lead performer"],
        performance=(
            "Controlled cinematic performance "
            "during the final musical phrase"
        ),
        lighting="Soft blue and magenta cinematic lighting",
        mood="Powerful and cinematic",
        dialogue_or_vocals="Professional emotional vocal performance",
        continuity={
            # Intentionally changed to demonstrate continuity detection.
            "wardrobe": "white cinematic outfit",
            "hair": "long dark hair",
        },
        negative_constraints=[
            "Distorted Face",
            "Extra Fingers",
            "Camera Jitter",
        ],
    )

    return CinematicProject(
        metadata=metadata,
        scenes=[
            scene_1,
            scene_2,
            scene_3,
        ],
    )


def main() -> None:
    """Run the complete demonstration workflow."""

    project = create_demo_project()

    print("=" * 72)
    print("AI CINEMATIC WORKFLOW TOOLKIT — MUSIC VIDEO DEMO")
    print("=" * 72)

    print(f"Project: {project.metadata.title}")
    print(f"Scenes: {project.scene_count}")
    print(
        "Total duration: "
        f"{project.total_duration_seconds} seconds"
    )

    print()

    results = process_project(
        project.scenes
    )

    for result in results:
        print("-" * 72)
        print(f"SCENE {result.scene_id}")
        print("-" * 72)

        print("Prompt:")
        print(result.prompt)

        print()
        print("Negative Prompt:")
        print(result.negative_prompt)

        if result.continuity_issues:
            print()
            print("Continuity Issues:")

            for issue in result.continuity_issues:
                print(
                    f"- {issue['field']}: "
                    f"{issue['previous_value']} -> "
                    f"{issue['current_value']}"
                )
        else:
            print()
            print("Continuity Issues: none")

        print()

    output_path = Path(
        "examples/output/music_video_project.json"
    )

    saved_path = save_project_json(
        project,
        output_path,
    )

    print("=" * 72)
    print("PROJECT EXPORT COMPLETE")
    print("=" * 72)
    print(f"JSON saved to: {saved_path}")


if __name__ == "__main__":
    main()
