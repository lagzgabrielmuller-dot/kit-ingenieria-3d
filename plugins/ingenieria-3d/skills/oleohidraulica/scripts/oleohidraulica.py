#!/usr/bin/env python3
"""oleohidraulica.py - cálculos de oleohidráulica para prensas, máquinas y equipos móviles.

Cada comando imprime fórmula, reemplazo y resultado con coma decimal, listo para una memoria de cálculo.
Unidades: presión en bar (manométrica salvo que se diga), caudal en L/min, diámetros en mm,
fuerzas en kN, largos de cañería en m, viscosidad en mm²/s, potencia en kW.
Los números se escriben con punto en la línea de comandos (--p 160 --Q 26.2).

  cilindro    fuerzas, relación de áreas, presión para una carga, velocidades, tiempos y diámetro normalizado
  bomba       cilindrada, caudal real, potencia hidráulica, torque y motor eléctrico
  motor       motor hidráulico: velocidad, torque y potencia (o cilindrada y caudal para un torque y una velocidad)
  viscosidad  viscosidad de un aceite a otra temperatura (ASTM D341)
  cano        diámetro interior mínimo por velocidad recomendada y manguera EN 853 2SN que cumple
  perdida     pérdida de carga por Darcy-Weisbach (laminar o turbulento)
  pandeo      pandeo del vástago: Euler o Tetmajer (método de los catálogos Rexroth) y longitud máxima
  acumulador  volumen de un acumulador de gas (Boyle, isotérmico y adiabático)
  tanque      volumen orientativo del tanque
  calor       potencia que se vuelve calor y la que disipa el tanque
  demo        ejemplo resuelto de una prensa de 10 t; verifica cada resultado y sale con 1 si algo no coincide

Ejemplos:
  python oleohidraulica.py cilindro --t 10 --p 160
  python oleohidraulica.py cilindro --D 100 --d 70 --p 160 --t 10 --carrera 300 --Q 26.2
  python oleohidraulica.py bomba --Q 25 --p 160 --n 1450
  python oleohidraulica.py cano --Q 26.2 --tipo presion --p 160
  python oleohidraulica.py perdida --Q 26.2 --d 13 --L 3 --vg 46 --temp 50
  python oleohidraulica.py pandeo --d 70 --L 450 --caso 3 --D 100 --p 160
  python oleohidraulica.py acumulador --dV 0.4 --p1 140 --p2 160
  python oleohidraulica.py calor --p 160 --Q 26.2 --area 1.14 --dT 25
Ayuda de cada comando: python oleohidraulica.py cilindro --help
Solo biblioteca estándar (Python 3.9 o posterior). Las fuentes de cada dato están en ../references/.
"""
import argparse
import math
import sys

G = 9.80665          # m/s2, gravedad normal (para pasar toneladas a kN)
P_ATM = 1.013        # bar, presion atmosferica para pasar a presion absoluta

# Diametros de cilindro preferidos de ISO 3320 (extracto publico de la edicion 1987; vigente ISO 3320:2013).
# No preferidos: 90, 110, 140, 180, 220, 280, 360, 450.
DIAMETROS = [8, 10, 12, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 320, 400, 500]
# Vastagos por diametro de la serie compacta de 160 bar ISO 6020-2 (catalogo Confortinet ISO 6020/2;
# coinciden con Rexroth CDT3, RE 17049/07.17).
ISO6020_2 = {25: (12, 18), 32: (14, 18, 22), 40: (18, 22, 28), 50: (22, 28, 36), 63: (28, 36, 45),
             80: (36, 45, 56), 100: (45, 56, 70), 125: (56, 70, 90), 160: (70, 90, 110), 200: (90, 110, 140)}
RELACIONES_ISO = [1.06, 1.12, 1.25, 1.4, 1.6, 2.0, 2.5, 5.0]    # relaciones de areas nominales (ISO 7181)
ETA_AVANCE, ETA_RETROCESO = 0.95, 0.92   # rendimientos de los diagramas de fuerza de HANSA-FLEX (2024)
V_MAX_JUNTAS, V_MAX_EXTREMOS = 0.42, 0.10   # m/s, HANSA-FLEX: juntas estandar / al entrar en los extremos

AZPF = [4, 5.5, 8, 11, 14, 16, 19, 22.5, 25, 28]   # cm3, bomba de engranajes Rexroth AZPF (RE 10089/2019-07-17)
MOTORES_KW = [0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3, 4, 5.5, 7.5, 11, 15, 18.5, 22, 30, 37, 45, 55, 75]   # skill calculos-ingenieria

# ISO 3448: grado -> (minimo, maximo) a 40 °C en mm2/s (punto medio +-10 %)
ISO_VG = {10: (9.0, 11.0), 15: (13.5, 16.5), 22: (19.8, 24.2), 32: (28.8, 35.2), 46: (41.4, 50.6),
          68: (61.2, 74.8), 100: (90.0, 110.0), 150: (135.0, 165.0)}
# Aceite de ejemplo: Mobil Nuto H (valores tipicos de la hoja de producto): nu40, nu100 [mm2/s], densidad 15 °C [kg/m3]
ACEITES = {32: (31.4, 5.3, 872.0), 46: (44.0, 6.6, 876.0), 68: (63.3, 8.3, 882.0)}

# Manguera DIN EN 853 2SN / SAE 100 R2 S (catalogo Semperit 2023): DN, dash, pulgadas, diametro interior [mm], presion de trabajo [bar]
MANGUERAS = [(6, '-4', '1/4"', 6.6, 400), (8, '-5', '5/16"', 8.3, 350), (10, '-6', '3/8"', 9.9, 330),
             (12, '-8', '1/2"', 13.0, 275), (16, '-10', '5/8"', 16.4, 250), (19, '-12', '3/4"', 19.5, 215),
             (25, '-16', '1"', 26.0, 165), (31, '-20', '1 1/4"', 32.5, 125), (38, '-24', '1 1/2"', 38.7, 90),
             (51, '-32', '2"', 51.1, 80)]
V_ASPIRACION, V_RETORNO = 1.0, 3.0   # m/s, maximos de HANSA-FLEX (2026); Atos y Roymech dan rangos parecidos

HYDAC_L = [0.5, 1, 2.5, 4, 5, 6, 10, 13, 20, 24, 32, 50, 60, 80, 100, 130, 160, 200]   # vejiga HYDAC 3.201.31/04.21
EULER = {1: (2.0, 'empotrado y libre (carga sin guiar)'), 2: (1.0, 'articulado en los dos extremos'),
         3: (0.7, 'empotrado y articulado guiado'), 4: (0.5, 'empotrado en los dos extremos')}
TETMAJER_A, TETMAJER_B = 335.0, 0.62   # N/mm2: recta de Tetmajer del acero S355 (St 52), la de los catalogos Rexroth
H_TANQUE = {'normal': 12.0, 'forzada': 24.0, 'mala': 6.0}   # W/(m2·K), Casey (Power & Motion, 2019)


# ------------------------------------------------------------------------------------------ formato
def n(x, d=2):
    """Coma decimal; espacio como separador de miles desde 10 000."""
    s = '%.*f' % (d, x)
    ent, _, dec = s.partition('.')
    signo = '-' if ent.startswith('-') else ''
    ent = ent.lstrip('-')
    if len(ent) > 4:
        grupos = []
        while len(ent) > 3:
            grupos.insert(0, ent[-3:])
            ent = ent[:-3]
        grupos.insert(0, ent)
        ent = ' '.join(grupos)
    return signo + ent + (',' + dec if dec else '')


def siguiente(valor, serie):
    return next((x for x in serie if x >= valor - 1e-9), None)


def positivo(**kw):
    for k, v in kw.items():
        if v is None or v <= 0:
            raise ValueError('%s tiene que ser positivo' % k)


# ------------------------------------------------------------------------------------------ cilindro
def areas(D, d):
    positivo(D=D, d=d)
    if d >= D:
        raise ValueError('el vástago tiene que ser menor que el émbolo')
    A1 = math.pi * D ** 2 / 4                 # mm2, lado del émbolo
    Av = math.pi * d ** 2 / 4                 # mm2, sección del vástago
    return A1, Av, A1 - Av                    # A3 = área anular


