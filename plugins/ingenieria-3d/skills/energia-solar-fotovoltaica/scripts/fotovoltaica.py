#!/usr/bin/env python3
"""fotovoltaica.py - sistemas solares fotovoltaicos aislados y conectados a la red (solo biblioteca estandar).

Cada comando imprime formula, reemplazo y resultado con coma decimal, listo para una memoria de calculo.
Los numeros se pueden escribir con punto o con coma decimal (5.5 o 5,5).

  consumo      --carga "nombre;cantidad;P_W;horas[;no]" (una por carga) [--eta-inv 0.95 --p0 15]
               energia diaria, potencia simultanea (';no' = no coincide con las demas) y energia de CC
  paneles      --E Wh/dia --hsp h --P W --gamma %/C --ta C [--noct 45] [--eta-reg 0.95 --eta-bat 0.92] [--serie 2]
               cantidad de modulos con perdidas desglosadas (temperatura de celda NOCT y perdidas de PVWatts)
  temperatura  --voc V --vmp V --beta %/C --gamma %/C --alfa %/C --tmin C --tmax C [--noct 45] [--serie N]
               Voc maxima en frio y Vmp minima en calor
  regulador    MPPT: datos del modulo + --serie --paralelo --vbat --vbat-max --vmax --iscmax --imax [--pnom]
               PWM:  --tipo pwm --vbat --imp --isc --paralelo [--P W]
  baterias     --E Wh/dia --dias N --V V [--tecnologia litio|plomo] [--pd] [--v-modulo V --ah-modulo Ah] [--isc A]
  inversor     --P W [--motor "U;In;Ip/In;P"] [--cont W --pico VA --V V --eta 0.95]
  cable        --I A --L m --U V (--S mm2 | --limite %) [--temp 70]     caida de tension en corriente continua
  fusibles     --isc A --mocpr A --strings N [--voc-max V]                fusibles de string y seccionador
  energia      --P W (--hsp h --pr 0.8 | --gti 12 valores kWh/m2 por mes --temp 12 valores C) [--pvout ...]
  inclinacion  --lat grados --ghi 12 valores --dif 12 valores [--totales] [--beta 30 45] [--fila m --beta-fila]
  demo         reproduce el ejemplo del SKILL.md y verifica cada resultado (sale con 1 si algo no coincide)
"""
import argparse
import math
import re
import sys

# ------------------------------------------------------------------------------------------ datos con fuente
# Modulo del ejemplo: LONGi LR5-72HBD-550M, hoja de datos 20240131V18Beta (cara frontal, STC y NOCT)
MODULO = {'P': 550.0, 'voc': 49.80, 'isc': 13.99, 'vmp': 41.95, 'imp': 13.12, 'beta': -0.265, 'gamma': -0.340,
          'alfa': 0.050, 'noct': 45.0, 'mocpr': 30.0, 'P_noct': 411.1, 'vmp_noct': 39.14}
# Perdidas por defecto de PVWatts v5 (Dobos, NREL/TP-6A20-62641, 2014) sin sombras (3 %) ni disponibilidad (3 %)
PERDIDAS = [('suciedad', 2.0), ('dispersión', 2.0), ('cableado', 2.0), ('conexiones', 0.5),
            ('degradación inicial (LID)', 1.5), ('tolerancia de placa', 1.0)]
# Global Solar Atlas 2 (Banco Mundial/ESMAP, datos Solargis 2.2.68), punto -33,89; -60,57; consulta 16/11/2026.
# Totales mensuales en kWh/m2 (GHI, DIF, GTI a 30 grados), kWh/kWp (PVOUT) y temperatura media en C.
GSA = {
    'ghi': [224.71875, 179.1640625, 160.1796875, 114.03125, 88.1015625, 71.4609375, 80.90625, 109.6171875,
            139.6796875, 177.9375, 206.0078125, 230.953125],
    'dif': [66.9609375, 57.234375, 52.640625, 38.1015625, 32.765625, 26.671875, 29.484375, 39.5234375,
            47.8203125, 59.640625, 61.6796875, 68.4765625],
    'gti': [210.0234375, 182.296875, 184.5703125, 150.4765625, 130.140625, 112.53125, 124.03125, 151.0625,
            168.296875, 188.7890625, 196.953125, 210.1484375],
    'temp': [24.375, 22.9375, 21.0625, 17.4375, 13.875, 10.875, 10.1875, 12.0625, 14.4375, 17.4375, 20.6875, 23.25],
    'pvout': [162.8740234375, 143.14276123046875, 147.43603515625, 123.719970703125, 110.14300537109375,
              97.20001220703125, 106.91900634765625, 127.1309814453125, 137.97003173828125, 151.55902099609375,
              155.010009765625, 163.4320068359375],
    'opta': 30}
MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
DIAS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
DIA_MEDIO = [17, 47, 75, 105, 135, 162, 198, 228, 258, 288, 318, 344]   # dia medio de cada mes (Klein, 1977)
RHO20, ALFA20 = 0.017241, 0.00393      # cobre recocido a 20 C (IEC 60028) y coeficiente de temperatura 1/C
SECCIONES = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240]   # mm2, serie IEC 60228
# Ciclos hasta 80 % de la capacidad (Victron: Lithium Battery Smart; GEL and AGM batteries), por profundidad de descarga
CICLOS = {'litio': [(0.8, 2500), (0.7, 3000), (0.5, 5000)],
          'agm': [(0.8, 400), (0.5, 600), (0.3, 1500)], 'gel': [(0.8, 500), (0.5, 750), (0.3, 1800)]}


def num(s):
    """float que acepta coma decimal."""
    try:
        return float(str(s).strip().replace(',', '.'))
    except ValueError:
        raise argparse.ArgumentTypeError('no es un número: %r' % s)


def n(x, d=2):
    return ('%.*f' % (d, x)).replace('.', ',')


def miles(x, d=0):
    s = '%.*f' % (d, x)
    ent, _, dec = s.partition('.')
    signo = '-' if ent.startswith('-') else ''
    ent = ent.lstrip('-')
    grupos = []
    while len(ent) > 3:
        grupos.insert(0, ent[-3:])
        ent = ent[:-3]
    grupos.insert(0, ent)
    return signo + ' '.join(grupos) + (',' + dec if dec else '')


def pct(x, d=1):
    return n(100 * x, d) + ' %'


def factor_perdidas(perdidas):
    f = 1.0
    for _, p in perdidas:
        f *= 1 - p / 100
    return f


def t_celda(ta, noct, G=1000.0):
    """Temperatura de celda con la NOCT: Tc = Ta + (NOCT - 20)·G/800 (G en W/m2)."""
    return ta + (noct - 20) * G / 800


# ------------------------------------------------------------------------------------------ consumo
def leer_carga(s):
    partes = [p.strip() for p in s.split(';')]
    if len(partes) not in (4, 5):
        raise ValueError('carga «%s»: hace falta "nombre;cantidad;P_W;horas[;no]"' % s)
    sim = not (len(partes) == 5 and partes[4].lower() in ('no', 'n'))
    return partes[0], num(partes[1]), num(partes[2]), num(partes[3]), sim


