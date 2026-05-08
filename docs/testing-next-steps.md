# NotebookLM Codex Skill: Testing and Next Steps

## Current State

The repository contains a valid Codex skill at:

```text
.agents/skills/notebooklm/SKILL.md
```

Basic validation passes with:

```bash
python <path-to-skill-creator>/scripts/quick_validate.py .agents/skills/notebooklm
```

The local notebook library exists and is valid JSON:

```text
.agents/skills/notebooklm/data/library.json
```

Current limitation: the library is empty, so testing should begin with a
NotebookLM URL or by opening NotebookLM home and having the user choose a
notebook to register.

Use the maintenance script for deterministic library checks:

```bash
python .agents/skills/notebooklm/scripts/library.py validate
python .agents/skills/notebooklm/scripts/library.py list
```

## Updated Control Assumption

There are now two Chrome control paths:

1. **Codex Chrome plugin:** preferred when the runtime exposes `@Chrome` or
   when the user explicitly invokes the Chrome plugin mention.
2. **Computer-use fallback:** use Chrome accessibility/computer-use controls
   when the Chrome plugin path is not exposed or fails its connection checks.

The official Codex Chrome extension docs
(`https://developers.openai.com/codex/app/chrome-extension`) show direct
prompts such as:

```text
@Chrome open https://notebooklm.google.com
```

The extension itself has been verified locally: Chrome's Codex extension popup
shows `Connected`, version `v1.1.4`.

The direct Chrome plugin path is now validated in a thread where the user
explicitly invoked:

```text
[@chrome](plugin://chrome@openai-bundled) open https://notebooklm.google.com
```

Important nuance: the working Chrome path did not appear as a separate
`mcp__chrome__...` tool. It appeared as the Chrome plugin skill plus the
extension `browser-client` backend executed through the Node REPL. That still
counts as native Chrome plugin validation because Codex communicated with the
Codex Chrome Extension, listed open Chrome tabs, claimed/opened NotebookLM
tabs, submitted questions, and extracted NotebookLM answers from the Chrome
session.

Computer Use remains a valid fallback, but fallback success must be reported as
fallback success. It must not be counted as validation of the Chrome plugin.

Validated control-path details are recorded in:

```text
docs/validated-flows.md
```

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
- Codex does not stop there:
  - if the prompt includes a NotebookLM URL, Codex starts registration;
  - if browser control is available, Codex opens `https://notebooklm.google.com`
    and asks the user to choose or open a notebook;
  - otherwise, Codex asks for a NotebookLM URL.

Pass condition:

- The skill triggers without manually pasting the skill instructions.
- `No notebooks registered.` is not treated as the final answer unless the user
  explicitly requested raw CLI output.

### 2. Chrome Plugin Availability

Goal: confirm the Codex Chrome plugin is installed and connected.

Test:

```text
Open Chrome's extensions menu and inspect the Codex extension.
```

Expected result:

- Codex extension appears under Chrome extensions.
- Extension has access to the current site when appropriate.
- Popup shows `Connected`.

Pass condition:

- Codex extension popup shows `Connected`.

Current result:

- Passed locally with Codex Chrome extension `v1.1.4`.

### 3. Direct `@Chrome` Invocation

Goal: confirm Codex can invoke the plugin as a first-class browser tool.

Test from a fresh Codex thread:

```text
@Chrome open https://notebooklm.google.com
```

Expected result:

- Codex routes the request to the Chrome plugin.
- NotebookLM opens in Chrome.
- Codex asks for website approval if needed.
- Codex can continue interacting with the page.
- The implementation may use the Chrome skill's `browser-client` backend
  through Node REPL rather than a separate visible Chrome MCP namespace.

Pass condition:

- The task uses the Chrome plugin/browser-client path, not Computer Use.

Current result:

- Passed. Codex opened NotebookLM through the Chrome plugin path and kept the
  NotebookLM tab open.

### 4. Computer-Use Fallback Availability

Goal: confirm Codex can open NotebookLM in Chrome and inspect the page.

Test:

```text
Use $notebooklm to open https://notebooklm.google.com
```

Expected result:

