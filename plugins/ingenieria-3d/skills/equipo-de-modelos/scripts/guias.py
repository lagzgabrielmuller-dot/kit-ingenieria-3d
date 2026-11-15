#!/usr/bin/env python3
"""guias.py - consultar a otros modelos ("guias") desde Claude: uno solo o varios en paralelo (solo biblioteca estandar).

Claude lidera y es el unico que escribe; los guias leen y opinan. Guias:
  codex              Codex CLI (OpenAI, con la sesion de ChatGPT), en solo lectura
  gemini[:modelo]    Gemini CLI (Google, con la cuenta de Google o GEMINI_API_KEY), en modo plan (solo lectura)
  claude[:modelo]    Claude Code (claude -p) en modo plan; gasta el mismo cupo que Claude
  ollama:MODELO      modelo local de Ollama: gratis y privado, pero usa la GPU
  openrouter:ID      cualquier modelo de OpenRouter (clave OPENROUTER_API_KEY; los ':free' no cobran, con limite diario)
  eco, eco-falla     guias de prueba (no consultan a nadie)

Comandos:
  estado                                         que guias hay, sesiones, modelos locales, claves (sin mostrarlas) y GPU
  preguntar GUIA "pedido" [opciones]             consulta a un guia e imprime la respuesta
  consejo "pedido" --guias a,b,c [opciones]      consulta a varios a la vez y arma un informe Markdown para comparar
  pal-clave gemini|openrouter|openai [--quitar]  guarda (o quita) la clave en el MCP "pal" de Claude Code
                                                 (~/.claude.json); la pide oculta, nunca por argumento
  demo                                           prueba completa sin gastar cuota
Opciones de preguntar y consejo:
  --pedido-archivo F   el pedido desde un archivo (textos largos)
  --archivo F          adjunta un archivo de texto (se repite); nunca .env, claves ni credenciales
  --rol revisor|alternativa|libre   revisor (por defecto) busca errores y da su resultado
  --carpeta DIR        carpeta que los CLI pueden leer (solo lectura)
  --salida F.md        donde guardar la respuesta o el informe
  --tiempo S           tiempo maximo por guia, en segundos (600)
  --forzar             usar un modelo local aunque la GPU este ocupada o haya un juego abierto
Antes de enviar, las claves y tokens del pedido se reemplazan por ***.
Codigos de salida: 0 bien (en consejo: respondio al menos un guia), 1 ningun guia respondio, 2 error de uso.
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import getpass
import glob
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

ES_WIN = os.name == 'nt'
SIN_VENTANA = 0x08000000 if ES_WIN else 0  # CREATE_NO_WINDOW
TIEMPO = 600
MAX_ADJUNTOS = 150000  # caracteres en total de los archivos adjuntos
VRAM_MAX_MB = 3500     # si la GPU ya usa mas, no se carga un modelo local nuevo (salvo --forzar)
JUEGOS = {'cs2.exe', 'valorant-win64-shipping.exe', 'fortniteclient-win64-shipping.exe', 'rocketleague.exe',
          'gta5.exe', 'gta5_enhanced.exe', 'r5apex.exe', 'eldenring.exe', 'overwatch.exe', 'league of legends.exe',
          'minecraft.windows.exe', 'robloxplayerbeta.exe', 'dota2.exe', 'cod.exe', 'rainbowsix.exe'}
JUEGOS |= {j.strip().lower() for j in os.environ.get('GUIAS_JUEGOS', '').split(',') if j.strip()}
PROVEEDORES = {'gemini': 'GEMINI_API_KEY', 'openrouter': 'OPENROUTER_API_KEY', 'openai': 'OPENAI_API_KEY'}
PREFIJOS = {'gemini': 'AIza', 'openrouter': 'sk-or-', 'openai': 'sk-'}
PROHIBIDOS = re.compile(r'(?i)(^\.env(\..*)?$|\.(key|pem|p12|pfx|kdbx)$|^id_(rsa|ed25519|ecdsa)|credential|secret'
                        r'|^\.claude\.json$|^\.netrc$|^\.npmrc$|^\.git-credentials$)')
SECRETOS = [
    (re.compile(r'(?i)(--?(?:clave|key|api[-_]?key|token|password|contrase(?:n|ñ)a|secret)[= ]+)\S+'), r'\1***'),
    (re.compile(r'\b([A-Z][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD)[A-Z0-9_]*\s*[=:]\s*)\S+'), r'\1***'),
    (re.compile(r'(?i)(bearer\s+)[A-Za-z0-9._\-]{8,}'), r'\1***'),
    (re.compile(r'\bsk-[A-Za-z0-9_\-]{12,}'), 'sk-***'),
    (re.compile(r'\bAIza[0-9A-Za-z_\-]{20,}'), 'AIza***'),
    (re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}'), 'gh_***'),
    (re.compile(r'\bxox[abprs]-[A-Za-z0-9\-]{10,}'), 'xox-***'),
    (re.compile(r'\bAKIA[0-9A-Z]{16}\b'), 'AKIA***'),
]
ROLES = {
    'revisor': ('Sos un revisor técnico independiente. Otro asistente (Claude) hizo el trabajo de abajo y necesita un '
                'control antes de entregarlo. No ves su conversación: todo el contexto está en este pedido.\n'
                'Respondé en español, con las fórmulas en texto plano (sin LaTeX), en este orden:\n'
                '1) Veredicto: de acuerdo, con reparos o en desacuerdo.\n'
                '2) Errores encontrados, cada uno con su corrección.\n'
                '3) Supuestos dudosos o datos que faltan.\n'
                '4) Tu resultado, si difiere, con el cálculo.\n'
                'Sé concreto: lo que está bien, decilo en una línea.'),
    'alternativa': ('Sos un consultor técnico independiente. Otro asistente (Claude) está resolviendo lo de abajo y '
                    'quiere otra mirada. No ves su conversación: todo el contexto está en este pedido.\n'
                    'Respondé en español: proponé una forma distinta de resolverlo, con sus ventajas, desventajas y '
                    'riesgos, y decí cuál elegirías y por qué. Fórmulas en texto plano (sin LaTeX).'),
    'libre': '',
}
CANDADO_OLLAMA = threading.Lock()  # dos modelos locales a la vez no entran en la GPU


class GuiaError(Exception):
    pass


class UsoError(Exception):
    pass


# ---------------------------------------------------------------------------------------------- utilidades
def tapar(texto):
    """Reemplaza claves y tokens por ***. Devuelve (texto, cantidad de reemplazos)."""
    total = 0
    for patron, reemplazo in SECRETOS:
        texto, n = patron.subn(reemplazo, texto)
        total += n
    return texto, total


def ultimas(texto, n=6):
    lineas = [l for l in (texto or '').strip().splitlines() if l.strip()]
    return ' | '.join(lineas[-n:])[:600] or '(sin mensaje)'


def correr(cmd, entrada, carpeta, tiempo):
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=carpeta or None, creationflags=SIN_VENTANA)
    try:
        out, err = p.communicate(entrada.encode('utf-8'), timeout=tiempo)
    except subprocess.TimeoutExpired:
        if ES_WIN:
            subprocess.run(['taskkill', '/T', '/F', '/PID', str(p.pid)], capture_output=True, creationflags=SIN_VENTANA)
        else:
            p.kill()
        p.communicate()
        raise GuiaError('no respondió en %d s' % tiempo)
    return p.returncode, out.decode('utf-8', 'replace'), err.decode('utf-8', 'replace')


def salida_de(cmd, tiempo=30):
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=tiempo, creationflags=SIN_VENTANA)
        return (p.stdout + p.stderr).decode('utf-8', 'replace').strip()
    except Exception as ex:
        return '(%s)' % ex


def es_local(url):
    return re.match(r'https?://(localhost|127\.0\.0\.1|\[::1\])(:|/|$)', url) is not None


def http_json(url, cuerpo=None, tiempo=30, cabeceras=None):
    datos = json.dumps(cuerpo).encode('utf-8') if cuerpo is not None else None
    h = {'Content-Type': 'application/json'}
    h.update(cabeceras or {})
    req = urllib.request.Request(url, data=datos, headers=h)
    abridor = urllib.request.build_opener(urllib.request.ProxyHandler({})) if es_local(url) else urllib.request.build_opener()
    try:
        with abridor.open(req, timeout=tiempo) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as ex:
        raise GuiaError('HTTP %d: %s' % (ex.code, ex.read().decode('utf-8', 'replace')[:300]))
    except (urllib.error.URLError, OSError, ValueError) as ex:
        raise GuiaError('sin respuesta de %s (%s)' % (re.sub(r'(https?://[^/]+).*', r'\1', url), ex))


def url_ollama():
    h = os.environ.get('OLLAMA_HOST', '').strip() or '127.0.0.1:11434'
    if '://' not in h:
        h = 'http://' + h
    esquema, resto = h.split('://', 1)
    resto = resto.rstrip('/').replace('0.0.0.0', '127.0.0.1', 1)
    if ':' not in resto.split('/')[0].replace('[::1]', ''):
        resto += ':11434'
    return esquema + '://' + resto


def ruta_config():
    return os.path.join(os.path.expanduser('~'), '.claude.json')


def leer_pal(ruta=None):
    """El servidor MCP "pal" de ~/.claude.json: dict, None si no esta configurado, False si no hay archivo."""
    try:
        with open(ruta or ruta_config(), encoding='utf-8') as f:
            pal = (json.load(f).get('mcpServers') or {}).get('pal')
        return pal if isinstance(pal, dict) else None
    except (OSError, ValueError):
        return False


def clave_de(var):
    pal = leer_pal()
    return os.environ.get(var) or (pal.get('env') or {}).get(var, '') if pal else os.environ.get(var, '')


def juegos_abiertos():
    if not ES_WIN:
        return []
    txt = salida_de(['tasklist', '/FO', 'CSV', '/NH'])
    nombres = {l.split('","')[0].strip('"').lower() for l in txt.splitlines() if l.startswith('"')}
    return sorted(nombres & JUEGOS)


def vram():
    """(usados, total) en MB, o None si no hay nvidia-smi."""
    exe = shutil.which('nvidia-smi')
    if not exe:
        return None
    m = re.search(r'(\d+)\s*,\s*(\d+)', salida_de([exe, '--query-gpu=memory.used,memory.total',
                                                   '--format=csv,noheader,nounits']))
    return (int(m.group(1)), int(m.group(2))) if m else None


def separar(guia):
    tipo, _, modelo = guia.strip().partition(':')
    return tipo.strip().lower(), modelo.strip()


# ---------------------------------------------------------------------------------------------- guias
def guia_codex(texto, modelo, a):
    exe = shutil.which('codex')
    if not exe:
        raise GuiaError('Codex no está instalado o no está en el PATH (npm install -g @openai/codex)')
    fd, archivo = tempfile.mkstemp(prefix='guia_codex_', suffix='.md')
    os.close(fd)
    try:
        cmd = [exe, 'exec', '--skip-git-repo-check', '--sandbox', 'read-only', '--ephemeral', '-o', archivo]
        if modelo:
            cmd += ['-m', modelo]
        if a.carpeta:
            cmd += ['-C', a.carpeta]
        rc, out, err = correr(cmd + ['-'], texto, a.carpeta, a.tiempo)
        with open(archivo, encoding='utf-8', errors='replace') as f:
            respuesta = f.read().strip()
    finally:
        os.remove(archivo)
    if rc != 0 or not respuesta:
        raise GuiaError('codex terminó con código %d: %s' % (rc, ultimas(err or out)))
    return respuesta


def guia_gemini(texto, modelo, a):
    exe = shutil.which('gemini')
    if not exe:
        raise GuiaError('Gemini CLI no está instalado (npm install -g @google/gemini-cli; después `gemini` y '
                        '"Sign in with Google")')
    # el pedido va por la entrada estandar (sin problemas de comillas) y -p lo dispara en modo no interactivo
    cmd = [exe, '--approval-mode', 'plan', '--output-format', 'json', '-p', 'Responde al pedido de arriba, en espanol.']
    if modelo:
        cmd += ['-m', modelo]
    rc, out, err = correr(cmd, texto, a.carpeta, a.tiempo)
    try:
        j = json.loads(out[out.find('{'):]) if '{' in out else {}
    except ValueError:
        j = {}
    if j.get('error'):
        raise GuiaError('gemini: %s' % (j['error'].get('message') if isinstance(j['error'], dict) else j['error']))
    respuesta = (j.get('response') or ('' if j else out)).strip()
    if rc != 0 or not respuesta:
        raise GuiaError('gemini terminó con código %d: %s' % (rc, ultimas(err or out)))
    return respuesta


AYUDA_CLAUDE = {}


def guia_claude(texto, modelo, a):
    exe = shutil.which('claude')
    if not exe:
        raise GuiaError('Claude Code no está instalado o no está en el PATH')
    if 'txt' not in AYUDA_CLAUDE:
        AYUDA_CLAUDE['txt'] = salida_de([exe, '--help'])
    cmd = [exe, '-p', '--permission-mode', 'plan', '--output-format', 'text']
    if '--permission-prompts' in AYUDA_CLAUDE['txt']:
        cmd += ['--permission-prompts', 'none']  # lo que pediria permiso se rechaza solo: nunca se traba
    if modelo:
        cmd += ['--model', modelo]
    rc, out, err = correr(cmd, texto, a.carpeta, a.tiempo)
    if rc != 0 or not out.strip():
        raise GuiaError('claude terminó con código %d: %s' % (rc, ultimas(err or out)))
    return out.strip()


def guia_ollama(texto, modelo, a):
    if not modelo:
        raise UsoError('falta el modelo: ollama:<nombre> (ver `guias.py estado`)')
    base = url_ollama()
    nombres = [m.get('name', '') for m in http_json(base + '/api/tags', tiempo=10).get('models', [])]
    if modelo not in nombres and modelo + ':latest' not in nombres:
        raise GuiaError('Ollama no tiene el modelo %s; tiene: %s' % (modelo, ', '.join(nombres) or 'ninguno'))
    with CANDADO_OLLAMA:
        cargados = [m.get('name', '') for m in http_json(base + '/api/ps', tiempo=10).get('models', [])]
        ya = modelo in cargados or modelo + ':latest' in cargados
        if not a.forzar:
            j = juegos_abiertos()
            if j:
                raise GuiaError('hay un juego abierto (%s): no uso la GPU (--forzar para usarla igual)' % ', '.join(j))
            v = vram()
            if not ya and v and v[0] > VRAM_MAX_MB:
                raise GuiaError('la GPU ya usa %d de %d MB: no cargo otro modelo (--forzar para cargarlo igual)' % v)
        cuerpo = {'model': modelo, 'messages': [{'role': 'user', 'content': texto}], 'stream': False}
        if not ya:
            cuerpo['keep_alive'] = 0  # si lo cargamos nosotros, que se descargue al terminar y libere la GPU
        r = http_json(base + '/api/chat', cuerpo, tiempo=a.tiempo)
    respuesta = ((r.get('message') or {}).get('content') or '').strip()
    if not respuesta:
        raise GuiaError('Ollama devolvió una respuesta vacía')
    return respuesta


def guia_openrouter(texto, modelo, a):
    if not modelo:
        raise UsoError('falta el modelo: openrouter:<id> (por ejemplo, uno terminado en :free)')
    clave = clave_de('OPENROUTER_API_KEY')
    if not clave:
        raise GuiaError('falta la clave: `guias.py pal-clave openrouter` (o la variable OPENROUTER_API_KEY)')
    r = http_json('https://openrouter.ai/api/v1/chat/completions',
                  {'model': modelo, 'messages': [{'role': 'user', 'content': texto}]}, tiempo=a.tiempo,
                  cabeceras={'Authorization': 'Bearer ' + clave, 'X-Title': 'guias.py'})
    try:
        return r['choices'][0]['message']['content'].strip()
    except (KeyError, IndexError, TypeError, AttributeError):
        raise GuiaError('respuesta inesperada de OpenRouter: %s' % json.dumps(r)[:300])


def guia_eco(texto, modelo, a):
    return 'eco: recibí %d caracteres.\n\n%s' % (len(texto), texto)


def guia_eco_falla(texto, modelo, a):
    raise GuiaError('falla de prueba')


GUIAS = {'codex': guia_codex, 'gemini': guia_gemini, 'claude': guia_claude, 'ollama': guia_ollama,
         'openrouter': guia_openrouter, 'eco': guia_eco, 'eco-falla': guia_eco_falla}


def consultar(guia, texto, a):
    tipo, modelo = separar(guia)
    t0 = time.time()
    try:
        if tipo not in GUIAS:
            raise UsoError('guía desconocido: %s (hay: %s)' % (tipo, ', '.join(GUIAS)))
        return {'guia': guia, 'ok': True, 'texto': GUIAS[tipo](texto, modelo, a), 'seg': time.time() - t0}
    except (GuiaError, UsoError) as ex:
        return {'guia': guia, 'ok': False, 'error': str(ex), 'seg': time.time() - t0}
    except Exception as ex:  # un guia que falla no tira abajo a los demas
        return {'guia': guia, 'ok': False, 'error': '%s: %s' % (type(ex).__name__, ex), 'seg': time.time() - t0}


# ---------------------------------------------------------------------------------------------- pedido
def leer_adjuntos(rutas):
    partes, avisos, total = [], [], 0
    for r in rutas or []:
        nombre = os.path.basename(r)
        if PROHIBIDOS.search(nombre):
            raise UsoError('no se adjunta %s: parece un archivo de claves o credenciales' % nombre)
        if not os.path.isfile(r):
            raise UsoError('no existe el archivo %s' % r)
        with open(r, 'rb') as f:
            crudo = f.read(MAX_ADJUNTOS * 4)
        if b'\0' in crudo[:4096]:
            raise UsoError('%s no es de texto: pasá su carpeta con --carpeta para que la lean los CLI' % nombre)
        txt = crudo.decode('utf-8', errors='replace')
        resto = MAX_ADJUNTOS - total
        if resto <= 0:
            avisos.append('%s no se adjuntó: se llegó al límite de %d caracteres' % (nombre, MAX_ADJUNTOS))
            continue
        if len(txt) > resto:
            txt = txt[:resto]
            avisos.append('%s se recortó a %d caracteres' % (nombre, resto))
        total += len(txt)
        partes.append('### %s\n```\n%s\n```' % (nombre, txt))
    return partes, avisos


def armar_pedido(a):
    if a.pedido_archivo:
        with open(a.pedido_archivo, encoding='utf-8', errors='replace') as f:
            pedido = f.read()
    else:
        pedido = a.pedido or ''
    if not pedido.strip():
        raise UsoError('falta el pedido (texto o --pedido-archivo)')
    adjuntos, avisos = leer_adjuntos(a.archivo)
    partes = ([ROLES[a.rol]] if ROLES[a.rol] else []) + ['## Pedido\n' + pedido.strip()]
    if adjuntos:
        partes.append('## Archivos adjuntos\n' + '\n\n'.join(adjuntos))
    texto = '\n\n'.join(partes)
    if re.search(r'-----BEGIN [A-Z ]*PRIVATE KEY-----', texto):
        raise UsoError('el pedido trae una clave privada: no se envía')
    texto, n = tapar(texto)
    return pedido.strip(), texto, n, avisos


def informe(pedido, a, resultados, tapadas, avisos):
    ahora = dt.datetime.now().strftime('%Y-%m-%d %H:%M')
    resumen = ', '.join('%s (%s)' % (r['guia'], '%.0f s' % r['seg'] if r['ok'] else 'no respondió') for r in resultados)
    l = ['# Consejo de modelos guía', '', '- Fecha: %s' % ahora, '- Rol pedido: %s' % a.rol, '- Guías: %s' % resumen,
         '- Claves o tokens tapados antes de enviar: %d' % tapadas]
    l += ['- Aviso: %s' % x for x in avisos]
    l += ['', '## Pedido', '', tapar(pedido)[0], '']
    for r in resultados:
        if r['ok']:
            l += ['## Respuesta de %s (%.0f s)' % (r['guia'], r['seg']), '', r['texto'], '']
        else:
            l += ['## %s: no respondió' % r['guia'], '', r['error'], '']
    l += ['## Cómo combinar (para Claude)', '',
          '1. Comparar punto por punto con la solución propia: qué coincide, qué falta, qué se contradice.',
          '2. Si difieren números, recalcular con código para decidir; no promediar ni elegir por mayoría.',
          '3. Contarle al usuario qué coincidió, qué corrigió cada guía (diciendo de quién vino) y la conclusión.',
          '4. Si un guía encontró un error real, corregirlo en el entregable y decirlo.', '']
    return '\n'.join(l)


def guardar(ruta, texto):
    carpeta = os.path.dirname(os.path.abspath(ruta))
    os.makedirs(carpeta, exist_ok=True)
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(texto)


# ---------------------------------------------------------------------------------------------- comandos
def cmd_preguntar(a):
    pedido, texto, tapadas, avisos = armar_pedido(a)
    for x in avisos:
        print('Aviso:', x, file=sys.stderr)
    r = consultar(a.guia, texto, a)
    if not r['ok']:
        print('%s no respondió: %s' % (a.guia, r['error']), file=sys.stderr)
        return 1
    if a.salida:
        guardar(a.salida, r['texto'] + '\n')
    print(r['texto'])
    if tapadas:
        print('\n(se taparon %d claves o tokens antes de enviar)' % tapadas, file=sys.stderr)
    return 0


def cmd_consejo(a):
    guias = [g.strip() for g in (a.guias or '').split(',') if g.strip()]
    if not guias:
        raise UsoError('faltan los guías: --guias codex,ollama:<modelo>,... (ver `guias.py estado`)')
    pedido, texto, tapadas, avisos = armar_pedido(a)
    with cf.ThreadPoolExecutor(max_workers=len(guias)) as ex:
        resultados = list(ex.map(lambda g: consultar(g, texto, a), guias))
    doc = informe(pedido, a, resultados, tapadas, avisos)
    salida = a.salida or os.path.join(tempfile.gettempdir(), 'consejo_%s.md' % dt.datetime.now().strftime('%Y%m%d_%H%M%S'))
    guardar(salida, doc)
    print(doc)
    print('Informe guardado en: %s' % salida)
    return 0 if any(r['ok'] for r in resultados) else 1


def cmd_estado(a):
    filas = []
    exe = shutil.which('codex')
    if exe:
        ses = salida_de([exe, 'login', 'status']).splitlines()
        ver = (salida_de([exe, '--version']).splitlines() or ['?'])[0]
        filas.append(('codex', 'listo' if any('logged in' in x.lower() for x in ses) else 'sin sesión',
                      '%s · %s' % (ver, ses[0] if ses else 'sesión: ?')))
    else:
        filas.append(('codex', 'falta', 'npm install -g @openai/codex; después `codex login` con la cuenta de ChatGPT'))
    exe = shutil.which('gemini')
    if exe:
        filas.append(('gemini', 'instalado', '%s · si no inició sesión, correr `gemini` una vez y elegir "Sign in with '
                      'Google"' % (salida_de([exe, '--version']).splitlines() or ['?'])[0]))
    else:
        filas.append(('gemini', 'falta', 'npm install -g @google/gemini-cli; después `gemini` y "Sign in with Google" '
                      '(gratis: 60 pedidos/min y 1000/día)'))
    exe = shutil.which('claude')
    filas.append(('claude', 'listo' if exe else 'falta', ((salida_de([exe, '--version']).splitlines() or ['?'])[0] +
                  ' · gasta el mismo cupo que Claude') if exe else 'https://claude.com/claude-code'))
    try:
        base = url_ollama()
        modelos = [m.get('name', '') for m in http_json(base + '/api/tags', tiempo=5).get('models', [])]
        cargados = {m.get('name', '') for m in http_json(base + '/api/ps', tiempo=5).get('models', [])}
        filas.append(('ollama', 'listo' if modelos else 'sin modelos',
                      ', '.join(m + (' (cargado)' if m in cargados else '') for m in modelos) + '  → ollama:<nombre>'))
    except GuiaError:
        filas.append(('ollama', 'apagado', 'Ollama no responde en %s' % url_ollama()))
    filas.append(('openrouter', 'listo' if clave_de('OPENROUTER_API_KEY') else 'sin clave',
                  'openrouter:<id> (los :free son gratis con límite diario)' if clave_de('OPENROUTER_API_KEY')
                  else '`guias.py pal-clave openrouter` (o la variable OPENROUTER_API_KEY)'))
    print('Guías:')
    for g, est, det in filas:
        print('  %-11s %-11s %s' % (g, est, det))
    pal = leer_pal()
    if pal:
        env = pal.get('env') or {}
        claves = [v for v in PROVEEDORES.values() if env.get(v)]
        print('PAL (Claude Code): configurado · claves: %s · modelo por defecto: %s'
              % (', '.join(claves) or 'ninguna', env.get('DEFAULT_MODEL', 'auto')))
    else:
        print('PAL (Claude Code): %s' % ('no configurado en ~/.claude.json' if pal is None else 'no hay ~/.claude.json'))
    v = vram()
    j = juegos_abiertos()
    print('GPU: %s · juegos abiertos: %s' % ('%d de %d MB usados' % v if v else 'sin nvidia-smi', ', '.join(j) or 'ninguno'))
    return 0


def claude_code_abierto():
    if ES_WIN:
        txt = salida_de(['powershell', '-NoProfile', '-Command',
                         "Get-Process -Name claude -ErrorAction SilentlyContinue | ForEach-Object { $_.Path }"])
        return any('.local' in l.lower() and l.lower().endswith('claude.exe') for l in txt.splitlines())
    return bool(salida_de(['pgrep', '-x', 'claude']).strip().isdigit())


def pedir_clave(proveedor):
    if os.environ.get('GUIAS_CLAVE'):
        return os.environ['GUIAS_CLAVE'].strip()
    if not sys.stdin.isatty():
        return sys.stdin.readline().strip()
    return getpass.getpass('Pegá la clave de %s (no se ve al escribir) y Enter: ' % proveedor).strip()


def cmd_pal_clave(a):
    var = PROVEEDORES[a.proveedor]
    ruta = a.config or ruta_config()
    if not a.config and not a.igual and claude_code_abierto():
        raise UsoError('Claude Code está abierto y podría pisar el cambio: cerralo y volvé a correr esto (o --igual)')
    try:
        with open(ruta, encoding='utf-8') as f:
            datos = json.load(f)
    except (OSError, ValueError) as ex:
        raise UsoError('no se pudo leer %s: %s' % (ruta, ex))
    pal = (datos.get('mcpServers') or {}).get('pal')
    if not isinstance(pal, dict):
        raise UsoError('%s no tiene un servidor MCP "pal" (instalarlo primero)' % ruta)
    env = pal.setdefault('env', {})
    if a.quitar:
        if var not in env:
            print('%s no estaba guardada.' % var)
            return 0
        env.pop(var)
    else:
        clave = pedir_clave(a.proveedor)
        if not clave:
            raise UsoError('no se pegó ninguna clave')
        if not clave.startswith(PREFIJOS[a.proveedor]) and not a.igual:
            raise UsoError('eso no parece una clave de %s (suele empezar con %s): revisala o usá --igual'
                           % (a.proveedor, PREFIJOS[a.proveedor]))
        env[var] = clave
    copia = '%s.copia-%s' % (ruta, dt.datetime.now().strftime('%Y%m%d-%H%M%S'))
    shutil.copy2(ruta, copia)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(ruta)), prefix='.tmp_guias_')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    os.replace(tmp, ruta)
    if a.quitar:
        print('Listo: se quitó %s del MCP pal. Copia de antes: %s' % (var, copia))
    else:
        print('Listo: %s guardada en el MCP pal de %s (%s…, %d caracteres). Copia de antes: %s'
              % (var, ruta, env[var][:4], len(env[var]), copia))
    print('Reiniciá Claude Code para que PAL la tome; `guias.py estado` lo confirma.')
    return 0


# ---------------------------------------------------------------------------------------------- demo
class OllamaFalso(http.server.BaseHTTPRequestHandler):
    def log_message(self, *x):
        pass

    def responder(self, obj):
        b = json.dumps(obj).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == '/api/tags':
            self.responder({'models': [{'name': 'prueba:latest'}]})
        else:
            self.responder({'models': []})

    def do_POST(self):
        largo = int(self.headers.get('Content-Length', 0))
        cuerpo = json.loads(self.rfile.read(largo).decode('utf-8'))
        OllamaFalso.ultimo = cuerpo
        self.responder({'message': {'role': 'assistant', 'content': 'De acuerdo: 50 MPa.'}})


def cmd_demo():
    d = tempfile.mkdtemp(prefix='guias_demo_')
    viejo_host = os.environ.get('OLLAMA_HOST')
    servidor = http.server.HTTPServer(('127.0.0.1', 0), OllamaFalso)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    os.environ['OLLAMA_HOST'] = '127.0.0.1:%d' % servidor.server_port
    chequeos = []
    try:
        adj = os.path.join(d, 'calculo.md')
        with open(adj, 'w', encoding='utf-8') as f:
            f.write('Tensión: σ = F/A = 2500 N / 50 mm² = 50 MPa\nexport GEMINI_API_KEY=AIzaSyA1234567890abcdefghijklmnopqrs\n'
                    'Chaveta (key): 8 x 7 mm\n')
        with open(os.path.join(d, '.env'), 'w') as f:
            f.write('X=1\n')
        try:
            leer_adjuntos([os.path.join(d, '.env')])
            chequeos.append(('un .env no se adjunta', False))
        except UsoError:
            chequeos.append(('un .env no se adjunta', True))
        inf = os.path.join(d, 'informe.md')
        rc = main(['consejo', '¿Está bien la tensión? Pieza de acero.', '--guias', 'eco,eco-falla,ollama:prueba',
                   '--archivo', adj, '--salida', inf, '--forzar'], silencio=True)
        with open(inf, encoding='utf-8') as f:
            txt = f.read()
        chequeos.append(('consejo responde y arma el informe', rc == 0 and '## Respuesta de eco' in txt
                         and '## eco-falla: no respondió' in txt and '## Respuesta de ollama:prueba' in txt))
        chequeos.append(('las claves se tapan antes de enviar', 'AIzaSy' not in txt and 'GEMINI_API_KEY=***' in txt
                         and 'AIzaSy' not in json.dumps(OllamaFalso.ultimo)))
        chequeos.append(('el texto técnico no se toca', 'Chaveta (key): 8 x 7 mm' in txt and '50 MPa' in txt))
        chequeos.append(('un modelo local no queda cargado', OllamaFalso.ultimo.get('keep_alive') == 0))
        rc = main(['consejo', 'x', '--guias', 'eco-falla', '--salida', os.path.join(d, 'i2.md')], silencio=True)
        chequeos.append(('sin respuestas devuelve 1', rc == 1))
        cfg = os.path.join(d, 'claude.json')
        with open(cfg, 'w', encoding='utf-8') as f:
            json.dump({'mcpServers': {'pal': {'command': 'uvx', 'env': {'DEFAULT_MODEL': 'x'}}}, 'otro': 1}, f)
        os.environ['GUIAS_CLAVE'] = 'sk-or-v1-' + 'a' * 64
        rc = main(['pal-clave', 'openrouter', '--config', cfg], silencio=True)
        with open(cfg, encoding='utf-8') as f:
            j = json.load(f)
        chequeos.append(('pal-clave guarda la clave con copia', rc == 0 and j['otro'] == 1
                         and j['mcpServers']['pal']['env'].get('OPENROUTER_API_KEY', '').startswith('sk-or-')
                         and j['mcpServers']['pal']['env']['DEFAULT_MODEL'] == 'x' and glob.glob(cfg + '.copia-*')))
        os.environ['GUIAS_CLAVE'] = 'mi-contraseña'
        rc = main(['pal-clave', 'gemini', '--config', cfg], silencio=True)
        chequeos.append(('pal-clave rechaza algo que no es una clave', rc == 2))
        rc = main(['pal-clave', 'openrouter', '--config', cfg, '--quitar'], silencio=True)
        with open(cfg, encoding='utf-8') as f:
            j = json.load(f)
        chequeos.append(('pal-clave --quitar la borra', rc == 0 and 'OPENROUTER_API_KEY' not in j['mcpServers']['pal']['env']))
        chequeos.append(('separar guías con dos puntos', separar('openrouter:org/modelo:free') == ('openrouter', 'org/modelo:free')
                         and separar('ollama:gemma4:12b') == ('ollama', 'gemma4:12b')))
    finally:
        servidor.shutdown()
        os.environ.pop('GUIAS_CLAVE', None)
        if viejo_host is None:
            os.environ.pop('OLLAMA_HOST', None)
        else:
            os.environ['OLLAMA_HOST'] = viejo_host
        shutil.rmtree(d, ignore_errors=True)
    for nombre, ok in chequeos:
        print('  %s %s' % ('ok ' if ok else 'MAL', nombre))
    bien = all(ok for _, ok in chequeos)
    print('DEMO %s' % ('OK' if bien else 'FALLO'))
    return 0 if bien else 1


# ---------------------------------------------------------------------------------------------- principal
def construir_parser():
    ap = argparse.ArgumentParser(prog='guias.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('estado')
    for nombre in ('preguntar', 'consejo'):
        p = sp.add_parser(nombre)
        if nombre == 'preguntar':
            p.add_argument('guia')
        p.add_argument('pedido', nargs='?')
        if nombre == 'consejo':
            p.add_argument('--guias', required=True)
        p.add_argument('--pedido-archivo')
        p.add_argument('--archivo', action='append')
        p.add_argument('--rol', default='revisor', choices=sorted(ROLES))
        p.add_argument('--carpeta')
        p.add_argument('--salida')
        p.add_argument('--tiempo', type=int, default=TIEMPO)
        p.add_argument('--forzar', action='store_true')
    p = sp.add_parser('pal-clave')
    p.add_argument('proveedor', choices=sorted(PROVEEDORES))
    p.add_argument('--quitar', action='store_true')
    p.add_argument('--igual', action='store_true', help='guardar aunque no parezca una clave o Claude Code este abierto')
    p.add_argument('--config', help='otro archivo en lugar de ~/.claude.json (para probar)')
    sp.add_parser('demo')
    return ap


def main(argv=None, silencio=False):
    a = construir_parser().parse_args(argv)
    real, real_err = sys.stdout, sys.stderr
    if silencio:
        sys.stdout = sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    try:
        if a.cmd == 'demo':
            sys.stdout, sys.stderr = real, real_err
            return cmd_demo()
        if getattr(a, 'carpeta', None):
            a.carpeta = os.path.abspath(a.carpeta)
            if not os.path.isdir(a.carpeta):
                raise UsoError('no existe la carpeta %s' % a.carpeta)
        return {'estado': cmd_estado, 'preguntar': cmd_preguntar, 'consejo': cmd_consejo,
                'pal-clave': cmd_pal_clave}[a.cmd](a)
    except UsoError as ex:
        print('guias.py: %s' % ex, file=sys.stderr)
        return 2
    finally:
        if silencio:
            sys.stdout.close()
            sys.stdout, sys.stderr = real, real_err


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
