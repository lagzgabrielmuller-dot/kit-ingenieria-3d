#!/usr/bin/env python3
"""video_calidad.py - control de calidad y arreglos de videos con ffmpeg (solo biblioteca estandar).

Subcomandos:
  revisar VIDEO   mide formato, color, cuadros negros o congelados, silencios, volumen (LUFS),
                  costura del loop y arma una hoja de contacto. Devuelve 0 sin errores, 1 con errores.
  audio VIDEO     normaliza el volumen en dos pasadas (EBU R128) copiando el video sin recodificar.
  color VIDEO     pasa el video a BT.709 con etiquetas (arregla rojos corridos al naranja).
  demo            arma un video con fallas, lo revisa, lo arregla y lo vuelve a revisar.

Ejemplos:
  python video_calidad.py revisar final.mp4 --perfil youtube --hoja
  python video_calidad.py revisar loop.mp4 --perfil wallpaper --ancho 2560 --alto 1440 --fps 32
  python video_calidad.py audio final.mp4 --lufs -14
  python video_calidad.py color viejo.mp4 --desde bt601
Usa ffmpeg y ffprobe del PATH, o los de las variables FFMPEG y FFPROBE.
"""
import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from fractions import Fraction

try:
    sys.stdout.reconfigure(errors='replace')
except Exception:
    pass

PERFILES = {
    # codecs y pix: lo aceptado; lufs: objetivo; tol: tolerancia en LU; tp: pico verdadero maximo (dBTP)
    'youtube': dict(codecs={'h264', 'hevc', 'av1', 'vp9'}, pix={'yuv420p', 'yuv420p10le'}, lufs=-14.0, tol=1.5,
                    tp=-1.0, faststart=True, nota='Subida a YouTube u otra plataforma de video.'),
    'presentacion': dict(codecs={'h264'}, pix={'yuv420p'}, lufs=-16.0, tol=2.0, tp=-1.0, faststart=True,
                         nota='Video para pasar en clase o en una exposicion (H.264 abre en cualquier compu).'),
    'vertical': dict(codecs={'h264'}, pix={'yuv420p'}, lufs=-14.0, tol=1.5, tp=-1.0, faststart=True,
                     ancho=1080, alto=1920, nota='Clip vertical 9:16 para redes.'),
    'wallpaper': dict(codecs={'h264'}, pix={'yuv420p'}, lufs=None, tol=None, tp=None, faststart=False, loop=True,
                      nota='Fondo animado en loop (Wallpaper Engine recomienda H.264 en .mp4).'),
    'libre': dict(codecs=None, pix=None, lufs=None, tol=None, tp=None, faststart=False, nota='Sin requisitos de plataforma.'),
}

COLOR_709 = ['-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv']
# setparams marca primarios y transferencia en cada cuadro: las versiones nuevas de ffmpeg toman eso y no las opciones
SETPARAMS_709 = 'setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv'
VF_709 = 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,' + SETPARAMS_709


def buscar_ffmpeg():
    ff = os.environ.get('FFMPEG') or shutil.which('ffmpeg')
    fp = os.environ.get('FFPROBE') or shutil.which('ffprobe')
    if ff and not fp:
        cand = os.path.join(os.path.dirname(ff), 'ffprobe' + ('.exe' if ff.lower().endswith('.exe') else ''))
        fp = cand if os.path.isfile(cand) else None
    if not ff or not fp:
        print('Falta ffmpeg o ffprobe: instalalo o defini las variables FFMPEG y FFPROBE.')
        sys.exit(2)
    return ff, fp


def correr(cmd, entrada=None):
    r = subprocess.run(cmd, input=entrada, capture_output=True)
    dec = lambda b: b.decode('utf-8', 'replace') if b else ''
    return r.returncode, dec(r.stdout), dec(r.stderr)


def fraccion(txt):
    try:
        f = Fraction(txt)
        return float(f) if f > 0 else None
    except (ValueError, ZeroDivisionError, TypeError):
        return None


def atomos_mp4(ruta, maximo=64):
    """Tipos de los atomos de primer nivel de un MP4/MOV, en orden."""
    tipos = []
    try:
        total = os.path.getsize(ruta)
        with open(ruta, 'rb') as f:
            pos = 0
            while pos < total and len(tipos) < maximo:
                f.seek(pos)
                cab = f.read(16)
                if len(cab) < 8:
                    break
                tam, tipo = struct.unpack('>I4s', cab[:8])
                if tam == 1 and len(cab) == 16:
                    tam = struct.unpack('>Q', cab[8:16])[0]
                elif tam == 0:
                    tam = total - pos
                if tam < 8:
                    break
                tipos.append(tipo.decode('latin-1'))
                pos += tam
    except OSError:
        pass
    return tipos


