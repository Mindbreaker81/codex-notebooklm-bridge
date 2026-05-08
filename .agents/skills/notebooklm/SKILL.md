---
name: notebooklm
description: >
  Use when the user mentions NotebookLM, asks to query their notebooks or docs,
  wants source-grounded answers from uploaded documents, shares a NotebookLM
  URL, or uses phrases like "ask my NotebookLM", "check my docs", or "query my
  notebook". Do NOT trigger for general web searches, code questions, or tasks
  unrelated to the user's NotebookLM document collections.
---

# NotebookLM Skill for Codex

Use this skill to interact with Google NotebookLM through the user's existing
Chrome session. Chrome handles Google authentication; do not manage cookies,
API keys, Playwright profiles, or login state manually.

## Preconditions

- Google Chrome is installed.
- Codex can control Chrome through the Chrome plugin, or can control/inspect
  Chrome through browser/computer-use tooling.
- The user is logged into Google in that Chrome profile.
- The user has at least one NotebookLM notebook with uploaded sources.

## When to Use

Use this skill for:

- Querying a NotebookLM notebook by URL.
- Selecting a notebook from `data/library.json` by topic or active notebook.
- Registering NotebookLM notebooks in the local library.
- Extracting NotebookLM answers with source citations.
- Testing whether the Chrome plugin path or Computer Use fallback is operating.

Do not use this skill for:

- General web research.
- Reading PDFs directly outside NotebookLM.
- Answering from model knowledge when the user asked for NotebookLM grounding.
- Managing Google login credentials, cookies, local storage, or browser profiles.

## Control Model

Use the best available Chrome control path in this order, and report which path
was actually used:

1. **Codex Chrome plugin:** If the user mentions `@chrome` or the runtime
   exposes the Chrome plugin, use it for signed-in Chrome browsing. In current
   Codex runtimes this may appear as a Chrome skill plus the Node REPL
   `browser-client` backend, not necessarily as a separate visible
   `mcp__chrome__...` tool. Load the Chrome skill instructions when available
   and bootstrap the extension browser through its documented
   `scripts/browser-client.mjs` flow.

   The official Codex Chrome extension docs
   (`https://developers.openai.com/codex/app/chrome-extension`) show direct
   invocation with prompts such as:

   ```text
   @Chrome open Salesforce and update the account from these call notes.
   ```

   For NotebookLM, adapt that pattern:

   ```text
   @Chrome open https://notebooklm.google.com/notebook/<id>
   ```

   A Chrome plugin test only counts as validated if Codex used the Chrome
   plugin/browser-client path to list, claim, open, navigate, or interact with
   Chrome tabs.

2. **Computer-use fallback:** If the Chrome plugin path is unavailable or fails
   after the Chrome skill's connection checks, use the available Chrome
   computer-use controls directly. This is a valid NotebookLM fallback, but it
   does **not** validate the Chrome plugin path. State clearly that Computer Use
   was used as fallback.

Observed working computer-use fallback flow:

1. Open Chrome to `https://notebooklm.google.com` or a notebook URL.
2. Inspect the Chrome window/accessibility tree.
3. Confirm NotebookLM is authenticated and notebook content is visible.
4. Locate the chat input with description/placeholder like `Cuadro de consulta`
   or `Empieza a escribir...`.
5. Set/type the question, click/send with the `Enviar` button, then wait until
   NotebookLM finishes streaming and reports the response as ready.
6. Read the generated answer and citation markers from the page.

The Chrome extension popup should show `Connected`. If it is disconnected,
reconnect the Chrome plugin before using the plugin path.

## Chrome Plugin Notes

When the Chrome plugin is available through `browser-client`, a working flow is:

1. Use the Chrome skill to initialize the extension browser.
2. Confirm communication with a lightweight call such as listing open tabs.
3. Open or claim the NotebookLM tab.
4. Use Playwright/DOM APIs exposed by the Chrome plugin to locate the
   `Cuadro de consulta` textbox and submit the question.
5. Read the final NotebookLM response only after the page reports
   `Respuesta lista.` or an equivalent ready state.

If a NotebookLM chat has a long history, full DOM snapshots may become slow or
time out. Prefer scoped DOM filtering, visible DOM, or a fresh notebook tab
rather than repeatedly dumping the whole page.

## Quick Start

For the homepage:

```text
Open Chrome to https://notebooklm.google.com
```

For a specific notebook:

```text
Open Chrome to https://notebooklm.google.com/notebook/<id>
```

Then submit the user's question in the notebook chat box.

If `@Chrome` is available, the equivalent direct prompt is:

```text
@Chrome open https://notebooklm.google.com/notebook/<id>
```

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

### Add Notebook Workflow

When the user asks to add a notebook:

