#!/usr/bin/env python3
"""progreso.py - tablero de progreso en vivo para trabajos largos (solo biblioteca estandar).

Arma una pagina HTML que se actualiza sola (cada 1,5 s, sin recargar ni perder el scroll) con el plan y sus pasos,
el paso actual, las ultimas imagenes (renders, vistas, hojas de contacto), el texto que se va escribiendo, las
preguntas para el usuario y la actividad. Se deja abierta en el navegador (por ejemplo en el segundo monitor)
mientras Claude trabaja: asi se corrige el rumbo temprano en lugar de rehacer al final.

Comandos:
  init "Titulo" --plan "Paso 1|Paso 2|..." [--carpeta DIR] [--abrir]   crea el tablero y lo marca como activo
  paso N [--estado en_curso|hecho|error|pendiente] [--nota "..."]          actualiza un paso (empieza en 1)
  imagen RUTA [--titulo "..."]                                             agrega una imagen (png, jpg, gif, svg, webp)
  vigilar DIR [--quitar]                                                   cada imagen nueva de DIR (renders, vistas) aparece sola
                                                                           (tambien: init ... --vigilar DIR)
  texto ARCHIVO | --texto "..." [--titulo "..."]                           muestra el borrador (Markdown simple)
  pregunta "..."  |  responder                                            destaca o borra una pregunta para el usuario
  nota "..."                                                               agrega una linea a la actividad
  fin [--nota "..."]                                                       lo cierra y deja de estar activo
  abrir | estado | demo
  hook                                                                     para hooks de Claude Code (lee el JSON por stdin)
Con --carpeta se elige el tablero; sin ella se usa el activo (archivo ~/.progreso_activo).
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import sys
import tempfile
import time
import webbrowser

PUNTERO = os.path.join(os.path.expanduser('~'), '.progreso_activo')
MAX_IMG, MAX_ACT = 12, 60

PAGINA = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Progreso</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--fondo:#0d0d0f;--panel:#16161a;--borde:#2a2a31;--texto:#ece9e6;--suave:#9b98a0;--rojo:#c8102e;--ok:#3fb950;--amarillo:#f2c14e}
*{box-sizing:border-box}body{margin:0;background:var(--fondo);color:var(--texto);font:15px/1.5 system-ui,Segoe UI,Arial,sans-serif}
header{padding:18px 24px;border-bottom:3px solid var(--rojo);display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap}
h1{margin:0;font-size:22px}#meta{color:var(--suave);font-size:13px}
main{display:grid;grid-template-columns:minmax(260px,340px) 1fr;gap:18px;padding:18px 24px}
@media(max-width:900px){main{grid-template-columns:1fr}}
section{background:var(--panel);border:1px solid var(--borde);border-radius:10px;padding:14px 16px;margin-bottom:18px}
h2{margin:0 0 10px;font-size:14px;letter-spacing:.06em;text-transform:uppercase;color:var(--suave)}
.barra{height:8px;background:#26262c;border-radius:6px;overflow:hidden;margin:6px 0 12px}.barra>div{height:100%;background:var(--rojo);transition:width .4s}
ol{margin:0;padding-left:0;list-style:none}li.p{padding:6px 8px;border-radius:6px;margin-bottom:4px;display:flex;gap:8px}
li.p .m{width:18px;flex:none;text-align:center}li.hecho{color:var(--suave)}li.hecho .m{color:var(--ok)}
li.en_curso{background:#2a0f15;outline:1px solid var(--rojo)}li.en_curso .m{color:var(--rojo)}li.error .m{color:#ff6b6b}
li .n{display:block;color:var(--suave);font-size:12px}
#pregunta{display:none;background:#2b230c;border:1px solid var(--amarillo);color:#ffe6a6;font-weight:600}
.galeria{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
figure{margin:0;background:#0f0f12;border:1px solid var(--borde);border-radius:8px;overflow:hidden}
figure img{width:100%;display:block;cursor:zoom-in}figcaption{padding:6px 10px;font-size:12px;color:var(--suave)}
#texto{max-height:60vh;overflow:auto}#texto h2,#texto h3,#texto h4{color:var(--texto);text-transform:none;letter-spacing:0;margin:14px 0 6px}
#texto h2{font-size:21px}#texto h3{font-size:17px}#texto h4{font-size:15px}#texto code{background:#24242a;padding:1px 5px;border-radius:4px}
#act{font:12px/1.6 Consolas,monospace;color:var(--suave);max-height:40vh;overflow:auto}
.vacio{color:var(--suave);font-style:italic}.zoom{position:fixed;inset:0;background:#000c;display:flex;align-items:center;justify-content:center}
.zoom img{max-width:96vw;max-height:96vh}
</style></head><body>
<header><h1 id="titulo">Progreso</h1><div id="meta">esperando datos…</div></header>
<main><div>
<section id="pregunta"></section>
<section><h2>Plan</h2><div class="barra"><div id="avance" style="width:0"></div></div><ol id="plan"></ol></section>
<section><h2>Actividad</h2><div id="act"></div></section>
</div><div>
<section><h2>Imágenes</h2><div class="galeria" id="galeria"><p class="vacio">Todavía no hay imágenes.</p></div></section>
<section><h2 id="ttexto">Borrador</h2><div id="texto"><p class="vacio">Todavía no hay texto.</p></div></section>
</div></main>
<script>
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
let ultimo='';
function pintar(e){
  const firma=JSON.stringify(e); if(firma===ultimo) return; ultimo=firma;
  document.title=(e.terminado?'✔ ':'⏳ ')+e.titulo; document.getElementById('titulo').textContent=e.titulo;
  const hechos=e.plan.filter(p=>p.estado==='hecho').length, total=e.plan.length||1;
  document.getElementById('avance').style.width=Math.round(100*hechos/total)+'%';
  document.getElementById('meta').textContent=(e.terminado?'Terminado':'Trabajando')+' · '+hechos+' de '+e.plan.length+' pasos · actualizado '+e.actualizado;
  const marca={hecho:'✔',en_curso:'▶',error:'✖',pendiente:'○'};
  document.getElementById('plan').innerHTML=e.plan.map((p,i)=>'<li class="p '+p.estado+'"><span class="m">'+(marca[p.estado]||'○')+'</span><span>'+(i+1)+'. '+esc(p.texto)+(p.nota?'<span class="n">'+esc(p.nota)+'</span>':'')+'</span></li>').join('');
  const q=document.getElementById('pregunta'); if(e.pregunta){q.style.display='block';q.textContent='Necesito que me digas: '+e.pregunta}else{q.style.display='none'}
  document.getElementById('galeria').innerHTML=e.imagenes.length?e.imagenes.slice().reverse().map(im=>'<figure><img src="'+esc(im.archivo)+'" onclick="zoom(this.src)"><figcaption>'+esc(im.titulo)+' · '+esc(im.hora)+'</figcaption></figure>').join(''):'<p class="vacio">Todavía no hay imágenes.</p>';
  if(e.texto){document.getElementById('ttexto').textContent=e.texto.titulo||'Borrador';document.getElementById('texto').innerHTML=e.texto.html}
  document.getElementById('act').innerHTML=e.actividad.slice().reverse().map(a=>esc(a)).join('<br>');
}
function zoom(src){const d=document.createElement('div');d.className='zoom';d.innerHTML='<img src="'+src+'">';d.onclick=()=>d.remove();document.body.appendChild(d)}
function cargar(){const s=document.createElement('script');s.src='.progreso/estado.js?t='+Date.now();s.onload=()=>{s.remove();if(window.PROGRESO)pintar(window.PROGRESO)};s.onerror=()=>s.remove();document.body.appendChild(s)}
cargar();setInterval(cargar,1500);
</script></body></html>
"""


