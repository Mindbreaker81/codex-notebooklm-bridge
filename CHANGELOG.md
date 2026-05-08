# Changelog

All notable changes to the NotebookLM Codex skill are tracked here.

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
- Validated Chrome plugin flow against the Example Research Notebook test notebook.
- Validated Computer Use as a separate fallback flow.
