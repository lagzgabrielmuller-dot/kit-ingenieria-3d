# Kit de ingeniería y diseño 3D para Claude

Plugin con skills para trabajos de electromecánica y diseño 3D. Una vez instalado, Claude usa cada skill sola cuando el pedido encaja; no hace falta nombrarla.

| Skill | Para qué sirve |
|---|---|
| `planos-tecnicos` | Planos en DXF (AutoCAD) y PDF A3 vectorial según normas IRAM, con recuadro, rótulo y tabla de revisiones |
| `modelado-3d-cad` | Modelos 3D sólidos con CadQuery: STEP para SolidWorks y Fusion 360, STL para imprimir, GLB para Blender y vistas DXF en método ISO E |
| `visor-3d-interactivo` | Visores 3D en una página HTML (three.js): rotar con el mouse, capas, vistas, datos de cada equipo y animaciones |
| `informe-tecnico` | Informes, trabajos prácticos y memorias técnicas en Word y PDF |
| `calculos-ingenieria` | Memorias de cálculo: iluminación, aire comprimido, conductores, motores, cintas y balances de masa y energía |
| `conectar-programas-cad` | Guía para conectar Claude con Blender y FreeCAD (servidores MCP) y que trabaje directamente en esos programas |

**Más recursos de la comunidad**: en [CATALOGO.md](CATALOGO.md) hay skills y plugins de otras personas para CAD, 3D, fluidos, bombas, termodinámica y cálculo científico, con su licencia, lo que revisé de cada uno y cómo instalarlos.

## Instalación

**En Claude (app de escritorio o web)**

1. Customize → Browse plugins.
2. Personal → **+** → Add marketplace from GitHub.
3. Pegar `https://github.com/lagzgabrielmuller-dot/kit-ingenieria-3d`.
4. Instalar el plugin **ingenieria-3d**.

Los nombres de los menús pueden aparecer en español.

**En Claude Code**

```
/plugin marketplace add lagzgabrielmuller-dot/kit-ingenieria-3d
/plugin install ingenieria-3d@kit-ingenieria-3d
```

## Mejorar o agregar skills

- Cada skill es una carpeta `plugins/ingenieria-3d/skills/<nombre>/` con un `SKILL.md`. El encabezado tiene `name` y `description`; la descripción es lo que decide cuándo Claude usa la skill.
- Se edita desde GitHub (lápiz ✏️ → *Commit changes*) o pidiéndoselo a Claude.
- El plugin no fija número de versión, así que cada cambio subido cuenta como actualización. En Claude Code se baja con `/plugin marketplace update kit-ingenieria-3d`.
- No guardar en este repo archivos `.zip` de otros plugins ni claves o contraseñas: el repo es público.

## Estructura

```
.claude-plugin/marketplace.json          catálogo del marketplace
plugins/ingenieria-3d/
  .claude-plugin/plugin.json             datos del plugin
  skills/
    planos-tecnicos/                     SKILL.md + scripts/lamina_a3.py
    modelado-3d-cad/                     SKILL.md + scripts/exportar_cad.py
    visor-3d-interactivo/                SKILL.md + plantilla/visor.html
    informe-tecnico/                     SKILL.md
    calculos-ingenieria/                 SKILL.md
    conectar-programas-cad/              SKILL.md
CATALOGO.md                              recursos de la comunidad, con licencias
```

## Requisitos de los scripts

```
pip install ezdxf pymupdf cadquery trimesh matplotlib
```

Cada script trae un ejemplo: `python lamina_a3.py demo salida` y `python exportar_cad.py demo salida`.
