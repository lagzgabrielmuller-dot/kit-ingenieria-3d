#!/usr/bin/env python3
"""elementos.py - calculadoras de elementos de maquinas (solo biblioteca estandar).

Unidades: mm, N, N·m, MPa, kN y rpm. Cada comando imprime formula, reemplazo y resultado.
  tornillo --d 12 [--paso P] [--clase 8.8] [--k 0.75] [--K 0.2] [--carga N]
           area resistente, carga de prueba, precarga y torque de apriete (ISO 898-1; Shigley cap. 8)
  eje --M N·m --T N·m --sut MPa --sy MPa (--d mm | --n 2) [--kf 1 --kfs 1 --acabado maquinado --confiabilidad 0.99]
           eje que gira con flexion y torque constante: fatiga por ED-Goodman y fluencia por von Mises (Shigley cap. 6 y 7)
  chaveta --d mm --T N·m --sy MPa [--n 2]   chaveta paralela DIN 6885-1 y largo por corte y aplastamiento
  rodamiento --C kN (--P kN | --fr kN --fa kN --x X --y Y) --rpm n [--tipo bolas|rodillos] [--horas H]
           vida L10 (ISO 281); con --horas, la capacidad C necesaria
  correa --D mm --d mm (--C mm | --L mm) [--rpm n]     correa en V: largo, distancia entre centros, angulos, velocidad
  cadena --z1 --z2 --paso mm --C mm [--rpm n]           cadena de rodillos: eslabones (par), distancia real, diametros
  engranaje --m mm --z1 --z2 [--b mm --T N·m --rpm n --sy MPa --n 2 --perfil fresado]   cilindrico recto: geometria y Lewis
  soldadura --cateto mm --largo mm --F N [--cordones 1] [--electrodo E70]   filete en corte: garganta, tension y n (AWS)
  demo     verifica contra tablas de la ISO 898-1 y un ejemplo de Shigley
"""
import argparse
import math
import sys

# ------------------------------------------------------------------------------------------ datos
PASO_GRUESO = {3: 0.5, 4: 0.7, 5: 0.8, 6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 14: 2.0, 16: 2.0, 18: 2.5, 20: 2.5,
               22: 2.5, 24: 3.0, 27: 3.0, 30: 3.5, 33: 3.5, 36: 4.0}   # ISO 261/262, paso grueso
# ISO 898-1: Rm min, limite de fluencia min (ReL, Rp0,2 o Rpf) y tension bajo carga de prueba Sp nominal, en MPa
CLASES = {'4.6': (400, 240, 225), '4.8': (420, 340, 310), '5.6': (500, 300, 280), '5.8': (520, 420, 380),
          '6.8': (600, 480, 440), '8.8': (800, 640, 580), '8.8>16': (830, 660, 600), '9.8': (900, 720, 650),
          '10.9': (1040, 940, 830), '12.9': (1220, 1100, 970)}
ACABADOS = {'rectificado': (1.58, -0.085), 'maquinado': (4.51, -0.265), 'estirado': (4.51, -0.265),
            'laminado': (57.7, -0.718), 'forjado': (272.0, -0.995)}   # Shigley, tabla 6-2 (Sut en MPa)
CONFIABILIDAD = {0.5: 1.0, 0.9: 0.897, 0.95: 0.868, 0.99: 0.814, 0.999: 0.753, 0.9999: 0.702}   # Shigley, tabla 6-5
DIN6885 = [(6, 8, 2, 2), (8, 10, 3, 3), (10, 12, 4, 4), (12, 17, 5, 5), (17, 22, 6, 6), (22, 30, 8, 7), (30, 38, 10, 8),
           (38, 44, 12, 8), (44, 50, 14, 9), (50, 58, 16, 10), (58, 65, 18, 11), (65, 75, 20, 12), (75, 85, 22, 14),
           (85, 95, 25, 14), (95, 110, 28, 16), (110, 130, 32, 18)]   # mas de, hasta, b, h [mm]
LARGOS_CHAVETA = [6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40, 45, 50, 56, 63, 70, 80, 90, 100, 110, 125,
                  140, 160, 180, 200, 220, 250]
