#!/usr/bin/env python3
"""psicrometria.py - aire humedo y secaderos por aire caliente (solo biblioteca estandar).

Formulas de ASHRAE Handbook - Fundamentals (2017), cap. 1 "Psychrometrics" (aire humedo como gas ideal):
  presion de saturacion de Hyland y Wexler (sobre hielo debajo de 0 C y sobre agua de 0 a 200 C),
  W = 0,621945 pw/(p - pw), h = 1,006 t + W (2501 + 1,86 t), v = 0,287042 (t + 273,15)(1 + 1,607858 W)/p,
  bulbo humedo con la ecuacion psicrometrica y presion segun la altitud p = 101,325 (1 - 2,25577e-5 Z)^5,2559.

Comandos:
  aire --t 20 --hr 50 [--p KPA | --altitud M]       propiedades del aire (en lugar de --hr: --w g/kg o --tbh C)
  secador --producto KG --hi % --hf % --tamb C --hramb % --taire C (--hrsal % | --tsal C) [opciones]
          balance de masa y energia de un secadero de aire caliente. Sin --lote-horas, KG es por hora (continuo);
          con --lote-horas H, KG es la carga de un lote que se seca en H horas.
          Opciones: --rend 0.9 (rendimiento del calentador), --pci MJ/kg o MJ/m3 (consumo de combustible),
          --diagrama carta.svg (dibuja el proceso). Con --hrsal sola o --tsal sola, el secado se toma adiabatico
          (el aire sale con la misma entalpia); con las dos, se usa el estado de salida dado.
  mezcla --a "t;hr;kg" --b "t;hr;kg"               mezcla de dos corrientes de aire (kg de aire seco o kg/h),
                                                    por ejemplo aire de salida recirculado con aire nuevo
  humedad --bh % | --bs %                           humedad del producto de base humeda a base seca y al reves
  diagrama --salida carta.svg [--punto "t;hr;nombre" ...] [--tmax C] [--p KPA]
                                                    diagrama psicrometrico en SVG con puntos unidos en orden
  demo                                              reproduce el ejemplo del SKILL.md y verifica los resultados
Unidades: t en C, p en kPa, W en g de agua por kg de aire seco, h en kJ/kg de aire seco, v en m3/kg de aire seco.
Precision contra CoolProp 8.0 (aire humedo real), de -20 a 50 C: W 0,7 %, h 1,2 kJ/kg, v 0,1 %, rocio y bulbo humedo
0,03 C (cerca de 0 C el bulbo humedo puede diferir 0,5 C: agua o hielo en la mecha); hasta 80 C, W 1,1 %.
"""
import argparse
import math
import os
import sys
import tempfile

EPS = 0.621945      # relacion de masas molares agua/aire seco
R_AS = 0.287042     # kJ/(kg K) del aire seco
P_NORMAL = 101.325  # kPa


# ------------------------------------------------------------------------------------------ propiedades
def p_sat(t):
    """Presion de saturacion del vapor de agua en kPa (Hyland y Wexler, ASHRAE 2017 cap. 1)."""
    T = t + 273.15
    if t < 0:
        ln = (-5.6745359e3 / T + 6.3925247 - 9.6778430e-3 * T + 6.2215701e-7 * T ** 2 + 2.0747825e-9 * T ** 3
              - 9.4840240e-13 * T ** 4 + 4.1635019 * math.log(T))
    else:
        ln = (-5.8002206e3 / T + 1.3914993 - 4.8640239e-2 * T + 4.1764768e-5 * T ** 2 - 1.4452093e-8 * T ** 3
              + 6.5459673 * math.log(T))
    return math.exp(ln) / 1000.0


def p_altitud(z):
    return P_NORMAL * (1 - 2.25577e-5 * z) ** 5.2559


def w_de_pw(pw, p):
    return EPS * pw / (p - pw)


def pw_de_w(w, p):
    return p * w / (EPS + w)


def entalpia(t, w):
    return 1.006 * t + w * (2501 + 1.86 * t)


def volumen(t, w, p):
    return R_AS * (t + 273.15) * (1 + 1.607858 * w) / p