def ahora():
    return dt.datetime.now().strftime('%H:%M:%S')


def carpeta_activa(args_carpeta=None):
    if args_carpeta:
        return os.path.abspath(args_carpeta)
    if os.path.isfile(PUNTERO):
        c = open(PUNTERO, encoding='utf-8').read().strip()
        if c and os.path.isdir(os.path.join(c, '.progreso')):
            return c
    return None


def leer(c):
    with open(os.path.join(c, '.progreso', 'estado.json'), encoding='utf-8') as f:
        return json.load(f)


def guardar(c, e):
    e['actualizado'] = ahora()
    d = os.path.join(c, '.progreso')
    for nombre, contenido in (('estado.json', json.dumps(e, ensure_ascii=False, indent=1)),
                              ('estado.js', 'window.PROGRESO = ' + json.dumps(e, ensure_ascii=False) + ';\n')):
        fd, tmp = tempfile.mkstemp(dir=d, prefix='.tmp_')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(contenido)
        for intento in range(5):
            try:
                os.replace(tmp, os.path.join(d, nombre))
                break
            except PermissionError:  # Windows: el navegador puede estar leyendo el archivo
                time.sleep(0.1)


def actividad(e, txt):
    e['actividad'].append('%s  %s' % (ahora(), txt))
    e['actividad'] = e['actividad'][-MAX_ACT:]


