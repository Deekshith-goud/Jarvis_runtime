# Jarvis Runtime Test Starter Pack

## Run

```powershell
pytest
```

`pytest.ini` is scoped to `tests/` so legacy ad-hoc scripts are not collected.

## Current Coverage Added

- Command contracts and normalization:
  - `CommandResult` success/failure factory behavior
  - command normalization cleanup and duplicate-half reduction
  - segment splitting for multi-action commands
- Entity resolution:
  - exact, prefix, fuzzy, and no-match behavior
  - alias/fuzzy resolution via `EntityRegistry`
- AI routing:
  - task routing priority (`code` over generic explain)
  - language detection and output format mapping
- Safety guard:
  - filename sanitization/length limits
  - confirmation requirement for executable extensions
  - output length speaking threshold
- Storage/session integration:
  - session memory update/get behavior
  - database task lifecycle and macro lifecycle

## High-Value Next Tests

- Router integration (`route_command`) with dependency mocks
- Voice/CLI parity tests for same normalized input
- Retry/fallback tests for AI failure paths
- Security tests for command injection and path traversal policies
- Timer/reminder scheduling with clock control fixtures
