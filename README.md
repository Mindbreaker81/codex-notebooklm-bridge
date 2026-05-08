# Codex NotebookLM Bridge Skill

Version: `0.4.0`

Skill local para consultar Google NotebookLM desde Codex usando la sesion
autenticada de Chrome del usuario. El objetivo es obtener respuestas grounded en
los documentos subidos a NotebookLM y preservar las citas que devuelve la
interfaz.

## Que puede hacer

- Abrir notebooks de NotebookLM por URL.
- Consultar notebooks autenticados desde Chrome.
- Enviar preguntas al chat de NotebookLM.
- Esperar a que NotebookLM termine de generar la respuesta.
- Extraer titulo, URL, fuentes, respuesta y citas numeradas.
- Registrar notebooks en `.agents/skills/notebooklm/data/library.json`.
- Seleccionar notebooks por tema o por notebook activo.
- Iniciar registro o reparacion cuando la biblioteca esta vacia, no hay match
  por tema o el notebook activo es invalido.
- Elegir DOM o accesibilidad segun el tipo de extraccion necesaria.
- Diagnosticar si se uso Chrome plugin o Computer Use fallback.

## Que no hace

- No gestiona login, cookies, local storage ni perfiles de Chrome.
- No consulta NotebookLM por API; opera la UI de NotebookLM.
- No inventa metadata de notebooks.
- No completa respuestas con conocimiento externo cuando el usuario pidio
  grounding en NotebookLM.
- No convierte Computer Use fallback en validacion del plugin Chrome.

## Requisitos

- Codex Desktop.
- Google Chrome instalado.
- Sesion de Google iniciada en Chrome con acceso a NotebookLM.
- Plugin Chrome de Codex instalado y conectado, recomendado.
- Extension Codex Chrome habilitada en el perfil correcto de Chrome.
- Al menos un notebook de NotebookLM con fuentes subidas.

Computer Use puede servir como fallback si el plugin Chrome no esta disponible,
pero ese fallback no cuenta como validacion del plugin Chrome.

## Instalacion

Hay dos formas practicas de usar esta skill.

### Opcion A: clonar el repo y abrirlo como workspace

Esta es la forma mas simple para probar o desarrollar la skill.

```bash
git clone https://github.com/Mindbreaker81/codex-notebooklm-bridge.git
cd codex-notebooklm-bridge
```

Despues abre ese directorio como workspace en Codex. Codex puede descubrir la
skill local en:

```text
.agents/skills/notebooklm
```

### Opcion B: clonar el repo e instalar la skill globalmente

Esta es la forma recomendada si quieres usar `$notebooklm` desde cualquier
workspace de Codex.

```bash
git clone https://github.com/Mindbreaker81/codex-notebooklm-bridge.git
cd codex-notebooklm-bridge
mkdir -p ~/.codex/skills
ln -s "$(pwd)/.agents/skills/notebooklm" ~/.codex/skills/notebooklm
```

Reinicia Codex para que cargue la skill.

Si prefieres copiar en vez de enlazar:

```bash
mkdir -p ~/.codex/skills
cp -R .agents/skills/notebooklm ~/.codex/skills/notebooklm
```

El symlink es mejor durante desarrollo porque los cambios del repo se reflejan
en la instalacion global tras reiniciar Codex.

### Opcion C: instalar desde Codex con GitHub/path

Si Codex tiene disponible el instalador de skills, puedes pedirle:

```text
Install the notebooklm skill from GitHub repo Mindbreaker81/codex-notebooklm-bridge path .agents/skills/notebooklm
```

Usa esta opcion solo si tu runtime de Codex expone el instalador de skills. Si
no, usa la opcion A o B.

### Comprobacion post-instalacion

En un thread nuevo de Codex:

```text
Use $notebooklm to list my notebooks.
```

Resultado esperado con la biblioteca vacia:

```text
No notebooks registered.
```

Ese mensaje no debe ser el final del flujo. Codex debe continuar de forma
proactiva: si ya tiene una URL de NotebookLM, debe registrar ese notebook; si no
la tiene y puede controlar Chrome, debe abrir `https://notebooklm.google.com`
para que el usuario elija un notebook; si no puede controlar el navegador, debe
pedir una URL de NotebookLM.

## Estructura

```text
.agents/skills/notebooklm/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── data/
│   └── library.json
├── scripts/
│   └── library.py
└── references/
    └── usage_patterns.md
```

Archivos principales:

- `SKILL.md`: instrucciones que carga Codex cuando se activa la skill.
- `agents/openai.yaml`: metadata UI para la skill.
- `data/library.json`: biblioteca local de notebooks.
- `scripts/library.py`: mantenimiento determinista de la biblioteca.
- `references/usage_patterns.md`: ejemplos de uso y patrones de consulta.

## Chrome plugin vs Computer Use fallback

Ruta principal:

```text
Control path used: Chrome plugin
```

Usa el plugin Chrome de Codex mediante `@chrome` o el backend `browser-client`.
En algunos runtimes no aparece una herramienta visible llamada
`mcp__chrome__...`; sigue contando como plugin Chrome si Codex comunica con la
extension, lista/reclama tabs y opera Chrome desde ese backend.

Fallback:

```text
Control path used: Computer Use fallback
```

Usa Computer Use cuando el plugin Chrome no esta disponible o falla. Este flujo
esta validado contra el notebook de prueba, pero no valida el plugin Chrome.

Sin control disponible:

```text
No browser control available
```

En ese caso la skill no puede operar NotebookLM desde este runtime.

## DOM vs accesibilidad

La skill usa UI/accesibilidad para navegar, hacer clicks, confirmar carga,
detectar login/errores visibles y comprobar estados de NotebookLM.