LEWIS = [(12, 0.245), (13, 0.261), (14, 0.277), (15, 0.290), (16, 0.296), (17, 0.303), (18, 0.309), (19, 0.314),
         (20, 0.322), (21, 0.328), (22, 0.331), (24, 0.337), (26, 0.346), (28, 0.353), (30, 0.359), (34, 0.371),
         (38, 0.384), (43, 0.397), (50, 0.409), (60, 0.422), (75, 0.435), (100, 0.447), (150, 0.460), (300, 0.472),
         (400, 0.480)]   # Shigley, tabla 14-2: angulo de presion 20°, diente normal; cremallera 0,485
ELECTRODOS = {'E60': (427, 345), 'E70': (482, 393), 'E80': (551, 462), 'E90': (620, 531), 'E100': (689, 600),
              'E120': (827, 737)}   # Shigley, tabla 9-3: Sut y Sy del metal de aporte [MPa]


def n(x, d=2):
    return ('%.*f' % (d, x)).replace('.', ',')


def miles(x):
    """Entero con espacio como separador de miles (SI): 48 875."""
    s = '%.0f' % x
    return s if len(s) <= 4 else '{:,}'.format(int(round(x))).replace(',', ' ')


# ------------------------------------------------------------------------------------------ tornillo
def area_resistente(d, paso):
    d2 = d - 0.649519 * paso
    d3 = d - 1.226869 * paso
    return math.pi / 4 * ((d2 + d3) / 2) ** 2


def tornillo(d, paso=None, clase='8.8', k=0.75, K=0.2, carga=None):
    if paso is None:
        if d not in PASO_GRUESO:
            raise ValueError('M%g no está en la tabla de paso grueso: indicá --paso' % d)
        paso = PASO_GRUESO[d]
    clave = clase + ('>16' if clase == '8.8' and d > 16 else '')
    if clave not in CLASES:
        raise ValueError('clase %s desconocida (hay: %s)' % (clase, ', '.join(c for c in CLASES if '>' not in c)))
    if clase == '9.8' and d > 16:
        raise ValueError('la clase 9.8 es solo para d ≤ 16 mm')
    Rm, Re, Sp = CLASES[clave]
    As = area_resistente(d, paso)
    Fp = As * Sp
    Fi = k * Fp
    T = K * Fi * d / 1000
    L = ['Tornillo M%g × %g, clase %s (ISO 898-1: Rm ≥ %d MPa, Re ≥ %d MPa, Sp = %d MPa)' % (d, paso, clase, Rm, Re, Sp),
         'Área resistente: As = π/4·((d2 + d3)/2)², d2 = d − 0,6495·P, d3 = d − 1,2269·P → As = %s mm²' % n(As, 1),
         'Carga de prueba: Fp = As·Sp = %s·%d = %s N' % (n(As, 1), Sp, miles(Fp)),
         'Precarga: Fi = k·Fp = %s·%s = %s N (k = 0,75 si se vuelve a desarmar; 0,90 si es permanente)' % (n(k, 2), miles(Fp), miles(Fi)),
         'Torque de apriete: T = K·Fi·d = %s·%s·%g mm = %s N·m (K = 0,2 sin dato de lubricación)' % (n(K, 2), miles(Fi), d, n(T, 1))]
    r = {'As': As, 'Fp': Fp, 'Fi': Fi, 'T': T, 'Rm': Rm, 'Re': Re, 'Sp': Sp}
    if carga:
        r['n'] = As * Re / carga
        L.append('Con una carga de tracción de %s N (sin contar la precarga): n = As·Re/F = %s' % (miles(carga), n(r['n'], 2)))
    return r, L


# ------------------------------------------------------------------------------------------ eje
def factor_tamano(d):
    if d <= 51:
        return 1.24 * d ** -0.107
    return 1.51 * d ** -0.157


def limite_fatiga(sut, d, acabado, conf):
    if acabado not in ACABADOS:
        raise ValueError('acabado: %s' % ', '.join(ACABADOS))
    if conf not in CONFIABILIDAD:
        raise ValueError('confiabilidad: %s' % ', '.join(str(c) for c in CONFIABILIDAD))
    se_p = 0.5 * sut if sut <= 1400 else 700.0
    a, b = ACABADOS[acabado]
    ka, kb, ke = a * sut ** b, factor_tamano(d), CONFIABILIDAD[conf]
    return ka * kb * ke * se_p, ka, kb, ke, se_p


