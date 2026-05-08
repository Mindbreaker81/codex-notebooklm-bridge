# Changelog

All notable changes to the NotebookLM Codex skill are tracked here.

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
- Validated Chrome plugin flow against the SymptomAI test notebook.
- Validated Computer Use as a separate fallback flow.
