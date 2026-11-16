#!/usr/bin/env python3
"""calor.py - transferencia de calor para equipos y procesos (solo biblioteca estandar).

Paredes planas y cilindricas multicapa, conveccion natural y forzada, radiacion, coeficiente global,
intercambiadores (LMTD con F y e-NTU), aletas y espesor de aislacion. Cada comando imprime las formulas,
los valores usados y el resultado con coma decimal, listo para una memoria de calculo.

Comandos:
  propiedades --fluido aire|agua --t C               propiedades interpoladas de la tabla
  materiales                                         conductividades cargadas y su fuente
  conveccion --caso CASO --ts C --tinf C ...         coeficiente h de una superficie (ver --help del comando)
  radiacion --ts C --tsur C --eps E [--area m2]      intercambio con alrededores grandes y h lineal
  pared --ti C --te C --capa MATERIAL:mm[:k] ...     pared plana multicapa entre dos fluidos (itera las T)
  cilindro --ti C --te C --d mm --capa ... [--largo m]   cano o tanque cilindrico con aislacion
  aislacion (opciones de pared, o de cilindro con --d) --tmax C | --qmax W/m2 (W/m en cilindro)
  intercambiador --tipo contracorriente|paralelo|carcasa ...   LMTD con F, o e-NTU
  aleta --tipo recta|aguja --k --h --L mm (--t mm | --d mm) [--tb C --tinf C]
  demo                                               reproduce el ejemplo del SKILL.md y los ejemplos publicados
Capas: MATERIAL:espesor_mm usa la k de la lista (ver "materiales"); MATERIAL:mm:k fija k en W/(m K);
       MATERIAL:mm:T1=k1/T2=k2/... da k segun la temperatura media de la capa (tabla del fabricante).
Unidades: temperaturas en C, longitudes en m salvo espesores y diametros en mm, h en W/(m2 K), q en W/m2 o W/m.
"""
import argparse
import bisect
import math
import sys

G = 9.81                     # m/s2, como en los ejemplos de Cengel
K0 = 273.15
_KB, _H, _C = 1.380649e-23, 6.62607015e-34, 299792458.0          # constantes exactas del SI (2019)
SIGMA = 2 * math.pi ** 5 * _KB ** 4 / (15 * _H ** 3 * _C ** 2)  # Stefan-Boltzmann: 5,670374419e-8 W/(m2 K4)

# Aire a 1 atm. Cengel: tabla A-15 de "Transferencia de calor y masa" (Cengel y Ghajar) y A-9 de "Mecanica de
# fluidos" (Cengel y Cimbala); datos generados con EES (Klein y Alvarado).
# T [C], rho [kg/m3], cp [J/(kg K)], k [W/(m K)], mu [kg/(m s)], nu [m2/s], Pr
AIRE = (
    (-20, 1.394, 1005, 0.02211, 1.630e-5, 1.169e-5, 0.7408),
    (-10, 1.341, 1006, 0.02288, 1.680e-5, 1.252e-5, 0.7387),
    (0, 1.292, 1006, 0.02364, 1.729e-5, 1.338e-5, 0.7362),
    (10, 1.246, 1006, 0.02439, 1.778e-5, 1.426e-5, 0.7336),
    (20, 1.204, 1007, 0.02514, 1.825e-5, 1.516e-5, 0.7309),
    (30, 1.164, 1007, 0.02588, 1.872e-5, 1.608e-5, 0.7282),
    (40, 1.127, 1007, 0.02662, 1.918e-5, 1.702e-5, 0.7255),
    (50, 1.092, 1007, 0.02735, 1.963e-5, 1.798e-5, 0.7228),
    (60, 1.059, 1007, 0.02808, 2.008e-5, 1.896e-5, 0.7202),
    (70, 1.028, 1007, 0.02881, 2.052e-5, 1.995e-5, 0.7177),
    (80, 0.9994, 1008, 0.02953, 2.096e-5, 2.097e-5, 0.7154),
    (90, 0.9718, 1008, 0.03024, 2.139e-5, 2.201e-5, 0.7132),
    (100, 0.9458, 1009, 0.03095, 2.181e-5, 2.306e-5, 0.7111),
    (120, 0.8977, 1011, 0.03235, 2.264e-5, 2.522e-5, 0.7073),
    (140, 0.8542, 1013, 0.03374, 2.345e-5, 2.745e-5, 0.7041),
    (160, 0.8148, 1016, 0.03511, 2.420e-5, 2.975e-5, 0.7014),
    (180, 0.7788, 1019, 0.03646, 2.504e-5, 3.212e-5, 0.6992),
    (200, 0.7459, 1023, 0.03779, 2.577e-5, 3.455e-5, 0.6974),
    (250, 0.6746, 1033, 0.04104, 2.760e-5, 4.091e-5, 0.6946),
    (300, 0.6158, 1044, 0.04418, 2.934e-5, 4.765e-5, 0.6935),
    (350, 0.5664, 1056, 0.04721, 3.101e-5, 5.475e-5, 0.6937),
    (400, 0.5243, 1069, 0.05015, 3.261e-5, 6.219e-5, 0.6948),
    (450, 0.4880, 1081, 0.05298, 3.415e-5, 6.997e-5, 0.6965),
    (500, 0.4565, 1093, 0.05572, 3.563e-5, 7.806e-5, 0.6986),
    (600, 0.4042, 1115, 0.06093, 3.846e-5, 9.515e-5, 0.7037),
)

# Agua liquida saturada. NIST Chemistry WebBook, SRD 69 (IAPWS-95; viscosidad IAPWS 2008; conductividad IAPWS 2011).
# beta: IAPWS-95 calculado con CoolProp 8.0.  T [C], rho [kg/m3], cp [J/(kg K)], mu [Pa s], k [W/(m K)], beta [1/K]
AGUA = (
    (5, 999.92, 4205.5, 1.5183e-3, 0.56772, 1.574e-5),
    (10, 999.65, 4195.5, 1.3060e-3, 0.57871, 8.769e-5),
    (15, 999.06, 4188.8, 1.1376e-3, 0.58874, 1.507e-4),
    (20, 998.16, 4184.4, 1.0016e-3, 0.59795, 2.067e-4),
    (25, 997.00, 4181.6, 8.9004e-4, 0.60646, 2.572e-4),
    (30, 995.61, 4180.1, 7.9722e-4, 0.61434, 3.033e-4),
    (35, 993.99, 4179.5, 7.1912e-4, 0.62165, 3.458e-4),
    (40, 992.18, 4179.6, 6.5272e-4, 0.62844, 3.855e-4),
    (45, 990.17, 4180.4, 5.9575e-4, 0.63474, 4.226e-4),
    (50, 988.00, 4181.5, 5.4650e-4, 0.64057, 4.578e-4),
    (55, 985.66, 4183.1, 5.0361e-4, 0.64598, 4.912e-4),
    (60, 983.16, 4185.1, 4.6602e-4, 0.65096, 5.233e-4),
    (65, 980.52, 4187.5, 4.3288e-4, 0.65554, 5.541e-4),
    (70, 977.73, 4190.2, 4.0353e-4, 0.65972, 5.840e-4),
    (75, 974.81, 4193.3, 3.7740e-4, 0.66353, 6.131e-4),
    (80, 971.77, 4196.9, 3.5404e-4, 0.66697, 6.414e-4),
    (85, 968.59, 4200.8, 3.3306e-4, 0.67004, 6.693e-4),
    (90, 965.30, 4205.3, 3.1417e-4, 0.67277, 6.967e-4),
    (95, 961.88, 4210.2, 2.9708e-4, 0.67516, 7.237e-4),
    (100, 958.35, 4215.7, 2.8158e-4, 0.67721, 7.506e-4),
    (110, 950.95, 4228.3, 2.5461e-4, 0.68035, 8.041e-4),
    (120, 943.11, 4243.5, 2.3203e-4, 0.68224, 8.578e-4),
    (130, 934.83, 4261.5, 2.1294e-4, 0.68295, 9.123e-4),
    (140, 926.13, 4282.6, 1.9664e-4, 0.68253, 9.684e-4),
    (150, 917.01, 4307.1, 1.8261e-4, 0.68102, 1.027e-3),
    (160, 907.45, 4335.4, 1.7043e-4, 0.67873, 1.088e-3),
    (170, 897.45, 4367.8, 1.5977e-4, 0.67552, 1.153e-3),
    (180, 887.00, 4405.0, 1.5038e-4, 0.67128, 1.222e-3),
    (190, 876.08, 4447.4, 1.4204e-4, 0.66609, 1.297e-3),
    (200, 864.66, 4495.8, 1.3458e-4, 0.66001, 1.379e-3),
)

FUENTES = {
    'R': 'Municipalidad de Rosario, lista de materiales para el cálculo higrotérmico (valores tipo IRAM 11601)',
    'I': 'Incropera y otros, Fundamentals of Heat and Mass Transfer, 6.ª ed., tablas A.1 y A.3',
    'M': 'Muzychka y Yovanovich, Thermal Spreading and Contact Resistance (2023), tabla C.1',
    'IS': 'ISOVER, ficha técnica TECH Slab 3.0 (EN 12667)',
    'IC': 'ISOVER, ficha técnica CLIMCOVER Lamela Mat (EN 12667 y EN 12939)',
    'RW': 'ROCKWOOL, ficha técnica ProRox PS 960 (EN ISO 8497)',
    'C': 'Çengel, tabla de propiedades del aire a 1 atm (20 °C)',
}
# nombre: (k en W/(m K) o tabla ((T C, k), ...), descripcion, fuente, temperatura maxima de servicio en C o None)
MATERIALES = {
    'acero': (58.0, 'acero', 'R', None),
    'inox': (17.0, 'acero inoxidable', 'R', None),
    'aluminio': (237.0, 'aluminio puro, a 300 K', 'I', None),
    'cobre': (401.0, 'cobre puro, a 300 K', 'M', None),
    'ladrillo': (0.81, 'ladrillo macizo común de 1600 kg/m³', 'R', None),
    'ladrillo1800': (0.91, 'ladrillo macizo común de 1800 kg/m³', 'R', None),
    'ladrillo2000': (1.10, 'ladrillo macizo común de 2000 kg/m³', 'R', None),
    'refractario': (1.0, 'ladrillo de arcilla refractaria, a 478 K', 'I', None),
    'hormigon': (1.63, 'hormigón de piedra de 2400 kg/m³', 'R', None),
    'hormigon-armado': (2.30, 'hormigón armado de 2500 kg/m³', 'R', None),
    'lana-vidrio': (0.040, 'fieltro de lana de vidrio de 15 a 18 kg/m³ (edificios)', 'R', None),
    'lana-vidrio-panel': (((-20, 0.030), (10, 0.034), (50, 0.038), (100, 0.047), (150, 0.058), (200, 0.070),
                           (250, 0.085)), 'panel de lana de vidrio TECH Slab 3.0', 'IS', 300.0),
    'lana-vidrio-manta': (((10, 0.036), (50, 0.044), (100, 0.056), (150, 0.072)),
                          'manta de lana de vidrio CLIMCOVER Lamela Mat', 'IC', None),
    'lana-roca-coquilla': (((50, 0.040), (100, 0.046), (150, 0.054), (200, 0.064), (250, 0.077), (300, 0.092),
                            (350, 0.112)), 'coquilla de lana de roca ProRox PS 960', 'RW', 650.0),
    'lana-mineral': (0.042, 'lana mineral de 30 a 50 kg/m³', 'R', None),
    'pur': (0.027, 'espuma rígida de poliuretano, placas sin protección, 30 a 60 kg/m³', 'R', None),
    'eps': (0.035, 'poliestireno expandido de 20 kg/m³', 'R', None),
    'vidrio-celular': (0.055, 'vidrio celular, a 285 K', 'I', None),
    'aire': (0.02514, 'aire quieto a 20 °C (solo capas muy delgadas, sin convección)', 'C', None),
}


