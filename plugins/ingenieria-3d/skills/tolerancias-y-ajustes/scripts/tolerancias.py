#!/usr/bin/env python3
"""tolerancias.py - tolerancias ISO 286, tolerancias generales ISO 2768, cadenas de cotas y medicion
(solo biblioteca estandar). Acepta coma o punto decimal.

Cotas nominales de mas de 0 hasta 500 mm. Desviaciones, IT y juegos en um (micrometros); limites en mm.
  ajuste D CLASES     limites, juego o aprieto maximo y minimo y tipo de ajuste:  ajuste 25 H7/g6
                      (sistema de eje unico: ajuste 25 G7/h6; una sola clase: ajuste 25 g6)
  it D GRADO          tolerancia fundamental IT01 a IT18:  it 25 7
  general COTA CLASE [--tipo lineal|arista|angulo|rectitud|planitud|perpendicularidad|simetria|oscilacion]
                      ISO 2768-1 (clases f, m, c, v) e ISO 2768-2 (clases H, K, L):  general 85 m
  cadena COTAS [--min mm --max mm]
                      cadena de cotas, peor caso y RSS. Cada cota: +50:0.1 (simetrica, +-0,1 mm) o
                      -20:+0.05:-0.02 (desviaciones superior e inferior). El signo dice si la cota suma (+)
                      o resta (-) en la cota de cierre. Todas entre comillas:  cadena "+50:0.1 -20:0.05"
  incertidumbre LECTURAS --res mm [--emax mm] [--k 2]
                      media, desvio, incertidumbre tipo A y B, combinada y expandida (GUM)
  nonio --div mm --n N [--entero mm --linea L]        apreciacion y lectura de un calibre con nonio
  micrometro [--paso 0.5 --div 50] [--escala mm --tambor L]   apreciacion y lectura de un micrometro
  demo                reproduce los ejemplos del SKILL.md y compara con valores publicados

Tablas cargadas: ISO 286-1 (IT01 a IT18; ejes c, d, e, f, g, h, js, k de IT4 a IT7, m, n, p, r, s;
agujeros F, G, H, JS, K y N de IT3 a IT8 y P desde IT3). Fuentes en references/tablas.md.
"""
import argparse
import math
import random
import re
import sys

# ------------------------------------------------------------------------------------------ tablas
# Escalones ISO 286-1: "de mas de a hasta b inclusive" (mm)
RANGOS = [(0, 3), (3, 6), (6, 10), (10, 18), (18, 30), (30, 50), (50, 80), (80, 120), (120, 180),
          (180, 250), (250, 315), (315, 400), (400, 500)]
SUBRANGOS = [(0, 3), (3, 6), (6, 10), (10, 14), (14, 18), (18, 24), (24, 30), (30, 40), (40, 50), (50, 65),
             (65, 80), (80, 100), (100, 120), (120, 140), (140, 160), (160, 180), (180, 200), (200, 225),
             (225, 250), (250, 280), (280, 315), (315, 355), (355, 400), (400, 450), (450, 500)]
# ISO 286-1:2010, tabla 1: tolerancias fundamentales en um, un valor por escalon de RANGOS
IT = {
    '01': [0.3, 0.4, 0.4, 0.5, 0.6, 0.6, 0.8, 1, 1.2, 2, 2.5, 3, 4],
    '0': [0.5, 0.6, 0.6, 0.8, 1, 1, 1.2, 1.5, 2, 3, 4, 5, 6],
    '1': [0.8, 1, 1, 1.2, 1.5, 1.5, 2, 2.5, 3.5, 4.5, 6, 7, 8],
    '2': [1.2, 1.5, 1.5, 2, 2.5, 2.5, 3, 4, 5, 7, 8, 9, 10],
    '3': [2, 2.5, 2.5, 3, 4, 4, 5, 6, 8, 10, 12, 13, 15],
    '4': [3, 4, 4, 5, 6, 7, 8, 10, 12, 14, 16, 18, 20],
    '5': [4, 5, 6, 8, 9, 11, 13, 15, 18, 20, 23, 25, 27],
    '6': [6, 8, 9, 11, 13, 16, 19, 22, 25, 29, 32, 36, 40],
    '7': [10, 12, 15, 18, 21, 25, 30, 35, 40, 46, 52, 57, 63],
    '8': [14, 18, 22, 27, 33, 39, 46, 54, 63, 72, 81, 89, 97],
    '9': [25, 30, 36, 43, 52, 62, 74, 87, 100, 115, 130, 140, 155],
    '10': [40, 48, 58, 70, 84, 100, 120, 140, 160, 185, 210, 230, 250],
    '11': [60, 75, 90, 110, 130, 160, 190, 220, 250, 290, 320, 360, 400],
    '12': [100, 120, 150, 180, 210, 250, 300, 350, 400, 460, 520, 570, 630],
    '13': [140, 180, 220, 270, 330, 390, 460, 540, 630, 720, 810, 890, 970],
    '14': [250, 300, 360, 430, 520, 620, 740, 870, 1000, 1150, 1300, 1400, 1550],
    '15': [400, 480, 580, 700, 840, 1000, 1200, 1400, 1600, 1850, 2100, 2300, 2500],
    '16': [600, 750, 900, 1100, 1300, 1600, 1900, 2200, 2500, 2900, 3200, 3600, 4000],
    '17': [1000, 1200, 1500, 1800, 2100, 2500, 3000, 3500, 4000, 4600, 5200, 5700, 6300],
    '18': [1400, 1800, 2200, 2700, 3300, 3900, 4600, 5400, 6300, 7200, 8100, 8900, 9700],
}
MULTIPLO_I = {'5': 7, '6': 10, '7': 16, '8': 25, '9': 40, '10': 64, '11': 100, '12': 160, '13': 250,
              '14': 400, '15': 640, '16': 1000, '17': 1600, '18': 2500}
# Desviaciones fundamentales de ejes (ISO 286-1), um. Ejes c a g: desviacion superior es; k a s: inferior ei.
ES_C = [-60, -70, -80, -95, -95, -110, -110, -120, -130, -140, -150, -170, -180, -200, -210, -230, -240,
        -260, -280, -300, -330, -360, -400, -440, -480]                       # por SUBRANGOS