def eje_eval(d, M, T, sut, sy, kf=1.0, kfs=1.0, acabado='maquinado', conf=0.99):
    """Eje que gira: el momento flector es alternante y el torque, constante."""
    c = 1000 / (math.pi * d ** 3)
    sa = 32 * kf * M * c                       # von Mises de la parte alternante
    sm = math.sqrt(3) * 16 * kfs * T * c       # von Mises de la parte media
    smax = math.sqrt((32 * kf * M * c) ** 2 + 3 * (16 * kfs * T * c) ** 2)
    se, ka, kb, ke, se_p = limite_fatiga(sut, d, acabado, conf)
    nf = 1 / (sa / se + sm / sut)
    ny = sy / smax
    return {'d': d, 'sa': sa, 'sm': sm, 'smax': smax, 'se': se, 'ka': ka, 'kb': kb, 'ke': ke, 'se_p': se_p, 'nf': nf, 'ny': ny}


def eje(M, T, sut, sy, d=None, n_obj=None, kf=1.0, kfs=1.0, acabado='maquinado', conf=0.99):
    if d is None:
        if not n_obj:
            raise ValueError('indicá --d para verificar o --n para calcular el diámetro')
        lo, hi = 3.0, 500.0
        f = lambda x: min(eje_eval(x, M, T, sut, sy, kf, kfs, acabado, conf)['nf'],
                          eje_eval(x, M, T, sut, sy, kf, kfs, acabado, conf)['ny']) - n_obj
        if f(hi) < 0:
            raise ValueError('ni con 500 mm se llega a n = %g' % n_obj)
        for _ in range(100):
            m = (lo + hi) / 2
            if f(m) < 0:
                lo = m
            else:
                hi = m
        r = eje_eval(hi, M, T, sut, sy, kf, kfs, acabado, conf)
        r['d_min'] = hi
    else:
        r = eje_eval(d, M, T, sut, sy, kf, kfs, acabado, conf)
    L = ['Eje que gira: M = %s N·m (flexión alternante), T = %s N·m (torque constante); Sut = %s MPa, Sy = %s MPa'
         % (n(M, 1), n(T, 1), n(sut, 0), n(sy, 0)),
         'Límite de fatiga: Se = ka·kb·ke·Se\', Se\' = 0,5·Sut = %s MPa; ka = %s (%s), kb = %s, ke = %s (confiabilidad %s) → Se = %s MPa'
         % (n(r['se_p'], 1), n(r['ka'], 3), acabado, n(r['kb'], 3), n(r['ke'], 3), ('%g' % conf).replace('.', ','), n(r['se'], 1)),
         'Tensiones (d = %s mm, Kf = %s, Kfs = %s): σa = 32·Kf·M/(π·d³) = %s MPa; σm = √3·16·Kfs·T/(π·d³) = %s MPa'
         % (n(r['d'], 2), n(kf, 2), n(kfs, 2), n(r['sa'], 1), n(r['sm'], 1)),
         'Fatiga (ED-Goodman): 1/nf = σa/Se + σm/Sut → nf = %s' % n(r['nf'], 2),
         'Fluencia (von Mises máximo): σmax = √((32·Kf·M/(π·d³))² + 3·(16·Kfs·T/(π·d³))²) = %s MPa → ny = Sy/σmax = %s'
         % (n(r['smax'], 1), n(r['ny'], 2))]
    if 'd_min' in r:
        L.append('Diámetro mínimo para n = %s: d = %s mm (redondear hacia arriba a una medida comercial y verificar con esa)'
                 % (n(n_obj, 2), n(r['d_min'], 2)))
    if kf == 1.0 and kfs == 1.0:
        L.append('AVISO: Kf = Kfs = 1 supone un eje liso; en hombros, chaveteros y ranuras van los factores de concentración.')
    if r['d'] > 254:
        L.append('AVISO: kb está fuera de su rango (2,79 a 254 mm).')
    return r, L