# ------------------------------------------------------------------------------------------ formato
def n(x, d=2):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return '-'
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


_SUP = str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹')


def sci(x, cifras=4):
    """1,867·10⁶ (cifras significativas)."""
    if x == 0:
        return '0'
    e = int(math.floor(math.log10(abs(x))))
    m = x / 10 ** e
    if round(abs(m), cifras - 1) >= 10:
        m, e = m / 10, e + 1
    if -2 <= e <= 4:
        dec = max(0, cifras - 1 - e)
        return miles(x, dec) if abs(x) >= 1e4 else n(x, dec)
    return '%s·10%s' % (n(m, cifras - 1), str(e).translate(_SUP))


def num(txt):
    return float(str(txt).strip().replace(',', '.'))


# ------------------------------------------------------------------------------------------ propiedades
def _fila(tabla, T, nombre):
    ts = [r[0] for r in tabla]
    if not ts[0] - 1e-9 <= T <= ts[-1] + 1e-9:
        raise ValueError('%s: %s °C está fuera de la tabla (%s a %s °C)' % (nombre, n(T, 1), n(ts[0], 0), n(ts[-1], 0)))
    i = min(max(bisect.bisect_right(ts, T) - 1, 0), len(tabla) - 2)
    a, b = tabla[i], tabla[i + 1]
    f = (T - a[0]) / (b[0] - a[0])
    return [a[j] + f * (b[j] - a[j]) for j in range(len(a))]


def props(fluido, T):
    """Propiedades por interpolacion lineal. Aire: beta = 1/T (gas ideal). Agua: liquido saturado."""
    if fluido == 'aire':
        _, rho, cp, k, mu, nu, Pr = _fila(AIRE, T, 'aire')
        beta = 1 / (T + K0)
    elif fluido == 'agua':
        _, rho, cp, mu, k, beta = _fila(AGUA, T, 'agua')
        nu, Pr = mu / rho, mu * cp / k
    else:
        raise ValueError('fluido: aire o agua')
    return {'fluido': fluido, 'T': T, 'rho': rho, 'cp': cp, 'k': k, 'mu': mu, 'nu': nu, 'Pr': Pr,
            'alpha': nu / Pr, 'beta': beta}


# ------------------------------------------------------------------------------------------ correlaciones
def nu_placa_vertical(Ra, Pr):
    """Churchill y Chu, toda la gama de Ra (Incropera ec. 9.26; Cengel ec. 9-21)."""
    return (0.825 + 0.387 * Ra ** (1 / 6) / (1 + (0.492 / Pr) ** (9 / 16)) ** (8 / 27)) ** 2, \
        'placa vertical, Churchill y Chu', []


def nu_cilindro_horizontal(Ra, Pr):
    """Churchill y Chu, Ra_D hasta 10^12 (Incropera ec. 9.34)."""
    av = ['Ra = %s supera 10¹²: fuera del rango de la correlación' % sci(Ra)] if Ra > 1e12 else []
    return (0.60 + 0.387 * Ra ** (1 / 6) / (1 + (0.559 / Pr) ** (9 / 16)) ** (8 / 27)) ** 2, \
        'cilindro horizontal, Churchill y Chu', av


def nu_placa_horizontal(Ra, caliente_arriba, ley=None):
    """Incropera ec. 9.30 a 9.32 (Cengel 9-22 a 9-24); L = area/perimetro.
    caliente_arriba: cara caliente hacia arriba o cara fria hacia abajo. ley: '1/4' o '1/3' fuerza la ley."""
    av = []
    if caliente_arriba:
        if ley == '1/4' or (ley is None and Ra <= 1e7):
            if Ra < 1e4 or Ra > 1e7:
                av.append('Ra = %s fuera de 10⁴ a 10⁷ para 0,54·Ra^¼' % sci(Ra))
            return 0.54 * Ra ** 0.25, 'placa horizontal, cara caliente arriba: Nu = 0,54·Ra^¼', av
        if Ra > 1e11:
            av.append('Ra = %s supera 10¹¹' % sci(Ra))
        return 0.15 * Ra ** (1 / 3), 'placa horizontal, cara caliente arriba: Nu = 0,15·Ra^⅓', av
    if Ra < 1e5 or Ra > 1e10:
        av.append('Ra = %s fuera de 10⁵ a 10¹⁰ (Çengel la extiende a 10¹¹)' % sci(Ra))
    return 0.27 * Ra ** 0.25, 'placa horizontal, cara caliente abajo: Nu = 0,27·Ra^¼', av


def nu_placa_forzada(Re, Pr):
    """Placa plana isoterma, valor medio. Laminar si Re_L <= 5e5; si no, capa mixta con Re_x,c = 5e5 (Incropera cap. 7)."""
    av = []
    if Re <= 5e5:
        if Pr < 0.6:
            av.append('Pr menor que 0,6')
        return 0.664 * Re ** 0.5 * Pr ** (1 / 3), 'placa plana, laminar: Nu = 0,664·Re^½·Pr^⅓', av
    if Re > 1e8 or not 0.6 <= Pr <= 60:
        av.append('fuera de 5·10⁵ ≤ Re ≤ 10⁸ y 0,6 ≤ Pr ≤ 60')
    return (0.037 * Re ** 0.8 - 871) * Pr ** (1 / 3), 'placa plana, capa mixta: Nu = (0,037·Re^0,8 − 871)·Pr^⅓', av


def f_petukhov(Re):
    """Factor de friccion de tubo liso, 3000 <= Re <= 5e6 (Incropera ec. 8.21; Cengel ec. 8-65)."""
    return (0.790 * math.log(Re) - 1.64) ** -2


def nu_gnielinski(Re, Pr):
    """Gnielinski, 3000 <= Re <= 5e6 y 0,5 <= Pr <= 2000 (Incropera ec. 8.62; Cengel ec. 8-71)."""
    f = f_petukhov(Re)
    return (f / 8) * (Re - 1000) * Pr / (1 + 12.7 * (f / 8) ** 0.5 * (Pr ** (2 / 3) - 1))


def nu_dittus_boelter(Re, Pr, calentando=True):
    """Dittus-Boelter, Re >= 10000, 0,7 <= Pr <= 160, L/D >= 10; n = 0,4 calentando y 0,3 enfriando (Incropera 8.60)."""
    return 0.023 * Re ** 0.8 * Pr ** (0.4 if calentando else 0.3)


def nu_tubo(Re, Pr, calentando=True, condicion='ts'):
    av = []
    extra = {}
    if Re < 2300:
        Nu = 3.66 if condicion == 'ts' else 4.36
        av.append('laminar: Nu de flujo desarrollado; en la región de entrada el Nu medio es mayor (Hausen, ver references)')
        return Nu, 'tubo, laminar desarrollado (%s)' % ('T de pared uniforme' if condicion == 'ts' else 'flujo de calor uniforme'), av, extra
    if Re < 3000:
        av.append('Re = %s en la transición (2300 a 3000): resultado orientativo' % sci(Re))
    if not 0.5 <= Pr <= 2000 or Re > 5e6:
        av.append('fuera del rango de Gnielinski (0,5 ≤ Pr ≤ 2000, Re ≤ 5·10⁶)')
    Nu = nu_gnielinski(Re, Pr)
    extra['f'] = f_petukhov(Re)
    if Re >= 1e4:
        extra['Nu_DB'] = nu_dittus_boelter(Re, Pr, calentando)
    return Nu, 'tubo, turbulento: Gnielinski con f de Petukhov', av, extra


def h_rad(eps, Ts, Tsur):
    """h de radiacion linealizado: eps sigma (Ts + Tsur)(Ts^2 + Tsur^2), temperaturas en K (Incropera, cap. 1)."""
    a, b = Ts + K0, Tsur + K0
    return eps * SIGMA * (a + b) * (a * a + b * b)


# ------------------------------------------------------------------------------------------ coeficientes h
def h_natural(caso, Ts, Tinf, L, fluido='aire', ley=None):
    """caso: vertical (L = altura), cilindro (L = diametro), techo o piso (L = area/perimetro)."""
    Tf = (Ts + Tinf) / 2
    p = props(fluido, Tf)
    dT = max(abs(Ts - Tinf), 1e-6)
    if p['beta'] <= 0:
        raise ValueError('beta del agua no positivo a %s °C' % n(Tf, 1))
    Ra = G * p['beta'] * dT * L ** 3 * p['Pr'] / p['nu'] ** 2
    if caso == 'vertical':
        Nu, corr, av = nu_placa_vertical(Ra, p['Pr'])
    elif caso == 'cilindro':
        Nu, corr, av = nu_cilindro_horizontal(Ra, p['Pr'])
    elif caso in ('techo', 'piso'):
        Nu, corr, av = nu_placa_horizontal(Ra, (Ts > Tinf) == (caso == 'techo'), ley)
    else:
        raise ValueError('caso de convección natural: vertical, cilindro, techo o piso')
    return {'h': Nu * p['k'] / L, 'Nu': Nu, 'Ra': Ra, 'Tf': Tf, 'p': p, 'corr': corr, 'avisos': av, 'L': L}


def h_placa_forzada(v, L, Ts, Tinf, fluido='aire'):
    Tf = (Ts + Tinf) / 2
    p = props(fluido, Tf)
    Re = v * L / p['nu']
    Nu, corr, av = nu_placa_forzada(Re, p['Pr'])
    return {'h': Nu * p['k'] / L, 'Nu': Nu, 'Re': Re, 'Tf': Tf, 'p': p, 'corr': corr, 'avisos': av, 'L': L}


def h_tubo(D, Tm, fluido='agua', v=None, m=None, Ts=None, condicion='ts'):
    p = props(fluido, Tm)
    area = math.pi * D ** 2 / 4
    if m is not None:
        v = m / (p['rho'] * area)
    elif v is None:
        raise ValueError('falta la velocidad (--v) o el caudal másico (--m)')
    m = p['rho'] * v * area
    Re = v * D / p['nu']
    calentando = True if Ts is None else Ts > Tm
    Nu, corr, av, extra = nu_tubo(Re, p['Pr'], calentando, condicion)
    r = {'h': Nu * p['k'] / D, 'Nu': Nu, 'Re': Re, 'v': v, 'm': m, 'Tf': Tm, 'p': p, 'corr': corr, 'avisos': av,
         'calentando': calentando, 'L': D}
    r.update(extra)
    if 'Nu_DB' in r:
        r['h_DB'] = r['Nu_DB'] * p['k'] / D
    return r