def biseccion(f, a, b, tol=1e-9, n=300):
    fa = f(a)
    if fa == 0:
        return a
    if fa * f(b) > 0:
        raise ValueError('sin solución entre %g y %g' % (a, b))
    for _ in range(n):
        m = (a + b) / 2
        fm = f(m)
        if fm == 0 or (b - a) / 2 < tol:
            return m
        if fa * fm < 0:
            b = m
        else:
            a, fa = m, fm
    return (a + b) / 2


def t_rocio(pw):
    return biseccion(lambda x: p_sat(x) - pw, -100, 200)


def w_bulbo(t, tbh, p):
    """Ecuacion psicrometrica: W del aire a t con bulbo humedo tbh (ASHRAE 2017 cap. 1)."""
    ws = w_de_pw(p_sat(tbh), p)
    if tbh >= 0:
        return ((2501 - 2.326 * tbh) * ws - 1.006 * (t - tbh)) / (2501 + 1.86 * t - 4.186 * tbh)
    return ((2830 - 0.24 * tbh) * ws - 1.006 * (t - tbh)) / (2830 + 1.86 * t - 2.1 * tbh)


def t_bulbo(t, w, p):
    tdp = t_rocio(pw_de_w(w, p))
    if t - tdp < 1e-6:
        return t
    return biseccion(lambda x: w_bulbo(t, x, p) - w, tdp - 1e-6, t)


def estado(t, p=P_NORMAL, hr=None, w=None, tbh=None, nombre=''):
    """Estado del aire a partir de t y una de: hr [%], w [kg/kg] o tbh [C]."""
    pws = p_sat(t)
    if pws >= p:
        raise ValueError('a %.1f °C el agua hierve a esta presión: el aire no puede estar a esa temperatura y %.2f kPa' % (t, p))
    if hr is not None:
        if not 0 <= hr <= 100:
            raise ValueError('la humedad relativa va de 0 a 100 %')
        pw = hr / 100 * pws
        w = w_de_pw(pw, p)
    elif w is not None:
        pw = pw_de_w(w, p)
    elif tbh is not None:
        if tbh > t:
            raise ValueError('el bulbo húmedo no puede ser mayor que la temperatura del aire')
        w = w_bulbo(t, tbh, p)
        pw = pw_de_w(w, p)
    else:
        raise ValueError('falta la humedad: hr, w o tbh')
    if w < 0:
        raise ValueError('datos imposibles: dan humedad absoluta negativa')
    if pw > pws * 1.0005:
        raise ValueError('aire sobresaturado: a %.1f °C entra como máximo W = %.2f g/kg' % (t, 1000 * w_de_pw(pws, p)))
    e = {'nombre': nombre, 't': t, 'p': p, 'w': w, 'pw': pw, 'pws': pws, 'hr': 100 * pw / pws,
         'h': entalpia(t, w), 'v': volumen(t, w, p)}
    e['tdp'] = t_rocio(pw) if pw > 1e-9 else float('nan')
    e['tbh'] = t_bulbo(t, w, p) if pw > 1e-9 else float('nan')
    return e


# ------------------------------------------------------------------------------------------ formato
def n(x, d=2):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return '-'
    return ('%.*f' % (d, x)).replace('.', ',')


def tabla_estados(estados):
    filas = [('Estado', 't [°C]', 'HR [%]', 'W [g/kg]', 'h [kJ/kg]', 'v [m³/kg]', 't rocío [°C]', 't bh [°C]')]
    for e in estados:
        filas.append((e['nombre'] or '-', n(e['t'], 1), n(e['hr'], 1), n(1000 * e['w'], 2), n(e['h'], 1),
                      n(e['v'], 3), n(e['tdp'], 1), n(e['tbh'], 1)))
    anchos = [max(len(f[i]) for f in filas) for i in range(len(filas[0]))]
    lineas = ['| ' + ' | '.join(c.ljust(anchos[i]) for i, c in enumerate(f)) + ' |' for f in filas]
    lineas.insert(1, '|' + '|'.join('-' * (a + 2) for a in anchos) + '|')
    return '\n'.join(lineas)