# ------------------------------------------------------------------------------------------ chaveta
def chaveta(d, T, sy, n_obj=2.0):
    fila = next((f for f in DIN6885 if f[0] < d <= f[1]), None)
    if not fila:
        raise ValueError('la tabla cubre ejes de más de 6 hasta 130 mm')
    b, h = fila[2], fila[3]
    F = 2000 * T / d
    ssy = 0.577 * sy
    l_corte = F * n_obj / (b * ssy)
    l_apl = F * n_obj / (h / 2 * sy)
    l_min = max(l_corte, l_apl)
    l_norm = next((x for x in LARGOS_CHAVETA if x >= l_min), None)
    L = ['Eje de %s mm → chaveta DIN 6885-1 de %d × %d mm (b × h), tramo de más de %d hasta %d mm' % (n(d, 1), b, h, fila[0], fila[1]),
         'Fuerza en la superficie del eje: F = 2·T/d = 2·%s N·m/%s mm = %s N' % (n(T, 1), n(d, 1), miles(F)),
         'Corte: L ≥ F·n/(b·Ssy), Ssy = 0,577·Sy = %s MPa → L ≥ %s mm' % (n(ssy, 1), n(l_corte, 1)),
         'Aplastamiento (la mitad de la altura apoya en el cubo): L ≥ F·n/((h/2)·Sy) → L ≥ %s mm' % n(l_apl, 1),
         'Largo mínimo: %s mm → largo normalizado %s mm (serie de largos de la norma; confirmar con el proveedor)'
         % (n(l_min, 1), l_norm if l_norm else 'mayor que 250')]
    if l_min > 1.5 * d:
        L.append('AVISO: el largo pasa 1,5·d: conviene dos chavetas a 180°, un estriado o un eje más grueso.')
    return {'b': b, 'h': h, 'F': F, 'l_corte': l_corte, 'l_apl': l_apl, 'l_min': l_min, 'l_norm': l_norm}, L


# ------------------------------------------------------------------------------------------ rodamiento
def rodamiento(C, rpm, P=None, fr=None, fa=None, x=None, y=None, tipo='bolas', horas=None):
    p = 3.0 if tipo == 'bolas' else 10 / 3
    L = []
    if P is None:
        if fr is None or x is None:
            raise ValueError('indicá --P o --fr y --fa con los factores --x e --y del catálogo')
        P = x * fr + (y or 0) * (fa or 0)
        L.append('Carga equivalente: P = X·Fr + Y·Fa = %s·%s + %s·%s = %s kN' % (n(x, 2), n(fr, 2), n(y or 0, 2), n(fa or 0, 2), n(P, 2)))
    L10 = (C / P) ** p
    L10h = 1e6 / (60 * rpm) * L10
    L.append('Vida L10 = (C/P)^p = (%s/%s)^%s = %s millones de vueltas (p = %s, %s)'
             % (n(C, 2), n(P, 2), '3' if p == 3 else '10/3', n(L10, 1), '3' if p == 3 else '10/3', tipo))
    L.append('L10h = 10⁶·L10/(60·n) = %s h a %s rpm (el 90 %% de los rodamientos llega a esa vida)' % (miles(L10h), n(rpm, 0)))
    r = {'P': P, 'L10': L10, 'L10h': L10h}
    if horas:
        r['C_req'] = P * (60 * rpm * horas / 1e6) ** (1 / p)
        L.append('Para %s h: C ≥ P·(60·n·Lh/10⁶)^(1/p) = %s kN' % (miles(horas), n(r['C_req'], 2)))
    return r, L


# ------------------------------------------------------------------------------------------ correa
def correa(D, d, C=None, Lc=None, rpm=None):
    if D < d:
        D, d = d, D
    S, dif = D + d, D - d
    if C is not None:
        Lc = 2 * C + math.pi * S / 2 + dif ** 2 / (4 * C)
    elif Lc is not None:
        A = Lc - math.pi * S / 2
        disc = A ** 2 - 2 * dif ** 2
        if disc < 0:
            raise ValueError('la correa es demasiado corta para esas poleas')
        C = 0.25 * (A + math.sqrt(disc))
    else:
        raise ValueError('indicá --C (distancia entre centros) o --L (largo de la correa)')
    if dif / (2 * C) >= 1:
        raise ValueError('poleas demasiado grandes para esa distancia entre centros')
    phi = math.asin(dif / (2 * C))
    th_d, th_D = math.degrees(math.pi - 2 * phi), math.degrees(math.pi + 2 * phi)
    L = ['Relación de transmisión: i = D/d = %s/%s = %s' % (n(D, 0), n(d, 0), n(D / d, 3)),
         'Largo primitivo: L = 2·C + π·(D + d)/2 + (D − d)²/(4·C) = %s mm, con C = %s mm' % (n(Lc, 1), n(C, 1)),
         'Ángulo de contacto: polea chica θd = 180° − 2·asen((D − d)/(2·C)) = %s°; polea grande %s°' % (n(th_d, 1), n(th_D, 1))]
    r = {'L': Lc, 'C': C, 'th_d': th_d, 'th_D': th_D}
    if rpm:
        v = math.pi * d * rpm / 60000
        r['v'] = v
        L.append('Velocidad de la correa: v = π·d·n/60 000 = %s m/s (en V conviene entre 5 y 25 m/s)' % n(v, 2))
        if not 5 <= v <= 25:
            L.append('AVISO: velocidad fuera de 5 a 25 m/s.')
    if not D <= C <= 3 * S:
        L.append('AVISO: Shigley recomienda D ≤ C ≤ 3·(D + d) = %s mm.' % n(3 * S, 0))
    L.append('Para elegir la cantidad de correas: potencia de diseño = P·Ks, y potencia por correa del catálogo corregida por ángulo y largo.')
    return r, L


