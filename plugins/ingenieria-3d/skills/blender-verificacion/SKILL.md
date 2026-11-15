---
name: blender-verificacion
description: "Verificación de modelos y escenas de Blender con scripts que se pueden correr: medidas reales de cada objeto en milímetros, escala sin aplicar, modificadores, geometría con errores (aristas con más de dos caras, vértices sueltos o repetidos, normales invertidas), materiales e imágenes faltantes, cámara, luces y render, y una hoja con las vistas de frente, lateral, planta e isométrica para controlar la forma mirando una imagen. Usar cuando Claude modela o cambia algo en Blender (por MCP o por script) y hay que comprobar que quedó con las medidas y la forma pedidas, antes de renderizar, exportar o imprimir en 3D, o cuando un bisel sale deforme, un booleano falla o el render sale negro o rosa."
---

# Verificación de modelos en Blender

Modelar con código o por MCP sin mirar el resultado lleva a piezas con la medida mal, escalas raras y errores que aparecen recién al exportar. Dos scripts de `scripts/` cierran el bucle: uno mide y revisa, el otro muestra las cuatro vistas en una sola imagen. Ninguno modifica la escena.

## Flujo

1. Modelar un paso (una pieza o un cambio).
2. `inspeccionar_escena.py`: medidas en mm y hallazgos. Comparar las medidas con las pedidas.
3. `vistas_ortogonales.py`: mirar `hoja_vistas.png` (arriba frente | derecha; abajo planta | iso).
4. Corregir y repetir hasta que las medidas coincidan y no queden errores. Recién ahí renderizar o exportar.

## Cómo se corren

En segundo plano, sobre un `.blend` guardado:

```
blender -b pieza.blend -P inspeccionar_escena.py -- informe.json [--solo COLECCION]
blender -b pieza.blend -P vistas_ortogonales.py -- CARPETA [--tam 700] [--solo COLECCION] [--color material|objeto|aleatorio]
```

En Windows, desde PowerShell, llamar a Blender con `cmd /c "blender.exe -b pieza.blend -P script.py -- args"`: PowerShell 5.1 se come el `--` y Blender toma los argumentos como suyos.

Dentro de una sesión abierta (por ejemplo, ejecutando código por un servidor MCP de Blender):

```python
ns = {'__name__': 'inspeccion'}
exec(open(r'RUTA/inspeccionar_escena.py', encoding='utf-8').read(), ns)
print(ns['texto'](ns['inspeccionar']()))
ns = {'__name__': 'vistas'}
exec(open(r'RUTA/vistas_ortogonales.py', encoding='utf-8').read(), ns)
ns['vistas'](r'C:/carpeta/vistas')
```

Las vistas usan Workbench (no necesita una placa potente: tarda un par de segundos), cámaras ortográficas temporales con encuadre automático, y devuelven la configuración de render, la cámara y el sombreado como estaban.

## Qué revisa `inspeccionar_escena.py`

| Hallazgo | Nivel | Por qué importa |
|---|---|---|
| Imagen de textura faltante | ERROR | Sale rosa en el render |
| Escala sin aplicar con bisel, espesor, arreglo o booleano | AVISO | El modificador trabaja en las medidas sin escalar: biseles ovalados, espesores distintos por eje |
| Escala negativa | AVISO | Invierte las normales al exportar |
| Aristas con más de dos caras | AVISO | Geometría imposible: falla al imprimir en 3D y en booleanos |
| Vértices o aristas sueltos, vértices repetidos | AVISO | Basura que rompe biseles, sombreado y exportación (Merge by Distance) |
| Normales inconsistentes entre caras vecinas | AVISO | Caras negras o transparentes en el render; impresión 3D con agujeros (Recalculate Outside) |
| Ranuras de material vacías | AVISO | Partes sin material |
| Escena sin cámara, o sin luces con el mundo apagado | AVISO | El render falla o sale negro |
| Bordes abiertos | NOTA | No es un sólido cerrado (importa para STL y CAD) |
| Origen lejos de la pieza, oculto en la vista pero visible en el render, Cycles en CPU, unidades en None | NOTA | Comportamientos que confunden |

Las medidas salen en mm a partir de las unidades de la escena (`scale_length`); con el sistema de unidades en None se toma 1 unidad = 1 m. La caja se calcula con los modificadores aplicados (lo que se ve), así que un arreglo o un espesor cambian la medida.

## Reglas para modelar con precisión