ES_EJE = {'d': [-20, -30, -40, -50, -65, -80, -100, -120, -145, -170, -190, -210, -230],
          'e': [-14, -20, -25, -32, -40, -50, -60, -72, -85, -100, -110, -125, -135],
          'f': [-6, -10, -13, -16, -20, -25, -30, -36, -43, -50, -56, -62, -68],
          'g': [-2, -4, -5, -6, -7, -9, -10, -12, -14, -15, -17, -18, -20]}   # por RANGOS
EI_EJE = {'k': [0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 5],                      # k: solo IT4 a IT7
          'm': [2, 4, 6, 7, 8, 9, 11, 13, 15, 17, 20, 21, 23],
          'n': [4, 8, 10, 12, 15, 17, 20, 23, 27, 31, 34, 37, 40],
          'p': [6, 12, 15, 18, 22, 26, 32, 37, 43, 50, 56, 62, 68]}          # por RANGOS
EI_RS = {'r': [10, 15, 19, 23, 23, 28, 28, 34, 34, 41, 43, 51, 54, 63, 65, 68, 77, 80, 84, 94, 98, 108,
               114, 126, 132],
         's': [14, 19, 23, 28, 28, 35, 35, 43, 43, 53, 59, 71, 79, 92, 100, 108, 122, 130, 140, 158, 170,
               190, 208, 232, 252]}                                              # por SUBRANGOS
LETRAS_EJE = ['c', 'd', 'e', 'f', 'g', 'h', 'js', 'k', 'm', 'n', 'p', 'r', 's']
LETRAS_AGUJERO = ['F', 'G', 'H', 'JS', 'K', 'N', 'P']

# ISO 2768-1:1989 (mm). Lineal: escalones de mas de a hasta b; None = la norma no da valor
ISO2768_LINEAL_RANGOS = [(0.5, 3), (3, 6), (6, 30), (30, 120), (120, 400), (400, 1000), (1000, 2000), (2000, 4000)]
ISO2768_LINEAL = {'f': [0.05, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, None],
                  'm': [0.1, 0.1, 0.2, 0.3, 0.5, 0.8, 1.2, 2],
                  'c': [0.2, 0.3, 0.5, 0.8, 1.2, 2, 3, 4],
                  'v': [None, 0.5, 1, 1.5, 2.5, 4, 6, 8]}
ISO2768_ARISTA_RANGOS = [(0.5, 3), (3, 6), (6, math.inf)]   # radios exteriores y alturas de chaflan
ISO2768_ARISTA = {'f': [0.2, 0.5, 1], 'm': [0.2, 0.5, 1], 'c': [0.4, 1, 2], 'v': [0.4, 1, 2]}
ISO2768_ANGULO_RANGOS = [(0, 10), (10, 50), (50, 120), (120, 400), (400, math.inf)]   # lado mas corto
ISO2768_ANGULO = {'f': [60, 30, 20, 10, 5], 'm': [60, 30, 20, 10, 5], 'c': [90, 60, 30, 15, 10],
                  'v': [180, 120, 60, 30, 20]}                                          # minutos de arco
# ISO 2768-2:1989 (mm), clases H, K, L (una sola fuente publica contrastada: verificar en la norma)
ISO2768_2 = {
    'rectitud': ([(0, 10), (10, 30), (30, 100), (100, 300), (300, 1000), (1000, 3000)],
                 {'H': [0.02, 0.05, 0.1, 0.2, 0.3, 0.4], 'K': [0.05, 0.1, 0.2, 0.4, 0.6, 0.8],
                  'L': [0.1, 0.2, 0.4, 0.8, 1.2, 1.6]}, 'largo de la línea o de la superficie'),
    'perpendicularidad': ([(0, 100), (100, 300), (300, 1000), (1000, 3000)],
                          {'H': [0.2, 0.3, 0.4, 0.5], 'K': [0.4, 0.6, 0.8, 1], 'L': [0.6, 1, 1.5, 2]},
                          'largo del lado más corto'),
    'simetria': ([(0, 100), (100, 300), (300, 1000), (1000, 3000)],
                 {'H': [0.5, 0.5, 0.5, 0.5], 'K': [0.6, 0.6, 0.8, 1], 'L': [0.6, 1, 1.5, 2]},
                 'largo del elemento'),
    'oscilacion': ([(0, math.inf)], {'H': [0.1], 'K': [0.2], 'L': [0.5]}, 'cualquier tamaño'),
}
ISO2768_2['planitud'] = ISO2768_2['rectitud']
NOMBRE_CLASE = {'f': 'fina', 'm': 'media', 'c': 'gruesa', 'v': 'muy gruesa'}


# ------------------------------------------------------------------------------------------ formato
def n(x, d=3):
    if abs(x) < 0.5 * 10 ** -d:
        x = 0.0
    return ('%.*f' % (d, x)).replace('.', ',')


def nc(x, d=3):
    """Como n() pero sin ceros de mas: 0,02 y 23,74."""
    return n(x, d).rstrip('0').rstrip(',')


def um(x):
    """Desviacion en um con signo: +21, -7, +10,5, 0."""
    if abs(x) < 1e-9:
        return '0'
    if abs(x - round(x)) < 1e-9:
        return '%+d' % round(x)
    return ('%+.1f' % x).replace('.', ',')


def um_sin_signo(x):
    return um(x).lstrip('+')


def num(txt):
    """Numero con coma o punto decimal."""
    try:
        return float(str(txt).replace(',', '.'))
    except ValueError:
        raise argparse.ArgumentTypeError('número inválido: %s' % txt)


def escalon_txt(a, b):
    return 'hasta %g mm' % b if a == 0 else 'de más de %g hasta %g mm' % (a, b)


# ------------------------------------------------------------------------------------------ ISO 286
def indice(D, rangos=RANGOS):
    if not 0 < D <= 500:
        raise ValueError('las tablas cargadas cubren cotas nominales de más de 0 hasta 500 mm (se pidió %g mm)' % D)
    for i, (a, b) in enumerate(rangos):
        if a < D <= b:
            return i
    raise ValueError('cota fuera de rango')