def consumo(cargas, eta_inv=None, p0=0.0, horas_p0=24.0):
    if not cargas:
        raise ValueError('indicá al menos una --carga')
    E = sum(c * P * h for _, c, P, h, _s in cargas)
    Ps = sum(c * P for _, c, P, h, s in cargas if s)
    L = ['Tabla de cargas: E = n·P·h']
    for nom, c, P, h, s in cargas:
        L.append('  %s: %s × %s W × %s h = %s Wh/día%s' % (nom, n(c, 0), n(P, 0), n(h, 1), miles(c * P * h),
                                                             '' if s else ' (no coincide con las demás)'))
    L.append('Energía diaria en alterna: E_CA = Σ n·P·h = %s Wh/día' % miles(E))
    L.append('Potencia simultánea: P_sim = Σ n·P de las cargas que pueden coincidir = %s W' % miles(Ps))
    r = {'E': E, 'Psim': Ps}
    if eta_inv:
        r['Ecc'] = E / eta_inv + p0 * horas_p0
        L.append('Energía de CC que sale de la batería: E_CC = E_CA/η_inv + P0·t = %s/%s + %s W·%s h = %s Wh/día'
                 % (miles(E), n(eta_inv, 2), n(p0, 0), n(horas_p0, 0), miles(r['Ecc'], 1)))
    return r, L


# ------------------------------------------------------------------------------------------ paneles
def paneles(E, hsp, P, gamma, ta, noct=45.0, G=1000.0, perdidas=None, eta_reg=0.95, eta_bat=0.92, serie=1):
    perdidas = PERDIDAS if perdidas is None else perdidas
    Tc = t_celda(ta, noct, G)
    fT = 1 + gamma / 100 * (Tc - 25)
    fp = factor_perdidas(perdidas)
    Emod = P * hsp * fT * fp
    Efv = E / (eta_reg * eta_bat)
    N = Efv / Emod
    Nad = serie * math.ceil(N / serie - 1e-9)
    disp = Nad * Emod * eta_reg * eta_bat
    L = ['Temperatura de celda: Tc = Ta + (NOCT − 20)·G/800 = %s + (%s − 20)·%s/800 = %s °C'
         % (n(ta, 2), n(noct, 0), n(G, 0), n(Tc, 2)),
         'Factor de temperatura: fT = 1 + γ·(Tc − 25) = 1 + (%s %%/°C)·(%s) = %s' % (n(gamma, 3), n(Tc - 25, 2), n(fT, 4)),
         'Otras pérdidas: fp = Π(1 − p) = ' + ' · '.join('(1 − %s)' % n(p / 100, 3) for _, p in perdidas)
         + ' = %s (%s)' % (n(fp, 4), ', '.join(nom for nom, _ in perdidas)),
         'Energía por módulo: E_mód = P·HSP·fT·fp = %s W·%s h·%s·%s = %s Wh/día'
         % (n(P, 0), n(hsp, 3), n(fT, 4), n(fp, 4), miles(Emod, 1)),
         'Energía que tienen que entregar los módulos: E_FV = E/(η_reg·η_bat) = %s/(%s·%s) = %s Wh/día'
         % (miles(E, 1), n(eta_reg, 2), n(eta_bat, 2), miles(Efv, 1)),
         'Cantidad: N = E_FV/E_mód = %s → %d módulos%s (%s W pico)'
         % (n(N, 3), Nad, (' (múltiplo de %d en serie)' % serie) if serie > 1 else '', miles(Nad * P)),
         'Con %d módulos quedan %s Wh/día de CC para %s Wh/día de consumo: margen %s'
         % (Nad, miles(disp, 1), miles(E, 1), pct(disp / E - 1))]
    return {'Tc': Tc, 'fT': fT, 'fp': fp, 'Emod': Emod, 'Efv': Efv, 'N': N, 'Nad': Nad, 'disp': disp}, L


# ------------------------------------------------------------------------------------------ temperatura
def temperatura(voc, vmp, beta, gamma, alfa, tmin, tmax, noct=45.0, G=1000.0, serie=1, beta_vmp=None):
    bv = beta_vmp if beta_vmp is not None else gamma - alfa
    voc_max = voc * (1 + beta / 100 * (tmin - 25))
    Tc = t_celda(tmax, noct, G)
    vmp_min = vmp * (1 + bv / 100 * (Tc - 25))
    L = ['Voc máxima (celda a la mínima ambiente, %s °C, con sol de la mañana): Voc·(1 + β·(T − 25)) = %s·(1 + (%s %%/°C)·(%s)) = %s V'
         % (n(tmin, 1), n(voc, 2), n(beta, 3), n(tmin - 25, 1), n(voc_max, 2)),
         'Celda en el día más caluroso: Tc = %s + (%s − 20)·%s/800 = %s °C'
         % (n(tmax, 1), n(noct, 0), n(G, 0), n(Tc, 2)),
         'Coeficiente de Vmp: %s %%/°C %s' % (n(bv, 3), '(dato de la hoja)' if beta_vmp is not None
                                              else '(sin dato en la hoja: γ − α, de P = V·I; queda del lado seguro)'),
         'Vmp mínima: Vmp·(1 + βVmp·(Tc − 25)) = %s·(1 + (%s %%/°C)·(%s)) = %s V' % (n(vmp, 2), n(bv, 3), n(Tc - 25, 2), n(vmp_min, 2))]
    r = {'voc_max': voc_max, 'vmp_min': vmp_min, 'Tc_cal': Tc, 'bv': bv}
    if serie > 1:
        r.update({'voc_s': serie * voc_max, 'vmp_s': serie * vmp_min})
        L.append('String de %d en serie: Voc máx = %s V; Vmp mín = %s V; Vmp a 25 °C = %s V'
                 % (serie, n(serie * voc_max, 2), n(serie * vmp_min, 2), n(serie * vmp, 2)))
    return r, L