def texto_h(nombre, r):
    p = r['p']
    if 'Ra' in r:
        base = 'Ra = gβΔT·L³·Pr/ν² = %s' % sci(r['Ra'])
    else:
        base = 'Re = %s' % sci(r['Re'])
    s = '%s: %s; %s, Pr = %s, Nu = %s → h = Nu·k/L = %s·%s/%s = %s W/(m²·K)  [%s a %s °C]' % (
        nombre, r['corr'], base, n(p['Pr'], 4), n(r['Nu'], 2), n(r['Nu'], 2), n(p['k'], 5), n(r['L'], 4),
        n(r['h'], 2), p['fluido'], n(r['Tf'], 1))
    for a in r['avisos']:
        s += '\n   AVISO: ' + a
    return s


# ------------------------------------------------------------------------------------------ capas y materiales
def k_de_tabla(tabla):
    ts = [t for t, _ in tabla]
    ks = [k for _, k in tabla]

    def k(T):
        if T <= ts[0]:
            return ks[0]
        if T >= ts[-1]:
            return ks[-1]
        i = bisect.bisect_right(ts, T) - 1
        return ks[i] + (T - ts[i]) / (ts[i + 1] - ts[i]) * (ks[i + 1] - ks[i])
    return k


def leer_capa(txt):
    """MATERIAL:espesor_mm[:k | :T1=k1/T2=k2...] -> dict de capa."""
    partes = [x.strip() for x in txt.split(':')]
    if len(partes) < 2:
        raise ValueError('capa "%s": se escribe MATERIAL:espesor_mm (por ejemplo acero:1,25 o lana:50:0,04)' % txt)
    nombre, e = partes[0], num(partes[1]) / 1000
    if e < 0:
        raise ValueError('espesor negativo en "%s"' % txt)
    tmax, fuente = None, None
    if len(partes) >= 3 and partes[2]:
        if '=' in partes[2]:
            tabla = []
            for par in partes[2].split('/'):
                t, k = par.split('=')
                tabla.append((num(t), num(k)))
            tabla.sort()
            kdato = tuple(tabla)
        else:
            kdato = num(partes[2])
        desc = nombre
    else:
        if nombre not in MATERIALES:
            raise ValueError('material "%s" desconocido: dar k (MATERIAL:mm:k) o usar uno de: %s'
                             % (nombre, ', '.join(sorted(MATERIALES))))
        kdato, desc, fuente, tmax = MATERIALES[nombre]
    if isinstance(kdato, tuple):
        if any(k <= 0 for _, k in kdato):
            raise ValueError('k tiene que ser positiva')
        kf = k_de_tabla(kdato)
        rango = (kdato[0][0], kdato[-1][0])
    else:
        if kdato <= 0:
            raise ValueError('k tiene que ser positiva')
        kf = (lambda kk: (lambda T: kk))(kdato)
        rango = None
    return {'nombre': nombre, 'desc': desc, 'e': e, 'k': kf, 'rango': rango, 'tmax': tmax, 'fuente': fuente}


# ------------------------------------------------------------------------------------------ solucion de paredes
def resolver(capas, Ti, Te, Tsur, eps, hi_fn, ho_fn, geom='plana', r0=None, puente=None, i_ais=None):
    """Itera las temperaturas de superficie (h y k dependen de ellas).
    hi_fn(Tsi) y ho_fn(Tso, D_ext) devuelven dicts con 'h'; hi_fn None: sin pelicula interior.
    Plana: por m2 (q en W/m2). Cilindro: por m de largo (q en W/m), r0 = radio donde empieza la primera capa."""
    if geom == 'cilindro':
        radios = [r0]
        for c in capas:
            radios.append(radios[-1] + c['e'])
        r_ext = radios[-1]
        a_int, a_ext = 2 * math.pi * r0, 2 * math.pi * r_ext        # m2 por m de largo
    else:
        radios, r_ext, a_int, a_ext = None, None, 1.0, 1.0
    dT = Ti - Te
    if abs(dT) < 1e-9:
        raise ValueError('Ti y Te son iguales: no hay flujo de calor')
    T = [Ti - (0.02 + 0.9 * j / max(len(capas), 1)) * dT for j in range(len(capas) + 1)]
    w = 0.7
    for it in range(1, 801):
        Tsi, Tso = T[0], T[-1]
        ri = hi_fn(Tsi) if hi_fn else None
        ro = ho_fn(Tso, 2 * r_ext if geom == 'cilindro' else None)
        hc = ro['h']
        hr = h_rad(eps, Tso, Tsur) if eps > 0 else 0.0
        R = []
        ks = []
        for j, c in enumerate(capas):
            Tm = (T[j] + T[j + 1]) / 2
            k = c['k'](Tm)
            if puente and j == i_ais:
                k = (1 - puente[0]) * k + puente[0] * puente[1]
            ks.append(k)
            if geom == 'cilindro':
                R.append(math.log(radios[j + 1] / radios[j]) / (2 * math.pi * k))
            else:
                R.append(c['e'] / k)
        Rpi = 1 / (ri['h'] * a_int) if ri else 0.0
        Rin = Rpi + sum(R)
        if Rin <= 1e-15:                 # superficie desnuda sin pelicula interior: queda a la temperatura del fluido
            Tso_n = Ti
            q = a_ext * (hc * (Ti - Te) + hr * (Ti - Tsur))
        else:
            Tso_n = (Ti / Rin + a_ext * (hc * Te + hr * Tsur)) / (1 / Rin + a_ext * (hc + hr))
            q = (Ti - Tso_n) / Rin
        Tn = [Ti - q * Rpi]
        for Rj in R:
            Tn.append(Tn[-1] - q * Rj)
        cambio = max(abs(a - b) for a, b in zip(Tn, T))
        T = [a + w * (b - a) for a, b in zip(T, Tn)]
        if cambio < 1e-9:
            break
    else:
        raise ValueError('el cálculo no converge: revisar los datos')
    q_ext = a_ext * (hc * (Tso_n - Te) + hr * (Tso_n - Tsur))
    return {'q': q, 'T': Tn, 'R': R, 'k': ks, 'Rpi': Rpi, 'hi': ri, 'ho': ro, 'hc': hc, 'hr': hr, 'it': it,
            'geom': geom, 'radios': radios, 'a_ext': a_ext, 'q_ext': q_ext, 'Ti': Ti, 'Te': Te, 'Tsur': Tsur,
            'eps': eps, 'capas': capas, 'puente': puente, 'i_ais': i_ais}


def informe(s, area=None, largo=None):
    L = []
    cil = s['geom'] == 'cilindro'
    uq, uR = ('W/m', 'm·K/W') if cil else ('W/m²', 'm²·K/W')
    L.append('Convergió en %d iteraciones (h y k se recalculan con las temperaturas de cada vuelta).' % s['it'])
    if s['hi']:
        L.append(texto_h('Película interior', s['hi']) if 'corr' in s['hi'] else
                 'Película interior: h = %s W/(m²·K) (dato)' % n(s['hi']['h'], 2))
    else:
        L.append('Sin película interior: la superficie interior está a la temperatura del fluido.')
    L.append(texto_h('Exterior, convección', s['ho']) if 'corr' in s['ho'] else
             'Exterior, convección: h = %s W/(m²·K) (dato)' % n(s['hc'], 2))
    if s['eps'] > 0:
        L.append('Exterior, radiación: hr = εσ(Ts + Tsur)(Ts² + Tsur²) = %s W/(m²·K)  (ε = %s, Ts y Tsur en K)'
                 % (n(s['hr'], 2), n(s['eps'], 2)))
    filas = [('Resistencia', 'R [%s]' % uR, '%', 'T al final [°C]')]
    q = s['q']
    Rtot = (s['Ti'] - s['Te']) / q
    if s['hi']:
        filas.append(('película interior' + (' 1/(hi·2π·r)' if cil else ' 1/hi'), n(s['Rpi'], 4), n(100 * s['Rpi'] / Rtot, 1), n(s['T'][0], 2)))
    for j, c in enumerate(s['capas']):
        kt = 'k = %s' % (n(s['k'][j], 4) if s['k'][j] < 1 else n(s['k'][j], 1))
        if c['rango']:
            kt += ' a %s °C' % n((s['T'][j] + s['T'][j + 1]) / 2, 1)
        if s['puente'] and j == s['i_ais']:
            kt += ' con puente'
        filas.append(('%s %s mm, %s' % (c['nombre'], n(1000 * c['e'], 2 if c['e'] < 0.01 else 1), kt),
                      n(s['R'][j], 4), n(100 * s['R'][j] / Rtot, 1), n(s['T'][j + 1], 2)))
    Rext = (s['T'][-1] - s['Te']) / q
    filas.append(('exterior, convección y radiación', n(Rext, 4), n(100 * Rext / Rtot, 1), n(s['Te'], 2)))
    filas.append(('Total', n(Rtot, 4), '100', ''))
    anchos = [max(len(f[i]) for f in filas) for i in range(4)]
    L.append('| ' + ' | '.join(filas[0][i].ljust(anchos[i]) for i in range(4)) + ' |')
    L.append('|' + '|'.join('-' * (a + 2) for a in anchos) + '|')
    for f in filas[1:]:
        L.append('| ' + ' | '.join(f[i].ljust(anchos[i]) for i in range(4)) + ' |')
    Tso = s['T'][-1]
    if cil:
        U = q / (s['a_ext'] * (s['Ti'] - s['Te']))
        L.append('q\' = (Ti − Te)/R\'total = %s/%s = %s W/m;  U (área exterior, D = %s mm) = %s W/(m²·K)'
                 % (n(s['Ti'] - s['Te'], 1), n(Rtot, 4), n(q, 1), n(2000 * s['radios'][-1], 1), n(U, 3)))
        if largo:
            L.append('Pérdida en %s m: Q = q\'·L = %s W' % (n(largo, 2), miles(q * largo)))
    else:
        L.append('q = (Ti − Te)/R_total = %s/%s = %s W/m²;  U = 1/R_total = %s W/(m²·K)'
                 % (n(s['Ti'] - s['Te'], 1), n(Rtot, 4), n(q, 2), n(1 / Rtot, 3)))
        if area:
            L.append('Pérdida en %s m²: Q = q·A = %s W' % (n(area, 2), miles(q * area)))
    qr = s['a_ext'] * s['hr'] * (Tso - s['Tsur'])
    L.append('Superficie exterior a %s °C; de la pérdida exterior, %s %% es radiación y %s %% convección.'
             % (n(Tso, 2), n(100 * qr / q, 0), n(100 - 100 * qr / q, 0)))
    L.append('Chequeo: hc·(Ts − Te) + hr·(Ts − Tsur) = %s %s, igual a la que atraviesa la pared.' % (n(s['q_ext'], 2), uq))
    for j, c in enumerate(s['capas']):
        Tmax_capa = max(s['T'][j], s['T'][j + 1])
        if c['tmax'] is not None and Tmax_capa > c['tmax']:
            L.append('AVISO: %s llega a %s °C, más que su máximo de servicio (%s °C).' % (c['nombre'], n(Tmax_capa, 0), n(c['tmax'], 0)))
        if c['rango']:
            Tm = (s['T'][j] + s['T'][j + 1]) / 2
            if not c['rango'][0] <= Tm <= c['rango'][1]:
                L.append('AVISO: la temperatura media de %s (%s °C) está fuera de su tabla de k: se usó el extremo.' % (c['nombre'], n(Tm, 0)))
    if cil and s['eps'] >= 0:
        k_ult = s['k'][-1] if s['capas'] else None
        if k_ult:
            rcr = k_ult / (s['hc'] + s['hr'])
            L.append('Radio crítico de la última capa: r_cr = k/h = %s/%s = %s mm (radio exterior %s mm)%s'
                     % (n(k_ult, 4), n(s['hc'] + s['hr'], 2), n(1000 * rcr, 1), n(1000 * s['radios'][-1], 1),
                        ': por debajo, agregar aislación aumenta la pérdida' if s['radios'][-1] < rcr else ''))
    return '\n'.join(L)