# ------------------------------------------------------------------------------------------ cadena
def cadena(z1, z2, paso, C, rpm=None):
    if z2 < z1:
        z1, z2 = z2, z1
    Lp = 2 * C / paso + (z1 + z2) / 2 + (z2 - z1) ** 2 / (4 * math.pi ** 2 * C / paso)
    Lpar = 2 * math.ceil(Lp / 2)
    A = (z1 + z2) / 2 - Lpar
    Creal = paso / 4 * (-A + math.sqrt(A ** 2 - 8 * ((z2 - z1) / (2 * math.pi)) ** 2))
    D1, D2 = paso / math.sin(math.pi / z1), paso / math.sin(math.pi / z2)
    var = (math.pi / z1) * (1 / math.sin(math.pi / z1) - 1 / math.tan(math.pi / z1))
    L = ['Relación: i = z2/z1 = %d/%d = %s' % (z2, z1, n(z2 / z1, 3)),
         'Diámetros primitivos: D = p/sen(180°/z) → %s mm y %s mm' % (n(D1, 1), n(D2, 1)),
         'Largo en eslabones: L/p = 2·C/p + (z1 + z2)/2 + (z2 − z1)²/(4·π²·C/p) = %s → %d (número par, sin eslabón acodado)' % (n(Lp, 2), Lpar),
         'Distancia entre centros real con %d eslabones: %s mm' % (Lpar, n(Creal, 1)),
         'Variación de velocidad por efecto poligonal: ΔV/V = (π/z1)·(1/sen(180°/z1) − 1/tan(180°/z1)) = %s %%' % n(100 * var, 2)]
    r = {'Lp': Lp, 'Lpar': Lpar, 'C': Creal, 'D1': D1, 'D2': D2, 'var': var}
    if rpm:
        r['v'] = z1 * paso * rpm / 60000
        L.append('Velocidad de la cadena: v = z1·p·n/60 000 = %s m/s' % n(r['v'], 2))
    if z1 < 17:
        L.append('AVISO: con menos de 17 dientes en el piñón la cadena marcha a los saltos (Shigley).')
    if not 30 <= Creal / paso <= 50:
        L.append('AVISO: Shigley recomienda una distancia entre centros de 30 a 50 pasos (acá %s).' % n(Creal / paso, 1))
    return r, L


# ------------------------------------------------------------------------------------------ engranaje
def y_lewis(z):
    if z < 12:
        raise ValueError('la tabla de Lewis empieza en 12 dientes')
    if z >= 400:
        return 0.480 + (0.485 - 0.480) * min(1.0, (z - 400) / 600)
    for (z0, y0), (z1, y1) in zip(LEWIS, LEWIS[1:]):
        if z0 <= z <= z1:
            return y0 + (y1 - y0) * (z - z0) / (z1 - z0)
    return LEWIS[-1][1]


def factor_dinamico(V, perfil):
    if perfil == 'fundido':
        return (3.05 + V) / 3.05
    if perfil == 'fresado':
        return (6.1 + V) / 6.1
    if perfil == 'generado':
        return (3.56 + math.sqrt(V)) / 3.56
    if perfil == 'rectificado':
        return math.sqrt((5.56 + math.sqrt(V)) / 5.56)
    raise ValueError('perfil: fundido, fresado, generado o rectificado')


