# Recetas probadas para Blender en vivo

Probadas en Blender 5.2.3 (EEVEE) con `blender_vivo.py`. Cada bloque es un paso que se puede mandar con `vivo.py enviar`; dentro del paso ya existen `bpy`, `log`, `captura`, `VENTANA`, `AREA` y `REGION`. Leer este archivo antes de armar un modelo con materiales emisivos, brillo, cortes o rótulos.

## 1. Vista limpia desde la cámara

```python
import bpy
esc = bpy.context.scene
centro = bpy.data.objects.get('Centro') or bpy.data.objects.new('Centro', None)
if centro.name not in esc.collection.objects:
    esc.collection.objects.link(centro)
cam = bpy.data.objects.new('Camara', bpy.data.cameras.new('Camara'))
esc.collection.objects.link(cam)
cam.data.lens = 50
cam.location = (0.0, -14.0, 0.6)
t = cam.constraints.new('TRACK_TO'); t.target = centro
t.track_axis = 'TRACK_NEGATIVE_Z'; t.up_axis = 'UP_Y'
esc.camera = cam
esc.render.engine = 'BLENDER_EEVEE'          # en 4.2 a 4.x era 'BLENDER_EEVEE_NEXT'
esc.render.resolution_x, esc.render.resolution_y = 1920, 1080
sp = AREA.spaces.active
sp.shading.type = 'RENDERED'
sp.overlay.show_overlays = False              # sin grilla, ejes ni textos
sp.show_gizmo = False
sp.region_3d.view_perspective = 'CAMERA'
with bpy.context.temp_override(window=VENTANA, screen=VENTANA.screen, area=AREA, region=REGION):
    bpy.ops.view3d.view_center_camera()
captura('paso01')
```

- Una cámara con restricción *Track To* hacia un vacío en el centro permite moverla sin recalcular giros.
- Con 50 mm y la cámara a 14 m, una esfera de 2 m de radio ocupa cerca del 70 % del alto del cuadro.

## 2. Material emisivo animado (superficie con celdas)

```python
mat = bpy.data.materials.new('Superficie'); mat.use_nodes = True
nt = mat.node_tree; nt.nodes.clear(); N, L = nt.nodes.new, nt.links.new
co = N('ShaderNodeTexCoord')
ru = N('ShaderNodeTexNoise'); ru.noise_dimensions = '4D'; ru.inputs['Scale'].default_value = 3.2
vo = N('ShaderNodeTexVoronoi'); vo.voronoi_dimensions = '4D'; vo.feature = 'DISTANCE_TO_EDGE'
vo.inputs['Scale'].default_value = 22.0
L(co.outputs['Object'], ru.inputs['Vector']); L(co.outputs['Object'], vo.inputs['Vector'])
for nodo, div in ((ru, 240), (vo, 90)):            # animación sin keyframes
    fc = nodo.inputs['W'].driver_add('default_value'); fc.driver.expression = 'frame / %d' % div
mx = N('ShaderNodeMath'); mx.operation = 'MULTIPLY_ADD'; mx.inputs[1].default_value = 0.75
L(ru.outputs['Fac'], mx.inputs[0]); L(vo.outputs['Distance'], mx.inputs[2])
rampa = N('ShaderNodeValToRGB')                    # colores de oscuro a claro
rampa.color_ramp.elements[0].color = (0.30, 0.03, 0.0, 1); rampa.color_ramp.elements[1].color = (1.0, 0.95, 0.8, 1)
L(mx.outputs[0], rampa.inputs['Fac'])
borde = N('ShaderNodeLayerWeight')                 # Facing: 0 en el centro, 1 en el borde
limbo = N('ShaderNodeValToRGB')
limbo.color_ramp.elements[1].color = (0.25, 0.11, 0.04, 1)
L(borde.outputs['Facing'], limbo.inputs['Fac'])
mul = N('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1
L(rampa.outputs['Color'], mul.inputs[6]); L(limbo.outputs['Color'], mul.inputs[7])
em = N('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.35
L(mul.outputs[2], em.inputs['Color'])
L(em.outputs[0], N('ShaderNodeOutputMaterial').inputs['Surface'])
```

