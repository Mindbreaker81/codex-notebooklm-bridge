# Usage Patterns

## 1) Query by URL

User:

```text
Usa este notebook https://notebooklm.google.com/notebook/ABC y dime los riesgos principales.
Incluye citas.
```

Flow:

1. Open URL directly.
2. Ask a self-contained question in NotebookLM.
3. Return summarized answer with NotebookLM citations.

NotebookLM prompt:

```text
What are the main risks discussed in this notebook? Include citations for each
major risk and name the cited source files when available.
```

## 2) Query by topic

User:

```text
Busca en mis notas de compliance qué dice sobre SOC2.
```

Flow:

1. Match notebook by topic in `data/library.json`.
2. Open matched notebook.
3. Ask question with enough context.
4. Follow up if citations are thin.

If multiple notebooks match `compliance`, ask:

```text
Tengo varios notebooks de compliance. ¿Quieres consultar <A> o <B>?
```

## 3) Register notebook

User:

```text
Agrega este notebook a mi biblioteca: https://notebooklm.google.com/notebook/ABC
```

Flow:

1. Request or use NotebookLM URL.
2. Prefer DOM extraction for canonical URL, full title, and visible source list.
3. Ask notebook to summarize its own contents/topics.
4. Save metadata in library.
5. Optionally set as active notebook.

NotebookLM prompt:

```text
What is the content of this notebook? What topics are covered? Give a concise
overview suitable for catalog metadata.
```

Library entry shape:

```json
{
  "id": "short-kebab-id",
  "name": "Notebook Title",
  "url": "https://notebooklm.google.com/notebook/ABC",
  "description": "One-sentence grounded description.",
  "topics": ["topic-a", "topic-b"],
  "use_cases": ["when to query this notebook"]
}
```

## 4) Empty library listing

User:

```text
Use $notebooklm to list my notebooks.
```

Flow:

1. Run or inspect the local library list.
2. If no notebooks are registered, do not stop at `No notebooks registered.`
3. If the prompt includes a NotebookLM URL, open it and register that notebook.
4. Otherwise open `https://notebooklm.google.com` when browser control is
   available. Try scoped DOM extraction for visible notebook titles and links.
   If DOM does not expose a reliable list, ask the user to choose or open a
   notebook to register.
5. If browser control is unavailable, ask for a NotebookLM URL.

User with URL:

```text
Use $notebooklm to list my notebooks. If empty, add this one:
https://notebooklm.google.com/notebook/ABC
```

Flow:

1. Detect that the library is empty.
2. Open the URL, ask NotebookLM for grounded metadata, save the entry, then list
   the updated library.

## 5) Active notebook query

User:

```text
Usa mi notebook activo y resume las decisiones abiertas.
```

Flow:

1. Read `active_notebook_id`.
2. Resolve it to a notebook entry.
3. If valid, query the active notebook.
4. If missing or invalid, repair before querying:
   - one notebook exists: use it and offer to set it active;
   - multiple notebooks exist: list them and ask which should be active;
   - no notebooks exist: clear the invalid active value and start the empty
     library listing flow.

## 6) Topic with no matching notebook

User:

```text
Busca en mis notas de compliance qué dice sobre SOC2.
```

Flow when no notebook matches:

1. If the library has notebooks, list available candidates and ask whether to
   choose one or register a new compliance notebook.
2. If the library is empty, start the empty library listing flow.
3. Do not answer from model knowledge unless the user explicitly stops requiring
   NotebookLM grounding.

## 7) Weak NotebookLM response

User:

```text
Usa mi notebook activo y dime qué riesgos clínicos aparecen. Incluye citas.
```

Flow:

1. Ask the initial self-contained question.
2. If the response is empty, weak, or uncited, ask 1-2 targeted follow-ups, for
   example:

```text
Which source passages mention clinical risks? Cite the source numbers.
```

```text
If the sources do not discuss clinical risks, say that explicitly and cite the
closest relevant passages.
```

3. If NotebookLM still cannot support the answer, report insufficient source
   coverage instead of filling gaps externally.

## 8) Comparative synthesis

User:

```text
Compara lo que dicen mis notebooks de onboarding y compliance sobre acceso de
usuarios. Incluye citas por notebook.
```

Flow:

1. Match both notebooks from the library.
2. Query each notebook separately.
3. Keep citations grouped by notebook/source.
4. Synthesize only after both NotebookLM answers are collected.

Output shape:

```text
Onboarding notebook:
- ...

Compliance notebook:
- ...

Synthesis:
- ...
```

## 9) Chrome path diagnostic

User:

```text
Prueba si puedes usar @chrome con NotebookLM; si no, usa fallback y dilo claro.
```

Flow:

1. Try the Chrome plugin path first.
2. If unavailable or broken, use Computer Use fallback only after reporting the
   fallback switch.
3. In the final response, use the exact canonical label:
   - `Control path used: Chrome plugin`, or
   - `Control path used: Computer Use fallback`, or
   - `No browser control available`.

## 10) Long or truncated notebook list

User:

```text
Use $notebooklm to list my notebooks.
```

Flow:

1. If `data/library.json` is empty and NotebookLM home opens, inspect the UI.
2. If accessibility truncates titles or URLs, switch to scoped DOM extraction
   for notebook cards/anchors before writing or reporting entries.
3. If DOM exposes reliable titles and `href` values, show candidates and ask
   which notebook to register.
4. If DOM does not expose reliable notebook data, ask the user to open a
   notebook or provide its URL.

Fail:

- Copying truncated URLs or titles from accessibility into `library.json`.

## 11) Register with DOM-backed metadata

User:

```text
Use $notebooklm to add the notebook currently open in Chrome.
```

Flow:

1. Confirm the visible page is a NotebookLM notebook.
2. Use DOM/Playwright for the canonical URL, full title, and visible sources
   when available.
3. Ask NotebookLM for grounded overview/topics.
4. Save only metadata supported by DOM, NotebookLM's answer, visible UI, or user
   context.
5. If a value is uncertain, ask a short confirmation before saving.
