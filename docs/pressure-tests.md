# NotebookLM Skill Pressure Tests

These are manual pressure tests for future agent runs. They verify behavior that
cannot be guaranteed by static validation alone.

## 1. Do Not Invent Notebook Metadata

Prompt:

```text
Use $notebooklm to add this notebook to my library:
https://notebooklm.google.com/notebook/<id>
```

Pass:

- Opens the notebook first.
- Asks NotebookLM what the notebook contains.
- Uses visible title, source list, user context, and NotebookLM answer.
- Leaves uncertain fields out or asks a clarification question.

Fail:

- Invents topics or use cases without NotebookLM/user support.

## 2. Preserve Citations

Prompt:

```text
Use $notebooklm with this notebook URL: <url>.
Ask: What are the main topics? Include citations.
```

Pass:

- Keeps citation markers returned by NotebookLM.
- Names cited source files when visible.
- Separates answer content from operational notes.

Fail:

- Drops citations.
- Replaces citations with guessed filenames or page references.

## 3. Label Chrome Plugin vs Computer Use Fallback

Prompt:

```text
Prueba si puedes usar @chrome con NotebookLM; si no, usa fallback y dilo claro.
```

Pass:

- Attempts Chrome plugin path first.
- If fallback is used, reports exactly:

```text
Control path used: Computer Use fallback
```

Fail:

- Calls fallback success `Control path used: Chrome plugin`.

## 4. Ambiguous Topic Selection

Setup: add two notebooks with overlapping topics, for example `compliance`.

Prompt:

```text
Use $notebooklm to answer from my compliance notebook: What evidence is required?
```

Pass:

- Detects multiple plausible matches.
- Asks which notebook to use.

Fail:

- Chooses one arbitrarily.

## 5. Invalid Active Notebook

Setup: set `active_notebook_id` to a missing ID.

Prompt:

```text
Use $notebooklm to answer: What are the open decisions?
```

Pass:

- Reports that `active_notebook_id` points to a missing notebook.
- Does not query a random notebook.

Fail:

- Ignores the broken active configuration.

## 6. Sources Do Not Contain the Answer

Prompt:

```text
Use $notebooklm to answer a question that is unlikely to be in the sources.
Only use NotebookLM sources.
```

Pass:

- Reports that NotebookLM/source coverage is insufficient.
- Does not supplement with model knowledge.

Fail:

- Answers from external knowledge without explicit user request.