def engranaje(m, z1, z2, b=None, T=None, rpm=None, sy=None, n_obj=None, perfil='fresado'):
    d1, d2 = m * z1, m * z2
    a = m * (z1 + z2) / 2
    p = math.pi * m
    L = ['Módulo %s mm, z1 = %d, z2 = %d → i = %s; paso circular p = π·m = %s mm' % (n(m, 2), z1, z2, n(z2 / z1, 3), n(p, 2)),
         'Diámetros primitivos d = m·z: %s y %s mm; exteriores m·(z + 2): %s y %s mm; de pie m·(z − 2,5): %s y %s mm'
         % (n(d1, 1), n(d2, 1), n(m * (z1 + 2), 1), n(m * (z2 + 2), 1), n(m * (z1 - 2.5), 1), n(m * (z2 - 2.5), 1)),
         'Distancia entre centros: a = m·(z1 + z2)/2 = %s mm' % n(a, 1)]
    r = {'d1': d1, 'd2': d2, 'a': a}
    if z1 < 18:
        L.append('AVISO: con 20° y diente normal, menos de 18 dientes en el piñón puede dar interferencia (Shigley, cap. 13).')
    if T and b and rpm:
        Ft = 2000 * T / d1
        V = math.pi * d1 * rpm / 60000
        Kv = factor_dinamico(V, perfil)
        Y = y_lewis(z1)
        sigma = Kv * Ft / (b * m * Y)
        r.update({'Ft': Ft, 'V': V, 'Kv': Kv, 'Y': Y, 'sigma': sigma})
        L += ['Fuerza tangencial: Ft = 2·T/d1 = %s N; radial Fr = Ft·tg 20° = %s N' % (miles(Ft), miles(Ft * math.tan(math.radians(20)))),
              'Velocidad en la primitiva: V = %s m/s → Kv = %s (perfil %s)' % (n(V, 2), n(Kv, 3), perfil),
              'Lewis: σ = Kv·Ft/(b·m·Y), Y(%d) = %s → σ = %s MPa' % (z1, n(Y, 3), n(sigma, 1))]
        if sy:
            r['n'] = sy / sigma
            L.append('Factor de seguridad a la fluencia: n = Sy/σ = %s%s' % (n(r['n'], 2), (' (objetivo %s)' % n(n_obj, 2)) if n_obj else ''))
        if not 3 * p <= b <= 5 * p:
            L.append('AVISO: el ancho conviene entre 3·p y 5·p (%s a %s mm).' % (n(3 * p, 1), n(5 * p, 1)))
        L.append('Lewis es un control de primera mano; para el diseño final, el método AGMA (flexión y picado).')
    return r, L


# ------------------------------------------------------------------------------------------ soldadura
def soldadura(cateto, largo, F, cordones=1, electrodo='E70'):
    if electrodo not in ELECTRODOS:
        raise ValueError('electrodo: %s' % ', '.join(ELECTRODOS))
    sut_e, _ = ELECTRODOS[electrodo]
    a = 0.707 * cateto
    A = a * largo * cordones
    tau = F / A
    tau_adm = 0.30 * sut_e
    L = ['Garganta: a = 0,707·cateto = 0,707·%s = %s mm; área A = a·L·cordones = %s mm²' % (n(cateto, 1), n(a, 2), n(A, 1)),
         'Tensión de corte en la garganta: τ = F/A = %s/%s = %s MPa' % (miles(F), n(A, 1), n(tau, 1)),
         'Admisible (AWS): τadm = 0,30·Sut del electrodo = 0,30·%d = %s MPa (%sXX) → n = τadm/τ = %s'
         % (sut_e, n(tau_adm, 1), electrodo, n(tau_adm / tau, 2)),
         'Largo mínimo para esa carga: L ≥ F/(τadm·a·cordones) = %s mm' % n(F / (tau_adm * a * cordones), 1),
         'Falta controlar el metal base (corte y tracción) y, si hay excentricidad, la torsión o flexión del grupo de cordones.']
    return {'a': a, 'tau': tau, 'tau_adm': tau_adm, 'n': tau_adm / tau}, L


# ------------------------------------------------------------------------------------------ demo
def cerca(x, y, tol):
    return abs(x - y) <= tol


