# NotebookLM Codex Skill: Testing and Next Steps

## Current State

The repository contains a valid Codex skill at:

```text
.agents/skills/notebooklm/SKILL.md
```

Basic validation passes with:

```bash
python /Users/erosales/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/notebooklm
```

The local notebook library exists and is valid JSON:

```text
.agents/skills/notebooklm/data/library.json
```

Current limitation: the library is empty, so only URL-based testing can start immediately.

## Main Unknown

The skill assumes Codex can control Chrome through a browser bridge using instructions such as:

```text
@Chrome open https://notebooklm.google.com
```

Before testing NotebookLM behavior, confirm that this is the correct invocation surface for the installed Codex browser/plugin. If the actual tool name or command syntax differs, update `SKILL.md` before running functional tests.

## What Still Needs Testing

### 1. Skill Discovery

Goal: confirm Codex can discover and load the skill.

Test:

```text
Use $notebooklm to list my notebooks.
```

Expected result:

- Codex loads the `notebooklm` skill.
- Codex reads `data/library.json`.
- Because the library is empty, Codex reports that no notebooks are registered yet.
- Codex asks for a NotebookLM URL or a notebook to add.

Pass condition:

- The skill triggers without manually pasting the skill instructions.

### 2. Browser Bridge Availability

Goal: confirm Codex can open NotebookLM in the controlled browser.

Test:

```text
Use $notebooklm to open https://notebooklm.google.com
```

Expected result:

- Codex opens NotebookLM through the configured browser bridge.
- The browser uses the user's existing Google login.
- If login is required, Codex reports that the user must sign in.

Pass condition:

- NotebookLM loads in an authenticated browser session controlled by Codex.

Blocking failure:

- Codex has no callable browser bridge.
- The `@Chrome open` syntax is unsupported.
- The browser opens but Codex cannot inspect or interact with the page.

### 3. Direct URL Query

Goal: validate the simplest functional path without relying on the local library.

Test:

```text
Use $notebooklm with this notebook URL: <NOTEBOOK_URL>. Ask: "What are the main topics covered by this notebook? Include citations when available."
```

Expected result:

- Codex opens the provided notebook URL.
- Codex submits a self-contained question to NotebookLM.
- Codex waits for the answer to finish streaming.
- Codex reads the answer and citations.
- Codex returns a grounded summary to the user.

Pass condition:

- The final answer is based on NotebookLM output, not external model knowledge.
- Citations or source references are preserved when NotebookLM provides them.

### 4. Add Notebook to Library

Goal: validate the registration workflow.

Test:

```text
Use $notebooklm to add this notebook to my library: <NOTEBOOK_URL>
```

Expected result:

- Codex opens the notebook.
- Codex asks NotebookLM what the notebook contains.
- Codex uses the answer to create a library entry.
- Codex updates `data/library.json`.
- Codex does not invent topics or descriptions not supported by NotebookLM or user input.

Pass condition:

- `library.json` contains one notebook with:
  - `id`
  - `name`
  - `url`
  - `description`
  - `topics`
  - `use_cases`
- The JSON remains valid.

### 5. Topic-Based Selection

Goal: validate lookup from `library.json`.

Test:

```text
Use $notebooklm to answer a question from my <TOPIC> notebook: <QUESTION>
```

Expected result:

- Codex matches `<TOPIC>` against notebook `topics`, `description`, and `name`.
- Codex selects the correct notebook.
- If multiple notebooks match, Codex asks a clarification question.

Pass condition:

- Correct notebook selected from library metadata.
- Ambiguous matches are not guessed.

### 6. Active Notebook Fallback

Goal: validate the default notebook path.

Setup:

- Set `active_notebook_id` in `data/library.json`.

Test:

```text
Use $notebooklm to answer: <QUESTION>
```

Expected result:

- Codex uses the active notebook when the user does not provide a URL or topic.

Pass condition:

- The active notebook is used correctly.
- If the active ID is missing or invalid, Codex reports the configuration problem.

### 7. Failure Modes

Validate these cases deliberately:

- Browser bridge disconnected.
- Google login required.
- Notebook URL invalid or inaccessible.
- NotebookLM returns an empty or weak answer.
- NotebookLM says the sources do not contain the answer.
- Rate limit or quota warning appears.

Pass condition:

- Codex reports the failure clearly.
- Codex does not fabricate NotebookLM content.
- Codex suggests the next concrete recovery step.

## Recommended Next Steps

1. Confirm the actual Codex browser/plugin command syntax.
2. Update `SKILL.md` if `@Chrome open` is not the correct command.
3. Add `agents/openai.yaml` for UI metadata and a default prompt.
4. Run the skill discovery test.
5. Run the browser bridge availability test.
6. Run one direct URL query against a real NotebookLM notebook.
7. Register that notebook in `library.json`.
8. Test topic-based selection.
9. Test active notebook fallback.
10. Test the listed failure modes.
11. Refine `SKILL.md` based on actual NotebookLM UI behavior.
12. Decide whether to add helper scripts for library maintenance.

## Suggested `agents/openai.yaml`

Create:

```text
.agents/skills/notebooklm/agents/openai.yaml
```

Suggested content:

```yaml
interface:
  display_name: "NotebookLM"
  short_description: "Query NotebookLM notebooks from Codex"
  default_prompt: "Use $notebooklm to query one of my NotebookLM notebooks with source-grounded citations."

policy:
  allow_implicit_invocation: true
```

## Cleanup Before Broader Testing

The working tree contains macOS AppleDouble files named `._*`. They are ignored by `.gitignore`, but local Git commands currently emit warnings from AppleDouble files inside `.git/objects/pack`.

Before relying on Git history or packaging the repo, clean local AppleDouble files carefully. Do not delete normal Git pack files.

Suggested local cleanup command:

```bash
find . -name '._*' -type f -delete
```

Then re-run:

```bash
git status --short
python /Users/erosales/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/notebooklm
python -m json.tool .agents/skills/notebooklm/data/library.json
```

## Minimum Definition of Ready for Real Use

The skill is ready for practical use when all of these are true:

- Codex discovers `$notebooklm`.
- Codex can control the browser bridge.
- NotebookLM opens authenticated.
- A direct URL query returns grounded content.
- Notebook registration updates `library.json` correctly.
- Topic selection works from library metadata.
- Active notebook fallback works.
- Failure modes produce clear, non-fabricated responses.
- `SKILL.md` reflects the real browser command syntax and current NotebookLM UI behavior.
