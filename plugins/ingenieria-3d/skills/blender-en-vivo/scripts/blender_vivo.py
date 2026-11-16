"""Blender en vivo: corre ADENTRO de Blender y ejecuta, de a uno, los .py que aparecen en una cola.

Lo arranca `vivo.py iniciar`, que abre Blender así:

    blender [escena.blend] --python blender_vivo.py -- --base CARPETA

También se puede cargar en un Blender ya abierto (Scripting > Run Script) o con exec()
desde otro script; en ese caso la carpeta sale de la variable BLENDER_VIVO_BASE o es
~/blender_vivo.

Carpeta base:
    cola/       los pasos a ejecutar (.py); se ejecutan en orden alfabético
    hechos/     cada paso, después de ejecutarse (con fecha y hora delante)
    capturas/   las capturas de la vista 3D
    blender.log una línea por evento: "inicio X", "ok X", "ERROR X" + traceback, "captura RUTA"

En cada paso quedan disponibles: bpy, BASE, VENTANA, AREA y REGION (la primera vista 3D),
log(texto) y captura(nombre, demora=6.0).

Seguridad: todo .py que aparezca en cola/ se ejecuta con los permisos del usuario.
La carpeta base tiene que ser privada (no compartida ni sincronizada con otros).
"""
import glob
import os
import sys
import time
import traceback

import bpy

ESPERA = 0.4      # s sin cambios antes de ejecutar un archivo (que termine de escribirse)


def _carpeta_base():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if '--base' in argv and argv.index('--base') + 1 < len(argv):
        return argv[argv.index('--base') + 1]
    return os.environ.get('BLENDER_VIVO_BASE') or os.path.join(os.path.expanduser('~'), 'blender_vivo')


BASE = os.path.abspath(_carpeta_base())
COLA = os.path.join(BASE, 'cola')
HECHOS = os.path.join(BASE, 'hechos')
CAPTURAS = os.path.join(BASE, 'capturas')
LOG = os.path.join(BASE, 'blender.log')
for _d in (COLA, HECHOS, CAPTURAS):
    os.makedirs(_d, exist_ok=True)


def log(texto):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(time.strftime('%H:%M:%S ') + str(texto) + '\n')


def vista3d():
    """(ventana, área, región) de la primera vista 3D abierta, o (None, None, None)."""
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type == 'VIEW_3D':
                r = next((x for x in a.regions if x.type == 'WINDOW'), None)
                return w, a, r
    return None, None, None


def captura(nombre, demora=6.0):
    """Guarda en capturas/ lo que muestra la vista 3D dentro de `demora` segundos.

    La demora deja que EEVEE compile los materiales y acumule muestras; con 5 a 10 s
    alcanza en una placa de video común. Devuelve la ruta que va a tener la imagen.
    """
    destino = os.path.join(CAPTURAS, nombre if nombre.lower().endswith('.png') else nombre + '.png')

    def _sacar():
        w, a, r = vista3d()
        if a is None:
            log('ERROR captura %s: no hay vista 3D abierta' % nombre)
            return None
        try:
            with bpy.context.temp_override(window=w, screen=w.screen, area=a, region=r):
                bpy.ops.screen.screenshot_area(filepath=destino)
            log('captura ' + destino)
        except Exception as e:  # noqa: BLE001 - se informa en el log
            log('ERROR captura %s: %s' % (nombre, e))
        return None

    bpy.app.timers.register(_sacar, first_interval=max(0.1, float(demora)))
    return destino


def _tick():
    try:
        for ruta in sorted(glob.glob(os.path.join(COLA, '*.py'))):
            if time.time() - os.path.getmtime(ruta) < ESPERA:
                continue
            nombre = os.path.basename(ruta)
            try:
                with open(ruta, encoding='utf-8') as f:
                    codigo = f.read()
                w, a, r = vista3d()
                entorno = {'bpy': bpy, '__name__': '__vivo__', 'BASE': BASE, 'VENTANA': w,
                           'AREA': a, 'REGION': r, 'log': log, 'captura': captura}
                log('inicio ' + nombre)
                exec(compile(codigo, nombre, 'exec'), entorno)
                log('ok ' + nombre)
            except Exception:  # noqa: BLE001 - el error va al log y la cola sigue
                log('ERROR ' + nombre + '\n' + traceback.format_exc().rstrip())
            os.replace(ruta, os.path.join(HECHOS, time.strftime('%Y%m%d-%H%M%S_') + nombre))
            return 0.2
    except Exception:  # noqa: BLE001 - un error acá no puede apagar el temporizador
        log('ERROR en la cola\n' + traceback.format_exc().rstrip())
    return ESPERA


_viejo = bpy.app.driver_namespace.get('blender_vivo_tick')
if _viejo is not None and bpy.app.timers.is_registered(_viejo):
    bpy.app.timers.unregister(_viejo)
bpy.app.driver_namespace['blender_vivo_tick'] = _tick
bpy.app.timers.register(_tick, first_interval=1.0, persistent=True)
log('listo (Blender %s) base=%s' % (bpy.app.version_string, BASE))