def md_a_html(t):
    """Markdown simple: titulos, listas, negrita, cursiva, codigo y parrafos."""
    out, lista = [], None
    def linea(s):
        s = html.escape(s)
        s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
        return re.sub(r'(?<![\w*])\*([^*]+)\*(?!\w)', r'<i>\1</i>', s)
    for crudo in t.splitlines():
        m = re.match(r'^(#{1,3})\s+(.*)', crudo)
        li = re.match(r'^\s*(?:[-*]|\d+[.)])\s+(.*)', crudo)
        if lista and not li:
            out.append('</%s>' % lista)
            lista = None
        if m:
            n = len(m.group(1))
            out.append('<h%d>%s</h%d>' % (n + 1, linea(m.group(2)), n + 1))
        elif li:
            tipo = 'ol' if re.match(r'^\s*\d', crudo) else 'ul'
            if lista != tipo:
                if lista:
                    out.append('</%s>' % lista)
                out.append('<%s>' % tipo)
                lista = tipo
            out.append('<li>%s</li>' % linea(li.group(1)))
        elif crudo.strip():
            out.append('<p>%s</p>' % linea(crudo))
    if lista:
        out.append('</%s>' % lista)
    return '\n'.join(out)


def cmd_init(a):
    c = os.path.abspath(a.carpeta or os.getcwd())
    os.makedirs(os.path.join(c, '.progreso', 'img'), exist_ok=True)
    with open(os.path.join(c, '.progreso', '.gitignore'), 'w', encoding='utf-8') as f:
        f.write('# estado del tablero de progreso: no se sube a git\n*\n')
    plan = [p.strip() for p in (a.plan or '').split('|') if p.strip()]
    e = {'titulo': a.titulo, 'plan': [{'texto': p, 'estado': 'pendiente', 'nota': ''} for p in plan],
         'imagenes': [], 'texto': None, 'pregunta': '', 'actividad': [], 'terminado': False,
         'creado': dt.datetime.now().strftime('%Y-%m-%d %H:%M')}
    if e['plan']:
        e['plan'][0]['estado'] = 'en_curso'
    actividad(e, 'Tablero creado: ' + a.titulo)
    if getattr(a, 'vigilar', None):
        if not os.path.isdir(a.vigilar):
            os.makedirs(a.vigilar, exist_ok=True)
        e['vigilar'], e['visto'] = os.path.abspath(a.vigilar), time.time()
        actividad(e, 'Vigila %s: cada imagen nueva aparece sola' % os.path.basename(e['vigilar'].rstrip('/\\')))
    with open(os.path.join(c, 'progreso.html'), 'w', encoding='utf-8') as f:
        f.write(PAGINA)
    guardar(c, e)
    with open(PUNTERO, 'w', encoding='utf-8') as f:
        f.write(c)
    pagina = os.path.join(c, 'progreso.html')
    print('Tablero:', pagina)
    if a.abrir:
        abrir(pagina)
    return 0


def abrir(pagina):
    try:
        if hasattr(os, 'startfile'):
            os.startfile(pagina)  # Windows: navegador por defecto
        else:
            webbrowser.open('file://' + pagina)
    except Exception as ex:
        print('No se pudo abrir solo; abrilo a mano:', pagina, ex)


def con_tablero(a):
    c = carpeta_activa(getattr(a, 'carpeta', None))
    if not c:
        print('No hay tablero activo: primero "progreso.py init".')
        sys.exit(2)
    return c, leer(c)


def cmd_paso(a):
    c, e = con_tablero(a)
    i = a.n - 1
    while i >= len(e['plan']):
        e['plan'].append({'texto': 'Paso %d' % (len(e['plan']) + 1), 'estado': 'pendiente', 'nota': ''})
    p = e['plan'][i]
    p['estado'] = a.estado
    if a.nota is not None:
        p['nota'] = a.nota
    if a.texto:
        p['texto'] = a.texto
    if a.estado == 'hecho' and i + 1 < len(e['plan']) and e['plan'][i + 1]['estado'] == 'pendiente' \
            and not any(q['estado'] == 'en_curso' for q in e['plan']):
        e['plan'][i + 1]['estado'] = 'en_curso'
    actividad(e, 'Paso %d %s: %s%s' % (a.n, a.estado.replace('_', ' '), p['texto'], (' (' + a.nota + ')') if a.nota else ''))
    revisar_vigilada(c, e)
    guardar(c, e)
    return 0