def diametro_minimo(F_kN, p, eta=ETA_AVANCE):
    positivo(F=F_kN, p=p, eta=eta)
    Dmin = math.sqrt(4 * F_kN * 1000 / (math.pi * p * 0.1 * eta))
    return Dmin, siguiente(Dmin, DIAMETROS)


def calc_cilindro(D, d, p, F_kN=None, carrera=None, Q=None, eta=ETA_AVANCE, eta_r=ETA_RETROCESO):
    A1, Av, A3 = areas(D, d)
    r = {'D': D, 'd': d, 'p': p, 'A1': A1, 'Av': Av, 'A3': A3, 'phi': A1 / A3,
         'F_av_teo': p * 0.1 * A1 / 1000, 'F_av': eta * p * 0.1 * A1 / 1000,
         'F_ret_teo': p * 0.1 * A3 / 1000, 'F_ret': eta_r * p * 0.1 * A3 / 1000,
         'F_reg': eta * p * 0.1 * Av / 1000, 'p_intens': p * A1 / A3, 'eta': eta, 'eta_r': eta_r}
    if F_kN:
        r['F'] = F_kN
        r['p_carga'] = F_kN * 1000 / (A1 * eta) * 10          # bar
        r['p_carga_ret'] = F_kN * 1000 / (A3 * eta_r) * 10
    if Q:
        r['Q'] = Q
        r['v_av'] = Q / (6 * A1 / 100)        # m/s, con Q en L/min y A en cm2
        r['v_ret'] = Q / (6 * A3 / 100)
        r['v_reg'] = Q / (6 * Av / 100)
        r['Q_sale_av'] = Q / r['phi']         # sale del lado del vástago al avanzar
        r['Q_sale_ret'] = Q * r['phi']        # sale del lado del émbolo al retroceder
        if carrera:
            r['t_av'] = carrera / 1000 / r['v_av']
            r['t_ret'] = carrera / 1000 / r['v_ret']
            r['t_reg'] = carrera / 1000 / r['v_reg']
    return r


def lineas_cilindro(r, carrera=None):
    return lineas_fuerzas(r) + lineas_velocidades(r, carrera)


def lineas_fuerzas(r):
    L = ['Cilindro Ø%s/%s mm a %s bar' % (n(r['D'], 0), n(r['d'], 0), n(r['p'], 0)),
         '  A1 = π·D²/4 = %s cm² (émbolo); Av = π·d²/4 = %s cm² (vástago); A3 = A1 − Av = %s cm² (anular)'
         % (n(r['A1'] / 100, 2), n(r['Av'] / 100, 2), n(r['A3'] / 100, 2)),
         '  Relación de áreas φ = A1/A3 = %s (la nominal más cercana de ISO 7181 es %s)'
         % (n(r['phi'], 3), n(min(RELACIONES_ISO, key=lambda x: abs(x - r['phi'])), 2).rstrip('0').rstrip(',')),
         '  Fuerza de avance  F = p·A1·η = %s·0,1·%s·%s = %s kN (teórica %s kN = %s t)'
         % (n(r['p'], 0), n(r['A1'], 0), n(r['eta'], 2), n(r['F_av'], 2), n(r['F_av_teo'], 2), n(r['F_av_teo'] / G, 2)),
         '  Fuerza de retroceso F = p·A3·η = %s kN (teórica %s kN)' % (n(r['F_ret'], 2), n(r['F_ret_teo'], 2))]
    if 'F' in r:
        L.append('  Presión para %s kN (%s t): p = F/(A1·η) = %s/(%s·%s)·10 = %s bar%s'
                 % (n(r['F'], 2), n(r['F'] / G, 2), n(r['F'] * 1000, 0), n(r['A1'], 0), n(r['eta'], 2), n(r['p_carga'], 1),
                    '  → alcanza' if r['p_carga'] <= r['p'] else '  → NO ALCANZA con esta presión'))
    L.append('  Intensificación: si se estrangula la salida del lado del vástago sin carga, p3 = p·φ = %s bar (revisar juntas y mangueras)'
             % n(r['p_intens'], 1))
    return L


def lineas_velocidades(r, carrera=None):
    L = []
    if 'Q' in r:
        L.append('  Velocidad con Q = %s L/min: v = Q/(6·A[cm²]) → avance %s m/s, retroceso %s m/s'
                 % (n(r['Q'], 2), n(r['v_av'], 4), n(r['v_ret'], 4)))
        if 't_av' in r:
            L.append('  Tiempo de carrera (%s mm): t = s/v → avance %s s, retroceso %s s'
                     % (n(carrera, 0), n(r['t_av'], 2), n(r['t_ret'], 2)))
        L.append('  Caudal que sale del otro lado: al avanzar Q/φ = %s L/min; al retroceder Q·φ = %s L/min (dimensionar el retorno con este)'
                 % (n(r['Q_sale_av'], 1), n(r['Q_sale_ret'], 1)))
        L.append('  Regenerativo (el aceite del lado del vástago vuelve al émbolo): v = Q/Av = %s m/s%s; F = p·Av·η = %s kN'
                 % (n(r['v_reg'], 4), (', t = %s s' % n(r['t_reg'], 2)) if 't_reg' in r else '', n(r['F_reg'], 2)))
        vmax = max(r['v_av'], r['v_ret'])
        if vmax > V_MAX_JUNTAS:
            L.append('  ATENCIÓN: %s m/s supera 0,42 m/s (máximo de HANSA-FLEX con juntas estándar).' % n(vmax, 3))
        elif vmax > V_MAX_EXTREMOS:
            L.append('  Llega a %s m/s: más de 0,10 m/s al entrar en los extremos pide amortiguación o frenar antes (HANSA-FLEX).' % n(vmax, 3))
    return L


# ------------------------------------------------------------------------------------------ bomba y motor
def calc_bomba(p, n_rpm=1450.0, Vg=None, Q=None, etav=0.95, etat=0.85):
    positivo(p=p, n=n_rpm, etav=etav, etat=etat)
    if etat > etav:
        raise ValueError('el rendimiento total no puede ser mayor que el volumétrico')
    r = {'p': p, 'n': n_rpm, 'etav': etav, 'etat': etat, 'etahm': etat / etav}
    if Vg is None:
        positivo(Q=Q)
        r['Q_pedido'] = Q
        r['Vg_nec'] = Q * 1000 / (n_rpm * etav)
        Vg = siguiente(r['Vg_nec'], AZPF)
        r['Vg_azpf'] = Vg
        if Vg is None:
            Vg = r['Vg_nec']
    r['Vg'] = Vg
    r['Q'] = Vg * n_rpm * etav / 1000
    r['P_hid'] = p * r['Q'] / 600
    r['P_motor'] = r['P_hid'] / etat
    r['T'] = Vg * p / (20 * math.pi * r['etahm'])
    r['P_check'] = 2 * math.pi * r['T'] * n_rpm / 60000
    r['motor_kW'] = siguiente(r['P_motor'], MOTORES_KW)
    return r


def lineas_bomba(r):
    L = []
    if 'Vg_nec' in r:
        L.append('Cilindrada necesaria: Vg = Q·1000/(n·ηv) = %s·1000/(%s·%s) = %s cm³/rev'
                 % (n(r['Q_pedido'], 2), n(r['n'], 0), n(r['etav'], 2), n(r['Vg_nec'], 2)))
        if r.get('Vg_azpf'):
            L.append('  Tamaño comercial siguiente (ejemplo: Rexroth AZPF): %s cm³ (verificar su presión continua en el catálogo)' % n(r['Vg'], 1))
        else:
            L.append('  Más de 28 cm³: elegir del catálogo de bombas de pistones o de paletas (se sigue con la calculada).')
    L += ['Bomba de %s cm³ a %s rpm y %s bar (ηv = %s, ηt = %s, ηhm = ηt/ηv = %s)'
          % (n(r['Vg'], 1), n(r['n'], 0), n(r['p'], 0), n(r['etav'], 2), n(r['etat'], 2), n(r['etahm'], 3)),
          '  Caudal real: Q = Vg·n·ηv/1000 = %s L/min' % n(r['Q'], 2),
          '  Potencia hidráulica: P = p·Q/600 = %s·%s/600 = %s kW' % (n(r['p'], 0), n(r['Q'], 2), n(r['P_hid'], 2)),
          '  Potencia en el eje: P = p·Q/(600·ηt) = %s kW (con 2π·T·n/60000 da %s kW)' % (n(r['P_motor'], 2), n(r['P_check'], 2)),
          '  Torque en el eje: T = Vg·p/(20·π·ηhm) = %s N·m' % n(r['T'], 1)]
    if r['motor_kW']:
        L.append('  Motor eléctrico: potencia normalizada siguiente %s kW (serie de la skill calculos-ingenieria; ver catálogo)' % n(r['motor_kW'], 2).rstrip('0').rstrip(','))
    else:
        L.append('  Más de 75 kW: elegir del catálogo del fabricante del motor.')
    return L


