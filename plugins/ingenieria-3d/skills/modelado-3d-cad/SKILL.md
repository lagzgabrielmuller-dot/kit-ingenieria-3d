---
name: modelado-3d-cad
description: "Modelado 3D sólido y paramétrico de piezas, conjuntos, máquinas e instalaciones con CadQuery (Python), entregado en STEP para SolidWorks y Fusion 360, STL para impresión 3D, GLB para Blender y el navegador, y DXF con las vistas normalizadas para AutoCAD. Usar cuando se pida modelar o diseñar una pieza o un conjunto en 3D, pasar un diseño a un programa CAD, preparar un archivo para imprimir en 3D o renderizar en Blender."
---

# Modelado 3D CAD (CadQuery)

Modelar con **CadQuery** (Python sobre OpenCASCADE: sólidos exactos, no mallas). Instalar con `pip install cadquery trimesh matplotlib ezdxf`.

## Qué entregar según el programa

| Programa | Archivo | Notas |
|---|---|---|
| SolidWorks | `.step` | Abre como pieza o como ensamble, con cada pieza separada, su nombre y su color |
| Fusion 360 | `.step` | Igual que en SolidWorks; se importa como cuerpos sólidos |
| AutoCAD | `_vistas.dxf` + `.step` | Frente, planta y lateral en método ISO E; para el plano completo con rótulo y cotas, usar la skill **planos-tecnicos** |
| Blender | `.glb` | glTF 2.0 en metros (Blender y three.js trabajan en metros), con colores por pieza |
| Impresión 3D | `.stl` | Malla cerrada; el resumen avisa si no lo está |

## Herramienta base

`scripts/exportar_cad.py` (en la carpeta de esta skill). Ejemplo completo: `python scripts/exportar_cad.py demo salida`.

```python
import sys; sys.path.insert(0, "<carpeta de esta skill>/scripts")
import cadquery as cq
from exportar_cad import exportar, vistas_dxf

# Todas las medidas como parámetros con nombre (mm): cambiar una regenera todo
L, A, E, D_AG, R = 120, 80, 12, 9, 6
placa = (cq.Workplane("XY").box(L, A, E).translate((0, 0, E / 2))
         .edges("|Z").fillet(R)
         .faces(">Z").workplane().rect(L - 24, A - 24, forConstruction=True).vertices().hole(D_AG))

exportar(placa, "salida/placa", nombre="Placa base", color=(0.6, 0.62, 0.66), densidad=7.85)
vistas_dxf(placa, "salida/placa_vistas.dxf")
```

- `exportar()` acepta un Workplane, una forma o un `cq.Assembly`. Genera `.step`, `.stl`, `.glb` y `_vista.png`, y muestra medidas totales, volumen, masa (con la densidad en g/cm³: acero 7,85; aluminio 2,70; PLA 1,24), si el sólido es válido y si la malla está cerrada.
- `vistas_dxf()` proyecta aristas visibles (capa CONTORNO) y ocultas (capa OCULTAS) y ubica las vistas en método ISO E: planta debajo del frente y lateral izquierda a la derecha. Con `msp=` y `escala=` dibuja directamente dentro de una lámina de la skill planos-tecnicos; devuelve la caja de cada vista para acotar.

Ensambles:

```python
ensamble = cq.Assembly(name="Transmisión")
ensamble.add(placa, name="Placa base", color=cq.Color(0.6, 0.62, 0.66))
ensamble.add(eje, name="Eje", loc=cq.Location((0, 0, E)), color=cq.Color(0.85, 0.55, 0.2))
exportar(ensamble, "salida/transmision")
```

## Cómo modelar bien

- Medidas en mm, Z hacia arriba, origen en un punto útil (centro de la base, eje del agujero principal).
- Ningún número suelto en el medio del código: todo como variable con nombre al principio.
- Orden: boceto → extruir, revolucionar, barrer o loft → agujeros (`hole`, `cboreHole`, `cskHole`) → redondeos y chaflanes al final, que son lo que más falla.
- Medidas reales y normalizadas: agujeros pasantes y roscas métricas ISO, perfiles, caños y chapas con medidas comerciales, rodamientos y chavetas de catálogo (anotar la fuente).
- En conjuntos, cada pieza con nombre y color, y sin interferencias: `a.intersect(b).Volume()` tiene que dar prácticamente 0.
- Si piden "lo más completo posible", sumar detalles reales (bulones, soportes, protecciones, placas de identificación) sin perder claridad.
- Si piden mejorar un modelo que ya existe, partir de ese archivo y su código, no empezar de cero.

## Verificación

1. Mirar `_vista.png` (es una vista de control aproximada; los colores reales quedan en el GLB y el STEP): la forma tiene que coincidir con lo pedido.
2. Revisar el resumen: medidas totales esperadas, `solido_valido: True` y, para imprimir, `malla_cerrada: True`.
3. Volver a importar el STEP (`cq.importers.importStep`) y contar los sólidos.
4. Renderizar el DXF de vistas y comprobar que frente, planta y lateral estén donde corresponde.

## Blender

Si Blender está instalado en la compu del usuario, se puede renderizar sin abrir la ventana con `blender -b -P render.py`. En el script: `bpy.ops.import_scene.gltf(filepath="pieza.glb")`, cámara, luces y `bpy.ops.render.render(write_still=True)`. El GLB ya viene en metros, no hay que escalarlo.