- Codex opens NotebookLM through Chrome control.
- The browser uses the user's existing Google login.
- If login is required, Codex reports that the user must sign in.

Pass condition:

- NotebookLM loads in an authenticated Chrome session controlled or inspected by Codex.
- The result is labeled as fallback validation, not Chrome plugin validation.

Current result:

- Passed manually against the Example Research Notebook notebook.
- Revalidation steps are documented in `docs/validated-flows.md`.

Blocking failure:

- Codex has no callable browser/computer-use control.
- The browser opens but Codex cannot inspect or interact with the page.

### 5. Direct URL Query

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
- The report states whether the Chrome plugin path or Computer Use fallback was
  used.

Current result:

- Passed through the Chrome plugin/browser-client path against:

  ```text
  https://notebooklm.google.com/notebook/<id>
  ```

- Notebook title extracted:

  ```text
  Example Research Notebook
  ```

- Source cited:

  ```text
  example-source.pdf
  ```

- The test submitted multiple questions, waited for NotebookLM's ready state,
  and extracted numbered citations from the NotebookLM answer.

### 6. Add Notebook to Library

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
- `python .agents/skills/notebooklm/scripts/library.py validate` passes.

### 7. Topic-Based Selection

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

### 8. Active Notebook Fallback

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
- If the active ID is missing or invalid, Codex repairs selection before
  querying: use the only notebook, ask which notebook should be active, or start
  registration when the library is empty.

### 9. Failure Modes

Validate these cases deliberately:

- Chrome plugin unavailable in the current thread.
- Chrome extension disconnected.
- Browser/computer-use control unavailable.
- Google login required.
- Notebook URL invalid or inaccessible.
- NotebookLM returns an empty or weak answer.
- NotebookLM says the sources do not contain the answer.
- Rate limit or quota warning appears.

Pass condition:

- Codex reports the failure clearly.
- Codex does not fabricate NotebookLM content.
- Codex suggests the next concrete recovery step.
- For empty or weak answers, Codex asks 1-2 targeted follow-ups before reporting
  insufficient source coverage, unless NotebookLM clearly says the sources do
  not contain the answer.

## Recommended Next Steps

1. Run the skill discovery test.
2. Run the Chrome plugin availability test.
3. Re-run the manual Computer Use fallback scenario in `docs/validated-flows.md`
   after NotebookLM UI or Codex browser tooling changes.
4. Register a real notebook in `library.json`.
5. Test topic-based selection.
6. Test active notebook fallback.
7. Run the listed failure modes and `docs/pressure-tests.md`.
8. Refine `SKILL.md` based on actual NotebookLM UI behavior.

## `agents/openai.yaml`

Created:

```text
.agents/skills/notebooklm/agents/openai.yaml
```

Current content:

```yaml
interface:
  display_name: "NotebookLM"
  short_description: "Query NotebookLM notebooks from Codex"
  default_prompt: "Use $notebooklm to query one of my NotebookLM notebooks with source-grounded citations."

policy:
  allow_implicit_invocation: true
```

## Cleanup Before Broader Testing

The working tree may contain macOS AppleDouble files named `._*`. They are
ignored by `.gitignore`, but on external/macOS volumes they can reappear inside
`.git` or cache directories.

Best-effort cleanup:

```bash
find . -name '._*' -type f -delete
```

Verification:

```bash
find . -name '._*' -type f -print | wc -l
```

If the count is non-zero but `git status --short` does not show these files,
they are ignored local metadata and not part of the skill package.

## Minimum Definition of Ready for Real Use

The skill is ready for practical use when all of these are true:

- Codex discovers `$notebooklm`.
- Codex can use the Chrome plugin path, or can control/inspect Chrome through browser/computer-use tooling.
- NotebookLM opens authenticated.
- A direct URL query returns grounded content.
- Notebook registration updates `library.json` correctly.
- Topic selection works from library metadata.
- Active notebook fallback works.
- Failure modes produce clear, non-fabricated responses.
- `SKILL.md` reflects the validated Chrome control path and current NotebookLM UI behavior.
- `scripts/library.py validate` passes.
