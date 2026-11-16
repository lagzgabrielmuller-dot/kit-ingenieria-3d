#!/usr/bin/env python3
"""Arma los pedidos (requests) del conector de Google Docs para escribir un informe en vivo.

Claude escribe cada sección en un texto con marcas simples; este programa calcula los
índices (en unidades UTF-16, como los cuenta Google Docs) y devuelve el JSON listo para
`update_doc`: texto, estilos de título, listas, fórmulas centradas, superíndices, enlaces,
espacio entre párrafos, tablas y figuras. Solo biblioteca estándar, Python 3.9 o más.

    python docs_bloques.py texto seccion.txt --inicio N --rev REVISION [--doc-vacio] [--despues-de-lista]
    python docs_bloques.py tabla --en N --filas filas.json --rev REVISION [--encabezado] [--anchos 140,226,85]
    python docs_bloques.py figuras --datos figuras.json --rev REVISION
    python docs_bloques.py indices lectura.json [--buscar "Figura 1."]
    python docs_bloques.py demo

Marcas del texto (un párrafo por línea; las líneas vacías no cuentan):
    TITULO: ...  SUBTITULO: ...  # Título 1  ## Título 2  ### Título 3
    - viñeta     1. numerada     $$ fórmula centrada     EPIGRAFE: Figura 1. ...
    **negrita**  *cursiva*  ^{superíndice}  _{subíndice}  [[texto|https://...]]  ~ = espacio que no corta
"""
import argparse
import json
import re
import sys

MARCA = re.compile(r'\*\*(.+?)\*\*|\*(.+?)\*|\^\{(.+?)\}|_\{(.+?)\}|\[\[(.+?)\|(.+?)\]\]')
NBSP = ' '
TIPOS_LINEA = [
    ('TITULO:', 'TITLE'), ('SUBTITULO:', 'SUBTITLE'), ('EPIGRAFE:', 'EPIGRAFE'),
    ('### ', 'HEADING_3'), ('## ', 'HEADING_2'), ('# ', 'HEADING_1'),
    ('$$ ', 'FORMULA'), ('- ', 'VINETA'), ('* ', 'VINETA'),
]


def u16(s):
    return len(s.encode('utf-16-le')) // 2


def desarmar(t):
    """Texto con marcas -> (texto plano, [(ini, fin, estilo, campo)]) con índices UTF-16 relativos."""
    t = t.replace('~', NBSP)
    plano, marcas, pos = '', [], 0
    for m in MARCA.finditer(t):
        plano += t[pos:m.start()]
        ini = u16(plano)
        if m.group(1) is not None:
            plano += m.group(1); marcas.append((ini, u16(plano), {'bold': True}, 'bold'))
        elif m.group(2) is not None:
            plano += m.group(2); marcas.append((ini, u16(plano), {'italic': True}, 'italic'))
        elif m.group(3) is not None:
            plano += m.group(3); marcas.append((ini, u16(plano), {'baselineOffset': 'SUPERSCRIPT'}, 'baselineOffset'))
        elif m.group(4) is not None:
            plano += m.group(4); marcas.append((ini, u16(plano), {'baselineOffset': 'SUBSCRIPT'}, 'baselineOffset'))
        else:
            plano += m.group(5); marcas.append((ini, u16(plano), {'link': {'url': m.group(6)}}, 'link'))
        pos = m.end()
    return plano + t[pos:], marcas


def leer_bloques(texto):
    bloques = []
    for linea in texto.splitlines():
        linea = linea.rstrip()
        if not linea.strip():
            continue
        tipo, cuerpo = 'NORMAL_TEXT', linea
        for prefijo, t in TIPOS_LINEA:
            if linea.startswith(prefijo):
                tipo, cuerpo = t, linea[len(prefijo):].strip()
                break
        else:
            m = re.match(r'^\d+\.\s+', linea)
            if m:
                tipo, cuerpo = 'NUMERO', linea[m.end():]
        bloques.append((tipo, cuerpo))
    return bloques


def con_tab(d, tab):
    if tab:
        d['tabId'] = tab
    return d