def sondear(fp, ruta):
    code, out, err = correr([fp, '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', ruta])
    if code != 0:
        raise RuntimeError(err.strip() or 'ffprobe no pudo leer el archivo')
    d = json.loads(out)
    v = next((s for s in d.get('streams', []) if s.get('codec_type') == 'video'
              and not s.get('disposition', {}).get('attached_pic')), None)
    a = next((s for s in d.get('streams', []) if s.get('codec_type') == 'audio'), None)
    fmt = d.get('format', {})
    dur = float(fmt.get('duration') or (v or {}).get('duration') or 0)
    return v, a, fmt, dur


def escanear(ff, ruta, con_audio, gpu=False):
    """Una sola pasada: cuadros negros, congelados, silencios y volumen EBU R128."""
    cmd = [ff, '-hide_banner', '-nostats']
    if gpu:
        cmd += ['-hwaccel', 'cuda']
    cmd += ['-i', ruta, '-map', '0:v:0', '-vf', 'scale=480:-2,blackdetect=d=0.25:pix_th=0.10,freezedetect=n=-60dB:d=1']
    if con_audio:
        cmd += ['-map', '0:a:0', '-af', 'ebur128=peak=true:framelog=verbose,silencedetect=n=-50dB:d=2']
    cmd += ['-f', 'null', '-']
    t0 = time.time()
    code, _, err = correr(cmd)
    res = {'segundos_escaneo': round(time.time() - t0, 1), 'negros': [], 'congelados': [], 'silencios': []}
    for m in re.finditer(r'black_start:\s*([\d.]+)\s+black_end:\s*([\d.]+)\s+black_duration:\s*([\d.]+)', err):
        res['negros'].append([float(m.group(1)), float(m.group(2))])
    ini = None
    for m in re.finditer(r'freezedetect\.freeze_(start|end):\s*([\d.]+)', err):
        if m.group(1) == 'start':
            ini = float(m.group(2))
        elif ini is not None:
            res['congelados'].append([ini, float(m.group(2))])
            ini = None
    if ini is not None:
        res['congelados'].append([ini, None])
    ini = None
    for m in re.finditer(r'silence_(start|end):\s*(-?[\d.]+)', err):
        if m.group(1) == 'start':
            ini = max(0.0, float(m.group(2)))
        elif ini is not None:
            res['silencios'].append([ini, float(m.group(2))])
            ini = None
    if ini is not None:
        res['silencios'].append([ini, None])
    if con_audio:
        resumen = err[err.rfind('Summary:'):] if 'Summary:' in err else ''
        num = lambda pat: (lambda m: (None if m is None else (float('-inf') if 'inf' in m.group(1) else float(m.group(1)))))(re.search(pat, resumen))
        res['lufs'] = num(r'I:\s*(-?inf|-?[\d.]+)\s*LUFS')
        res['lra'] = num(r'LRA:\s*(-?inf|-?[\d.]+)\s*LU\b')
        res['pico_db'] = num(r'Peak:\s*(-?inf|-?[\d.]+)\s*dBFS')
    if code != 0:
        res['error'] = err.strip().splitlines()[-1:] if err.strip() else ['ffmpeg fallo']
    return res


def ssim(ff, a, b):
    _, _, err = correr([ff, '-hide_banner', '-nostats', '-i', a, '-i', b, '-lavfi', 'ssim', '-f', 'null', '-'])
    m = re.search(r'All:\s*(-?[\d.]+)', err)
    return float(m.group(1)) if m else None


