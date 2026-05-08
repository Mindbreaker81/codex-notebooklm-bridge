# Contributing

## What this repository is for

This repository contains the `notebooklm` Codex skill and its support files.

## Before opening a pull request

- Run the local checks that exist in the repo.
- Make sure no secrets, tokens, or personal data are added.
- Keep changes focused and easy to review.

## Useful validation commands

```bash
python .agents/skills/notebooklm/scripts/library.py validate
python -m pytest
```

## Style

- Keep docs in Spanish when they describe the skill behavior.
- Keep JSON deterministic and valid.
- Prefer small, explicit changes over large rewrites.

## Pull requests

- Explain what changed and why.
- Mention any validation you ran.
- Call out any behavior changes in the skill or the library workflow.