# ------------------------------------------------------------------------------------------ secador
def salida_adiabatica(h2, p, hrsal=None, tsal=None, tope=200):
    if tsal is not None:
        w3 = (h2 - 1.006 * tsal) / (2501 + 1.86 * tsal)
        return estado(tsal, p, w=w3, nombre='3 salida')
    f = lambda t: entalpia(t, w_de_pw(hrsal / 100 * p_sat(t), p)) - h2
    t3 = biseccion(f, -40, tope)
    return estado(t3, p, hr=hrsal, nombre='3 salida')


def secador(m_h, hi, hf, tamb, hramb, taire, p=P_NORMAL, hrsal=None, tsal=None, lote_horas=None, rend=1.0, pci=None):
    if not 0 <= hf < hi < 100:
        raise ValueError('la humedad final tiene que ser menor que la inicial (las dos en %, base húmeda, menores que 100)')
    if hrsal is None and tsal is None:
        raise ValueError('falta el estado del aire a la salida: --hrsal o --tsal')
    if not 0 < rend <= 1:
        raise ValueError('el rendimiento va entre 0 y 1')
    wi, wf = hi / 100, hf / 100
    r = {'m_h': m_h, 'wi': wi, 'wf': wf, 'lote_horas': lote_horas}
    r['m_s'] = m_h * (1 - wi)
    r['m_w'] = m_h * (wi - wf) / (1 - wf)
    r['m_fin'] = r['m_s'] / (1 - wf)
    e1 = estado(tamb, p, hr=hramb, nombre='1 ambiente')
    e2 = estado(taire, p, w=e1['w'], nombre='2 aire caliente')
    if hrsal is not None and tsal is not None:
        e3 = estado(tsal, p, hr=hrsal, nombre='3 salida')
        r['adiabatico'] = False
    else:
        e3 = salida_adiabatica(e2['h'], p, hrsal=hrsal, tsal=tsal, tope=taire)
        r['adiabatico'] = True
    dw = e3['w'] - e1['w']
    if dw <= 1e-6:
        raise ValueError('con esa salida el aire no levanta agua (W3 ≤ W1): subir la temperatura del aire o la HR de salida')
    if e3['t'] > e2['t'] + 1e-6:
        raise ValueError('el aire no puede salir más caliente de lo que entra')
    horas = lote_horas or 1.0
    r['m_w_h'] = r['m_w'] / horas
    r['m_a'] = r['m_w'] / dw                      # kg de aire seco (por hora o por lote)
    r['m_a_h'] = r['m_a'] / horas                 # kg/h
    r['V1'] = r['m_a_h'] * e1['v']                # m3/h a la entrada del ventilador (aire ambiente)
    r['V2'] = r['m_a_h'] * e2['v']                # m3/h a la entrada del secador (aire caliente)
    r['P_aire'] = r['m_a_h'] * (e2['h'] - e1['h']) / 3600   # kW
    r['P_cal'] = r['P_aire'] / rend
    r['E_esp'] = r['P_cal'] * 3600 / r['m_w_h']   # kJ por kg de agua evaporada
    r['rend'] = rend
    r['pci'] = pci
    r['comb_h'] = r['P_cal'] * 3.6 / pci if pci else None   # (kg o m3)/h; pci en MJ por unidad
    r['estados'] = [e1, e2, e3]
    r['perdida'] = e2['h'] - e3['h']              # kJ/kg que no quedaron en el aire (0 si es adiabatico)
    return r