EXT_IMG = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')


def agregar_imagen(c, e, ruta, titulo=None):
    ext = os.path.splitext(ruta)[1].lower()
    base = re.sub(r'[^\w\-]', '_', os.path.splitext(os.path.basename(ruta))[0])[:40]
    nombre = '%s_%s%s' % (dt.datetime.now().strftime('%H%M%S%f'), base, ext)
    shutil.copy2(ruta, os.path.join(c, '.progreso', 'img', nombre))
    e['imagenes'].append({'archivo': '.progreso/img/' + nombre, 'titulo': titulo or os.path.basename(ruta), 'hora': ahora()})
    for viejo in e['imagenes'][:-MAX_IMG]:
        try:
            os.remove(os.path.join(c, viejo['archivo']))
        except OSError:
            pass
    e['imagenes'] = e['imagenes'][-MAX_IMG:]
    actividad(e, 'Imagen: ' + (titulo or os.path.basename(ruta)))


def revisar_vigilada(c, e, maximo=6):
    """Suma al tablero las imagenes nuevas de la carpeta vigilada (renders, vistas, graficos). Devuelve cuantas sumo."""
    d = e.get('vigilar')
    if not d or not os.path.isdir(d):
        return 0
    visto, ahora_s, nuevas = e.get('visto', 0.0), time.time(), []
    for nombre in os.listdir(d):
        ruta = os.path.join(d, nombre)
        if not nombre.lower().endswith(EXT_IMG) or not os.path.isfile(ruta):
            continue
        st = os.stat(ruta)
        if st.st_mtime > visto and st.st_size > 0 and ahora_s - st.st_mtime > 0.5:  # completas, no a medio escribir
            nuevas.append((st.st_mtime, ruta))
    nuevas.sort()
    for mt, ruta in nuevas[-maximo:]:
        agregar_imagen(c, e, ruta)
    if nuevas:
        e['visto'] = nuevas[-1][0]
    return len(nuevas[-maximo:])


def cmd_imagen(a):
    c, e = con_tablero(a)
    if not os.path.isfile(a.ruta):
        print('No existe la imagen:', a.ruta)
        return 2
    agregar_imagen(c, e, a.ruta, a.titulo)
    guardar(c, e)
    return 0


def cmd_vigilar(a):
    c, e = con_tablero(a)
    if a.quitar:
        e.pop('vigilar', None)
        actividad(e, 'Deja de vigilar la carpeta de imágenes')
    else:
        if not a.dir or not os.path.isdir(a.dir):
            print('No existe la carpeta:', a.dir)
            return 2
        e['vigilar'], e['visto'] = os.path.abspath(a.dir), time.time()
        actividad(e, 'Vigila %s: cada imagen nueva aparece sola' % os.path.basename(e['vigilar'].rstrip('/\\')))
    guardar(c, e)
    return 0


def cmd_texto(a):
    c, e = con_tablero(a)
    t = a.texto if a.texto is not None else open(a.archivo, encoding='utf-8', errors='replace').read()
    e['texto'] = {'titulo': a.titulo or (os.path.basename(a.archivo) if a.archivo else 'Borrador'), 'html': md_a_html(t)}
    actividad(e, 'Borrador actualizado (%d palabras)' % len(t.split()))
    guardar(c, e)
    return 0


def cmd_simple(a):
    c, e = con_tablero(a)
    if a.cmd == 'pregunta':
        e['pregunta'] = a.texto
        actividad(e, 'Pregunta: ' + a.texto)
    elif a.cmd == 'responder':
        e['pregunta'] = ''
        actividad(e, 'Pregunta respondida')
    elif a.cmd == 'nota':
        actividad(e, a.texto)
    elif a.cmd == 'fin':
        e['terminado'] = True
        for p in e['plan']:
            if p['estado'] == 'en_curso':
                p['estado'] = 'hecho'
        actividad(e, 'Terminado' + ((': ' + a.nota) if a.nota else ''))
        if os.path.isfile(PUNTERO) and open(PUNTERO, encoding='utf-8').read().strip() == c:
            os.remove(PUNTERO)
    revisar_vigilada(c, e)
    guardar(c, e)
    return 0