def calc_motor(Vg=None, Q=None, dp=None, etav=0.95, etahm=0.90, n_rpm=None, T=None):
    positivo(dp=dp, etav=etav, etahm=etahm)
    r = {'dp': dp, 'etav': etav, 'etahm': etahm}
    if Vg is None:
        positivo(n=n_rpm, T=T)
        Vg = 20 * math.pi * T / (dp * etahm)
        Q = Vg * n_rpm / (1000 * etav)
        r.update({'Vg_nec': Vg, 'Q_nec': Q})
    positivo(Vg=Vg, Q=Q)
    r.update({'Vg': Vg, 'Q': Q})
    r['n'] = Q * 1000 * etav / Vg
    r['T'] = Vg * dp * etahm / (20 * math.pi)
    r['P'] = 2 * math.pi * r['T'] * r['n'] / 60000
    r['P_entrada'] = dp * Q / 600
    return r


def lineas_motor(r):
    L = []
    if 'Vg_nec' in r:
        L.append('Para T = %s N·m con Δp = %s bar: Vg = 20·π·T/(Δp·ηhm) = %s cm³/rev; caudal Q = Vg·n/(1000·ηv) = %s L/min'
                 % (n(r['T'], 1), n(r['dp'], 0), n(r['Vg_nec'], 1), n(r['Q_nec'], 2)))
    L += ['Motor hidráulico de %s cm³ con %s L/min y Δp = %s bar (ηv = %s, ηhm = %s)'
          % (n(r['Vg'], 1), n(r['Q'], 2), n(r['dp'], 0), n(r['etav'], 2), n(r['etahm'], 2)),
          '  Velocidad: n = Q·1000·ηv/Vg = %s rpm' % n(r['n'], 1),
          '  Torque: T = Vg·Δp·ηhm/(20·π) = %s N·m' % n(r['T'], 1),
          '  Potencia de salida: P = 2π·T·n/60000 = %s kW (entra p·Q/600 = %s kW)' % (n(r['P'], 2), n(r['P_entrada'], 2))]
    return L


# ------------------------------------------------------------------------------------------ aceite
def _z(nu):
    """ASTM D341: Z = ν + 0,7 + exp(−1,47 − 1,84·ν − 0,51·ν²)."""
    return nu + 0.7 + math.exp(-1.47 - 1.84 * nu - 0.51 * nu ** 2)


def walther(nu1, t1, nu2, t2):
    """Constantes A y B de log log Z = A − B·log T (T en K) por dos puntos."""
    positivo(nu1=nu1, nu2=nu2)
    T1, T2 = t1 + 273.15, t2 + 273.15
    y1, y2 = math.log10(math.log10(_z(nu1))), math.log10(math.log10(_z(nu2)))
    B = (y1 - y2) / (math.log10(T2) - math.log10(T1))
    return y1 + B * math.log10(T1), B


def nu_a(A, B, t):
    """Viscosidad cinemática [mm2/s] a t [°C]; invierte Z(ν) por bisección."""
    z = 10 ** (10 ** (A - B * math.log10(t + 273.15)))
    lo, hi = 1e-3, 1e8
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if _z(mid) > z:
            hi = mid
        else:
            lo = mid
    return math.sqrt(lo * hi)


def temp_para(A, B, nu):
    """Temperatura [°C] a la que el aceite tiene la viscosidad nu."""
    lo, hi = -50.0, 200.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if nu_a(A, B, mid) > nu:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def datos_aceite(vg=None, nu40=None, nu100=None, rho=None):
    if nu40 is None or nu100 is None:
        if vg not in ACEITES:
            raise ValueError('con --vg solo hay datos cargados para 32, 46 y 68; si no, dar --nu40 y --nu100 de la hoja técnica')
        nu40, nu100, rho_hoja = ACEITES[vg]
        rho = rho or rho_hoja
        origen = 'ISO VG %d, valores típicos de Mobil Nuto H %d' % (vg, vg)
    else:
        origen = 'hoja técnica del aceite'
    return nu40, nu100, (rho or 870.0), origen


def lineas_viscosidad(nu40, nu100, t, origen):
    A, B = walther(nu40, 40, nu100, 100)
    nu = nu_a(A, B, t)
    L = ['Aceite: ν40 = %s mm²/s y ν100 = %s mm²/s (%s)' % (n(nu40, 1), n(nu100, 1), origen),
         '  ASTM D341: log log Z = A − B·log T, con Z = ν + 0,7 + exp(−1,47 − 1,84·ν − 0,51·ν²) y T en K',
         '  A = %s; B = %s' % (n(A, 4), n(B, 4)),
         '  ν(%s °C) = %s mm²/s' % (n(t, 0), n(nu, 2)),
         '  Rangos de bombas: Rexroth A10VSO óptimo 16 a 36 mm²/s → de %s a %s °C con este aceite;'
         ' AZPF recomendado 20 a 100 mm²/s → de %s a %s °C'
         % (n(temp_para(A, B, 36), 0), n(temp_para(A, B, 16), 0), n(temp_para(A, B, 100), 0), n(temp_para(A, B, 20), 0))]
    for vg, (lo, hi) in ISO_VG.items():
        if lo <= nu40 <= hi:
            L.append('  ν40 dentro del grado ISO VG %d (%s a %s mm²/s, ISO 3448)' % (vg, n(lo, 1), n(hi, 1)))
    return nu, L


# ------------------------------------------------------------------------------------------ canerias
def velocidad_recomendada(tipo, p=None):
    if tipo == 'aspiracion':
        return V_ASPIRACION
    if tipo == 'retorno':
        return V_RETORNO
    if p is None:
        raise ValueError('para una línea de presión hace falta --p')
    # Ortwig (Hochschule Trier): <50 bar 4 m/s; 50-100: 4-5; 100-200: 5-6; >200: 6-7. Se toma el valor bajo.
    return 4.0 if p <= 100 else 5.0 if p <= 200 else 6.0


def calc_cano(Q, tipo, p=None, v=None):
    positivo(Q=Q)
    v = v or velocidad_recomendada(tipo, p)
    dmin = math.sqrt(4 * Q / 60000 / (math.pi * v)) * 1000
    elegida = None
    for m in MANGUERAS:
        if m[3] >= dmin and (p is None or tipo != 'presion' or m[4] >= p):
            elegida = m
            break
    r = {'Q': Q, 'tipo': tipo, 'v': v, 'dmin': dmin, 'manguera': elegida, 'p': p}
    if elegida:
        r['v_real'] = Q / 60000 / (math.pi * (elegida[3] / 1000) ** 2 / 4)
    return r


TIPOS = {'presion': 'presión', 'retorno': 'retorno', 'aspiracion': 'aspiración'}


def lineas_cano(r):
    L = ['Línea de %s con Q = %s L/min y v = %s m/s: d = √(4·Q/(π·v)) = %s mm'
         % (TIPOS[r['tipo']], n(r['Q'], 2), n(r['v'], 1), n(r['dmin'], 2))]
    m = r['manguera']
    if m:
        L.append('  Manguera EN 853 2SN DN %d (%s, %s): interior %s mm, %d bar de trabajo → v = %s m/s'
                 % (m[0], m[2], m[1], n(m[3], 1), m[4], n(r['v_real'], 2)))
        if r['tipo'] == 'presion' and r['p'] and m[4] < r['p']:
            L.append('  NO VERIFICA la presión de trabajo.')
    else:
        L.append('  Ninguna 2SN cumple (diámetro o presión): usar manguera espiralada (EN 856 4SP/4SH) o caño de acero; ver catálogo.')
    return L


