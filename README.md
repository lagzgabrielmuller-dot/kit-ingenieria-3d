# Kit de ingeniería y diseño 3D para Claude

Marketplace de plugins con **355 skills** para trabajos de electromecánica, diseño 3D, electrónica y automatización. Una vez instalado un plugin, Claude usa cada skill sola cuando el pedido encaja; no hace falta nombrarla.

Hay un plugin propio (`ingenieria-3d`) y catorce armados con skills de la comunidad, copiadas sin cambios desde sus repos con sus licencias y créditos (cada plugin tiene su `CREDITOS.md` y su carpeta `licencias/`).

## Plugins

| Plugin | Skills | Para qué sirve |
|---|---:|---|
| `ingenieria-3d` | 34 | **Propio.** Cálculo electromecánico (instalaciones eléctricas, máquinas eléctricas, energía solar, elementos de máquinas, resistencia de materiales, tolerancias y ajustes, neumática, oleohidráulica, maniobra y transporte, transferencia de calor, secado, refrigeración, CNC y ensayos), gestión (mantenimiento, organización industrial, higiene y seguridad, normas argentinas), planos IRAM, modelos y visores 3D, Blender en vivo y control de modelos, informes (también en Google Docs, en vivo) y memorias de cálculo, simuladores, exposiciones, revisión técnica, control de videos, tablero de progreso y equipo de modelos guía (Codex, Gemini, Claude, Ollama, OpenRouter) |
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

### Cálculo electromecánico

| Skill | Para qué sirve |
|---|---|
| `calculos-ingenieria` | Memorias de cálculo: iluminación, aire comprimido, conductores, motores, cintas y balances de masa y energía |
| `instalaciones-electricas` | Corriente de proyecto, caída de tensión y sección mínima, corrección del factor de potencia, cortocircuito de un transformador y sección térmica, jabalina de puesta a tierra e iluminación por lúmenes, con memoria de cálculo (`electricas.py`) |
| `maquinas-electricas` | Transformadores (ensayos de vacío y cortocircuito, regulación, rendimiento, Dyn11, paralelo), motor asincrónico (placa, cupla, Kloss, arranques directo, estrella-triángulo, autotransformador, arrancador suave, variador, clases IE), monofásicos y Steinmetz, máquina sincrónica y de continua. Calculadora `maquinas.py` |
| `energia-solar-fotovoltaica` | Sistemas fotovoltaicos aislados y conectados a la red: horas de sol pico, consumos, paneles en serie y paralelo con corrección por temperatura, regulador PWM o MPPT, baterías, inversor, cables y protecciones, energía anual y Ley 27.424 (`fotovoltaica.py`) |
| `elementos-de-maquinas` | Tornillos (ISO 898-1, precarga y torque), ejes a fatiga (Goodman) y fluencia, chavetas DIN 6885-1, rodamientos (L10), correas en V, cadenas, engranajes rectos (Lewis) y soldadura en filete, con memoria de cálculo; reproduce un ejemplo de Shigley (`elementos.py`) |
| `resistencia-de-materiales` | Resistencia de materiales: tracción, corte, torsión, vigas (reacciones, diagramas y flecha por integración numérica), pandeo (Euler y Tetmajer), círculo de Mohr y von Mises, secciones y perfiles IPN, UPN y ángulos, con datos del CIRSOC (`resistencia.py`) |
| `tolerancias-y-ajustes` | Tolerancias y ajustes: sistema ISO 286 (grados IT, desviaciones, juego y aprieto), ajustes recomendados, tolerancias generales ISO 2768, tolerancias geométricas, rugosidad, cadenas de cotas y metrología con calibre, micrómetro e incertidumbre (`tolerancias.py`) |
| `ensayos-materiales` | Tracción, dureza Brinell, Rockwell y Vickers, Charpy, doblado y plegado, fatiga y ensayos no destructivos, con informe de laboratorio e incertidumbre. Calculadora `ensayos.py` (lee el CSV de la máquina de tracción) |
| `neumatica-electroneumatica` | Circuitos neumáticos y electroneumáticos (FluidSIM o tablero): símbolos ISO 1219, secuencias, cascada, paso a paso, relés, GRAFCET y paso a PLC, cilindros y pandeo. Calculadora `neumatica.py` (arma la cascada desde la secuencia) |
| `oleohidraulica` | Oleohidráulica: cilindros (fuerza, presión, velocidades, diámetro normalizado ISO 3320, pandeo del vástago), bombas y motores, viscosidad del aceite, mangueras y pérdida de carga, acumuladores, tanque, calor, válvulas y circuitos ISO 1219 (`oleohidraulica.py`) |
| `maniobra-y-transporte` | Maniobra y transporte: cintas transportadoras (CEMA y DIN 22101), tornillos sinfín, elevadores de cangilones, aparejos, cables de acero, eslingas, puentes grúa y autoelevadores, con el Decreto 351/79 para aparatos de izar (`transporte.py`) |
| `transferencia-de-calor` | Transferencia de calor: paredes y caños multicapa, convección natural y forzada con propiedades del aire y del agua, radiación, coeficiente U, intercambiadores (LMTD y ε-NTU), aletas y espesor de aislación de hornos, secaderos, tanques y cañerías (`calor.py`) |
| `secado-y-psicrometria` | Aire húmedo (HR, W, entalpía, rocío, bulbo húmedo, altitud) y secaderos de aire caliente: agua a evaporar, caudal del ventilador, potencia del calentador, combustible, recirculación y diagrama psicrométrico en SVG; verificado contra CoolProp (`psicrometria.py`) |
| `refrigeracion-y-aire-acondicionado` | Refrigeración y aire acondicionado: ciclo de compresión y COP, tablas presión-temperatura de siete refrigerantes (R-134a, R-410A, R-32, R-22, R-600a, R-290, R-404A), diagnóstico por sobrecalentamiento y subenfriamiento, vacío y carga de gas, carga térmica en W y frigorías/h (`refrigeracion.py`) |
| `cnc-mecanizado` | Programación CNC de torno y fresadora (estilo Fanuc, con notas de controles GSK), ciclos, compensaciones, datos de corte, hoja de proceso y simulación. `cnc.py` calcula corte, genera un perfil de torneado y revisa programas .nc |