- Un driver con expresión simple (`frame / 240`) anima sin habilitar la ejecución automática de scripts.
- En `ShaderNodeMix` del tipo RGBA, las entradas de color son la 6 (A) y la 7 (B), y la salida de color es la 2.
- Emisión entre 1 y 1,5 conserva el color con la transformada de vista AgX; con más, el color se va a blanco.

## 3. Halo que siempre mira a la cámara

```python
import bmesh
me = bpy.data.meshes.new('HaloMalla'); bm = bmesh.new()
bm.faces.new([bm.verts.new(c) for c in ((-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0))])
bm.to_mesh(me); bm.free()
halo = bpy.data.objects.new('Halo', me); bpy.context.scene.collection.objects.link(halo)
halo.scale = (5, 5, 5)                             # radio del halo
c = halo.constraints.new('TRACK_TO'); c.target = bpy.context.scene.camera
c.track_axis = 'TRACK_Z'; c.up_axis = 'UP_Y'
m = bpy.data.materials.new('Halo'); m.use_nodes = True
m.surface_render_method = 'BLENDED'; m.use_backface_culling = False
```

- Material: `Gradient Texture` esférico con coordenadas de objeto, elevado a la potencia 5,5 y multiplicado por 6 a 8, como fuerza de una emisión que se suma (`Add Shader`) a un `Transparent BSDF`.
- Rayos irregulares: ruido sobre la dirección normalizada `(x, y)`. Así no aparece la costura que deja `atan2`.
- Cada vez que cambia la cámara activa, cambiar también el destino de la restricción.

## 4. Brillo en el compositor (Blender 5.x)

```python
esc = bpy.context.scene
ng = bpy.data.node_groups.new('Brillo', 'CompositorNodeTree')
esc.compositing_node_group = ng                    # en 4.x: esc.use_nodes = True y esc.node_tree
ng.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
rl = ng.nodes.new('CompositorNodeRLayers'); gl = ng.nodes.new('CompositorNodeGlare')
out = ng.nodes.new('NodeGroupOutput')
gl.inputs['Type'].default_value = 'Bloom'          # en 5.x el tipo es una entrada, no gl.glare_type
for k, v in (('Threshold', 1.0), ('Strength', 0.35), ('Size', 0.5)):
    gl.inputs[k].default_value = v
ng.links.new(rl.outputs['Image'], gl.inputs['Image']); ng.links.new(gl.outputs['Image'], out.inputs[0])
AREA.spaces.active.shading.use_compositor = 'ALWAYS'   # el brillo también en la vista 3D
```

## 5. Corte con booleanos y caras de corte de otro color

```python
from mathutils import Euler
def restar(ob, cortadores):
    for c in cortadores:
        md = ob.modifiers.new('Resta', 'BOOLEAN'); md.operation = 'DIFFERENCE'
        md.solver = 'EXACT'; md.object = c
    dg = bpy.context.evaluated_depsgraph_get(); dg.update()
    nueva = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))   # aplica sin operadores
    ob.modifiers.clear(); vieja = ob.data; ob.data = nueva; bpy.data.meshes.remove(vieja)
```

- Cortador de un octante: cubo de 3 m de lado con centro en (1,5; −1,5; 1,5), oculto con `hide_set(True)` y `hide_render = True`. Hay que borrarlo después de aplicar.
- Antes del booleano, girar la malla un ángulo mínimo para evitar caras coplanares: `bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Euler((0.011, 0.007, 0.013)).to_matrix())`.
- Capas huecas: cada capa es una esfera menos la esfera interior menos el octante. Si no se ahuecan, las caras de corte de las capas quedan superpuestas y parpadean.
- Caras de corte con otro material: después de aplicar, `p.material_index = 1` en los polígonos con `min(abs(c.x), abs(c.y), abs(c.z)) < 1e-4`, donde `c = p.center`.

## 6. Etiquetas con línea guía

