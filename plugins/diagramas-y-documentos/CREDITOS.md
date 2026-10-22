# Créditos: Diagramas y documentos

Diagramas para informes y herramientas de documentos que complementan las skills de Word, PDF y Excel que ya trae la app.

Skills escritas por otras personas y copiadas **sin modificaciones** desde sus repos, con permiso de sus licencias. Las licencias completas están en `licencias/`.

| Autor y repo | Licencia | Commit copiado |
|---|---|---|
| bahayonghang, [bahayonghang/drawio-skills](https://github.com/bahayonghang/drawio-skills) | MIT | `2aa612ef9d5b65179eeebe7ab33f97f39d2315b4` |
| daymade, [daymade/claude-code-skills](https://github.com/daymade/claude-code-skills) | MIT | `1edbe0b346a1f1fd9fbf61102d80be338fd91eb2` |

## Skills (6)

| Skill | Para qué sirve (descripción original) |
|---|---|
| `drawio` | Create, edit, replicate, import, and export draw.io diagrams with an offline YAML-first workflow: architecture, network topologies, flowcharts, UML/ER, org charts,… |
| `drawio-academic-skills` | Publication-figure overlay for draw.io. Use instead of drawio whenever the diagram is for a paper, thesis, dissertation, journal, conference, IEEE/ACM submission,… |
| `excalidraw-use` | Places existing images onto an Excalidraw whiteboard, turns a slide deck into clean per-slide images, and inspects a .excalidraw file. Use whenever someone mentions… |
| `excel-automation` | Creates formatted Excel reports with openpyxl, parses complex xlsm financial models with stdlib zipfile+xml when openpyxl fails, and controls Excel windows on macOS… |
| `pdf-to-html` | Converts a PDF into one self-contained, readable HTML file that preserves images, tables, charts and reading order — optionally translating it into another language… |
| `photo-to-scanned-pdf` | Two pipelines ending at a scanner-look PDF. (1) Phone photos of paper documents (contracts, stamped certificates, receipts, forms, handwritten notes) → clean… |

## Qué necesitan

- `drawio`: Node.js; la app de escritorio de draw.io para exportar a PNG, SVG o PDF. La carpeta trae un `.mcp.json` de ejemplo para un servidor MCP de draw.io que no se activa solo.
- `photo-to-scanned-pdf`, `pdf-to-html`, `excel-automation`: Python con las bibliotecas que indica cada skill (Pillow, opencv, pymupdf, openpyxl).

## Revisión

Antes de copiarlas revisé licencia, estructura, scripts, llamadas de red, binarios, hooks y frases que intenten darle órdenes ocultas a Claude. Los scripts no se ejecutaron durante la revisión. Si un autor publica una versión nueva, se puede volver a copiar y actualizar el commit de la tabla.

Un detalle de `drawio`: el archivo de referencia `references/upstream/pure-drawio-skill.md` (copia de otra skill, que se consulta solo para editar XML a mano) le pide a Claude que actualice la carpeta con `git pull` sin avisar. Instalado como plugin no hace nada, porque esa carpeta no es un repositorio git; si alguna vez se usa desde un clon de este kit, lo único que haría es bajar los últimos cambios de este mismo repo. Igual, si Claude menciona una actualización así, se le puede decir que no la haga. El catálogo de formas viene comprimido (`assets/catalog/*.json.gz`): son listas JSON de formas de draw.io.
