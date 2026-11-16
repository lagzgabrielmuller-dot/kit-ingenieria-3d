#!/usr/bin/env python3
"""transporte.py - equipos de maniobra y transporte (solo biblioteca estándar).

Cada comando imprime fórmula, reemplazo y resultado con coma decimal, listo para una memoria de cálculo.
Unidades: mm (anchos y diámetros), m, m/s, rpm, kg/m³, kg (las cargas se dan como masa), kN y kW; g = 9,81 m/s².
  cinta         capacidad por la sección de carga (CEMA o DIN 22101), potencia en el tambor y tensiones T1 y T2
  tornillo      transportador a tornillo sinfín: capacidad, rpm necesarias y potencia (CEMA 350, datos de KWS)
  cangilones    elevador de cangilones: capacidad, potencia de elevación y tipo de descarga en la cabeza
  aparejo       aparejo o polipasto: rendimiento y fuerza en el tiro
  cable         cable de acero: carga de rotura mínima requerida, diámetro sugerido y D/d de tambor y poleas
  eslinga       eslinga de 1 a 4 ramales: tensión por ramal y cadena de grado 8 sugerida
  autoelevador  capacidad con otro centro de carga (momento respecto del eje delantero)
  grua          grupo de clasificación (ISO 4301-1) y cargas en las ruedas de un puente grúa
  demo          reproduce los ejemplos del SKILL.md y de las fuentes; termina en DEMO OK
Ayuda de cada comando: python transporte.py <comando> --help
Los valores marcados "(verificar)" en la salida no se pudieron confirmar con la norma: revisarlos antes de entregar.
"""
import argparse
import math
import sys

G = 9.81                        # m/s²
FT = 0.3048                     # m por pie (exacto)
PULG = 25.4                     # mm por pulgada (exacto)
FT3 = FT ** 3                   # m³ por ft³
LB = 0.45359237                 # kg por libra (exacto)
LB_FT3 = LB / FT3               # kg/m³ por lb/ft³ (16,018)
HP_KW = 550 * FT * LB * 9.80665 / 1000   # kW por hp mecánico (0,7457)

# ------------------------------------------------------------------------------------------ datos de cintas
L3_TERNA = {400: 160, 500: 200, 650: 250, 800: 315, 1000: 380, 1200: 465, 1400: 530, 1600: 600,
            1800: 670, 2000: 750, 2200: 800, 2400: 900}    # mm, rodillo central de la terna (DIN 22107, verificar)
K_INCLINACION = [(0, 1.00), (2, 1.00), (4, 0.99), (6, 0.98), (8, 0.97), (10, 0.95), (12, 0.93), (14, 0.91),
                 (16, 0.89), (18, 0.85), (20, 0.81), (21, 0.78), (22, 0.76), (23, 0.73), (24, 0.71), (25, 0.68),
                 (26, 0.66), (27, 0.64), (28, 0.61), (29, 0.59), (30, 0.56)]   # IS 11592:2000, tabla 9
C_LARGO = [(80, 1.92), (100, 1.78), (150, 1.58), (200, 1.45), (300, 1.31), (400, 1.25), (500, 1.20), (600, 1.17),
           (700, 1.14), (800, 1.12), (900, 1.10), (1000, 1.09), (1500, 1.06), (2000, 1.05), (2500, 1.04),
           (5000, 1.03)]    # coeficiente C de resistencias secundarias, DIN 22101 / ISO 5048 (verificar)
VEL_MAX = [(0, (2.50, 2.30, 2.00, 1.65, 1.45)), (600, (3.00, 2.75, 2.38, 2.00, 1.75)),
           (750, (3.50, 3.20, 2.75, 2.35, 2.05)), (950, (4.00, 3.65, 3.15, 2.65, 2.35)),
           (1200, (4.50, 4.12, 3.55, 3.00, 2.62))]   # IS 11592:2000, tabla 6: m/s por ancho y factor de velocidad
MU_DISENO = {'revestido': 0.35, 'desnudo': 0.25}      # IS 11592:2000, tabla 20
POT_IEC = [0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3, 4, 5.5, 7.5, 11, 15, 18.5, 22, 30, 37, 45, 55, 75, 90, 110, 132,
           160, 200, 250, 315]   # kW, potencias normalizadas de motores (IEC)

# ------------------------------------------------------------------------------------------ datos de tornillos (KWS, según CEMA 350)
FD_CEMA = {4: 12, 6: 18, 9: 31, 12: 55, 14: 78, 16: 106, 18: 135, 20: 165, 24: 235, 30: 377, 36: 549}
FB_CEMA = {'rodamiento': 1.0, 'bronce': 1.7, 'plastico': 2.0, 'hierro': 4.4}   # cojinetes intermedios
LLENADO = {'15': 0.15, '30A': 0.30, '30B': 0.30, '45': 0.45}
ORDEN_LL = ('15', '30A', '30B', '45')
RPM_MAX = {6: (60, 120, 60, 165), 9: (55, 100, 55, 155), 12: (50, 90, 50, 145), 14: (50, 85, 50, 140),
           16: (45, 80, 45, 130)}   # rpm máximas por diámetro [in] y llenado (KWS)
CAP_1RPM_KWS = {6: (0.8, 1.5, 1.5, 2.2), 9: (2.7, 5.5, 5.5, 8.2), 12: (6.5, 12.9, 12.9, 19.4),
                14: (10.4, 20.8, 20.8, 31.2), 16: (15.6, 31.2, 31.2, 46.7)}   # ft³/h a 1 rpm (KWS)
MATERIALES = {   # nombre, densidad aparente [lb/ft³], llenado, Fm (tabla de materiales de KWS)
    'maiz': ('maíz desgranado', (45, 45), '45', 0.4), 'trigo': ('trigo', (45, 48), '45', 0.4),
    'soja': ('soja en grano', (45, 50), '45', 0.5), 'arroz': ('arroz descascarado', (45, 49), '45', 0.4),
    'avena': ('avena', (26, 26), '45', 0.6), 'harina': ('harina de trigo', (33, 40), '30A', 0.6),
    'harina-soja': ('harina de soja, fría', (35, 45), '30A', 0.6),
    'azucar': ('azúcar refinada granulada seca', (50, 55), '30A', 1.2), 'aserrin': ('aserrín seco', (10, 13), '30A', 1.4),
    'carbon': ('carbón bituminoso', (40, 60), '30A', 0.9), 'cemento': ('cemento portland', (94, 94), '30B', 1.4),
    'sal': ('sal seca fina', (70, 80), '30B', 1.7), 'ceniza': ('ceniza volante', (30, 45), '30B', 2.0),
    'caliza': ('caliza agrícola', (68, 68), '30A', 2.0), 'arena': ('arena de banco, húmeda', (110, 130), '15', 2.8)}

# ------------------------------------------------------------------------------------------ datos de izaje (verificar)
K_CABLE = {('6x19', 'fibra'): 0.330, ('6x19', 'acero'): 0.356, ('6x36', 'fibra'): 0.330, ('6x36', 'acero'): 0.356}
DIAM_CABLE = [6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 19, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]   # mm
ZP = {'M1': 3.15, 'M2': 3.35, 'M3': 3.55, 'M4': 4.0, 'M5': 4.5, 'M6': 5.6, 'M7': 7.1, 'M8': 9.0}
H1 = {'M1': 11.2, 'M2': 12.5, 'M3': 14.0, 'M4': 16.0, 'M5': 18.0, 'M6': 20.0, 'M7': 22.4, 'M8': 25.0}   # tambor
H2 = {'M1': 12.5, 'M2': 14.0, 'M3': 16.0, 'M4': 18.0, 'M5': 20.0, 'M6': 22.4, 'M7': 25.0, 'M8': 28.0}   # polea
TOOLBOX_6X19 = [(0.5, 95.2), (0.625, 149.0), (0.75, 212.0), (0.875, 286.0), (1.0, 372.0)]   # in, kN (6x19 IPS alma de fibra)
GRADO8 = [(6, 1.12), (7, 1.5), (8, 2.0), (10, 3.15), (13, 5.3), (16, 8.0), (18, 10.0), (19, 11.2), (20, 12.5),
          (22, 15.0), (23, 16.0), (26, 21.2), (28, 25.0), (32, 31.5)]   # mm, t por ramal vertical (EN 818-4)
