"""vistas_ortogonales.py - renderiza frente, lateral derecha, planta e isometrica y arma una hoja de 2 x 2.

Sirve para que Claude (o cualquiera) controle la forma de un modelo mirando una sola imagen, sin tocar la escena:
crea camaras temporales con encuadre automatico, renderiza con Workbench (rapido, sin placa) y deja todo como estaba.

Uso en segundo plano (Windows: llamarlo con cmd /c para que PowerShell no se coma el --):
  blender -b archivo.blend -P vistas_ortogonales.py -- CARPETA [--tam 700] [--solo COLECCION] [--color material|objeto|aleatorio]
  blender -b --factory-startup -P vistas_ortogonales.py -- demo CARPETA
Dentro de una sesion (por ejemplo, ejecutando codigo por MCP):
  ns = {'__name__': 'vistas'}; exec(open(RUTA, encoding='utf-8').read(), ns); ns['vistas']('C:/carpeta')
Deja frente.png, derecha.png, planta.png, iso.png y hoja_vistas.png (arriba: frente | derecha; abajo: planta | iso).
Probado con Blender 5.2.3.
"""
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

VISTAS = [  # nombre, direccion desde el centro hacia la camara
    ('frente', Vector((0, -1, 0))),
    ('derecha', Vector((1, 0, 0))),
    ('planta', Vector((0, 0, 1))),
    ('iso', Vector((1, -1, 1)).normalized()),
]


def _caja(objetos, dg):
    pts = []
    for ob in objetos:
        ev = ob.evaluated_get(dg)
        pts += [ev.matrix_world @ Vector(c) for c in ev.bound_box]
    if not pts:
        return Vector((-1, -1, -1)), Vector((1, 1, 1))
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def vistas(carpeta, tam=700, solo=None, color='material'):
    esc = bpy.context.scene
    dg = bpy.context.evaluated_depsgraph_get()
    os.makedirs(carpeta, exist_ok=True)
    if solo and bpy.data.collections.get(solo):
        objetos = [o for o in bpy.data.collections[solo].all_objects if o.type in ('MESH', 'CURVE', 'FONT', 'SURFACE', 'META')]
    else:
        objetos = [o for o in esc.objects if o.type in ('MESH', 'CURVE', 'FONT', 'SURFACE', 'META') and not o.hide_render]
    lo, hi = _caja(objetos, dg)
    centro = (lo + hi) / 2
    diag = max((hi - lo).length, 1e-6)
    r, sh = esc.render, esc.display.shading
    guardado = dict(engine=r.engine, rx=r.resolution_x, ry=r.resolution_y, rp=r.resolution_percentage,
                    path=r.filepath, cam=esc.camera, fmt=r.image_settings.file_format, transp=r.film_transparent,
                    light=sh.light, ctype=sh.color_type, outline=sh.show_object_outline, cavity=sh.show_cavity)
    cam_data = bpy.data.cameras.new('_vista_tmp')
    cam = bpy.data.objects.new('_vista_tmp', cam_data)
    esc.collection.objects.link(cam)
    archivos = []
    try:
        r.engine = 'BLENDER_WORKBENCH'
        r.resolution_x = r.resolution_y = tam
        r.resolution_percentage = 100
        r.image_settings.file_format = 'PNG'
        r.film_transparent = False
        sh.light = 'STUDIO'
        sh.color_type = {'material': 'MATERIAL', 'objeto': 'OBJECT', 'aleatorio': 'RANDOM'}.get(color, 'MATERIAL')
        sh.show_object_outline = True
        sh.show_cavity = True
        esc.camera = cam
        cam_data.type = 'ORTHO'
        cam_data.ortho_scale = diag * 1.08
        cam_data.clip_start = diag * 0.01
        cam_data.clip_end = diag * 10
        for nombre, d in VISTAS:
            cam.location = centro + d * diag * 2.5
            cam.rotation_euler = (centro - cam.location).to_track_quat('-Z', 'Y').to_euler()
            if nombre == 'planta':
                cam.rotation_euler = (0.0, 0.0, 0.0)
            dg.update()
            ruta = os.path.join(carpeta, nombre + '.png')
            r.filepath = ruta
            bpy.ops.render.render(write_still=True)
            archivos.append(ruta)
    finally:
        r.engine, r.resolution_x, r.resolution_y = guardado['engine'], guardado['rx'], guardado['ry']
        r.resolution_percentage, r.filepath = guardado['rp'], guardado['path']
        r.image_settings.file_format, r.film_transparent = guardado['fmt'], guardado['transp']
        sh.light, sh.color_type = guardado['light'], guardado['ctype']
        sh.show_object_outline, sh.show_cavity = guardado['outline'], guardado['cavity']
        esc.camera = guardado['cam']
        bpy.data.objects.remove(cam, do_unlink=True)
        bpy.data.cameras.remove(cam_data)
    hoja = _hoja(archivos, os.path.join(carpeta, 'hoja_vistas.png'), tam)
    medidas = [round(v, 6) for v in (hi - lo)]
    print('Vistas listas en %s | caja total (unidades de Blender): %s' % (carpeta, medidas))
    return {'vistas': archivos, 'hoja': hoja, 'caja': medidas}


def _hoja(archivos, salida, tam):
    """Junta las 4 vistas en una imagen de 2 x 2 (las imagenes de Blender empiezan abajo a la izquierda)."""
    sep = 6
    W = H = 2 * tam + sep
    lienzo = np.full((H, W, 4), 0.08, dtype=np.float32)
    lienzo[..., 3] = 1.0
    pos = {0: (1, 0), 1: (1, 1), 2: (0, 0), 3: (0, 1)}  # (fila desde abajo, columna)
    for i, ruta in enumerate(archivos):
        im = bpy.data.images.load(ruta, check_existing=False)
        w, h = im.size
        px = np.empty(w * h * 4, dtype=np.float32)
        im.pixels.foreach_get(px)
        px = px.reshape(h, w, 4)
        fila, col = pos[i]
        y0, x0 = fila * (tam + sep), col * (tam + sep)
        lienzo[y0:y0 + h, x0:x0 + w] = px[:tam, :tam]
        bpy.data.images.remove(im)
    img = bpy.data.images.new('_hoja_vistas', W, H, alpha=True)
    img.pixels.foreach_set(lienzo.ravel())
    img.filepath_raw = salida
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)
    return salida


def demo(carpeta):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=1.5, location=(0, 0, 2.75))
    bpy.ops.mesh.primitive_cone_add(radius1=0.6, depth=1, location=(1.6, 0, 0.5))
    res = vistas(carpeta, tam=400, color='aleatorio')
    ok = os.path.isfile(res['hoja']) and all(os.path.isfile(a) for a in res['vistas']) \
        and abs(res['caja'][2] - 3.5) < 1e-3 and abs(res['caja'][0] - 3.2) < 1e-3
    print('DEMO %s' % ('OK' if ok else 'FALLO'))
    return ok


def main():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if args and args[0] == 'demo':
        ok = demo(args[1] if len(args) > 1 else os.path.join(os.getcwd(), 'demo_vistas'))
        sys.exit(0 if ok else 1)
    if not args:
        print(__doc__)
        sys.exit(2)
    op = {'--tam': 700, '--solo': None, '--color': 'material'}
    i = 1
    while i < len(args):
        if args[i] in op and i + 1 < len(args):
            op[args[i]] = args[i + 1]
            i += 2
        else:
            i += 1
    vistas(args[0], tam=int(op['--tam']), solo=op['--solo'], color=op['--color'])


if __name__ == '__main__':
    main()