# ------------------------------------------------------------------------------------------ armado desde argumentos
def leer_puente(txt):
    if not txt:
        return None
    f, k = [num(x) for x in txt.split(':')]
    if not 0 < f < 1:
        raise ValueError('la fracción del puente térmico va entre 0 y 1')
    return (f, k)


def funcion_hi(a, geom, D_int):
    if a.hi is not None:
        return (lambda h: (lambda Ts: {'h': h}))(a.hi) if a.hi > 0 else None
    if not a.interior:
        return None
    partes = a.interior.split(':')
    tipo = partes[0]
    fl = a.fluido_int
    if tipo == 'forzada':
        v, L = num(partes[1]), num(partes[2])
        return lambda Ts: h_placa_forzada(v, L, Ts, a.ti, fl)
    if tipo == 'vertical':
        H = num(partes[1])
        return lambda Ts: h_natural('vertical', Ts, a.ti, H, fl)
    if tipo == 'tubo':
        if geom != 'cilindro':
            raise ValueError('--interior tubo:V solo en cilindro')
        v = num(partes[1])
        return lambda Ts: h_tubo(D_int, a.ti, fl, v=v, Ts=Ts)
    raise ValueError('--interior: forzada:V:L, vertical:H o tubo:V (en cilindro)')


def funcion_ho(a, geom):
    if a.ho is not None:
        return (lambda h: (lambda Ts, D: {'h': h}))(a.ho)
    ext = a.exterior or ('horizontal' if geom == 'cilindro' else None)
    if not ext:
        raise ValueError('falta el exterior: --exterior vertical:H, techo:L, piso:L, viento:V:L (pared) o --ho')
    partes = ext.split(':')
    tipo = partes[0]
    if tipo == 'horizontal':
        if geom != 'cilindro':
            raise ValueError('--exterior horizontal es para cilindros')
        return lambda Ts, D: h_natural('cilindro', Ts, a.te, D)
    if tipo in ('vertical', 'techo', 'piso'):
        L = num(partes[1])
        return lambda Ts, D: h_natural(tipo, Ts, a.te, L)
    if tipo == 'viento':
        if geom == 'cilindro':
            raise ValueError('viento sobre cilindros: este script no lo trae; dar --ho')
        v, L = num(partes[1]), num(partes[2])
        return lambda Ts, D: h_placa_forzada(v, L, Ts, a.te)
    raise ValueError('--exterior no reconocido: %s' % ext)


def armar(a):
    capas = [leer_capa(c) for c in (a.capa or [])]
    geom = 'cilindro' if getattr(a, 'd', None) else 'plana'
    if not capas and geom == 'plana':
        raise ValueError('falta al menos una capa (--capa MATERIAL:mm)')
    r0 = a.d / 2000 if geom == 'cilindro' else None
    tsur = a.te if a.tsur is None else a.tsur
    hi_fn = funcion_hi(a, geom, a.d / 1000 if geom == 'cilindro' else None)
    ho_fn = funcion_ho(a, geom)
    puente = leer_puente(getattr(a, 'puente', None))
    if not capas:
        i_ais = None
    elif a.aislante:
        i_ais = a.aislante - 1
        if not 0 <= i_ais < len(capas):
            raise ValueError('--aislante va de 1 a %d' % len(capas))
    else:
        i_ais = max(range(len(capas)), key=lambda j: capas[j]['e'] / capas[j]['k'](20.0))
    return capas, geom, r0, tsur, hi_fn, ho_fn, puente, i_ais


def resolver_args(a, capas_mod=None):
    capas, geom, r0, tsur, hi_fn, ho_fn, puente, i_ais = armar(a)
    if capas_mod:
        capas = capas_mod(capas, i_ais)
    return resolver(capas, a.ti, a.te, tsur, a.eps, hi_fn, ho_fn, geom, r0, puente, i_ais)


def espesor_minimo(evaluar, cumple, e_max=1.0, paso=0.005):
    """Menor espesor con el que se cumple el criterio desde ahi en adelante (barrido y biseccion)."""
    ultimo_mal = None
    k = 0
    while k * paso <= e_max + 1e-12:
        if not cumple(*evaluar(k * paso)):
            ultimo_mal = k
        k += 1
    if ultimo_mal is None:
        return 0.0
    if ultimo_mal * paso >= e_max - 1e-12:
        raise ValueError('ni con %s mm de aislación se cumple el criterio' % n(1000 * e_max, 0))
    a_, b_ = ultimo_mal * paso, (ultimo_mal + 1) * paso
    for _ in range(50):
        m = (a_ + b_) / 2
        if cumple(*evaluar(m)):
            b_ = m
        else:
            a_ = m
    return b_


def calcular_aislacion(a):
    capas, geom, r0, tsur, hi_fn, ho_fn, puente, i_ais = armar(a)
    if i_ais is None:
        raise ValueError('falta la capa aislante (--capa MATERIAL:mm)')
    if a.tmax is None and a.qmax is None:
        raise ValueError('falta el criterio: --tmax (temperatura de superficie) o --qmax (pérdida admitida)')
    if a.tmax is not None and a.ti <= a.te:
        raise ValueError('--tmax es para equipos calientes (Ti mayor que Te)')

    def con_espesor(e):
        cs = [dict(c) for c in capas]
        cs[i_ais]['e'] = e
        return cs

    def evaluar(e):
        s = resolver(con_espesor(e), a.ti, a.te, tsur, a.eps, hi_fn, ho_fn, geom, r0, puente, i_ais)
        return s['T'][-1], abs(s['q'])

    def cumple(Ts, q):
        return (a.tmax is None or Ts <= a.tmax + 1e-9) and (a.qmax is None or q <= a.qmax + 1e-9)

    e_min = espesor_minimo(evaluar, cumple)
    s_min = resolver(con_espesor(e_min), a.ti, a.te, tsur, a.eps, hi_fn, ho_fn, geom, r0, puente, i_ais)
    return {'e_min': e_min, 's_min': s_min, 'evaluar': evaluar, 'capa': capas[i_ais], 'geom': geom}


# ------------------------------------------------------------------------------------------ intercambiadores
def dt_ml(dT1, dT2):
    if dT1 <= 0 or dT2 <= 0:
        raise ValueError('diferencias de temperatura en los extremos no positivas (%s y %s K): revisar el tipo de flujo'
                         % (n(dT1, 2), n(dT2, 2)))
    if abs(dT1 - dT2) < 1e-9 * max(dT1, dT2):
        return dT1
    return (dT1 - dT2) / math.log(dT1 / dT2)


def efectividad(tipo, NTU, Cr):
    """Relaciones de efectividad (tabla 10-3 con la numeracion de Holman; Incropera, cap. 11)."""
    if Cr < 1e-12:
        return 1 - math.exp(-NTU)
    if tipo == 'contracorriente':
        if abs(1 - Cr) < 1e-9:
            return NTU / (1 + NTU)
        x = math.exp(-NTU * (1 - Cr))
        return (1 - x) / (1 - Cr * x)
    if tipo == 'paralelo':
        return (1 - math.exp(-NTU * (1 + Cr))) / (1 + Cr)
    if tipo == 'carcasa':
        s = math.sqrt(1 + Cr * Cr)
        x = math.exp(-NTU * s)
        return 2 / (1 + Cr + s * (1 + x) / (1 - x))
    raise ValueError('tipo: contracorriente, paralelo o carcasa')


def ntu_de_efectividad(tipo, eps, Cr):
    """Relaciones NTU(efectividad) (tabla 10-4 con la numeracion de Holman; Incropera, cap. 11)."""
    if not 0 < eps < 1:
        raise ValueError('efectividad fuera de 0 a 1')
    if Cr < 1e-12:
        return -math.log(1 - eps)
    if tipo == 'contracorriente':
        if abs(1 - Cr) < 1e-9:
            return eps / (1 - eps)
        return math.log((eps - 1) / (eps * Cr - 1)) / (Cr - 1)
    if tipo == 'paralelo':
        if eps * (1 + Cr) >= 1:
            raise ValueError('en paralelo la efectividad no puede llegar a %s con Cr = %s' % (n(eps, 3), n(Cr, 3)))
        return -math.log(1 - eps * (1 + Cr)) / (1 + Cr)
    if tipo == 'carcasa':
        s = math.sqrt(1 + Cr * Cr)
        E = (2 / eps - (1 + Cr)) / s
        if E <= 1:
            raise ValueError('con un paso de carcasa no se llega a esa efectividad: hacen falta más pasos de carcasa')
        return -math.log((E - 1) / (E + 1)) / s
    raise ValueError('tipo: contracorriente, paralelo o carcasa')


def factor_F(P, R):
    """F de un paso de carcasa y 2, 4, ... pasos de tubos. P = (to - ti)/(Ti - ti), R = (Ti - To)/(to - ti),
    con t del fluido de los tubos y T del de la carcasa."""
    if not 0 < P < 1:
        raise ValueError('P fuera de 0 a 1')
    s = math.sqrt(R * R + 1)
    den = 2 - P * (R + 1 + s)
    if den <= 0 or P * R >= 1:
        raise ValueError('con un paso de carcasa no se alcanzan esas temperaturas (hacen falta más pasos de carcasa)')
    if abs(R - 1) < 1e-9:
        return (P * math.sqrt(2) / (1 - P)) / math.log((2 - P * (2 - math.sqrt(2))) / (2 - P * (2 + math.sqrt(2))))
    return (s / (R - 1)) * math.log((1 - P) / (1 - P * R)) / math.log((2 - P * (R + 1 - s)) / den)


