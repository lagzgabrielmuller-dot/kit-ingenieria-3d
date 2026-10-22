# Kit de ingeniería y diseño 3D para Claude

Marketplace de plugins con **328 skills** para trabajos de electromecánica, diseño 3D, electrónica y automatización. Una vez instalado un plugin, Claude usa cada skill sola cuando el pedido encaja; no hace falta nombrarla.

Hay un plugin propio (`ingenieria-3d`) y catorce armados con skills de la comunidad, copiadas sin cambios desde sus repos con sus licencias y créditos (cada plugin tiene su `CREDITOS.md` y su carpeta `licencias/`).

## Plugins

| Plugin | Skills | Para qué sirve |
|---|---:|---|
| `ingenieria-3d` | 7 | **Propio.** Planos DXF y PDF A3 según IRAM, modelos 3D para SolidWorks, Fusion 360 y Blender, visores 3D, informes, memorias de cálculo, conexión con Blender y FreeCAD y consultas a Codex (ChatGPT) |
| `cad-3d-comunidad` | 16 | build123d, ensambles sin interferencias, render de GLB, fabricabilidad (CNC, chapa, inyección), impresión 3D, piezas en STEP, OpenSCAD y automatización de SolidWorks, Fusion 360, CATIA, NX y Rhino |
| `fluidos-bombas-termo` | 31 | Bombas, curvas H-Q, NPSH y cavitación, pérdidas en cañerías, CoolProp y thermo, unidades, OpenFOAM, ANSYS Fluent, COMSOL |
| `ciencia-y-calculo` | 26 | SymPy, gráficos, incertidumbre de mediciones, estadística, análisis de datos, scikit-learn, grafos, SimPy, optimización, Octave, redacción técnica, bibliografía y pósters |
| `simulacion-numerica` | 17 | Convergencia de malla, estabilidad (CFL), diferencias finitas, solvers, integración de ODE, posprocesamiento y validación de simulaciones |
| `arduino-embebidos` | 43 | Arduino, ESP32, Raspberry Pi Pico, STM32, MicroPython y Zephyr: placas y pines, código, proyectos, depuración, consumo, baterías, lista de materiales |
| `kicad-electronica` | 16 | Revisión de esquemáticos y placas de KiCad, SPICE y LTspice, EMC, hojas de datos, compra de componentes, JLCPCB y PCBWay |
| `automatizacion-industrial` | 15 | PLC con TIA Portal, CODESYS y Studio 5000, LabVIEW, OpenCV y robótica con ROS 2 |
| `blender-render` | 29 | Modelado, materiales, luces, cámaras, render y animación en Blender; reconstruir modelos a partir de vistas o planos |
| `blender-bim-sverchok` | 73 | Programar Blender con bpy, BIM con Bonsai e IfcOpenShell (instalaciones MEP, cómputos) y diseño paramétrico con Sverchok |
| `manim-animaciones` | 6 | Animaciones explicativas con Manim (con voz en off opcional), FFmpeg y Remotion |
| `diagramas-y-documentos` | 6 | Diagramas en draw.io y Excalidraw, fotos de hojas a PDF escaneado, PDF a HTML y planillas de Excel |
| `investigacion-web` | 4 | `find-skills` (buscar más skills en skills.sh), informes de investigación con fuentes, verificación de datos y resúmenes |
| `superpowers` | 12 | Método estricto para programar: planes, depuración sistemática, TDD, revisión de código. Hace que Claude pregunte y planifique más |
| `mattpocock-skills` | 27 | `grill-me` (entrevista para afilar un plan), `teach`, research, prototipos, especificaciones, TDD y revisión de código |

### Cuáles conviene instalar

Cada plugin instalado suma las descripciones de sus skills a lo que Claude tiene en cuenta, y skills parecidas compiten entre sí. Conviene instalar lo que se usa:

- **Para la escuela y los proyectos**: `ingenieria-3d`, `cad-3d-comunidad`, `fluidos-bombas-termo`, `ciencia-y-calculo`, `diagramas-y-documentos`.
- **Electrónica y automatización**: `arduino-embebidos`, `kicad-electronica`, `automatizacion-industrial`.
- **3D y presentaciones**: `blender-render` (renders lindos), `blender-bim-sverchok` (Blender por código y BIM), `manim-animaciones`.
- **Programar**: `superpowers` **o** `mattpocock-skills`, no los dos (se superponen en TDD, depuración y revisión). `superpowers` cambia bastante la forma de trabajar de Claude: antes de construir cualquier cosa propone una lluvia de ideas.
- `simulacion-numerica` e `investigacion-web` cuando haga falta.

## Instalación

**En Claude (app de escritorio o web)**

1. Customize → Browse plugins.
2. Personal → **+** → Add marketplace from GitHub.
3. Pegar `https://github.com/lagzgabrielmuller-dot/kit-ingenieria-3d`.
4. Instalar los plugins que se quieran.

