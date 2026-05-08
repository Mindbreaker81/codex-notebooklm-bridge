# Codex NotebookLM Bridge Skill

Skill local para consultar Google NotebookLM desde Codex usando la sesión
autenticada de Chrome del usuario. El objetivo es obtener respuestas grounded en
los documentos subidos a NotebookLM, preservando las citas que devuelve la
interfaz.

## Qué hace

- Abre notebooks de NotebookLM por URL.
- Pregunta dentro del chat de NotebookLM.
- Espera a que la respuesta termine de generarse.
- Extrae título, fuentes, respuesta y citas numeradas.
- Mantiene una biblioteca local opcional de notebooks en JSON.
- Usa el plugin Chrome de Codex como ruta principal y Computer Use como fallback.

## Requisitos

- Codex Desktop.
- Google Chrome instalado.
- Sesión de Google iniciada en Chrome con acceso a NotebookLM.
- Plugin Chrome de Codex instalado y conectado, recomendado.
- Extensión Codex Chrome habilitada en el perfil correcto de Chrome.
- Al menos un notebook de NotebookLM con fuentes subidas.

Computer Use puede servir como fallback si el plugin Chrome no está disponible,
pero ese fallback no cuenta como validación del plugin Chrome.

## Instalación

### Opción 1: usarla desde este repo

Abre este repo como workspace de Codex:

```text
/Volumes/EXTERNAL/proyectos/codex-notebooklm-bridge
```

La skill vive en:

```text
.agents/skills/notebooklm
```

En este modo, Codex puede descubrir la skill como skill local del workspace.

### Opción 2: instalarla globalmente en Codex

Copia o enlaza la skill al directorio global de skills:

```bash
mkdir -p ~/.codex/skills
ln -s <repo>/.agents/skills/notebooklm ~/.codex/skills/notebooklm
```

Después reinicia Codex para que cargue la nueva skill.

Si prefieres copiar en vez de enlazar:

```bash
mkdir -p ~/.codex/skills
cp -R <repo>/.agents/skills/notebooklm ~/.codex/skills/notebooklm
```

El enlace simbólico es mejor durante desarrollo porque los cambios del repo se
ven inmediatamente tras reiniciar Codex.

En esta máquina, `<repo>` es:

```text
/Volumes/EXTERNAL/proyectos/codex-notebooklm-bridge
```

## Estructura

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

Archivos principales:

- `SKILL.md`: instrucciones que carga Codex cuando se activa la skill.
- `agents/openai.yaml`: metadata UI para la skill.
- `data/library.json`: biblioteca local de notebooks.
- `references/usage_patterns.md`: ejemplos de uso y patrones de consulta.

## Configuración de Chrome

Ruta preferida:

1. Instala y habilita el plugin Chrome en Codex.
2. Verifica que la extensión Codex Chrome aparece como conectada.
3. Usa una mención explícita cuando quieras probar el plugin:

```text
[@chrome](plugin://chrome@openai-bundled) open https://notebooklm.google.com
```

En runtimes actuales, la ruta Chrome puede aparecer como skill Chrome más backend
`browser-client` ejecutado desde Node REPL, no necesariamente como una
herramienta visible llamada `mcp__chrome__...`. Eso sigue contando como plugin
Chrome si Codex se comunica con la extensión, lista/reclama pestañas y opera
Chrome desde esa ruta.

## Uso básico

### Consultar un notebook por URL

```text
Usa $notebooklm con este notebook:
https://notebooklm.google.com/notebook/<id>

Pregunta:
What are the main topics covered by this notebook? Include citations when available.
```

### Registrar un notebook

```text
Usa $notebooklm para agregar este notebook a mi biblioteca:
https://notebooklm.google.com/notebook/<id>
```

Codex debe abrir el notebook, preguntarle a NotebookLM de qué trata y guardar
metadata grounded en `data/library.json`. No debe inventar topics ni
descripciones si NotebookLM no los respalda.

### Consultar por tema

