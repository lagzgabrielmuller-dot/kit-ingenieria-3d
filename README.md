# Kit de ingeniería y diseño 3D para Claude

Marketplace de plugins con skills para trabajos de electromecánica y diseño 3D. Una vez instalado, Claude usa cada skill sola cuando el pedido encaja; no hace falta nombrarla.

## Plugins

### `ingenieria-3d` (propio, 7 skills)

| Skill | Para qué sirve |
|---|---|
| `planos-tecnicos` | Planos en DXF (AutoCAD) y PDF A3 vectorial según normas IRAM, con recuadro, rótulo y tabla de revisiones |
| `modelado-3d-cad` | Modelos 3D sólidos con CadQuery: STEP para SolidWorks y Fusion 360, STL para imprimir, GLB para Blender y vistas DXF en método ISO E |
| `visor-3d-interactivo` | Visores 3D en una página HTML (three.js): rotar con el mouse, capas, vistas, datos de cada equipo y animaciones |
| `informe-tecnico` | Informes, trabajos prácticos y memorias técnicas en Word y PDF |
| `calculos-ingenieria` | Memorias de cálculo: iluminación, aire comprimido, conductores, motores, cintas y balances de masa y energía |
| `conectar-programas-cad` | Guía para conectar Claude con Blender y FreeCAD (servidores MCP) y que trabaje directamente en esos programas |
| `trabajar-con-codex` | Claude le consulta a Codex (ChatGPT) desde la terminal para una segunda opinión o una revisión independiente, y combina las dos respuestas |

### `cad-3d-comunidad` (10 skills de la comunidad)

Modelado con build123d (con ejemplos de engranajes, roscas, rodamientos y bridas), comparación de modelos, render y optimización de GLB, ensambles con control de interferencias y holguras, revisión de fabricabilidad para CNC, chapa plegada e inyección, reglas de impresión 3D, laminado con OrcaSlicer, descarga de piezas comerciales en STEP y hardware de laboratorio paramétrico.

### `fluidos-bombas-termo` (29 skills de la comunidad)

Bombas centrífugas y volumétricas, curvas H-Q y leyes de afinidad, NPSH y cavitación, selección del tipo de bomba, pérdidas en cañerías y accesorios, propiedades termodinámicas (CoolProp, thermo), conversión de unidades con pint, redes hidráulicas, optimización, análisis estructural, OpenFOAM y automatización de SolidWorks.

### `ciencia-y-calculo` (12 skills de la comunidad)

SymPy, gráficos con Matplotlib, unidades e incertidumbre de mediciones, estadística, simulación de líneas de producción con SimPy, optimización con pymoo, MATLAB y Octave, combustión con Cantera, conversión de PDF y Office a texto, diagramas Mermaid y pósters en PowerPoint.

Los tres plugins de la comunidad son copias sin cambios de repos con licencia MIT o Apache-2.0. Cada uno tiene su `CREDITOS.md` con autores, commit copiado y requisitos, y su carpeta `licencias/`. En [CATALOGO.md](CATALOGO.md) hay más recursos para instalar desde su repo original.

## Instalación

**En Claude (app de escritorio o web)**

1. Customize → Browse plugins.
2. Personal → **+** → Add marketplace from GitHub.
3. Pegar `https://github.com/lagzgabrielmuller-dot/kit-ingenieria-3d`.
4. Instalar los plugins que se quieran: **ingenieria-3d**, **cad-3d-comunidad**, **fluidos-bombas-termo**, **ciencia-y-calculo**.

Los nombres de los menús pueden aparecer en español.

**En Claude Code**

```
/plugin marketplace add lagzgabrielmuller-dot/kit-ingenieria-3d
/plugin install ingenieria-3d@kit-ingenieria-3d
/plugin install cad-3d-comunidad@kit-ingenieria-3d
/plugin install fluidos-bombas-termo@kit-ingenieria-3d
/plugin install ciencia-y-calculo@kit-ingenieria-3d
```

## Mejorar o agregar skills

- Cada skill es una carpeta `plugins/<plugin>/skills/<nombre>/` con un `SKILL.md`. El encabezado tiene `name` y `description`; la descripción es lo que decide cuándo Claude usa la skill.
- Las skills propias se mejoran en `plugins/ingenieria-3d/`. Las de la comunidad conviene dejarlas como están y, si sus autores las actualizan, volver a copiarlas y anotar el commit nuevo en el `CREDITOS.md`.
- Se edita desde GitHub (lápiz ✏️ → *Commit changes*) o pidiéndoselo a Claude.
- Los plugins no fijan número de versión, así que cada cambio subido cuenta como actualización. En Claude Code se baja con `/plugin marketplace update kit-ingenieria-3d`.
- No guardar en este repo archivos `.zip` de otros plugins ni claves o contraseñas: el repo es público.

## Estructura

```
.claude-plugin/marketplace.json          catálogo del marketplace (4 plugins)
plugins/ingenieria-3d/                   skills propias
  skills/
    planos-tecnicos/                     SKILL.md + scripts/lamina_a3.py
    modelado-3d-cad/                     SKILL.md + scripts/exportar_cad.py
    visor-3d-interactivo/                SKILL.md + plantilla/visor.html
    informe-tecnico/                     SKILL.md
    calculos-ingenieria/                 SKILL.md
    conectar-programas-cad/              SKILL.md
    trabajar-con-codex/                  SKILL.md
plugins/cad-3d-comunidad/                CREDITOS.md, licencias/, skills/ (10)
plugins/fluidos-bombas-termo/            CREDITOS.md, licencias/, skills/ (29)
plugins/ciencia-y-calculo/               CREDITOS.md, licencias/, skills/ (12)
CATALOGO.md                              recursos de la comunidad, con licencias
```

## Requisitos de los scripts propios

```
pip install ezdxf pymupdf cadquery trimesh matplotlib
```

Cada script trae un ejemplo: `python lamina_a3.py demo salida` y `python exportar_cad.py demo salida`. Los requisitos de las skills de la comunidad están en el `CREDITOS.md` de cada plugin.
