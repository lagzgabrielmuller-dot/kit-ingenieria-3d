"""estudio_turntable.py - render de presentacion de un modelo en Blender con un comando.

Arma un estudio (piso, fondo, tres luces de area escaladas al modelo), encuadra una camara, saca la foto principal
y un video girando 360 grados (turntable). El video sale en MP4 H.264 con color BT.709 etiquetado (ffmpeg).
No guarda el .blend: trabaja sobre lo abierto en memoria.

Uso en segundo plano (Windows: desde PowerShell con cmd /c para que no se coma el --):
  blender -b modelo.blend -P estudio_turntable.py -- SALIDA [opciones]
  blender -b --factory-startup -P estudio_turntable.py -- SALIDA --importar pieza.glb|.stl|.obj|.fbx [opciones]
  blender -b --factory-startup -P estudio_turntable.py -- demo SALIDA
Opciones:
  --segundos 8   --fps 30   --tam 1920x1080   --motor eevee|cycles   --muestras 64   --previa (mitad de tamano, 1 de cada 3 cuadros)
  --contorno (lineas Freestyle)   --solo COLECCION   --altura 20 (grados de la camara)   --sin-video (solo la foto)
Deja en SALIDA: foto.png, cuadros/0001.png..., turntable.mp4 y estudio.txt (lo que se uso). Probado con Blender 5.2.3.
"""
import math
import os
import shutil
import subprocess
import sys

import bpy
from mathutils import Vector

VF_709 = ('scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,'
          'setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv')
TIPOS = ('MESH', 'CURVE', 'FONT', 'SURFACE', 'META')


def opciones(args):
    op = {'--segundos': '8', '--fps': '30', '--tam': '1920x1080', '--motor': 'eevee', '--muestras': '64',
          '--solo': None, '--importar': None, '--altura': '20'}
    banderas = {a for a in args if a in ('--previa', '--contorno', '--sin-video')}
    i = 1
    while i < len(args):
        if args[i] in op and i + 1 < len(args):
            op[args[i]] = args[i + 1]
            i += 2
        else:
            i += 1
    return op, banderas


def importar(ruta):
    ext = os.path.splitext(ruta)[1].lower()
    antes = set(bpy.data.objects)
    if ext in ('.glb', '.gltf'):
        bpy.ops.import_scene.gltf(filepath=ruta)
    elif ext == '.stl':
        bpy.ops.wm.stl_import(filepath=ruta, global_scale=0.001)  # STL en mm -> metros
    elif ext == '.obj':
        bpy.ops.wm.obj_import(filepath=ruta)
    elif ext == '.fbx':
        bpy.ops.import_scene.fbx(filepath=ruta)
    else:
        raise SystemExit('Formato no soportado: %s (usar .blend, .glb, .stl, .obj o .fbx)' % ext)
    return [o for o in bpy.data.objects if o not in antes]