def intercambiador(tipo, thi=None, tho=None, tci=None, tco=None, Ch=None, Cc=None, U=None, A=None, q=None,
                   tubos='frio'):
    L = []
    r = {}
    # completar con balances de energia
    if q is None and Ch and thi is not None and tho is not None:
        q = Ch * (thi - tho)
    if q is None and Cc and tci is not None and tco is not None:
        q = Cc * (tco - tci)
    if U and A and Ch and Cc and thi is not None and tci is not None and (tho is None or tco is None):
        Cmin, Cmax = min(Ch, Cc), max(Ch, Cc)
        Cr = Cmin / Cmax
        NTU = U * A / Cmin
        eps = efectividad(tipo, NTU, Cr)
        q = eps * Cmin * (thi - tci)
        tho, tco = thi - q / Ch, tci + q / Cc
        L.append('Método ε-NTU: Cmin = %s W/K, Cmax = %s W/K, Cr = %s; NTU = U·A/Cmin = %s·%s/%s = %s'
                 % (n(Cmin, 1), n(Cmax, 1), n(Cr, 4), n(U, 1), n(A, 3), n(Cmin, 1), n(NTU, 4)))
        L.append('ε = %s → q = ε·Cmin·(Th,e − Tc,e) = %s·%s·%s = %s W' % (n(eps, 4), n(eps, 4), n(Cmin, 1), n(thi - tci, 1), miles(q)))
        L.append('Salidas: Th,s = Th,e − q/Ch = %s °C;  Tc,s = Tc,e + q/Cc = %s °C' % (n(tho, 2), n(tco, 2)))
        r.update({'NTU': NTU, 'eps': eps, 'Cr': Cr})
    if q is not None:
        if tho is None and Ch and thi is not None:
            tho = thi - q / Ch
        if tco is None and Cc and tci is not None:
            tco = tci + q / Cc
        if thi is None and Ch and tho is not None:
            thi = tho + q / Ch
        if tci is None and Cc and tco is not None:
            tci = tco - q / Cc
    if None in (thi, tho, tci, tco) or q is None:
        raise ValueError('faltan datos: con U y A, dar Th,e, Tc,e, Ch y Cc; para dimensionar, las cuatro temperaturas '
                         '(o tres y Ch y Cc) y el calor o un caudal')
    if Ch and abs(Ch * (thi - tho) - q) > 1e-6 * max(1.0, abs(q)):
        L.append('AVISO: Ch·(Th,e − Th,s) = %s W no coincide con q = %s W' % (miles(Ch * (thi - tho)), miles(q)))
    if Cc and abs(Cc * (tco - tci) - q) > 1e-6 * max(1.0, abs(q)):
        L.append('AVISO: Cc·(Tc,s − Tc,e) = %s W no coincide con q = %s W' % (miles(Cc * (tco - tci)), miles(q)))
    if tipo == 'paralelo':
        d1, d2 = thi - tci, tho - tco
    else:
        d1, d2 = thi - tco, tho - tci
    dtml = dt_ml(d1, d2)
    F = 1.0
    if tipo == 'carcasa':
        if tubos == 'frio':
            P, R = (tco - tci) / (thi - tci), (thi - tho) / (tco - tci)
        else:
            P, R = (thi - tho) / (thi - tci), (tco - tci) / (thi - tho)
        F = factor_F(P, R)
        r.update({'P': P, 'R': R})
    L.append('ΔT extremos: %s y %s K → ΔTml = (ΔT1 − ΔT2)/ln(ΔT1/ΔT2) = %s K%s'
             % (n(d1, 2), n(d2, 2), n(dtml, 2), ' (como contracorriente)' if tipo == 'carcasa' else ''))
    if tipo == 'carcasa':
        L.append('Carcasa con 1 paso y 2, 4… pasos de tubos (fluido %s en los tubos): P = %s, R = %s → F = %s'
                 % (tubos, n(r['P'], 4), n(r['R'], 4), n(F, 4)))
    r.update({'q': q, 'dtml': dtml, 'F': F, 'thi': thi, 'tho': tho, 'tci': tci, 'tco': tco})
    if U and not A:
        A = q / (U * F * dtml)
        L.append('Área: A = q/(U·F·ΔTml) = %s/(%s·%s·%s) = %s m²' % (miles(q), n(U, 1), n(F, 4), n(dtml, 2), n(A, 3)))
        r['A'] = A
    elif U and A:
        L.append('Control: U·A·F·ΔTml = %s W (igual a q)' % miles(U * A * F * dtml))
    if U and A and Ch and Cc and 'eps' not in r:
        Cmin, Cmax = min(Ch, Cc), max(Ch, Cc)
        eps = q / (Cmin * (thi - tci))
        NTU = ntu_de_efectividad(tipo, eps, Cmin / Cmax)
        L.append('Control por ε-NTU: ε = %s, NTU = %s → U·A = NTU·Cmin = %s W/K (con LMTD: %s W/K)'
                 % (n(eps, 4), n(NTU, 4), n(NTU * Cmin, 1), n(q / (F * dtml), 1)))
        r.update({'eps': eps, 'NTU': NTU})
    return r, L


# ------------------------------------------------------------------------------------------ aletas
def aleta(tipo, k, h, L, t=None, d=None, w=1.0, tb=None, tinf=None):
    """Aleta de seccion constante con extremo convectivo, por longitud corregida (Incropera tablas 3.4 y 3.5)."""
    if tipo == 'recta':
        if not t:
            raise ValueError('falta el espesor --t (mm)')
        P, Ac = 2 * (w + t), w * t
        Lc = L + t / 2
        m = math.sqrt(2 * h / (k * t))
        Af = 2 * w * Lc
    elif tipo == 'aguja':
        if not d:
            raise ValueError('falta el diámetro --d (mm)')
        P, Ac = math.pi * d, math.pi * d * d / 4
        Lc = L + d / 4
        m = math.sqrt(4 * h / (k * d))
        Af = math.pi * d * Lc
    else:
        raise ValueError('tipo de aleta: recta o aguja')
    mLc = m * Lc
    eta = math.tanh(mLc) / mLc
    r = {'m': m, 'Lc': Lc, 'mLc': mLc, 'eta': eta, 'Af': Af, 'Ac': Ac}
    mx = math.sqrt(h * P / (k * Ac))           # m exacto con el perimetro real (extremo convectivo, tabla 3.4 caso A)
    hmk = h / (mx * k)
    r['frac_exacta'] = ((math.sinh(mx * L) + hmk * math.cosh(mx * L)) / (math.cosh(mx * L) + hmk * math.sinh(mx * L))
                        * math.sqrt(h * P * k * Ac))
    if tb is not None and tinf is not None:
        th = tb - tinf
        r['q'] = eta * h * Af * th
        r['q_exacta'] = r['frac_exacta'] * th
        r['efect'] = r['q'] / (h * Ac * th)
    return r


# ------------------------------------------------------------------------------------------ comandos
def cmd_propiedades(a):
    p = props(a.fluido, a.t)
    print('%s a %s °C (interpolación lineal de la tabla; %s)' % (a.fluido, n(a.t, 1),
          'Çengel, aire a 1 atm' if a.fluido == 'aire' else 'NIST SRD 69, agua líquida saturada'))
    print('ρ = %s kg/m³ · cp = %s J/(kg·K) · k = %s W/(m·K) · μ = %s kg/(m·s) · ν = %s m²/s · Pr = %s · α = %s m²/s · β = %s 1/K'
          % (n(p['rho'], 2), n(p['cp'], 1), n(p['k'], 5), sci(p['mu']), sci(p['nu']), n(p['Pr'], 4), sci(p['alpha']), sci(p['beta'])))
    return 0


def cmd_materiales(a):
    print('| Nombre | Descripción | k [W/(m·K)] | Fuente |')
    print('|---|---|---|---|')
    for nombre in sorted(MATERIALES):
        k, desc, f, tmax = MATERIALES[nombre]
        kt = ' · '.join('%s °C: %s' % (n(t, 0), n(v, 3)) for t, v in k) if isinstance(k, tuple) else n(k, 4 if k < 1 else 1)
        if tmax:
            desc += ' (hasta %s °C)' % n(tmax, 0)
        print('| %s | %s | %s | %s |' % (nombre, desc, kt, FUENTES[f]))
    print('Valores de cálculo: si el fabricante, la norma o la consigna dan otros, mandan esos.')
    return 0


def cmd_conveccion(a):
    c = a.caso
    if a.ts is None and c != 'tubo':
        raise ValueError('falta --ts (temperatura de la superficie)')
    if c in ('vertical', 'cilindro', 'techo', 'piso'):
        L = a.L if a.L is not None else (a.D if c == 'cilindro' else None)
        if L is None:
            raise ValueError('falta --L (altura, o área/perímetro en techo y piso) o --D (cilindro), en m')
        r = h_natural(c, a.ts, a.tinf, L, a.fluido)
    elif c == 'placa':
        if a.v is None or a.L is None:
            raise ValueError('placa con flujo forzado: --v (m/s) y --L (largo en el sentido del flujo, m)')
        r = h_placa_forzada(a.v, a.L, a.ts, a.tinf, a.fluido)
    elif c == 'tubo':
        if a.D is None:
            raise ValueError('tubo: --D (diámetro interior, m), --tinf (temperatura media del fluido) y --v o --m')
        r = h_tubo(a.D, a.tinf, a.fluido, v=a.v, m=a.m, Ts=a.ts, condicion=a.condicion)
    else:
        raise ValueError('caso no reconocido')
    print(texto_h('Convección', r))
    if c == 'tubo':
        print('Velocidad media %s m/s, caudal %s kg/s; %s el fluido' % (n(r['v'], 3), n(r['m'], 4), 'calentando' if r['calentando'] else 'enfriando'))
        if 'f' in r:
            print('f = (0,790·ln Re − 1,64)⁻² = %s' % n(r['f'], 5))
        if 'Nu_DB' in r:
            print('Comparación: Dittus-Boelter Nu = 0,023·Re^0,8·Pr^%s = %s → h = %s W/(m²·K) (%s %% de Gnielinski)'
                  % ('0,4' if r['calentando'] else '0,3', n(r['Nu_DB'], 2), n(r['h_DB'], 1), n(100 * r['Nu_DB'] / r['Nu'] - 100, 1)))
        if a.largo and a.tent is not None and a.ts is not None:
            p, As = r['p'], math.pi * a.D * a.largo
            Tsal = a.ts - (a.ts - a.tent) * math.exp(-r['h'] * As / (r['m'] * p['cp']))
            print('Pared a %s °C y %s m de tubo: Ts − T_sal = (Ts − T_ent)·exp(−h·As/(ṁ·cp)) → T_sal = %s °C; Q = ṁ·cp·(T_sal − T_ent) = %s W'
                  % (n(a.ts, 1), n(a.largo, 2), n(Tsal, 2), miles(r['m'] * p['cp'] * (Tsal - a.tent))))
            if abs((a.tent + Tsal) / 2 - a.tinf) > 2:
                print('AVISO: la temperatura media (%s °C) difiere de --tinf: repetir con --tinf %s'
                      % (n((a.tent + Tsal) / 2, 1), n((a.tent + Tsal) / 2, 1).replace(',', '.')))
    return 0


def cmd_radiacion(a):
    q = a.eps * SIGMA * ((a.ts + K0) ** 4 - (a.tsur + K0) ** 4)
    hr = h_rad(a.eps, a.ts, a.tsur)
    print('q = εσ(Ts⁴ − Tsur⁴) = %s·5,6704·10⁻⁸·(%s⁴ − %s⁴) = %s W/m²' % (n(a.eps, 2), n(a.ts + K0, 2), n(a.tsur + K0, 2), n(q, 1)))
    print('hr = εσ(Ts + Tsur)(Ts² + Tsur²) = %s W/(m²·K)  →  q = hr·(Ts − Tsur) = %s W/m²' % (n(hr, 3), n(hr * (a.ts - a.tsur), 1)))
    if a.area:
        print('En %s m²: Q = %s W' % (n(a.area, 2), miles(q * a.area)))
    print('Vale para una superficie chica frente a alrededores grandes (o de emisividad 1) a Tsur.')
    return 0