def informe_secador(r):
    e1, e2, e3 = r['estados']
    por = 'h' if not r['lote_horas'] else 'lote'
    L = []
    L.append('Datos: producto %s kg/%s, humedad %s %% → %s %% (base húmeda)%s; presión %s kPa.'
             % (n(r['m_h'], 1), por, n(100 * r['wi'], 1), n(100 * r['wf'], 1),
                (', lote de %s h' % n(r['lote_horas'], 1)) if r['lote_horas'] else '', n(e1['p'], 3)))
    L.append('')
    L.append('1) Producto')
    L.append('   Sólidos secos:     m_s = m_h·(1 − w_i) = %s·(1 − %s) = %s kg/%s'
             % (n(r['m_h'], 1), n(r['wi'], 3), n(r['m_s'], 2), por))
    L.append('   Agua a evaporar:   m_w = m_h·(w_i − w_f)/(1 − w_f) = %s·(%s − %s)/(1 − %s) = %s kg/%s'
             % (n(r['m_h'], 1), n(r['wi'], 3), n(r['wf'], 3), n(r['wf'], 3), n(r['m_w'], 2), por))
    L.append('   Producto seco:     m_f = m_s/(1 − w_f) = %s kg/%s' % (n(r['m_fin'], 2), por))
    L.append('')
    L.append('2) Aire (%s)' % ('salida adiabática: h3 = h2' if r['adiabatico'] else 'estado de salida dado'))
    L.append(tabla_estados(r['estados']))
    L.append('')
    L.append('3) Aire necesario')
    L.append('   Aire seco:   m_a = m_w/(W3 − W1) = %s/(%s − %s) = %s kg/%s'
             % (n(r['m_w'], 2), n(e3['w'], 5), n(e1['w'], 5), n(r['m_a'], 0), por))
    if r['lote_horas']:
        L.append('   Por hora:    %s kg/h de aire seco y %s kg/h de agua evaporada' % (n(r['m_a_h'], 0), n(r['m_w_h'], 2)))
    L.append('   Caudal en el ventilador (aire ambiente): V1 = m_a·v1 = %s m³/h' % n(r['V1'], 0))
    L.append('   Caudal a la entrada del secador (caliente): V2 = m_a·v2 = %s m³/h' % n(r['V2'], 0))
    L.append('')
    L.append('4) Energía')
    L.append('   Calor al aire:      P = m_a·(h2 − h1)/3600 = %s·(%s − %s)/3600 = %s kW'
             % (n(r['m_a_h'], 0), n(e2['h'], 1), n(e1['h'], 1), n(r['P_aire'], 2)))
    L.append('   Calentador:         P_cal = P/η = %s/%s = %s kW' % (n(r['P_aire'], 2), n(r['rend'], 2), n(r['P_cal'], 2)))
    L.append('   Energía específica: %s kJ por kg de agua evaporada' % n(r['E_esp'], 0))
    if r['comb_h']:
        L.append('   Combustible:        P_cal·3,6/PCI = %s·3,6/%s = %s unidades/h (kg o m³, según el PCI dado en MJ)'
                 % (n(r['P_cal'], 2), n(r['pci'], 2), n(r['comb_h'], 3)))
    L.append('')
    L.append('Chequeos')
    L.append('   Balance de agua: m_a·(W3 − W1) = %s kg/%s (igual a m_w)' % (n(r['m_a'] * (e3['w'] - e1['w']), 2), por))
    if not r['adiabatico']:
        L.append('   El aire salió con %s kJ/kg menos que lo que entró: calor que se llevaron el producto y las paredes.'
                 % n(r['perdida'], 1))
    if e3['hr'] > 90:
        L.append('   AVISO: el aire sale casi saturado (%s %%): riesgo de condensación en conductos fríos.' % n(e3['hr'], 0))
    if e3['t'] - e3['tdp'] < 3:
        L.append('   AVISO: la salida está a menos de 3 °C de su punto de rocío.')
    return '\n'.join(L)


def mezcla(ea, ma, eb, mb, p=P_NORMAL):
    """Mezcla adiabatica: balances de agua y energia por kg de aire seco."""
    if ma <= 0 or mb <= 0:
        raise ValueError('las masas de aire seco tienen que ser positivas')
    w = (ma * ea['w'] + mb * eb['w']) / (ma + mb)
    h = (ma * ea['h'] + mb * eb['h']) / (ma + mb)
    t = (h - 2501 * w) / (1.006 + 1.86 * w)
    pws = p_sat(t)
    if pw_de_w(w, p) > pws:  # la mezcla cae en la zona de niebla: condensa
        raise ValueError('la mezcla queda sobresaturada (niebla): condensa agua en el conducto')
    return estado(t, p, w=w, nombre='mezcla')