```python
from mathutils import Vector
cam = bpy.context.scene.camera
hacia_cam = cam.location.normalized(); f = -hacia_cam
der = f.cross(Vector((0, 0, 1))).normalized(); arr = der.cross(f).normalized()
def etiqueta(texto, lx, ly, destino, prof=3.5, tam=0.19):
    pos = der * lx + arr * ly + hacia_cam * prof     # por delante del objeto
    cu = bpy.data.curves.new('Txt_' + texto, 'FONT'); cu.body = texto; cu.size = tam
    cu.align_x = 'RIGHT' if lx < 0 else 'LEFT'; cu.align_y = 'CENTER'
    ob = bpy.data.objects.new('Txt_' + texto, cu); bpy.context.scene.collection.objects.link(ob)
    ob.location = pos + der * (-0.08 if lx < 0 else 0.08)
    k = ob.constraints.new('TRACK_TO'); k.target = cam; k.track_axis = 'TRACK_Z'; k.up_axis = 'UP_Y'
    lc = bpy.data.curves.new('Guia_' + texto, 'CURVE'); lc.dimensions = '3D'; lc.bevel_depth = 0.005
    sp = lc.splines.new('POLY'); sp.points.add(1)
    sp.points[0].co = (*pos, 1.0); sp.points[1].co = (*Vector(destino), 1.0)
    bpy.context.scene.collection.objects.link(bpy.data.objects.new('Guia_' + texto, lc))
```

- `lx` y `ly` están en el plano de la pantalla; con `prof = 3,5` y la cámara a 14 m, un valor entre 2,2 y 2,5 cae justo afuera de una esfera de 2 m.
- Elegir a mano la posición de cada rótulo para que no se superpongan. Calcularla desde el destino amontonó dos rótulos en el mismo lugar.
- La fuente de Blender incluye tildes y la eñe.

## 7. Render, captura y animación

```python
esc = bpy.context.scene
esc.render.filepath = r'C:/trabajo/figura1.png'
bpy.ops.render.render(write_still=True)           # congela la interfaz unos segundos
captura('despues_del_render')
esc.frame_start, esc.frame_end = 1, 240
for w in bpy.context.window_manager.windows:
    for a in w.screen.areas:
        if a.type == 'VIEW_3D':
            r = next(x for x in a.regions if x.type == 'WINDOW')
            with bpy.context.temp_override(window=w, screen=w.screen, area=a, region=r):
                if not bpy.context.screen.is_animation_playing:
                    bpy.ops.screen.animation_play()
bpy.ops.wm.save_mainfile(filepath=r'C:/trabajo/modelo.blend')
```

- Para mostrar dos estados del modelo (completo y en corte), conviene separarlos en dos colecciones y ocultar una con `view_layer.layer_collection.children['Corte'].hide_viewport = True`.

## Ejemplo completo: el Sol en 12 pasos

| Paso | Qué se ve | Valores que funcionaron |
|---|---|---|
| 1 | Cámara y vista en modo render | Receta 1 |
| 2 | Esfera con granulación animada | Esfera UV de 160 × 80 y radio 2; receta 2 |
| 3 | Corona y brillo | Halo de radio 5, potencia 5,5, fuerza 6,5; Glare con Bloom |
| 4 | Ajuste de color | El primer intento quedó lavado: emisión de 3 bajada a 1,35 |
| 5 | Manchas solares | Voronoi F1 de escala 2,6 sobre el 20 % de las celdas, con umbra y penumbra, solo con 0,25 m < \|z\| < 1,25 m |
| 6 | Cromosfera | Esfera de 1,016 R con emisión roja según Facing entre 0,90 y 0,97 |
| 7 | Protuberancias | Cinco hebras Bézier por arco, de grosor 0,014 m, emisión roja de 1,2 a 4,5 modulada con ruido |
| 8 | Figura 1 | Render 1920 × 1080 con 64 muestras |
| 9 | Corte | Zona convectiva (R − 0,7 R), radiativa (0,7 R − 0,25 R) y núcleo entero, con un octante quitado |
| 10 | Etiquetas | Receta 6, con la cámara del corte en (9,2; −9,2; 6,2) y 40 mm |
| 11 | Figura 2 | Render del corte |
| 12 | Cierre | Colecciones, animación y guardado (receta 7) |