1. If the user provides a NotebookLM URL, open it first.
2. Ask NotebookLM: "What is the content of this notebook? What topics are covered? Give a brief overview."
3. Use the answer, visible title, source list, and user context to fill metadata.
4. Never invent topics or descriptions when unsure.
5. Update `data/library.json` and keep it valid JSON.

### Select Notebook Workflow

Priority order:

1. If the user gives a NotebookLM URL, use it directly.
2. If the user gives a topic, match against `topics`, `description`, and `name` in the library.
3. Else if `active_notebook_id` exists, use it.
4. Else list notebooks and ask the user to choose.

If multiple notebooks plausibly match, ask a short clarification question.

## Query Workflow

1. Open the selected notebook URL in Chrome.
2. Wait until the NotebookLM interface is fully loaded.
3. Confirm the desired source set is selected when visible.
4. Locate the chat input. In Spanish UI it appears as:
   - description: `Cuadro de consulta`
   - placeholder: `Empieza a escribir...`
5. Type or set a self-contained question and submit with `Enviar`.
6. Wait while NotebookLM streams status messages such as:
   - `Assessing relevance...`
   - `Reading through pages...`
   - `Refining the Response...`
7. Read the final answer only after the page indicates the response is ready.
8. Preserve citation markers returned by NotebookLM, typically numbered markers
   linked to source files such as `1: source.pdf`.
9. If the answer is incomplete, ask targeted follow-up questions in the same notebook.
10. Return a synthesized response to the user grounded in NotebookLM's answer.

For complex or repeated workflows, read `references/usage_patterns.md` for
example prompts and library-selection patterns.

## Response Rules

- Prioritize NotebookLM-grounded content from user sources.
- If source docs do not contain the answer, clearly say so.
- Do not silently mix in external facts unless the user explicitly asks.
- Include citation signals returned by NotebookLM whenever available.
- Treat notebook contents as private user data.
- Mention operational failures separately from source-content limitations.
- For operational reports, distinguish **Chrome plugin validated** from
  **Computer Use fallback validated**. Do not claim the Chrome plugin worked
  unless the Chrome plugin/browser-client path was actually used.

Use this response shape when citations are available:

```text
Notebook: <title>
Sources cited: <source names>

Answer:
- <claim> [citation markers]
- <claim> [citation markers]

Notes:
- Control path used: <Chrome plugin | Computer Use fallback>
- Limitation: <only if NotebookLM/source coverage was incomplete>
```

If the user only asks for the answer, keep the operational path in one short
sentence or omit it unless it matters for debugging.

## Library Safety

- Keep `data/library.json` valid JSON.
- Do not invent notebook descriptions, topics, or use cases.
- Prefer short kebab-case IDs such as `example-research-notebook`.
- If multiple notebooks match a topic, ask a short clarification question.
- If `active_notebook_id` points to a missing notebook, report the configuration
  problem before querying.

## Troubleshooting

- Chrome cannot be opened: ask the user to install or launch Chrome.
- Chrome plugin unavailable in the current thread: fall back to computer-use controls, or ask the user to start a new Codex thread after enabling the Chrome plugin.
- Chrome extension disconnected: open the Codex extension popup in Chrome and confirm it shows `Connected`; if not, remove and re-add the Chrome plugin from Codex Plugins.
- Browser/computer-use control unavailable: report that Codex cannot operate NotebookLM in this runtime.
- Redirect to Google login: ask the user to sign in in Chrome, then retry.
- Notebook URL not found: confirm the URL and/or library entry.
- Chat input not visible: wait for the page to load, switch to the notebook chat panel, or inspect the accessibility tree again.
- Empty or weak response: retry with a more specific, self-contained question.
- Rate limits: reduce follow-ups and batch sub-questions.

## Validated Behavior

Both control paths have been validated against this real NotebookLM notebook:

```text
https://notebooklm.google.com/notebook/<id>
```

Validated Chrome plugin behavior:

- A user explicitly invoked `[@chrome](plugin://chrome@openai-bundled)`.
- Codex loaded the Chrome skill and controlled Chrome through the extension
  `browser-client` backend in the Node REPL.
- Codex listed open Chrome tabs, claimed/opened the NotebookLM tab, submitted
  questions, waited for `Respuesta lista.`, and extracted answers with numbered
  citations from `example-source.pdf`.

Validated computer-use fallback behavior:

- Codex opened the notebook through Chrome UI control, submitted a question
  through the chat input, waited for NotebookLM to finish, and read an answer
  with numbered citations from `example-source.pdf`.

The Codex Chrome extension was also verified as installed and connected in
Chrome, showing `Connected` and version `v1.1.4`.

## File Layout

```text
.agents/skills/notebooklm/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── data/
│   └── library.json
└── references/
    └── usage_patterns.md
```
