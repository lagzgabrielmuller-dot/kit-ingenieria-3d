"""inspeccionar_escena.py - revisa una escena de Blender y devuelve un informe (texto y JSON).

Mide cada objeto en milimetros, avisa escala sin aplicar, modificadores, geometria con errores (aristas con mas de
dos caras, vertices sueltos o repetidos, normales invertidas), materiales e imagenes faltantes, camara, luces y render.

Uso en segundo plano (Windows: llamarlo con cmd /c para que PowerShell no se coma el --):
  blender -b archivo.blend -P inspeccionar_escena.py -- [informe.json] [--solo COLECCION]
  blender -b --factory-startup -P inspeccionar_escena.py -- demo
Dentro de una sesion (por ejemplo, ejecutando codigo por MCP):
  ns = {'__name__': 'inspeccion'}; exec(open(RUTA, encoding='utf-8').read(), ns); informe = ns['inspeccionar']()
Sale con codigo 1 si hay errores (solo en segundo plano). Probado con Blender 5.2.3.
"""
import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

MOD_SENSIBLES_A_ESCALA = {'BEVEL', 'SOLIDIFY', 'ARRAY', 'BOOLEAN', 'SCREW', 'WELD', 'REMESH', 'DISPLACE', 'WIREFRAME'}


def _mm(escena):
    """Factor de unidades de Blender a milimetros."""
    us = escena.unit_settings
    return (us.scale_length if us.system != 'NONE' else 1.0) * 1000.0


