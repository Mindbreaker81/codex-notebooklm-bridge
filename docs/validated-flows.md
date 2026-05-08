# Validated NotebookLM Flows

This document records manual validation evidence for the NotebookLM skill. It is
not a substitute for live testing; it is the baseline that future changes should
preserve.

## Test Notebook

```text
https://notebooklm.google.com/notebook/<id>
```

- Notebook title: `Example Research Notebook`
- Visible source: `example-source.pdf`
- Test question: `What are the main topics covered by this notebook? Include citations when available.`

## Chrome Plugin Flow

Status: validated.

Control path label:

```text
Control path used: Chrome plugin
```

Observed flow:

1. User explicitly invoked the Chrome plugin with `[@chrome](plugin://chrome@openai-bundled)`.
2. Codex loaded the Chrome skill and connected through the extension
   `browser-client` backend.
3. Codex listed open Chrome tabs.
4. Codex opened or claimed the NotebookLM tab.
5. Codex submitted questions through NotebookLM chat.
6. Codex waited for the ready state, observed as `Respuesta lista.`
7. Codex extracted responses and numbered citations from `example-source.pdf`.

Important nuance: this may not appear as a visible `mcp__chrome__...` namespace.
It still counts as Chrome plugin validation if the browser is controlled through
the Codex Chrome extension backend.

## Computer Use Fallback Flow

Status: validated.

Control path label:

```text
Control path used: Computer Use fallback
```

Observed flow:

1. Chrome opened NotebookLM in the user's authenticated Google session.
2. Codex inspected the visible Chrome/NotebookLM UI.
3. Codex confirmed notebook content and source list were visible.
4. Codex located the chat input using Spanish UI labels:
   - `Cuadro de consulta`
   - `Empieza a escribir...`
5. Codex typed the test question and clicked `Enviar`.
6. Codex waited until NotebookLM finished streaming.
7. Codex read the answer and numbered citations from `example-source.pdf`.

Computer Use fallback success does not validate the Chrome plugin path. Reports
must keep those labels separate.

## Manual Revalidation Scenario

Use this when the NotebookLM UI changes or a runtime changes browser tooling:

```text
Use $notebooklm with this notebook URL:
https://notebooklm.google.com/notebook/<id>

Ask:
What are the main topics covered by this notebook? Include citations when available.
```

Pass criteria:

- Notebook opens authenticated.
- Notebook title is visible or extractable.
- `example-source.pdf` is visible or cited.
- The question is submitted to NotebookLM.
- The answer is read only after generation completes.
- Citation markers are preserved.
- The final report states one exact control path label.

Failure criteria:

- Codex silently uses Computer Use while claiming Chrome plugin validation.
- Codex invents citations or source names.
- Codex supplements NotebookLM with external model knowledge without user
  request.
- Codex reads an incomplete streaming answer as final.