# ------------------------------------------------------------------------------------------ regulador
def regulador_mppt(voc, vmp, isc, beta, gamma, alfa, tmin, tmax, serie, paralelo, vbat, vbat_max, vmax, iscmax, imax,
                   noct=45.0, pnom=None, P=None, margen=5.0, beta_vmp=None):
    t, L = temperatura(voc, vmp, beta, gamma, alfa, tmin, tmax, noct, 1000.0, serie, beta_vmp)
    voc_s, vmp_s = serie * t['voc_max'], serie * t['vmp_min']
    isc_g = paralelo * isc
    ok = []
    ok.append(('Voc máx del string %s V ≤ %s V del regulador' % (n(voc_s, 1), n(vmax, 0)), voc_s <= vmax))
    ok.append(('Vmp mín del string %s V ≥ V_bat máx + %s V = %s V (arranque del MPPT)' % (n(vmp_s, 1), n(margen, 0), n(vbat_max + margen, 1)),
               vmp_s >= vbat_max + margen))
    ok.append(('Isc del generador ×1,25 = %s·%s·1,25 = %s A ≤ %s A' % (n(paralelo, 0), n(isc, 2), n(1.25 * isc_g, 2), n(iscmax, 0)),
               1.25 * isc_g <= iscmax))
    r = {'voc_s': voc_s, 'vmp_s': vmp_s, 'isc_125': 1.25 * isc_g,
         'n_max': math.floor(vmax / t['voc_max'] + 1e-9), 'n_min': math.ceil((vbat_max + margen) / t['vmp_min'] - 1e-9)}
    if P:
        Pfv = P * serie * paralelo
        Ic = Pfv / vbat
        r.update({'Pfv': Pfv, 'Ic': Ic})
        ok.append(('Corriente de carga P_FV/V_bat = %s/%s = %s A ≤ %s A' % (miles(Pfv), n(vbat, 1), n(Ic, 2), n(imax, 0)), Ic <= imax))
        if pnom:
            ok.append(('P_FV %s W ≤ %s W (potencia FV nominal del regulador a esa tensión)' % (miles(Pfv), miles(pnom)), Pfv <= pnom))
    L.append('Módulos en serie posibles: de %d (Vmp en calor) a %d (Voc en frío)' % (r['n_min'], r['n_max']))
    for txt, b in ok:
        L.append('%s: %s' % ('Verifica' if b else 'NO VERIFICA', txt))
    r['ok'] = all(b for _, b in ok)
    return r, L


def regulador_pwm(vbat, imp, isc, paralelo, P=None):
    Pu = vbat * imp * paralelo
    I = 1.25 * isc * paralelo
    L = ['PWM: el regulador conecta el generador a la batería y la tensión de los módulos baja a la de la batería',
         'Potencia aprovechada: P ≈ V_bat·Imp·Np = %s·%s·%s = %s W' % (n(vbat, 1), n(imp, 2), n(paralelo, 0), n(Pu, 1)),
         'Corriente del regulador: I ≥ 1,25·Isc·Np = 1,25·%s·%s = %s A' % (n(isc, 2), n(paralelo, 0), n(I, 2))]
    r = {'Pu': Pu, 'I': I}
    if P:
        r['frac'] = Pu / (P * paralelo)
        L.append('Se aprovecha el %s de los %s W pico: con módulos de tensión alta conviene un MPPT' % (pct(r['frac'], 0), miles(P * paralelo)))
    return r, L


# ------------------------------------------------------------------------------------------ baterias
def ciclos(tecno, pd):
    tabla = CICLOS.get(tecno)
    if not tabla:
        return None
    for p, c in sorted(tabla, reverse=True):
        if pd >= p - 1e-9:
            return p, c
    return tabla[-1]


def baterias(E, dias, V, tecnologia='litio', pd=None, v_mod=None, ah_mod=None, isc=None):
    if tecnologia not in ('litio', 'plomo'):
        raise ValueError('tecnología: litio o plomo')
    pd = pd if pd else (0.8 if tecnologia == 'litio' else 0.5)
    Cwh = E * dias / pd
    Cah = Cwh / V
    L = ['Capacidad útil necesaria: C = E_CC·N/PD = %s Wh/día·%s días/%s = %s Wh' % (miles(E, 1), n(dias, 0), n(pd, 2), miles(Cwh)),
         'En amperhora a %s V: C = %s/%s = %s Ah' % (n(V, 1), miles(Cwh), n(V, 1), n(Cah, 1))]
    r = {'Cwh': Cwh, 'Cah': Cah, 'pd': pd}
    if v_mod and ah_mod:
        ns = V / v_mod
        if abs(ns - round(ns)) > 1e-6:
            raise ValueError('la tensión del sistema no es múltiplo de la del módulo')
        ns = int(round(ns))
        np_ = math.ceil(Cah / ah_mod - 1e-9)
        Cad = np_ * ah_mod * V
        r.update({'ns': ns, 'np': np_, 'Cad': Cad, 'aut': Cad * pd / E})
        L.append('Banco: %d en serie (%s V/%s V) × %d en paralelo (%s Ah/%s Ah) = %s Wh nominales → autonomía real %s días'
                 % (ns, n(V, 1), n(v_mod, 1), np_, n(Cah, 1), n(ah_mod, 0), miles(Cad), n(r['aut'], 2)))
    if tecnologia == 'plomo':
        for t in ('agm', 'gel'):
            p, c = ciclos(t, pd)
            L.append('Vida orientativa %s a PD %s: %s ciclos (Victron)' % (t.upper(), pct(p, 0), miles(c)))
        if isc:
            r['c20_isc'] = Cah / isc
            L.append('%s: C20/Isc = %s/%s = %s (el IDAE pide menos de 25 para que el generador alcance a cargar el plomo)'
                     % ('Verifica' if r['c20_isc'] < 25 else 'NO VERIFICA', n(Cah, 1), n(isc, 2), n(r['c20_isc'], 1)))
    else:
        p, c = ciclos('litio', pd)
        L.append('Vida orientativa LiFePO4 a PD %s: %s ciclos (Victron); no cargar por debajo de 5 °C sin calefacción' % (pct(p, 0), miles(c)))
    return r, L


# ------------------------------------------------------------------------------------------ inversor
def inversor(P, motor=None, cont=None, pico=None, V=None, eta=0.95, p_cc=None):
    L = ['Potencia continua necesaria: la simultánea, P_sim = %s W (comparar con la del inversor a la temperatura del local)' % miles(P)]
    r = {'P': P, 'S_pico': P}
    if motor:
        U, In, k, Pm = motor
        Sa = U * k * In
        r['S_arr'] = Sa
        r['S_pico'] = (P - Pm) + Sa
        L.append('Arranque del motor: S_a = U·(Ip/In)·In = %s V·%s·%s A = %s VA' % (n(U, 0), n(k, 1), n(In, 2), miles(Sa)))
        L.append('Pico: resto de las cargas en marcha + arranque = (%s − %s) + %s = %s VA (se suman como aparentes, del lado seguro)'
                 % (miles(P), miles(Pm), miles(Sa), miles(r['S_pico'])))
    ok = []
    if cont:
        ok.append(('potencia continua %s W ≥ %s W' % (miles(cont), miles(P)), cont >= P))
    if pico:
        ok.append(('potencia pico %s VA ≥ %s VA' % (miles(pico), miles(r['S_pico'])), pico >= r['S_pico']))
    for txt, b in ok:
        L.append('%s: %s' % ('Verifica' if b else 'NO VERIFICA', txt))
    r['ok'] = all(b for _, b in ok) if ok else None
    pcc = p_cc or cont
    if pcc and V:
        r['Icc'] = pcc / (eta * V)
        L.append('Corriente de CC a la potencia continua máxima del inversor: I = P/(η·V) = %s/(%s·%s) = %s A (cable y fusible de batería)'
                 % (miles(pcc), n(eta, 2), n(V, 1), n(r['Icc'], 2)))
    return r, L