def costura_loop(ff, ruta, carpeta):
    """Compara el ultimo cuadro con el primero, contra el paso normal entre cuadros al principio y al final."""
    d = os.path.join(carpeta, 'loop')
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    correr([ff, '-y', '-hide_banner', '-loglevel', 'error', '-i', ruta, '-vf', 'scale=640:-2', '-frames:v', '2',
            os.path.join(d, 'ini_%d.png')])
    correr([ff, '-y', '-hide_banner', '-loglevel', 'error', '-sseof', '-1', '-i', ruta, '-vf', 'scale=640:-2',
            '-fps_mode', 'passthrough', os.path.join(d, 'fin_%04d.png')])
    fin = sorted(f for f in os.listdir(d) if f.startswith('fin_'))
    i1, i2 = os.path.join(d, 'ini_1.png'), os.path.join(d, 'ini_2.png')
    if len(fin) < 2 or not (os.path.isfile(i1) and os.path.isfile(i2)):
        return None
    u1, u2 = os.path.join(d, fin[-2]), os.path.join(d, fin[-1])
    r = {'paso_inicio': ssim(ff, i1, i2), 'paso_final': ssim(ff, u1, u2), 'costura': ssim(ff, u2, i1)}
    for f in fin[:-2]:
        os.remove(os.path.join(d, f))
    if None in r.values():
        return None
    paso = (r['paso_inicio'] + r['paso_final']) / 2
    r['relacion'] = round((1 - r['costura']) / max(0.004, 1 - paso), 2)  # 1 = como un paso normal
    r['repite_primero'] = paso < 0.997 and (1 - r['costura']) < 0.35 * (1 - paso)
    return r


def hoja_contacto(ff, ruta, dur, carpeta, n=12, ancho=480, cols=4):
    """Hoja de contacto de n cuadros repartidos; cada uno rotulado con su tiempo si drawtext anda."""
    tiempos = [dur * (i + 0.5) / n for i in range(n)]
    hechos = 0
    for i, t in enumerate(tiempos):
        dst = os.path.join(carpeta, 'c_%02d.png' % i)
        base = [ff, '-y', '-hide_banner', '-loglevel', 'error', '-ss', '%.3f' % t, '-i', ruta, '-frames:v', '1']
        rot = ("scale=%d:-2,drawtext=text='%.1f s':x=8:y=8:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.6:boxborderw=4"
               % (ancho, t))
        if correr(base + ['-vf', rot, dst])[0] != 0:
            correr(base + ['-vf', 'scale=%d:-2' % ancho, dst])
        hechos += os.path.isfile(dst)
    if not hechos:
        return None, tiempos
    filas = (n + cols - 1) // cols
    salida = os.path.join(carpeta, 'hoja.jpg')
    correr([ff, '-y', '-hide_banner', '-loglevel', 'error', '-framerate', '1', '-i', os.path.join(carpeta, 'c_%02d.png'),
            '-vf', 'tile=%dx%d:padding=4:color=0x101010' % (cols, filas), '-frames:v', '1', '-q:v', '3', salida])
    for i in range(n):
        try:
            os.remove(os.path.join(carpeta, 'c_%02d.png' % i))
        except OSError:
            pass
    return (salida if os.path.isfile(salida) else None), tiempos