SECRETOS = [
    (re.compile(r'(?i)(--?(?:clave|key|api[-_]?key|token|password|contrase(?:n|ñ)a|secret)[= ]+)\S+'), r'\1***'),
    (re.compile(r'(?i)\b([A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD)[A-Z0-9_]*\s*[=:]\s*)\S+'), r'\1***'),
    (re.compile(r'(?i)(bearer\s+)\S+'), r'\1***'),
    (re.compile(r'\bsk-[A-Za-z0-9_\-]{12,}'), 'sk-***'),
    (re.compile(r'\bAIza[0-9A-Za-z_\-]{20,}'), 'AIza***'),
    (re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}'), 'gh_***'),
]
VIGENCIA_HOOK_H = 12  # un tablero sin cambios hace mas de 12 h se considera abandonado y el hook no anota


def tapar(t):
    """Tapa claves y tokens antes de mostrarlos (el tablero puede verse en pantalla o en una captura)."""
    for patron, reemplazo in SECRETOS:
        t = patron.sub(reemplazo, t)
    return t


def texto_hook(d):
    h, ti = d.get('tool_name', '?'), d.get('tool_input') or {}
    ruta = ti.get('file_path') or ti.get('notebook_path')
    que = os.path.basename(str(ruta)) if ruta else str(ti.get('command') or ti.get('description') or '')
    que = tapar(re.sub(r'\s+', ' ', que))[:90]
    return ('%s %s' % (h.replace('mcp__', '').replace('__', ': '), que)).strip()


def cmd_hook():
    """Hook PostToolUse de Claude Code: anota la herramienta usada en el tablero activo. Nunca falla."""
    try:
        c = carpeta_activa()
        if not c:
            return 0
        if time.time() - os.path.getmtime(os.path.join(c, '.progreso', 'estado.json')) > VIGENCIA_HOOK_H * 3600:
            return 0
        e = leer(c)
        if e.get('terminado'):
            return 0
        actividad(e, texto_hook(json.loads(sys.stdin.read() or '{}')))
        revisar_vigilada(c, e)
        guardar(c, e)
    except Exception:
        pass
    return 0


def cmd_demo():
    d = tempfile.mkdtemp(prefix='progreso_demo_')
    viejo = open(PUNTERO, encoding='utf-8').read() if os.path.isfile(PUNTERO) else None
    try:
        ap = construir_parser()
        corre = lambda *xs: despachar(ap.parse_args(list(xs)))
        corre('init', 'Demo: soporte de motor', '--plan', 'Medidas|Modelo 3D|Informe|Revisión', '--carpeta', d)
        svg = os.path.join(d, 'vista.svg')
        with open(svg, 'w', encoding='utf-8') as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180"><rect width="320" height="180" fill="#222"/>'
                    '<rect x="90" y="60" width="140" height="70" fill="#c8102e"/><text x="12" y="24" fill="#eee" font-size="16">frente</text></svg>')
        corre('paso', '1', '--estado', 'hecho', '--nota', '120 x 80 x 6 mm')
        corre('imagen', svg, '--titulo', 'Vista de frente')
        corre('texto', '--texto', '# Informe\n## Cálculo\n- Carga: **2,5 kN**\n- Tensión: `σ = F/A`', '--titulo', 'Informe (borrador)')
        corre('pregunta', '¿El agujero va de 10 o de 12 mm?')
        renders = os.path.join(d, 'renders')
        os.makedirs(renders)
        viejo_png = os.path.join(renders, 'viejo.svg')
        with open(viejo_png, 'w', encoding='utf-8') as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>')
        os.utime(viejo_png, (time.time() - 60, time.time() - 60))
        corre('vigilar', renders)
        nuevo_svg = os.path.join(renders, 'vista_iso.svg')
        with open(nuevo_svg, 'w', encoding='utf-8') as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180"><rect width="320" height="180" fill="#333"/></svg>')
        visto = leer(d)['visto']
        os.utime(nuevo_svg, (visto + 0.05, visto + 0.05))  # escrita despues de empezar a vigilar
        time.sleep(0.6)  # el tablero no toma archivos de menos de 0,5 s (pueden estar a medio escribir)
        ev = leer(d)
        sumadas = revisar_vigilada(d, ev)
        guardar(d, ev)
        vig_ok = sumadas == 1 and leer(d)['imagenes'][-1]['titulo'] == 'vista_iso.svg' and revisar_vigilada(d, leer(d)) == 0
        h1 = texto_hook({'tool_name': 'Bash', 'tool_input': {'command': 'guias.py pal-clave gemini --clave AIzaSyA1234567890abcdefghijk'}})
        h2 = texto_hook({'tool_name': 'mcp__blender__execute_blender_code', 'tool_input': {'code': 'x'}})
        h3 = texto_hook({'tool_name': 'Edit', 'tool_input': {'file_path': os.path.join(d, 'informe.md')}})
        hook_ok = ('AIza' not in h1.replace('AIza***', '') and '--clave ***' in h1 and h2 == 'blender: execute_blender_code'
                   and h3 == 'Edit informe.md')
        e = leer(d)
        ok = (hook_ok and vig_ok and os.path.isfile(os.path.join(d, '.progreso', '.gitignore'))
              and e['plan'][0]['estado'] == 'hecho' and e['plan'][1]['estado'] == 'en_curso' and len(e['imagenes']) == 2
              and '<b>2,5 kN</b>' in e['texto']['html'] and e['pregunta'] and os.path.isfile(os.path.join(d, 'progreso.html'))
              and open(os.path.join(d, '.progreso', 'estado.js'), encoding='utf-8').read().startswith('window.PROGRESO'))
        corre('fin', '--nota', 'demo')
        print('Tablero de prueba:', os.path.join(d, 'progreso.html'))
        print('DEMO %s' % ('OK' if ok else 'FALLO'))
        return 0 if ok else 1
    finally:
        if viejo:
            with open(PUNTERO, 'w', encoding='utf-8') as f:
                f.write(viejo)


