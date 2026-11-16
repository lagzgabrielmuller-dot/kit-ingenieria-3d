#!/usr/bin/env python3
"""Controla un Blender abierto paso por paso, para que el usuario vea el modelo armándose.

Del lado de Blender corre blender_vivo.py (lo carga `iniciar`); este programa deja cada paso
en la cola, espera a que Blender lo ejecute y muestra el resultado del log.

    python vivo.py iniciar --blender RUTA\\blender.exe [--escena x.blend] [--base CARPETA]
                           [--ventana=X,Y,ANCHO,ALTO] [--maximizar]
    python vivo.py enviar paso.py            (o --codigo "bpy.ops.mesh.primitive_cube_add()")
    python vivo.py captura nombre [--demora 6]
    python vivo.py estado
    python vivo.py cerrar [--guardar modelo.blend]
    python vivo.py demo                      (prueba el protocolo sin Blender)

La carpeta base sale de --base, de la variable BLENDER_VIVO_BASE o es ~/blender_vivo.
Solo biblioteca estándar, Python 3.9 o más.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback

AQUI = os.path.dirname(os.path.abspath(__file__))
CORREDOR = os.path.join(AQUI, 'blender_vivo.py')


def carpeta_base(arg=None):
    base = arg or os.environ.get('BLENDER_VIVO_BASE') or os.path.join(os.path.expanduser('~'), 'blender_vivo')
    return os.path.abspath(base)


def rutas(base):
    return {'cola': os.path.join(base, 'cola'), 'hechos': os.path.join(base, 'hechos'),
            'capturas': os.path.join(base, 'capturas'), 'log': os.path.join(base, 'blender.log')}


def tam_log(base):
    try:
        return os.path.getsize(rutas(base)['log'])
    except OSError:
        return 0


def leer_desde(base, desde):
    try:
        with open(rutas(base)['log'], 'rb') as f:
            f.seek(desde)
            return f.read().decode('utf-8', 'replace')
    except OSError:
        return ''


# ---------------------------------------------------------------- enviar un paso

def poner_en_cola(base, codigo, nombre='paso'):
    """Escribe el paso en la cola de forma atómica y devuelve el nombre de archivo."""
    r = rutas(base)
    os.makedirs(r['cola'], exist_ok=True)
    limpio = ''.join(c if c.isalnum() or c in '-_' else '_' for c in os.path.splitext(os.path.basename(nombre))[0])
    archivo = '%013d_%s.py' % (int(time.time() * 1000), limpio or 'paso')
    tmp = os.path.join(r['cola'], '.' + archivo + '.part')
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(codigo)
    os.replace(tmp, os.path.join(r['cola'], archivo))
    return archivo


def esperar_resultado(base, archivo, desde, espera=120.0):
    """Espera la línea 'ok ARCHIVO' o 'ERROR ARCHIVO' en el log. Devuelve (ok, texto nuevo)."""
    limite = time.time() + espera
    while time.time() < limite:
        nuevo = leer_desde(base, desde)
        for linea in nuevo.splitlines():
            partes = linea.split(' ', 2)
            if len(partes) >= 3 and partes[2] == archivo and partes[1] in ('ok', 'ERROR'):
                return partes[1] == 'ok', nuevo
            if len(partes) >= 3 and partes[1] == 'ERROR' and partes[2].startswith(archivo):
                return False, nuevo
        time.sleep(0.25)
    return None, leer_desde(base, desde)


def enviar(base, codigo, nombre='paso', espera=120.0, mostrar=True):
    desde = tam_log(base)
    archivo = poner_en_cola(base, codigo, nombre)
    ok, texto = esperar_resultado(base, archivo, desde, espera)
    if mostrar:
        print(texto.rstrip() or '(el log no cambió)')
        if ok is None:
            print('Sin respuesta en %.0f s: ¿Blender está abierto con blender_vivo.py y la misma carpeta base?' % espera)
    return ok, archivo, texto


def pedir_captura(base, nombre, demora=6.0, espera=60.0):
    nombre_png = nombre if nombre.lower().endswith('.png') else nombre + '.png'
    destino = os.path.join(rutas(base)['capturas'], nombre_png)
    antes = os.path.getmtime(destino) if os.path.exists(destino) else 0.0
    ok, _, _ = enviar(base, 'captura(%r, demora=%r)\n' % (nombre_png, float(demora)), 'captura_' + nombre,
                      espera=espera, mostrar=False)
    if not ok:
        return None
    limite = time.time() + demora + espera
    while time.time() < limite:
        if os.path.exists(destino) and os.path.getmtime(destino) > antes and os.path.getsize(destino) > 0:
            time.sleep(0.3)
            return destino
        time.sleep(0.3)
    return None


# ---------------------------------------------------------------- abrir Blender

def mover_ventana(pid, x, y, ancho, alto, maximizar=False, espera=90.0):
    """Windows: lleva la ventana principal del proceso a un rectángulo (por ejemplo, otro monitor)."""
    if os.name != 'nt':
        return False
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    limite = time.time() + espera
    while time.time() < limite:
        halladas = []

        def cb(hwnd, _lp):
            p = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
            if p.value == pid and user32.IsWindowVisible(hwnd) and user32.GetWindowTextLengthW(hwnd) > 0:
                halladas.append(hwnd)
            return True

        user32.EnumWindows(proc(cb), 0)
        if halladas:
            hwnd = halladas[0]
            user32.ShowWindow(hwnd, 9)                       # SW_RESTORE
            user32.MoveWindow(hwnd, x, y, ancho, alto, True)
            if maximizar:
                user32.ShowWindow(hwnd, 3)                   # SW_MAXIMIZE, en el monitor donde quedó
            return True
        time.sleep(1.0)
    return False


def iniciar(args):
    base = carpeta_base(args.base)
    r = rutas(base)
    for d in ('cola', 'hechos', 'capturas'):
        os.makedirs(r[d], exist_ok=True)
    blender = args.blender or os.environ.get('BLENDER') or shutil.which('blender')
    if not blender or not os.path.exists(blender):
        print('No encuentro Blender: pasá --blender RUTA o definí la variable BLENDER.')
        return 2
    escena = args.escena
    if not escena:   # con un .blend en la línea de comandos Blender no muestra el cartel de bienvenida
        escena = os.path.join(base, 'inicio.blend')
        if not os.path.exists(escena):
            expr = 'import bpy; bpy.ops.wm.save_as_mainfile(filepath=%r)' % escena
            subprocess.run([blender, '-b', '--python-expr', expr], stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
        if not os.path.exists(escena):
            escena = None
    cmd = [blender] + ([escena] if escena else []) + ['--python', CORREDOR, '--', '--base', base]
    desde = tam_log(base)
    banderas = 0
    if os.name == 'nt':   # que Blender siga abierto aunque se cierre esta terminal
        banderas = 0x00000008 | 0x00000200 | 0x01000000   # DETACHED | NEW_PROCESS_GROUP | BREAKAWAY_FROM_JOB
    try:
        p = subprocess.Popen(cmd, creationflags=banderas, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=(os.name != 'nt'))
    except OSError:
        if os.name != 'nt':
            raise
        p = subprocess.Popen(cmd, creationflags=0x00000008 | 0x00000200, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(os.path.join(base, 'blender.pid'), 'w') as f:
        f.write(str(p.pid))
    print('Blender abierto (pid %d). Base: %s' % (p.pid, base))
    if args.ventana:
        x, y, an, al = (int(v) for v in args.ventana.split(','))
        print('ventana movida' if mover_ventana(p.pid, x, y, an, al, args.maximizar) else 'no pude mover la ventana')
    limite = time.time() + args.espera
    while time.time() < limite:
        if 'listo (Blender' in leer_desde(base, desde):
            print(leer_desde(base, desde).strip().splitlines()[-1])
            return 0
        if p.poll() is not None:
            print('Blender se cerró al arrancar (código %s).' % p.returncode)
            return 1
        time.sleep(0.5)
    print('Blender abrió pero el corredor no avisó "listo" en %.0f s: mirá %s' % (args.espera, r['log']))
    return 1


def proceso_vivo(pid):
    if os.name == 'nt':
        r = subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid, '/NH'], capture_output=True, text=True)
        return str(pid) in r.stdout
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def cerrar(args):
    base = carpeta_base(args.base)
    codigo = ''
    if args.guardar:
        codigo += 'bpy.ops.wm.save_as_mainfile(filepath=%r)\nlog(%r)\n' % (os.path.abspath(args.guardar), 'guardado ' + args.guardar)
    codigo += 'bpy.app.timers.register(lambda: bpy.ops.wm.quit_blender(), first_interval=0.5)\n'
    ok, _, _ = enviar(base, codigo, 'cerrar', 60)
    if not ok:
        return 1
    try:
        with open(os.path.join(base, 'blender.pid')) as f:
            pid = int(f.read().strip())
    except (OSError, ValueError):
        print('Blender recibió la orden de cerrar.')
        return 0
    limite = time.time() + 30
    while time.time() < limite and proceso_vivo(pid):
        time.sleep(0.5)
    vivo = proceso_vivo(pid)
    print('Blender sigue abierto (pid %d).' % pid if vivo else 'Blender cerrado.')
    return 1 if vivo else 0


def estado(args):
    base = carpeta_base(args.base)
    r = rutas(base)
    pendientes = sorted(x for x in os.listdir(r['cola']) if x.endswith('.py')) if os.path.isdir(r['cola']) else []
    print('Base: %s\nEn cola: %d %s' % (base, len(pendientes), ' '.join(pendientes)))
    try:
        with open(r['log'], encoding='utf-8', errors='replace') as f:
            lineas = f.read().splitlines()
        print('\n'.join(lineas[-args.lineas:]))
    except OSError:
        print('(todavía no hay log)')
    return 0


# ---------------------------------------------------------------- demo sin Blender

class CorredorSimulado(threading.Thread):
    """Imita a blender_vivo.py (mismo protocolo de cola y log) para probar sin Blender."""

    def __init__(self, base):
        super().__init__(daemon=True)
        self.base, self.r, self.parar = base, rutas(base), False

    def log(self, texto):
        with open(self.r['log'], 'a', encoding='utf-8') as f:
            f.write(time.strftime('%H:%M:%S ') + str(texto) + '\n')

    def captura(self, nombre, demora=6.0):
        destino = os.path.join(self.r['capturas'], nombre)

        def sacar():
            time.sleep(min(demora, 0.5))
            with open(destino, 'wb') as f:   # PNG mínimo de 1 x 1
                f.write(bytes.fromhex('89504e470d0a1a0a0000000d4948445200000001000000010806000000'
                                      '1f15c4890000000d49444154789c6300010000000500010d0a2db40000'
                                      '000049454e44ae426082'))
            self.log('captura ' + destino)
        threading.Thread(target=sacar, daemon=True).start()
        return destino

    def run(self):
        for d in ('cola', 'hechos', 'capturas'):
            os.makedirs(self.r[d], exist_ok=True)
        self.log('listo (simulado) base=' + self.base)
        while not self.parar:
            for nombre in sorted(x for x in os.listdir(self.r['cola']) if x.endswith('.py')):
                ruta = os.path.join(self.r['cola'], nombre)
                if time.time() - os.path.getmtime(ruta) < 0.2:
                    continue
                try:
                    with open(ruta, encoding='utf-8') as f:
                        codigo = f.read()
                    self.log('inicio ' + nombre)
                    exec(compile(codigo, nombre, 'exec'),
                         {'__name__': '__vivo__', 'log': self.log, 'captura': self.captura, 'BASE': self.base})
                    self.log('ok ' + nombre)
                except Exception:  # noqa: BLE001
                    self.log('ERROR ' + nombre + '\n' + traceback.format_exc().rstrip())
                os.replace(ruta, os.path.join(self.r['hechos'], time.strftime('%Y%m%d-%H%M%S_') + nombre))
            time.sleep(0.1)


def demo(_args):
    base = tempfile.mkdtemp(prefix='blender_vivo_demo_')
    corredor = CorredorSimulado(base)
    corredor.start()
    fallas = []
    try:
        ok, archivo, texto = enviar(base, "log('cubo de 2 m listo: volumen = %d m3' % (2 ** 3))\n", 'cubo', 10, False)
        print('1) paso correcto      ->', 'ok' if ok else 'FALLA', '|', archivo)
        if not (ok and 'volumen = 8 m3' in texto):
            fallas.append('el paso correcto no dio ok')
        ok, archivo, texto = enviar(base, "raise ValueError('radio negativo')\n", 'con_error', 10, False)
        print('2) paso con error     ->', 'ERROR detectado' if ok is False else 'FALLA', '|', archivo)
        if ok is not False or 'radio negativo' not in texto:
            fallas.append('el error no se detectó')
        img = pedir_captura(base, 'vista_demo', demora=0.2, espera=10)
        print('3) captura de la vista ->', img or 'FALLA')
        if not img or open(img, 'rb').read(4) != b'\x89PNG':
            fallas.append('la captura no apareció')
        hechos = os.listdir(rutas(base)['hechos'])
        print('4) pasos en hechos/    ->', len(hechos))
        if len(hechos) != 3:
            fallas.append('no se archivaron los 3 pasos')
        if os.listdir(rutas(base)['cola']):
            fallas.append('quedaron archivos en la cola')
    finally:
        corredor.parar = True
        corredor.join(2)
        shutil.rmtree(base, ignore_errors=True)
    if fallas:
        print('DEMO FALLÓ: ' + '; '.join(fallas))
        return 1
    print('DEMO OK')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='Blender en vivo: abrir Blender con la cola, enviar pasos, capturar la vista.')
    ap.add_argument('--base', help='carpeta de trabajo (cola, log y capturas); por defecto BLENDER_VIVO_BASE o ~/blender_vivo')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('iniciar', help='abrir Blender con el corredor de la cola')
    p.add_argument('--blender', help='ruta de blender.exe (o variable BLENDER)')
    p.add_argument('--escena', help='.blend a abrir')
    p.add_argument('--ventana', help='X,Y,ANCHO,ALTO para ubicar la ventana (Windows); con números negativos usar el signo =, p. ej. --ventana=-1920,0,1920,1080')
    p.add_argument('--maximizar', action='store_true', help='maximizar en el monitor donde quedó la ventana')
    p.add_argument('--espera', type=float, default=120.0, help='segundos para esperar el aviso "listo"')
    p = sub.add_parser('enviar', help='ejecutar un paso en Blender y mostrar el resultado')
    p.add_argument('archivo', nargs='?', help='.py con el paso')
    p.add_argument('--codigo', help='código Python en vez de un archivo')
    p.add_argument('--espera', type=float, default=180.0, help='segundos máximos de espera')
    p = sub.add_parser('captura', help='guardar lo que muestra la vista 3D (PNG en capturas/)')
    p.add_argument('nombre')
    p.add_argument('--demora', type=float, default=6.0, help='segundos para que la vista termine de dibujarse')
    p = sub.add_parser('cerrar', help='cerrar el Blender abierto con iniciar (opcional: guardar antes)')
    p.add_argument('--guardar', help='ruta .blend donde guardar antes de cerrar')
    p = sub.add_parser('estado', help='cola pendiente y últimas líneas del log')
    p.add_argument('--lineas', type=int, default=15)
    sub.add_parser('demo', help='probar el protocolo con un corredor simulado (no necesita Blender)')
    args = ap.parse_args(argv)

    if args.cmd == 'iniciar':
        return iniciar(args)
    if args.cmd == 'estado':
        return estado(args)
    if args.cmd == 'cerrar':
        return cerrar(args)
    if args.cmd == 'demo':
        return demo(args)
    base = carpeta_base(args.base)
    if args.cmd == 'enviar':
        if args.codigo:
            codigo, nombre = args.codigo + '\n', 'codigo'
        elif args.archivo:
            with open(args.archivo, encoding='utf-8') as f:
                codigo, nombre = f.read(), args.archivo
        else:
            print('Falta el archivo del paso o --codigo.')
            return 2
        ok, _, _ = enviar(base, codigo, nombre, args.espera)
        return 0 if ok else 1
    if args.cmd == 'captura':
        img = pedir_captura(base, args.nombre, args.demora)
        print(img or 'No apareció la captura: mirá `vivo.py estado`.')
        return 0 if img else 1
    return 2


if __name__ == '__main__':
    sys.exit(main())