def pedidos_texto(bloques, inicio, doc_vacio=False, despues_de_lista=False, tab=None, espacio=8.0,
                  color_titulo=None):
    planos = [desarmar(c) for _, c in bloques]
    texto = '\n'.join(p for p, _ in planos)
    pos = inicio
    if not doc_vacio:
        texto, pos = '\n' + texto, inicio + 1
    reqs = [{'insertText': {'location': con_tab({'index': inicio}, tab), 'text': texto}}]
    fin_total = inicio + u16(texto)
    if despues_de_lista:   # el texto nuevo nace de un ítem de lista: sacarle viñeta y sangría heredadas
        rango = con_tab({'startIndex': pos, 'endIndex': fin_total + 1}, tab)
        reqs.append({'deleteParagraphBullets': {'range': dict(rango)}})
        reqs.append({'updateParagraphStyle': {'range': dict(rango), 'paragraphStyle': {},
                                              'fields': 'indentStart,indentFirstLine'}})
    parr, letra, listas, con_espacio, todos = [], [], [], [], []
    grupo = None
    for (tipo, _), (plano, marcas) in zip(bloques, planos):
        s, e = pos, pos + u16(plano)
        pos = e + 1
        nombre = 'NORMAL_TEXT' if tipo in ('VINETA', 'NUMERO', 'FORMULA', 'EPIGRAFE') else tipo
        ps, campos = {'namedStyleType': nombre}, ['namedStyleType']
        if tipo in ('FORMULA', 'EPIGRAFE'):
            ps['alignment'] = 'CENTER'; campos.append('alignment')
        rango = con_tab({'startIndex': s, 'endIndex': e + 1}, tab)
        parr.append({'updateParagraphStyle': {'range': rango, 'paragraphStyle': ps, 'fields': ','.join(campos)}})
        todos.append((s, e))
        if e > s:
            if nombre == 'NORMAL_TEXT':
                letra.append({'updateTextStyle': {'range': con_tab({'startIndex': s, 'endIndex': e}, tab), 'textStyle': {},
                                                  'fields': 'bold,italic,foregroundColor,fontSize,baselineOffset,link'}})
            if tipo == 'EPIGRAFE':
                letra.append({'updateTextStyle': {
                    'range': con_tab({'startIndex': s, 'endIndex': e}, tab),
                    'textStyle': {'italic': True, 'fontSize': {'magnitude': 9.5, 'unit': 'PT'},
                                  'foregroundColor': {'color': {'rgbColor': {'red': 0.35, 'green': 0.35, 'blue': 0.35}}}},
                    'fields': 'italic,fontSize,foregroundColor'}})
            if tipo == 'TITLE' and color_titulo:
                r, g, b = color_titulo
                letra.append({'updateTextStyle': {
                    'range': con_tab({'startIndex': s, 'endIndex': e}, tab),
                    'textStyle': {'foregroundColor': {'color': {'rgbColor': {'red': r, 'green': g, 'blue': b}}}},
                    'fields': 'foregroundColor'}})
        for i0, i1, estilo, campo in marcas:
            letra.append({'updateTextStyle': {'range': con_tab({'startIndex': s + i0, 'endIndex': s + i1}, tab),
                                              'textStyle': estilo, 'fields': campo}})
        if tipo in ('VINETA', 'NUMERO'):
            if grupo and grupo['tipo'] == tipo and grupo['fin'] + 1 == s:
                grupo['fin'] = e
            else:
                grupo = {'tipo': tipo, 'ini': s, 'fin': e}
                listas.append(grupo)
        else:
            grupo = None
            if nombre == 'NORMAL_TEXT':
                con_espacio.append(e)
    for g in listas:
        preset = 'BULLET_DISC_CIRCLE_SQUARE' if g['tipo'] == 'VINETA' else 'NUMBERED_DECIMAL_ALPHA_ROMAN'
        parr.append({'createParagraphBullets': {'range': con_tab({'startIndex': g['ini'], 'endIndex': g['fin'] + 1}, tab),
                                                'bulletPreset': preset}})
        con_espacio.append(g['fin'])          # espacio solo debajo del último ítem
    con_espacio = set(con_espacio)
    espacio_req = []
    for s, e in todos:   # lo que no lleva espacio vuelve al de su estilo (si no, hereda el del párrafo partido)
        if e not in con_espacio:
            espacio_req.append({'updateParagraphStyle': {'range': con_tab({'startIndex': s, 'endIndex': e + 1}, tab),
                                                         'paragraphStyle': {}, 'fields': 'spaceBelow'}})
    for s, e in todos:
        if e in con_espacio:
            espacio_req.append({'updateParagraphStyle': {
                'range': con_tab({'startIndex': s, 'endIndex': e + 1}, tab),
                'paragraphStyle': {'spaceBelow': {'magnitude': espacio, 'unit': 'PT'}}, 'fields': 'spaceBelow'}})
    return reqs + parr + letra + espacio_req, fin_total