### Normas, gestión y seguridad

| Skill | Para qué sirve |
|---|---|
| `normas-tecnicas-ar` | Mapa de normas argentinas: AEA 90364, IRAM-AADL J 20-06, Ley 19.587 y Dec. 351/79 con sus resoluciones, serie IRAM 4500 de dibujo, ISO 1219, aceros, ambiente y aparatos a presión por provincia; valores clave con su fuente y cómo citar en APA 7 |
| `higiene-y-seguridad` | Higiene y seguridad en Argentina (Ley 19.587, Decreto 351/79 y resoluciones de la SRT): carga de fuego y matafuegos, clases de fuego, ruido y dosis, estrés térmico, ventilación, riesgo eléctrico, máquinas, EPP y matriz de riesgos (`seguridad.py`) |
| `mantenimiento-industrial` | Mantenimiento: estrategias (correctivo, preventivo, predictivo, TPM, RCM), MTBF, MTTR, disponibilidad, confiabilidad y OEE, Pareto, Ishikawa y AMFE, plan preventivo y órdenes de trabajo, lubricación de rodamientos, vibraciones ISO 20816-3, termografía, alineación, balanceo y bloqueo (`mantenimiento.py`) |
| `organizacion-industrial` | Organización industrial: costos y punto de equilibrio, amortización, VAN, TIR y recupero en moneda constante, estudio de métodos y tiempos con los suplementos de la OIT, capacidad y balanceo de línea, layout, Gantt y PERT/CPM, gráficos de control y Cp/Cpk (`organizacion.py`) |

### Planos, 3D y video

| Skill | Para qué sirve |
|---|---|
| `planos-tecnicos` | Planos en DXF (AutoCAD) y PDF A3 vectorial según normas IRAM, con recuadro, rótulo y tabla de revisiones |
| `modelado-3d-cad` | Modelos 3D sólidos con CadQuery: STEP para SolidWorks y Fusion 360, STL para imprimir, GLB para Blender y vistas DXF en método ISO E |
| `visor-3d-interactivo` | Visores 3D en una página HTML (three.js): rotar con el mouse, capas, vistas, datos de cada equipo y animaciones |
| `conectar-programas-cad` | Guía para conectar Claude con Blender (servidor comunitario y el oficial de Blender Lab), Fusion 360 y FreeCAD (servidores MCP), con los cuidados de seguridad |
| `blender-verificacion` | Control de modelos de Blender: medidas de cada pieza en mm, escala sin aplicar, errores de geometría, normales, texturas faltantes, cámara y luces (`inspeccionar_escena.py`), y hoja con frente, lateral, planta e isométrica (`vistas_ortogonales.py`). Reglas para modelar con precisión y exportar |
| `render-presentacion-3d` | Render de presentación con un comando (`estudio_turntable.py`): estudio con piso y tres luces escaladas al modelo, cámara encuadrada, foto principal y video girando 360° en MP4 con color BT.709, desde un `.blend` o importando GLB, STL, OBJ o FBX |
| `blender-en-vivo` | Modelo 3D que se arma en vivo en un Blender abierto (por ejemplo en el segundo monitor): Claude le manda pasos de Python, saca capturas para ir mostrando el avance y al final guarda el `.blend` (`vivo.py`) |
| `video-calidad` | Control de calidad de videos antes de entregarlos: color BT.709 con etiquetas (evita rojos anaranjados en YouTube), negros y congelados, silencios, volumen en LUFS, costura de loops y hoja de contacto. `video_calidad.py` revisa, normaliza el audio y corrige el color |

### Informes, presentaciones y control

