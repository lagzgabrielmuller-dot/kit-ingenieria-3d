# Créditos: CAD y 3D (comunidad)

Skills escritas por otras personas y copiadas **sin modificaciones** desde sus repos, con permiso de sus licencias. Las licencias completas están en `licencias/` (y `dfm`, `dfam-check`, `step-parts` y `gcode` traen además la suya dentro de su carpeta).

| Skill | Autor y repo | Licencia | Commit copiado |
|---|---|---|---|
| `build123d`, `model-compare`, `render-glb`, `gltf-transform` | Raymond Weitekamp, [rawwerks/VibeCAD](https://github.com/rawwerks/VibeCAD) | MIT | `609e8885270cfdaeb73d96dda2e29362194d544d` |
| `cad-khana` | cyberchitta, [cyberchitta/cad-khana](https://github.com/cyberchitta/cad-khana) | Apache-2.0 | `8d8892ae8978ec044f030465769c027478b15af9` |
| `dfm`, `dfam-check`, `step-parts`, `gcode` | Thompson Labs LLC, [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) | MIT | `2f793659fb7bab537e2f00836e06448fc4087cb2` |
| `lab-hardware-cad` | K-Dense Inc., [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) | MIT | `593377bb048752abb0152deab9fbb1083a6087df` |
| `openscad` | Armin Ronacher (mitsuhiko), [mitsuhiko/agent-stuff](https://github.com/mitsuhiko/agent-stuff) | Apache-2.0 | `0865c849befd2021490679f96a8dee58c84ac857` |
| `solidworks`, `fusion-360`, `catia`, `siemens-nx`, `rhino` | Major AI Skills contributors, [alivirgo/Major-AI-Skills](https://github.com/alivirgo/Major-AI-Skills) | MIT | `17fb963bd185e23367d23b22f2ea5f3688d27f40` |

## Qué necesita cada una

- `build123d`, `model-compare`, `lab-hardware-cad`: Python con build123d (`pip install build123d`, o `uvx --from build123d ...` como indica la skill).
- `render-glb`, `gltf-transform`: [bun](https://bun.sh) (`bunx render-glb ...`, `bunx @gltf-transform/cli ...`).
- `cad-khana`: la herramienta `khana`, con `uv tool install git+https://github.com/cyberchitta/cad-khana` (la skill lo explica en `references/install.md`).
- `dfm`, `dfam-check`: `pip install -r requirements.txt` dentro de cada carpeta (trimesh, numpy, rtree, scipy, networkx, lxml).
- `gcode`: OrcaSlicer instalado.
- `step-parts`: conexión a internet; baja piezas de [step.parts](https://step.parts).
- `openscad`: OpenSCAD instalado (la skill genera vistas previas desde varios ángulos, extrae los parámetros y exporta STL).
- `solidworks`, `fusion-360`, `catia`, `siemens-nx`, `rhino`: guías para automatizar cada programa por su API (SolidWorks por COM con Python o VBA en Windows, Fusion con su API de Python, NX Open, RhinoCommon y Grasshopper). Necesitan el programa instalado con su licencia; las carpetas traen además versiones de la guía para otros asistentes (`gpt.md`, `gemini.md`).

## Revisión

Antes de copiarlas revisé licencia, estructura, scripts, llamadas de red, binarios e instrucciones sospechosas, sin encontrar problemas. Los scripts de estas skills no se ejecutaron durante la revisión. Si un autor publica una versión nueva, se puede volver a copiar y actualizar el commit de esta tabla.