def pedidos_tabla(filas, en, tab=None, encabezado=True, color_encabezado=None, anchos=None):
    """Tabla después del párrafo que termina en `en` (su endIndex - 1), llena en el mismo pedido."""
    R, C = len(filas), max(len(f) for f in filas)
    reqs = [{'insertTable': {'rows': R, 'columns': C, 'location': con_tab({'index': en}, tab)}},
            {'updateParagraphStyle': {'range': con_tab({'startIndex': en + 3 + R * (2 * C + 1),
                                                        'endIndex': en + 4 + R * (2 * C + 1)}, tab),
                                      'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'}, 'fields': 'namedStyleType'}}]
    celdas = []
    for r in range(R):
        for c in range(C):
            celdas.append((en + 4 + r * (2 * C + 1) + 2 * c, r, c, (filas[r][c] if c < len(filas[r]) else '').replace('~', NBSP)))
    for idx, _, _, txt in sorted(celdas, reverse=True):     # de la última celda a la primera
        if txt:
            reqs.append({'insertText': {'location': con_tab({'index': idx}, tab), 'text': txt}})
    if encabezado:
        corrido = 0
        for c in range(C):
            idx = en + 4 + 2 * c + corrido
            txt = filas[0][c] if c < len(filas[0]) else ''
            if txt:
                reqs.append({'updateTextStyle': {'range': con_tab({'startIndex': idx, 'endIndex': idx + u16(txt)}, tab),
                                                 'textStyle': {'bold': True}, 'fields': 'bold'}})
            corrido += u16(txt.replace('~', NBSP))
    inicio_tabla = con_tab({'index': en + 1}, tab)
    if color_encabezado:
        r_, g_, b_ = color_encabezado
        reqs.append({'updateTableCellStyle': {
            'tableRange': {'tableCellLocation': {'tableStartLocation': dict(inicio_tabla), 'rowIndex': 0, 'columnIndex': 0},
                           'rowSpan': 1, 'columnSpan': C},
            'tableCellStyle': {'backgroundColor': {'color': {'rgbColor': {'red': r_, 'green': g_, 'blue': b_}}}},
            'fields': 'backgroundColor'}})
    for c, ancho in enumerate(anchos or []):
        reqs.append({'updateTableColumnProperties': {
            'tableStartLocation': dict(inicio_tabla), 'columnIndices': [c],
            'tableColumnProperties': {'widthType': 'FIXED_WIDTH', 'width': {'magnitude': ancho, 'unit': 'PT'}},
            'fields': 'width,widthType'}})
    return reqs


def pedidos_figuras(figuras, tab=None):
    """Cada figura va en su propio párrafo, arriba de su epígrafe (`epigrafe` = startIndex del epígrafe)."""
    orden = sorted(figuras, key=lambda f: f['epigrafe'])
    reqs = []
    for f in reversed(orden):                               # de abajo hacia arriba: no corre los índices pendientes
        tam = {'width': {'magnitude': f.get('ancho', 430), 'unit': 'PT'},
               'height': {'magnitude': f.get('alto', 242), 'unit': 'PT'}}
        reqs.append({'insertInlineImage': {'location': con_tab({'index': f['epigrafe']}, tab), 'uri': f['uri'], 'objectSize': tam}})
        reqs.append({'insertText': {'location': con_tab({'index': f['epigrafe'] + 1}, tab), 'text': '\n'}})
    for k, f in enumerate(orden):                           # cada figura anterior corre 2 posiciones a las siguientes
        s = f['epigrafe'] + 2 * k
        reqs.append({'updateParagraphStyle': {
            'range': con_tab({'startIndex': s, 'endIndex': s + 2}, tab),
            'paragraphStyle': {'keepWithNext': True, 'spaceAbove': {'magnitude': 4, 'unit': 'PT'},
                               'spaceBelow': {'magnitude': 2, 'unit': 'PT'}},
            'fields': 'keepWithNext,spaceAbove,spaceBelow'}})
    return reqs