# ------------------------------------------------------------------------------------------ cable
def cable(I, L_, U, S=None, limite=None, temp=70.0):
    rho = RHO20 * (1 + ALFA20 * (temp - 20))
    L = ['Resistividad del cobre a %s °C: ρ = 0,017241·(1 + 0,00393·%s) = %s Ω·mm²/m' % (n(temp, 0), n(temp - 20, 0), n(rho, 5))]
    r = {'rho': rho}
    if S is None:
        if not limite:
            raise ValueError('indicá --S (sección) o --limite (caída máxima en %)')
        du_max = limite / 100 * U
        Smin = 2 * I * L_ * rho / du_max
        S = next((s for s in SECCIONES if s >= Smin - 1e-9), None)
        if S is None:
            raise ValueError('hace falta más de 240 mm²: subir la tensión del sistema o acortar el tramo')
        r['Smin'] = Smin
        L.append('Sección mínima por caída (%s %% de %s V = %s V): S = 2·I·L·ρ/ΔU = 2·%s A·%s m·%s/%s V = %s mm² → %s mm²'
                 % (n(limite, 1), n(U, 1), n(du_max, 3), n(I, 2), n(L_, 1), n(rho, 5), n(du_max, 3), n(Smin, 2), n(S, 1).replace(',0', '')))
    du = 2 * I * L_ * rho / S
    r.update({'S': S, 'du': du, 'pct': 100 * du / U})
    L.append('Caída: ΔU = 2·I·L·ρ/S = %s V → %s %% de %s V' % (n(du, 3), n(r['pct'], 2), n(U, 1)))
    if limite:
        L.append('%s: %s %% %s %s %%' % ('Verifica' if r['pct'] <= limite + 1e-9 else 'NO VERIFICA', n(r['pct'], 2),
                                         '≤' if r['pct'] <= limite + 1e-9 else '>', n(limite, 1)))
    L.append('Falta verificar la corriente admisible del cable (Ib ≤ In ≤ Iz) con la forma de instalación: ver instalaciones-electricas.')
    return r, L


# ------------------------------------------------------------------------------------------ fusibles
def fusibles(isc, mocpr, strings, voc_max=None):
    req = 1.35 * mocpr < (strings - 1) * isc
    lo, hi = 1.5 * isc, min(2.4 * isc, mocpr)
    L = ['Fusible de string necesario si 1,35·I_fus,máx < (Ns − 1)·Isc: 1,35·%s = %s A %s (%d − 1)·%s = %s A → %s'
         % (n(mocpr, 0), n(1.35 * mocpr, 2), '<' if req else '≥', strings, n(isc, 2), n((strings - 1) * isc, 2),
            'hace falta un fusible para fotovoltaica en cada string (polo + y −)' if req else 'no hace falta fusible de string')]
    if req:
        L.append('Corriente del fusible: 1,5·Isc < In ≤ mín(2,4·Isc; I_fus,máx del módulo) → %s A < In ≤ %s A' % (n(lo, 1), n(hi, 1)))
        if lo >= hi:
            L.append('AVISO: no hay valor posible: consultar al fabricante del módulo.')
    isc_g = 1.25 * strings * isc
    L.append('Seccionador de CC del generador: corriente ≥ 1,25·Ns·Isc = %s A%s, apto para corriente continua'
             % (n(isc_g, 2), ('; tensión ≥ Voc máx = %s V' % n(voc_max, 1)) if voc_max else ''))
    return {'req': req, 'In_min': lo, 'In_max': hi, 'I_secc': isc_g}, L


# ------------------------------------------------------------------------------------------ energia
def energia(P, hsp=None, pr=None, gti=None, temp=None, gamma=-0.34, noct=45.0, perdidas=None, eta_inv=0.96, pvout=None):
    kw = P / 1000
    if gti is None:
        if not hsp or not pr:
            raise ValueError('indicá --hsp y --pr, o los 12 valores de --gti y --temp')
        Ed = kw * hsp * pr
        L = ['Energía: E = P·HSP·PR = %s kW·%s h·%s = %s kWh/día → %s kWh/año' % (n(kw, 3), n(hsp, 3), n(pr, 3), n(Ed, 3), miles(Ed * 365))]
        return {'Edia': Ed, 'Eano': Ed * 365}, L
    if temp is None or len(gti) != 12 or len(temp) != 12:
        raise ValueError('--gti y --temp llevan 12 valores (enero a diciembre)')
    perdidas = PERDIDAS if perdidas is None else perdidas
    fp = factor_perdidas(perdidas)
    L = ['Mes a mes: E_m = P·H_m·fT_m·fp·η_inv, fT_m = 1 + γ·(Ta_m + (NOCT − 20)·1000/800 − 25), fp = %s, η_inv = %s' % (n(fp, 4), n(eta_inv, 3))]
    Em = []
    for i in range(12):
        fT = 1 + gamma / 100 * (t_celda(temp[i], noct) - 25)
        e = kw * gti[i] * fT * fp * eta_inv
        Em.append(e)
        L.append('  %s: %s kW·%s kWh/m²·%s·%s·%s = %s kWh' % (MESES[i], n(kw, 3), n(gti[i], 1), n(fT, 4), n(fp, 4), n(eta_inv, 3), n(e, 1)))
    Ea = sum(Em)
    PR = Ea / (kw * sum(gti))
    L.append('Energía anual: %s kWh/año (%s kWh/kWp); PR = E/(P·H) = %s; promedio %s kWh/día'
             % (miles(Ea), miles(Ea / kw), n(PR, 3), n(Ea / 365, 2)))
    r = {'Em': Em, 'Eano': Ea, 'PR': PR, 'esp': Ea / kw}
    if pvout:
        ref = sum(pvout) * kw if len(pvout) == 12 else pvout[0] * kw
        r['dif'] = Ea / ref - 1
        L.append('Contra la referencia (PVOUT %s kWh/año): diferencia %s' % (miles(ref), pct(r['dif'], 2)))
    return r, L


# ------------------------------------------------------------------------------------------ inclinacion
def declinacion(nd):
    return 23.45 * math.sin(math.radians(360 * (284 + nd) / 365))      # Cooper (1969)


def rb_medio(lat, beta, nd):
    """R_b medio mensual, superficie mirando al ecuador (Klein, 1977; Duffie y Beckman, ec. 2.19.3).

    lat negativa en el hemisferio sur: la superficie inclinada beta hacia el norte equivale a una horizontal
    en la latitud lat + beta (en el norte, lat - beta)."""
    d, p = math.radians(declinacion(nd)), math.radians(lat)
    pb = math.radians(lat + beta if lat < 0 else lat - beta)
    ws = math.acos(max(-1.0, min(1.0, -math.tan(p) * math.tan(d))))
    wsp = min(ws, math.acos(max(-1.0, min(1.0, -math.tan(pb) * math.tan(d)))))
    num_ = math.cos(pb) * math.cos(d) * math.sin(wsp) + wsp * math.sin(pb) * math.sin(d)
    den = math.cos(p) * math.cos(d) * math.sin(ws) + ws * math.sin(p) * math.sin(d)
    return max(0.0, num_ / den)