| Skill | Para qué sirve |
|---|---|
| `informe-tecnico` | Informes, trabajos prácticos y memorias técnicas en Word, PDF o Google Docs; en Google Docs se ven escribirse en vivo, sección por sección, con tablas y figuras (`docs_bloques.py`) |
| `exposicion-oral` | Defensas y exposiciones en grupo: reparto por tiempos, guion hablado, tarjetas, Pecha Kucha, panel de expertos, banco de preguntas probables con respuesta y checklist del día |
| `simulador-educativo` | Simuladores de una sola página que andan sin internet, para corroborar un ensayo o un cálculo: parámetros, gráfico, animación, modo laboratorio con mediciones y exportar CSV/PNG. Plantilla probada con Playwright |
| `revision-tecnica` | Control independiente antes de entregar: rehace las cuentas (`verificar_numeros.py`), revisa unidades, normas, citas, coherencia y consigna, y pasa el archivo final por `revisar_documento.py` (marcadores sin completar, nombres escritos de dos formas, tablas incompletas, texto que quedó) |

### Trabajo con IA

| Skill | Para qué sirve |
|---|---|
| `progreso-en-vivo` | Tablero en el navegador que se actualiza solo mientras Claude trabaja: plan y pasos, imágenes (renders, vistas), borrador del texto, preguntas y actividad; con hook para Claude Code (`progreso.py`) |
| `equipo-de-modelos` | Claude lidera y otros modelos (Codex, Gemini, otra sesión de Claude, Ollama local, OpenRouter) revisan o proponen alternativas, de a uno o en paralelo, con un informe para comparar; tapa claves antes de enviar y no usa la GPU con un juego abierto (`guias.py`) |
| `trabajar-con-codex` | Claude le consulta a Codex (ChatGPT) desde la terminal para una segunda opinión o una revisión independiente, y combina las dos respuestas |

Requisitos de los scripts propios: las calculadoras (`scripts/*.py` de cada skill) usan solo Python 3.9 o más y traen `--help` y un `demo` que reproduce el ejemplo resuelto de su SKILL.md (por ejemplo `python maquinas.py demo`). Las excepciones: planos y 3D piden `pip install ezdxf pymupdf cadquery trimesh matplotlib`; `video_calidad.py` necesita `ffmpeg`; los scripts de `blender-verificacion` y `render-presentacion-3d` corren dentro de Blender (`blender -b archivo.blend -P script.py -- ...`), y `vivo.py` (de `blender-en-vivo`) abre Blender en pantalla y le manda los pasos.

## Skills de la comunidad

- Copiadas **sin modificaciones** de repos con licencia MIT, Apache-2.0 o BSD. Cada plugin dice en su `CREDITOS.md` de qué repo y de qué commit viene cada skill, qué necesita instalado y qué se revisó.
- Antes de copiarlas revisé scripts, llamadas de red, binarios, hooks e instrucciones ocultas para Claude. Los avisos puntuales (por ejemplo, skills que necesitan una clave de API o un programa pago) están en cada `CREDITOS.md`.
- En [CATALOGO.md](CATALOGO.md) hay más recursos que se instalan desde su repo original y los que no se copiaron, con el motivo.

## Mejorar o agregar skills

- Cada skill es una carpeta con un `SKILL.md`. El encabezado tiene `name` y `description`; la descripción es lo que decide cuándo Claude usa la skill.
- Las skills propias se mejoran en `plugins/ingenieria-3d/`. Las de la comunidad conviene dejarlas como están y, si sus autores las actualizan, volver a copiarlas y anotar el commit nuevo en el `CREDITOS.md`.
- Algunos plugins (`blender-bim-sverchok`, `simulacion-numerica`, `mattpocock-skills`) conservan las subcarpetas del original para que funcionen los enlaces entre skills; por eso su `plugin.json` lista cada skill en el campo `skills`.
- Se edita desde GitHub (lápiz ✏️ → *Commit changes*) o pidiéndoselo a Claude (las reglas para Claude están en `CLAUDE.md`).
- Antes de subir cambios: `python scripts/validar_kit.py --completo`. Revisa frontmatter, nombres, descripciones, rutas, skills repetidas y claves filtradas, que este README esté al día, que las skills nombradas en negrita existan y los links, y corre el demo de cada script. GitHub Actions lo corre solo en cada push.
- Los plugins no fijan número de versión, así que cada cambio subido cuenta como actualización. En Claude Code se baja con `/plugin marketplace update kit-ingenieria-3d`.
- No guardar en este repo archivos `.zip` de otros plugins ni claves o contraseñas: el repo es público.

## Estructura

```
.claude-plugin/marketplace.json     catálogo del marketplace (15 plugins)
CLAUDE.md                           reglas para Claude cuando edita este repo
scripts/validar_kit.py              revisa marketplace, plugins, skills, README y demos (lo corre GitHub Actions)
plugins/ingenieria-3d/              skills propias, con scripts y plantillas
plugins/<plugin de la comunidad>/
  .claude-plugin/plugin.json
  CREDITOS.md                       autores, commits, requisitos y revisión
  licencias/                        licencia completa de cada repo de origen
  skills/                           las skills
CATALOGO.md                         más recursos de la comunidad, con licencias
```