def caja(objetos):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in objetos:
        ev = ob.evaluated_get(dg)
        pts += [ev.matrix_world @ Vector(c) for c in ev.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def material(nombre, color, rugosidad=0.6):
    m = bpy.data.materials.new(nombre)
    if hasattr(m, 'use_nodes'):
        try:
            m.use_nodes = True
        except Exception:
            pass
    bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m.node_tree else None
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = rugosidad
    m.diffuse_color = (*color, 1.0)
    return m


def luz(nombre, tipo, energia, tam, pos, mirar):
    d = bpy.data.lights.new(nombre, tipo)
    d.energy = energia
    if tipo == 'AREA':
        d.size = tam
    ob = bpy.data.objects.new(nombre, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = pos
    ob.rotation_euler = (mirar - pos).to_track_quat('-Z', 'Y').to_euler()
    return ob


def armar_estudio(objetos, altura_grados=20.0, contorno=False):
    esc = bpy.context.scene
    lo, hi = caja(objetos)
    centro = (lo + hi) / 2
    radio = max((hi - lo).length / 2, 1e-3)
    col = bpy.data.collections.new('_estudio')
    esc.collection.children.link(col)
    # piso gris claro, grande, apoyado en la base del modelo
    bpy.ops.mesh.primitive_plane_add(size=radio * 40, location=(centro.x, centro.y, lo.z))
    piso = bpy.context.active_object
    piso.name = '_piso'
    piso.data.materials.append(material('_piso', (0.42, 0.42, 0.44), 0.85))
    for c in piso.users_collection:
        c.objects.unlink(piso)
    col.objects.link(piso)
    # fondo: el mundo del mismo gris, apenas iluminado
    mundo = esc.world or bpy.data.worlds.new('_mundo')
    esc.world = mundo
    if hasattr(mundo, 'use_nodes'):
        try:
            mundo.use_nodes = True
        except Exception:
            pass
    if mundo.node_tree:
        bg = next((n for n in mundo.node_tree.nodes if n.type == 'BACKGROUND'), None)
        if bg:
            bg.inputs['Color'].default_value = (0.45, 0.46, 0.48, 1.0)
            bg.inputs['Strength'].default_value = 0.2
    # tres luces de area (principal, relleno y contraluz), escaladas al tamano del modelo
    e = 320.0 * radio ** 2
    for nombre, energia, ang, alt in (('_luz_principal', e, -40, 1.1), ('_luz_relleno', e * 0.35, 55, 0.6), ('_contraluz', e * 0.6, 170, 1.4)):
        a = math.radians(ang)
        pos = centro + Vector((math.sin(a), -math.cos(a), 0)) * radio * 3.2 + Vector((0, 0, radio * 2.2 * alt))
        ob = luz(nombre, 'AREA', energia, radio * 2.0, pos, centro)
        for c in ob.users_collection:
            c.objects.unlink(ob)
        col.objects.link(ob)
    # camara de 50 mm en un pivote que gira
    piv = bpy.data.objects.new('_pivote', None)
    col.objects.link(piv)
    piv.location = centro
    cd = bpy.data.cameras.new('_camara')
    cd.lens = 50
    cam = bpy.data.objects.new('_camara', cd)
    col.objects.link(cam)
    r = esc.render
    aspecto = r.resolution_x / r.resolution_y
    ancho_sensor = cd.sensor_width
    if aspecto >= 1:
        fov_h = 2 * math.atan(ancho_sensor / (2 * cd.lens))
        fov_v = 2 * math.atan(math.tan(fov_h / 2) / aspecto)
    else:
        fov_v = 2 * math.atan(ancho_sensor / (2 * cd.lens))
        fov_h = 2 * math.atan(math.tan(fov_v / 2) * aspecto)
    radio_xy = max(((hi.x - lo.x) ** 2 + (hi.y - lo.y) ** 2) ** 0.5 / 2, 1e-3)  # no cambia al girar
    a = math.radians(altura_grados)
    medio_alto = (hi.z - lo.z) / 2 * math.cos(a) + radio_xy * math.sin(a)
    dist = max(radio_xy / math.tan(fov_h / 2), medio_alto / math.tan(fov_v / 2)) * 1.08 + radio_xy * 0.6
    cam.parent = piv
    cam.location = Vector((math.sin(math.radians(-35)), -math.cos(math.radians(-35)), 0)) * dist * math.cos(a) + Vector((0, 0, dist * math.sin(a)))
    cam.rotation_euler = (-cam.location).to_track_quat('-Z', 'Y').to_euler()
    cd.clip_start = dist * 0.01
    cd.clip_end = dist * 20
    esc.camera = cam
    if contorno:
        r.use_freestyle = True
        r.line_thickness_mode = 'ABSOLUTE'
        r.line_thickness = 1.4
    return piv, radio


def configurar_render(motor, muestras, ancho, alto):
    esc = bpy.context.scene
    r = esc.render
    r.resolution_x, r.resolution_y, r.resolution_percentage = ancho, alto, 100
    r.image_settings.file_format = 'PNG'
    r.image_settings.color_mode = 'RGB'
    for look in ('AgX - Punchy', 'Punchy', 'AgX - Medium High Contrast'):
        try:
            esc.view_settings.look = look
            break
        except TypeError:
            continue
    if motor == 'cycles':
        r.engine = 'CYCLES'
        try:
            p = bpy.context.preferences.addons['cycles'].preferences
            for tipo in ('OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI'):
                try:
                    p.compute_device_type = tipo
                    p.get_devices()
                    if any(d.type == tipo for d in p.devices):
                        for d in p.devices:
                            d.use = d.type == tipo
                        esc.cycles.device = 'GPU'
                        break
                except TypeError:
                    continue
        except KeyError:
            pass
        esc.cycles.samples = muestras
        esc.cycles.use_denoising = True
        return 'Cycles (%s), %d muestras' % (esc.cycles.device, muestras)
    for nombre in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
        try:
            r.engine = nombre
            break
        except TypeError:
            continue
    try:
        esc.eevee.taa_render_samples = muestras
        esc.eevee.use_raytracing = True
    except AttributeError:
        pass
    return '%s, %d muestras' % (r.engine, muestras)


def codificar(cuadros, fps, salida):
    ff = os.environ.get('FFMPEG') or shutil.which('ffmpeg')
    if not ff:
        return 'sin ffmpeg: quedan los cuadros PNG en %s' % cuadros
    r = subprocess.run([ff, '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(cuadros, '%04d.png'),
                        '-vf', VF_709, '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
                        '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
                        '-movflags', '+faststart', salida], capture_output=True)
    return salida if r.returncode == 0 else 'ffmpeg fallo: ' + r.stderr.decode('utf-8', 'replace')[-300:]


def presentar(salida, op, banderas, objetos=None):
    esc = bpy.context.scene
    os.makedirs(salida, exist_ok=True)
    if op['--importar']:
        objetos = importar(op['--importar'])
    if objetos is None:
        if op['--solo'] and bpy.data.collections.get(op['--solo']):
            objetos = [o for o in bpy.data.collections[op['--solo']].all_objects if o.type in TIPOS]
        else:
            objetos = [o for o in esc.objects if o.type in TIPOS and not o.hide_render]
    objetos = [o for o in objetos if o.type in TIPOS]
    if not objetos:
        raise SystemExit('No hay objetos para mostrar.')
    ancho, alto = (int(v) for v in op['--tam'].lower().split('x'))
    fps, seg = int(op['--fps']), float(op['--segundos'])
    previa = '--previa' in banderas
    if previa:
        ancho, alto = ancho // 2 // 2 * 2, alto // 2 // 2 * 2
    info_motor = configurar_render(op['--motor'], int(op['--muestras']) if not previa else max(8, int(op['--muestras']) // 4), ancho, alto)
    piv, radio = armar_estudio(objetos, float(op['--altura']), '--contorno' in banderas)
    total = max(2, int(round(fps * seg)))
    esc.frame_start, esc.frame_end = 1, total
    esc.render.fps, esc.render.fps_base = fps, 1
    drv = piv.driver_add('rotation_euler', 2).driver
    drv.type = 'SCRIPTED'
    drv.expression = '2*pi*(frame-1)/%d' % total
    # foto principal
    esc.frame_set(1)
    esc.render.filepath = os.path.join(salida, 'foto.png')
    bpy.ops.render.render(write_still=True)
    video = '(sin video)'
    if '--sin-video' not in banderas:
        cuadros = os.path.join(salida, 'cuadros')
        os.makedirs(cuadros, exist_ok=True)
        paso = 3 if previa else 1
        k = 0
        for f in range(1, total + 1, paso):
            esc.frame_set(f)
            k += 1
            esc.render.filepath = os.path.join(cuadros, '%04d.png' % k)
            bpy.ops.render.render(write_still=True)
        video = codificar(cuadros, max(1, round(fps / paso)), os.path.join(salida, 'turntable.mp4'))
    lo, hi = caja(objetos)
    resumen = ['Estudio de presentacion (%s)' % ('previa' if previa else 'final'),
               'Motor: %s | %dx%d | %d cuadros a %d cuadros/s (%.1f s)' % (info_motor, ancho, alto, total, fps, seg),
               'Objetos: %d | caja %.3f x %.3f x %.3f (unidades de Blender)' % (len(objetos), *(hi - lo)),
               'Foto: %s' % os.path.join(salida, 'foto.png'), 'Video: %s' % video]
    open(os.path.join(salida, 'estudio.txt'), 'w', encoding='utf-8').write('\n'.join(resumen) + '\n')
    print('\n'.join(resumen))
    return video


def demo(salida):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # una "maquina" simple: base, cuerpo cilindrico, motor y tolva
    piezas = [
        ('Base', lambda: bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.1), scale=(1.6, 0.9, 0.2)), (0.12, 0.13, 0.15)),
        ('Cuerpo', lambda: bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=1.4, location=(0, 0, 0.75), rotation=(0, math.pi / 2, 0)), (0.55, 0.04, 0.06)),
        ('Motor', lambda: bpy.ops.mesh.primitive_cube_add(size=0.35, location=(0.95, 0, 0.5)), (0.1, 0.18, 0.45)),
        ('Tolva', lambda: bpy.ops.mesh.primitive_cone_add(radius1=0.45, radius2=0.15, depth=0.5, location=(-0.4, 0, 1.25), rotation=(math.pi, 0, 0)), (0.6, 0.6, 0.58)),
    ]
    for nombre, crear, color in piezas:
        crear()
        ob = bpy.context.active_object
        ob.name = nombre
        ob.data.materials.append(material('m_' + nombre, color, 0.4))
    op, banderas = opciones(['demo', '--segundos', '4', '--fps', '24', '--tam', '1280x720', '--muestras', '32'])
    banderas.add('--previa')
    video = presentar(salida, op, banderas)
    ok = os.path.isfile(os.path.join(salida, 'foto.png')) and video.endswith('.mp4') and os.path.isfile(video)
    print('DEMO %s' % ('OK' if ok else 'FALLO: ' + video))
    return ok


def main():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if not args:
        print(__doc__)
        sys.exit(2)
    if args[0] == 'demo':
        sys.exit(0 if demo(args[1] if len(args) > 1 else os.path.join(os.getcwd(), 'demo_estudio')) else 1)
    op, banderas = opciones(args)
    presentar(args[0], op, banderas)


if __name__ == '__main__':
    main()