def fmt_t(t):
    return 'fin' if t is None else ('%d:%04.1f' % (t // 60, t % 60))


def revisar(args, ff=None, fp=None, silencioso=False):
    ff, fp = (ff, fp) if ff else buscar_ffmpeg()
    ruta = os.path.abspath(args.video)
    if not os.path.isfile(ruta):
        print('No existe:', ruta)
        return 2, None
    perfil = PERFILES[args.perfil]
    carpeta = args.salida or os.path.join(tempfile.gettempdir(), 'revision_video',
                                          re.sub(r'[^\w\-]+', '_', os.path.splitext(os.path.basename(ruta))[0]))
    os.makedirs(carpeta, exist_ok=True)
    try:
        v, a, fmt, dur = sondear(fp, ruta)
    except Exception as e:
        print('No se pudo leer el video:', e)
        return 2, None
    if v is None:
        print('El archivo no tiene video.')
        return 2, None
    hall = []  # (nivel, mensaje, arreglo)
    def h(nivel, msg, arreglo=''):
        hall.append((nivel, msg, arreglo))
    W, H = int(v.get('width', 0)), int(v.get('height', 0))
    fps_r, fps_m = fraccion(v.get('r_frame_rate')), fraccion(v.get('avg_frame_rate'))
    fps = fps_m or fps_r
    codec, pix = v.get('codec_name'), v.get('pix_fmt')
    cs, cp, ct, cr = (v.get(k) for k in ('color_space', 'color_primaries', 'color_transfer', 'color_range'))
    exp_w = args.ancho or perfil.get('ancho')
    exp_h = args.alto or perfil.get('alto')
    nombre = os.path.basename(ruta)
    # formato
    if W % 2 or H % 2:
        h('ERROR', 'Medidas impares (%dx%d): yuv420p necesita ancho y alto pares.' % (W, H), 'Escalar a medidas pares: `scale=trunc(iw/2)*2:trunc(ih/2)*2`.')
    if exp_w and exp_h and (W, H) != (exp_w, exp_h):
        h('ERROR', 'Resolucion %dx%d; se esperaba %dx%d.' % (W, H, exp_w, exp_h), 'Volver a exportar con la resolucion pedida (sin estirar: scale + crop o pad).')
    if args.fps and fps and abs(fps - args.fps) > 0.01:
        h('ERROR', 'Cuadros por segundo %.3f; se esperaban %g.' % (fps, args.fps), 'Exportar a la tasa pedida sin cambiar la duracion (RIFE para subir cuadros, `-r` en la salida).')
    if fps_r and fps_m and abs(fps_r - fps_m) / fps_r > 0.01:
        h('AVISO', 'Tasa de cuadros variable (nominal %.3f, promedio %.3f).' % (fps_r, fps_m), 'Exportar con `-r` fijo (cuadros constantes) para que no tironee.')
    if perfil['codecs'] and codec not in perfil['codecs']:
        h('ERROR' if args.perfil != 'youtube' else 'AVISO', 'Codec %s; para %s conviene %s.' % (codec, args.perfil, '/'.join(sorted(perfil['codecs']))), 'Recodificar a H.264 (libx264 o h264_nvenc).')
    if perfil['pix'] and pix not in perfil['pix']:
        h('ERROR', 'Formato de pixel %s; para %s va %s.' % (pix, args.perfil, ' o '.join(sorted(perfil['pix']))), 'Agregar `-pix_fmt yuv420p` al exportar.')
    # color
    sin_etiqueta = cs in (None, '', 'unknown', 'unspecified')
    if pix and pix.startswith(('yuv', 'nv')):
        if H >= 720 and sin_etiqueta:
            h('ERROR', 'Video HD sin etiqueta de color. Los reproductores (YouTube, navegadores, Windows) lo leen como BT.709; si se convirtio desde RGB sin indicar la matriz quedo en BT.601 y los rojos se ven corridos al naranja.',
              'Al exportar desde RGB (cuadros PNG o un render): `-vf ' + VF_709 + ' ' + ' '.join(COLOR_709) + '`. Para un video ya hecho: `video_calidad.py color VIDEO --desde bt601`.')
        elif cs in ('bt470bg', 'smpte170m') and H >= 720:
            h('NOTA', 'Color etiquetado como BT.601 (%s) en un video HD: se ve bien, pero lo habitual en HD es BT.709.' % cs)
        elif not sin_etiqueta and (cp in (None, 'unknown') or ct in (None, 'unknown')):
            h('AVISO', 'Etiqueta de color incompleta (matriz %s, primarios %s, transferencia %s).' % (cs, cp, ct), 'Agregar `' + SETPARAMS_709 + '` al final del -vf (y ' + ' '.join(COLOR_709) + ').')
        if cr == 'pc':
            h('AVISO', 'Rango de color completo (pc/jpeg): algunos reproductores lo muestran lavado o con negros aplastados.', 'Exportar en rango limitado: `out_range=tv` y `-color_range tv`.')
    # contenedor
    at = atomos_mp4(ruta) if ruta.lower().endswith(('.mp4', '.mov', '.m4v')) else []
    faststart = ('moov' in at and 'mdat' in at and at.index('moov') < at.index('mdat')) if at else None
    if perfil['faststart'] and faststart is False:
        h('AVISO', 'El indice (moov) esta al final del archivo: tarda en empezar en la web y al subir.', '`ffmpeg -i VIDEO -c copy -movflags +faststart SALIDA.mp4`')
    # escaneo
    esc = {} if args.rapido else escanear(ff, ruta, a is not None, gpu=args.gpu)
    for s, e in esc.get('negros', []):
        e2 = dur if e is None else e
        if s <= 0.05 and e2 - s <= 0.5:
            continue
        if e2 >= dur - 0.1 and e2 - s <= 1.5 and args.perfil != 'wallpaper':
            continue
        h('AVISO', 'Pantalla negra de %s a %s (%.2f s).' % (fmt_t(s), fmt_t(e), e2 - s), 'Si no es un fundido a proposito, revisar esa toma.')
    negros = esc.get('negros', [])
    for s, e in esc.get('congelados', []):
        e2 = dur if e is None else e
        if any(ns - 0.1 <= s and e2 <= ne + 0.1 for ns, ne in negros):
            continue  # es la misma pantalla negra
        h('AVISO', 'Imagen congelada de %s a %s (%.1f s).' % (fmt_t(s), fmt_t(e), e2 - s), 'Si no es una pausa a proposito: clip que se corto, cuadros repetidos o render que fallo.')
    if a is not None and args.perfil in ('youtube', 'vertical', 'presentacion'):
        for s, e in esc.get('silencios', []):
            e2 = dur if e is None else e
            if s > 0.5 and e2 < dur - 0.5:
                h('NOTA', 'Silencio de %s a %s (%.1f s).' % (fmt_t(s), fmt_t(e), e2 - s))
    if 'error' in esc:
        h('AVISO', 'ffmpeg tuvo problemas al decodificar: %s' % ' '.join(esc['error']), 'Puede ser un archivo cortado o dañado: volver a exportar.')
    # audio
    objetivo = args.lufs if args.lufs is not None else perfil['lufs']
    tol = perfil['tol'] or 1.5
    if a is None:
        if objetivo is not None:
            h('NOTA', 'El video no tiene audio.')
    else:
        acod, asr = a.get('codec_name'), int(a.get('sample_rate') or 0)
        if args.perfil in ('youtube', 'vertical', 'presentacion') and acod not in ('aac', 'opus', 'mp3'):
            h('AVISO', 'Audio en %s; en .mp4 lo mas compatible es AAC.' % acod, '`-c:a aac -b:a 256k`')
        if asr and asr not in (44100, 48000):
            h('AVISO', 'Frecuencia de audio %d Hz; lo habitual en video es 48000 Hz.' % asr, '`-ar 48000`')
        lufs, pico = esc.get('lufs'), esc.get('pico_db')
        if objetivo is not None and lufs is not None and lufs != float('-inf'):
            dif = lufs - objetivo
            if abs(dif) > 2 * tol:
                h('ERROR', 'Volumen integrado %.1f LUFS; objetivo %.1f (%+.1f LU).' % (lufs, objetivo, dif), '`video_calidad.py audio VIDEO --lufs %g`' % objetivo)
            elif abs(dif) > tol:
                h('AVISO', 'Volumen integrado %.1f LUFS; objetivo %.1f (%+.1f LU).' % (lufs, objetivo, dif), '`video_calidad.py audio VIDEO --lufs %g`' % objetivo)
        tp = perfil.get('tp')
        if tp is not None and pico is not None and pico > tp:
            h('AVISO', 'Pico verdadero %.1f dBTP (arriba de %.1f): puede saturar al comprimir.' % (pico, tp), '`video_calidad.py audio VIDEO` (limita el pico a %.1f dBTP)' % tp)
    # loop
    loop = None
    if args.loop or perfil.get('loop'):
        loop = costura_loop(ff, ruta, carpeta)
        if loop:
            c, rel = loop['costura'], loop['relacion']
            if loop['repite_primero']:
                h('AVISO', 'El ultimo cuadro repite al primero (SSIM %.4f): al dar la vuelta se ve un cuadro quieto.' % c,
                  'Sacar el ultimo cuadro antes de exportar (con primer = ultimo cuadro en Wan, el loop ya cierra solo).')
            elif rel > 3:
                h('ERROR', 'Salto visible en el loop: el cambio del ultimo al primer cuadro es %.1f veces un paso normal.' % rel,
                  'Cerrar el loop: mismo cuadro de inicio y fin (Wan FLF2V) sacando el repetido, fundido cruzado o ping-pong; la costura en un momento con poco movimiento.')
            elif rel > 1.8:
                h('AVISO', 'La costura del loop se puede notar: el cambio del ultimo al primer cuadro es %.1f veces un paso normal.' % rel,
                  'Suavizar con un fundido cruzado corto en la costura.')
    # notas de plataforma
    if args.perfil == 'wallpaper' and fps and fps > 31:
        h('NOTA', '%.0f cuadros por segundo: mas fluido, pero decodificar cuesta mas que a 30 (importa en compus con jugando de fondo).' % fps)
    hoja, tiempos = (None, [])
    if args.hoja:
        hoja, tiempos = hoja_contacto(ff, ruta, dur, carpeta)
    # informe
    errores = sum(1 for x in hall if x[0] == 'ERROR')
    avisos = sum(1 for x in hall if x[0] == 'AVISO')
    br = fmt.get('bit_rate')
    datos = {
        'archivo': ruta, 'perfil': args.perfil, 'duracion_s': round(dur, 3), 'tamano_mb': round(os.path.getsize(ruta) / 1e6, 1),
        'bitrate_mbps': round(int(br) / 1e6, 2) if br else None, 'codec': codec, 'perfil_codec': v.get('profile'),
        'pix_fmt': pix, 'resolucion': '%dx%d' % (W, H), 'fps': round(fps, 3) if fps else None,
        'color': {'matriz': cs, 'primarios': cp, 'transferencia': ct, 'rango': cr}, 'faststart': faststart,
        'audio': None if a is None else {'codec': a.get('codec_name'), 'hz': a.get('sample_rate'), 'canales': a.get('channels'),
                                          'lufs': esc.get('lufs'), 'lra': esc.get('lra'), 'pico_dbtp': esc.get('pico_db')},
        'escaneo': {k: esc.get(k) for k in ('negros', 'congelados', 'silencios', 'segundos_escaneo')} if esc else None,
        'loop': loop, 'hoja': hoja, 'tiempos_hoja': [round(t, 2) for t in tiempos],
        'hallazgos': [{'nivel': n, 'mensaje': m, 'arreglo': f} for n, m, f in hall], 'errores': errores, 'avisos': avisos,
    }
    estado = 'CON ERRORES' if errores else ('OK con avisos' if avisos else 'OK')
    lin = ['# Revision de video: %s' % nombre, '', '**%s**: %d errores, %d avisos (perfil %s: %s)' % (estado, errores, avisos, args.perfil, perfil['nota']), '',
           '| Dato | Valor |', '|---|---|',
           '| Duracion | %.2f s |' % dur, '| Resolucion | %dx%d |' % (W, H), '| Cuadros por segundo | %s |' % (('%.3f' % fps) if fps else '?'),
           '| Video | %s %s, %s |' % (codec, v.get('profile') or '', pix), '| Color | matriz %s, primarios %s, transferencia %s, rango %s |' % tuple(x or '-' for x in (cs, cp, ct, cr)),
           '| Bitrate | %s Mb/s (%s MB) |' % (datos['bitrate_mbps'], datos['tamano_mb']),
           '| Inicio rapido (faststart) | %s |' % {True: 'si', False: 'no', None: '-'}[faststart]]
    if a is not None:
        lin.append('| Audio | %s, %s Hz, canales: %s; %s LUFS, LRA %s LU, pico %s dBTP |' % (a.get('codec_name'), a.get('sample_rate'), a.get('channels'),
                   esc.get('lufs', '-'), esc.get('lra', '-'), esc.get('pico_db', '-')))
    else:
        lin.append('| Audio | sin audio |')
    if loop:
        lin.append('| Loop | costura %.4f (SSIM), %.2f veces un paso normal%s |' % (loop['costura'], loop['relacion'], ', repite el primer cuadro' if loop['repite_primero'] else ''))
    if esc:
        lin.append('| Escaneo | %s s |' % esc.get('segundos_escaneo'))
    lin += ['', '## Hallazgos', '']
    if not hall:
        lin.append('Nada para corregir.')
    for n, m, f in hall:
        lin.append('- **%s** %s%s' % (n, m, ('  \n  Arreglo: ' + f) if f else ''))
    if hoja:
        lin += ['', '## Hoja de contacto', '', '`%s` (cuadros en %s s). Mirala como imagen antes de entregar.' % (hoja, ', '.join('%.1f' % t for t in tiempos))]
    texto = '\n'.join(lin) + '\n'
    with open(os.path.join(carpeta, 'revision.md'), 'w', encoding='utf-8') as f:
        f.write(texto)
    with open(os.path.join(carpeta, 'revision.json'), 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    if not silencioso:
        print(json.dumps(datos, ensure_ascii=False, indent=1) if args.json else texto)
        print('Informe en', carpeta)
    return (1 if errores else 0), datos


def cmd_audio(args):
    ff, _ = buscar_ffmpeg()
    ruta = os.path.abspath(args.video)
    I, TP, LRA = args.lufs, args.tp, args.lra
    _, _, err = correr([ff, '-hide_banner', '-nostats', '-i', ruta, '-map', '0:a:0', '-af',
                        'loudnorm=I=%g:TP=%g:LRA=%g:print_format=json' % (I, TP, LRA), '-f', 'null', '-'])
    bloques = re.findall(r'\{[^{}]*"input_i"[^{}]*\}', err, re.S)
    if not bloques:
        print('No se pudo medir el audio (el video tiene audio?).')
        return 2
    d = json.loads(bloques[-1])
    if 'inf' in str(d.get('input_i')):
        print('El audio esta en silencio: no hay nada que normalizar.')
        return 2
    salida = args.salida or '%s_lufs%g%s' % (os.path.splitext(ruta)[0], abs(I), '.mp4')
    filtro = ('loudnorm=I=%g:TP=%g:LRA=%g:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s'
              ':linear=true:print_format=json,aresample=48000') % (I, TP, LRA, d['input_i'], d['input_tp'], d['input_lra'],
                                                                   d['input_thresh'], d['target_offset'])
    code, _, err2 = correr([ff, '-y', '-hide_banner', '-nostats', '-i', ruta, '-map', '0:v?', '-map', '0:a:0', '-c:v', 'copy',
                            '-af', filtro, '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-movflags', '+faststart', salida])
    if code != 0:
        print('Fallo la normalizacion:', err2.strip().splitlines()[-1:] if err2.strip() else '')
        return 1
    b2 = re.findall(r'\{[^{}]*"input_i"[^{}]*\}', err2, re.S)
    modo = json.loads(b2[-1]).get('normalization_type', '?') if b2 else '?'
    print('Audio: %s LUFS, pico %s dBTP -> objetivo %g LUFS, pico %g dBTP (modo %s). Video copiado sin recodificar.' % (
        d['input_i'], d['input_tp'], I, TP, modo))
    if modo.lower() == 'dynamic':
        print('Ojo: loudnorm uso modo dinamico (comprime un poco el rango). Pasa cuando el pico no entra con ganancia lineal o el rango (LRA) supera el objetivo: proba --tp -2 o --lra 15.')
    print('Listo:', salida)
    return 0


def cmd_color(args):
    ff, fp = buscar_ffmpeg()
    ruta = os.path.abspath(args.video)
    v, a, fmt, dur = sondear(fp, ruta)
    salida = args.salida or '%s_bt709.mp4' % os.path.splitext(ruta)[0]
    base = [ff, '-y', '-hide_banner', '-loglevel', 'error', '-i', ruta, '-map', '0:v:0', '-map', '0:a?']
    if args.desde == 'bt709':
        bsf = {'h264': 'h264_metadata', 'hevc': 'hevc_metadata'}.get(v.get('codec_name'))
        if not bsf:
            print('Solo se puede etiquetar sin recodificar H.264 o HEVC; usa --desde bt601 o recodifica.')
            return 2
        cmd = base + ['-c', 'copy', '-bsf:v', '%s=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1' % bsf,
                      '-movflags', '+faststart', salida]
        que = 'etiquetado como BT.709 sin recodificar'
    else:
        vf = 'scale=in_color_matrix=bt601:in_range=tv,format=gbrp16le,' + VF_709
        if args.gpu:
            enc = ['-c:v', 'h264_nvenc', '-preset', 'p7', '-tune', 'hq', '-rc', 'vbr', '-cq', str(args.calidad), '-b:v', '0',
                   '-spatial-aq', '1', '-temporal-aq', '1', '-rc-lookahead', '32', '-profile:v', 'high']
        else:
            enc = ['-c:v', 'libx264', '-preset', 'slow', '-crf', str(args.calidad)]
        cmd = base + ['-vf', vf] + enc + COLOR_709 + ['-c:a', 'copy', '-movflags', '+faststart', salida]
        que = 'convertido de %s a BT.709 y etiquetado' % args.desde
    code, _, err = correr(cmd)
    if code != 0:
        print('Fallo:', err.strip().splitlines()[-3:] if err.strip() else '')
        return 1
    v2 = sondear(fp, salida)[0]
    print('Listo (%s): %s  [matriz %s, primarios %s, transferencia %s]' % (que, salida, v2.get('color_space'),
                                                                          v2.get('color_primaries'), v2.get('color_transfer')))
    return 0


def cmd_demo(args):
    ff, fp = buscar_ffmpeg()
    d = tempfile.mkdtemp(prefix='video_calidad_demo_')
    malo = os.path.join(d, 'demo_con_fallas.mp4')
    print('1) Video de prueba con fallas (sin etiqueta de color, audio bajo, 1 s negro, indice al final):')
    code, _, err = correr([ff, '-y', '-hide_banner', '-loglevel', 'error',
                           '-f', 'lavfi', '-i', 'testsrc2=size=1280x720:rate=30:duration=8',
                           '-f', 'lavfi', '-i', "aevalsrc='0.3*sin(2*PI*440*t)*(0.55+0.45*sin(2*PI*0.5*t))':s=48000:d=8",
                           '-vf', "format=rgb24,drawbox=enable='between(t,3,4)':color=black:t=fill",
                           '-af', 'volume=-24dB', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '128k', '-shortest', malo])
    if code != 0:
        print('No se pudo crear el video de prueba:', err[-300:])
        return 2
    ns = argparse.Namespace(video=malo, perfil='youtube', ancho=None, alto=None, fps=None, loop=False, lufs=None,
                            hoja=True, salida=os.path.join(d, 'revision_antes'), rapido=False, gpu=False, json=False)
    c1, d1 = revisar(ns, ff, fp)
    print('2) Arreglos: color y volumen')
    fijo_color = os.path.join(d, 'demo_color.mp4')
    cmd_color(argparse.Namespace(video=malo, desde='bt601', gpu=False, calidad=18, salida=fijo_color))
    fijo = os.path.join(d, 'demo_arreglado.mp4')
    cmd_audio(argparse.Namespace(video=fijo_color, lufs=-14.0, tp=-1.0, lra=11.0, salida=fijo))
    ns2 = argparse.Namespace(**dict(vars(ns), video=fijo, salida=os.path.join(d, 'revision_despues'), hoja=False))
    c2, d2 = revisar(ns2, ff, fp)
    esperado = c1 == 1 and c2 == 0 and any('etiqueta de color' in x['mensaje'] for x in d1['hallazgos']) \
        and any('Pantalla negra' in x['mensaje'] for x in d1['hallazgos'])
    print('DEMO %s: antes %d errores, despues %d errores. Archivos en %s' % ('OK' if esperado else 'FALLO', d1['errores'], d2['errores'], d))
    return 0 if esperado else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd')
    r = sp.add_parser('revisar', help='revisar un video')
    r.add_argument('video')
    r.add_argument('--perfil', choices=sorted(PERFILES), default='libre')
    r.add_argument('--ancho', type=int)
    r.add_argument('--alto', type=int)
    r.add_argument('--fps', type=float)
    r.add_argument('--loop', action='store_true', help='medir la costura del loop (el perfil wallpaper ya lo hace)')
    r.add_argument('--lufs', type=float, help='objetivo de volumen integrado (pisa el del perfil)')
    r.add_argument('--hoja', action='store_true', help='armar hoja de contacto de 12 cuadros')
    r.add_argument('--salida', help='carpeta del informe (por defecto, una carpeta temporal)')
    r.add_argument('--rapido', action='store_true', help='sin escaneo de cuadros ni volumen (solo formato)')
    r.add_argument('--gpu', action='store_true', help='decodificar con la placa (NVIDIA)')
    r.add_argument('--json', action='store_true', help='imprimir el informe en JSON')
    au = sp.add_parser('audio', help='normalizar el volumen (EBU R128, dos pasadas)')
    au.add_argument('video')
    au.add_argument('--lufs', type=float, default=-14.0)
    au.add_argument('--tp', type=float, default=-1.0, help='pico verdadero maximo en dBTP')
    au.add_argument('--lra', type=float, default=11.0)
    au.add_argument('--salida')
    co = sp.add_parser('color', help='pasar a BT.709 con etiquetas')
    co.add_argument('video')
    co.add_argument('--desde', choices=['bt601', 'bt709'], default='bt601',
                    help='bt601: convierte la matriz (videos hechos desde RGB sin indicarla); bt709: solo etiqueta, sin recodificar')
    co.add_argument('--gpu', action='store_true', help='recodificar con h264_nvenc')
    co.add_argument('--calidad', type=int, default=16, help='CRF de libx264 o CQ de NVENC (menor = mejor)')
    co.add_argument('--salida')
    sp.add_parser('demo', help='prueba completa con un video sintetico')
    args = ap.parse_args()
    if args.cmd == 'revisar':
        sys.exit(revisar(args)[0])
    if args.cmd == 'audio':
        sys.exit(cmd_audio(args))
    if args.cmd == 'color':
        sys.exit(cmd_color(args))
    if args.cmd == 'demo':
        sys.exit(cmd_demo(args))
    ap.print_help()


if __name__ == '__main__':
    main()