def recorrer(contenido, salida):
    for el in contenido:
        if 'paragraph' in el:
            p = el['paragraph']
            txt = ''.join(x.get('textRun', {}).get('content', '') for x in p.get('elements', []))
            salida.append({'ini': el.get('startIndex', 0), 'fin': el['endIndex'], 'texto': txt,
                           'estilo': p.get('paragraphStyle', {}).get('namedStyleType', ''), 'lista': 'bullet' in p})
        elif 'table' in el:
            salida.append({'ini': el['startIndex'], 'fin': el['endIndex'], 'texto': '[TABLA]', 'estilo': 'TABLE', 'lista': False})
    return salida


def indices(lectura, buscar=()):
    d = lectura.get('content', lectura)
    tabs = d.get('tabs')
    cuerpo = tabs[0]['documentTab']['body']['content'] if tabs else d['body']['content']
    parrafos = recorrer(cuerpo, [])
    ultimo = parrafos[-1]
    info = {'revisionId': d.get('revisionId'), 'fin_cuerpo': ultimo['fin'],
            'inicio_para_agregar': ultimo['fin'] - 1, 'ultimo_vacio': ultimo['texto'] == '\n',
            'ultimo_es_lista': ultimo['lista'], 'encontrados': []}
    for b in buscar:
        for p in parrafos:
            if b in p['texto']:
                info['encontrados'].append({'buscado': b, 'ini': p['ini'], 'fin': p['fin'], 'estilo': p['estilo'],
                                            'texto': p['texto'][:70].rstrip('\n')})
    return info


def salida_json(reqs, rev):
    return {'requests': reqs, 'writeControl': {'requiredRevisionId': rev}}


# ---------------------------------------------------------------- demo con verificación

def simular(reqs):
    """Aplica los insertText a un texto de prueba (índice 1 = primer carácter) para revisar los rangos."""
    doc = ['\x00', '\n']
    for r in reqs:
        if 'insertText' in r:
            i = r['insertText']['location']['index']
            doc[i:i] = list(r['insertText']['text'])
    return ''.join(doc)