MODO_EN = {2: ((45, 1.4), (60, 1.0)), 3: ((45, 2.1), (60, 1.5)), 4: ((45, 2.1), (60, 1.5))}
CICLOS_U = [16000, 32000, 63000, 125000, 250000, 500000, 1e6, 2e6, 4e6]       # límites de U0 a U8; más: U9
HORAS_T = [200, 400, 800, 1600, 3200, 6300, 12500, 25000, 50000]             # límites de T0 a T8; más: T9
ESPECTRO = [0.125, 0.25, 0.5, 1.0]                                             # kp o km máximos de Q1-Q4 / L1-L4
MATRIZ = [[1, 1, 1, 2, 3, 4, 5, 6, 7, 8], [1, 1, 2, 3, 4, 5, 6, 7, 8, 8], [1, 2, 3, 4, 5, 6, 7, 8, 8, 8],
          [2, 3, 4, 5, 6, 7, 8, 8, 8, 8]]
PHI2 = {'HC1': (1.05, 0.17), 'HC2': (1.10, 0.34), 'HC3': (1.15, 0.51), 'HC4': (1.20, 0.68)}   # EN 13001-2


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


def interp(tabla, x):
    if x <= tabla[0][0]:
        return tabla[0][1]
    for (x0, y0), (x1, y1) in zip(tabla, tabla[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return tabla[-1][1]


def motor_iec(p):
    return next((x for x in POT_IEC if x >= p - 1e-9), None)


def kw(p):
    """Potencia normalizada siguiente, escrita como en el catálogo: 0,37 · 1,1 · 4 · 18,5."""
    m = motor_iec(p)
    return n(m if m else p, 2).rstrip('0').rstrip(',')


# ------------------------------------------------------------------------------------------ cinta
def ancho_util(B):
    """B en mm; b en m (IS 11592, cl. 8.4.3; el mismo criterio que DIN 22101)."""
    Bm = B / 1000
    return 0.9 * Bm - 0.05 if Bm <= 2.0 else Bm - 0.25


def seccion(B, lam=30.0, theta=20.0, metodo='cema', l3=None):
    b = ancho_util(B)
    r = {'b': b, 'l3': None, 'l1': None}
    if lam == 0:
        x, A2 = b, 0.0
    else:
        if l3 is None:
            if int(round(B)) not in L3_TERNA:
                raise ValueError('ancho de %g mm sin largo de rodillo en la tabla: indicá --l3 (mm, del catálogo)' % B)
            l3 = L3_TERNA[int(round(B))]
        l3m = l3 / 1000
        if l3m >= b:
            raise ValueError('el rodillo central (%s m) no puede ser más largo que el ancho útil (%s m)' % (n(l3m, 3), n(b, 3)))
        l1 = (b - l3m) / 2
        lr = math.radians(lam)
        x = l3m + 2 * l1 * math.cos(lr)
        A2 = (l3m + x) / 2 * l1 * math.sin(lr)
        r.update({'l3': l3m, 'l1': l1})
    t = math.radians(theta)
    if theta <= 0:
        A1 = 0.0
    elif metodo == 'cema':
        A1 = (x / 2) ** 2 / math.sin(t) ** 2 * (t - math.sin(t) * math.cos(t))   # segmento circular
    else:
        A1 = x ** 2 * math.tan(t) / 4                                           # triángulo de DIN 22101
    r.update({'x': x, 'A1': A1, 'A2': A2, 'A': A1 + A2})
    return r


def vel_max(B, fv):
    fila = [f for b0, f in VEL_MAX if B >= b0][-1]
    col = {1: 0, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4}[fv]
    return fila[col]


def cinta(B, v, rho, theta=None, lam=30.0, delta=0.0, metodo='cema', l3=None, fv=None, L=None, H=None, mr=None,
          mg=None, f=0.020, C=None, fs=0.0, tambor='revestido', mu=None, arco=180.0, eta=0.94, a0=None, flecha=0.01):
    if theta is None:
        if metodo == 'din':
            raise ValueError('con --metodo din indicá --theta: es el ángulo dinámico β del triángulo (menor que el θ de CEMA)')
        theta = 20.0
    if abs(delta) > 30:
        raise ValueError('la tabla 9 de la IS 11592 llega a 30°: con más inclinación va banda con nervios o tacos (fabricante)')
    s = seccion(B, lam, theta, metodo, l3)
    K = interp(K_INCLINACION, abs(delta))
    A = s['A']
    Iv = 3600 * A * v * K
    Im = Iv * rho / 1000
    mL = A * K * rho
    pct = 0.75 if B <= 600 else 0.90
    out = ['Ancho útil: b = 0,9·B − 0,05 m = %s m (B = %s mm; IS 11592, cl. 8.4.3, y DIN 22101)' % (n(s['b'], 3), n(B, 0))
           if B <= 2000 else 'Ancho útil: b = B − 0,25 m = %s m (IS 11592, cl. 8.4.3)' % n(s['b'], 3)]
    if lam:
        out += ['Terna a %s°: rodillo central l3 = %s m%s; lateral útil l1 = (b − l3)/2 = %s m; ancho de la carga en los bordes x = l3 + 2·l1·cos λ = %s m'
                % (n(lam, 0), n(s['l3'], 3), ' (DIN 22107, verificar con el catálogo)' if l3 is None else '', n(s['l1'], 4), n(s['x'], 4)),
                'Parte de abajo (trapecio): A2 = (l3 + x)/2·l1·sen λ = %s m²' % n(s['A2'], 5)]
    else:
        out.append('Banda plana: la carga es solo la sobrecarga sobre el ancho útil x = b = %s m' % n(s['x'], 3))
    if metodo == 'cema':
        out.append('Sobrecarga en arco de círculo (CEMA), θ = %s°: A1 = (x/2)²·(θ − sen θ·cos θ)/sen² θ = %s m²' % (n(theta, 0), n(s['A1'], 5)))
    else:
        out.append('Sobrecarga en triángulo (DIN 22101), ángulo dinámico β = %s°: A1 = x²·tg β/4 = %s m²' % (n(theta, 0), n(s['A1'], 5)))
    out += ['Sección de carga: A = A1 + A2 = %s m²' % n(A, 5),
            'Factor por inclinación δ = %s° (IS 11592, tabla 9): K = %s' % (n(delta, 1), n(K, 3)),
            'Capacidad: Iv = 3600·A·v·K = 3600·%s·%s·%s = %s m³/h; Im = Iv·ρ = %s t/h (ρ = %s kg/m³)'
            % (n(A, 5), n(v, 2), n(K, 3), n(Iv, 1), n(Im, 1), n(rho, 0)),
            'Capacidad de diseño (IS 11592, cl. 8.4.5: %d %% de la calculada%s): %s t/h'
            % (pct * 100, ', por ser de hasta 600 mm' if B <= 600 else '', n(Im * pct, 1)),
            'Carga por metro: m\'L = A·K·ρ = %s kg/m' % n(mL, 2)]
    r = {'b': s['b'], 'A1': s['A1'], 'A2': s['A2'], 'A': A, 'K': K, 'Iv': Iv, 'Im': Im, 'mL': mL}
    if fv:
        vm = vel_max(B, fv)
        r['vmax'] = vm
        out.append('Velocidad máxima (IS 11592, tabla 6) con B = %s mm y factor de velocidad %d: %s m/s → %s'
                   % (n(B, 0), fv, n(vm, 2), 'verifica' if v <= vm + 1e-9 else 'NO VERIFICA: bajar la velocidad o ensanchar la banda'))
    if L is None:
        out.append('Para la potencia y las tensiones: --L (m), --mr y --mg (kg/m, de los catálogos de rodillos y de banda).')
        return r, out
    if mr is None or mg is None:
        raise ValueError('para la potencia hacen falta --mr (rodillos, superior + inferior, kg/m) y --mg (banda, kg/m) del catálogo')
    if H is None:
        H = L * math.sin(math.radians(delta))
    if C is None:
        C = interp(C_LARGO, L)
        origen = 'tabla de DIN 22101/ISO 5048 para L = %s m, verificar en la norma vigente' % n(L, 0)
    else:
        origen = 'dato'
    cd = math.cos(math.radians(delta))
    Fh = C * f * L * G * (mr + (2 * mg + mL) * cd)
    Fst = mL * G * H
    FU = Fh + Fst + fs
    PA = FU * v / 1000
    PM = PA / eta
    out += ['Fuerza en el tambor (IS 11592, ec. 6; DIN 22101): FU = C·f·L·g·[m\'R + (2·m\'G + m\'L)·cos δ] + m\'L·g·H + FS',
            '  = %s·%s·%s·9,81·[%s + (2·%s + %s)·%s] + %s·9,81·%s + %s = %s N   (C = %s: %s)'
            % (n(C, 2), n(f, 3), n(L, 1), n(mr, 1), n(mg, 1), n(mL, 2), n(cd, 4), n(mL, 2), n(H, 2), miles(fs), miles(FU), n(C, 2), origen),
            'Potencia en el tambor: PA = FU·v = %s kW; en el motor PM = PA/η = %s/%s = %s kW → motor normalizado de %s kW'
            % (n(PA, 2), n(PA, 2), n(eta, 2), n(PM, 2), kw(PM))]
    if L < 80:
        out.append('AVISO: con L < 80 m el valor de C es incierto (IS 11592, cl. 8.5.1.2): el script usa el de 80 m, que se queda corto; calcular las resistencias secundarias una por una o pedir el cálculo al fabricante.')
    if f == 0.020:
        out.append('f = 0,020 es el valor normal (IS 11592, cl. 8.5.1.1): 0,016 en condiciones favorables, hasta 0,030 desfavorables, 0,012 en bajada con freno.')
    if delta < 0 or H < 0:
        out.append('AVISO: cinta en bajada: usar f = 0,012 (IS 11592) y revisar si el motor frena (FU negativa = genera).')
    r.update({'H': H, 'C': C, 'FU': FU, 'PA': PA, 'PM': PM})
    if FU > 0:
        mu = mu if mu is not None else MU_DISENO[tambor]
        e_ma = math.exp(mu * math.radians(arco))
        T2e = FU / (e_ma - 1)
        T2 = T2e
        out.append('Euler-Eytelwein: T1/T2 ≤ e^(μ·α) = e^(%s·%s rad) = %s (μ = %s, tambor %s; arco %s°) → T2 ≥ FU/(e^(μ·α) − 1) = %s N'
                   % (n(mu, 2), n(math.radians(arco), 3), n(e_ma, 3), n(mu, 2), tambor if mu == MU_DISENO.get(tambor) else 'dato', n(arco, 0), miles(T2e)))
        if a0:
            Tf = a0 * (mg + mL) * G / (8 * flecha)
            out.append('Flecha entre rodillos de carga: T ≥ a0·(m\'G + m\'L)·g/(8·h/a) = %s·(%s + %s)·9,81/(8·%s) = %s N (h/a = %s %%, verificar con el fabricante)'
                       % (n(a0, 2), n(mg, 1), n(mL, 2), n(flecha, 3), miles(Tf), n(100 * flecha, 1)))
            if Tf > T2:
                T2 = Tf
                out.append('Manda la flecha: T2 = %s N (del lado seguro: la cola tiene T2 más la resistencia del retorno)' % miles(T2))
            r['Tf'] = Tf
        T1 = FU + T2
        out += ['Tensiones: T2 = %s N; T1 = FU + T2 = %s N; por unidad de ancho T1/B = %s N/mm: comparar con la tensión de trabajo de la banda (catálogo)'
                % (miles(T2), miles(T1), n(T1 / B, 1))]
        r.update({'T1': T1, 'T2': T2, 'T2e': T2e, 'e_ma': e_ma})
    return r, out


# ------------------------------------------------------------------------------------------ tornillo
def tornillo(D, d, p=None, rpm=None, Q=None, llenado=None, material=None, rho=None, L=None, H=0.0, Fm=None,
             cojinete='rodamiento', Ff=1.0, Fp=1.0, e=0.88, fo=1.0):
    p = p or D
    out = []
    if material:
        if material not in MATERIALES:
            raise ValueError('material: %s' % ', '.join(sorted(MATERIALES)))
        nombre, (w1, w2), ll, fm = MATERIALES[material]
        rho = rho or (w1 + w2) / 2 * LB_FT3
        llenado = llenado or ll
        Fm = Fm or fm
        out.append('Material: %s; tabla de KWS: %s lb/ft³ → ρ = %s kg/m³, llenado %s %%, Fm = %s'
                   % (nombre, ('%g' % w1) if w1 == w2 else '%g a %g' % (w1, w2), n(rho, 0), llenado, n(Fm, 1)))
    if llenado not in LLENADO or rho is None:
        raise ValueError('indicá --material o --llenado (15, 30A, 30B o 45) y --rho (kg/m³)')
    if d >= D:
        raise ValueError('el tubo (d) tiene que ser menor que la hélice (D)')
    phi = LLENADO[llenado]
    q1 = 60 * math.pi / 4 * ((D / 1000) ** 2 - (d / 1000) ** 2) * (p / 1000) * phi
    out.append('Capacidad a 1 rpm: q = 60·(π/4)·(D² − d²)·p·φ = 60·0,7854·(%s² − %s²)·%s·%s = %s m³/h por rpm (CEMA 350)'
               % (n(D / 1000, 3), n(d / 1000, 4), n(p / 1000, 3), n(phi, 2), n(q1, 4)))
    if rpm is None:
        if Q is None:
            raise ValueError('indicá --rpm o la capacidad pedida --Q (t/h)')
        rpm = Q * 1000 / rho / q1
        out.append('Velocidad necesaria para %s t/h: n = Q/(ρ·q) = %s rpm' % (n(Q, 1), n(rpm, 1)))
    Qv = q1 * rpm
    Qm = Qv * rho / 1000
    out.append('A %s rpm: Q = %s m³/h = %s t/h' % (n(rpm, 1), n(Qv, 2), n(Qm, 2)))
    D_in = D / PULG
    Dn = min(FD_CEMA, key=lambda k: abs(k - D_in))
    if abs(Dn - D_in) > 0.6:
        out.append('AVISO: %s mm (%s in) no es un diámetro de CEMA: se toman los datos del de %d in' % (n(D, 0), n(D_in, 1), Dn))
    r = {'q1': q1, 'rpm': rpm, 'Qv': Qv, 'Qm': Qm, 'Dn': Dn}
    if Dn in RPM_MAX:
        nm = RPM_MAX[Dn][ORDEN_LL.index(llenado)]
        r['rpm_max'] = nm
        out.append('Máximo recomendado para %d in con llenado %s (KWS): %d rpm → %s' % (Dn, llenado, nm, 'verifica' if rpm <= nm else 'NO VERIFICA: más diámetro'))
    if L:
        if Fm is None:
            raise ValueError('para la potencia indicá --material o --Fm (factor del material, tabla de CEMA/KWS)')
        if cojinete not in FB_CEMA:
            raise ValueError('cojinete: %s' % ', '.join(FB_CEMA))
        Fd, Fb = FD_CEMA[Dn], FB_CEMA[cojinete]
        Lft, Cft, W = L / FT, Qv / FT3, rho / LB_FT3
        HPf = Lft * rpm * Fd * Fb / 1e6
        HPm = Cft * Lft * W * Ff * Fm * Fp / 1e6
        hp = (HPf + HPm) * fo / e
        P = hp * HP_KW
        PH = Qm * G * H / 3600 / e if H else 0.0
        out += ['Potencia (CEMA 350, en unidades inglesas): L = %s ft, C = %s ft³/h, W = %s lb/ft³' % (n(Lft, 1), n(Cft, 0), n(W, 1)),
                '  vacío HPf = L·n·Fd·Fb/10⁶ = %s·%s·%d·%s/10⁶ = %s hp (Fd del de %d in; cojinetes %s)'
                % (n(Lft, 1), n(rpm, 1), Fd, n(Fb, 1), n(HPf, 4), Dn, cojinete),
                '  material HPm = C·L·W·Ff·Fm·Fp/10⁶ = %s·%s·%s·%s·%s·%s/10⁶ = %s hp'
                % (n(Cft, 0), n(Lft, 1), n(W, 1), n(Ff, 2), n(Fm, 2), n(Fp, 2), n(HPm, 4)),
                '  total = (HPf + HPm)·Fo/e = (%s + %s)·%s/%s = %s hp = %s kW' % (n(HPf, 3), n(HPm, 3), n(fo, 2), n(e, 2), n(hp, 3), n(P, 2))]
        if (HPf + HPm) < 5 and fo == 1.0:
            out.append('AVISO: HPf + HPm < 5 hp: CEMA corrige con el factor de sobrecarga Fo de su gráfico (KWS, "Corrected Material HP"); el script no lo tiene: ingresarlo con --fo.')
        if H:
            out.append('Desnivel de %s m: se suma la elevación ṁ·g·H/e = %s kW (CEMA calcula el sinfín horizontal; inclinado, la capacidad baja: consultar al fabricante, verificar)'
                       % (n(H, 1), n(PH, 2)))
        Pt = P + PH
        out.append('Potencia en el eje: %s kW → motor normalizado de %s kW (Dec. 351/79, art. 131: el sinfín va totalmente cubierto)'
                   % (n(Pt, 2), kw(Pt)))
        r.update({'HPf': HPf, 'HPm': HPm, 'hp': hp, 'P': P, 'PH': PH, 'Pt': Pt})
    return r, out


# ------------------------------------------------------------------------------------------ cangilones
def cangilones(V, paso, rho, phi=0.75, v=None, rpm=None, D=None, proy=None, H=None, Q=None):
    out = []
    if v is None:
        if rpm and D:
            v = math.pi * D / 1000 * rpm / 60
        elif Q:
            v = Q / (3.6 * V / paso * phi * rho / 1000)
            out.append('Velocidad necesaria para %s t/h: v = Q/(3,6·(V/a)·φ·ρ) = %s m/s' % (n(Q, 1), n(v, 2)))
        else:
            raise ValueError('indicá --v, o --rpm con --D, o la capacidad pedida --Q')
    Qv = 3.6 * V / paso * v * phi
    Qm = Qv * rho / 1000
    out.append('Capacidad: Q = 3,6·(V/a)·v·φ = 3,6·(%s l/%s m)·%s m/s·%s = %s m³/h = %s t/h (ρ = %s kg/m³; φ = %s, verificar con el fabricante)'
               % (n(V, 2), n(paso, 3), n(v, 2), n(phi, 2), n(Qv, 2), n(Qm, 2), n(rho, 0), n(phi, 2)))
    r = {'v': v, 'Qv': Qv, 'Qm': Qm}
    if D:
        rt = D / 2000
        w = v / rt
        hp = G / w ** 2
        rcg = rt + (proy / 2000 if proy else 0.0)
        w_id = math.sqrt(G / rcg)
        r.update({'w': w, 'rpm': w * 60 / (2 * math.pi), 'hp': hp, 'v_id': w_id * rt, 'rpm_id': w_id * 60 / (2 * math.pi)})
        out.append('Tambor de cabeza de %s mm: ω = v/r = %s rad/s (%s rpm); distancia polar hp = g/ω² = %s m (radio del tambor %s m)'
                   % (n(D, 0), n(w, 3), n(r['rpm'], 1), n(hp, 3), n(rt, 3)))
        if hp < rt:
            tipo = 'centrífuga: el polo cae dentro del tambor (v² > g·r)'
        elif proy and hp > rt + proy / 1000:
            tipo = 'por gravedad: el polo cae fuera del borde exterior del cangilón'
        elif proy:
            tipo = 'mixta: el polo cae entre el tambor y el borde del cangilón'
        else:
            tipo = 'no centrífuga (polo fuera del tambor): con --proy (saliente del cangilón, mm) dice si es por gravedad o mixta'
        r['tipo'] = tipo.split(':')[0]
        out += ['Descarga %s' % tipo,
                'Para que el material salga arriba del tambor: ω²·rc ≥ g, con rc = %s m al centro del cangilón → v ≥ %s m/s en la banda (%s rpm)'
                % (n(rcg, 3), n(r['v_id'], 2), n(r['rpm_id'], 1))]
    if H:
        r['P'] = Qm * G * H / 3600
        out.append('Potencia teórica de elevación: P = ṁ·g·H = %s kW para %s m; el fabricante suma el dragado del pie y los rozamientos (verificar)'
                   % (n(r['P'], 2), n(H, 1)))
    return r, out


# ------------------------------------------------------------------------------------------ aparejo y cable
def rendimiento_aparejo(ramales, eta_p):
    return 1.0 if eta_p >= 1 else (1 - eta_p ** ramales) / (ramales * (1 - eta_p))


def aparejo(m, ramales, eta_polea=0.98, eta=None, desvios=0, h=None):
    W = m * G
    eta_ap = eta if eta is not None else rendimiento_aparejo(ramales, eta_polea)
    F = W / (ramales * eta_ap) / eta_polea ** desvios
    out = ['Carga W = m·g = %s·9,81 = %s N; %d ramales → ventaja mecánica ideal %d' % (miles(m), miles(W), ramales, ramales)]
    if eta is None:
        out.append('Rendimiento del aparejo: η = (1 − ηp^n)/(n·(1 − ηp)) = (1 − %s^%d)/(%d·(1 − %s)) = %s (ηp = %s por polea, verificar con el fabricante)'
                   % (n(eta_polea, 3), ramales, ramales, n(eta_polea, 3), n(eta_ap, 4), n(eta_polea, 3)))
    out.append('Fuerza en el tiro: F = W/(n·η)%s = %s N (%s kg); ventaja mecánica real W/F = %s'
               % ('/ηp^%d' % desvios if desvios else '', miles(F), n(F / G, 1), n(W / F, 2)))
    if h:
        out.append('Para subir la carga %s m, el tiro recorre n·h = %s m' % (n(h, 2), n(ramales * h, 2)))
    return {'W': W, 'eta': eta_ap, 'F': F}, out


def cable(m, ramales, eta=None, cs=6.0, construccion='6x36', alma='acero', grado=1770, grupo=None, gancho=0.0,
          eta_polea=0.98, desvios=0):
    if (construccion, alma) not in K_CABLE:
        raise ValueError('construcción 6x19 o 6x36; alma fibra o acero')
    if grupo and grupo not in ZP:
        raise ValueError('grupo: M1 a M8')
    eta_ap = eta if eta is not None else rendimiento_aparejo(ramales, eta_polea)
    S = (m + gancho) * G / (ramales * eta_ap) / eta_polea ** desvios
    out = ['Tensión en el ramal más cargado: S = (m + m_gancho)·g/(n·η)%s = (%s + %s)·9,81/(%d·%s) = %s N'
           % ('/ηp^%d' % desvios if desvios else '', miles(m), miles(gancho), ramales, n(eta_ap, 4), miles(S))]
    cs_u = cs
    if grupo:
        out.append('Grupo %s: coeficiente mínimo Zp = %s (ISO 4308-1 / FEM 1.001, verificar en la norma vigente)' % (grupo, n(ZP[grupo], 2)))
        cs_u = max(cs, ZP[grupo])
    if cs_u < 6:
        out.append('AVISO: el Dec. 351/79 (arts. 118 y 123) pide coeficiente de seguridad ≥ 6 en cables izadores.')
    F_req = cs_u * S / 1000
    K = K_CABLE[(construccion, alma)]
    d_s = next((d for d in DIAM_CABLE if K * d * d * grado / 1000 >= F_req), None)
    out.append('Carga de rotura mínima requerida: Fmin ≥ cs·S = %s·%s N = %s kN' % (n(cs_u, 2), miles(S), n(F_req, 2)))
    out.append('Cable %s alma de %s, grado %d N/mm²: Fmin = K·d²·R/1000 con K = %s (EN 12385-4, verificar en la norma vigente)'
               % (construccion, alma, grado, n(K, 3)))
    r = {'S': S, 'F_req': F_req, 'd': d_s, 'cs': cs_u, 'eta': eta_ap}
    if d_s is None:
        out.append('Ningún diámetro de la tabla (hasta 40 mm) alcanza: más ramales o cable de más resistencia.')
        return r, out
    F_d = K * d_s ** 2 * grado / 1000
    out.append('Diámetro sugerido: %d mm → Fmin = %s·%d²·%d/1000 = %s kN (coeficiente real %s); confirmar en el catálogo del fabricante'
               % (d_s, n(K, 3), d_s, grado, n(F_d, 1), n(F_d * 1000 / S, 2)))
    r['F_d'] = F_d
    if grupo:
        r.update({'Dt': H1[grupo] * d_s, 'Dp': H2[grupo] * d_s})
        out.append('Diámetros mínimos (al eje del cable) para %s: tambor D ≥ %s·d = %s mm; poleas D ≥ %s·d = %s mm (verificar en la norma vigente)'
                   % (grupo, n(H1[grupo], 1), n(r['Dt'], 0), n(H2[grupo], 1), n(r['Dp'], 0)))
    out.append('Descarte: Dec. 351/79, art. 123 (más del 10 % de alambres rotos en dos tramos del cableado separados menos de 8·d) y la ISO 4309.')
    return r, out


# ------------------------------------------------------------------------------------------ eslinga
def eslinga(m, ramales, angulo=0.0, desde='vertical', portantes=None):
    if ramales not in (1, 2, 3, 4):
        raise ValueError('ramales: 1 a 4')
    beta = angulo if desde == 'vertical' else 90.0 - angulo
    if not 0 <= beta < 90:
        raise ValueError('el ángulo con la vertical tiene que estar entre 0° y 90°')
    nport = portantes or min(ramales, 3)
    cb = math.cos(math.radians(beta))
    T = m * G / (nport * cb)
    t_ramal = T / G / 1000
    out = ['Ángulo de cada ramal con la vertical β = %s°; factor de ángulo 1/cos β = %s' % (n(beta, 1), n(1 / cb, 3)),
           'Tensión por ramal: T = m·g/(n·cos β) = %s·9,81/(%d·%s) = %s kN (%s t), con %d ramales que toman la carga'
           % (miles(m), nport, n(cb, 4), n(T / 1000, 2), n(t_ramal, 3), nport)]
    if ramales == 4 and not portantes:
        out.append('Con 4 ramales se cuenta que trabajan 3 (los largos nunca son iguales); con carga rígida, contar 2 (verificar).')
    if beta > 60:
        out.append('AVISO: más de 60° con la vertical (menos de 30° con la horizontal): las tablas de eslingas no lo admiten.')
    r = {'beta': beta, 'T': T, 't_ramal': t_ramal}
    d4 = next((d for d, w in GRADO8 if w >= t_ramal - 1e-9), None)
    d5 = next((d for d, w in GRADO8 if 0.8 * w >= t_ramal - 1e-9), None)
    r.update({'d4': d4, 'd5': d5})
    out.append('Cadena de grado 8 (EN 818-4, carga de trabajo con coeficiente 4, verificar en el catálogo): %s'
               % ('%d mm (%s t por ramal)' % (d4, n(dict(GRADO8)[d4], 2)) if d4 else 'más de 32 mm'))
    out.append('Con el coeficiente 5 del Dec. 351/79, art. 122 (carga de tabla × 4/5): %s'
               % ('%d mm (%s t)' % (d5, n(0.8 * dict(GRADO8)[d5], 2)) if d5 else 'más de 32 mm'))
    if ramales in MODO_EN and beta <= 60:
        M = next(f for lim, f in MODO_EN[ramales] if beta <= lim)
        r['M'] = M
        out.append('Factor de modo europeo para %d ramales y β ≤ %d°: %s → la eslinga levanta %s veces la carga de un ramal (verificar en la norma vigente)'
                   % (ramales, 45 if beta <= 45 else 60, n(M, 1), n(M, 1)))
    return r, out


# ------------------------------------------------------------------------------------------ autoelevador
def autoelevador(Qn, cn, c, x=None):
    out = []
    if c <= cn:
        out.append('Con el centro de carga a %s mm (no más que el nominal de %s mm) la capacidad es la nominal: %s kg; no se puede superar.'
                   % (n(c, 0), n(cn, 0), miles(Qn)))
        return {'Q': Qn, 'Qx': Qn}, out
    Q = Qn * cn / c
    out.append('Momento de la carga constante (OSHA 1910.178, ap. A): Q = Qn·cn/c = %s·%s/%s = %s kg' % (miles(Qn), n(cn, 0), n(c, 0), miles(Q)))
    r = {'Q': Q}
    if x:
        Qx = Qn * (x + cn) / (x + c)
        r['Qx'] = Qx
        out.append('Contando la distancia x del eje delantero a la cara de las horquillas: Q = Qn·(x + cn)/(x + c) = %s kg (menos conservador; usar la placa)'
                   % miles(Qx))
    out.append('Con la carga alta la capacidad baja más: manda la tabla o curva de la placa (Res. SRT 960/15, art. 2; IRAM 8412-1).')
    return r, out


# ------------------------------------------------------------------------------------------ grua
def clase(valor, limites):
    return next((i for i, lim in enumerate(limites) if valor <= lim), len(limites))


def grupo(valor, k, limites):
    j = next((i for i, lim in enumerate(ESPECTRO) if k <= lim + 1e-12), None)
    if j is None:
        raise ValueError('el factor de espectro va de 0 a 1')
    i = clase(valor, limites)
    return i, j, MATRIZ[j][i]


def grua(ciclos=None, kp=None, horas=None, km=None, carga=None, carro=0.0, puente=0.0, luz=None, aprox=None, phi=None,
         hc=None, vh=None):
    out, r = [], {}
    if ciclos is not None and kp is not None:
        i, j, a = grupo(ciclos, kp, CICLOS_U)
        r['A'] = 'A%d' % a
        out.append('Aparato: %s ciclos → U%d; kp = %s → Q%d; grupo A%d (ISO 4301-1 / FEM 1.001, verificar en la norma vigente)'
                   % (miles(ciclos), i, n(kp, 3), j + 1, a))
    if horas is not None and km is not None:
        i, j, mm = grupo(horas, km, HORAS_T)
        r['M'] = 'M%d' % mm
        out.append('Mecanismo: %s h de marcha → T%d; km = %s → L%d; grupo M%d (para el cable, comando cable --grupo M%d)'
                   % (miles(horas), i, n(km, 3), j + 1, mm, mm))
    if carga is not None and luz:
        if phi is None:
            if hc:
                p0, b2 = PHI2[hc]
                phi = p0 + b2 * (vh or 0.0)
                out.append('Coeficiente dinámico de izaje φ2 = φ2,min + β2·vh = %s + %s·%s = %s (EN 13001-2, clase %s, verificar en la norma vigente)'
                           % (n(p0, 2), n(b2, 2), n(vh or 0.0, 2), n(phi, 3), hc))
            else:
                phi = 1.0
                out.append('AVISO: sin coeficiente dinámico (--phi o --hc con --vh): se toma φ = 1.')
        e = aprox or 0.0
        Qd = phi * carga + carro
        Rmax = (Qd * (luz - e) / luz + puente / 2) / 2 * G / 1000
        Rmin = (Qd * e / luz + puente / 2) / 2 * G / 1000
        r.update({'phi': phi, 'Rmax': Rmax, 'Rmin': Rmin})
        out += ['Carga en las ruedas (2 por testero, carro a %s m de un riel): R = [(φ·Q + Gc)·(L − e)/L + Gp/2]/2' % n(e, 2),
                '  Rmax = [(%s·%s + %s)·(%s − %s)/%s + %s/2]/2·9,81 = %s kN; en el riel opuesto Rmin = %s kN'
                % (n(phi, 3), miles(carga), miles(carro), n(luz, 2), n(e, 2), n(luz, 2), miles(puente), n(Rmax, 2), n(Rmin, 2)),
                'Con Rmax se verifica la viga carrilera (flexión, flecha, aplastamiento del alma): skill resistencia-de-materiales.']
    if not out:
        raise ValueError('indicá --ciclos y --kp, --horas y --km, o --carga, --luz, --carro y --puente')
    return r, out


# ------------------------------------------------------------------------------------------ demo
def cerca(x, y, tol_rel):
    return abs(x - y) <= tol_rel * abs(y)


def cmd_demo():
    ok = []
    # 1) DIN 22101 por el manual de Dunlop: B 1200, terna 30°, β 15°, l3 465 mm → 580 m³/h a 1 m/s (A = 0,161 m²)
    s = seccion(1200, 30, 15, 'din', 465)
    ok.append(('DIN 22101 (Dunlop, tabla 3): B 1200, 30°, β 15° → A = %s m² (tabla: 580 m³/h a 1 m/s = 0,1611 m²)' % n(s['A'], 4),
               cerca(s['A'], 580 / 3600, 0.005)))
    # 2) CEMA, arco de círculo (manual de rodillos de Sandvik, tabla 4): θ 25° → 0,169 m²
    s = seccion(1200, 30, 25, 'cema', 465)
    ok.append(('CEMA (Sandvik, tabla 4): B 1200, 30°, θ 25° → A = %s m² (tabla: 0,169)' % n(s['A'], 4), cerca(s['A'], 0.169, 0.01)))
    # 3) IS 11592:2000, tabla 8, banda plana
    for B, th, tab in ((500, 10, 0.0047), (500, 30, 0.0145), (1000, 10, 0.0210), (1000, 20, 0.0427), (1000, 30, 0.0653)):
        a = seccion(B, 0, th, 'cema')['A']
        ok.append(('IS 11592, tabla 8: banda plana de %d mm, θ %d° → %s m² (tabla: %s)' % (B, th, n(a, 4), n(tab, 4)), cerca(a, tab, 0.01)))
    # 4) IS 11592, tabla 20: e^(μ·α) con μ 0,25 (desnudo) y 0,35 (revestido)
    t20 = ((180, 2.19, 3.00), (200, 2.39, 3.39), (240, 2.85, 4.33), (360, 4.80, 9.02))
    bien = all(abs(math.exp(0.25 * math.radians(a)) - b) < 0.012 and abs(math.exp(0.35 * math.radians(a)) - c) < 0.012 for a, b, c in t20)
    ok.append(('IS 11592, tabla 20: e^(μ·α) de 180° a 360° (2,19 / 3,00 ... 4,80 / 9,02)', bien))
    # 5) ejemplo del SKILL.md: cinta de maíz
    r, _ = cinta(800, 2.5, 720, lam=30, delta=5, fv=1, L=100, mr=12, mg=9, arco=200)
    A = seccion(800, 30, 20, 'cema')['A']
    K = (0.99 + 0.98) / 2
    mL = A * K * 720
    FU = 1.78 * 0.02 * 100 * G * (12 + (2 * 9 + mL) * math.cos(math.radians(5))) + mL * G * 100 * math.sin(math.radians(5))
    T2 = FU / (math.exp(0.35 * math.radians(200)) - 1)
    ok.append(('cinta de maíz: %s t/h, FU = %s N, %s kW en el tambor, T1 = %s N' % (n(r['Im'], 1), miles(r['FU']), n(r['PA'], 2), miles(r['T1'])),
               cerca(r['Im'], 3600 * A * 2.5 * K * 0.72, 1e-9) and cerca(r['FU'], FU, 1e-9) and cerca(r['T1'], FU + T2, 1e-9)
               and cerca(r['Im'], 411.8, 0.001) and cerca(r['PA'], 16.37, 0.001) and cerca(r['T1'], 9285, 0.001)))
    # 6) tornillo: tabla de capacidad a 1 rpm de KWS con tubo de 2 3/8 in (6 y 9 in) y 3 1/2 in (12 in)
    for Din, tubo, ll in ((6, 2.375, '30A'), (9, 2.375, '30A'), (12, 3.5, '15'), (12, 3.5, '30A'), (12, 3.5, '45')):
        q = 0.7854 * (Din ** 2 - tubo ** 2) * Din * LLENADO[ll] * 60 / 1728
        tab = CAP_1RPM_KWS[Din][ORDEN_LL.index(ll)]
        ok.append(('KWS: sinfín de %d in, tubo de %s in, llenado %s → %s ft³/h a 1 rpm (tabla: %s)' % (Din, n(tubo, 3), ll, n(q, 2), n(tab, 1)),
                   cerca(q, tab, 0.015)))
    ok.append(('KWS, ejemplo de cal viva: 1,50·3,75·333 = %s ft³/h; en el de 16 in (31,2 ft³/h a 1 rpm) → %s rpm (libro: 60)'
               % (n(1.5 * 3.75 * 333, 0), n(1.5 * 3.75 * 333 / 31.2, 1)), abs(1.5 * 3.75 * 333 / 31.2 - 60) < 0.5))
    # 7) ejemplo del SKILL.md: sinfín de maíz, cuenta a mano en unidades inglesas
    r, _ = tornillo(300, 89, rpm=80, material='maiz', L=12)
    Cft = math.pi / 4 * ((300 / PULG) ** 2 - (89 / PULG) ** 2) * (300 / PULG) * 0.45 * 60 / 1728 * 80
    hp = (12 / FT * 80 * 55 * 1.0 / 1e6 + Cft * 12 / FT * 45 * 0.4 / 1e6) / 0.88
    ok.append(('sinfín de maíz de 300 mm a 80 rpm: %s t/h y %s kW (cuenta a mano: %s ft³/h, %s hp)' % (n(r['Qm'], 2), n(r['P'], 3), n(Cft, 0), n(hp, 3)),
               cerca(r['Qv'], Cft * FT3, 1e-9) and cerca(r['hp'], hp, 1e-9) and cerca(r['Qm'], 30.11, 0.001) and cerca(r['P'], 1.033, 0.002)))
    # 8) cangilones: el polo de la resultante de g y ω²·r cae siempre a g/ω² del centro
    w, peor = 5.0, 0.0
    for ang in (10, 35, 60, 120, 200, 300):
        for rr in (0.4, 0.5, 0.6):
            px, py = rr * math.cos(math.radians(ang)), rr * math.sin(math.radians(ang))
            ax, ay = w * w * px, w * w * py - G
            t = -px / ax
            peor = max(peor, abs(py + t * ay - G / w ** 2))
    r0, _ = cangilones(1.6, 0.25, 720, v=2.5, D=1000)
    r, _ = cangilones(1.6, 0.25, 720, v=2.5, D=1000, proy=150, H=20)
    ok.append(('cangilones: polo a g/ω² en cualquier posición (error %s m); n = 42,3/√D con D en m (%s rpm para 1 m)'
               % ('%.0e' % peor, n(r0['rpm_id'], 2)), peor < 1e-9 and cerca(r0['rpm_id'], 42.3, 0.002)))
    ok.append(('cangilones de 1,6 l cada 0,25 m a 2,5 m/s: %s t/h, descarga %s, %s kW de elevación en 20 m' % (n(r['Qm'], 2), r['tipo'], n(r['P'], 2)),
               cerca(r['Qm'], 3.6 * 1.6 / 0.25 * 2.5 * 0.75 * 0.72, 1e-9) and r['tipo'] == 'centrífuga'
               and cerca(r['P'], r['Qm'] * G * 20 / 3600, 1e-9) and cerca(r['v_id'], 0.5 * math.sqrt(G / 0.575), 1e-9)))
    # 9) aparejo: la fórmula contra el recorrido polea por polea
    T, tens = 1.0, []
    for _ in range(4):
        tens.append(T)
        T *= 0.98
    F_lazo = 2000 * G / sum(tens)
    r, _ = aparejo(2000, 4, 0.98)
    ok.append(('aparejo de 4 ramales, ηp 0,98: η = %s, tiro %s N (sumando ramal por ramal: %s N)' % (n(r['eta'], 4), miles(r['F']), miles(F_lazo)),
               cerca(r['F'], F_lazo, 1e-9)))
    # 10) cable: K·d²·R con K 0,330 y 1770 N/mm² contra la tabla de 6x19 IPS alma de fibra (Engineering ToolBox)
    peor = max(abs(0.330 * (d * PULG) ** 2 * 1770 / 1000 / kn - 1) for d, kn in TOOLBOX_6X19)
    ok.append(('cable: K·d²·R contra la tabla de 6x19 IPS de 1/2 a 1 in (peor %s %%)' % n(100 * peor, 1), peor < 0.02))
    r, _ = cable(2000, 4, grupo='M4')
    ok.append(('polipasto de 2000 kg, 4 ramales, coeficiente 6: Fmin ≥ %s kN → cable de %d mm (%s kN), tambor ≥ %s mm'
               % (n(r['F_req'], 2), r['d'], n(r['F_d'], 1), n(r['Dt'], 0)), r['d'] == 7 and cerca(r['F_req'], 30.33, 0.001) and r['Dt'] == 112))
    # 11) eslinga: tensión a mano y factores de modo = n·cos(β límite)
    r, _ = eslinga(2000, 2, 45)
    modo = all(abs(np_ * math.cos(math.radians(lim)) - f) < 0.03 for k, filas in MODO_EN.items() for (lim, f), np_ in
               zip(filas, (min(k, 3),) * 2))
    ok.append(('eslinga de 2 ramales a 45°: %s kN por ramal → cadena de %d mm (factor 4) o %d mm (factor 5)' % (n(r['T'] / 1000, 2), r['d4'], r['d5']),
               cerca(r['T'], 2000 * G / (2 * math.cos(math.radians(45))), 1e-9) and r['d4'] == 7 and r['d5'] == 8 and modo))
    rot = all(0.9 * 2 * math.pi / 4 * d * d * 800 / 4 / G / 1000 <= w <= 2 * math.pi / 4 * d * d * 800 / 4 / G / 1000 for d, w in GRADO8)
    ok.append(('tabla de grado 8: cada carga está entre 90 % y 100 % de la rotura (800 N/mm² en dos secciones) / 4', rot))
    # 12) autoelevador: ejemplo de OSHA 1910.178, apéndice A (3000 lb a 24 in → 2400 lb a 30 in)
    r, _ = autoelevador(3000, 24, 30)
    r2, _ = autoelevador(2500, 500, 700, x=450)
    ok.append(('autoelevador: 3000 lb a 24 in → %s lb a 30 in (OSHA: 2400); 2500 kg a 500 mm → %s kg a 700 mm' % (n(r['Q'], 0), miles(r2['Q'])),
               cerca(r['Q'], 2400, 1e-9) and cerca(r2['Qx'], 2500 * 950 / 1150, 1e-9)))
    # 13) grúa: matriz de grupos y reacciones a mano
    r, _ = grua(ciclos=200000, kp=0.25, horas=3000, km=0.5, carga=5000, carro=800, puente=6000, luz=15, aprox=1, phi=1.2)
    Rm = ((1.2 * 5000 + 800) * 14 / 15 + 3000) / 2 * G / 1000
    ok.append(('grúa: U4/Q2 → %s; T4/L3 → %s; rueda más cargada %s kN' % (r['A'], r['M'], n(r['Rmax'], 2)),
               r['A'] == 'A4' and r['M'] == 'M5' and cerca(r['Rmax'], Rm, 1e-9)))
    for nombre, b in ok:
        print('  %s %s' % ('ok ' if b else 'MAL', nombre))
    todo = all(b for _, b in ok)
    print('DEMO %s' % ('OK' if todo else 'FALLO'))
    return 0 if todo else 1


# ------------------------------------------------------------------------------------------ principal
def construir_parser():
    ap = argparse.ArgumentParser(prog='transporte.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True, metavar='comando')
    p = sp.add_parser('cinta', help='capacidad, potencia y tensiones de una cinta transportadora',
                      description='Capacidad por la sección de carga (ancho útil de IS 11592 y DIN 22101; sobrecarga en arco de CEMA '
                                  'o en triángulo de DIN 22101), potencia en el tambor (IS 11592 ec. 6) y tensiones T1 y T2 (Euler-Eytelwein).')
    p.add_argument('--B', type=float, required=True, help='ancho de la banda [mm]')
    p.add_argument('--v', type=float, required=True, help='velocidad de la banda [m/s]')
    p.add_argument('--rho', type=float, required=True, help='densidad aparente del material [kg/m³]')
    p.add_argument('--theta', type=float, help='ángulo de sobrecarga θ (CEMA, 20° por defecto) o dinámico β (DIN) [°]')
    p.add_argument('--lam', type=float, default=30.0, help='ángulo de los rodillos laterales de la terna [°]; 0 = banda plana')
    p.add_argument('--delta', type=float, default=0.0, help='inclinación de la cinta [°] (negativa si baja)')
    p.add_argument('--metodo', default='cema', choices=['cema', 'din'], help='forma de la sobrecarga: arco (cema) o triángulo (din)')
    p.add_argument('--l3', type=float, help='largo del rodillo central [mm] (si no, la tabla de DIN 22107)')
    p.add_argument('--fv', type=int, choices=range(1, 9), help='factor de velocidad de la IS 11592 (tamaño + abrasividad, 1 a 8)')
    p.add_argument('--L', type=float, help='distancia entre centros de tambores [m]')
    p.add_argument('--H', type=float, help='desnivel [m] (por defecto L·sen δ)')
    p.add_argument('--mr', type=float, help="masa de las partes que giran de los rodillos, superior + inferior [kg/m] (catálogo)")
    p.add_argument('--mg', type=float, help='masa de la banda [kg/m] (catálogo)')
    p.add_argument('--f', type=float, default=0.020, help='coeficiente ficticio de rozamiento (0,020 normal)')
    p.add_argument('--C', type=float, help='coeficiente de resistencias secundarias (si no, la tabla por largo)')
    p.add_argument('--fs', type=float, default=0.0, help='resistencias especiales: raspadores, faldones, trippers [N]')
    p.add_argument('--tambor', default='revestido', choices=['revestido', 'desnudo'], help='tambor motriz (μ 0,35 o 0,25)')
    p.add_argument('--mu', type=float, help='coeficiente de rozamiento banda-tambor (reemplaza al de --tambor)')
    p.add_argument('--arco', type=float, default=180.0, help='arco abrazado en el tambor motriz [°]')
    p.add_argument('--eta', type=float, default=0.94, help='rendimiento de la transmisión motor-tambor')
    p.add_argument('--a0', type=float, help='paso de los rodillos de carga [m], para la tensión mínima por flecha')
    p.add_argument('--flecha', type=float, default=0.01, help='flecha admisible h/a (0,01 = 1 %%)')
    p = sp.add_parser('tornillo', help='transportador a tornillo sinfín (CEMA 350)',
                      description='Capacidad Q = 60·(π/4)·(D² − d²)·p·n·φ·ρ, rpm necesarias, límite de rpm y potencia por CEMA 350 (factores de KWS).')
    p.add_argument('--D', type=float, required=True, help='diámetro de la hélice [mm]')
    p.add_argument('--d', type=float, required=True, help='diámetro exterior del tubo central [mm]')
    p.add_argument('--p', type=float, help='paso [mm] (por defecto igual a D)')
    p.add_argument('--rpm', type=float, help='velocidad [rpm]')
    p.add_argument('--Q', type=float, help='capacidad pedida [t/h], para calcular las rpm')
    p.add_argument('--material', choices=sorted(MATERIALES), help='material de la tabla (densidad, llenado y Fm)')
    p.add_argument('--llenado', choices=ORDEN_LL, help='llenado de CEMA: 15, 30A, 30B o 45 [%%]')
    p.add_argument('--rho', type=float, help='densidad aparente [kg/m³]')
    p.add_argument('--L', type=float, help='largo [m], para la potencia')
    p.add_argument('--H', type=float, default=0.0, help='desnivel [m]')
    p.add_argument('--Fm', type=float, help='factor del material de CEMA')
    p.add_argument('--cojinete', default='rodamiento', choices=sorted(FB_CEMA), help='cojinetes intermedios (factor Fb)')
    p.add_argument('--Ff', type=float, default=1.0, help='factor de hélice especial (cortada, plegada, de cinta)')
    p.add_argument('--Fp', type=float, default=1.0, help='factor de paletas')
    p.add_argument('--e', type=float, default=0.88, help='rendimiento del accionamiento')
    p.add_argument('--fo', type=float, default=1.0, help='factor de sobrecarga de CEMA (gráfico, con menos de 5 hp)')
    p = sp.add_parser('cangilones', help='elevador de cangilones: capacidad y descarga',
                      description='Capacidad Q = 3,6·(V/a)·v·φ·ρ, potencia de elevación y tipo de descarga por la distancia polar hp = g/ω².')
    p.add_argument('--V', type=float, required=True, help='capacidad de cada cangilón [l]')
    p.add_argument('--paso', type=float, required=True, help='separación entre cangilones [m]')
    p.add_argument('--rho', type=float, required=True, help='densidad aparente [kg/m³]')
    p.add_argument('--phi', type=float, default=0.75, help='llenado del cangilón (0,75 por defecto, verificar)')
    p.add_argument('--v', type=float, help='velocidad de la banda o cadena [m/s]')
    p.add_argument('--rpm', type=float, help='rpm del tambor de cabeza (con --D)')
    p.add_argument('--D', type=float, help='diámetro del tambor de cabeza [mm]')
    p.add_argument('--proy', type=float, help='saliente del cangilón desde la banda [mm]')
    p.add_argument('--H', type=float, help='altura de elevación [m]')
    p.add_argument('--Q', type=float, help='capacidad pedida [t/h], para calcular la velocidad')
    p = sp.add_parser('aparejo', help='aparejo o polipasto: rendimiento y fuerza en el tiro')
    p.add_argument('--m', type=float, required=True, help='masa de la carga [kg]')
    p.add_argument('--ramales', type=int, required=True, help='ramales que sostienen la carga')
    p.add_argument('--eta-polea', dest='eta_polea', type=float, default=0.98, help='rendimiento por polea (0,98 con rodamientos, verificar)')
    p.add_argument('--eta', type=float, help='rendimiento del aparejo completo (si se conoce)')
    p.add_argument('--desvios', type=int, default=0, help='poleas fijas de desvío entre el aparejo y el tiro')
    p.add_argument('--h', type=float, help='altura a subir [m]')
    p = sp.add_parser('cable', help='cable de acero: carga de rotura requerida y diámetro')
    p.add_argument('--m', type=float, required=True, help='masa de la carga [kg]')
    p.add_argument('--ramales', type=int, required=True, help='ramales que sostienen la carga')
    p.add_argument('--eta', type=float, help='rendimiento del aparejo (si no, se calcula con --eta-polea)')
    p.add_argument('--eta-polea', dest='eta_polea', type=float, default=0.98, help='rendimiento por polea')
    p.add_argument('--desvios', type=int, default=0, help='poleas de desvío hasta el tambor')
    p.add_argument('--cs', type=float, default=6.0, help='coeficiente de seguridad (6: Dec. 351/79, cables izadores)')
    p.add_argument('--construccion', default='6x36', choices=['6x19', '6x36'], help='clase del cable')
    p.add_argument('--alma', default='acero', choices=['fibra', 'acero'], help='alma de fibra o de acero')
    p.add_argument('--grado', type=int, default=1770, choices=[1770, 1960], help='resistencia de los alambres [N/mm²]')
    p.add_argument('--grupo', choices=sorted(ZP), help='grupo del mecanismo M1 a M8 (Zp y D/d)')
    p.add_argument('--gancho', type=float, default=0.0, help='masa del gancho y del aparejo móvil [kg]')
    p = sp.add_parser('eslinga', help='eslinga de 1 a 4 ramales: tensión por ramal')
    p.add_argument('--m', type=float, required=True, help='masa de la carga [kg]')
    p.add_argument('--ramales', type=int, required=True, help='cantidad de ramales (1 a 4)')
    p.add_argument('--angulo', type=float, default=0.0, help='ángulo de cada ramal [°]')
    p.add_argument('--desde', default='vertical', choices=['vertical', 'horizontal'], help='desde dónde se mide el ángulo')
    p.add_argument('--portantes', type=int, help='ramales que se cuentan como portantes')
    p = sp.add_parser('autoelevador', help='capacidad de un autoelevador con otro centro de carga')
    p.add_argument('--Qn', type=float, required=True, help='capacidad nominal de la placa [kg]')
    p.add_argument('--cn', type=float, required=True, help='centro de carga nominal [mm] (500 o 600 habituales)')
    p.add_argument('--c', type=float, required=True, help='centro de carga real [mm]')
    p.add_argument('--x', type=float, help='distancia del eje delantero a la cara de las horquillas [mm]')
    p = sp.add_parser('grua', help='grupo de clasificación y cargas en las ruedas de un puente grúa')
    p.add_argument('--ciclos', type=float, help='ciclos de izaje en la vida del aparato')
    p.add_argument('--kp', type=float, help='factor de espectro de carga del aparato (0 a 1)')
    p.add_argument('--horas', type=float, help='horas de marcha del mecanismo en su vida')
    p.add_argument('--km', type=float, help='factor de espectro del mecanismo (0 a 1)')
    p.add_argument('--carga', type=float, help='carga nominal [kg]')
    p.add_argument('--carro', type=float, default=0.0, help='masa del carro con el aparejo [kg]')
    p.add_argument('--puente', type=float, default=0.0, help='masa del puente sin carro [kg]')
    p.add_argument('--luz', type=float, help='luz entre rieles [m]')
    p.add_argument('--aprox', type=float, help='aproximación mínima del gancho al riel [m]')
    p.add_argument('--phi', type=float, help='coeficiente dinámico de la carga')
    p.add_argument('--hc', choices=sorted(PHI2), help='clase de izaje de EN 13001-2 (con --vh)')
    p.add_argument('--vh', type=float, help='velocidad de izaje [m/s]')
    sp.add_parser('demo', help='reproduce los ejemplos y termina en DEMO OK')
    return ap


def main(argv=None):
    a = construir_parser().parse_args(argv)
    try:
        if a.cmd == 'demo':
            return cmd_demo()
        if a.cmd == 'cinta':
            _, L = cinta(a.B, a.v, a.rho, a.theta, a.lam, a.delta, a.metodo, a.l3, a.fv, a.L, a.H, a.mr, a.mg, a.f, a.C, a.fs,
                         a.tambor, a.mu, a.arco, a.eta, a.a0, a.flecha)
        elif a.cmd == 'tornillo':
            _, L = tornillo(a.D, a.d, a.p, a.rpm, a.Q, a.llenado, a.material, a.rho, a.L, a.H, a.Fm, a.cojinete, a.Ff, a.Fp, a.e, a.fo)
        elif a.cmd == 'cangilones':
            _, L = cangilones(a.V, a.paso, a.rho, a.phi, a.v, a.rpm, a.D, a.proy, a.H, a.Q)
        elif a.cmd == 'aparejo':
            _, L = aparejo(a.m, a.ramales, a.eta_polea, a.eta, a.desvios, a.h)
        elif a.cmd == 'cable':
            _, L = cable(a.m, a.ramales, a.eta, a.cs, a.construccion, a.alma, a.grado, a.grupo, a.gancho, a.eta_polea, a.desvios)
        elif a.cmd == 'eslinga':
            _, L = eslinga(a.m, a.ramales, a.angulo, a.desde, a.portantes)
        elif a.cmd == 'autoelevador':
            _, L = autoelevador(a.Qn, a.cn, a.c, a.x)
        else:
            _, L = grua(a.ciclos, a.kp, a.horas, a.km, a.carga, a.carro, a.puente, a.luz, a.aprox, a.phi, a.hc, a.vh)
    except ValueError as ex:
        print('transporte.py: %s' % ex, file=sys.stderr)
        return 2
    print('\n'.join(L))
    return 0


if __name__ == '__main__':
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(errors='replace')
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
