# Pull Request

Thank you for contributing to **AI Cinematic Workflow Toolkit**.

Please complete the sections below so the proposed change can be reviewed efficiently.

---

## Summary

Describe what this pull request changes.

Explain the main purpose of the contribution and the problem it solves.

---

## Related Issue

Link any related Issue if applicable.

Example:

```text
Closes #123
```

If no Issue exists, write:

```text
Not applicable
```

---

## Type of Change

Select all that apply:

* [ ] New feature
* [ ] Bug fix
* [ ] Refactor
* [ ] Documentation
* [ ] Test improvement
* [ ] CI / automation
* [ ] Example project
* [ ] Exporter
* [ ] Workflow logic
* [ ] Platform-specific adapter
* [ ] Other

---

## Affected Components

Select all relevant areas:

* [ ] Scene Model
* [ ] Scene Validation
* [ ] Prompt Builder
* [ ] Negative Constraint Validator
* [ ] Continuity Validator
* [ ] Workflow Engine
* [ ] Cinematic Project Model
* [ ] JSON Export
* [ ] Public Python API
* [ ] Example Project
* [ ] Documentation
* [ ] Packaging
* [ ] GitHub Actions
* [ ] Other

---

## What Changed?

Describe the implementation in enough detail for reviewers to understand the approach.

Include important architectural decisions when relevant.

---

## Cinematic Workflow Impact

Does this pull request change any cinematic workflow behavior?

Examples:

* Scene validation rules
* Prompt construction
* Continuity detection
* Negative constraints
* Project structure
* Export format
* Scene ordering
* Duration handling
* Platform-specific behavior

If yes, explain the expected behavior before and after this change.

If not, write:

```text
No cinematic workflow behavior changed.
```

---

## Platform Scope

Choose the most appropriate option:

* [ ] Platform-agnostic core change
* [ ] Platform-specific adapter
* [ ] Development tooling only
* [ ] Documentation only
* [ ] Not applicable

If this is platform-specific, identify the platform and explain why the behavior does not belong in the core toolkit.

---

## Testing

Describe how the change was tested.

Examples:

```bash
pytest
```

```bash
python examples/music_video_project.py
```

Include any additional commands or manual validation steps used.

---

## Test Results

Provide a short summary of the results.

Example:

```text
All automated tests pass.
Music-video example runs successfully.
Generated JSON output validated.
```

---

## Backward Compatibility

Does this change affect existing public APIs or project data?

* [ ] No breaking changes
* [ ] Public API changed
* [ ] Export format changed
* [ ] Scene or project schema changed
* [ ] Existing behavior changed
* [ ] Breaking change

If compatibility is affected, explain the migration path.

---

## Documentation

Select the appropriate option:

* [ ] Documentation was updated
* [ ] Documentation is not required
* [ ] README was updated
* [ ] CHANGELOG was updated
* [ ] Example usage was updated

---

## Security Considerations

Does this change introduce or modify:

* File handling
* External input parsing
* Credentials
* Network access
* Dependencies
* Platform integrations
* Command execution

If yes, describe relevant security considerations.

Do not include private credentials, API keys, tokens, or vulnerability details that should remain private.

---

## Screenshots / Output

Add screenshots, command output, generated JSON excerpts, or other evidence when useful.

Remove this section if it is not applicable.

---

## Contributor Checklist

Before requesting review:

* [ ] I reviewed the existing Issues and pull requests for related work.
* [ ] My changes are focused and do not include unrelated modifications.
* [ ] The project installs successfully.
* [ ] I ran the relevant automated tests.
* [ ] Existing tests continue to pass.
* [ ] I added tests for new behavior where appropriate.
* [ ] Public functions or classes have useful documentation.
* [ ] I updated documentation when public behavior changed.
* [ ] I did not commit generated files that should be ignored.
* [ ] I did not include passwords, API keys, tokens, or other private credentials.
* [ ] Platform-specific behavior is isolated from the core toolkit when appropriate.
* [ ] I considered backward compatibility.
