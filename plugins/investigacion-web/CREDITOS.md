# Créditos: Investigación y búsqueda de skills

Incluye `find-skills`, la skill de Vercel que aparece en los videos de skills.sh: con ella Claude busca skills nuevas con `npx skills find` y sugiere cómo instalarlas.

Skills escritas por otras personas y copiadas **sin modificaciones** desde sus repos, con permiso de sus licencias. Las licencias completas están en `licencias/`.

| Autor y repo | Licencia | Commit copiado |
|---|---|---|
| Vercel, Inc., [vercel-labs/skills](https://github.com/vercel-labs/skills) | MIT | `a80e4c9d12d607631249d4d7d059f835d4b2f13a` |
| daymade, [daymade/claude-code-skills](https://github.com/daymade/claude-code-skills) | MIT | `1edbe0b346a1f1fd9fbf61102d80be338fd91eb2` |
| Armin Ronacher (mitsuhiko), [mitsuhiko/agent-stuff](https://github.com/mitsuhiko/agent-stuff) | Apache-2.0 | `0865c849befd2021490679f96a8dee58c84ac857` |

## Skills (4)

| Skill | Para qué sirve (descripción original) |
|---|---|
| `deep-research` | Creates reusable, source-traced research reports and coordinates provider/mode lanes with original exports. Use for 深度研究, 调研报告, literature reviews, market or company… |
| `fact-checker` | Verifies factual claims in documents using web search and official sources, then proposes corrections with user confirmation. Use when the user asks to fact-check,… |
| `find-skills` | Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest… |
| `summarize` | Fetch a URL or convert a local file (PDF/DOCX/HTML/etc.) into Markdown using `uvx markitdown`, optionally it can summarize |

## Qué necesitan

- `find-skills`: Node.js (`npx skills ...`). Antes de instalar una skill que encuentre, revisarla como dice `CATALOGO.md`.
- `summarize`: `uv` (corre `uvx markitdown`).
- `deep-research` tiene partes y disparadores en chino; funciona igual en español.

## Revisión

Antes de copiarlas revisé licencia, estructura, scripts, llamadas de red, binarios, hooks y frases que intenten darle órdenes ocultas a Claude, sin encontrar problemas. Los scripts no se ejecutaron durante la revisión. Si un autor publica una versión nueva, se puede volver a copiar y actualizar el commit de la tabla.