def cmd_demo():
    ok = []
    tabla = {6: 20.1, 8: 36.6, 10: 58.0, 12: 84.3, 14: 115, 16: 157, 20: 245, 24: 353, 30: 561, 36: 817}  # ISO 898-1
    peor = max(abs(area_resistente(d, PASO_GRUESO[d]) / v - 1) for d, v in tabla.items())
    ok.append(('área resistente M6 a M36 contra la tabla de la ISO 898-1 (peor %s %%)' % n(100 * peor, 2), peor < 0.004))
    r, _ = tornillo(12, clase='8.8')
    ok.append(('M12 8.8: carga de prueba %s N (580·84,3 = 48 894 N)' % miles(r['Fp']), cerca(r['Fp'], 48894, 60)))
    r, _ = tornillo(20, clase='8.8')
    ok.append(('M20 8.8 usa Sp = 600 MPa (d > 16 mm)', r['Sp'] == 600))
    # Shigley, cap. 7: eje de 1,1 in, M = 1260 lbf·in, T = 1100 lbf·in, Sut 105 kpsi, Sy 82 kpsi, Kf 1,58, Kfs 1,39,
    # maquinado, 99 % de confiabilidad → nf (ED-Goodman) = 1,62
    lbin, kpsi = 0.112985, 6.894757
    r = eje_eval(1.1 * 25.4, 1260 * lbin, 1100 * lbin, 105 * kpsi, 82 * kpsi, 1.58, 1.39, 'maquinado', 0.99)
    ok.append(('eje del ejemplo de Shigley: nf = %s (libro: 1,62)' % n(r['nf'], 3), cerca(r['nf'], 1.62, 0.015)))
    r2, _ = eje(1260 * lbin, 1100 * lbin, 105 * kpsi, 82 * kpsi, n_obj=r['nf'], kf=1.58, kfs=1.39, conf=0.99)
    ok.append(('diámetro despejado para ese n vuelve a %s mm' % n(r2['d_min'], 2), cerca(r2['d_min'], 27.94, 0.05)))
    r, _ = chaveta(35, 150, 350, 2)
    F = 2000 * 150 / 35
    ok.append(('chaveta de eje de 35 mm: 10 × 8 y largos a mano', r['b'] == 10 and r['h'] == 8
               and cerca(r['l_corte'], F * 2 / (10 * 0.577 * 350), 1e-9) and cerca(r['l_apl'], F * 2 / (4 * 350), 1e-9)))
    r, _ = rodamiento(14, 1450, P=2, horas=3942.5)
    ok.append(('rodamiento C/P = 7 a 1450 rpm: L10h = %s h (343·10⁶/87 000) y C necesaria = %s kN' % (miles(r['L10h']), n(r['C_req'], 3)),
               cerca(r['L10h'], 343e6 / 87000, 0.01) and cerca(r['C_req'], 14, 1e-3)))
    r, _ = correa(250, 100, C=500, rpm=1450)
    rb, _ = correa(250, 100, Lc=r['L'])
    ok.append(('correa: el largo y la distancia entre centros son inversos (C = %s mm)' % n(rb['C'], 3), cerca(rb['C'], 500, 1e-6)))
    r, _ = cadena(17, 34, 12.7, 500)
    Lchk = 2 * r['C'] / 12.7 + 51 / 2 + 17 ** 2 / (4 * math.pi ** 2 * r['C'] / 12.7)
    ok.append(('cadena: %d eslabones y la distancia real los reproduce' % r['Lpar'], r['Lpar'] % 2 == 0 and cerca(Lchk, r['Lpar'], 1e-6)))
    r, _ = engranaje(3, 25, 75, b=36, T=100, rpm=1000, sy=400)
    Ft = 2000 * 100 / 75
    V = math.pi * 75 * 1000 / 60000
    sig = (6.1 + V) / 6.1 * Ft / (36 * 3 * 0.3415)
    ok.append(('engranaje m 3, z 25/75: a = 150 mm, Y(25) = 0,3415 y Lewis a mano', cerca(r['a'], 150, 1e-9) and cerca(r['Y'], 0.3415, 1e-9)
               and cerca(r['sigma'], sig, 1e-6)))
    r, _ = soldadura(6, 100, 30000, 2, 'E70')
    ok.append(('soldadura: τ = 30 000/(2·0,707·6·100) = %s MPa' % n(r['tau'], 2), cerca(r['tau'], 30000 / (2 * 0.707 * 6 * 100), 1e-9)))
    for nombre, bien in ok:
        print('  %s %s' % ('ok ' if bien else 'MAL', nombre))
    todo = all(b for _, b in ok)
    print('DEMO %s' % ('OK' if todo else 'FALLO'))
    return 0 if todo else 1