def grado_clave(g):
    g = str(g).upper().replace('IT', '').strip()
    if g in IT:
        return g
    if g.isdigit() and str(int(g)) in IT:
        return str(int(g))
    raise ValueError('grado IT inválido: %s (IT01, IT0, IT1 a IT18)' % g)


def tolerancia_it(D, grado):
    return IT[grado_clave(grado)][indice(D)]


def factor_i(D):
    """Factor de tolerancia i = 0,45*cbrt(Dm) + 0,001*Dm (um), Dm media geometrica del escalon (solo D > 3 mm)."""
    a, b = RANGOS[indice(D)]
    Dm = math.sqrt(a * b)
    return 0.45 * Dm ** (1 / 3) + 0.001 * Dm, Dm


def delta(D, grado):
    """Delta = IT(n) - IT(n-1) para agujeros K, N (hasta IT8) y P (hasta IT7); 0 hasta 3 mm."""
    g = int(grado)
    if not 3 <= g <= 8:
        raise ValueError('Δ está definido de IT3 a IT8')
    if D <= 3:
        return 0.0
    i = indice(D)
    return IT[str(g)][i] - IT[str(g - 1)][i]


def leer_clase(txt):
    m = re.fullmatch(r'\s*([A-Za-z]{1,2})\s*(?:IT)?\s*(01|0|1[0-8]|[1-9])\s*', txt)
    if not m:
        raise ValueError('clase de tolerancia inválida: «%s» (ejemplos: H7, g6, JS7, js6)' % txt)
    letra, grado = m.group(1), m.group(2)
    if letra in ('JS', 'Js'):
        return 'JS', grado, True
    if letra == 'js':
        return 'js', grado, False
    if len(letra) == 1 and letra.isupper():
        return letra, grado, True
    if len(letra) == 1 and letra.islower():
        return letra, grado, False
    raise ValueError('clase «%s»: mayúscula para agujeros (H7) y minúscula para ejes (g6)' % txt)


def desviaciones(D, txt):
    """Devuelve dict con sup, inf (um), it, agujero (bool), clase y como se obtiene cada limite."""
    letra, grado, es_agujero = leer_clase(txt)
    t = tolerancia_it(D, grado)
    i13, i25 = indice(D), indice(D, SUBRANGOS)
    g = grado_clave(grado)
    clase = letra + grado
    if es_agujero:
        if letra not in LETRAS_AGUJERO:
            raise ValueError('agujero %s: letras cargadas %s (el resto, en ISO 286-2)' % (letra, ', '.join(LETRAS_AGUJERO)))
        if letra == 'H':
            inf = 0.0
            sup = inf + t
            como, otra = 'EI = 0 (H)', 'ES = EI + IT = %s µm' % um(sup)
        elif letra == 'JS':
            sup, inf = t / 2, -t / 2
            como, otra = 'ES = +IT/2 = %s µm' % um(sup), 'EI = −IT/2 = %s µm' % um(inf)
        elif letra in ('F', 'G'):
            inf = -ES_EJE[letra.lower()][i13]
            sup = inf + t
            como, otra = 'EI = −es(%s) = %s µm' % (letra.lower(), um(inf)), 'ES = EI + IT = %s µm' % um(sup)
        else:   # K, N, P
            if g in ('01', '0') or int(g) < 3:
                raise ValueError('%s: cargado desde IT3 (Δ de la tabla de IT3 a IT8)' % clase)
            gi = int(g)
            ei_eje = EI_EJE[{'K': 'k', 'N': 'n', 'P': 'p'}[letra]][i13]
            tope = 7 if letra == 'P' else 8
            if gi <= tope:
                dl = delta(D, gi)
                sup = -ei_eje + dl
                como = 'ES = −ei(%s) + Δ = %s + %s = %s µm (Δ = IT%d − IT%d%s)' % (
                    letra.lower(), um(-ei_eje), um_sin_signo(dl), um(sup), gi, gi - 1, '; 0 hasta 3 mm' if D <= 3 else '')
            elif letra == 'P':
                sup = -ei_eje
                como = 'ES = −ei(p) = %s µm (sin Δ por encima de IT7)' % um(sup)
            else:
                raise ValueError('%s: por encima de IT8 no está cargado (verificar en ISO 286-2)' % clase)
            inf = sup - t
            otra = 'EI = ES − IT = %s µm' % um(inf)
    else:
        if letra not in LETRAS_EJE:
            raise ValueError('eje %s: letras cargadas %s (el resto, en ISO 286-2)' % (letra, ', '.join(LETRAS_EJE)))
        if letra == 'h':
            sup = 0.0
            inf = sup - t
            como, otra = 'es = 0 (h)', 'ei = es − IT = %s µm' % um(inf)
        elif letra == 'js':
            sup, inf = t / 2, -t / 2
            como, otra = 'es = +IT/2 = %s µm' % um(sup), 'ei = −IT/2 = %s µm' % um(inf)
        elif letra in ('c', 'd', 'e', 'f', 'g'):
            sup = ES_C[i25] if letra == 'c' else ES_EJE[letra][i13]
            inf = sup - t
            como, otra = 'es = %s µm (desviación fundamental de %s)' % (um(sup), letra), 'ei = es − IT = %s µm' % um(inf)
        else:   # k, m, n, p, r, s
            if letra == 'k' and (g in ('01', '0') or not 4 <= int(g) <= 7):
                raise ValueError('%s: k está cargado de IT4 a IT7 (fuera de eso, verificar en ISO 286-2)' % clase)
            inf = EI_RS[letra][i25] if letra in EI_RS else EI_EJE[letra][i13]
            sup = inf + t
            como, otra = 'ei = %s µm (desviación fundamental de %s)' % (um(inf), letra), 'es = ei + IT = %s µm' % um(sup)
    return {'sup': sup, 'inf': inf, 'it': t, 'agujero': es_agujero, 'clase': clase, 'grado': g, 'como': como, 'otra': otra}


def dev_mm(x):
    """Desviacion en mm para el plano: +0,021, 0, -0,007, +0,0105."""
    if abs(x) < 1e-9:
        return '0'
    d = 3 if abs(x - round(x)) < 1e-9 else 4
    return ('%+.*f' % (d, x / 1000)).replace('.', ',')