def cmd_pared(a):
    s = resolver_args(a)
    print('%s: Ti = %s °C → Te = %s °C' % ('Cilindro' if s['geom'] == 'cilindro' else 'Pared plana', n(a.ti, 1), n(a.te, 1)))
    print(informe(s, area=getattr(a, 'area', None), largo=getattr(a, 'largo', None)))
    return 0


def cmd_aislacion(a):
    r = calcular_aislacion(a)
    cil = r['geom'] == 'cilindro'
    uq = 'W/m' if cil else 'W/m²'
    crit = []
    if a.tmax is not None:
        crit.append('superficie a %s °C o menos' % n(a.tmax, 1))
    if a.qmax is not None:
        crit.append('pérdida de %s %s o menos' % (n(a.qmax, 1), uq))
    s = r['s_min']
    print('Aislación (%s, capa %s) para %s.' % (r['capa']['nombre'], a.aislante or 'de mayor resistencia', ' y '.join(crit)))
    print('Espesor mínimo: e = %s mm → Ts = %s °C, q = %s %s' % (n(1000 * r['e_min'], 1), n(s['T'][-1], 2), n(s['q'], 2), uq))
    if a.espesores:
        lista = [num(x) / 1000 for x in a.espesores.split('/')]
    else:
        tope = max(0.02, 2 * r['e_min'])
        paso = 0.01 if tope <= 0.1 else 0.025
        lista = [paso * i for i in range(0, int(tope / paso) + 2)]
    mult = a.largo if cil else a.area
    print('| e [mm] | Ts [°C] | q [%s] |%s' % (uq, ' Q [W] |' if mult else ''))
    print('|---|---|---|%s' % ('---|' if mult else ''))
    for e in lista:
        Ts, q = r['evaluar'](e)
        print('| %s | %s | %s |%s' % (n(1000 * e, 0), n(Ts, 1), n(q, 1), (' %s |' % miles(q * mult)) if mult else ''))
    if any(e == 0 for e in lista):
        print('La fila de 0 mm usa la misma superficie exterior (emisividad %s); para el equipo desnudo, recalcular con su ε.' % n(a.eps, 2))
    print('Se adopta el espesor comercial igual o mayor (catálogo del fabricante) y se recalcula con "%s".' % ('cilindro' if cil else 'pared'))
    return 0


def cmd_intercambiador(a):
    Ch = a.Ch if a.Ch else (a.mh * a.cph if a.mh and a.cph else None)
    Cc = a.Cc if a.Cc else (a.mc * a.cpc if a.mc and a.cpc else None)
    r, L = intercambiador(a.tipo, a.thi, a.tho, a.tci, a.tco, Ch, Cc, a.U, a.A, a.q, a.tubos)
    print('\n'.join(L))
    return 0


def cmd_aleta(a):
    r = aleta(a.tipo, a.k, a.h, a.L / 1000, t=a.t / 1000 if a.t else None, d=a.d / 1000 if a.d else None,
              w=a.w / 1000 if a.w else 1.0, tb=a.tb, tinf=a.tinf)
    if a.tipo == 'recta':
        print('m = √(2h/(k·t)) = %s 1/m;  Lc = L + t/2 = %s mm' % (n(r['m'], 3), n(1000 * r['Lc'], 2)))
    else:
        print('m = √(4h/(k·D)) = %s 1/m;  Lc = L + D/4 = %s mm' % (n(r['m'], 3), n(1000 * r['Lc'], 2)))
    print('m·Lc = %s → eficiencia η = tanh(m·Lc)/(m·Lc) = %s' % (n(r['mLc'], 4), n(r['eta'], 4)))
    if 'q' in r:
        por = '' if (a.w or a.tipo == 'aguja') else ' por metro de ancho'
        print('Calor por aleta%s: q = η·h·Af·(Tb − T∞) = %s W  (solución exacta con extremo convectivo: %s W)'
              % (por, n(r['q'], 3), n(r['q_exacta'], 3)))
        print('Efectividad: ε_a = q/(h·Ac·(Tb − T∞)) = %s' % n(r['efect'], 2))
        if a.n and a.Ab is not None:
            At = a.n * r['Af'] + a.Ab
            eta_o = 1 - a.n * r['Af'] / At * (1 - r['eta'])
            print('Conjunto de %d aletas: η_o = 1 − N·Af/At·(1 − η) = %s; Q = η_o·h·At·(Tb − T∞) = %s W'
                  % (a.n, n(eta_o, 4), n(eta_o * a.h * At * (a.tb - a.tinf), 1)))
    return 0


# ------------------------------------------------------------------------------------------ demo
class _A:
    """Argumentos armados en codigo para el demo."""
    def __init__(self, **kw):
        base = dict(capa=None, d=None, hi=None, ho=None, interior=None, exterior=None, fluido_int='aire', tsur=None,
                    eps=0.0, area=None, largo=None, puente=None, aislante=None, tmax=None, qmax=None, espesores=None)
        base.update(kw)
        self.__dict__.update(base)


DEMO_SECADOR = dict(ti=80.0, te=20.0, capa=['acero:1.25', 'lana-vidrio-panel:50', 'acero:0.8'],
                    interior='forzada:3:2', exterior='vertical:2', eps=0.8, area=20.0, aislante=2)
DEMO_CANO = dict(ti=150.0, te=20.0, d=60.3, capa=['lana-roca-coquilla:40'], eps=0.1, largo=1.0, aislante=1)