def rb_numerico(lat, beta, nd, pasos=20000):
    """Mismo cociente integrando cos(theta) a lo largo del dia (para verificar la formula cerrada)."""
    d, p = math.radians(declinacion(nd)), math.radians(lat)
    pb = math.radians(lat + beta if lat < 0 else lat - beta)
    st = sh = 0.0
    for i in range(pasos):
        w = -math.pi + (i + 0.5) * 2 * math.pi / pasos
        cz = math.cos(p) * math.cos(d) * math.cos(w) + math.sin(p) * math.sin(d)
        if cz <= 0:
            continue
        sh += cz
        st += max(0.0, math.cos(pb) * math.cos(d) * math.cos(w) + math.sin(pb) * math.sin(d))
    return st / sh


def h_inclinada(H, Hd, lat, beta, nd, albedo=0.2):
    """Modelo isotropico (Liu y Jordan): H_T = (H - Hd)·Rb + Hd·(1 + cos b)/2 + H·rho·(1 - cos b)/2."""
    cb = math.cos(math.radians(beta))
    return (H - Hd) * rb_medio(lat, beta, nd) + Hd * (1 + cb) / 2 + H * albedo * (1 - cb) / 2


def inclinacion(lat, ghi, dif, betas=(30.0, 45.0), totales=False, albedo=0.2, fila=None, beta_fila=None):
    if len(ghi) != 12 or len(dif) != 12:
        raise ValueError('--ghi y --dif llevan 12 valores (enero a diciembre)')
    H = [g / DIAS[i] for i, g in enumerate(ghi)] if totales else list(ghi)
    Hd = [g / DIAS[i] for i, g in enumerate(dif)] if totales else list(dif)

    def serie_hsp(b):
        return [h_inclinada(H[i], Hd[i], lat, b, DIA_MEDIO[i], albedo) for i in range(12)]

    def anual(v):
        return sum(v[i] * DIAS[i] for i in range(12))

    tabla = {b: serie_hsp(b) for b in betas}
    L = ['Modelo isotrópico mes a mes: H_T = (H − Hd)·Rb + Hd·(1 + cos β)/2 + H·ρ·(1 − cos β)/2, ρ = %s, día medio de cada mes' % n(albedo, 2),
         'HSP [h/día] = H_T [kWh/m²·día]/1 kW/m²:',
         '  %-5s %s' % ('β', ' '.join('%6s' % m for m in MESES)) + '   anual [kWh/m²]',
         '  %-5s %s' % ('0°', ' '.join('%6s' % n(x, 2) for x in H)) + '   %s' % miles(anual(H))]
    for b in betas:
        L.append('  %-5s %s' % (n(b, 0) + '°', ' '.join('%6s' % n(x, 2) for x in tabla[b])) + '   %s' % miles(anual(tabla[b])))
    mejor_a = max(range(0, 91), key=lambda b: anual(serie_hsp(b)))
    mejor_i = max(range(0, 91), key=lambda b: min(serie_hsp(b)))
    phi = abs(lat)
    b_inv = round(phi + 10)
    peor_i, peor_idae = min(serie_hsp(mejor_i)), min(serie_hsp(b_inv))
    L += ['Inclinación de máxima energía anual (modelo isotrópico): %d°, con %s kWh/m²·año' % (mejor_a, miles(anual(serie_hsp(mejor_a)))),
          'Peor mes (consumo parejo todo el año): el máximo está en %d° con %s h/día; a %d° (|φ| + 10°, IDAE) da %s h/día (%s menos)'
          % (mejor_i, n(peor_i, 2), b_inv, n(peor_idae, 2), pct(1 - peor_idae / peor_i)),
          'Regla del IDAE (pliego de aisladas, hemisferio norte; acá con los meses cambiados): invierno |φ| + 10° = %s°, verano |φ| − 20° = %s°, anual |φ| − 10° = %s°'
          % (n(phi + 10, 0), n(phi - 20, 0), n(phi - 10, 0)),
          'Orientación: al norte (hemisferio sur). El modelo isotrópico da algo menos que el de Perez de PVGIS o Solargis (queda del lado seguro).']
    r = {'tabla': tabla, 'H': H, 'mejor_anual': mejor_a, 'mejor_invierno': mejor_i}
    if fila and beta_fila is not None:
        ac = 90 - phi - 23.5 - 7
        h = fila * math.sin(math.radians(beta_fila))
        d = h / math.tan(math.radians(ac))
        r['d'] = d
        L.append('Separación entre filas (Manual de GD, ec. 2): h = L·sen β = %s m; αc = 90° − |φ| − 23,5° − 7° = %s°; d = h/tg αc = %s m (paso entre filas d + L·cos β = %s m)'
                 % (n(h, 3), n(ac, 1), n(d, 2), n(d + fila * math.cos(math.radians(beta_fila)), 2)))
    return r, L


# ------------------------------------------------------------------------------------------ demo
CARGAS_EJEMPLO = [('Lámparas LED', 10, 9, 5, True), ('Heladera con freezer', 1, 150, 8, True), ('Televisor LED', 1, 100, 5, True),
                  ('Notebook y cargadores', 2, 60, 4, True), ('Router wifi', 1, 10, 24, True),
                  ('Bomba 0,5 cv (WEG: 2,82 A a 220 V, cos φ 0,90)', 1, 560, 2, True), ('Lavarropas', 1, 500, 1, False)]


def cerca(x, y, tol):
    return abs(x - y) <= tol