def construir_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd')
    p = sp.add_parser('init'); p.add_argument('titulo'); p.add_argument('--plan'); p.add_argument('--carpeta'); p.add_argument('--abrir', action='store_true')
    p.add_argument('--vigilar', help='carpeta de renders o graficos: cada imagen nueva aparece sola en el tablero')
    p = sp.add_parser('vigilar'); p.add_argument('dir', nargs='?'); p.add_argument('--quitar', action='store_true'); p.add_argument('--carpeta')
    p = sp.add_parser('paso'); p.add_argument('n', type=int); p.add_argument('--estado', default='hecho', choices=['pendiente', 'en_curso', 'hecho', 'error'])
    p.add_argument('--nota'); p.add_argument('--texto'); p.add_argument('--carpeta')
    p = sp.add_parser('imagen'); p.add_argument('ruta'); p.add_argument('--titulo'); p.add_argument('--carpeta')
    p = sp.add_parser('texto'); p.add_argument('archivo', nargs='?'); p.add_argument('--texto'); p.add_argument('--titulo'); p.add_argument('--carpeta')
    for n in ('pregunta', 'nota'):
        p = sp.add_parser(n); p.add_argument('texto'); p.add_argument('--carpeta')
    p = sp.add_parser('responder'); p.add_argument('--carpeta')
    p = sp.add_parser('fin'); p.add_argument('--nota'); p.add_argument('--carpeta')
    p = sp.add_parser('abrir'); p.add_argument('--carpeta')
    p = sp.add_parser('estado'); p.add_argument('--carpeta')
    sp.add_parser('demo'); sp.add_parser('hook')
    return ap


def despachar(a):
    if a.cmd == 'init':
        return cmd_init(a)
    if a.cmd == 'paso':
        return cmd_paso(a)
    if a.cmd == 'imagen':
        return cmd_imagen(a)
    if a.cmd == 'texto':
        if a.texto is None and not a.archivo:
            print('Falta el archivo o --texto')
            return 2
        return cmd_texto(a)
    if a.cmd in ('pregunta', 'responder', 'nota', 'fin'):
        return cmd_simple(a)
    if a.cmd == 'abrir':
        c, _ = con_tablero(a)
        abrir(os.path.join(c, 'progreso.html'))
        return 0
    if a.cmd == 'estado':
        c, e = con_tablero(a)
        hechos = sum(p['estado'] == 'hecho' for p in e['plan'])
        print('%s: %d de %d pasos, %d imagenes, %s' % (e['titulo'], hechos, len(e['plan']), len(e['imagenes']), os.path.join(c, 'progreso.html')))
        return 0
    if a.cmd == 'vigilar':
        return cmd_vigilar(a)
    if a.cmd == 'demo':
        return cmd_demo()
    if a.cmd == 'hook':
        return cmd_hook()
    construir_parser().print_help()
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except Exception:
        pass
    sys.exit(despachar(construir_parser().parse_args()))