def cmd_demo():
    ok = []

    def chk(txt, cond):
        ok.append((txt, bool(cond)))

    def cerca(x, y, rel):
        return abs(x - y) <= rel * abs(y)
    # 1) propiedades
    p = props('aire', 45)
    chk('aire a 45 °C interpolado: k = %s, ν = %s, Pr = %s (Çengel, ej. 9-1: 0,02699; 1,750·10⁻⁵; 0,7241)'
        % (n(p['k'], 5), sci(p['nu']), n(p['Pr'], 4)),
        cerca(p['k'], 0.02699, 0.001) and cerca(p['nu'], 1.750e-5, 0.001) and cerca(p['Pr'], 0.7241, 0.001))
    peor = max(abs(r[5] / (r[4] / r[1]) - 1) for r in AIRE)
    chk('tabla de aire coherente: ν = μ/ρ en todas las filas (máx. %s %%)' % n(100 * peor, 2), peor < 0.002)
    ref = {0: 0.02436, 20: 0.02587, 100: 0.03162, 200: 0.03825, 400: 0.05024}     # CoolProp 8.0, aire a 1 atm
    peor = max(abs(props('aire', t)['k'] / v - 1) for t, v in ref.items())
    chk('k del aire contra CoolProp 8.0 (Lemmon y Jacobsen) de 0 a 400 °C: diferencia máx. %s %% (menor que 3,5 %%)'
        % n(100 * peor, 1), peor < 0.035)
    w = props('agua', 40)
    chk('agua a 40 °C: ρ = %s, cp = %s, k = %s, Pr = %s (Çengel: 992,1; 4179; 0,631; 4,32)'
        % (n(w['rho'], 2), n(w['cp'], 0), n(w['k'], 4), n(w['Pr'], 3)),
        cerca(w['rho'], 992.1, 0.001) and cerca(w['cp'], 4179, 0.001) and cerca(w['k'], 0.631, 0.006) and cerca(w['Pr'], 4.32, 0.006))
    chk('σ = %s W/(m²·K⁴) (CODATA: 5,670374419·10⁻⁸)' % sci(SIGMA, 10), cerca(SIGMA, 5.670374419e-8, 1e-9))
    # 2) conveccion natural: Cengel ej. 9-1 y 9-2 (propiedades del libro)
    k, Pr, nu, be = 0.02699, 0.7241, 1.750e-5, 1 / 318
    Ra = G * be * 50 * 0.08 ** 3 * Pr / nu ** 2
    Nu = nu_cilindro_horizontal(Ra, Pr)[0]
    h = Nu * k / 0.08
    Q = h * math.pi * 0.08 * 6 * 50
    chk('Çengel ej. 9-1, caño horizontal: Ra = %s, Nu = %s, h = %s, Q = %s W (libro: 1,867·10⁶; 17,39; 5,867; 442)'
        % (sci(Ra), n(Nu, 2), n(h, 3), n(Q, 0)), cerca(Ra, 1.867e6, 0.002) and cerca(Nu, 17.39, 0.002) and cerca(Q, 442, 0.003))
    Qr = 1.0 * math.pi * 0.08 * 6 * SIGMA * ((70 + K0) ** 4 - (20 + K0) ** 4)
    chk('Çengel ej. 9-1, radiación con ε = 1: %s W (libro: 553)' % n(Qr, 0), cerca(Qr, 553, 0.005))
    k, Pr, nu, be = 0.02808, 0.7202, 1.896e-5, 1 / 333
    Ra = G * be * 60 * 0.6 ** 3 * Pr / nu ** 2
    Nu = nu_placa_vertical(Ra, Pr)[0]
    chk('Çengel ej. 9-2, placa vertical: Ra = %s, Nu = %s, h = %s (libro: 7,649·10⁸; 113,3; 5,302)'
        % (sci(Ra), n(Nu, 1), n(Nu * k / 0.6, 3)), cerca(Ra, 7.649e8, 0.002) and cerca(Nu, 113.3, 0.002))
    Ra2 = Ra * (0.15 / 0.6) ** 3
    Nu_b = nu_placa_horizontal(Ra2, True, ley='1/4')[0]
    Nu_c = nu_placa_horizontal(Ra2, False)[0]
    chk('Çengel ej. 9-2, placa horizontal (L = 0,15 m): Nu arriba %s y abajo %s (libro: 31,75 y 15,87)'
        % (n(Nu_b, 2), n(Nu_c, 2)), cerca(Nu_b, 31.75, 0.002) and cerca(Nu_c, 15.87, 0.002))
    k, nu, al, Pr, be = 33.8e-3, 26.4e-6, 38.3e-6, 0.69, 2.5e-3
    Ra = 9.8 * be * 209 * 0.71 ** 3 / (nu * al)
    q = nu_placa_vertical(Ra, Pr)[0] * k / 0.71 * 0.71 * 1.02 * 209
    chk('Incropera (6.ª ed.) ej. 9.2, pantalla de chimenea: q = %s W (libro: 1060)' % n(q, 0), cerca(q, 1060, 0.003))
    k, nu, al, Pr, be = 0.0313, 22.8e-6, 32.8e-6, 0.697, 2.725e-3
    Ra = 9.8 * be * 142 * 0.1 ** 3 / (nu * al)
    Nu = nu_cilindro_horizontal(Ra, Pr)[0]
    qc = Nu * k / 0.1 * math.pi * 0.1 * 142
    qr = 0.85 * math.pi * 0.1 * 5.67e-8 * ((165 + 273) ** 4 - (23 + 273) ** 4)
    chk('Incropera (6.ª ed.) ej. 9.4, caño de vapor: Ra = %s, Nu = %s, q\' = %s + %s = %s W/m (libro: 5,073·10⁶; 23,3; 325 + 441 = 766; '
        'el Nu del libro queda 0,9 %% arriba de su propia fórmula)' % (sci(Ra), n(Nu, 2), n(qc, 0), n(qr, 0), n(qc + qr, 0)),
        cerca(Ra, 5.073e6, 0.002) and cerca(Nu, 23.3, 0.012) and cerca(qr, 441, 0.003) and cerca(qc + qr, 766, 0.006))
    chk('solucionario de Çengel (problemas 14-82 y 14-45): Nu = %s y %s (35,15 y 374,1)'
        % (n(nu_placa_vertical(1.495e7, 0.7316)[0], 2), n(nu_cilindro_horizontal(3.869e10, 0.7383)[0], 1)),
        cerca(nu_placa_vertical(1.495e7, 0.7316)[0], 35.15, 0.001) and cerca(nu_cilindro_horizontal(3.869e10, 0.7383)[0], 374.1, 0.001))
    # 3) conveccion forzada: Cengel ej. 7-1 (placa) y 8-5, 8-6 (tubos)
    Re = 2 * 5 / 242e-6
    h = nu_placa_forzada(Re, 2870)[0] * 0.144 / 5
    chk('Çengel ej. 7-1, aceite sobre placa: Re = %s, h = %s, Q = %s W (libro: 4,13·10⁴; 55,2; 11 040)'
        % (sci(Re), n(h, 2), miles(h * 5 * 40)), cerca(h, 55.2, 0.002) and cerca(h * 5 * 40, 11040, 0.002))
    V = 0.01 / 60 / (math.pi * 0.03 ** 2 / 4)
    Re = V * 0.03 / 0.658e-6
    Nu = nu_dittus_boelter(Re, 4.32, True)
    h = Nu * 0.631 / 0.03
    qs = 992.1 * 0.01 / 60 * 4179 * 50 / (math.pi * 0.03 * 5)
    chk('Çengel ej. 8-5, agua calentada en tubo: Re = %s, Nu = %s, h = %s, Ts salida = %s °C (libro: 10 760; 69,4; 1460; 115)'
        % (miles(Re), n(Nu, 1), n(h, 0), n(65 + qs / h, 1)),
        cerca(Re, 10760, 0.002) and cerca(Nu, 69.4, 0.002) and cerca(h, 1460, 0.002) and cerca(65 + qs / h, 115, 0.005))
    Re = 3.75 * 0.2 / 2.097e-5
    Nu = nu_dittus_boelter(Re, 0.7154, False)
    h = Nu * 0.02953 / 0.2
    Tsal = 60 + 20 * math.exp(-h * 6.4 / (1.009 * 0.15 * 1008))
    chk('Çengel ej. 8-6, aire enfriado en ducto: Re = %s, Nu = %s, h = %s, T salida = %s °C (libro: 35 765; 91,4; 13,5; 71,3)'
        % (miles(Re), n(Nu, 1), n(h, 2), n(Tsal, 1)),
        cerca(Re, 35765, 0.001) and cerca(Nu, 91.4, 0.002) and cerca(h, 13.5, 0.005) and cerca(Tsal, 71.3, 0.002))
    dif = [abs(nu_dittus_boelter(R, P) / nu_gnielinski(R, P) - 1) for R in (1e4, 3e4, 1e5) for P in (0.7, 2, 5)]
    chk('Gnielinski y Dittus-Boelter coinciden dentro del 20 %% donde valen las dos (máx. %s %%)' % n(100 * max(dif), 1), max(dif) < 0.2)
    # 4) aletas, radio critico, pared con espesor por despeje directo
    r = aleta('recta', 200, 60, 0.06, t=0.003, w=1.0, tb=100, tinf=20)
    chk('aleta recta (biblioteca de EES, Nellis y Klein): η = %s (0,8063); longitud corregida vs exacta: %s %%'
        % (n(r['eta'], 4), n(100 * (r['q'] / r['q_exacta'] - 1), 2)), cerca(r['eta'], 0.8063, 0.0005) and cerca(r['q'], r['q_exacta'], 0.01))
    rcr = 0.055 / 5
    chk('Incropera (6.ª ed.) ej. 3.5: radio crítico r_cr = k/h = 0,055/5 = %s mm (libro: 11 mm)' % n(1000 * rcr, 1), cerca(rcr, 0.011, 1e-9))

    def ventana(e):          # dos plasticos, LA = e y LB = e/2; adentro h = 25 + 25 (conveccion y radiacion a 400 C)
        capas = [leer_capa('A:%r:0.15' % (1000 * e)), leer_capa('B:%r:0.08' % (500 * e))]
        s = resolver(capas, 400.0, 25.0, 25.0, 0.0, lambda T: {'h': 50.0}, lambda T, D: {'h': 25.0})
        return s['T'][-1], s['q']
    LA = espesor_minimo(ventana, lambda Ts, q: Ts <= 50.0, e_max=0.5)
    L_mano = 1.5 * (375 / 625 - 1 / 50 - 1 / 25) / (1 / 0.15 + 0.5 / 0.08)
    chk('Incropera (4.ª ed.) ej. 3.1, ventana del horno (Ts ≤ 50 °C, LA = 2·LB): L = %s mm (despeje directo: %s mm)'
        % (n(1500 * LA, 2), n(1000 * L_mano, 2)), cerca(1.5 * LA, L_mano, 1e-6))
    # 5) intercambiadores
    r, _ = intercambiador('contracorriente', thi=100, tho=60, tci=30, Ch=0.1 * 2131, Cc=0.2 * 4178)
    chk('Incropera (6.ª ed.) ej. 11.1: q = %s W, Tc,s = %s °C, ΔTml = %s K (8524; 40,2; 43,2)'
        % (miles(r['q']), n(r['tco'], 1), n(r['dtml'], 1)),
        cerca(r['q'], 8524, 0.001) and abs(r['tco'] - 40.2) < 0.05 and abs(r['dtml'] - 43.2) < 0.05)
    peor = 0.0
    for tipo in ('contracorriente', 'paralelo', 'carcasa'):
        for NTU in (0.3, 1.0, 2.5):
            for Cr in (0.0, 0.4, 1.0):
                e = efectividad(tipo, NTU, Cr)
                peor = max(peor, abs(ntu_de_efectividad(tipo, e, Cr) / NTU - 1))
                Ch, Cc = (1000.0, 1000.0 / Cr) if Cr > 0 else (1000.0, 1e12)
                A = NTU * 1000 / 500
                rr, _ = intercambiador(tipo, thi=150, tci=20, Ch=Ch, Cc=Cc, U=500, A=A)
                peor = max(peor, abs(500 * A * rr['F'] * rr['dtml'] / rr['q'] - 1))
    chk('ε-NTU: la inversa NTU(ε) y U·A·F·ΔTml = q cierran en los 3 tipos (error máx. %s)' % sci(peor, 2), peor < 1e-6)
    peor = 0.0
    for P in (0.1, 0.3, 0.5):
        for R in (0.5, 1.0, 2.0):
            try:
                F = factor_F(P, R)
            except ValueError:
                continue
            eps, Cr = (P, R) if R <= 1 else (P * R, 1 / R)
            peor = max(peor, abs(F - ntu_de_efectividad('contracorriente', eps, Cr) / ntu_de_efectividad('carcasa', eps, Cr)))
    chk('F de 1 paso de carcasa = NTU contracorriente/NTU carcasa (máx. diferencia %s); F(P = 0,5; R = 1) = %s'
        % (sci(peor, 2), n(factor_F(0.5, 1.0), 4)), peor < 1e-9)
    # 6) caño de acero desnudo de 2" contra la tabla 6 de NIA (datos de ASHRAE), aire quieto a 80 °F, ε = 0,8
    peor = 0.0
    for tf, btu in ((180, 141), (280, 350), (380, 623), (480, 974), (580, 1420)):
        sd = resolver([], (tf - 32) / 1.8, 80 / 1.8 - 32 / 1.8, 80 / 1.8 - 32 / 1.8, 0.8, None,
                      lambda T, D: h_natural('cilindro', T, 80 / 1.8 - 32 / 1.8, D), 'cilindro', 0.0603 / 2)
        peor = max(peor, abs(sd['q'] / (btu * 0.961519) - 1))
    chk('caño desnudo de 2" de 82 a 304 °C contra ASHRAE (NIA, tabla 6): diferencia máx. %s %% (menor que 3 %%)' % n(100 * peor, 1),
        peor < 0.03)
    # 7) ejemplo del SKILL.md: pared del secador
    D = DEMO
    s = resolver_args(_A(**DEMO_SECADOR))
    hi, hc, hr = s['hi']['h'], s['hc'], s['hr']
    chk('secador: hi = %s, hc = %s, hr = %s W/(m²·K) (SKILL.md: %s; %s; %s)' % (n(hi, 2), n(hc, 2), n(hr, 2), n(D['hi'], 2),
        n(D['hc'], 2), n(D['hr'], 2)), abs(hi - D['hi']) < 0.006 and abs(hc - D['hc']) < 0.006 and abs(hr - D['hr']) < 0.006)
    chk('secador: Ts = %s °C, q = %s W/m², Q = %s W, U = %s (SKILL.md: %s; %s; %s; %s)'
        % (n(s['T'][-1], 1), n(s['q'], 1), miles(20 * s['q']), n(s['q'] / 60, 3), n(D['Tso'], 1), n(D['q'], 1), miles(D['Q']), n(D['U'], 3)),
        abs(s['T'][-1] - D['Tso']) < 0.06 and abs(s['q'] - D['q']) < 0.06 and abs(20 * s['q'] - D['Q']) < 0.6
        and abs(s['q'] / 60 - D['U']) < 0.0006)
    chk('secador: balance en la superficie exterior: %s = %s W/m²' % (n(s['q_ext'], 4), n(s['q'], 4)), abs(s['q_ext'] - s['q']) < 1e-6)
    Tm_lana = (s['T'][1] + s['T'][2]) / 2
    chk('secador: la lana trabaja a %s °C de media y toma k = %s de la ficha (0,034 a 10 °C; 0,038 a 50 °C)'
        % (n(Tm_lana, 1), n(s['k'][1], 4)), abs(s['k'][1] - (0.034 + (Tm_lana - 10) / 40 * 0.004)) < 1e-9)
    s0 = resolver_args(_A(**dict(DEMO_SECADOR, capa=['acero:1.25', 'acero:0.8'], aislante=1)))
    chk('secador sin lana: q = %s W/m², Ts = %s °C, Q = %s W (SKILL.md: %s; %s; %s)'
        % (n(s0['q'], 1), n(s0['T'][-1], 1), miles(20 * s0['q']), n(D['q0'], 1), n(D['Ts0'], 1), miles(D['Q0'])),
        abs(s0['q'] - D['q0']) < 0.06 and abs(s0['T'][-1] - D['Ts0']) < 0.06)
    ra = calcular_aislacion(_A(qmax=D['qmax'], **DEMO_SECADOR))
    chk('secador: espesor mínimo para q ≤ %s W/m²: %s mm, con él q = %s (SKILL.md: %s mm)'
        % (n(D['qmax'], 0), n(1000 * ra['e_min'], 1), n(ra['s_min']['q'], 3), n(D['e_min'], 1)),
        abs(1000 * ra['e_min'] - D['e_min']) < 0.06 and abs(ra['s_min']['q'] - D['qmax']) < 1e-3)
    s8 = resolver_args(_A(**dict(DEMO_SECADOR, capa=['acero:1.25', 'lana-vidrio-panel:80', 'acero:0.8'])))
    chk('secador con 2 × 40 mm: q = %s W/m², Q = %s W (SKILL.md: %s; %s)' % (n(s8['q'], 1), miles(20 * s8['q']), n(D['q80'], 1), miles(D['Q80'])),
        abs(s8['q'] - D['q80']) < 0.06 and abs(20 * s8['q'] - D['Q80']) < 0.6)
    # 8) caño de vapor del SKILL.md
    sc = resolver_args(_A(**DEMO_CANO))
    chk('caño de vapor, 40 mm de lana de roca y chapa de aluminio: Ts = %s °C, q\' = %s W/m (SKILL.md: %s; %s)'
        % (n(sc['T'][-1], 1), n(sc['q'], 1), n(D['Ts_cano'], 1), n(D['q_cano'], 1)),
        abs(sc['T'][-1] - D['Ts_cano']) < 0.06 and abs(sc['q'] - D['q_cano']) < 0.06)
    sd = resolver_args(_A(**dict(DEMO_CANO, capa=[], eps=0.8)))
    chk('caño desnudo con ε = 0,8: q\' = %s W/m (SKILL.md: %s)' % (n(sd['q'], 0), n(D['q_desnudo'], 0)), abs(sd['q'] - D['q_desnudo']) < 0.6)
    e60 = calcular_aislacion(_A(tmax=60.0, **DEMO_CANO))['e_min']
    e50 = calcular_aislacion(_A(qmax=50.0, **DEMO_CANO))['e_min']
    chk('caño: espesor mínimo para Ts ≤ 60 °C: %s mm; para q\' ≤ 50 W/m: %s mm (SKILL.md: %s; %s)'
        % (n(1000 * e60, 1), n(1000 * e50, 1), n(D['e60'], 1), n(D['e_q50'], 1)),
        abs(1000 * e60 - D['e60']) < 0.06 and abs(1000 * e50 - D['e_q50']) < 0.06)
    for txt, bien in ok:
        print('  %s %s' % ('ok ' if bien else 'MAL', txt))
    todo = all(b for _, b in ok)
    print('DEMO %s' % ('OK' if todo else 'FALLO'))
    return 0 if todo else 1


