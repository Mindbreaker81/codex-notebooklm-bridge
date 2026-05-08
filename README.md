# Codex NotebookLM Bridge Skill

Repositorio inicial para una skill de Codex que conecta con Google NotebookLM
mediante una sesión autenticada de Chrome controlada por el plugin de Chrome de
Codex cuando está disponible, o por Computer Use como fallback, con enfoque RAG
sobre fuentes del usuario.

## Qué incluye este repo

- Skill lista para instalar en `.agents/skills/notebooklm/SKILL.md`.
- Biblioteca local de notebooks en `.agents/skills/notebooklm/data/library.json`.
- Guía de patrones de uso en `.agents/skills/notebooklm/references/usage_patterns.md`.

## Objetivo

Permitir que Codex consulte notebooks de NotebookLM del usuario y responda con
contenido grounded en sus documentos, reutilizando citas y minimizando
alucinaciones.

## Estado actual

✅ MVP de instrucciones de skill preparado.
✅ Flujo básico validado en Chrome con un notebook real.
✅ Extensión de Chrome de Codex verificada como instalada y conectada.

## Próximos pasos sugeridos

1. Probar invocación directa `@Chrome` desde un thread nuevo con el plugin activo.
2. Registrar notebooks reales en `.agents/skills/notebooklm/data/library.json`.
3. Probar selección por tema y fallback de notebook activo.
4. Ajustar pasos de interacción si cambia la UX de NotebookLM.
5. Añadir automatizaciones auxiliares (por ejemplo scripts de mantenimiento de la biblioteca).
6. Incluir ejemplos de prompts de alta calidad para consultas complejas.
