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
2. Ask notebook to summarize its own contents/topics.
3. Save metadata in library.
4. Optionally set as active notebook.

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

## 4) Active notebook query

User:

```text
Usa mi notebook activo y resume las decisiones abiertas.
```

Flow:

1. Read `active_notebook_id`.
2. Resolve it to a notebook entry.
3. If missing or invalid, report the configuration problem.
4. Query the active notebook.

## 5) Comparative synthesis

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

## 6) Chrome path diagnostic

User:

```text
Prueba si puedes usar @chrome con NotebookLM; si no, usa fallback y dilo claro.
```

Flow:

1. Try the Chrome plugin path first.
2. If unavailable or broken, use Computer Use fallback only after reporting the
   fallback switch.
3. In the final response, state:
   - `Chrome plugin validated`, or
   - `Computer Use fallback validated`, or
   - `No browser control available`.