# valores del ejemplo del SKILL.md (los controla el demo)
DEMO = {'hi': 4.69, 'hc': 2.43, 'hr': 4.69, 'Tso': 25.0, 'q': 35.8, 'Q': 717, 'U': 0.597, 'q0': 184.0, 'Ts0': 40.9, 'Q0': 3679,
        'qmax': 25.0, 'e_min': 77.4, 'q80': 24.3, 'Q80': 486, 'Ts_cano': 37.9, 'q_cano': 37.8, 'q_desnudo': 399, 'e60': 14.2,
        'e_q50': 24.5}


# ------------------------------------------------------------------------------------------ parser
def construir_parser():
    ap = argparse.ArgumentParser(prog='calor.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True, metavar='comando')

    p = sp.add_parser('propiedades', help='propiedades del aire o del agua a una temperatura')
    p.add_argument('--fluido', choices=['aire', 'agua'], default='aire')
    p.add_argument('--t', type=float, required=True, help='temperatura en °C (aire de −20 a 600; agua de 5 a 200)')

    sp.add_parser('materiales', help='conductividades cargadas y su fuente')

    p = sp.add_parser('conveccion', help='coeficiente de convección h de una superficie',
                      description='Casos: vertical (placa o pared, --L altura), cilindro (horizontal, --D), techo (cara '
                                  'superior de una placa horizontal) y piso (cara inferior), con --L = área/perímetro, placa '
                                  '(flujo forzado, --v y --L en el sentido del flujo) y tubo (flujo interno, --D, --v o --m; '
                                  '--tinf es la temperatura media del fluido y --ts la de la pared, si se conoce).')
    p.add_argument('--caso', required=True, choices=['vertical', 'cilindro', 'techo', 'piso', 'placa', 'tubo'])
    p.add_argument('--ts', type=float, help='temperatura de la superficie, °C')
    p.add_argument('--tinf', type=float, required=True, help='temperatura del fluido lejos de la superficie (o media en tubo), °C')
    p.add_argument('--L', type=float, help='longitud característica, m')
    p.add_argument('--D', type=float, help='diámetro, m')
    p.add_argument('--v', type=float, help='velocidad, m/s')
    p.add_argument('--m', type=float, help='caudal másico en tubo, kg/s')
    p.add_argument('--fluido', choices=['aire', 'agua'], default='aire')
    p.add_argument('--condicion', choices=['ts', 'q'], default='ts', help='tubo laminar: pared isoterma (3,66) o flujo uniforme (4,36)')
    p.add_argument('--largo', type=float, help='tubo: largo en m para la temperatura de salida (con --ts y --tent)')
    p.add_argument('--tent', type=float, help='tubo: temperatura de entrada del fluido, °C')

    p = sp.add_parser('radiacion', help='radiación de una superficie a alrededores grandes')
    p.add_argument('--ts', type=float, required=True)
    p.add_argument('--tsur', type=float, required=True)
    p.add_argument('--eps', type=float, required=True)
    p.add_argument('--area', type=float)

    def comunes(p, cil):
        p.add_argument('--ti', type=float, required=True, help='temperatura del fluido interior, °C')
        p.add_argument('--te', type=float, required=True, help='temperatura del aire exterior, °C')
        p.add_argument('--tsur', type=float, help='temperatura de los alrededores para la radiación (por defecto Te)')
        p.add_argument('--capa', action='append', help='MATERIAL:espesor_mm[:k], de adentro hacia afuera (repetir)')
        p.add_argument('--hi', type=float, help='h interior dado, W/(m²·K)')
        p.add_argument('--interior', help='forzada:V:L (aire a V m/s a lo largo de L m), vertical:H (convección natural)'
                       + (', tubo:V (fluido a V m/s por el caño)' if cil else ''))
        p.add_argument('--fluido-int', dest='fluido_int', choices=['aire', 'agua'], default='aire')
        p.add_argument('--ho', type=float, help='h exterior de convección dado, W/(m²·K)')
        p.add_argument('--exterior', help=('horizontal (por defecto) o vertical:H' if cil else
                                           'vertical:H, techo:L, piso:L (L = área/perímetro) o viento:V:L'))
        p.add_argument('--eps', type=float, default=0.0, help='emisividad de la superficie exterior (0 = sin radiación)')
        p.add_argument('--aislante', type=int, help='número de capa aislante (1 = la primera); por defecto la de mayor R')
        if cil:
            p.add_argument('--d', type=float, required=True, help='diámetro donde empieza la primera capa, mm')
            p.add_argument('--largo', type=float, help='largo del caño, m')
        else:
            p.add_argument('--area', type=float, help='área de la pared, m²')
            p.add_argument('--puente', help='F:K: fracción del área de la capa aislante ocupada por otro material de conductividad K')

    p = sp.add_parser('pared', help='pared plana multicapa (horno, secador, cámara, tanque de paredes planas)')
    comunes(p, False)
    p = sp.add_parser('cilindro', help='caño o tanque cilindrico con capas')
    comunes(p, True)

    p = sp.add_parser('aislacion', help='espesor de aislación por temperatura de superficie o pérdida admitida',
                      description='Mismas opciones que "pared"; con --d (mm) es un cilindro. El espesor que se busca es '
                                  'el de la capa --aislante.')
    comunes(p, False)
    p.add_argument('--d', type=float, help='diámetro exterior del caño, mm (cilindro)')
    p.add_argument('--largo', type=float, help='largo del caño, m')
    p.add_argument('--tmax', type=float, help='temperatura máxima de la superficie exterior, °C')
    p.add_argument('--qmax', type=float, help='pérdida admitida: W/m² en pared, W/m en caño')
    p.add_argument('--espesores', help='espesores a tabular en mm, separados por / (por ejemplo 25/40/50/80)')

    p = sp.add_parser('intercambiador', help='intercambiador de calor: LMTD con F o ε-NTU',
                      description='Para dimensionar: las cuatro temperaturas (o tres y Ch y Cc) y U → área. Para verificar '
                                  'uno existente: Th,e, Tc,e, Ch, Cc, U y A → salidas por ε-NTU. C = ṁ·cp en W/K.')
    p.add_argument('--tipo', required=True, choices=['contracorriente', 'paralelo', 'carcasa'],
                   help='carcasa = 1 paso de carcasa y 2, 4… pasos de tubos')
    for nombre in ('thi', 'tho', 'tci', 'tco'):
        p.add_argument('--' + nombre, type=float, help={'thi': 'entrada caliente', 'tho': 'salida caliente',
                                                        'tci': 'entrada fría', 'tco': 'salida fría'}[nombre] + ', °C')
    for nombre, ayuda in (('Ch', 'W/K del caliente'), ('Cc', 'W/K del frío'), ('mh', 'kg/s caliente'), ('mc', 'kg/s frío'),
                          ('cph', 'J/(kg·K) caliente'), ('cpc', 'J/(kg·K) frío'), ('U', 'W/(m²·K)'), ('A', 'm²'), ('q', 'W')):
        p.add_argument('--' + nombre, type=float, help=ayuda)
    p.add_argument('--tubos', choices=['frio', 'caliente'], default='frio', help='fluido que va por los tubos (carcasa)')

    p = sp.add_parser('aleta', help='eficiencia y calor de una aleta recta o de aguja')
    p.add_argument('--tipo', choices=['recta', 'aguja'], default='recta')
    p.add_argument('--k', type=float, required=True, help='conductividad de la aleta, W/(m·K)')
    p.add_argument('--h', type=float, required=True, help='coeficiente de convección, W/(m²·K)')
    p.add_argument('--L', type=float, required=True, help='largo de la aleta, mm')
    p.add_argument('--t', type=float, help='espesor de la aleta recta, mm')
    p.add_argument('--d', type=float, help='diámetro de la aleta de aguja, mm')
    p.add_argument('--w', type=float, help='ancho de la aleta recta, mm (sin él, por metro de ancho)')
    p.add_argument('--tb', type=float, help='temperatura de la base, °C')
    p.add_argument('--tinf', type=float, help='temperatura del fluido, °C')
    p.add_argument('--n', type=int, help='cantidad de aletas (para η_o)')
    p.add_argument('--Ab', type=float, help='área de base sin aletas, m² (para η_o)')

    sp.add_parser('demo', help='reproduce el ejemplo del SKILL.md y los ejemplos publicados')
    return ap


def main(argv=None):
    a = construir_parser().parse_args(argv)
    try:
        if a.cmd == 'demo':
            return cmd_demo()
        return {'propiedades': cmd_propiedades, 'materiales': cmd_materiales, 'conveccion': cmd_conveccion,
                'radiacion': cmd_radiacion, 'pared': cmd_pared, 'cilindro': cmd_pared, 'aislacion': cmd_aislacion,
                'intercambiador': cmd_intercambiador, 'aleta': cmd_aleta}[a.cmd](a)
    except ValueError as ex:
        print('calor.py: %s' % ex, file=sys.stderr)
        return 2


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