def par(x):
    """Valor con signo entre parentesis para restar: (+2), (-20), 0."""
    return '0' if abs(x) < 1e-9 else '(%s)' % um(x)


def cota_txt(D):
    return nc(D)


def texto_clase(D, d):
    if d['agujero']:
        return ['Agujero %s %s: IT%s = %s µm; %s; %s → Dmín = %s mm, Dmáx = %s mm'
                % (cota_txt(D), d['clase'], d['grado'], um_sin_signo(d['it']), d['como'], d['otra'],
                   n(D + d['inf'] / 1000, 4 if abs(d['inf'] - round(d['inf'])) > 1e-9 else 3),
                   n(D + d['sup'] / 1000, 4 if abs(d['sup'] - round(d['sup'])) > 1e-9 else 3))]
    return ['Eje %s %s: IT%s = %s µm; %s; %s → dmáx = %s mm, dmín = %s mm'
            % (cota_txt(D), d['clase'], d['grado'], um_sin_signo(d['it']), d['como'], d['otra'],
               n(D + d['sup'] / 1000, 4 if abs(d['sup'] - round(d['sup'])) > 1e-9 else 3),
               n(D + d['inf'] / 1000, 4 if abs(d['inf'] - round(d['inf'])) > 1e-9 else 3))]


def ajuste(D, txt):
    a, b = RANGOS[indice(D)]
    if '/' not in txt:
        d = desviaciones(D, txt)
        L = ['Ø %s %s (escalón %s)' % (cota_txt(D), d['clase'], escalon_txt(a, b))] + texto_clase(D, d)
        L.append('En el plano: Ø%s %s (%s/%s)' % (cota_txt(D), d['clase'], dev_mm(d['sup']), dev_mm(d['inf'])))
        return {'clase': d}, L
    h_txt, s_txt = txt.split('/', 1)
    h, s = desviaciones(D, h_txt), desviaciones(D, s_txt)
    if not h['agujero'] or s['agujero']:
        raise ValueError('el ajuste se escribe agujero/eje: H7/g6 (mayúscula/minúscula)')
    jmax = h['sup'] - s['inf']
    jmin = h['inf'] - s['sup']
    if jmin >= 0:
        tipo = 'con juego'
    elif jmax <= 0:
        tipo = 'con aprieto'
    else:
        tipo = 'incierto (de transición)'
    D_txt = cota_txt(D)
    L = ['Ø %s %s/%s (escalón %s)' % (D_txt, h['clase'], s['clase'], escalon_txt(a, b))]
    L += texto_clase(D, h) + texto_clase(D, s)
    L.append('Juego máximo: Jmáx = Dmáx − dmín = ES − ei = %s − %s = %s µm' % (um(h['sup']), par(s['inf']), um(jmax)))
    L.append('Juego mínimo: Jmín = Dmín − dmáx = EI − es = %s − %s = %s µm' % (um(h['inf']), par(s['sup']), um(jmin)))
    if tipo == 'con juego':
        L.append('Ajuste con juego: entre %s y %s mm de juego' % (n(jmin / 1000), n(jmax / 1000)))
    elif tipo == 'con aprieto':
        L.append('Ajuste con aprieto: aprieto máximo Amáx = −Jmín = %s mm; aprieto mínimo Amín = −Jmáx = %s mm'
                 % (n(-jmin / 1000), n(-jmax / 1000)))
    else:
        L.append('Ajuste incierto: puede quedar con hasta %s mm de juego o hasta %s mm de aprieto'
                 % (n(jmax / 1000), n(-jmin / 1000)))
    L.append('Tolerancia del ajuste: Jmáx − Jmín = IT agujero + IT eje = %s + %s = %s µm'
             % (um_sin_signo(h['it']), um_sin_signo(s['it']), um_sin_signo(jmax - jmin)))
    L.append('En el plano: Ø%s %s (%s/%s) en el agujero y Ø%s %s (%s/%s) en el eje'
             % (D_txt, h['clase'], dev_mm(h['sup']), dev_mm(h['inf']), D_txt, s['clase'], dev_mm(s['sup']), dev_mm(s['inf'])))
    return {'agujero': h, 'eje': s, 'jmax': jmax, 'jmin': jmin, 'tipo': tipo}, L


def it_cmd(D, grado):
    g = grado_clave(grado)
    a, b = RANGOS[indice(D)]
    t = IT[g][indice(D)]
    L = ['IT%s para Ø %s mm (escalón %s): %s µm = %s mm (ISO 286-1, tabla 1)' % (g, cota_txt(D), escalon_txt(a, b),
                                                                             um_sin_signo(t), nc(t / 1000, 4))]
    r = {'it': t}
    if g in MULTIPLO_I and D > 3:
        i, Dm = factor_i(D)
        r['i'] = i
        L.append('Origen de la tabla: i = 0,45·∛D + 0,001·D con D = √(%g·%g) = %s mm → i = %s µm; IT%s ≈ %d·i = %s µm'
                 % (a, b, n(Dm, 2), n(i, 3), g, MULTIPLO_I[g], n(MULTIPLO_I[g] * i, 1)))
        L.append('La tabla es la que vale: redondea esos productos.')
    return r, L


# ------------------------------------------------------------------------------------------ ISO 2768
def buscar(valor, rangos, incluir_primero=True):
    for i, (a, b) in enumerate(rangos):
        if (a < valor <= b) or (incluir_primero and i == 0 and valor == a):
            return i
    return None