def friccion(Re, d_mm=None, rug=None, laminar=64.0):
    if Re < 2300:
        return laminar / Re, 'laminar (Re < 2300): λ = %s/Re' % n(laminar, 0)
    if rug is None and Re <= 1e5:
        return 0.3164 / Re ** 0.25, 'turbulento, tubo liso: λ = 0,3164/Re^0,25 (Blasius)'
    e = (rug or 0.0) / d_mm
    lam = (1 / (-1.8 * math.log10((e / 3.7) ** 1.11 + 6.9 / Re))) ** 2
    return lam, 'turbulento: Haaland 1/√λ = −1,8·log((ε/d/3,7)^1,11 + 6,9/Re)'


def calc_perdida(Q, d, L, nu, rho=870.0, rug=None, zeta=0.0, laminar=64.0):
    positivo(Q=Q, d=d, L=L, nu=nu, rho=rho)
    A = math.pi * (d / 1000) ** 2 / 4
    v = Q / 60000 / A
    Re = v * (d / 1000) / (nu * 1e-6)
    lam, modo = friccion(Re, d, rug, laminar)
    dp_lin = lam * L / (d / 1000) * rho * v ** 2 / 2 / 1e5
    dp_loc = zeta * rho * v ** 2 / 2 / 1e5
    return {'v': v, 'Re': Re, 'lam': lam, 'modo': modo, 'dp_lin': dp_lin, 'dp_loc': dp_loc, 'dp': dp_lin + dp_loc,
            'Q': Q, 'd': d, 'L': L, 'nu': nu, 'rho': rho, 'zeta': zeta}


def lineas_perdida(r):
    L = ['Caño o manguera de %s mm y %s m, Q = %s L/min, ν = %s mm²/s, ρ = %s kg/m³'
         % (n(r['d'], 1), n(r['L'], 2), n(r['Q'], 2), n(r['nu'], 2), n(r['rho'], 0)),
         '  v = Q/A = %s m/s; Re = v·d/ν = %s → %s' % (n(r['v'], 3), n(r['Re'], 0), r['modo']),
         '  λ = %s; Δp = λ·(L/d)·ρ·v²/2 = %s bar' % (n(r['lam'], 4), n(r['dp_lin'], 3))]
    if r['zeta']:
        L.append('  Pérdidas localizadas: Δp = Σζ·ρ·v²/2 = %s·%s = %s bar' % (n(r['zeta'], 2), n(r['rho'] * r['v'] ** 2 / 2 / 1e5, 4), n(r['dp_loc'], 3)))
        L.append('  Total: %s bar' % n(r['dp'], 3))
    if 2300 <= r['Re'] < 4000:
        L.append('  Re entre 2300 y 4000: zona de transición; el cálculo turbulento queda del lado seguro.')
    if r['v'] > 8:
        L.append('  ATENCIÓN: %s m/s es demasiado (Atos y Hydroscand: no pasar de 8 m/s); agrandar el diámetro.' % n(r['v'], 1))
    return L


# ------------------------------------------------------------------------------------------ pandeo
def calc_pandeo(d, L, beta, F_kN, Re=355.0, nu=3.5, E=210000.0):
    positivo(d=d, L=L, beta=beta, F=F_kN, Re=Re, nu=nu, E=E)
    I = math.pi * d ** 4 / 64
    Lk = beta * L
    lam = 4 * Lk / d
    lam_g = math.pi * math.sqrt(E / (0.8 * Re))
    F_euler = math.pi ** 2 * E * I / (nu * Lk ** 2) / 1000
    sigma_lin = TETMAJER_A - TETMAJER_B * lam
    sigma_t = min(sigma_lin, Re)                 # nunca por encima de la fluencia
    F_tet = math.pi * d ** 2 / 4 * sigma_t / nu / 1000
    metodo = 'Euler' if lam > lam_g else 'Tetmajer'
    F_adm = F_euler if metodo == 'Euler' else F_tet
    # longitud libre máxima para F
    Lk_e = math.pi * math.sqrt(E * I / (nu * F_kN * 1000))
    sigma_nec = 4 * nu * F_kN * 1000 / (math.pi * d ** 2)    # tensión que hace falta con el coeficiente ν
    if 4 * Lk_e / d > lam_g:
        Lk_max, metodo_max = Lk_e, 'Euler'
    elif sigma_nec >= min(TETMAJER_A, Re):
        Lk_max, metodo_max = 0.0, 'ni con longitud cero: aumentar el vástago'
    else:
        Lk_max, metodo_max = (TETMAJER_A - sigma_nec) / TETMAJER_B * d / 4, 'Tetmajer'
    return {'d': d, 'L': L, 'beta': beta, 'F': F_kN, 'Re': Re, 'nu': nu, 'E': E, 'I': I, 'Lk': Lk, 'lam': lam,
            'lam_g': lam_g, 'F_euler': F_euler, 'F_tet': F_tet, 'metodo': metodo, 'F_adm': F_adm,
            'tope_Re': sigma_lin > Re, 'ok': F_kN <= F_adm, 'Lk_max': Lk_max, 'L_max': Lk_max / beta,
            'metodo_max': metodo_max}


def lineas_pandeo(r, caso=None):
    desc = ('caso %d de Euler, %s' % (caso, EULER[caso][1])) if caso else 'β = %s' % n(r['beta'], 2)
    L = ['Pandeo del vástago Ø%s mm, %s, F = %s kN, E = %s N/mm², Re = %s N/mm², ν = %s'
         % (n(r['d'], 0), desc, n(r['F'], 2), n(r['E'], 0), n(r['Re'], 0), n(r['nu'], 1)),
         '  I = π·d⁴/64 = %s mm⁴; Lk = β·L = %s·%s = %s mm' % (n(r['I'], 0), n(r['beta'], 2), n(r['L'], 0), n(r['Lk'], 0)),
         '  Esbeltez λ = 4·Lk/d = %s; límite λg = π·√(E/(0,8·Re)) = %s' % (n(r['lam'], 1), n(r['lam_g'], 1))]
    if r['metodo'] == 'Euler':
        L.append('  λ > λg → Euler: F adm = π²·E·I/(ν·Lk²) = %s kN' % n(r['F_euler'], 1))
    else:
        L.append('  λ ≤ λg → Euler no vale (daría %s kN); Tetmajer: F adm = π·d²·(335 − 0,62·λ)/(4·ν) = %s kN%s'
                 % (n(r['F_euler'], 1), n(r['F_tet'], 1), ' (tensión limitada a Re)' if r['tope_Re'] else ''))
    L.append('  %s: %s kN %s %s kN' % ('VERIFICA' if r['ok'] else 'NO VERIFICA', n(r['F'], 2), '≤' if r['ok'] else '>', n(r['F_adm'], 1)))
    if r['Lk_max'] > 0:
        L.append('  Longitud libre máxima para %s kN (%s): Lk = %s mm → L máx = Lk/β = %s mm'
                 % (n(r['F'], 2), r['metodo_max'], n(r['Lk_max'], 0), n(r['L_max'], 0)))
    else:
        L.append('  Para %s kN no alcanza ni con longitud cero: hace falta un vástago más grueso.' % n(r['F'], 2))
    if r['Re'] < 355:
        L.append('  AVISO: la recta de Tetmajer 335 − 0,62·λ es la del acero S355; con Re = %s N/mm² usar el diagrama del fabricante.'
                 % n(r['Re'], 0))
    return L


# ------------------------------------------------------------------------------------------ acumulador
def calc_acumulador(p1, p2, dV=None, V0=None, p0=None, patm=P_ATM):
    positivo(p1=p1, p2=p2)
    if p2 <= p1:
        raise ValueError('p2 (máxima) tiene que ser mayor que p1 (mínima)')
    p0 = p0 if p0 is not None else 0.9 * p1
    positivo(p0=p0)
    a0, a1, a2 = p0 + patm, p1 + patm, p2 + patm
    r = {'p0': p0, 'p1': p1, 'p2': p2, 'patm': patm}
    for nombre, k in (('iso', 1.0), ('adi', 1.4)):
        f = (a0 / a1) ** (1 / k) - (a0 / a2) ** (1 / k)
        r['f_' + nombre] = f
        if dV is not None:
            r['V0_' + nombre] = dV / f
        if V0 is not None:
            r['dV_' + nombre] = V0 * f
    r['dV'], r['V0'] = dV, V0
    if dV is not None:
        r['nominal'] = siguiente(max(r['V0_iso'], r['V0_adi']), HYDAC_L)
    r['ok_p0'] = p0 <= 0.9 * p1 + 1e-9
    r['relacion'] = p2 / p0
    return r