def demo(_args):
    fallas = []
    seccion = ('TITULO: El Sol: nuestra estrella\n'
               '# Energía\n'
               'La potencia es P = 3,828 × 10^{26}~W según la **ficha del NSSDC**.\n'
               '- **Núcleo**: hasta 0,25~R.\n'
               '- **Zona radiativa**: hasta 0,7~R.\n'
               '$$ E = Δm · c^{2}\n'
               'EPIGRAFE: Figura 1. Render del modelo.\n')
    bloques = leer_bloques(seccion)
    reqs, fin = pedidos_texto(bloques, 1, doc_vacio=True, color_titulo=(0.8, 0.33, 0.0))
    doc = simular(reqs)
    tipos = [t for t, _ in bloques]
    print('1) bloques leídos:', ', '.join(tipos))
    if tipos != ['TITLE', 'HEADING_1', 'NORMAL_TEXT', 'VINETA', 'VINETA', 'FORMULA', 'EPIGRAFE']:
        fallas.append('tipos de línea')
    esperados = {'SUPERSCRIPT': ['26', '2'], 'bold': ['ficha del NSSDC', 'Núcleo', 'Zona radiativa']}
    vistos = {'SUPERSCRIPT': [], 'bold': []}
    for r in reqs:
        st = r.get('updateTextStyle')
        if st and st['textStyle'].get('baselineOffset') == 'SUPERSCRIPT':
            vistos['SUPERSCRIPT'].append(doc[st['range']['startIndex']:st['range']['endIndex']])
        if st and st['textStyle'].get('bold'):
            vistos['bold'].append(doc[st['range']['startIndex']:st['range']['endIndex']])
    print('2) superíndices:', vistos['SUPERSCRIPT'], '| negritas:', vistos['bold'])
    if vistos != esperados:
        fallas.append('rangos de estilo')
    for r in reqs:   # cada estilo de párrafo empieza al principio de un párrafo
        ps = r.get('updateParagraphStyle')
        if ps and 'namedStyleType' in ps['paragraphStyle'] and doc[ps['range']['startIndex'] - 1] not in '\x00\n':
            fallas.append('párrafo mal ubicado en %s' % ps['range'])
    print('3) salto final del documento en', fin, '(simulado: %d)' % (len(doc) - 1))
    if fin != len(doc) - 1 or doc[fin] != '\n':
        fallas.append('índice final')
    reqs2, _ = pedidos_texto(leer_bloques('# Siguiente\nTexto.'), 2844, despues_de_lista=True)
    borra = [r for r in reqs2 if 'deleteParagraphBullets' in r]
    print('4) después de una lista: quita viñetas en', borra[0]['deleteParagraphBullets']['range'] if borra else None)
    if not borra or borra[0]['deleteParagraphBullets']['range'] != {'startIndex': 2845, 'endIndex': 2862}:
        fallas.append('limpieza después de lista')
    # Tabla de 15 x 3 insertada en 1250: índices comprobados contra un documento real de Google Docs
    filas = [['Magnitud', 'Valor', 'Fuente'], ['Tipo espectral', 'G2 V (enana amarilla)', 'NSSDC']] + [['a', 'b', 'c']] * 13
    t = pedidos_tabla(filas, 1250, encabezado=True)
    celdas = {r['insertText']['text']: r['insertText']['location']['index'] for r in t if 'insertText' in r}
    negrita = [(r['updateTextStyle']['range']['startIndex'], r['updateTextStyle']['range']['endIndex'])
               for r in t if 'updateTextStyle' in r]
    vacio = t[1]['updateParagraphStyle']['range']['startIndex']
    print('5) tabla: Magnitud en', celdas['Magnitud'], '| Tipo espectral en', celdas['Tipo espectral'],
          '| párrafo después en', vacio, '| encabezado en negrita', negrita)
    if (celdas['Magnitud'], celdas['Tipo espectral'], vacio) != (1254, 1261, 1358) or \
            negrita != [(1254, 1262), (1264, 1269), (1271, 1277)]:
        fallas.append('índices de la tabla')
    # Figuras arriba de epígrafes en 8565 y 8675 (comprobado en el mismo documento)
    f = pedidos_figuras([{'epigrafe': 8675, 'uri': 'https://ejemplo/2'}, {'epigrafe': 8565, 'uri': 'https://ejemplo/1'}])
    orden = [r['insertInlineImage']['location']['index'] for r in f if 'insertInlineImage' in r]
    juntos = [(r['updateParagraphStyle']['range']['startIndex'], r['updateParagraphStyle']['range']['endIndex'])
              for r in f if 'updateParagraphStyle' in r]
    print('6) figuras: se insertan en', orden, '| párrafos de imagen', juntos)
    if orden != [8675, 8565] or juntos != [(8565, 8567), (8677, 8679)]:
        fallas.append('figuras')
    lectura = {'revisionId': 'R1', 'body': {'content': [
        {'endIndex': 1, 'sectionBreak': {}},
        {'startIndex': 1, 'endIndex': 12, 'paragraph': {'elements': [{'textRun': {'content': 'Figura 1. x\n'}}],
                                                        'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'}}},
        {'startIndex': 12, 'endIndex': 20, 'paragraph': {'elements': [{'textRun': {'content': 'Fuentes\n'}}],
                                                         'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'},
                                                         'bullet': {'listId': 'k'}}}]}}
    info = indices(lectura, ['Figura 1.'])
    print('7) índices: agregar en', info['inicio_para_agregar'], '| último es lista:', info['ultimo_es_lista'],
          '| Figura 1. en', info['encontrados'][0]['ini'])
    if (info['inicio_para_agregar'], info['ultimo_es_lista'], info['encontrados'][0]['ini']) != (19, True, 1):
        fallas.append('lectura de índices')
    if fallas:
        print('DEMO FALLÓ: ' + '; '.join(fallas))
        return 1
    print('DEMO OK')
    return 0