def general(cota, clase, tipo='lineal'):
    c = clase.strip().replace('ISO', '').replace('2768', '').replace('-', '').strip()
    if tipo in ('lineal', 'arista', 'angulo'):
        letra = c[:1].lower()
        if letra not in ISO2768_LINEAL:
            raise ValueError('clase ISO 2768-1: f, m, c o v (por ejemplo «m» o «mK»)')
        nombre = 'ISO 2768-1 clase %s (%s)' % (letra, NOMBRE_CLASE[letra])
        if tipo == 'angulo':
            i = buscar(cota, ISO2768_ANGULO_RANGOS)
            if cota <= 0 or i is None:
                raise ValueError('para ángulos, indicar el largo del lado más corto en mm (mayor que 0)')
            minutos = ISO2768_ANGULO[letra][i]
            txt = '±%d°' % (minutos // 60) if minutos % 60 == 0 else ('±%d°%02d\'' % divmod(minutos, 60))
            a, b = ISO2768_ANGULO_RANGOS[i]
            esc = 'lado corto hasta %g mm' % b if a == 0 else ('lado corto de más de %g mm' % a if b == math.inf else
                                                               'lado corto de más de %g hasta %g mm' % (a, b))
            return {'minutos': minutos}, ['%s, ángulo con %s → %s' % (nombre, esc, txt)]
        rangos, tabla = (ISO2768_ARISTA_RANGOS, ISO2768_ARISTA) if tipo == 'arista' else (ISO2768_LINEAL_RANGOS, ISO2768_LINEAL)
        if cota < 0.5:
            raise ValueError('por debajo de 0,5 mm la tolerancia se indica junto a la cota (verificar en la norma vigente)')
        i = buscar(cota, rangos)
        if i is None:
            raise ValueError('ISO 2768-1 llega hasta 4000 mm')
        t = tabla[letra][i]
        if t is None:
            raise ValueError('la clase %s no tiene valor para ese escalón en ISO 2768-1' % letra)
        a, b = rangos[i]
        esc = ('de %g hasta %g mm' % (a, b)) if i == 0 else ('de más de %g mm' % a if b == math.inf else 'de más de %g hasta %g mm' % (a, b))
        que = 'radio exterior o altura de chaflán' if tipo == 'arista' else 'cota lineal'
        return {'t': t}, ['%s, %s de %s mm (escalón %s) → ±%s mm' % (nombre, que, nc(cota), esc,
                                                                    nc(t, 2))]
    if tipo not in ISO2768_2:
        raise ValueError('tipo: lineal, arista, angulo, rectitud, planitud, perpendicularidad, simetria u oscilacion')
    letra = c[-1:].upper()
    rangos, tabla, que = ISO2768_2[tipo]
    if letra not in tabla:
        raise ValueError('clase ISO 2768-2: H, K o L (por ejemplo «K» o «mK»)')
    i = buscar(cota, rangos) if tipo != 'oscilacion' else 0
    if i is None:
        raise ValueError('ISO 2768-2 llega hasta 3000 mm')
    t = tabla[letra][i]
    a, b = rangos[i]
    esc = '' if tipo == 'oscilacion' else (' (%s %s)' % (que, 'hasta %g mm' % b if a == 0 else 'de más de %g hasta %g mm' % (a, b)))
    return {'t': t}, ['ISO 2768-2 clase %s, %s%s → %s mm (contrastada con una sola fuente pública: verificar en la norma vigente)'
                      % (letra, tipo.replace('simetria', 'simetría').replace('oscilacion', 'oscilación circular'), esc,
                         nc(t, 2))]


# ------------------------------------------------------------------------------------------ cadena
def leer_cota(txt):
    m = re.fullmatch(r'([+-])?(\d+(?:[.,]\d+)?)(?::([+-]?\d+(?:[.,]\d+)?))?(?::([+-]?\d+(?:[.,]\d+)?))?', txt.strip())
    if not m or m.group(3) is None:
        raise ValueError('cota «%s»: formato +50:0.1 (±0,1) o -20:+0.05:-0.02' % txt)
    signo = -1 if m.group(1) == '-' else 1
    nom = float(m.group(2).replace(',', '.'))
    a = float(m.group(3).replace(',', '.'))
    if m.group(4) is None:
        sup, inf = abs(a), -abs(a)
    else:
        sup, inf = a, float(m.group(4).replace(',', '.'))
    if sup < inf:
        raise ValueError('cota «%s»: la desviación superior va primero' % txt)
    return signo, nom, sup, inf


def cadena(cotas, cmin=None, cmax=None):
    items = [leer_cota(t) for t in cotas]
    if not items:
        raise ValueError('faltan las cotas')
    nom = sum(s * c for s, c, _, _ in items)
    medio = sum(s * (c + (a + b) / 2) for s, c, a, b in items)
    t_wc = sum(a - b for _, _, a, b in items)
    t_rss = math.sqrt(sum((a - b) ** 2 for _, _, a, b in items))
    vmax = sum((c + a) if s > 0 else -(c + b) for s, c, a, b in items)
    vmin = sum((c + b) if s > 0 else -(c + a) for s, c, a, b in items)
    rmin, rmax = medio - t_rss / 2, medio + t_rss / 2
    terminos = ''.join(('%s%s' % ('' if j == 0 else ' + ', nc(c)) if s > 0 else '%s%s' % ('−' if j == 0 else ' − ', nc(c)))
                       for j, (s, c, _, _) in enumerate(items))
    L = ['Cota de cierre nominal = Σ(cotas que suman) − Σ(cotas que restan) = %s = %s mm' % (terminos, n(nom)),
         'Peor caso (suma aritmética): T = ΣTi = %s = %s mm → cierre entre %s y %s mm'
         % (' + '.join(n(a - b) for _, _, a, b in items), n(t_wc), n(vmin), n(vmax)),
         'Estadístico (RSS): T = √(ΣTi²) = √(%s) = %s mm → cierre entre %s y %s mm (centrado en %s mm)'
         % (' + '.join(n((a - b) ** 2, 4) for _, _, a, b in items), n(t_rss), n(rmin), n(rmax), n(medio)),
         'El RSS supone cotas independientes, centradas, con distribución normal y tolerancia = ±3σ: '
         'queda adentro el 99,73 % de los conjuntos. Con pocas cotas o en piezas únicas, usar el peor caso.']
    r = {'nom': nom, 'medio': medio, 't_wc': t_wc, 't_rss': t_rss, 'min': vmin, 'max': vmax, 'rss_min': rmin, 'rss_max': rmax}
    if cmin is not None or cmax is not None:
        lo = -math.inf if cmin is None else cmin
        hi = math.inf if cmax is None else cmax
        for nombre, a, b in (('peor caso', vmin, vmax), ('RSS', rmin, rmax)):
            ok = lo - 1e-12 <= a and b <= hi + 1e-12
            L.append('%s: %s el requisito (%s a %s mm)' % (nombre[0].upper() + nombre[1:], 'cumple' if ok else 'NO cumple',
                                                          '−∞' if cmin is None else n(lo), '∞' if cmax is None else n(hi)))
    return r, L


# ------------------------------------------------------------------------------------------ medicion
def redondear_u(U):
    """U a dos cifras significativas; devuelve (U redondeada, decimales)."""
    dec = max(0, 1 - int(math.floor(math.log10(U))))
    return round(U, dec), dec


def incertidumbre(lecturas, res, emax=None, k=2.0):
    x = [float(v) for v in lecturas]
    nn = len(x)
    if nn < 2:
        raise ValueError('hacen falta al menos dos lecturas para el desvío')
    media = sum(x) / nn
    s = math.sqrt(sum((v - media) ** 2 for v in x) / (nn - 1))
    ua = s / math.sqrt(nn)
    ur = res / (2 * math.sqrt(3))
    ue = emax / math.sqrt(3) if emax else 0.0
    uc = math.sqrt(ua ** 2 + ur ** 2 + ue ** 2)
    U = k * uc
    Ur, dec = redondear_u(U)
    L = ['n = %d lecturas: media x̄ = Σx/n = %s mm; desvío s = √(Σ(x − x̄)²/(n − 1)) = %s mm' % (nn, n(media, 5), n(s, 5)),
         'Tipo A (repetibilidad): uA = s/√n = %s mm' % n(ua, 5),
         'Tipo B (resolución %s mm, rectangular): uδ = δ/(2·√3) = %s mm' % (nc(res, 4), n(ur, 5))]
    if emax:
        L.append('Tipo B (error máximo ±%s mm del instrumento, rectangular): ue = a/√3 = %s mm' % (nc(emax, 4), n(ue, 5)))
    L += ['Combinada: uc = √(%s) = %s mm' % (' + '.join(['uA²', 'uδ²'] + (['ue²'] if emax else [])), n(uc, 5)),
          'Expandida: U = k·uc = %s·%s = %s mm%s' % (nc(k, 2), n(uc, 5), n(U, 5),
                                                     ' (k = 2: nivel de confianza de aproximadamente 95 %, distribución normal)' if k == 2 else ''),
          'Resultado: (%s ± %s) mm, k = %s (U con dos cifras significativas y la media a la misma posición)'
          % (n(media, dec), n(Ur, dec), nc(k, 2))]
    return {'media': media, 's': s, 'ua': ua, 'ur': ur, 'ue': ue, 'uc': uc, 'U': U, 'Ur': Ur, 'dec': dec}, L


def nonio(div, nd, entero=None, linea=None):
    a = div / nd
    L = ['Apreciación del nonio: a = división de la regla / divisiones del nonio = %s/%d = %s mm' % (nc(div), nd, nc(a))]
    r = {'a': a}
    if entero is not None and linea is not None:
        if not 0 <= linea < nd:
            raise ValueError('la línea del nonio va de 0 a %d' % (nd - 1))
        r['lectura'] = entero + linea * a
        L.append('Lectura = regla antes del cero del nonio + línea que coincide × a = %s + %d·%s = %s mm'
                 % (nc(entero), linea, nc(a), nc(r['lectura'])))
    return r, L


def micrometro(paso=0.5, nd=50, escala=None, tambor=None):
    a = paso / nd
    L = ['Apreciación: a = paso del tornillo / divisiones del tambor = %s/%d = %s mm' % (nc(paso), nd, nc(a))]
    r = {'a': a}
    if escala is not None and tambor is not None:
        if not 0 <= tambor < nd:
            raise ValueError('la división del tambor va de 0 a %d' % (nd - 1))
        r['lectura'] = escala + tambor * a
        L.append('Lectura = escala del cilindro (mm y medios mm) + división del tambor × a = %s + %d·%s = %s mm'
                 % (nc(escala), tambor, nc(a), nc(r['lectura'])))
    return r, L


def error_abbe(h, theta_grados):
    """Error de Abbe: e = h*sen(theta), h distancia entre el eje de medida y la escala (mm)."""
    return h * math.sin(math.radians(theta_grados))


# ------------------------------------------------------------------------------------------ demo
def cerca(x, y, tol=1e-9):
    return abs(x - y) <= tol


def cmd_demo():
    ok = []
    # 1. Ejemplo del SKILL.md: buje que gira sobre un eje, Ø 25 H7/g6
    r, _ = ajuste(25, 'H7/g6')
    ok.append(('Ø 25 H7/g6: H7 +21/0, g6 −7/−20, juego de 7 a 41 µm, con juego',
               r['agujero']['sup'] == 21 and r['agujero']['inf'] == 0 and r['eje']['sup'] == -7 and r['eje']['inf'] == -20
               and r['jmin'] == 7 and r['jmax'] == 41 and r['tipo'] == 'con juego'))
    # 2. Ajustes de Wikipedia "Engineering fit" a 50 mm (juego máximo y mínimo en µm)
    for clases, jmax, jmin, tipo in (('H8/f7', 89, 25, 'con juego'), ('H7/k6', 23, -18, 'incierto (de transición)'),
                                     ('H7/p6', -1, -42, 'con aprieto')):
        r, _ = ajuste(50, clases)
        ok.append(('Ø 50 %s: juego %s a %s µm (Wikipedia: %s a %s), %s' % (clases, um(r['jmin']), um(r['jmax']), um(jmin), um(jmax), tipo),
                   r['jmax'] == jmax and r['jmin'] == jmin and r['tipo'] == tipo))
    # 3. Tabla de ajustes del SKILL.md a 25 mm, contra BS 4500:1969 (Machinery's Handbook, tabla 3, fila 18-30)
    bs = {'H11/c11': (110, 370), 'H8/f7': (20, 74), 'H7/g6': (7, 41), 'H7/h6': (0, 34), 'H7/k6': (-15, 19),
          'H7/n6': (-28, 6), 'H7/p6': (-35, -1), 'H7/s6': (-48, -14)}
    bien = all(ajuste(25, k)[0]['jmin'] == v[0] and ajuste(25, k)[0]['jmax'] == v[1] for k, v in bs.items())
    ok.append(('ocho ajustes recomendados a 25 mm iguales a BS 4500 (juegos mínimo y máximo)', bien))
    # 4. Aprieto grande: H7/s6 en 450-500 mm (BS 4500: −292 µm) y K7 de 300 mm (RoyMech: +16/−36 µm)
    r, _ = ajuste(480, 'H7/s6')
    ok.append(('Ø 480 H7/s6: Jmín = %s µm (BS 4500: −292)' % um(r['jmin']), r['jmin'] == -292))
    d = desviaciones(300, 'K7')
    ok.append(('Ø 300 K7: %s/%s µm (RoyMech: +16/−36)' % (um(d['sup']), um(d['inf'])), d['sup'] == 16 and d['inf'] == -36))
    # 5. Regla de Δ: K7 de 18 a 30 mm, ES = −2 + 8 = +6; P8 sin Δ; y valores de JIS B 0401-2 (Miki Pulley, Misumi)
    d = desviaciones(25, 'K7')
    ok.append(('Ø 25 K7: Δ = 21 − 13 = 8, ES = +6, EI = −15 µm', delta(25, 7) == 8 and d['sup'] == 6 and d['inf'] == -15))
    tabla = [(475, 'r6', 172, 132), (475, 'N7', -17, -80), (475, 'P7', -45, -108), (110, 'js6', 11, -11),
             (2, 'm6', 8, 2), (2, 'K7', 0, -10), (2, 'N7', -4, -14), (2, 'P7', -6, -16), (2, 'F7', 16, 6),
             (25, 'JS7', 10.5, -10.5), (35, 'P8', -26, -65), (12, 'c9', -95, -138), (380, 'e8', -125, -214)]
    malos = [c for D, c, s, i in tabla if not (cerca(desviaciones(D, c)['sup'], s) and cerca(desviaciones(D, c)['inf'], i))]
    ok.append(('13 clases sueltas contra JIS B 0401-2 e ISO 286-2 publicadas%s' % (': fallan ' + ', '.join(malos) if malos else ''), not malos))
    # 6. IT y factor i
    r, _ = it_cmd(25, 7)
    i_25 = 0.45 * math.sqrt(18 * 30) ** (1 / 3) + 0.001 * math.sqrt(18 * 30)
    ok.append(('IT7 de 25 mm = 21 µm; i = %s µm y 16·i = %s µm' % (n(r['i'], 3), n(16 * r['i'], 1)),
               r['it'] == 21 and cerca(r['i'], i_25) and abs(16 * r['i'] - 21) < 0.5))
    fuera = [(g, j) for g in range(6, 14) for j in range(13) if IT[str(g + 5)][j] != 10 * IT[str(g)][j]]
    ok.append(('desde IT6, cada cinco grados la tolerancia se multiplica por 10 (única excepción: IT6 de 3 a 6 mm, 8 µm, e IT11 75 µm)',
               fuera == [(6, 1)]))
    # 7. ISO 2768
    ok.append(('ISO 2768-m de 85 mm: ±0,3 mm', cerca(general(85, 'm')[0]['t'], 0.3)))
    ok.append(('ISO 2768-f, chaflán de 4 mm: ±0,5 mm; ángulo con lado corto de 30 mm en clase c: ±1°',
               cerca(general(4, 'f', 'arista')[0]['t'], 0.5) and general(30, 'c', 'angulo')[0]['minutos'] == 60))
    ok.append(('ISO 2768-K, planitud de una cara de 250 mm: 0,4 mm', cerca(general(250, 'mK', 'planitud')[0]['t'], 0.4)))
    # 8. Cadena de cotas del SKILL.md: 50 ±0,1 − 20 ±0,05 − 29,8 ±0,05
    r, _ = cadena(['+50:0.1', '-20:0.05', '-29.8:0.05'])
    ok.append(('cadena: nominal 0,200; peor caso 0,000 a 0,400; RSS ±%s mm' % n(r['t_rss'] / 2, 4),
               cerca(r['nom'], 0.2) and cerca(r['min'], 0.0) and cerca(r['max'], 0.4) and cerca(r['t_rss'], math.sqrt(0.06))))
    rnd = random.Random(286)
    sig = [0.2 / 6, 0.1 / 6, 0.1 / 6]
    muestras = 100000
    dentro = sum(1 for _ in range(muestras)
                 if abs(rnd.gauss(0, sig[0]) - rnd.gauss(0, sig[1]) - rnd.gauss(0, sig[2])) <= r['t_rss'] / 2)
    ok.append(('simulación de %d conjuntos con tolerancia = ±3σ: %s %% dentro del RSS (teórico 99,73 %%)' % (muestras, n(100 * dentro / muestras, 2)),
               0.996 <= dentro / muestras <= 0.9985 and cerca(math.erf(3 / math.sqrt(2)), 0.9973, 5e-5)))
    # 9. Incertidumbre del SKILL.md: cinco lecturas con micrómetro de 0,001 mm y error máximo ±0,002 mm
    lect = [24.986, 24.988, 24.987, 24.985, 24.988]
    r, _ = incertidumbre(lect, 0.001, 0.002)
    m = sum(lect) / 5
    s = math.sqrt(sum((v - m) ** 2 for v in lect) / 4)
    uc = math.sqrt((s / math.sqrt(5)) ** 2 + (0.001 / math.sqrt(12)) ** 2 + (0.002 / math.sqrt(3)) ** 2)
    ok.append(('incertidumbre: media %s mm, U = %s mm (k = 2)' % (n(r['media'], 4), n(r['Ur'], r['dec'])),
               cerca(r['media'], 24.9868, 1e-9) and cerca(r['U'], 2 * uc) and cerca(r['Ur'], 0.0027)))
    # 10. Calibre, micrómetro y error de Abbe
    r1, _ = nonio(1, 50, 23, 37)
    r2, _ = micrometro(0.5, 50, 12.5, 28)
    ok.append(('nonio 1/50: a = 0,02 mm y lectura 23,74 mm; micrómetro: a = 0,01 mm y 12,78 mm',
               cerca(r1['a'], 0.02) and cerca(r1['lectura'], 23.74) and cerca(r2['a'], 0.01) and cerca(r2['lectura'], 12.78)))
    ok.append(('error de Abbe con h = 25 mm y 0,02°: %s mm' % n(error_abbe(25, 0.02), 4), cerca(error_abbe(25, 0.02), 0.00873, 5e-6)))
    ok.append(('nonio: n divisiones en n − 1 (o 2·n − 1) divisiones de la regla dan a = 1/n',
               all(cerca(1 - (k - 1) / k, 1 / k) and cerca(2 - (2 * k - 1) / k, 1 / k) for k in (10, 20, 50))))
    ok.append(('bloques patrón: 1,005 + 1,12 + 9 + 30 = 41,125 mm', cerca(1.005 + 1.12 + 9 + 30, 41.125)))
    r, _ = ajuste(25, 'g6')
    lo, hi = 25 + r['clase']['inf'] / 1000, 25 + r['clase']['sup'] / 1000
    ok.append(('eje Ø 25 g6 medido (24,9868 ± 0,0027) mm: queda entero entre %s y %s mm, cumple' % (n(lo), n(hi)),
               lo <= 24.9868 - 0.0027 and 24.9868 + 0.0027 <= hi))
    for nombre, b in ok:
        print('  %s %s' % ('ok ' if b else 'MAL', nombre))
    todo = all(b for _, b in ok)
    print('DEMO %s' % ('OK' if todo else 'FALLO'))
    return 0 if todo else 1


# ------------------------------------------------------------------------------------------ principal
def separar(lista):
    out = []
    for t in lista:
        out += [p for p in re.split(r'[\s;]+', t) if p]
    return out


def construir_parser():
    ap = argparse.ArgumentParser(prog='tolerancias.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('ajuste', help='límites, juego y aprieto de un ajuste ISO 286 (ajuste 25 H7/g6)')
    p.add_argument('D', type=num, help='cota nominal en mm (más de 0 hasta 500)')
    p.add_argument('clases', help='ajuste agujero/eje (H7/g6, G7/h6) o una sola clase (g6, H7)')
    p = sp.add_parser('it', help='tolerancia fundamental IT (it 25 7)')
    p.add_argument('D', type=num, help='cota nominal en mm (más de 0 hasta 500)')
    p.add_argument('grado', help='grado: 01, 0, 1 a 18 (o IT7)')
    p = sp.add_parser('general', help='tolerancia general ISO 2768 (general 85 m)')
    p.add_argument('cota', type=num, help='cota en mm (en ángulos, el lado más corto; en ISO 2768-2, el largo que pide la tabla)')
    p.add_argument('clase', help='f, m, c o v (ISO 2768-1); H, K o L (ISO 2768-2); o las dos juntas: mK')
    p.add_argument('--tipo', default='lineal', choices=['lineal', 'arista', 'angulo', 'rectitud', 'planitud',
                                                        'perpendicularidad', 'simetria', 'oscilacion'])
    p = sp.add_parser('cadena', help='cadena de cotas: peor caso y RSS (cadena "+50:0.1 -20:0.05")')
    p.add_argument('cotas', nargs='+', help='cotas entre comillas: +50:0.1 o -20:+0.05:-0.02')
    p.add_argument('--min', type=num, help='valor mínimo admisible de la cota de cierre (mm)')
    p.add_argument('--max', type=num, help='valor máximo admisible de la cota de cierre (mm)')
    p = sp.add_parser('incertidumbre', help='incertidumbre de una medición repetida (GUM)')
    p.add_argument('lecturas', nargs='+', help='lecturas en mm, entre comillas y separadas por espacios')
    p.add_argument('--res', type=num, required=True, help='resolución (apreciación) del instrumento en mm')
    p.add_argument('--emax', type=num, help='error máximo del instrumento ± en mm (certificado o ficha)')
    p.add_argument('--k', type=num, default=2.0, help='factor de cobertura (2 por defecto)')
    p = sp.add_parser('nonio', help='apreciación y lectura de un calibre con nonio')
    p.add_argument('--div', type=num, default=1.0, help='división de la regla en mm (1 por defecto)')
    p.add_argument('--n', type=int, required=True, help='cantidad de divisiones del nonio (10, 20 o 50)')
    p.add_argument('--entero', type=num, help='mm de la regla antes del cero del nonio')
    p.add_argument('--linea', type=int, help='número de la línea del nonio que coincide')
    p = sp.add_parser('micrometro', help='apreciación y lectura de un micrómetro')
    p.add_argument('--paso', type=num, default=0.5, help='paso del tornillo en mm (0,5 por defecto)')
    p.add_argument('--div', type=int, default=50, help='divisiones del tambor (50 por defecto)')
    p.add_argument('--escala', type=num, help='lectura del cilindro en mm (mm y medios mm)')
    p.add_argument('--tambor', type=int, help='división del tambor que coincide con la línea de referencia')
    sp.add_parser('demo', help='reproduce los ejemplos del SKILL.md y termina en DEMO OK')
    return ap


def main(argv=None):
    a = construir_parser().parse_args(argv)
    try:
        if a.cmd == 'demo':
            return cmd_demo()
        if a.cmd == 'ajuste':
            _, L = ajuste(a.D, a.clases.replace(' ', ''))
        elif a.cmd == 'it':
            _, L = it_cmd(a.D, a.grado)
        elif a.cmd == 'general':
            _, L = general(a.cota, a.clase, a.tipo)
        elif a.cmd == 'cadena':
            _, L = cadena(separar(a.cotas), a.min, a.max)
        elif a.cmd == 'incertidumbre':
            _, L = incertidumbre([num(v) for v in separar(a.lecturas)], a.res, a.emax, a.k)
        elif a.cmd == 'nonio':
            _, L = nonio(a.div, a.n, a.entero, a.linea)
        else:
            _, L = micrometro(a.paso, a.div, a.escala, a.tambor)
    except (ValueError, argparse.ArgumentTypeError) as ex:
        print('tolerancias.py: %s' % ex, file=sys.stderr)
        return 2
    print('\n'.join(L))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
