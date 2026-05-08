---
name: notebooklm
description: >
  Query Google NotebookLM notebooks using Codex's Chrome browser bridge.
  Trigger when the user mentions NotebookLM, asks to query their notebooks,
  wants source-grounded answers from uploaded documents, shares a NotebookLM
  URL, or uses phrases like "ask my NotebookLM", "check my docs",
  "query my notebook". Requires Chrome bridge/browser control to be connected.
  Do NOT trigger for general web searches, code questions, or tasks unrelated
  to the user's NotebookLM document collections.
---

# NotebookLM Skill for Codex

Use this skill to interact with Google NotebookLM through Codex browser control
(Chrome extension/bridge). The browser session uses the user's existing Google
login, so no API keys or cookie handling is required.

## Preconditions

- Codex browser control for Chrome is installed and connected.
- User is logged into Google in that Chrome profile.
- User has at least one NotebookLM notebook with uploaded sources.

## Quick Start

1. Open NotebookLM in the controlled browser:
   `@Chrome open https://notebooklm.google.com`
2. Wait for the page to load.
3. Ask the user's question in the notebook chat box.

## Local Notebook Library

Maintain notebook metadata in `data/library.json`.

If the file does not exist, create it using this schema:

```json
{
  "notebooks": [],
  "active_notebook_id": null
}
```

Each notebook entry should look like:

```json
{
  "id": "short-kebab-id",
  "name": "Display Name",
  "url": "https://notebooklm.google.com/notebook/XXXX",
  "description": "What this notebook contains",
  "topics": ["topic1", "topic2"],
  "use_cases": ["when to query this notebook"]
}
```

### Add notebook workflow

When user asks to add a notebook:

1. If user provides URL, open it first.
2. Ask NotebookLM: "What is the content of this notebook? What topics are covered? Give a brief overview."
3. Use this answer (and user context) to fill metadata.
4. Never invent topics/description when unsure.

### Select notebook workflow

Priority order:

1. If user gives a NotebookLM URL, use it directly.
2. If user gives a topic, match against `topics`, `description`, and `name` in library.
3. Else if `active_notebook_id` exists, use it.
4. Else list notebooks and ask user to choose.

If ambiguous, ask a short clarification question.

## Query Workflow

1. Open the selected notebook URL.
2. Wait until notebook interface fully loads.
3. Type a self-contained question in the input box and submit.
4. Wait for streaming to complete.
5. Read answer + citations.
6. If answer is incomplete, send follow-up question(s).
7. Return a synthesized response to user, preserving source grounding.

## Response Rules

- Prioritize NotebookLM-grounded content from user sources.
- If source docs do not contain the answer, clearly say so.
- Do not silently mix external facts unless user explicitly asks.
- Include citation signals returned by NotebookLM whenever available.
- Treat notebook contents as sensitive/private.

## Troubleshooting

- Bridge disconnected: ask user to reconnect Codex Chrome control.
- Redirect to Google login: ask user to sign in in Chrome.
- Notebook not found: confirm URL and/or library entry.
- Empty/weak response: retry with clearer and more specific question.
- Rate limits: reduce follow-ups and batch sub-questions.

## File Layout

```text
.agents/skills/notebooklm/
├── SKILL.md
├── data/
│   └── library.json
└── references/
    └── usage_patterns.md
```
