# Codex NotebookLM Bridge Skill

Repositorio inicial para una skill de Codex que conecta con Google NotebookLM
mediante control del navegador Chrome (extensión/bridge de Codex), con enfoque
RAG sobre fuentes del usuario.

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

## Próximos pasos sugeridos

1. Validar en una sesión real con el bridge de Chrome conectado.
2. Ajustar selectores/pasos de interacción según UX actual de NotebookLM.
3. Añadir automatizaciones auxiliares (por ejemplo scripts de mantenimiento de la biblioteca).
4. Incluir ejemplos de prompts de alta calidad para consultas complejas.
