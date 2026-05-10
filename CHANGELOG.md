# Changelog

All notable changes to the NotebookLM Codex skill are tracked here.

## 0.5.0 - 2026-05-10

- Removed the stray `._SKILL.md` AppleDouble metadata file from the skill tree.
- Normalized NotebookLM URLs on `add`/`update` to strip query strings and
  fragments so `library.json` stores the canonical notebook URL.
- Added `set-active --clear` as the explicit way to clear the active notebook;
  the `none` positional argument is kept as a deprecated alias.
- Added English UI aliases (`Query box`, `Start typing...`, `Send`,
  `Response ready.`) alongside the Spanish strings in `SKILL.md`.
- Documented the follow-up policy: default 1-2 follow-ups, allow more only when
  the user explicitly asks for deeper digging.
- Added a `version` field to `agents/openai.yaml`.
- Added a GitHub Actions workflow that runs `pytest` for the library script.
- Added a minimal `pyproject.toml` configuring pytest's `testpaths`. Pytest
  itself is installed separately (`pip install pytest`).
- Added a pre-commit hook that flags suspiciously long real-looking notebook
  IDs in tracked files.

## 0.4.0 - 2026-05-08

- Added an explicit DOM vs UI/accessibility extraction strategy.
- Preferred DOM/Playwright for exact URLs, titles, source lists, answer text,
  citations, and truncated accessibility content.
- Updated notebook registration and empty-library flows to try scoped DOM
  extraction before asking the user for data already visible in NotebookLM.
- Clarified DOM fallback rules: use UI/accessibility or screenshots when DOM is
  incomplete, and never invent metadata.

## 0.3.0 - 2026-05-08

- Made empty-library handling proactive: `list my notebooks` no longer stops at
  `No notebooks registered.` unless raw CLI output was explicitly requested.
- Added registration recovery flows for NotebookLM URLs, NotebookLM home
  selection, and unavailable browser control.
- Added selection repair rules for invalid `active_notebook_id`, unmatched
  topics, single-notebook libraries, and ambiguous notebook matches.
- Added weak-answer handling that asks 1-2 targeted NotebookLM follow-ups before
  reporting insufficient source coverage.
- Updated usage patterns and testing guidance for proactive library workflows.

## 0.2.0 - 2026-05-08

- Clarified installation paths for workspace-local and global Codex use.
- Documented Chrome plugin vs Computer Use fallback reporting rules.
- Added reproducible validated-flow documentation for Chrome plugin and
  Computer Use fallback.
- Added manual pressure tests for citation handling, fallback labeling, notebook
  selection, and metadata safety.
- Added `scripts/library.py` for deterministic `library.json` maintenance.
- Added automated tests for the library maintenance script.

## 0.1.0 - 2026-05-08

- Added initial `notebooklm` skill.
- Documented NotebookLM querying through authenticated Chrome.
- Added local `data/library.json` notebook registry.
- Added usage pattern reference docs.
- Validated Chrome plugin flow against a private NotebookLM test notebook.
- Validated Computer Use as a separate fallback flow.