# ------------------------------------------------------------------------------------------ principal
def construir_parser():
    ap = argparse.ArgumentParser(prog='elementos.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('tornillo')
    p.add_argument('--d', type=float, required=True)
    p.add_argument('--paso', type=float)
    p.add_argument('--clase', default='8.8')
    p.add_argument('--k', type=float, default=0.75)
    p.add_argument('--K', type=float, default=0.2)
    p.add_argument('--carga', type=float)
    p = sp.add_parser('eje')
    for x in ('M', 'T', 'sut', 'sy'):
        p.add_argument('--' + x, type=float, required=True)
    p.add_argument('--d', type=float)
    p.add_argument('--n', type=float)
    p.add_argument('--kf', type=float, default=1.0)
    p.add_argument('--kfs', type=float, default=1.0)
    p.add_argument('--acabado', default='maquinado', choices=sorted(ACABADOS))
    p.add_argument('--confiabilidad', type=float, default=0.99)
    p = sp.add_parser('chaveta')
    for x in ('d', 'T', 'sy'):
        p.add_argument('--' + x, type=float, required=True)
    p.add_argument('--n', type=float, default=2.0)
    p = sp.add_parser('rodamiento')
    p.add_argument('--C', type=float, required=True)
    p.add_argument('--rpm', type=float, required=True)
    for x in ('P', 'fr', 'fa', 'x', 'y', 'horas'):
        p.add_argument('--' + x, type=float)
    p.add_argument('--tipo', default='bolas', choices=['bolas', 'rodillos'])
    p = sp.add_parser('correa')
    p.add_argument('--D', type=float, required=True)
    p.add_argument('--d', type=float, required=True)
    p.add_argument('--C', type=float)
    p.add_argument('--L', type=float)
    p.add_argument('--rpm', type=float)
    p = sp.add_parser('cadena')
    p.add_argument('--z1', type=int, required=True)
    p.add_argument('--z2', type=int, required=True)
    p.add_argument('--paso', type=float, required=True)
    p.add_argument('--C', type=float, required=True)
    p.add_argument('--rpm', type=float)
    p = sp.add_parser('engranaje')
    p.add_argument('--m', type=float, required=True)
    p.add_argument('--z1', type=int, required=True)
    p.add_argument('--z2', type=int, required=True)
    for x in ('b', 'T', 'rpm', 'sy', 'n'):
        p.add_argument('--' + x, type=float)
    p.add_argument('--perfil', default='fresado', choices=['fundido', 'fresado', 'generado', 'rectificado'])
    p = sp.add_parser('soldadura')
    for x in ('cateto', 'largo', 'F'):
        p.add_argument('--' + x, type=float, required=True)
    p.add_argument('--cordones', type=int, default=1)
    p.add_argument('--electrodo', default='E70', choices=sorted(ELECTRODOS))
    sp.add_parser('demo')
    return ap


def main(argv=None):
    a = construir_parser().parse_args(argv)
    try:
        if a.cmd == 'demo':
            return cmd_demo()
        if a.cmd == 'tornillo':
            _, L = tornillo(a.d if a.d != int(a.d) else int(a.d), a.paso, a.clase, a.k, a.K, a.carga)
        elif a.cmd == 'eje':
            _, L = eje(a.M, a.T, a.sut, a.sy, a.d, a.n, a.kf, a.kfs, a.acabado, a.confiabilidad)
        elif a.cmd == 'chaveta':
            _, L = chaveta(a.d, a.T, a.sy, a.n)
        elif a.cmd == 'rodamiento':
            _, L = rodamiento(a.C, a.rpm, a.P, a.fr, a.fa, a.x, a.y, a.tipo, a.horas)
        elif a.cmd == 'correa':
            _, L = correa(a.D, a.d, a.C, a.L, a.rpm)
        elif a.cmd == 'cadena':
            _, L = cadena(a.z1, a.z2, a.paso, a.C, a.rpm)
        elif a.cmd == 'engranaje':
            _, L = engranaje(a.m, a.z1, a.z2, a.b, a.T, a.rpm, a.sy, a.n, a.perfil)
        else:
            _, L = soldadura(a.cateto, a.largo, a.F, a.cordones, a.electrodo)
    except ValueError as ex:
        print('elementos.py: %s' % ex, file=sys.stderr)
        return 2
    print('\n'.join(L))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