def numeros(txt):
    return tuple(float(x) for x in txt.split(','))


def main(argv=None):
    ap = argparse.ArgumentParser(description='Pedidos para escribir un informe en Google Docs (conector update_doc).')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('texto', help='agregar una sección escrita con marcas')
    p.add_argument('archivo', help='texto de la sección (UTF-8), o - para leer de la entrada')
    p.add_argument('--inicio', type=int, required=True, help='endIndex - 1 del último párrafo (o su startIndex si el doc está vacío)')
    p.add_argument('--rev', required=True, help='revisionId de una lectura hecha después de la última escritura')
    p.add_argument('--doc-vacio', action='store_true', help='el último párrafo está vacío (documento nuevo)')
    p.add_argument('--despues-de-lista', action='store_true', help='el último párrafo es un ítem de lista')
    p.add_argument('--tab', help='tabId si el documento tiene varias pestañas')
    p.add_argument('--espacio', type=float, default=8.0, help='espacio debajo de cada párrafo, en pt')
    p.add_argument('--color-titulo', type=numeros, help='color del TITULO como r,g,b de 0 a 1, p. ej. 0.8,0.33,0')
    p.add_argument('--salida', help='guardar el JSON en un archivo')
    p = sub.add_parser('tabla', help='insertar una tabla llena')
    p.add_argument('--en', type=int, required=True, help='endIndex - 1 del párrafo que presenta la tabla')
    p.add_argument('--filas', required=True, help='JSON con la lista de filas (la primera es el encabezado)')
    p.add_argument('--rev', required=True)
    p.add_argument('--tab')
    p.add_argument('--sin-encabezado', action='store_true', help='no poner en negrita la primera fila')
    p.add_argument('--color-encabezado', type=numeros, help='fondo de la primera fila, r,g,b de 0 a 1')
    p.add_argument('--anchos', type=numeros, help='ancho de cada columna en pt, p. ej. 140,226,85')
    p.add_argument('--salida')
    p = sub.add_parser('figuras', help='insertar imágenes arriba de sus epígrafes')
    p.add_argument('--datos', required=True, help='JSON: [{"epigrafe": índice, "uri": "...", "ancho": 430, "alto": 242}]')
    p.add_argument('--rev', required=True)
    p.add_argument('--tab')
    p.add_argument('--salida')
    p = sub.add_parser('indices', help='leer un read_doc guardado: revisión, dónde agregar y dónde está un texto')
    p.add_argument('lectura')
    p.add_argument('--buscar', action='append', default=[])
    sub.add_parser('demo', help='probar todo contra índices de un documento real')
    a = ap.parse_args(argv)

    if a.cmd == 'demo':
        return demo(a)
    if a.cmd == 'indices':
        with open(a.lectura, encoding='utf-8') as f:
            print(json.dumps(indices(json.load(f), a.buscar), ensure_ascii=False, indent=1))
        return 0
    if a.cmd == 'texto':
        texto = sys.stdin.read() if a.archivo == '-' else open(a.archivo, encoding='utf-8').read()
        reqs, fin = pedidos_texto(leer_bloques(texto), a.inicio, a.doc_vacio, a.despues_de_lista, a.tab,
                                  a.espacio, a.color_titulo)
        print('fin del texto nuevo: %d (para la próxima sección, volver a leer el documento)' % fin, file=sys.stderr)
    elif a.cmd == 'tabla':
        with open(a.filas, encoding='utf-8') as f:
            reqs = pedidos_tabla(json.load(f), a.en, a.tab, not a.sin_encabezado, a.color_encabezado, a.anchos)
    else:
        with open(a.datos, encoding='utf-8') as f:
            reqs = pedidos_figuras(json.load(f), a.tab)
    out = json.dumps(salida_json(reqs, a.rev), ensure_ascii=True)
    if a.salida:
        with open(a.salida, 'w', encoding='utf-8') as f:
            f.write(out)
        print('%d pedidos en %s' % (len(reqs), a.salida), file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