def lineas_acumulador(r):
    L = ['Acumulador: p0 = %s bar (precarga), p1 = %s bar (mínima), p2 = %s bar (máxima); absolutas: + %s bar'
         % (n(r['p0'], 1), n(r['p1'], 1), n(r['p2'], 1), n(r['patm'], 3)),
         '  Boyle: p0·V0ⁿ = p1·V1ⁿ = p2·V2ⁿ → ΔV = V1 − V2 = V0·((p0/p1)^(1/n) − (p0/p2)^(1/n))']
    if r['dV'] is not None:
        L.append('  Para ΔV = %s L: isotérmico (n = 1) V0 = %s L; adiabático (n = 1,4) V0 = %s L'
                 % (n(r['dV'], 2), n(r['V0_iso'], 2), n(r['V0_adi'], 2)))
        if r['nominal']:
            L.append('  Volumen nominal siguiente (vejiga HYDAC): %s L' % n(r['nominal'], 1).replace(',0', ''))
    if r['V0'] is not None:
        L.append('  Con V0 = %s L entrega ΔV = %s L (isotérmico) o %s L (adiabático)' % (n(r['V0'], 2), n(r['dV_iso'], 3), n(r['dV_adi'], 3)))
    L.append('  Precarga p0 ≤ 0,9·p1 (HYDAC): %s; relación p2/p0 = %s %s (máximo de la vejiga, HYDAC)'
             % ('cumple' if r['ok_p0'] else 'NO CUMPLE', n(r['relacion'], 2), '≤ 4: cumple' if r['relacion'] <= 4 else '> 4: NO CUMPLE'))
    return L


# ------------------------------------------------------------------------------------------ tanque y calor
def calc_tanque(Q, movil=False):
    positivo(Q=Q)
    a, b = (1.5, 2.0) if movil else (3.0, 5.0)
    return {'Q': Q, 'min': a * Q, 'max': b * Q, 'a': a, 'b': b, 'movil': movil}


def calc_calor(p=None, Q=None, etat=None, P_motor=None, P_util=0.0, area=None, dT=None, h=12.0):
    r = {'h': h}
    if P_motor is None:
        positivo(p=p, Q=Q)
        r['P_hid'] = p * Q / 600
        P_motor = r['P_hid'] / etat if etat else r['P_hid']
    r['P_motor'] = P_motor
    r['P_calor'] = P_motor - P_util
    if area and dT:
        r['P_disip'] = dT * area * h / 1000
    return r


# ------------------------------------------------------------------------------------------ demo
def cerca(x, y, tol):
    return abs(x - y) <= tol