1. Unidades al empezar: Metric, `scale_length` 1,0 (1 unidad = 1 m, lo que espera glTF) y longitud mostrada en milímetros. En el código, todo pasa por `mm = lambda v: v / 1000` (`mm(50)` = 0,05). Solo para una escena que es únicamente para imprimir conviene `scale_length` 0,001.
2. Construir con las medidas reales desde la primera primitiva (tamaño y posición en el operador), no escalando después. Si se escaló, aplicar la escala (`bpy.ops.object.transform_apply(scale=True)`) antes de biselar, dar espesor o hacer booleanos.
3. Una pieza por objeto, con nombre que diga qué es (`Eje_motor`, `Chapa_lateral_izq`) y en una colección por subconjunto.
4. Origen en un punto con sentido (centro de la base, eje de giro, punto de montaje): las rotaciones y los ensambles salen solos.
5. Modificadores en lugar de editar a mano (Mirror, Array, Solidify, Bevel); aplicarlos solo para exportar.
6. Booleanos sobre mallas cerradas, sin caras coplanares ni superficies que se toquen apenas: agrandar el cortador una décima de milímetro.
7. Después de cada pieza: inspeccionar, mirar las cuatro vistas y comparar medidas con la consigna o el plano.
8. Guardar como `.py` el script que arma el modelo: la escena se puede rehacer, corregir una medida y volver a generar.
9. Para CAD de verdad (STEP para SolidWorks o Fusion 360, planos acotados), modelar con código paramétrico (**modelado-3d-cad**) y traer a Blender solo el GLB para render y animación.
10. Exportar según el destino: STL o 3MF para imprimir (el STL no guarda unidades: con 1 unidad = 1 m, `bpy.ops.wm.stl_export(..., apply_modifiers=True, global_scale=1000.0)` lo deja en mm); GLB para web y para **visor-3d-interactivo** (`bpy.ops.export_scene.gltf(..., export_format='GLB', export_apply=True)`); FBX o USD para otros programas. STEP solo sale de CAD (**modelado-3d-cad**). Revisar la escala del archivo importado en el programa de destino.
11. Leer `bpy.app.version_string` y escribir para esa versión: entre 4.2 y 5.2 cambiaron EEVEE (`'BLENDER_EEVEE'` desde 5.0), los complementos (extensiones desde 4.2), Grease Pencil (v3 desde 4.3) y las entradas de Geometry Nodes (5.2). Ante la duda, consultar `docs.blender.org/api/<versión>` ([notas de la API 5.2](https://developer.blender.org/docs/release_notes/5.2/python_api/)).

Render final en una placa NVIDIA RTX (Cycles con OptiX y eliminación de ruido por GPU; [manual](https://docs.blender.org/manual/en/5.2/render/cycles/gpu_rendering.html)):

```python
p = bpy.context.preferences.addons["cycles"].preferences
p.compute_device_type = 'OPTIX'; p.get_devices()
for d in p.devices: d.use = (d.type == 'OPTIX')
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; c = sc.cycles
c.device = 'GPU'; c.samples = 256; c.adaptive_threshold = 0.01
c.use_denoising = True; c.denoiser = 'OPENIMAGEDENOISE'; c.denoising_use_gpu = True
```

## Errores frecuentes

| Síntoma | Causa probable | Arreglo |
|---|---|---|
| Bisel o espesor distinto en cada eje | Escala sin aplicar | Aplicar escala y revisar el modificador |
| Booleano que deja agujeros o no corta | Mallas abiertas, caras coplanares o normales invertidas | Cerrar la malla, mover el cortador un poco, Recalculate Outside |
| Render negro | Sin luces y mundo apagado, o la cámara adentro de un objeto | Agregar luz o HDRI; mirar las vistas |
| Render rosa | Textura faltante | Rutas relativas (`//texturas/...`) o empaquetar las imágenes |
| Pieza 1000 veces más grande o más chica al importar | Unidades distintas entre programas | Fijar las unidades al exportar y al importar |
| Script viejo que falla en Blender 4.2 o 5.x | Cambió la API (EEVEE, add-ons pasados a extensiones) | Consultar el manual de la API de la versión instalada |

## Verificación

```
blender -b --factory-startup -P inspeccionar_escena.py -- demo
blender -b --factory-startup -P vistas_ortogonales.py -- demo CARPETA
```

Los dos tienen que terminar en `DEMO OK`: el primero arma una escena con fallas conocidas (escala sin aplicar con bisel, vértice suelto, textura faltante, sin cámara) y las encuentra todas; el segundo renderiza tres sólidos y comprueba la caja (3,2 × 2,0 × 3,5). Probado con Blender 5.2.3.

Ver también **conectar-programas-cad** (cómo conectar Claude con Blender) y **video-calidad** (revisar el video de un render o recorrido).
