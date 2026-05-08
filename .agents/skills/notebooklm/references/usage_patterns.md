# Usage Patterns

## 1) Query by URL
User: "Usa este notebook https://notebooklm.google.com/notebook/ABC y dime los riesgos principales"

Flow:
1. Open URL directly.
2. Ask a self-contained question in NotebookLM.
3. Return summarized answer with NotebookLM citations.

## 2) Query by topic
User: "Busca en mis notas de compliance qué dice sobre SOC2"

Flow:
1. Match notebook by topic in `data/library.json`.
2. Open matched notebook.
3. Ask question with enough context.
4. Follow up if citations are thin.

## 3) Register notebook
User: "Agrega mi notebook de onboarding"

Flow:
1. Request or use NotebookLM URL.
2. Ask notebook to summarize its own contents/topics.
3. Save metadata in library.
4. Optionally set as active notebook.