def cmd_demo():
    ok = []
    m = MODULO
    # 1. recurso: HSP de junio a 30 grados (Global Solar Atlas)
    hsp = GSA['gti'][5] / 30
    ok.append(('HSP de junio a 30°: %s h (112,53 kWh/m²/30 días, Global Solar Atlas)' % n(hsp, 3), cerca(hsp, 3.751, 5e-4)))
    ghi_jun = GSA['ghi'][5] / 30
    ok.append(('GHI de junio del GSA %s kWh/m²·día contra 2,33 medido en Pergamino (red solarimétrica UNLu): %s'
               % (n(ghi_jun, 2), pct(ghi_jun / 2.33 - 1)), abs(ghi_jun / 2.33 - 1) < 0.05))
    # 2. consumo
    r, _ = consumo(CARGAS_EJEMPLO, 0.95, 15)
    ok.append(('consumo: %s Wh/día en alterna, %s W simultáneos, E_CC = %s Wh/día' % (miles(r['E']), miles(r['Psim']), miles(r['Ecc'], 1)),
               r['E'] == 4490 and r['Psim'] == 1030 and cerca(r['Ecc'], 4490 / 0.95 + 360, 1e-9)))
    Ecc = r['Ecc']
    # 3. temperatura contra la hoja de datos (condiciones NOCT: 800 W/m2, 20 C de aire -> celda a 45 C)
    P_noct = m['P'] * 0.8 * (1 + m['gamma'] / 100 * (t_celda(20, m['noct'], 800) - 25))
    ok.append(('P a NOCT con γ: %s W contra %s W de la hoja (%s)' % (n(P_noct, 1), n(m['P_noct'], 1), pct(P_noct / m['P_noct'] - 1, 2)),
               abs(P_noct / m['P_noct'] - 1) < 0.01))
    vmp_noct = m['vmp'] * (1 + (m['gamma'] - m['alfa']) / 100 * 20)
    ok.append(('Vmp a NOCT con γ − α: %s V ≤ %s V de la hoja (del lado seguro, %s)' % (n(vmp_noct, 2), n(m['vmp_noct'], 2), pct(vmp_noct / m['vmp_noct'] - 1, 2)),
               vmp_noct <= m['vmp_noct'] and abs(vmp_noct / m['vmp_noct'] - 1) < 0.025))
    # 4. paneles
    r, _ = paneles(Ecc, hsp, m['P'], m['gamma'], GSA['temp'][5], m['noct'], serie=2)
    fp = 0.98 ** 3 * 0.995 * 0.985 * 0.99
    Emod = 550 * hsp * (1 - 0.0034 * (10.875 + 31.25 - 25)) * fp
    ok.append(('paneles: E_mód = %s Wh/día, N = %s → %d (2 en serie × 2 en paralelo)' % (miles(r['Emod'], 1), n(r['N'], 2), r['Nad']),
               cerca(r['Emod'], Emod, 1e-6) and cerca(r['N'], Ecc / (0.95 * 0.92) / Emod, 1e-9) and r['Nad'] == 4))
    # 5. regulador MPPT 150/45 (Victron) con 2 en serie y 2 en paralelo; tmin -10 C y tmax 40 C (supuestos del ejemplo)
    reg, _ = regulador_mppt(m['voc'], m['vmp'], m['isc'], m['beta'], m['gamma'], m['alfa'], -10, 40, 2, 2, 51.2, 57.6,
                            150, 45, 45, m['noct'], pnom=2600, P=m['P'])
    ok.append(('regulador: Voc máx %s V ≤ 150 V; Vmp mín %s V ≥ 62,6 V; Isc·1,25 %s A; carga %s A ≤ 45 A'
               % (n(reg['voc_s'], 2), n(reg['vmp_s'], 2), n(reg['isc_125'], 2), n(reg['Ic'], 2)),
               reg['ok'] and cerca(reg['voc_s'], 2 * 49.80 * (1 + 0.00265 * 35), 1e-9)
               and cerca(reg['vmp_s'], 2 * 41.95 * (1 - 0.0039 * 46.25), 1e-9) and reg['n_max'] == 2))
    reg3, _ = regulador_mppt(m['voc'], m['vmp'], m['isc'], m['beta'], m['gamma'], m['alfa'], -10, 40, 3, 1, 51.2, 57.6,
                             150, 45, 45, m['noct'])
    ok.append(('con 3 en serie la Voc en frío (%s V) pasa los 150 V: el script lo rechaza' % n(reg3['voc_s'], 1), not reg3['ok']))
    # 6. baterias
    b, _ = baterias(Ecc, 3, 51.2, 'litio', 0.8, 51.2, 100)
    ok.append(('LiFePO4: %s Wh = %s Ah a 51,2 V → %d × 100 Ah, autonomía %s días' % (miles(b['Cwh']), n(b['Cah'], 1), b['np'], n(b['aut'], 2)),
               cerca(b['Cwh'], Ecc * 3 / 0.8, 1e-9) and b['np'] == 4))
    bp, _ = baterias(Ecc, 3, 48, 'plomo', 0.5, 12, 200, isc=2 * m['isc'])
    ok.append(('plomo-ácido al 50 %%: %s Ah a 48 V; C20/Isc = %s < 25' % (n(bp['Cah'], 1), n(bp['c20_isc'], 1)),
               cerca(bp['Cah'], Ecc * 3 / 0.5 / 48, 1e-9) and bp['c20_isc'] < 25))
    # 7. inversor (Victron Inverter Smart 48 V: 2000 VA -> 1450 W a 40 C y 4000 VA de pico; 3000 VA -> 2200 W y 6000 VA)
    inv2, _ = inversor(1030, (220, 2.82, 6.8, 560), 1450, 4000)
    inv3, _ = inversor(1030, (220, 2.82, 6.8, 560), 2200, 6000, 48, 0.95, p_cc=2400)
    ok.append(('inversor: pico %s VA por el arranque de la bomba: 2000 VA no alcanza, 3000 VA sí; I de CC %s A'
               % (miles(inv3['S_pico']), n(inv3['Icc'], 2)),
               cerca(inv3['S_pico'], 470 + 220 * 6.8 * 2.82, 1e-9) and inv2['ok'] is False and inv3['ok'] is True
               and cerca(inv3['Icc'], 2400 / (0.95 * 48), 1e-9)))
    # 8. cables de CC
    c1, _ = cable(m['imp'], 10, 2 * m['vmp'], limite=1.5)
    c2, _ = cable(inv3['Icc'], 2, 48, limite=1.5)
    rho = 0.017241 * (1 + 0.00393 * 50)
    ok.append(('cable string 10 m: %s mm² → %s mm² (%s %%); batería-inversor 2 m: %s mm² → %s mm² (%s %%)'
               % (n(c1['Smin'], 2), n(c1['S'], 0), n(c1['pct'], 2), n(c2['Smin'], 2), n(c2['S'], 0), n(c2['pct'], 2)),
               cerca(c1['Smin'], 2 * 13.12 * 10 * rho / (0.015 * 83.9), 1e-9) and c1['S'] == 6 and c2['S'] == 10 and c2['pct'] <= 1.5))
    # 9. fusibles: con 2 strings no hacen falta; con 4 si (1,35·30 = 40,5 A < 3·13,99 = 41,97 A)
    f2, _ = fusibles(m['isc'], m['mocpr'], 2, reg['voc_s'])
    f4, _ = fusibles(m['isc'], m['mocpr'], 4)
    ok.append(('fusibles de string: 2 strings no; 4 strings sí, con %s A < In ≤ %s A' % (n(f4['In_min'], 1), n(f4['In_max'], 0)),
               (not f2['req']) and f4['req'] and cerca(f4['In_min'], 1.5 * 13.99, 1e-9) and f4['In_max'] == 30))
    # 10. PWM con un modulo de 550 W en 12 V
    pw, _ = regulador_pwm(13.5, m['imp'], m['isc'], 1, m['P'])
    ok.append(('PWM en 12 V con un módulo de 550 W: %s W (%s)' % (n(pw['Pu'], 1), pct(pw['frac'], 0)), cerca(pw['Pu'], 13.5 * 13.12, 1e-9)))
    # 11. conectado a la red: 6 modulos (3,3 kWp), energia mes a mes contra el PVOUT del GSA
    e, _ = energia(3300, gti=GSA['gti'], temp=GSA['temp'], gamma=m['gamma'], noct=m['noct'], pvout=GSA['pvout'])
    ok.append(('red: 3,3 kWp → %s kWh/año (PR %s), %s del PVOUT del Global Solar Atlas' % (miles(e['Eano']), n(e['PR'], 3), pct(e['dif'], 2)),
               abs(e['dif']) < 0.03))
    e550, _ = energia(550, gti=GSA['gti'], temp=GSA['temp'], gamma=m['gamma'], noct=m['noct'])
    ok.append(('un módulo de 550 W: %s kWh/año (%s kWh/día de promedio)' % (miles(e550['Eano']), n(e550['Eano'] / 365, 2)),
               cerca(e550['Eano'], e['Eano'] / 6, 1e-6)))
    # 12. inclinacion: formula cerrada de Rb contra la integracion numerica, y modelo isotropico contra el GSA
    peor = max(abs(rb_medio(-33.89, b_, DIA_MEDIO[i]) - rb_numerico(-33.89, b_, DIA_MEDIO[i])) for b_ in (30, 45) for i in range(12))
    ok.append(('Rb cerrado contra integración numérica (30° y 45°, 12 meses): diferencia máxima %s' % n(peor, 5), peor < 1e-3))
    inc, _ = inclinacion(-33.89, GSA['ghi'], GSA['dif'], (30, 45), totales=True, fila=1.0, beta_fila=40)
    difs = [inc['tabla'][30][i] * DIAS[i] / GSA['gti'][i] - 1 for i in range(12)]
    ok.append(('isotrópico a 30° contra el GTI del GSA: de %s a %s por mes (sesgo conservador)' % (pct(min(difs)), pct(max(difs))),
               all(-0.06 <= x <= 0.0 for x in difs)))
    gan = inc['tabla'][45][5] / inc['tabla'][30][5] - 1
    ok.append(('junio a 45° contra 30°: %s más (modelo isotrópico)' % pct(gan), 0.05 < gan < 0.15))
    # Manual de GD (2019), ec. 2: CABA (34,6 S), modulo de 1 m a 40 grados -> 1,38 m
    inc_caba, _ = inclinacion(-34.6, GSA['ghi'], GSA['dif'], (30,), totales=True, fila=1.0, beta_fila=40)
    ok.append(('separación entre filas del ejemplo del Manual de GD: %s m (libro: 1,38 m)' % n(inc_caba['d'], 2), cerca(inc_caba['d'], 1.38, 0.01)))
    for nombre, bien in ok:
        print('  %s %s' % ('ok ' if bien else 'MAL', nombre))
    todo = all(b_ for _, b_ in ok)
    print('DEMO %s' % ('OK' if todo else 'FALLO'))
    return 0 if todo else 1