Los nombres de los menús pueden aparecer en español.

**En Claude Code**

```
/plugin marketplace add lagzgabrielmuller-dot/kit-ingenieria-3d
/plugin install ingenieria-3d@kit-ingenieria-3d
/plugin install cad-3d-comunidad@kit-ingenieria-3d
/plugin install fluidos-bombas-termo@kit-ingenieria-3d
/plugin install ciencia-y-calculo@kit-ingenieria-3d
/plugin install simulacion-numerica@kit-ingenieria-3d
/plugin install arduino-embebidos@kit-ingenieria-3d
/plugin install kicad-electronica@kit-ingenieria-3d
/plugin install automatizacion-industrial@kit-ingenieria-3d
/plugin install blender-render@kit-ingenieria-3d
/plugin install blender-bim-sverchok@kit-ingenieria-3d
/plugin install manim-animaciones@kit-ingenieria-3d
/plugin install diagramas-y-documentos@kit-ingenieria-3d
/plugin install investigacion-web@kit-ingenieria-3d
/plugin install superpowers@kit-ingenieria-3d
/plugin install mattpocock-skills@kit-ingenieria-3d
```

## Skills propias (`ingenieria-3d`)

| Skill | Para qué sirve |
|---|---|
| `planos-tecnicos` | Planos en DXF (AutoCAD) y PDF A3 vectorial según normas IRAM, con recuadro, rótulo y tabla de revisiones |
| `modelado-3d-cad` | Modelos 3D sólidos con CadQuery: STEP para SolidWorks y Fusion 360, STL para imprimir, GLB para Blender y vistas DXF en método ISO E |
| `visor-3d-interactivo` | Visores 3D en una página HTML (three.js): rotar con el mouse, capas, vistas, datos de cada equipo y animaciones |
| `informe-tecnico` | Informes, trabajos prácticos y memorias técnicas en Word y PDF |
| `calculos-ingenieria` | Memorias de cálculo: iluminación, aire comprimido, conductores, motores, cintas y balances de masa y energía |
| `conectar-programas-cad` | Guía para conectar Claude con Blender y FreeCAD (servidores MCP) y que trabaje directamente en esos programas |
| `trabajar-con-codex` | Claude le consulta a Codex (ChatGPT) desde la terminal para una segunda opinión o una revisión independiente, y combina las dos respuestas |

Requisitos de los scripts propios: `pip install ezdxf pymupdf cadquery trimesh matplotlib`. Cada script trae un ejemplo: `python lamina_a3.py demo salida` y `python exportar_cad.py demo salida`.

## Skills de la comunidad

- Copiadas **sin modificaciones** de repos con licencia MIT, Apache-2.0 o BSD. Cada plugin dice en su `CREDITOS.md` de qué repo y de qué commit viene cada skill, qué necesita instalado y qué se revisó.
- Antes de copiarlas revisé scripts, llamadas de red, binarios, hooks e instrucciones ocultas para Claude. Los avisos puntuales (por ejemplo, skills que necesitan una clave de API o un programa pago) están en cada `CREDITOS.md`.
- En [CATALOGO.md](CATALOGO.md) hay más recursos que se instalan desde su repo original y los que no se copiaron, con el motivo.

## Mejorar o agregar skills

- Cada skill es una carpeta con un `SKILL.md`. El encabezado tiene `name` y `description`; la descripción es lo que decide cuándo Claude usa la skill.
- Las skills propias se mejoran en `plugins/ingenieria-3d/`. Las de la comunidad conviene dejarlas como están y, si sus autores las actualizan, volver a copiarlas y anotar el commit nuevo en el `CREDITOS.md`.
- Algunos plugins (`blender-bim-sverchok`, `simulacion-numerica`, `mattpocock-skills`) conservan las subcarpetas del original para que funcionen los enlaces entre skills; por eso su `plugin.json` lista cada skill en el campo `skills`.
- Se edita desde GitHub (lápiz ✏️ → *Commit changes*) o pidiéndoselo a Claude.
- Los plugins no fijan número de versión, así que cada cambio subido cuenta como actualización. En Claude Code se baja con `/plugin marketplace update kit-ingenieria-3d`.
- No guardar en este repo archivos `.zip` de otros plugins ni claves o contraseñas: el repo es público.

## Estructura

```
.claude-plugin/marketplace.json     catálogo del marketplace (15 plugins)
plugins/ingenieria-3d/              skills propias, con scripts y plantillas
plugins/<plugin de la comunidad>/
  .claude-plugin/plugin.json
  CREDITOS.md                       autores, commits, requisitos y revisión
  licencias/                        licencia completa de cada repo de origen
  skills/                           las skills
CATALOGO.md                         más recursos de la comunidad, con licencias
```