Usa DOM/Playwright cuando necesita datos exactos o estructurados: URLs
completas, atributos `href`, titulos completos, listas largas de notebooks,
fuentes visibles, texto final de respuestas y citas. Si la accesibilidad
muestra texto truncado o una lista ambigua, Codex debe intentar DOM antes de
copiar a mano, pedir el mismo dato al usuario o escribir `library.json`.

Si DOM no expone el dato de forma fiable, la skill vuelve a UI/accesibilidad o
screenshot y pide una confirmacion corta cuando el valor afecte metadata
guardada. DOM no autoriza inventar metadata: solo captura lo que NotebookLM o
el usuario respaldan.

## Uso basico

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

Codex debe abrir el notebook, preguntarle a NotebookLM de que trata y guardar
metadata grounded en `data/library.json`. No debe inventar topics ni
descripciones si NotebookLM no los respalda. Para registrar debe preferir DOM
cuando este disponible para capturar URL canonica, titulo completo y fuentes
visibles antes de guardar.

### Consultar por tema

```text
Usa $notebooklm para responder desde mi notebook de compliance:
Que controles SOC2 aparecen y que evidencias piden?
```

Codex compara el tema contra `topics`, `description` y `name` en
`data/library.json`. Si hay una coincidencia, la usa; si hay varias, pregunta
cual usar; si no hay coincidencias, lista candidatos existentes o inicia el
flujo de registro cuando la biblioteca esta vacia.

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
Usa $notebooklm para responder: Cuales son los hallazgos principales?
```

## Mantenimiento de la biblioteca

Validar:

```bash
python .agents/skills/notebooklm/scripts/library.py validate
```

Listar:

```bash
python .agents/skills/notebooklm/scripts/library.py list
python .agents/skills/notebooklm/scripts/library.py list --json
```

Agregar:

```bash
python .agents/skills/notebooklm/scripts/library.py add \
  --id example-research-notebook \
  --name "Example Research Notebook" \
  --url "https://notebooklm.google.com/notebook/<id>" \
  --description "Research notebook about the example topic." \
  --topic example-topic \
  --topic research-notes \
  --use-case "answer questions about the example research notes"
```

Actualizar:

```bash
python .agents/skills/notebooklm/scripts/library.py update example-research-notebook \
  --description "Updated description." \
  --topic updated-topic
```

Marcar activo:

```bash
python .agents/skills/notebooklm/scripts/library.py set-active example-research-notebook
python .agents/skills/notebooklm/scripts/library.py set-active none
```

El script solo edita `library.json`. No abre Chrome ni consulta NotebookLM.

## Casos de uso

- Resumir papers o reportes subidos a NotebookLM.
- Extraer citas verificables de documentos privados.
- Consultar notas de compliance, onboarding, producto o investigacion.
- Comparar respuestas entre varios notebooks registrados.
- Crear una biblioteca local de notebooks consultables por tema.
- Diagnosticar si Codex esta usando plugin Chrome o fallback Computer Use.

## Formato esperado de respuesta

Cuando NotebookLM devuelve citas, la skill debe preservar senales como:

```text
Notebook: Example Research Notebook
Sources cited: example-source.pdf

Answer:
- The notebook describes the main research context. [1, 2]
- It compares the example method against baseline approaches. [3, 4]

Control path used: Chrome plugin
```

Si se usa Computer Use:

```text
Control path used: Computer Use fallback
```

No se debe presentar el fallback como validacion del plugin Chrome.

## Validacion

Validar la skill:

```bash
python <path-to-skill-creator>/scripts/quick_validate.py .agents/skills/notebooklm
```

Validar la biblioteca:

```bash
python .agents/skills/notebooklm/scripts/library.py validate
python -m json.tool .agents/skills/notebooklm/data/library.json
```

Ejecutar tests del script:

```bash
python -m pytest tests/test_library_script.py
```

Validar whitespace antes de commit:

```bash
git diff --check
```

## Estado validado

Validado con un notebook de prueba privado. Este repositorio no publica IDs de
notebooks reales; para revalidar, usa un notebook propio:

```text
https://notebooklm.google.com/notebook/<id>
```

Resultado validado:

- Notebook cargado autenticado en Chrome.
- Titulo extraido desde la interfaz de NotebookLM.
- Fuente visible o citada por NotebookLM.
- Preguntas enviadas desde Codex.
- Respuestas y citas extraidas desde NotebookLM.
- Ruta plugin Chrome validada mediante Chrome skill + `browser-client`.
- Ruta Computer Use validada como fallback separado.

Detalles reproducibles:

- `docs/validated-flows.md`
- `docs/pressure-tests.md`

## Limitaciones

- NotebookLM no ofrece una API publica estable para este flujo; se opera la UI.
- Cambios en la interfaz de NotebookLM pueden requerir ajustar la skill.
- Chats largos pueden hacer lentos los snapshots DOM completos; la skill prefiere
  extraccion acotada o pestanas frescas.
- DOM puede no exponer todos los datos utiles; en ese caso se usa
  UI/accesibilidad y confirmacion del usuario para valores que se guardaran.
- La calidad depende de las fuentes subidas al notebook.
- Si NotebookLM no contiene una respuesta tras 1-2 follow-ups concretos, Codex
  debe reportarlo en vez de completar con conocimiento externo.

## Desarrollo

Antes de publicar cambios:

```bash
python <path-to-skill-creator>/scripts/quick_validate.py .agents/skills/notebooklm
python .agents/skills/notebooklm/scripts/library.py validate
python -m json.tool .agents/skills/notebooklm/data/library.json
python -m pytest tests/test_library_script.py
git diff --check
```