# ------------------------------------------------------------------------------------------ principal
class Parser(argparse.ArgumentParser):
    """ArgumentParser que toma «-0,34» (coma decimal) como número negativo y no como una opción."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._negative_number_matcher = re.compile(r'^-\d+$|^-\d*[.,]\d+$')


def construir_parser():
    ap = Parser(prog='fotovoltaica.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True, metavar='comando')

    p = sp.add_parser('consumo', help='tabla de cargas: Wh/día, potencia simultánea y energía de CC')
    p.add_argument('--carga', action='append', required=True, help='"nombre;cantidad;P_W;horas[;no]"; repetir por carga')
    p.add_argument('--eta-inv', type=num, help='rendimiento del inversor (hoja de datos), por ejemplo 0,95')
    p.add_argument('--p0', type=num, default=0.0, help='consumo en vacío del inversor [W]')
    p.add_argument('--horas-p0', type=num, default=24.0, help='horas por día que el inversor queda encendido')

    p = sp.add_parser('paneles', help='cantidad de módulos con pérdidas desglosadas')
    p.add_argument('--E', type=num, required=True, help='energía de CC que sale de la batería [Wh/día] (salida de consumo)')
    p.add_argument('--hsp', type=num, required=True, help='horas de sol pico del mes de diseño en el plano de los módulos [h]')
    p.add_argument('--P', type=num, required=True, help='potencia pico del módulo [W]')
    p.add_argument('--gamma', type=num, required=True, help='coeficiente de Pmax [%%/°C], negativo')
    p.add_argument('--ta', type=num, required=True, help='temperatura ambiente media del mes de diseño [°C]')
    p.add_argument('--noct', type=num, default=45.0, help='NOCT de la hoja de datos [°C]')
    p.add_argument('--G', type=num, default=1000.0, help='irradiancia para la temperatura de celda [W/m²]')
    p.add_argument('--eta-reg', type=num, default=0.95, help='rendimiento del regulador')
    p.add_argument('--eta-bat', type=num, default=0.92, help='rendimiento de ida y vuelta de la batería')
    p.add_argument('--serie', type=int, default=1, help='módulos por string (redondea a múltiplo)')
    p.add_argument('--perdidas', type=num, nargs='+', help='otras pérdidas en %% (reemplazan a las de PVWatts)')

    p = sp.add_parser('temperatura', help='Voc máxima en frío y Vmp mínima en calor')
    for x, h in (('voc', 'Voc STC [V]'), ('vmp', 'Vmp STC [V]'), ('beta', 'coef. de Voc [%%/°C]'), ('gamma', 'coef. de Pmax [%%/°C]'),
                 ('alfa', 'coef. de Isc [%%/°C]'), ('tmin', 'mínima ambiente del lugar [°C]'), ('tmax', 'máxima ambiente [°C]')):
        p.add_argument('--' + x, type=num, required=True, help=h)
    p.add_argument('--noct', type=num, default=45.0)
    p.add_argument('--serie', type=int, default=1)
    p.add_argument('--beta-vmp', type=num, help='coef. de Vmp si la hoja lo da [%%/°C]')

    p = sp.add_parser('regulador', help='MPPT: ventana de tensión y corrientes; PWM: potencia aprovechada')
    p.add_argument('--tipo', choices=['mppt', 'pwm'], default='mppt')
    for x in ('voc', 'vmp', 'isc', 'imp', 'beta', 'gamma', 'alfa', 'tmin', 'tmax', 'vbat', 'vbat-max', 'vmax', 'iscmax', 'imax', 'pnom', 'P', 'beta-vmp'):
        p.add_argument('--' + x, type=num)
    p.add_argument('--noct', type=num, default=45.0)
    p.add_argument('--serie', type=int, default=1)
    p.add_argument('--paralelo', type=int, default=1)
    p.add_argument('--margen', type=num, default=5.0, help='V_PV mínima sobre la batería para arrancar [V] (Victron: 5 V)')

    p = sp.add_parser('baterias', help='banco de baterías: autonomía, PD y tensión')
    p.add_argument('--E', type=num, required=True, help='energía de CC diaria [Wh/día]')
    p.add_argument('--dias', type=num, required=True, help='días de autonomía')
    p.add_argument('--V', type=num, required=True, help='tensión del sistema [V]: 12, 24, 48 o la nominal del litio (12,8; 25,6; 51,2)')
    p.add_argument('--tecnologia', choices=['litio', 'plomo'], default='litio')
    p.add_argument('--pd', type=num, help='profundidad de descarga (por defecto 0,8 litio y 0,5 plomo)')
    p.add_argument('--v-modulo', type=num, help='tensión de cada batería o módulo [V]')
    p.add_argument('--ah-modulo', type=num, help='capacidad de cada batería o módulo [Ah]')
    p.add_argument('--isc', type=num, help='Isc total del generador [A] (control C20/Isc del plomo)')

    p = sp.add_parser('inversor', help='potencia continua y pico de arranque de motores')
    p.add_argument('--P', type=num, required=True, help='potencia simultánea [W]')
    p.add_argument('--motor', help='"U;In;Ip/In;P": tensión, corriente nominal, relación de arranque y potencia del motor mayor')
    p.add_argument('--cont', type=num, help='potencia continua del inversor a la temperatura del local [W]')
    p.add_argument('--pico', type=num, help='potencia pico del inversor [VA]')
    p.add_argument('--V', type=num, help='tensión de la batería [V] (corriente de CC)')
    p.add_argument('--eta', type=num, default=0.95)
    p.add_argument('--p-cc', type=num, help='potencia continua máxima del inversor a 25 °C [W] para la corriente de CC (si no, --cont)')

    p = sp.add_parser('cable', help='caída de tensión y sección en corriente continua')
    p.add_argument('--I', type=num, required=True)
    p.add_argument('--L', type=num, required=True, help='largo del tramo, ida [m]')
    p.add_argument('--U', type=num, required=True, help='tensión del tramo [V]')
    p.add_argument('--S', type=num, help='sección [mm²] para verificar')
    p.add_argument('--limite', type=num, help='caída máxima [%%] para calcular la sección')
    p.add_argument('--temp', type=num, default=70.0, help='temperatura del conductor [°C]')

    p = sp.add_parser('fusibles', help='fusibles de string y seccionador del generador')
    p.add_argument('--isc', type=num, required=True, help='Isc del módulo [A]')
    p.add_argument('--mocpr', type=num, required=True, help='corriente máxima de fusible en serie del módulo [A] (hoja de datos)')
    p.add_argument('--strings', type=int, required=True)
    p.add_argument('--voc-max', type=num, help='Voc máxima del string en frío [V]')

    p = sp.add_parser('energia', help='energía diaria o anual de un módulo o un sistema')
    p.add_argument('--P', type=num, required=True, help='potencia pico [W]')
    p.add_argument('--hsp', type=num)
    p.add_argument('--pr', type=num)
    p.add_argument('--gti', type=num, nargs=12, help='irradiación mensual en el plano [kWh/m² por mes], enero a diciembre')
    p.add_argument('--temp', type=num, nargs=12, help='temperatura media mensual [°C]')
    p.add_argument('--gamma', type=num, default=-0.34)
    p.add_argument('--noct', type=num, default=45.0)
    p.add_argument('--eta-inv', type=num, default=0.96)
    p.add_argument('--pvout', type=num, nargs='+', help='referencia: 12 valores mensuales o el anual [kWh/kWp]')

    p = sp.add_parser('inclinacion', help='HSP mes a mes según la inclinación y separación entre filas')
    p.add_argument('--lat', type=num, required=True, help='latitud [°], negativa en el hemisferio sur')
    p.add_argument('--ghi', type=num, nargs=12, required=True, help='irradiación global horizontal, enero a diciembre')
    p.add_argument('--dif', type=num, nargs=12, required=True, help='irradiación difusa horizontal, enero a diciembre')
    p.add_argument('--totales', action='store_true', help='los valores son totales del mes (PVGIS, GSA) y no medias diarias')
    p.add_argument('--beta', type=num, nargs='+', default=[30.0, 45.0], help='inclinaciones a comparar [°]')
    p.add_argument('--albedo', type=num, default=0.2)
    p.add_argument('--fila', type=num, help='largo del módulo en la pendiente [m] (separación entre filas)')
    p.add_argument('--beta-fila', type=num, help='inclinación de las filas [°]')

    sp.add_parser('demo', help='reproduce el ejemplo del SKILL.md y verifica los resultados')
    return ap


def main(argv=None):
    a = construir_parser().parse_args(argv)
    try:
        if a.cmd == 'demo':
            return cmd_demo()
        if a.cmd == 'consumo':
            _, L = consumo([leer_carga(c) for c in a.carga], a.eta_inv, a.p0, a.horas_p0)
        elif a.cmd == 'paneles':
            perd = None if a.perdidas is None else [('pérdida %d' % (i + 1), p) for i, p in enumerate(a.perdidas)]
            _, L = paneles(a.E, a.hsp, a.P, a.gamma, a.ta, a.noct, a.G, perd, a.eta_reg, a.eta_bat, a.serie)
        elif a.cmd == 'temperatura':
            _, L = temperatura(a.voc, a.vmp, a.beta, a.gamma, a.alfa, a.tmin, a.tmax, a.noct, 1000.0, a.serie, a.beta_vmp)
        elif a.cmd == 'regulador':
            if a.tipo == 'pwm':
                if None in (a.vbat, a.imp, a.isc):
                    raise ValueError('PWM: indicá --vbat, --imp e --isc')
                _, L = regulador_pwm(a.vbat, a.imp, a.isc, a.paralelo, a.P)
            else:
                falta = [x for x in ('voc', 'vmp', 'isc', 'beta', 'gamma', 'alfa', 'tmin', 'tmax', 'vbat', 'vbat_max', 'vmax', 'iscmax', 'imax')
                         if getattr(a, x) is None]
                if falta:
                    raise ValueError('MPPT: faltan --%s' % ', --'.join(f.replace('_', '-') for f in falta))
                _, L = regulador_mppt(a.voc, a.vmp, a.isc, a.beta, a.gamma, a.alfa, a.tmin, a.tmax, a.serie, a.paralelo, a.vbat,
                                      a.vbat_max, a.vmax, a.iscmax, a.imax, a.noct, a.pnom, a.P, a.margen, a.beta_vmp)
        elif a.cmd == 'baterias':
            _, L = baterias(a.E, a.dias, a.V, a.tecnologia, a.pd, a.v_modulo, a.ah_modulo, a.isc)
        elif a.cmd == 'inversor':
            motor = None
            if a.motor:
                partes = [num(x) for x in a.motor.split(';')]
                if len(partes) != 4:
                    raise ValueError('--motor lleva "U;In;Ip/In;P"')
                motor = tuple(partes)
            _, L = inversor(a.P, motor, a.cont, a.pico, a.V, a.eta, a.p_cc)
        elif a.cmd == 'cable':
            _, L = cable(a.I, a.L, a.U, a.S, a.limite, a.temp)
        elif a.cmd == 'fusibles':
            _, L = fusibles(a.isc, a.mocpr, a.strings, a.voc_max)
        elif a.cmd == 'energia':
            _, L = energia(a.P, a.hsp, a.pr, a.gti, a.temp, a.gamma, a.noct, None, a.eta_inv, a.pvout)
        else:
            _, L = inclinacion(a.lat, a.ghi, a.dif, tuple(a.beta), a.totales, a.albedo, a.fila, a.beta_fila)
    except (ValueError, argparse.ArgumentTypeError) as ex:
        print('fotovoltaica.py: %s' % ex, file=sys.stderr)
        return 2
    print('\n'.join(L))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
