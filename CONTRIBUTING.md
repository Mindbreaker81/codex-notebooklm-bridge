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

- Use Spanish for user-facing README sections when practical.
- Use English for internal skill instructions and technical validation docs when
  it improves precision or matches the existing file.
- Keep JSON deterministic and valid.
- Prefer small, explicit changes over large rewrites.

## Pull requests

- Explain what changed and why.
- Mention any validation you ran.
- Call out any behavior changes in the skill or the library workflow.