def cmd_demo():
    ok = []

    def check(texto, cond):
        ok.append((texto, bool(cond)))

    print('=' * 100)
    print('PRENSA HIDRÁULICA DE 10 t')
    print('=' * 100)
    print('Datos: 10 t de fuerza de prensado; 160 bar en la válvula de alivio; carrera 300 mm; η del cilindro 0,95 al avanzar'
          ' y 0,92 al retroceder;\n  bomba de engranajes a 1450 rpm para unos 25 L/min (ηv = 0,95 y ηt = 0,85, supuestos: usar las curvas'
          ' del catálogo);\n  aceite ISO VG 46 (Mobil Nuto H 46) a 50 °C de trabajo y 10 °C en el arranque; manguera de presión de 3 m;'
          '\n  cilindro con brida delantera y puente guiado (caso 3, L = 450 mm), vástago con Re = 355 N/mm².\n')
    F = 10 * G                                        # kN
    print('a) Cilindro')
    Dmin, Dad = diametro_minimo(F, 160, ETA_AVANCE)
    print('  F = 10 t·9,80665 = %s kN; D mín = √(4·F/(π·p·η)) = √(4·%s/(π·16·0,95)) = %s mm → Ø%d (ISO 3320); vástagos ISO 6020-2: %s mm'
          % (n(F, 2), n(F * 1000, 0), n(Dmin, 2), Dad, ', '.join(str(x) for x in ISO6020_2[Dad])))
    check('D mín = %s mm (a mano 90,63) y se adopta Ø100' % n(Dmin, 2),
          cerca(Dmin, math.sqrt(4 * 98066.5 / (math.pi * 16 * 0.95)), 1e-9) and Dad == 100)
    print('  Se elige Ø100/70 (φ ≈ 2: retroceso al doble de velocidad y circuito regenerativo posible)')
    bomba = calc_bomba(160, 1450, Q=25, etav=0.95, etat=0.85)
    Q = bomba['Q']
    cil = calc_cilindro(100, 70, 160, F_kN=F, carrera=300, Q=Q)
    for linea in lineas_fuerzas(cil):
        print(linea)
    check('A1 = %s cm² y A3 = %s cm² (π·100²/4 y π·(100² − 70²)/4)' % (n(cil['A1'] / 100, 2), n(cil['A3'] / 100, 2)),
          cerca(cil['A1'], 7853.98, 0.01) and cerca(cil['A3'], 4005.53, 0.01))
    check('φ = %s (el catálogo Rexroth CDT3 da 1,96 para 100/70)' % n(cil['phi'], 3), cerca(cil['phi'], 1.96, 0.005))
    # Relaciones de áreas publicadas por Rexroth para la CDT3 (RE 17049/07.17), redondeadas a 2 decimales
    rexroth = {(25, 12): 1.3, (25, 18): 2.07, (32, 14): 1.25, (32, 22): 1.90, (40, 18): 1.25, (40, 22): 1.43,
               (40, 28): 1.96, (50, 22): 1.25, (50, 28): 1.46, (50, 36): 2.08, (63, 28): 1.25, (63, 36): 1.48,
               (63, 45): 2.04, (80, 36): 1.25, (80, 45): 1.46, (80, 56): 1.96, (100, 45): 1.25, (100, 56): 1.46,
               (100, 70): 1.96, (125, 56): 1.25, (125, 70): 1.46, (125, 90): 2.08, (160, 70): 1.25, (160, 110): 1.90,
               (200, 90): 1.25, (200, 140): 1.96}
    dif = {(D, d): areas(D, d)[0] / areas(D, d)[2] - phi for (D, d), phi in rexroth.items()}
    nominales = sorted(k for k, x in dif.items() if abs(x) >= 0.01)
    check('las %d relaciones φ de la CDT3 de Rexroth se reproducen con menos de 0,01; en %s el catálogo pone el nominal 1,25 (da %s)'
          % (len(rexroth), ' y '.join('%d/%d' % k for k in nominales), n(areas(*nominales[0])[0] / areas(*nominales[0])[2], 3)),
          all(abs(x) < 0.015 for x in dif.values()) and all(rexroth[k] == 1.25 for k in nominales))
    check('presión para 10 t = %s bar (98 066,5/(7854·0,95)·10)' % n(cil['p_carga'], 1),
          cerca(cil['p_carga'], 98066.5 / (math.pi * 2500 * 0.95) * 10, 1e-9) and cil['p_carga'] < 160)
    check('fuerza útil a 160 bar = %s kN ≥ 98,07 kN' % n(cil['F_av'], 2), cerca(cil['F_av'], 119.38, 0.01) and cil['F_av'] >= F)

    print('\nb) Bomba y motor eléctrico (caudal buscado 25 L/min; ηv = 0,95 y ηt = 0,85 supuestos: tomar las curvas del catálogo)')
    for linea in lineas_bomba(bomba):
        print(linea)
    check('cilindrada %s cm³ → 19 cm³ y Q real %s L/min' % (n(bomba['Vg_nec'], 2), n(Q, 2)),
          cerca(bomba['Vg_nec'], 25000 / (1450 * 0.95), 1e-9) and bomba['Vg'] == 19 and cerca(Q, 19 * 1450 * 0.95 / 1000, 1e-9))
    check('potencia en el eje %s kW por p·Q/(600·ηt) y por 2π·T·n/60000' % n(bomba['P_motor'], 2),
          cerca(bomba['P_motor'], bomba['P_check'], 1e-9) and cerca(bomba['P_motor'], 8.211, 0.001))
    check('motor eléctrico normalizado de 11 kW', bomba['motor_kW'] == 11)

    print('\nc) Velocidades y tiempos con el caudal real de la bomba')
    for linea in lineas_velocidades(cil, 300):
        print(linea)
    check('avance %s m/s en %s s, retroceso %s m/s en %s s, regenerativo %s m/s'
          % (n(cil['v_av'], 4), n(cil['t_av'], 2), n(cil['v_ret'], 4), n(cil['t_ret'], 2), n(cil['v_reg'], 4)),
          cerca(cil['v_av'] * cil['A1'] * 1e-6 * 60000, Q, 1e-9) and cerca(cil['v_ret'] * cil['A3'] * 1e-6 * 60000, Q, 1e-9)
          and cerca(cil['v_reg'] * cil['Av'] * 1e-6 * 60000, Q, 1e-9) and cerca(cil['t_av'], 5.40, 0.01))
    check('caudal que vuelve al retroceder Q·φ = %s L/min' % n(cil['Q_sale_ret'], 2), cerca(cil['Q_sale_ret'], Q * 7853.98 / 4005.53, 0.01))
    check('intensificación p·φ = %s bar' % n(cil['p_intens'], 1), cerca(cil['p_intens'], 313.7, 0.1))

    print('\nd) Aceite ISO VG 46 a la temperatura de trabajo')
    nu40, nu100, rho, origen = datos_aceite(46)
    nu50, Lv = lineas_viscosidad(nu40, nu100, 50, origen)
    for linea in Lv:
        print(linea)
    A, B = walther(nu40, 40, nu100, 100)
    nu10 = nu_a(A, B, 10)
    print('  En el arranque en frío, a 10 °C: ν = %s mm²/s' % n(nu10, 1))
    check('la ecuación vuelve a 44,0 y 6,6 mm²/s en los puntos de partida', cerca(nu_a(A, B, 40), 44.0, 1e-6) and cerca(nu_a(A, B, 100), 6.6, 1e-6))
    At, Bt = walther(46, 40, 6.8, 100)
    nu0 = nu_a(At, Bt, 0)
    check('Shell Tellus S3 M 46 a 0 °C: calculado %s mm²/s, hoja técnica 565 (± 5 %%)' % n(nu0, 0), abs(nu0 / 565 - 1) < 0.05)
    check('ν(50 °C) = %s mm²/s y ν(10 °C) = %s mm²/s' % (n(nu50, 2), n(nu10, 1)), cerca(nu50, 28.76, 0.01) and cerca(nu10, 247.3, 0.1))

    print('\ne) Mangueras')
    lineas = [('presion', Q, 160), ('presion', cil['Q_sale_ret'], 160), ('retorno', cil['Q_sale_ret'], None), ('aspiracion', Q, None)]
    nombres = ['bomba–válvula y línea B (lado del vástago)', 'línea A (lado del émbolo: en el retroceso devuelve Q·φ)',
               'retorno válvula–tanque (en el retroceso pasa Q·φ)', 'aspiración']
    dn = []
    for (tipo, q, p), nombre in zip(lineas, nombres):
        r = calc_cano(q, tipo, p)
        print('  ' + nombre + ':')
        for linea in lineas_cano(r):
            print('  ' + linea)
        dn.append(r['manguera'][0])
    check('mangueras DN %s' % ' / '.join(str(x) for x in dn), dn == [12, 16, 19, 25])

    print('\nf) Pérdida de carga en la manguera de presión (DN 12, 13,0 mm, 3 m)')
    p50 = calc_perdida(Q, 13.0, 3.0, nu50, rho)
    for linea in lineas_perdida(p50):
        print(linea)
    hp = 128 * (nu50 * 1e-6 * rho) * 3.0 * (Q / 60000) / (math.pi * 0.013 ** 4) / 1e5
    check('Δp laminar %s bar = Hagen-Poiseuille 128·μ·L·Q/(π·d⁴) = %s bar' % (n(p50['dp'], 3), n(hp, 3)),
          p50['Re'] < 2300 and cerca(p50['dp'], hp, 1e-9))
    p10 = calc_perdida(Q, 13.0, 3.0, nu10, rho)
    print('  En frío (10 °C): Re = %s, Δp = %s bar: %s veces más' % (n(p10['Re'], 0), n(p10['dp'], 2), n(p10['dp'] / p50['dp'], 1)))
    check('en frío la pérdida crece con la viscosidad (laminar): %s bar' % n(p10['dp'], 2), cerca(p10['dp'] / p50['dp'], nu10 / nu50, 1e-9))
    asp = calc_perdida(Q, 26.0, 0.5, nu10, rho)
    p_ent = P_ATM - asp['dp']
    print('  Aspiración DN 25 de 0,5 m en frío: Δp = %s bar → entrada de la bomba a %s bar absolutos (AZPF pide ≥ 0,7)'
          % (n(asp['dp'], 3), n(p_ent, 2)))
    check('presión absoluta en la aspiración en frío %s bar ≥ 0,7 bar' % n(p_ent, 2), p_ent >= 0.7)
    lam_b, _ = friccion(1e4)
    lam_h, _ = friccion(1e4, 13.0, 0.0)
    check('a Re = 10 000 Blasius (%s) y Haaland liso (%s) difieren menos de 5 %%' % (n(lam_b, 4), n(lam_h, 4)), abs(lam_b / lam_h - 1) < 0.05)

    print('\ng) Pandeo (brida delantera y puente guiado: caso 3, L = 450 mm; Re = 355 N/mm²; ν = 3,5)')
    F_max = cil['F_av_teo']
    print('  Se verifica con la fuerza máxima del cilindro: p·A1 = %s kN (presión de la válvula de alivio)' % n(F_max, 2))
    pz = calc_pandeo(70, 450, EULER[3][0], F_max, Re=355.0)
    for linea in lineas_pandeo(pz, 3):
        print(linea)
    check('λ = %s ≤ λg = %s → Tetmajer: %s kN ≥ %s kN' % (n(pz['lam'], 1), n(pz['lam_g'], 1), n(pz['F_adm'], 1), n(F_max, 1)),
          pz['metodo'] == 'Tetmajer' and pz['ok'] and cerca(pz['F_adm'], math.pi * 4900 / 4 * (335 - 0.62 * 18) / 3.5 / 1000, 1e-6))
    I = math.pi * 70 ** 4 / 64
    check('longitud máxima por Euler %s mm: ahí F adm = F' % n(pz['L_max'], 0),
          pz['metodo_max'] == 'Euler' and cerca(math.pi ** 2 * 210000 * I / (3.5 * pz['Lk_max'] ** 2) / 1000, F_max, 1e-6))
    lg = pz['lam_g']
    check('en λg la tensión de Euler es 0,8·Re y la de Tetmajer difiere menos de 1 %',
          cerca(math.pi ** 2 * 210000 / lg ** 2, 0.8 * 355, 1e-9) and abs((335 - 0.62 * lg) / (0.8 * 355) - 1) < 0.01)

    print('\nh) Acumulador para mantener la presión 2 min con la bomba descargada (fugas 0,2 L/min → ΔV = 0,4 L entre 140 y 160 bar)')
    ac = calc_acumulador(140, 160, dV=0.4)
    for linea in lineas_acumulador(ac):
        print(linea)
    vuelta = calc_acumulador(140, 160, V0=ac['V0_iso'])
    check('V0 = %s L (isotérmico) y %s L (adiabático) → 5 L; con V0 vuelve ΔV = 0,4 L' % (n(ac['V0_iso'], 2), n(ac['V0_adi'], 2)),
          cerca(vuelta['dV_iso'], 0.4, 1e-12) and ac['V0_adi'] > ac['V0_iso'] and ac['nominal'] == 5 and ac['ok_p0'])
    print('  A 140 bar el cilindro todavía hace %s kN: sigue alcanzando las 10 t' % n(140 * 0.1 * cil['A1'] * ETA_AVANCE / 1000, 1))
    check('a 140 bar la fuerza útil sigue siendo ≥ 10 t', 140 * 0.1 * cil['A1'] * ETA_AVANCE / 1000 >= F)

    print('\ni) Tanque y calor')
    tq = calc_tanque(Q)
    print('  Tanque de instalación fija: V = 3 a 5 veces el caudal por minuto = %s a %s L, más 10 %% de cámara de aire'
          % (n(tq['min'], 0), n(tq['max'], 0)))
    cl = calc_calor(160, Q, 0.85, area=1.14, dT=25, h=12)
    print('  Si la bomba descarga por la válvula de alivio a 160 bar: p·Q/600 = %s kW de potencia hidráulica sin trabajo útil;'
          ' toda la potencia del eje (%s kW) termina como calor' % (n(cl['P_hid'], 2), n(cl['P_calor'], 2)))
    print('  Tanque de 0,6 × 0,4 × 0,45 m (108 L): paredes y tapa 1,14 m²; P = h·A·ΔT = 12·1,14·25/1000 = %s kW'
          % n(cl['P_disip'], 3))
    print('  → el tanque disipa %s veces menos de lo que se genera: centro tándem o descarga de la bomba, acumulador o intercambiador'
          % n(cl['P_calor'] / cl['P_disip'], 0))
    check('tanque de %s a %s L y calor %s kW contra %s kW disipados' % (n(tq['min'], 1), n(tq['max'], 1), n(cl['P_calor'], 2), n(cl['P_disip'], 3)),
          cerca(tq['min'], 3 * Q, 1e-9) and cerca(cl['P_calor'], bomba['P_motor'], 1e-9) and cerca(cl['P_disip'], 0.342, 1e-9))

    print('\nj) Motor hidráulico (otro ejemplo: 80 cm³ con el caudal de la bomba y Δp = 140 bar, ηv = 0,95, ηhm = 0,90)')
    mo = calc_motor(80, Q, 140, 0.95, 0.90)
    for linea in lineas_motor(mo):
        print(linea)
    check('motor: n = %s rpm, T = %s N·m, P = %s kW = p·Q/600·ηv·ηhm' % (n(mo['n'], 1), n(mo['T'], 1), n(mo['P'], 2)),
          cerca(mo['P'], mo['P_entrada'] * 0.95 * 0.90, 1e-9) and cerca(mo['n'], 310.8, 0.05))
    mo2 = calc_motor(None, None, 140, 0.95, 0.90, n_rpm=mo['n'], T=mo['T'])
    check('para ese torque y esa velocidad el cálculo inverso vuelve a 80 cm³', cerca(mo2['Vg'], 80, 1e-9) and cerca(mo2['Q'], Q, 1e-9))

    print('\nVerificación')
    for texto, bien in ok:
        print('  %s %s' % ('ok ' if bien else 'MAL', texto))
    todo = all(b for _, b in ok)
    print('DEMO %s (%d controles)' % ('OK' if todo else 'FALLO', len(ok)))
    return 0 if todo else 1