```text
Usa $notebooklm para responder desde mi notebook de compliance:
¿Qué controles SOC2 aparecen y qué evidencias piden?
```

Codex compara el tema contra `topics`, `description` y `name` en
`data/library.json`. Si hay varias coincidencias plausibles, debe preguntar cuál
usar.

### Usar notebook activo

Configura `active_notebook_id` en `data/library.json`:

```json
{
  "notebooks": [
    {
      "id": "example-research-notebook",
      "name": "Example Research Notebook",
      "url": "https://notebooklm.google.com/notebook/<id>",
      "description": "Research notebook about the example topic.",
      "topics": ["example-topic", "research-notes"],
      "use_cases": ["answer questions about the example research notes"]
    }
  ],
  "active_notebook_id": "example-research-notebook"
}
```

Luego:

```text
Usa $notebooklm para responder: ¿Cuáles son los hallazgos principales?
```

## Casos de uso

- Resumir papers o reportes subidos a NotebookLM.
- Extraer citas verificables de documentos privados.
- Consultar notas de compliance, onboarding, producto o investigación.
- Comparar respuestas entre varios notebooks registrados.
- Crear una biblioteca local de notebooks consultables por tema.
- Diagnosticar si Codex está usando plugin Chrome o fallback Computer Use.

## Formato esperado de respuesta

Cuando NotebookLM devuelve citas, la skill debe preservar señales como:

```text
Notebook: Example Research Notebook
Sources cited: example-source.pdf

Answer:
- Example Research Notebook was deployed through Fitbit for everyday symptom assessment. [1, 2]
- The study compared Example Research Notebook's differential diagnoses against clinicians. [3, 4]

Control path used: Chrome plugin
```

Si se usa Computer Use, debe decirlo:

```text
Control path used: Computer Use fallback
```

No se debe presentar el fallback como validación del plugin Chrome.

## Validación

Validar la skill:

```bash
python /Users/erosales/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/notebooklm
```

Validar la biblioteca JSON:

```bash
python -m json.tool .agents/skills/notebooklm/data/library.json
```

Validar que no hay problemas de whitespace antes de commit:

```bash
git diff --check
```

## Estado validado

Probado con:

```text
https://notebooklm.google.com/notebook/<id>
```

Resultado validado:

- Notebook cargado autenticado en Chrome.
- Título extraído: `Example Research Notebook`.
- Fuente citada: `example-source.pdf`.
- Preguntas enviadas desde Codex.
- Respuestas y citas extraídas desde NotebookLM.
- Ruta plugin Chrome validada mediante Chrome skill + `browser-client`.
- Ruta Computer Use validada como fallback separado.

## Limitaciones

- NotebookLM no ofrece una API pública estable para este flujo; se opera la UI.
- Cambios en la interfaz de NotebookLM pueden requerir ajustar la skill.
- Chats largos pueden hacer lentos los snapshots DOM completos; la skill prefiere
  extracción acotada o pestañas frescas.
- La calidad depende de las fuentes subidas al notebook.
- Si NotebookLM no contiene una respuesta, Codex debe reportarlo en vez de
  completar con conocimiento externo.

## Mejoras recomendadas

- Scripts de mantenimiento para `data/library.json`:
  - listar notebooks
  - validar esquema
  - marcar notebook activo
  - normalizar IDs
- Tests de presión para comprobar que otros agentes:
  - no inventan metadata
  - no confunden fallback con plugin Chrome validado
  - preservan citas
- Ejemplos adicionales para consultas multi-notebook.
- Plantillas de prompts para papers, compliance, producto y meeting notes.
- Registro opcional de resultados de test en `docs/`.

## Desarrollo

Repositorio:

```text
/Volumes/EXTERNAL/proyectos/codex-notebooklm-bridge
```

Rama de trabajo actual:

```text
codex/update-notebooklm-skill-docs
```

Antes de publicar cambios:

```bash
python /Users/erosales/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/notebooklm
python -m json.tool .agents/skills/notebooklm/data/library.json
git diff --check
```
