# Créditos: Superpowers: método de trabajo para programar

Copia de las skills de [obra/superpowers](https://github.com/obra/superpowers). Mantiene el nombre `superpowers` porque las skills se llaman entre sí como `superpowers:...`. No se copiaron `using-superpowers` (obliga a usar skills antes de cualquier respuesta), `diagnosing-superpowers` ni `writing-skills` (la app ya trae una para crear skills).

**Ojo**: `brainstorming` pide usarse antes de cualquier trabajo creativo, así que con este plugin instalado Claude va a preguntar y planificar más antes de hacer. Conviene instalarlo solo para proyectos de programación.

Skills escritas por otras personas y copiadas **sin modificaciones** desde sus repos, con permiso de sus licencias. Las licencias completas están en `licencias/`.

| Autor y repo | Licencia | Commit copiado |
|---|---|---|
| Jesse Vincent, [obra/superpowers](https://github.com/obra/superpowers) | MIT | `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b` |

## Skills (12)

| Skill | Para qué sirve (descripción original) |
|---|---|
| `brainstorming` | You MUST use this before any creative work - creating features, building components, adding functionality, modifying behavior, or planning anything new, in software… |
| `dispatching-parallel-agents` | Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies |
| `executing-plans` | Use when executing an implementation plan in the current session as the implementer yourself — your human partner chose inline execution, or no subagent tool is available |
| `finishing-a-development-branch` | Use when implementation is complete, all tests pass, and you need to decide how to integrate the work |
| `receiving-code-review` | Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor… |
| `requesting-code-review` | Use when completing tasks, implementing major features, or before merging to verify work meets requirements |
| `subagent-driven-development` | Use when executing implementation plans with independent tasks in the current session |
| `systematic-debugging` | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| `test-driven-development` | Use when implementing any feature or bugfix, before writing implementation code |
| `using-git-worktrees` | Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated workspace exists via native… |
| `verification-before-completion` | Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before… |
| `writing-plans` | Use when you have a spec or requirements for a multi-step task, before touching code |

## Qué necesitan

- git. Node.js solo para el compañero visual opcional de `brainstorming` (un servidor local en la propia compu).

## Revisión

Antes de copiarlas revisé licencia, estructura, scripts, llamadas de red, binarios, hooks y frases que intenten darle órdenes ocultas a Claude, sin encontrar problemas. Los scripts no se ejecutaron durante la revisión. Si un autor publica una versión nueva, se puede volver a copiar y actualizar el commit de la tabla. El servidor de `brainstorming` escucha solo en la compu local y pide una clave por sesión.