# ------------------------------------------------------------------------------------------ diagrama SVG
def diagrama_svg(puntos, p=P_NORMAL, tmin=0.0, tmax=None, wmax=None, titulo='Diagrama psicrométrico'):
    """puntos: lista de estados (dict de estado()); se unen en orden con flechas."""
    tmax = tmax or max([50.0] + [math.ceil((e['t'] + 5) / 10) * 10 for e in puntos])
    if wmax is None:
        wmax = max([0.03] + [e['w'] * 1.25 for e in puntos])
        wmax = min(wmax, w_de_pw(min(p_sat(tmax), 0.6 * p), p))
    wmax = math.ceil(wmax * 1000 / 5) * 5 / 1000
    W, H, iz, de, ar, ab = 900, 600, 70, 70, 40, 60
    X = lambda t: iz + (t - tmin) / (tmax - tmin) * (W - iz - de)
    Y = lambda w: H - ab - w / wmax * (H - ab - ar)
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="Arial, sans-serif">' % (W, H, W, H),
         '<rect width="100%" height="100%" fill="white"/>',
         '<text x="%d" y="24" font-size="17" font-weight="bold" fill="#222">%s</text>' % (iz, titulo),
         '<text x="%d" y="24" font-size="12" fill="#555" text-anchor="end">p = %s kPa · ASHRAE 2017, cap. 1</text>' % (W - de, n(p, 3))]
    s.append('<clipPath id="area"><rect x="%d" y="%d" width="%d" height="%d"/></clipPath>' % (iz, ar, W - iz - de, H - ab - ar))
    paso_t = 5 if tmax - tmin <= 60 else 10
    t = math.ceil(tmin / paso_t) * paso_t
    while t <= tmax + 1e-9:
        s.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#eee"/>' % (X(t), ar, X(t), H - ab))
        s.append('<text x="%.1f" y="%d" font-size="11" text-anchor="middle" fill="#444">%g</text>' % (X(t), H - ab + 16, t))
        t += paso_t
    paso_w = 0.005 if wmax <= 0.05 else 0.01
    w = 0.0
    while w <= wmax + 1e-12:
        s.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#eee"/>' % (iz, Y(w), W - de, Y(w)))
        s.append('<text x="%d" y="%.1f" font-size="11" text-anchor="start" fill="#444">%g</text>' % (W - de + 6, Y(w) + 4, round(w * 1000, 1)))
        w += paso_w
    # entalpia constante cada 10 o 20 kJ/kg
    hmin, hmax = entalpia(tmin, 0), entalpia(tmax, wmax)
    paso_h = 10 if hmax - hmin <= 150 else 20
    h = math.ceil(hmin / paso_h) * paso_h
    while h <= hmax:
        pts = []
        for i in range(61):
            tt = tmin + (tmax - tmin) * i / 60
            ww = (h - 1.006 * tt) / (2501 + 1.86 * tt)
            if 0 <= ww <= w_de_pw(p_sat(tt), p) and ww <= wmax:
                pts.append('%.1f,%.1f' % (X(tt), Y(ww)))
        if len(pts) > 1:
            s.append('<polyline points="%s" fill="none" stroke="#9bb" stroke-width="0.8" stroke-dasharray="4 3" clip-path="url(#area)"/>' % ' '.join(pts))
            x0, y0 = pts[0].split(',')
            s.append('<text x="%s" y="%.1f" font-size="9" fill="#688" paint-order="stroke" stroke="white" stroke-width="3">%g</text>' % (x0, float(y0) - 3, h))
        h += paso_h
    # humedad relativa: cada curva con su rotulo a distinta altura para que no se pisen
    halo = 'paint-order="stroke" stroke="white" stroke-width="3"'
    for hr in range(10, 101, 10):
        pts = []
        for i in range(121):
            tt = tmin + (tmax - tmin) * i / 120
            pw = hr / 100 * p_sat(tt)
            if pw >= p:
                break
            ww = w_de_pw(pw, p)
            pts.append('%.1f,%.1f' % (X(tt), Y(min(ww, wmax * 1.02))))
            if ww > wmax:
                break
        ancho = 2.2 if hr == 100 else 0.9
        color = '#c8102e' if hr == 100 else '#5a7fb0'
        s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s" clip-path="url(#area)"/>' % (' '.join(pts), color, ancho))
        objetivo = wmax * (0.20 + 0.075 * (hr / 10 - 1))
        f = lambda tt: w_de_pw(hr / 100 * p_sat(tt), p) - objetivo
        if f(tmin) < 0 < f(min(tmax, 99.0)):
            tl = biseccion(f, tmin, min(tmax, 99.0))
            xl, yl = X(tl), Y(objetivo)
        else:
            xl, yl = [float(v) for v in pts[-1].split(',')]
            yl = max(yl, ar + 12)
        rotulo = 'saturación' if hr == 100 else '%d %%' % hr
        s.append('<text x="%.1f" y="%.1f" font-size="10" fill="%s" %s>%s</text>' % (xl + 4, yl + 3, color, halo, rotulo))
    s.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#333"/>' % (iz, ar, W - iz - de, H - ab - ar))
    s.append('<text x="%.1f" y="%d" font-size="13" text-anchor="middle" fill="#222">Temperatura de bulbo seco t [°C]</text>' % ((iz + W - de) / 2, H - 18))
    s.append('<text x="%d" y="%d" font-size="13" text-anchor="middle" fill="#222" transform="rotate(90 %d %d)">Humedad absoluta W [g/kg de aire seco]</text>'
             % (W - 18, (ar + H - ab) // 2, W - 18, (ar + H - ab) // 2))
    s.append('<text x="%d" y="%d" font-size="10" fill="#688">líneas de trazos: entalpía h [kJ/kg]; curvas azules: humedad relativa</text>' % (iz, H - 4))
    # proceso
    s.append('<defs><marker id="fl" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>')
    for a, b in zip(puntos, puntos[1:]):
        x1, y1, x2, y2 = X(a['t']), Y(a['w']), X(b['t']), Y(b['w'])
        largo = math.hypot(x2 - x1, y2 - y1)
        if largo < 14:
            continue
        ux, uy = (x2 - x1) / largo, (y2 - y1) / largo
        s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#111" stroke-width="2" marker-end="url(#fl)"/>'
                 % (x1 + 6 * ux, y1 + 6 * uy, x2 - 7 * ux, y2 - 7 * uy))
    for i, e in enumerate(puntos):
        x, y = X(e['t']), Y(e['w'])
        vecinos = [X(o['t']) for o in puntos[max(0, i - 1):i + 2] if o is not e]
        izquierda = (bool(vecinos) and sum(vecinos) / len(vecinos) > x and x - iz > 170) or x > W - de - 170
        dx, anc = (-9, 'end') if izquierda else (9, 'start')
        s.append('<circle cx="%.1f" cy="%.1f" r="5" fill="#111"/>' % (x, y))
        s.append('<text x="%.1f" y="%.1f" font-size="12" font-weight="bold" fill="#111" text-anchor="%s" %s>%s</text>'
                 % (x + dx, y - 8, anc, halo, (e['nombre'] or '').replace('&', 'y').replace('<', '')))
        s.append('<text x="%.1f" y="%.1f" font-size="10" fill="#333" text-anchor="%s" %s>%s °C · %s %% · %s g/kg</text>'
                 % (x + dx, y + 16, anc, halo, n(e['t'], 1), n(e['hr'], 0), n(1000 * e['w'], 1)))
    s.append('</svg>')
    return '\n'.join(s)


# ------------------------------------------------------------------------------------------ comandos
def presion(a):
    if getattr(a, 'altitud', None) is not None:
        return p_altitud(a.altitud)
    return a.p if getattr(a, 'p', None) else P_NORMAL


def cmd_aire(a):
    p = presion(a)
    e = estado(a.t, p, hr=a.hr, w=(a.w / 1000 if a.w is not None else None), tbh=a.tbh, nombre='aire')
    print(tabla_estados([e]))
    print('Presión %s kPa · presión de vapor %s kPa · de saturación %s kPa' % (n(p, 3), n(e['pw'], 4), n(e['pws'], 4)))
    return 0


def cmd_secador(a):
    p = presion(a)
    r = secador(a.producto, a.hi, a.hf, a.tamb, a.hramb, a.taire, p, hrsal=a.hrsal, tsal=a.tsal,
                lote_horas=a.lote_horas, rend=a.rend, pci=a.pci)
    print(informe_secador(r))
    if a.diagrama:
        with open(a.diagrama, 'w', encoding='utf-8') as f:
            f.write(diagrama_svg(r['estados'], p, titulo='Proceso de secado'))
        print('Diagrama: %s' % a.diagrama)
    return 0


def leer_punto(txt, p, nombre=''):
    partes = [x.strip() for x in txt.split(';')]
    if len(partes) < 2:
        raise ValueError('el punto va como "t;hr;..." (por ejemplo "20;50;1 ambiente")')
    return [float(x.replace(',', '.')) for x in partes[:2]], partes[2:]


def cmd_mezcla(a):
    p = presion(a)
    (ta, hra), resto_a = leer_punto(a.a, p)
    (tb, hrb), resto_b = leer_punto(a.b, p)
    if not resto_a or not resto_b:
        raise ValueError('falta la masa de aire seco de cada corriente: "t;hr;kg"')
    ma, mb = float(resto_a[0].replace(',', '.')), float(resto_b[0].replace(',', '.'))
    ea = estado(ta, p, hr=hra, nombre='A')
    eb = estado(tb, p, hr=hrb, nombre='B')
    em = mezcla(ea, ma, eb, mb, p)
    print(tabla_estados([ea, eb, em]))
    print('W_m = (m_A·W_A + m_B·W_B)/(m_A + m_B) = %s g/kg;  h_m = %s kJ/kg;  t_m = (h_m − 2501·W_m)/(1,006 + 1,86·W_m) = %s °C'
          % (n(1000 * em['w'], 2), n(em['h'], 1), n(em['t'], 1)))
    return 0


def cmd_humedad(a):
    if a.bh is not None:
        if not 0 <= a.bh < 100:
            raise ValueError('la base húmeda va de 0 a menos de 100 %')
        x = a.bh / (100 - a.bh)
        print('Base húmeda %s %% = base seca %s %% (X = w/(1 − w) = %s kg de agua por kg de sólido seco)'
              % (n(a.bh, 2), n(100 * x, 2), n(x, 4)))
    else:
        if a.bs < 0:
            raise ValueError('la base seca no puede ser negativa')
        w = a.bs / (100 + a.bs)
        print('Base seca %s %% = base húmeda %s %% (w = X/(1 + X))' % (n(a.bs, 2), n(100 * w, 2)))
    return 0


def cmd_diagrama(a):
    p = presion(a)
    pts = []
    for txt in a.punto or []:
        (t, hr), resto = leer_punto(txt, p)
        pts.append(estado(t, p, hr=hr, nombre=resto[0] if resto else ''))
    with open(a.salida, 'w', encoding='utf-8') as f:
        f.write(diagrama_svg(pts, p, tmax=a.tmax))
    print('Diagrama: %s' % a.salida)
    return 0


def cerca(x, y, tol):
    return abs(x - y) <= tol


def cmd_demo():
    ok = []
    # 1) presion de saturacion contra tablas de vapor (IAPWS-IF97): 20, 50, 80 y 100 C
    for t, ref in ((20, 2.3393), (50, 12.352), (80, 47.414), (100, 101.42)):
        ok.append(('p_sat(%d °C) = %s kPa (tabla: %s)' % (t, n(p_sat(t), 4), n(ref, 4)), cerca(p_sat(t), ref, ref * 0.001)))
    # 2) aire a 20 C y 50 %, nivel del mar: valores de CoolProp 8.0 (aire humedo real, ASHRAE RP-1485)
    e = estado(20, hr=50)
    ok.append(('W = %s g/kg (CoolProp 7,29; el modelo de gas ideal da hasta 0,7 %% menos)' % n(1000 * e['w'], 3), cerca(1000 * e['w'], 7.29, 7.29 * 0.007)))
    ok.append(('h = %s kJ/kg (CoolProp 38,62)' % n(e['h'], 2), cerca(e['h'], 38.62, 0.1)))
    ok.append(('t rocío = %s °C (CoolProp 9,27)' % n(e['tdp'], 2), cerca(e['tdp'], 9.27, 0.05)))
    ok.append(('t bh = %s °C (CoolProp 13,78)' % n(e['tbh'], 2), cerca(e['tbh'], 13.78, 0.05)))
    ok.append(('v = %s m³/kg (CoolProp 0,8399)' % n(e['v'], 4), cerca(e['v'], 0.8399, 0.0005)))
    # 3) secador del SKILL.md: 100 kg/h de 75 % a 15 %, aire 25 C y 60 %, calentado a 70 C, sale adiabatico al 70 %
    r = secador(100, 75, 15, 25, 60, 70, hrsal=70, rend=0.9)
    e1, e2, e3 = r['estados']
    ok.append(('agua a evaporar %s kg/h (100·0,60/0,85 = 70,59)' % n(r['m_w'], 2), cerca(r['m_w'], 70.588, 0.01)))
    ok.append(('balance de agua cierra', cerca(r['m_a'] * (e3['w'] - e1['w']), r['m_w'], 1e-6)))
    ok.append(('salida adiabática h3 = h2', cerca(e3['h'], e2['h'], 1e-4)))
    ok.append(('energía específica mayor que el calor de vaporización', r['E_esp'] > 2400))
    resumen = 'aire %s kg/h, %s m³/h en el ventilador, calentador %s kW' % (n(r['m_a_h'], 0), n(r['V1'], 0), n(r['P_cal'], 1))
    # 4) mezcla mitad y mitad del aire ambiente con el de salida: W y h promedio, y t de la mezcla contra CoolProp
    em = mezcla(e1, 1.0, e3, 1.0)
    ok.append(('mezcla: W y h promedio, t = %s °C (CoolProp 30,27)' % n(em['t'], 2),
               cerca(em['w'], (e1['w'] + e3['w']) / 2, 1e-12) and cerca(em['h'], (e1['h'] + e3['h']) / 2, 1e-9)
               and cerca(em['t'], 30.27, 0.05)))
    # 5) humedad base humeda / seca y diagrama
    ok.append(('75 % bh = 300 % bs', cerca(0.75 / 0.25, 3.0, 1e-12)))
    d = os.path.join(tempfile.gettempdir(), 'psicrometria_demo.svg')
    with open(d, 'w', encoding='utf-8') as f:
        f.write(diagrama_svg(r['estados'], titulo='Proceso de secado (demo)'))
    ok.append(('diagrama SVG', os.path.getsize(d) > 5000))
    for nombre, bien in ok:
        print('  %s %s' % ('ok ' if bien else 'MAL', nombre))
    print('Secador del ejemplo: %s' % resumen)
    print('Diagrama de prueba: %s' % d)
    todo = all(b for _, b in ok)
    print('DEMO %s' % ('OK' if todo else 'FALLO'))
    return 0 if todo else 1


def construir_parser():
    ap = argparse.ArgumentParser(prog='psicrometria.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    def pres(p):
        p.add_argument('--p', type=float, help='presión en kPa (101,325 por defecto)')
        p.add_argument('--altitud', type=float, help='altitud en m (calcula la presión)')
    p = sp.add_parser('aire')
    p.add_argument('--t', type=float, required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--hr', type=float)
    g.add_argument('--w', type=float, help='g/kg')
    g.add_argument('--tbh', type=float)
    pres(p)
    p = sp.add_parser('secador')
    for nombre in ('producto', 'hi', 'hf', 'tamb', 'hramb', 'taire'):
        p.add_argument('--' + nombre, type=float, required=True)
    p.add_argument('--hrsal', type=float)
    p.add_argument('--tsal', type=float)
    p.add_argument('--lote-horas', type=float)
    p.add_argument('--rend', type=float, default=1.0)
    p.add_argument('--pci', type=float)
    p.add_argument('--diagrama')
    pres(p)
    p = sp.add_parser('mezcla')
    p.add_argument('--a', required=True)
    p.add_argument('--b', required=True)
    pres(p)
    p = sp.add_parser('humedad')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--bh', type=float)
    g.add_argument('--bs', type=float)
    p = sp.add_parser('diagrama')
    p.add_argument('--salida', required=True)
    p.add_argument('--punto', action='append')
    p.add_argument('--tmax', type=float)
    pres(p)
    sp.add_parser('demo')
    return ap


def main(argv=None):
    a = construir_parser().parse_args(argv)
    try:
        if a.cmd == 'demo':
            return cmd_demo()
        return {'aire': cmd_aire, 'secador': cmd_secador, 'humedad': cmd_humedad, 'diagrama': cmd_diagrama,
                'mezcla': cmd_mezcla}[a.cmd](a)
    except ValueError as ex:
        print('psicrometria.py: %s' % ex, file=sys.stderr)
        return 2


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