def _caja_mundo(obj, dg):
    ev = obj.evaluated_get(dg)
    pts = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def _geometria(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    r = {
        'vertices': len(bm.verts), 'caras': len(bm.faces),
        'aristas_mas_de_2_caras': sum(1 for e in bm.edges if len(e.link_faces) > 2),
        'bordes_abiertos': sum(1 for e in bm.edges if len(e.link_faces) == 1),
        'aristas_sueltas': sum(1 for e in bm.edges if not e.link_faces),
        'vertices_sueltos': sum(1 for v in bm.verts if not v.link_edges),
        'normales_inconsistentes': sum(1 for e in bm.edges if e.is_manifold and not e.is_contiguous),
        'caras_area_cero': sum(1 for f in bm.faces if f.calc_area() < 1e-12),
        'ngonos': sum(1 for f in bm.faces if len(f.verts) > 4),
    }
    try:
        r['vertices_repetidos'] = len(bmesh.ops.find_doubles(bm, verts=bm.verts, dist=1e-6)['targetmap'])
    except Exception:
        r['vertices_repetidos'] = None
    bm.free()
    return r


def inspeccionar(solo=None):
    esc = bpy.context.scene
    dg = bpy.context.evaluated_depsgraph_get()
    f = _mm(esc)
    us = esc.unit_settings
    hall = []

    def h(nivel, objeto, msg):
        hall.append({'nivel': nivel, 'objeto': objeto, 'mensaje': msg})

    objetos = list(esc.objects)
    if solo:
        col = bpy.data.collections.get(solo)
        objetos = list(col.all_objects) if col else []
        if not col:
            h('ERROR', None, 'No existe la coleccion %s.' % solo)
    datos_obj = []
    for ob in objetos:
        d = {'nombre': ob.name, 'tipo': ob.type, 'coleccion': ob.users_collection[0].name if ob.users_collection else None,
             'visible_render': not ob.hide_render}
        if ob.type == 'MESH':
            lo, hi = _caja_mundo(ob, dg)
            d['medidas_mm'] = [round(v * f, 3) for v in ob.dimensions]
            d['caja_mundo_mm'] = {'min': [round(v * f, 3) for v in lo], 'max': [round(v * f, 3) for v in hi]}
            d['escala'] = [round(v, 5) for v in ob.scale]
            d['rotacion_grados'] = [round(math.degrees(v), 3) for v in ob.rotation_euler]
            d['modificadores'] = [m.type for m in ob.modifiers]
            d['materiales'] = [s.material.name if s.material else None for s in ob.material_slots]
            g = _geometria(ob.data)
            d['geometria'] = g
            if any(s < 0 for s in ob.scale):
                h('AVISO', ob.name, 'Escala negativa %s: invierte las normales al exportar. Aplicar escala (Ctrl+A) y revisar normales.' % d['escala'])
            if any(abs(s - 1) > 1e-6 for s in ob.scale):
                sens = MOD_SENSIBLES_A_ESCALA.intersection(d['modificadores'])
                if sens:
                    h('AVISO', ob.name, 'Escala sin aplicar %s con %s: el bisel, el espesor o el arreglo salen deformados. Aplicar escala antes.' % (d['escala'], ', '.join(sorted(sens))))
                else:
                    h('NOTA', ob.name, 'Escala sin aplicar %s (aplicarla antes de exportar o de agregar biseles).' % d['escala'])
            if g['aristas_mas_de_2_caras']:
                h('AVISO', ob.name, '%d aristas compartidas por mas de dos caras (geometria imposible para imprimir o para booleanos).' % g['aristas_mas_de_2_caras'])
            if g['vertices_sueltos'] or g['aristas_sueltas']:
                h('AVISO', ob.name, '%d vertices y %d aristas sueltos (sin caras).' % (g['vertices_sueltos'], g['aristas_sueltas']))
            if g['vertices_repetidos']:
                h('AVISO', ob.name, '%d vertices repetidos en el mismo lugar (Merge by Distance).' % g['vertices_repetidos'])
            if g['normales_inconsistentes']:
                h('AVISO', ob.name, '%d aristas con normales invertidas entre caras vecinas (Recalculate Outside).' % g['normales_inconsistentes'])
            if g['caras_area_cero']:
                h('AVISO', ob.name, '%d caras de area cero.' % g['caras_area_cero'])
            if g['bordes_abiertos'] and 'SOLIDIFY' not in d['modificadores']:
                h('NOTA', ob.name, '%d bordes abiertos: no es un solido cerrado (importa para imprimir en 3D o exportar a CAD).' % g['bordes_abiertos'])
            if any(m is None for m in d['materiales']):
                h('AVISO', ob.name, 'Tiene ranuras de material vacias.')
            elif not d['materiales'] and not ob.hide_render:
                h('NOTA', ob.name, 'Sin material (sale gris en el render).')
            centro = (lo + hi) / 2
            tam = max((hi - lo).length, 1e-9)
            if (ob.matrix_world.translation - centro).length > 0.75 * tam:
                h('NOTA', ob.name, 'El origen esta lejos de la pieza: rota y escala alrededor de otro punto.')
            if ob.hide_get() and not ob.hide_render:
                h('NOTA', ob.name, 'Oculto en la vista pero sale en el render.')
        elif ob.type == 'LIGHT':
            d['luz'] = {'tipo': ob.data.type, 'energia': ob.data.energy}
        elif ob.type == 'CAMERA':
            d['camara'] = {'tipo': ob.data.type, 'lente_mm': ob.data.lens, 'escala_orto': ob.data.ortho_scale}
        datos_obj.append(d)
    # imagenes
    faltan = []
    for im in bpy.data.images:
        if im.source in ('FILE', 'SEQUENCE', 'TILED') and not im.packed_file and im.filepath:
            if not os.path.exists(bpy.path.abspath(im.filepath)):
                faltan.append(im.filepath)
    for p in faltan:
        h('ERROR', None, 'Imagen faltante: %s (sale rosa en el render).' % p)
    # escena
    r = esc.render
    if esc.camera is None:
        h('AVISO', None, 'La escena no tiene camara activa: el render falla.')
    luces = [o for o in esc.objects if o.type == 'LIGHT' and not o.hide_render]
    mundo = esc.world
    fuerza_mundo = None
    if mundo and getattr(mundo, 'use_nodes', True) and mundo.node_tree:
        bg = next((n for n in mundo.node_tree.nodes if n.type == 'BACKGROUND'), None)
        if bg:
            fuerza_mundo = bg.inputs['Strength'].default_value
    if not luces and (fuerza_mundo is not None and fuerza_mundo <= 0):
        h('AVISO', None, 'Escena sin luces y con el mundo apagado: el render sale negro.')
    if us.system == 'NONE':
        h('NOTA', None, 'Unidades en "None": se asume 1 unidad = 1 m. Para piezas, usar Metric con milimetros.')
    if r.engine == 'CYCLES':
        try:
            disp = esc.cycles.device
            if disp == 'CPU':
                h('NOTA', None, 'Cycles en CPU: con placa NVIDIA conviene GPU (OptiX).')
        except AttributeError:
            pass
    escena = {
        'archivo': bpy.data.filepath or '(sin guardar)', 'blender': bpy.app.version_string,
        'unidades': {'sistema': us.system, 'escala': us.scale_length, 'longitud': us.length_unit, 'factor_mm': f},
        'render': {'motor': r.engine, 'resolucion': [r.resolution_x, r.resolution_y, r.resolution_percentage],
                   'fps': round(r.fps / r.fps_base, 3), 'cuadros': [esc.frame_start, esc.frame_end],
                   'salida': r.filepath, 'camara': esc.camera.name if esc.camera else None},
        'luces': len(luces), 'fuerza_mundo': fuerza_mundo, 'imagenes_faltantes': faltan,
    }
    errores = sum(1 for x in hall if x['nivel'] == 'ERROR')
    avisos = sum(1 for x in hall if x['nivel'] == 'AVISO')
    return {'escena': escena, 'objetos': datos_obj, 'hallazgos': hall, 'errores': errores, 'avisos': avisos}


def texto(inf):
    e = inf['escena']
    lin = ['Escena: %s (Blender %s)' % (e['archivo'], e['blender']),
           'Unidades: %s, escala %s, %s (1 unidad = %g mm)' % (e['unidades']['sistema'], e['unidades']['escala'], e['unidades']['longitud'], e['unidades']['factor_mm']),
           'Render: %s %sx%s al %s%%, %s cuadros/s, cuadros %s-%s, camara %s' % (e['render']['motor'], *e['render']['resolucion'], e['render']['fps'], *e['render']['cuadros'], e['render']['camara']),
           '', 'Objetos de malla (medidas en mm, ancho x profundidad x alto):']
    for o in inf['objetos']:
        if o['tipo'] == 'MESH':
            g = o['geometria']
            lin.append('  %-28s %10.2f x %10.2f x %10.2f  %6d caras  esc %s  mods %s' % (
                o['nombre'][:28], *o['medidas_mm'], g['caras'], o['escala'], ','.join(o['modificadores']) or '-'))
    lin += ['', 'Hallazgos: %d errores, %d avisos' % (inf['errores'], inf['avisos'])]
    for x in inf['hallazgos']:
        lin.append('  [%s] %s%s' % (x['nivel'], (x['objeto'] + ': ') if x['objeto'] else '', x['mensaje']))
    return '\n'.join(lin)


def demo():
    """Escena con fallas conocidas: el informe tiene que encontrarlas todas."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    esc = bpy.context.scene
    esc.unit_settings.system = 'METRIC'
    esc.unit_settings.length_unit = 'MILLIMETERS'
    bpy.ops.mesh.primitive_cube_add(size=0.1)  # 100 mm
    cubo = bpy.context.active_object
    cubo.name = 'Cubo_escalado'
    cubo.scale = (2.0, 1.0, 0.5)
    cubo.modifiers.new('Bisel', 'BEVEL')
    me = bpy.data.meshes.new('con_suelto')
    me.from_pydata([(0, 0, 0), (0.05, 0, 0), (0, 0.05, 0), (0.3, 0.3, 0.3)], [], [(0, 1, 2)])
    ob = bpy.data.objects.new('Triangulo_con_vertice_suelto', me)
    esc.collection.objects.link(ob)
    img = bpy.data.images.new('falta', 4, 4)
    img.source = 'FILE'
    img.filepath = '//no_existe_textura.png'
    inf = inspeccionar()
    print(texto(inf))
    nombres = ' '.join(x['mensaje'] for x in inf['hallazgos'])
    cubo_mm = next(o for o in inf['objetos'] if o['nombre'] == 'Cubo_escalado')['medidas_mm']
    ok = (abs(cubo_mm[0] - 200) < 0.01 and abs(cubo_mm[2] - 50) < 0.01 and 'BEVEL' in nombres
          and 'vertices y' in nombres and 'Imagen faltante' in nombres and 'camara' in nombres)
    print('DEMO %s' % ('OK' if ok else 'FALLO'))
    return ok


def main():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if args and args[0] == 'demo':
        ok = demo()
        sys.exit(0 if ok else 1)
    solo = None
    if '--solo' in args:
        i = args.index('--solo')
        solo = args[i + 1] if i + 1 < len(args) else None
        args = args[:i] + args[i + 2:]
    inf = inspeccionar(solo)
    print(texto(inf))
    if args:
        with open(args[0], 'w', encoding='utf-8') as fh:
            json.dump(inf, fh, ensure_ascii=False, indent=1)
        print('Informe JSON en', args[0])
    if bpy.app.background:
        sys.exit(1 if inf['errores'] else 0)


if __name__ == '__main__':
    main()