# ------------------------------------------------------------------------------------------ CLI
def construir_parser():
    ap = argparse.ArgumentParser(prog='oleohidraulica.py', description=__doc__, add_help=False,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('-h', '--help', action='help', help='muestra esta ayuda y termina')
    sp = ap.add_subparsers(dest='cmd', title='comandos')
    nuevo = sp.add_parser

    def sub(nombre, help=''):   # mismo nombre de argumento que argparse
        p = nuevo(nombre, help=help, description=help, add_help=False)
        p.add_argument('-h', '--help', action='help', help='muestra esta ayuda y termina')
        return p

    sp.add_parser = sub

    c = sp.add_parser('cilindro', help='fuerzas, presión, velocidades, tiempos y diámetro normalizado')
    c.add_argument('--p', type=float, required=True, help='presión de trabajo [bar]')
    c.add_argument('--D', type=float, help='diámetro del émbolo [mm] (sin --D se calcula con la fuerza)')
    c.add_argument('--d', type=float, help='diámetro del vástago [mm]')
    c.add_argument('--F', type=float, help='fuerza pedida [kN]')
    c.add_argument('--t', type=float, help='carga en toneladas (se pasa a kN con g = 9,80665)')
    c.add_argument('--carrera', type=float, help='carrera [mm]')
    c.add_argument('--Q', type=float, help='caudal de la bomba [L/min]')
    c.add_argument('--eta', type=float, default=ETA_AVANCE, help='rendimiento en el avance (0,95)')
    c.add_argument('--eta-ret', type=float, default=ETA_RETROCESO, help='rendimiento en el retroceso (0,92)')

    b = sp.add_parser('bomba', help='cilindrada, caudal, potencia, torque y motor eléctrico')
    b.add_argument('--p', type=float, required=True, help='presión máxima (la de la válvula de alivio) [bar]')
    b.add_argument('--Vg', type=float, help='cilindrada [cm³/rev]')
    b.add_argument('--Q', type=float, help='caudal buscado [L/min] (calcula la cilindrada)')
    b.add_argument('--n', type=float, default=1450.0, help='velocidad del motor [rpm] (1450, 4 polos a 50 Hz)')
    b.add_argument('--etav', type=float, default=0.95, help='rendimiento volumétrico (0,95; ver catálogo)')
    b.add_argument('--etat', type=float, default=0.85, help='rendimiento total (0,85; ver catálogo)')

    m = sp.add_parser('motor', help='motor hidráulico: velocidad, torque y potencia')
    m.add_argument('--dp', type=float, required=True, help='diferencia de presión entre entrada y salida [bar]')
    m.add_argument('--Vg', type=float, help='cilindrada [cm³/rev]')
    m.add_argument('--Q', type=float, help='caudal que recibe [L/min]')
    m.add_argument('--n', type=float, help='velocidad pedida [rpm] (con --T calcula Vg y Q)')
    m.add_argument('--T', type=float, help='torque pedido [N·m]')
    m.add_argument('--etav', type=float, default=0.95, help='rendimiento volumétrico (0,95)')
    m.add_argument('--etahm', type=float, default=0.90, help='rendimiento hidromecánico (0,90)')

    v = sp.add_parser('viscosidad', help='viscosidad a otra temperatura (ASTM D341)')
    v.add_argument('--temp', type=float, required=True, help='temperatura [°C]')
    v.add_argument('--vg', type=int, help='grado ISO VG con datos cargados: 32, 46 o 68')
    v.add_argument('--nu40', type=float, help='viscosidad a 40 °C de la hoja técnica [mm²/s]')
    v.add_argument('--nu100', type=float, help='viscosidad a 100 °C de la hoja técnica [mm²/s]')

    k = sp.add_parser('cano', help='diámetro interior mínimo y manguera EN 853 2SN')
    k.add_argument('--Q', type=float, required=True, help='caudal que pasa por esa línea [L/min]')
    k.add_argument('--tipo', choices=['presion', 'retorno', 'aspiracion'], required=True, help='tipo de línea')
    k.add_argument('--p', type=float, help='presión de trabajo [bar] (obligatoria en presión)')
    k.add_argument('--v', type=float, help='velocidad elegida [m/s] (si no, la recomendada)')

    q = sp.add_parser('perdida', help='pérdida de carga por Darcy-Weisbach')
    q.add_argument('--Q', type=float, required=True, help='caudal [L/min]')
    q.add_argument('--d', type=float, required=True, help='diámetro interior [mm]')
    q.add_argument('--L', type=float, required=True, help='largo [m]')
    q.add_argument('--nu', type=float, help='viscosidad cinemática a la temperatura de trabajo [mm²/s]')
    q.add_argument('--vg', type=int, help='grado ISO VG con datos cargados (32, 46, 68), con --temp')
    q.add_argument('--nu40', type=float, help='ν a 40 °C [mm²/s], con --nu100 y --temp')
    q.add_argument('--nu100', type=float, help='ν a 100 °C [mm²/s]')
    q.add_argument('--temp', type=float, help='temperatura del aceite [°C]')
    q.add_argument('--rho', type=float, help='densidad [kg/m³] (la de la hoja técnica; 870 si no hay)')
    q.add_argument('--rugosidad', type=float, help='rugosidad absoluta [mm] (si se da, Haaland)')
    q.add_argument('--zeta', type=float, default=0.0, help='suma de coeficientes de pérdidas localizadas (del fabricante)')
    q.add_argument('--laminar', type=float, default=64.0, help='constante laminar λ = C/Re (64)')

    z = sp.add_parser('pandeo', help='pandeo del vástago (Euler o Tetmajer)')
    z.add_argument('--d', type=float, required=True, help='diámetro del vástago [mm]')
    z.add_argument('--L', type=float, required=True, help='longitud de pandeo con el vástago afuera, sin el factor del caso [mm]')
    z.add_argument('--caso', type=int, choices=[1, 2, 3, 4], default=2,
                   help='1 empotrado-libre (Lk = 2·L), 2 articulado-articulado (L, defecto), 3 empotrado-articulado guiado (0,7·L), 4 empotrado-empotrado (0,5·L)')
    z.add_argument('--F', type=float, help='fuerza de compresión [kN]')
    z.add_argument('--D', type=float, help='diámetro del émbolo [mm], con --p: F = p·A1')
    z.add_argument('--p', type=float, help='presión máxima (válvula de alivio) [bar]')
    z.add_argument('--Re', type=float, default=355.0, help='límite de fluencia del vástago [N/mm²] (355)')
    z.add_argument('--seguridad', type=float, default=3.5, help='coeficiente de seguridad ν (3,5)')
    z.add_argument('--E', type=float, default=210000.0, help='módulo de elasticidad [N/mm²] (210 000)')

    a = sp.add_parser('acumulador', help='volumen de un acumulador (Boyle)')
    a.add_argument('--p1', type=float, required=True, help='presión mínima de trabajo [bar]')
    a.add_argument('--p2', type=float, required=True, help='presión máxima de trabajo [bar]')
    a.add_argument('--dV', type=float, help='volumen de aceite que tiene que entregar [L]')
    a.add_argument('--V0', type=float, help='volumen del acumulador [L] (calcula lo que entrega)')
    a.add_argument('--p0', type=float, help='presión de precarga [bar] (0,9·p1)')

    t = sp.add_parser('tanque', help='volumen orientativo del tanque')
    t.add_argument('--Q', type=float, required=True, help='caudal de la bomba [L/min]')
    t.add_argument('--movil', action='store_true', help='equipo móvil (1,5 a 2 veces el caudal)')

    h = sp.add_parser('calor', help='potencia que se vuelve calor y disipación del tanque')
    h.add_argument('--p', type=float, help='presión a la que descarga la bomba [bar]')
    h.add_argument('--Q', type=float, help='caudal [L/min]')
    h.add_argument('--etat', type=float, default=0.85, help='rendimiento total de la bomba (0,85)')
    h.add_argument('--Pmotor', type=float, help='potencia en el eje [kW] (en lugar de --p y --Q)')
    h.add_argument('--Putil', type=float, default=0.0, help='potencia útil que sale como trabajo [kW]')
    h.add_argument('--area', type=float, help='superficie del tanque que disipa (paredes y tapa) [m²]')
    h.add_argument('--dT', type=float, help='diferencia entre aceite y ambiente [K]')
    h.add_argument('--ventilacion', choices=['normal', 'forzada', 'mala'], default='normal', help='h = 12, 24 o 6 W/(m²·K)')

    sp.add_parser('demo', help='ejemplo resuelto de la prensa de 10 t con verificación')
    return ap


def main(argv=None):
    ap = construir_parser()
    a = ap.parse_args(argv)
    try:
        if a.cmd == 'demo':
            return cmd_demo()
        if a.cmd == 'cilindro':
            F = a.F if a.F else (a.t * G if a.t else None)
            L = []
            if a.D is None:
                if not F:
                    ap.error('falta --D o la fuerza (--F en kN o --t en toneladas)')
                Dmin, Dad = diametro_minimo(F, a.p, a.eta)
                L.append('Para %s kN (%s t) a %s bar con η = %s: D mín = √(4·F/(π·p·η)) = %s mm → Ø%s (ISO 3320)'
                         % (n(F, 2), n(F / G, 2), n(a.p, 0), n(a.eta, 2), n(Dmin, 2), Dad if Dad else 'más de 500'))
                if Dad in ISO6020_2:
                    L.append('  Vástagos de la serie ISO 6020-2 (160 bar) para Ø%d:' % Dad)
                    for d in ISO6020_2[Dad]:
                        r = calc_cilindro(Dad, d, a.p, F, a.carrera, a.Q, a.eta, a.eta_ret)
                        extra = (', v avance %s m/s, v retroceso %s m/s' % (n(r['v_av'], 3), n(r['v_ret'], 3))) if a.Q else ''
                        L.append('    Ø%d: φ = %s, F retroceso útil %s kN%s' % (d, n(r['phi'], 2), n(r['F_ret'], 1), extra))
                    L.append('  Elegir el vástago por pandeo (comando pandeo) y velocidad de retroceso, y repetir con --D y --d.')
                elif Dad:
                    L.append('  Para Ø%d, vástago y presión nominal del catálogo (ISO 6022 o del fabricante).' % Dad)
                if a.d is None or not Dad:
                    print('\n'.join(L))
                    return 0
                a.D = Dad
            if a.d is None:
                ap.error('falta --d (diámetro del vástago)')
            r = calc_cilindro(a.D, a.d, a.p, F, a.carrera, a.Q, a.eta, a.eta_ret)
            L += lineas_cilindro(r, a.carrera)
        elif a.cmd == 'bomba':
            if a.Vg is None and a.Q is None:
                ap.error('falta --Vg o --Q')
            L = lineas_bomba(calc_bomba(a.p, a.n, a.Vg, a.Q, a.etav, a.etat))
        elif a.cmd == 'motor':
            if a.Vg is None and (a.n is None or a.T is None):
                ap.error('dar --Vg y --Q, o --n y --T')
            L = lineas_motor(calc_motor(a.Vg, a.Q, a.dp, a.etav, a.etahm, a.n, a.T))
        elif a.cmd == 'viscosidad':
            nu40, nu100, _, origen = datos_aceite(a.vg, a.nu40, a.nu100)
            _, L = lineas_viscosidad(nu40, nu100, a.temp, origen)
        elif a.cmd == 'cano':
            L = lineas_cano(calc_cano(a.Q, a.tipo, a.p, a.v))
        elif a.cmd == 'perdida':
            L = []
            rho = a.rho
            nu = a.nu
            if nu is None:
                if a.temp is None:
                    ap.error('dar --nu, o --temp con --vg o con --nu40 y --nu100')
                nu40, nu100, rho, origen = datos_aceite(a.vg, a.nu40, a.nu100, a.rho)
                nu, L = lineas_viscosidad(nu40, nu100, a.temp, origen)
            L += lineas_perdida(calc_perdida(a.Q, a.d, a.L, nu, rho or 870.0, a.rugosidad, a.zeta, a.laminar))
        elif a.cmd == 'pandeo':
            F = a.F
            if F is None:
                if a.D is None or a.p is None:
                    ap.error('dar --F o --D y --p')
                F = a.p * 0.1 * math.pi * a.D ** 2 / 4 / 1000
            L = lineas_pandeo(calc_pandeo(a.d, a.L, EULER[a.caso][0], F, a.Re, a.seguridad, a.E), a.caso)
        elif a.cmd == 'acumulador':
            if a.dV is None and a.V0 is None:
                ap.error('falta --dV o --V0')
            L = lineas_acumulador(calc_acumulador(a.p1, a.p2, a.dV, a.V0, a.p0))
        elif a.cmd == 'tanque':
            r = calc_tanque(a.Q, a.movil)
            L = ['Tanque %s: V = %s a %s veces el caudal por minuto = %s a %s L, más 10 %% de cámara de aire (Casey, Power & Motion)'
                 % ('de equipo móvil' if r['movil'] else 'de instalación fija', n(r['a'], 1), n(r['b'], 1), n(r['min'], 0), n(r['max'], 0))]
        elif a.cmd == 'calor':
            if a.Pmotor is None and (a.p is None or a.Q is None):
                ap.error('dar --p y --Q, o --Pmotor')
            r = calc_calor(a.p, a.Q, a.etat, a.Pmotor, a.Putil, a.area, a.dT, H_TANQUE[a.ventilacion])
            L = []
            if 'P_hid' in r:
                L.append('Potencia hidráulica p·Q/600 = %s kW; en el eje %s kW' % (n(r['P_hid'], 2), n(r['P_motor'], 2)))
            L.append('Calor = potencia en el eje − potencia útil = %s kW' % n(r['P_calor'], 2))
            if 'P_disip' in r:
                L.append('Disipa el tanque: P = h·A·ΔT = %s·%s·%s/1000 = %s kW → %s'
                         % (n(r['h'], 0), n(a.area, 2), n(a.dT, 0), n(r['P_disip'], 3),
                            'alcanza' if r['P_disip'] >= r['P_calor'] else 'falta un intercambiador de %s kW' % n(r['P_calor'] - r['P_disip'], 2)))
        else:
            ap.print_help()
            return 0
    except ValueError as ex:
        print('oleohidraulica.py: %s' % ex, file=sys.stderr)
        return 2
    print('\n'.join(L))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
