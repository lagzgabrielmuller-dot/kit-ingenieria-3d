# Catálogo de skills y plugins de la comunidad

Recursos de GitHub para que Claude trabaje mejor en diseño 3D, CAD e ingeniería. El 21/10/2026 revisé la licencia y la estructura de cada repo, y en detalle (hooks o servidores que se ejecutan solos, llamadas de red, binarios e instrucciones sospechosas) las skills que se indican debajo de cada tabla. En esas no encontré problemas; las demás no las revisé a fondo.

**Ya incluidas en este kit**: las skills revisadas en detalle de las tablas 1 a 3 (51 en total) están copiadas en los plugins `cad-3d-comunidad`, `fluidos-bombas-termo` y `ciencia-y-calculo`, con sus licencias y créditos. El resto de cada repo, y los de las secciones 4 a 6, se instalan desde su repo original. El commit revisado figura debajo de cada tabla; si un repo cambió mucho después de esa fecha, conviene mirarlo antes de instalar.

## 1. CAD y modelado 3D

| Repo | Licencia | Qué trae | Cómo se instala |
|---|---|---|---|
| [rawwerks/VibeCAD](https://github.com/rawwerks/VibeCAD) | MIT | Marketplace `vibecad` con 3 plugins: **build123d** (modelado paramétrico con build123d, 30 ejemplos: engranajes, roscas, rodamientos, bridas, caños; script que mide volumen y caja), **model-compare** (compara dos modelos por booleanas: IoU, Dice), **render-glb** (renderiza un GLB a PNG para verlo) y **gltf-transform** (optimiza y comprime GLB) | Claude Code: `/plugin marketplace add rawwerks/VibeCAD` y después `/plugin install build123d@vibecad` (igual con `render-glb` y `gltf-transform`). App de Claude: agregar el marketplace desde GitHub con `rawwerks/VibeCAD`. Necesita `uv` y `bun` |
| [cyberchitta/cad-khana](https://github.com/cyberchitta/cad-khana) | Apache-2.0 | Skill **cad-khana**: ensambles con build123d con verificación de interferencias y holguras entre piezas, y controles de imprimibilidad | La herramienta: `uv tool install git+https://github.com/cyberchitta/cad-khana`. La skill, según su README |
| [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) | MIT | 13 skills. Las más útiles acá: **dfm** (revisión de fabricabilidad para chapa plegada, mecanizado CNC e inyección), **dfam-check** (reglas de impresión 3D FDM, SLA y SLS sobre una malla), **engineering-drawing** (plano en PDF con vistas, ocultas, cotas y rótulo), **dxf**, **cad**, **gcode** (laminar con OrcaSlicer), **step-parts** (baja piezas comerciales en STEP: motores, rodamientos, placas) y otras de robótica (URDF, SDF, SRDF) | Según su README. Ojo: `cad`, `dxf` y `engineering-drawing` usan su herramienta `cadgen`, que descarga su propia instalación la primera vez; `dfm` y `dfam-check` son scripts Python independientes (trimesh) |
| [JonFermin/cadsmith](https://github.com/JonFermin/cadsmith) | MIT | Skills **make-model**, **make-mechanism** (mecanismos: articulaciones, trenes de engranajes, tornillos), **edit-model** y **export-model**, con vista previa en three.js | Pensado para usarse dentro de su propio repo: clonarlo y abrirlo con Claude Code |

Revisadas en detalle: las 4 de VibeCAD (commit `609e888`), cad-khana (`8d8892a`) y, de text-to-cad (`2f79365`), dfm, dfam-check, gcode y step-parts. De cadsmith solo miré licencia, descripciones y dependencias.

## 2. Ingeniería: fluidos, bombas y termodinámica

| Repo | Licencia | Qué trae | Cómo se instala |
|---|---|---|---|
| [Soljourner/claude-engineering-skills](https://github.com/Soljourner/claude-engineering-skills) | MIT | 36 skills. Ayudas: conversor de unidades de ingeniería, propiedades de fluidos, selección del tipo de bomba. Librerías: **pint** (unidades), **fluids** (pérdida por fricción en cañerías, dimensionado de bombas), **thermo** y **CoolProp** (propiedades termodinámicas), **scipy** (optimización), **networkx** (redes hidráulicas), **pyvista** (visualización 3D). Métodos: análisis estructural (FEA), dinámica de fluidos, termodinámica, bombas centrífugas y volumétricas, curvas H-Q y leyes de afinidad, NPSH y cavitación, rendimiento. Datos: coeficientes de pérdida de accesorios, propiedades de materiales, modelos de turbulencia. Integraciones: API de **SolidWorks**, OpenFOAM, ANSYS y COMSOL | Según su README. Las skills están en subcarpetas (`skills/helpers`, `skills/packages`, etc.) |

Revisadas en detalle (commit `1c3340b`): 29 de las 36, todas menos ANSYS, COMSOL, REFPROP, NASA Earthdata, get-available-resources, sympy-symbolic y matplotlib-visualization.

## 3. Ciencia y cálculo

| Repo | Licencia | Qué trae | Cómo se instala |
|---|---|---|---|
| [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) | MIT | 177 skills, la mayoría de biología y química. Útiles para electromecánica: **sympy** (cálculo simbólico), **matplotlib** y **scientific-visualization** (gráficos), **uncertainty-and-units** (unidades e incertidumbre de mediciones, ideal para ensayos), **statistical-analysis**, **simpy** (simulación de líneas de producción y colas), **pymoo** (optimización con varios objetivos), **matlab** (MATLAB y GNU Octave), **cantera** (combustión), **lab-hardware-cad** (piezas de laboratorio con build123d, con STEP, STL y DXF), **markitdown** (pasar PDF y documentos de Office a texto), **markdown-mermaid-writing** (diagramas) y **pptx-posters** (pósters en PowerPoint) | Según su README. Evitar `infographics`, `scientific-schematics` y `scientific-slides` si no se tiene una clave paga de OpenRouter: la necesitan |

Revisadas en detalle (commit `593377b`): las 13 nombradas en negrita.

## 4. Conectores para manejar programas de la compu

| Repo | Licencia | Para qué |
|---|---|---|
| [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) (MCP for Blender) | MIT | Que Claude cree y modifique escenas directamente en Blender |
| [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) | MIT | Que Claude cree y edite piezas directamente en FreeCAD |

Los pasos de instalación están en la skill `conectar-programas-cad` de este kit.

## 5. Para mirar, pero no copiar

Se pueden leer e instalar desde su repo; no tienen licencia abierta (o la tienen solo para uso no comercial), así que no se pueden copiar a este repo:
[flowful-ai/cad-skill](https://github.com/flowful-ai/cad-skill) (PolyForm Noncommercial, CadQuery para impresión 3D) ·
[rohittp0/ClaudeCAD](https://github.com/rohittp0/ClaudeCAD) ·
[SalvatoreMastrangelo/freecad_skill](https://github.com/SalvatoreMastrangelo/freecad_skill) ·
[swh/openscad-skill](https://github.com/swh/openscad-skill) ·
[andreahaku/openscad_claude_skill](https://github.com/andreahaku/openscad_claude_skill) ·
[Ericonaldo/Claude-CAD-skill](https://github.com/Ericonaldo/Claude-CAD-skill).

Encontrados pero no revisados: [iancanderson/openscad-agent](https://github.com/iancanderson/openscad-agent) ·
[sergioalexo/freecad-skill](https://github.com/sergioalexo/freecad-skill) ·
[dlockamy/claude-cad-workbench](https://github.com/dlockamy/claude-cad-workbench) ·
[mfranzon/render](https://github.com/mfranzon/render) ·
[fed3c3sa/claude-cad](https://github.com/fed3c3sa/claude-cad).

## 6. Listas para descubrir más

[VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) (más de 1000 skills) ·
[BehiSecc/awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills) ·
[GetBindu/awesome-claude-code-and-skills](https://github.com/GetBindu/awesome-claude-code-and-skills) ·
[alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (380 skills, sobre todo de software y negocios).

## Antes de instalar algo nuevo

- Mirar la licencia y la fecha del último cambio.
- Abrir el `SKILL.md` y los scripts: una skill puede pedirle a Claude que ejecute comandos.
- Desconfiar de lo que trae hooks, archivos `.mcp.json` o comandos del tipo `curl ... | sh` de sitios que no sean oficiales.
- Instalar pocas cosas y bien elegidas: muchas skills con temas parecidos compiten entre sí y Claude puede elegir la equivocada.
