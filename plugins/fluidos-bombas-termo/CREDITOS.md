# Créditos: fluidos, bombas y termodinámica (comunidad)

31 skills de [Soljourner/claude-engineering-skills](https://github.com/Soljourner/claude-engineering-skills), licencia MIT (texto completo en `licencias/claude-engineering-skills-MIT.txt`), copiadas del commit `1c3340ba171b475fb0ecd7b1699e41dac6acd986`.

## Cambios respecto del original

El contenido de los archivos no se modificó. Solo cambió la ubicación: en el original las skills están en subcarpetas (`skills/helpers/…`, `skills/thinking/pump-design/…`) y acá van todas directamente en `skills/`, como necesita Claude para encontrarlas. Siete carpetas se renombraron para coincidir con el nombre que declara su `SKILL.md`:

| Ubicación original | Carpeta acá |
|---|---|
| `thinking/structural-analysis` | `structural-analysis-workflow` |
| `thinking/fluid-dynamics` | `fluid-dynamics-workflow` |
| `thinking/thermodynamics` | `thermodynamics-workflow` |
| `thinking/pump-design/centrifugal-pumps` | `centrifugal-pump-design` |
| `thinking/pump-design/efficiency-optimization` | `pump-efficiency-optimization` |
| `thinking/pump-design/performance-curves` | `pump-performance-curves` |
| `thinking/pump-design/system-integration` | `pump-system-integration` |

Las demás conservan su nombre: de `helpers/` (fluid-property-calculator, engineering-context-init, pump-selection-helper, unit-converter, error-handler-fluids), de `packages/` (numpy-numerics, scipy-optimization, pyvista-visualization, networkx-flow-networks, thermo-package, pint-units, fluids-package), de `integrations/` (solidworks-cad, openfoam-cfd), de `thinking/pump-design/` (cavitation-analysis, positive-displacement-pumps) y de `databases/` (coolprop-db, hydraulic-components-db, material-properties-db, cavitation-risk-db, pump-performance-db, turbulence-models-db).

Después se sumaron, de `integrations/`, `ansys-simulation` (ANSYS Fluent por Python y archivos journal) y `comsol-multiphysics` (interacción fluido-estructura, por ejemplo vibraciones de bombas), para usar con las licencias de la escuela, la facultad o una empresa.

No se copiaron: NIST REFPROP (programa pago y muy específico), NASA Earthdata (aeroespacial), get-available-resources, sympy-symbolic y matplotlib-visualization (estas dos ya están cubiertas por el plugin ciencia-y-calculo).

## Qué necesitan

- Python: `pip install fluids thermo CoolProp pint numpy scipy matplotlib networkx pyvista`.
- `solidworks-cad`: SolidWorks instalado en Windows.
- `openfoam-cfd`: OpenFOAM (en Linux o WSL).
- `ansys-simulation`: ANSYS Fluent con licencia y PyAnsys (`pip install ansys-fluent-core`).
- `comsol-multiphysics`: COMSOL con LiveLink for MATLAB, o el paquete de Python MPh.

## Revisión

Revisé licencia, scripts, enlaces externos (documentación de CoolProp, NIST, fluids, thermo y fabricantes de bombas) e instrucciones sospechosas, sin encontrar problemas. Los scripts no se ejecutaron durante la revisión. Los datos de tablas (coeficientes de pérdida, propiedades) conviene contrastarlos con un catálogo o una norma antes de usarlos en un trabajo.
