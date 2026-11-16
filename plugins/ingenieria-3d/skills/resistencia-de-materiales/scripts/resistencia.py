#!/usr/bin/env python3
"""resistencia.py - resistencia de materiales con memoria de cálculo (solo biblioteca estándar).

Cada comando imprime fórmula, reemplazo y resultado con coma decimal, listo para la memoria de cálculo.
Unidades: fuerzas en kN, momentos flectores en kN·m, torque en N·m; largos de barras, vigas y columnas en m;
medidas de secciones en mm; I en cm⁴ y W en cm³ (como los catálogos); tensiones, E y G en MPa.
Los números aceptan coma o punto decimal (2,5 o 2.5).

  axial    --F kN --L m (--A mm² | --d mm | --tubo DxE | --perfil IPN200) [--dT °C --impedida --holgura mm] [--fy MPa]
           tracción o compresión (ley de Hooke) y dilatación térmica libre o impedida
  corte    (--F kN | --T N·m --dp mm) --d mm [--planos 1|2] [--pernos n] [--t mm] [--fy MPa]
           pernos y pasadores en corte simple o doble, y aplastamiento
  torsion  (--T N·m | --P kW --rpm n) --d mm [--di mm] [--L m] [--G MPa] [--tadm MPa] [--giro-adm °/m] [--fy MPa]
           ejes macizos y huecos: tensión, ángulo de giro y diámetro mínimo
  viga     --tipo apoyada|voladizo --L m [--P kN@x] [--q kN/m[@x1:x2]] [--M kN·m@x] [--apoyos x1:x2]
           (--I cm⁴ [--W cm³] | --perfil IPN200 | --rect BxH | --circ D | --tubo DxE | --elegir IPN --sadm MPa)
           [--E MPa] [--limite 250] [--csv archivo.csv]
           reacciones, corte y momento máximos, tensiones y flecha por integración numérica (Simpson)
  pandeo   --L m (--vinculos art-art|emp-libre|emp-art|emp-emp | --K k) (--perfil | --tubo | --circ | --rect | --A --I)
           [--fy 235] [--E] [--P kN] [--Pu kN] [--tetmajer a,b,λ0]      Euler, Johnson y CIRSOC 301 (E.2)
  mohr     --sx MPa --sy MPa --txy MPa [--theta °] [--fy MPa]   tensiones principales, τ máxima, von Mises y Tresca
  seccion  rect|circ|tubo|doble-t|angulo|perfil|compuesta (medidas en mm)   A, I, W, i; Steiner en la compuesta
  perfiles IPN|UPN|L [--W cm³] [--I cm⁴] [--i cm]               tabla de catálogo y el más liviano que cumple
  demo     reproduce los ejemplos del SKILL.md y de libro, y compara la flecha numérica con las fórmulas cerradas
"""
import argparse
import math
import sys

# ------------------------------------------------------------------------------------------ datos
E_ACERO = 200000.0      # MPa   CIRSOC 301-2005, A.3.5 (a)
G_ACERO = 77200.0       # MPa   CIRSOC 301-2005, A.3.5 (b)
ALFA_ACERO = 12e-6      # 1/°C  CIRSOC 301-2005, A.3.5 (d)
FY_F24 = 235.0          # MPa   acero F-24 (ejemplos de aplicación del CIRSOC 303 y del 301)
PHI_C = 0.85            # CIRSOC 301-2005, E.2

# IPN, doble T de alas inclinadas: ArcelorMittal, catálogo de perfiles, tabla IPN (medidas según EN 10365:2017)
#      h    b    tw    tf    A cm²  G kg/m  Iy cm⁴  Wy cm³  Iz cm⁴  Wz cm³
IPN = {
    80: (80, 42, 3.9, 5.9, 7.6, 5.9, 77.8, 19.5, 6.29, 3.00),
    100: (100, 50, 4.5, 6.8, 10.6, 8.3, 171, 34.2, 12.2, 4.88),
    120: (120, 58, 5.1, 7.7, 14.2, 11.1, 328, 54.7, 21.5, 7.41),
    140: (140, 66, 5.7, 8.6, 18.2, 14.3, 573, 81.9, 35.2, 10.7),
    160: (160, 74, 6.3, 9.5, 22.8, 17.9, 935, 117, 54.7, 14.8),
    180: (180, 82, 6.9, 10.4, 27.9, 21.9, 1450, 161, 81.3, 19.8),
    200: (200, 90, 7.5, 11.3, 33.4, 26.2, 2140, 214, 117, 26.0),
    220: (220, 98, 8.1, 12.2, 39.5, 31.1, 3060, 278, 162, 33.1),
    240: (240, 106, 8.7, 13.1, 46.1, 36.2, 4250, 354, 221, 41.7),
    260: (260, 113, 9.4, 14.1, 53.3, 41.9, 5740, 442, 288, 51.0),
    280: (280, 119, 10.1, 15.2, 61.0, 47.9, 7590, 542, 364, 61.2),
    300: (300, 125, 10.8, 16.2, 69.0, 54.2, 9800, 653, 451, 72.2),
    320: (320, 131, 11.5, 17.3, 77.7, 61.0, 12510, 782, 555, 84.7),
    340: (340, 137, 12.2, 18.3, 86.7, 68.0, 15700, 923, 674, 98.4),
    360: (360, 143, 13.0, 19.5, 97.0, 76.1, 19610, 1090, 818, 114),
    380: (380, 149, 13.7, 20.5, 107.0, 84.0, 24010, 1260, 975, 131),
    400: (400, 155, 14.4, 21.6, 117.7, 92.4, 29210, 1460, 1160, 149),
    450: (450, 170, 16.2, 24.3, 146.9, 115, 45850, 2040, 1730, 203),
    500: (500, 185, 18.0, 27.0, 179.4, 141, 68740, 2750, 2480, 268),
    550: (550, 200, 19.0, 30.0, 212.0, 166, 99180, 3610, 3490, 349),
    600: (600, 215, 21.6, 32.4, 253.7, 199, 139000, 4630, 4670, 434),
}
# UPN, U de alas inclinadas: datos técnicos de secciones de STAD (distribuidor; valores indicativos)
UPN = {
    80: (80, 45, 6.0, 8.0, 11.0, 8.6, 106, 26.5, 19.4, 6.36),
    100: (100, 50, 6.0, 8.5, 13.5, 10.6, 206, 41.2, 29.3, 8.49),
    120: (120, 55, 7.0, 9.0, 17.0, 13.3, 364, 60.7, 43.2, 11.1),
    140: (140, 60, 7.0, 10.0, 20.4, 16.0, 605, 86.4, 62.7, 14.8),
    160: (160, 65, 7.5, 10.5, 24.0, 18.8, 925, 116, 85.3, 18.3),
    180: (180, 70, 8.0, 11.0, 28.0, 22.0, 1350, 150, 114, 22.4),
    200: (200, 75, 8.5, 11.5, 32.2, 25.3, 1910, 191, 148, 27.0),
    220: (220, 80, 9.0, 12.5, 37.4, 29.4, 2690, 245, 197, 33.6),
    240: (240, 85, 9.5, 13.0, 42.3, 33.2, 3600, 300, 248, 39.6),
    260: (260, 90, 10.0, 14.0, 48.3, 37.9, 4820, 371, 317, 47.7),
    280: (280, 95, 10.0, 15.0, 53.3, 41.8, 6280, 448, 399, 57.2),
    300: (300, 100, 10.0, 16.0, 58.8, 46.2, 8030, 535, 495, 67.8),
}
# Ángulos de alas iguales: (ala, espesor): radio de raíz r1 [mm] según STAD; radio de borde r2 = r1/2.
# Las propiedades se calculan con las medidas (con los radios); el demo las compara con STAD.
ANGULOS = {(40, 4): 6, (50, 5): 7, (60, 6): 8, (70, 7): 9, (80, 8): 10, (100, 10): 12, (120, 12): 13}
STAD_AREA_L = {(40, 4): 3.08, (50, 5): 4.80, (60, 6): 6.91, (70, 7): 9.40, (80, 8): 12.30, (100, 10): 19.20,
               (120, 12): 27.54}   # cm²
VINCULOS = {'art-art': (1.0, 'articulado en los dos extremos'),
            'emp-libre': (2.0, 'empotrado en la base y libre arriba (ménsula)'),
            'emp-art': (0.7, 'empotrado en un extremo y articulado en el otro (teórico 0,699)'),
            'emp-emp': (0.5, 'empotrado en los dos extremos')}


# ------------------------------------------------------------------------------------------ formato
def n(x, d=2):
    if abs(x) < 0.5 * 10 ** -d:
        x = 0.0
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
    r = signo + ' '.join(grupos) + (',' + dec if dec else '')
    return '0' if r in ('-0', '0') and not dec else r


def g(x, d=3):
    """Número con d cifras significativas, coma decimal y separador de miles."""
    if x == 0:
        return '0'
    dec = max(0, d - 1 - int(math.floor(math.log10(abs(x)))))
    return miles(x, dec)


def med(x):
    """Medida sin ceros de más: 80, 7,5 o 114,3."""
    return ('%.2f' % x).rstrip('0').rstrip('.').replace('.', ',')


def par_neg(x, d=0):
    """Número con paréntesis si es negativo, para un reemplazo."""
    return ('(%s)' % n(x, d)) if x < 0 else n(x, d)


def num(s):
    try:
        return float(str(s).strip().replace(',', '.'))
    except ValueError:
        raise argparse.ArgumentTypeError('no es un número: %s' % s)


def dupla(s):
    """'80x4' o '80×4' → (80.0, 4.0)."""
    partes = str(s).lower().replace('×', 'x').split('x')
    if len(partes) != 2:
        raise argparse.ArgumentTypeError('se esperaba AxB, por ejemplo 80x4: %s' % s)
    return num(partes[0]), num(partes[1])


def carga_en(s):
    """'10@2,5' → (10.0, 2.5)."""
    if '@' not in s:
        raise argparse.ArgumentTypeError('se esperaba valor@posición, por ejemplo 10@2: %s' % s)
    v, x = s.split('@', 1)
    return num(v), num(x)


def carga_q(s):
    """'6' (todo el largo) o '6@0:3' → (6.0, x1, x2), con x1 y x2 None si es todo el largo."""
    if '@' not in s:
        return num(s), None, None
    v, tramo = s.split('@', 1)
    if ':' not in tramo:
        raise argparse.ArgumentTypeError('el tramo de la carga uniforme va como x1:x2, por ejemplo 6@0:3: %s' % s)
    a, b = tramo.split(':', 1)
    return num(v), num(a), num(b)


def tramo(s):
    if ':' not in s:
        raise argparse.ArgumentTypeError('se esperaba x1:x2, por ejemplo 0:4: %s' % s)
    a, b = s.split(':', 1)
    return num(a), num(b)


# ------------------------------------------------------------------------------------------ secciones (mm)
def _sec(nombre, A, Iy, Iz, Wy, Wz, **extra):
    s = {'nombre': nombre, 'A': A, 'Iy': Iy, 'Iz': Iz, 'Wy': Wy, 'Wz': Wz,
         'iy': math.sqrt(Iy / A), 'iz': math.sqrt(Iz / A)}
    s['imin'] = min(s['iy'], s['iz'])
    s.update(extra)
    return s


def sec_rect(b, h):
    if b <= 0 or h <= 0:
        raise ValueError('las medidas tienen que ser positivas')
    return _sec('rectángulo %s × %s mm' % (med(b), med(h)), b * h, b * h ** 3 / 12, h * b ** 3 / 12, b * h ** 2 / 6,
                h * b ** 2 / 6, forma='rect', h=h, b=b)


def sec_tubo(D, di):
    if not 0 <= di < D:
        raise ValueError('el diámetro interior tiene que ser menor que el exterior')
    A = math.pi / 4 * (D ** 2 - di ** 2)
    I = math.pi / 64 * (D ** 4 - di ** 4)
    nombre = ('círculo de %s mm' % med(D)) if di == 0 else ('tubo %s × %s mm (D × e)' % (med(D), med((D - di) / 2)))
    return _sec(nombre, A, I, I, 2 * I / D, 2 * I / D, forma='circ' if di == 0 else 'tubo', h=D, D=D, di=di,
                J=2 * I, Wp=4 * I / D)


def sec_doble_t(b, h, tw, tf):
    if not (0 < tw < b and 0 < 2 * tf < h):
        raise ValueError('medidas del doble T incoherentes (tw < b y 2·tf < h)')
    hw = h - 2 * tf
    A = 2 * b * tf + hw * tw
    Iy = (b * h ** 3 - (b - tw) * hw ** 3) / 12
    Iz = (2 * tf * b ** 3 + hw * tw ** 3) / 12
    Q = b * tf * (h - tf) / 2 + tw * (h / 2 - tf) ** 2 / 2
    return _sec('doble T de chapas %s × %s mm (alma %s, alas %s; sin radios)' % (med(h), med(b), med(tw), med(tf)), A, Iy, Iz,
                2 * Iy / h, 2 * Iz / b, forma='doble-t', h=h, b=b, tw=tw, tf=tf, Q=Q)


# esquina de chapa con acuerdo ("enjuta"): cuadrado r × r menos el cuarto de círculo; constantes por r², r y r⁴
_AS = 1 - math.pi / 4
_YS = (1 / 2 - math.pi / 4 + 1 / 3) / _AS
_IS = (1 / 3 - (5 * math.pi / 16 - 2 / 3)) - _AS * _YS ** 2
_IXYS = (1 / 4 - (math.pi / 4 - 2 / 3 + 1 / 8)) - _AS * _YS ** 2


def sec_angulo(a, t, r1=None, r2=None):
    """Ángulo de alas iguales a × a × t con radio de raíz r1 y de borde r2 (por defecto, los de la tabla)."""
    if r1 is None:
        r1 = ANGULOS.get((int(a), int(t)), 0.0) if a == int(a) and t == int(t) else 0.0
    if r2 is None:
        r2 = r1 / 2
    if not 0 < t < a:
        raise ValueError('el espesor tiene que ser menor que el ala')
    p = [(1, a * t, a / 2, t / 2, a * t ** 3 / 12, t * a ** 3 / 12, 0.0),
         (1, t * (a - t), t / 2, t + (a - t) / 2, t * (a - t) ** 3 / 12, (a - t) * t ** 3 / 12, 0.0),
         (1, _AS * r1 ** 2, t + _YS * r1, t + _YS * r1, _IS * r1 ** 4, _IS * r1 ** 4, _IXYS * r1 ** 4),
         (-1, _AS * r2 ** 2, a - _YS * r2, t - _YS * r2, _IS * r2 ** 4, _IS * r2 ** 4, _IXYS * r2 ** 4),
         (-1, _AS * r2 ** 2, t - _YS * r2, a - _YS * r2, _IS * r2 ** 4, _IS * r2 ** 4, _IXYS * r2 ** 4)]
    A = sum(s * Ai for s, Ai, *_ in p)
    xc = sum(s * Ai * xi for s, Ai, xi, *_ in p) / A
    yc = sum(s * Ai * yi for s, Ai, xi, yi, *_ in p) / A
    Ix = sum(s * (Ii + Ai * (yi - yc) ** 2) for s, Ai, xi, yi, Ii, _, _ in p)
    Iy = sum(s * (Ij + Ai * (xi - xc) ** 2) for s, Ai, xi, yi, _, Ij, _ in p)
    Ixy = sum(s * (Ik + Ai * (xi - xc) * (yi - yc)) for s, Ai, xi, yi, _, _, Ik in p)
    R = math.hypot((Ix - Iy) / 2, Ixy)
    Iu, Iv = (Ix + Iy) / 2 + R, (Ix + Iy) / 2 - R
    s = _sec('ángulo L %s × %s × %s mm (r1 = %s, r2 = %s)' % (med(a), med(a), med(t), med(r1), med(r2)), A, Ix, Iy,
             Ix / (a - yc), Iy / (a - xc), forma='angulo', h=a, e=yc, Iu=Iu, Iv=Iv, iv=math.sqrt(Iv / A),
             G=A * 0.00785)
    s['imin'] = s['iv']
    return s


def sec_perfil(nombre):
    k = nombre.upper().replace(' ', '').replace('-', '').replace('×', 'X')
    for serie, tabla, fuente in (('IPN', IPN, 'catálogo ArcelorMittal'), ('UPN', UPN, 'datos técnicos STAD')):
        if k.startswith(serie):
            try:
                t = tabla[int(k[3:])]
            except (ValueError, KeyError):
                raise ValueError('no está el %s; hay %s %s' % (nombre, serie, ', '.join(str(x) for x in tabla)))
            h, b, tw, tf, A, G, Iy, Wy, Iz, Wz = t
            return _sec('%s %s (%s)' % (serie, k[3:], fuente), A * 100, Iy * 1e4, Iz * 1e4, Wy * 1e3, Wz * 1e3,
                        forma=serie, h=h, b=b, tw=tw, tf=tf, G=G, catalogo=True)
    if k.startswith('L'):
        medidas = [x for x in k[1:].split('X') if x]
        try:
            a, t = (int(medidas[0]), int(medidas[-1])) if len(medidas) in (2, 3) else (None, None)
        except ValueError:
            a, t = None, None
        if (a, t) not in ANGULOS:
            raise ValueError('ángulos cargados: %s (o usar «seccion angulo» con las medidas)'
                             % ', '.join('L%dx%d' % x for x in ANGULOS))
        return sec_angulo(a, t)
    raise ValueError('perfil desconocido: %s (series IPN, UPN y L)' % nombre)


def seccion_de(args, eje=None):
    """Arma la sección a partir de las opciones comunes (--perfil, --tubo, --circ, --rect)."""
    if getattr(args, 'perfil', None):
        s = sec_perfil(args.perfil)
    elif getattr(args, 'tubo', None):
        D, e = args.tubo
        s = sec_tubo(D, D - 2 * e)
    elif getattr(args, 'circ', None):
        s = sec_tubo(args.circ, 0.0)
    elif getattr(args, 'rect', None):
        s = sec_rect(*args.rect)
    else:
        return None
    if eje == 'z':
        s = dict(s, Iy=s['Iz'], Wy=s['Wz'], iy=s['iz'], nombre=s['nombre'] + ', eje débil z')
    return s


# ------------------------------------------------------------------------------------------ axial
def axial(F, L, A, E=E_ACERO, dT=None, alfa=ALFA_ACERO, impedida=False, holgura=0.0, fy=None):
    if A <= 0 or L <= 0:
        raise ValueError('A y L tienen que ser positivos')
    r, Ls = {}, []
    if impedida and F:
        raise ValueError('con --impedida la fuerza la pone la restricción (hiperestático): calcular la carga mecánica aparte')
    sig = F * 1000 / A
    eps = sig / E
    dl = F * 1000 * L * 1000 / (E * A)
    r.update(sigma=sig, eps=eps, delta=dl)
    if F:
        Ls.append('Tensión normal: σ = F/A = %s N/%s mm² = %s MPa (%s)' % (miles(F * 1000), g(A, 4), n(sig, 1),
                                                                          'tracción' if F > 0 else 'compresión'))
        Ls.append('Ley de Hooke: ε = σ/E = %s/%s = %s; alargamiento δ = F·L/(E·A) = %s mm en %s m'
                  % (n(sig, 1), miles(E), g(eps, 4), n(dl, 3), n(L, 2)))
    sig_t = 0.0
    if dT:
        libre = alfa * dT * L * 1000
        r['libre'] = libre
        Ls.append('Dilatación térmica libre: δT = α·ΔT·L = %s·%s·%s mm = %s mm (ε = α·ΔT = %s)'
                  % (g(alfa * 1e6, 3) + '·10⁻⁶', par_neg(dT, 0), miles(L * 1000), n(libre, 3), g(alfa * dT, 4)))
        if impedida:
            impedido = libre
            if dT > 0 and holgura:
                impedido = max(0.0, libre - holgura)
                Ls.append('Con %s mm de holgura, la parte impedida es %s mm' % (n(holgura, 2), n(impedido, 3)))
            sig_t = -E * impedido / (L * 1000)
            Ft = sig_t * A / 1000
            r.update(sigma_t=sig_t, F_t=Ft, eps_t=alfa * dT)
            Ls.append('Dilatación impedida (apoyos rígidos): σT = %s = %s MPa (%s); fuerza F = σT·A = %s kN'
                      % ('−E·(δT − holgura)/L' if impedido != libre else '−E·α·ΔT', n(sig_t, 1),
                         'compresión' if sig_t < 0 else 'tracción', n(Ft, 1)))
            if sig_t < 0:
                Ls.append('AVISO: en compresión, verificar además el pandeo de la barra (comando pandeo).')
    s_tot = sig + sig_t
    if fy:
        r['n'] = fy / abs(s_tot) if s_tot else float('inf')
        Ls.append('Coeficiente de seguridad a la fluencia: n = fy/|σ| = %s/%s = %s' % (n(fy, 0), n(abs(s_tot), 1), n(r['n'], 2)))
        if abs(s_tot) > fy:
            Ls.append('AVISO: la tensión supera la fluencia: el resultado elástico deja de valer.')
    if sig < 0 and not impedida:
        Ls.append('AVISO: barra comprimida: verificar el pandeo (comando pandeo).')
    return r, Ls


# ------------------------------------------------------------------------------------------ corte directo
def corte(d, F=None, T=None, dp=None, planos=1, pernos=1, t=None, fy=None):
    if planos not in (1, 2) or pernos < 1 or d <= 0:
        raise ValueError('planos: 1 (simple) o 2 (doble); pernos ≥ 1; d > 0')
    Ls = []
    if F is None:
        if T is None or not dp:
            raise ValueError('indicá --F, o --T con --dp (diámetro de la circunferencia de los pernos)')
        Fp = T / (dp / 2000) / pernos / 1000     # kN por perno
        Ls.append('Acoplamiento: fuerza por perno F = T/(R·n) = %s N·m/(%s m·%d) = %s kN'
                  % (miles(T), n(dp / 2000, 3), pernos, n(Fp, 2)))
    else:
        Fp = F / pernos
        if pernos > 1:
            Ls.append('Fuerza por perno: F/n = %s/%d = %s kN (reparto parejo)' % (n(F, 2), pernos, n(Fp, 2)))
    A = math.pi * d ** 2 / 4
    tau = Fp * 1000 / (planos * A)
    r = {'F': Fp, 'A': A, 'tau': tau}
    Ls.append('Corte %s: A = π·d²/4 = %s mm²; τ = %s = %s N/(%s mm²) = %s MPa'
              % ('simple (1 plano)' if planos == 1 else 'doble (2 planos)', n(A, 1), 'F/A' if planos == 1 else 'F/(2·A)',
                 miles(Fp * 1000), n(planos * A, 1), n(tau, 2)))
    if t:
        sap = Fp * 1000 / (d * t)
        r['sap'] = sap
        Ls.append('Aplastamiento: σap = F/(d·t) = %s N/(%s·%s mm²) = %s MPa (t = la chapa que apoya menos)'
                  % (miles(Fp * 1000), med(d), med(t), n(sap, 1)))
    if fy:
        r['n'] = 0.577 * fy / tau
        Ls.append('Fluencia en corte (von Mises): τy = 0,577·fy = %s MPa → n = %s' % (n(0.577 * fy, 1), n(r['n'], 2)))
    Ls.append('El aplastamiento admisible y la resistencia de los bulones los fija la norma del caso o la consigna.')
    return r, Ls


# ------------------------------------------------------------------------------------------ torsión
def torsion(d, T=None, P=None, rpm=None, di=0.0, L=1.0, G=G_ACERO, tadm=None, giro_adm=None, fy=None):
    Ls = []
    if T is None:
        if not P or not rpm:
            raise ValueError('indicá --T, o --P (kW) con --rpm')
        w = 2 * math.pi * rpm / 60
        T = P * 1000 / w
        Ls.append('Torque: T = P/ω = %s W/(2π·%s/60 rad/s) = %s N·m (T [N·m] = 9549·P [kW]/n [rpm])'
                  % (miles(P * 1000), med(rpm), miles(T, 1)))
    if not 0 <= di < d:
        raise ValueError('el diámetro interior tiene que ser menor que el exterior')
    J = math.pi * (d ** 4 - di ** 4) / 32
    tau = T * 1000 * (d / 2) / J
    th = T * 1000 * L * 1000 / (G * J)
    r = {'T': T, 'J': J, 'tau': tau, 'theta': th}
    if di:
        Ls.append('Eje hueco %s/%s mm: J = π·(D⁴ − d⁴)/32 = %s mm⁴' % (g(d), g(di), miles(J)))
    else:
        Ls.append('Eje macizo de %s mm: J = π·d⁴/32 = %s mm⁴' % (g(d), miles(J)))
    Ls.append('Tensión máxima (en la superficie): τ = T·r/J = %s N·mm·%s mm/%s mm⁴ = %s MPa'
              % (miles(T * 1000), g(d / 2), miles(J), n(tau, 2)))
    if di:
        r['tau_i'] = tau * di / d
        Ls.append('En el borde interior: τi = τ·di/D = %s MPa' % n(r['tau_i'], 2))
    Ls.append('Ángulo de giro: θ = T·L/(G·J) = %s rad = %s° en %s m (%s °/m), G = %s MPa'
              % (g(th, 4), n(math.degrees(th), 3), n(L, 2), n(math.degrees(th) / L, 3), miles(G)))
    k = di / d
    if tadm:
        r['d_res'] = (16 * T * 1000 / (math.pi * tadm * (1 - k ** 4))) ** (1 / 3)
        Ls.append('Diámetro mínimo por resistencia: d = (16·T/(π·τadm·(1 − k⁴)))^(1/3) = %s mm (τadm = %s MPa, k = di/D = %s)'
                  % (n(r['d_res'], 1), n(tadm, 1), n(k, 3)))
    if giro_adm:
        th_mm = math.radians(giro_adm) / 1000
        r['d_rig'] = (32 * T * 1000 / (math.pi * G * th_mm * (1 - k ** 4))) ** 0.25
        Ls.append('Diámetro mínimo por rigidez (%s °/m): d = (32·T/(π·G·θ\'·(1 − k⁴)))^(1/4) = %s mm'
                  % (n(giro_adm, 2), n(r['d_rig'], 1)))
    if fy:
        r['n_vm'] = 0.577 * fy / tau
        r['n_tr'] = 0.5 * fy / tau
        Ls.append('Fluencia: n = 0,577·fy/τ = %s (von Mises); 0,5·fy/τ = %s (Tresca)' % (n(r['n_vm'], 2), n(r['n_tr'], 2)))
    Ls.append('Si además hay flexión, combinar con el comando mohr; a fatiga, la skill elementos-de-maquinas.')
    return r, Ls


# ------------------------------------------------------------------------------------------ vigas
class Viga:
    """Viga simplemente apoyada (con voladizos si los apoyos no están en los extremos) o en voladizo.

    Cargas P y q hacia abajo positivas (kN, kN/m); pares M antihorarios positivos (kN·m). x en m desde el
    extremo izquierdo; en el voladizo el empotramiento está en x = 0. M positivo: tracción abajo.
    """

    def __init__(self, tipo, L, P=(), q=(), M=(), apoyos=None):
        if L <= 0:
            raise ValueError('el largo L tiene que ser positivo')
        self.tipo, self.L = tipo, float(L)
        self.P = [(float(v), float(x)) for v, x in P]
        self.q = [(float(w), float(0 if a is None else a), float(L if b is None else b)) for w, a, b in q]
        self.M = [(float(v), float(x)) for v, x in M]
        for _, x in self.P + self.M:
            if not 0 <= x <= L:
                raise ValueError('hay una carga fuera de la viga (x = %s m)' % n(x))
        for _, a, b in self.q:
            if not 0 <= a < b <= L:
                raise ValueError('tramo de carga uniforme inválido (%s a %s m)' % (n(a), n(b)))
        total = sum(v for v, _ in self.P) + sum(w * (b - a) for w, a, b in self.q)
        mom0 = sum(v * x for v, x in self.P) + sum(w * (b - a) * (a + b) / 2 for w, a, b in self.q)
        sumM = sum(v for v, _ in self.M)
        self.total = total
        if tipo == 'apoyada':
            xa, xb = apoyos if apoyos else (0.0, self.L)
            if not 0 <= xa < xb <= self.L:
                raise ValueError('apoyos fuera de la viga o en orden inverso')
            Rb = (mom0 - total * xa - sumM) / (xb - xa)
            Ra = total - Rb
            self.xa, self.xb = float(xa), float(xb)
            self.fuerzas = [(self.xa, Ra), (self.xb, Rb)]
            self.pares = []
            self.reacciones = {'RA': Ra, 'RB': Rb}
        elif tipo == 'voladizo':
            Memp = mom0 - sumM       # par de empotramiento, antihorario positivo
            self.fuerzas = [(0.0, total)]
            self.pares = [(0.0, Memp)]
            self.reacciones = {'R': total, 'Memp': Memp}
        else:
            raise ValueError('tipo: apoyada o voladizo')
        self.fuerzas += [(x, -v) for v, x in self.P]
        self.pares += [(x, v) for v, x in self.M]

    def V(self, x, der=True):
        s = 0.0
        for xf, f in self.fuerzas:
            if xf < x or (der and xf == x):
                s += f
        for w, a, b in self.q:
            if x > a:
                s -= w * (min(x, b) - a)
        return s

    def Mf(self, x, der=True):
        s = 0.0
        for xf, f in self.fuerzas:
            if xf < x:
                s += f * (x - xf)
        for xc, c in self.pares:
            if xc < x or (der and xc == x):
                s -= c
        for w, a, b in self.q:
            if x > a:
                l = min(x, b) - a
                s -= w * l * (x - a - l / 2)
        return s

    def resolver(self, EI, tramos=400):
        """Integra EI·y'' = M dos veces con Simpson en cada tramo (exacto con cargas puntuales y uniformes)."""
        L = self.L
        esp = {0.0, L}
        esp.update(x for x, _ in self.fuerzas)
        esp.update(x for x, _ in self.pares)
        for _, a, b in self.q:
            esp.update((a, b))
        malla = sorted(esp.union(L * i / tramos for i in range(tramos + 1)))
        xs = [malla[0]]
        for x in malla[1:]:
            if x - xs[-1] > 1e-9 * L:
                xs.append(x)
            elif x in esp:
                xs[-1] = x
        th, y = [0.0], [0.0]
        for a, b in zip(xs, xs[1:]):
            h = b - a
            m0, m1, m2, m4 = self.Mf(a, True), self.Mf(a + h / 4), self.Mf(a + h / 2), self.Mf(b, False)
            tb = th[-1] + h / 6 * (m0 + 4 * m2 + m4) / EI
            tm = th[-1] + h / 12 * (m0 + 4 * m1 + m2) / EI
            y.append(y[-1] + h / 6 * (th[-1] + 4 * tm + tb))
            th.append(tb)
        if self.tipo == 'apoyada':
            ia, ib = xs.index(self.xa), xs.index(self.xb)
            C1 = -(y[ib] - y[ia]) / (self.xb - self.xa)
            C2 = -y[ia] - C1 * self.xa
            th = [t + C1 for t in th]
            y = [yy + C1 * x + C2 for yy, x in zip(y, xs)]
        self.xs, self.th, self.y, self.EI = xs, th, y, EI
        return xs, th, y

    def _en(self, i, x):
        """Giro y flecha exactos en x dentro del tramo i (requiere resolver)."""
        a = self.xs[i]
        h = x - a
        if h <= 0:
            return self.th[i], self.y[i]
        m0, mx = self.Mf(a, True), self.Mf(x, False)
        tx = self.th[i] + h / 6 * (m0 + 4 * self.Mf(a + h / 2) + mx) / self.EI
        tm = self.th[i] + h / 12 * (m0 + 4 * self.Mf(a + h / 4) + self.Mf(a + h / 2)) / self.EI
        return tx, self.y[i] + h / 6 * (self.th[i] + 4 * tm + tx)

    def flecha(self, x):
        """y(x) en m (positiva hacia arriba) en cualquier punto."""
        for i in range(len(self.xs) - 1):
            if self.xs[i] <= x <= self.xs[i + 1]:
                return self._en(i, x)[1]
        raise ValueError('x fuera de la viga')

    def flecha_maxima(self):
        cand = [(abs(yy), x, yy) for x, yy in zip(self.xs, self.y)]
        for i in range(len(self.xs) - 1):
            t0, t1 = self.th[i], self.th[i + 1]
            if t0 * t1 < 0:
                lo, hi = self.xs[i], self.xs[i + 1]
                for _ in range(80):
                    m = (lo + hi) / 2
                    if self._en(i, m)[0] * t0 > 0:
                        lo = m
                    else:
                        hi = m
                yy = self._en(i, (lo + hi) / 2)[1]
                cand.append((abs(yy), (lo + hi) / 2, yy))
        _, x, yy = max(cand)
        return x, yy

    def extremos(self):
        """Corte máximo y momentos extremos con sus posiciones (V es lineal entre nodos)."""
        vm, mm = [], []
        for x in self.xs:
            for der in (False, True):
                vm.append((abs(self.V(x, der)), x, self.V(x, der)))
                mm.append((self.Mf(x, der), x))
        for a, b in zip(self.xs, self.xs[1:]):
            va, vb = self.V(a, True), self.V(b, False)
            if va * vb < 0:
                x0 = a + va / (va - vb) * (b - a)
                mm.append((self.Mf(x0), x0))
        Mmax = max(mm)
        Mmin = min(mm)
        return max(vm), Mmax, Mmin


def analizar_viga(a, sec=None, E=E_ACERO, silencioso=False):
    """Arma y resuelve la viga a partir de las opciones; devuelve (resultados, líneas)."""
    P = list(a.P or [])
    q = list(a.q or [])
    if a.peso_propio:
        if not sec or not sec.get('G'):
            raise ValueError('--peso-propio necesita --perfil (de ahí sale el peso por metro)')
        q.append((sec['G'] * 9.80665 / 1000, None, None))
    viga = Viga(a.tipo, a.L, P, q, a.M or [], a.apoyos)
    if sec is not None:
        I_cm4, W_cm3 = sec['Iy'] / 1e4, sec['Wy'] / 1e3
    else:
        if not a.I:
            raise ValueError('falta la sección: --I (cm⁴), --perfil, --rect, --circ o --tubo')
        I_cm4, W_cm3 = a.I, a.W
    EI = E * I_cm4 * 1e-5        # kN·m²
    viga.resolver(EI, a.tramos)
    (vabs, xv, vval), (Mmax, xM), (Mmin, xm) = viga.extremos()
    Mabs, xMabs = (Mmax, xM) if abs(Mmax) >= abs(Mmin) else (Mmin, xm)
    xf, yf = viga.flecha_maxima()
    r = {'viga': viga, 'V': vabs, 'xV': xv, 'Mmax': Mmax, 'xMmax': xM, 'Mmin': Mmin, 'xMmin': xm, 'M': Mabs,
         'xM': xMabs, 'f': -yf * 1000, 'xf': xf, 'EI': EI}
    r.update(viga.reacciones)
    Ls = []
    cargas = ['P = %s kN en x = %s m' % (n(v), n(x)) for v, x in viga.P]
    cargas += ['q = %s kN/m de %s a %s m' % (n(w, 3), n(x1), n(x2)) for w, x1, x2 in viga.q]
    cargas += ['par M = %s kN·m en x = %s m' % (n(v), n(x)) for v, x in viga.M]
    if a.tipo == 'apoyada':
        Ls.append('Viga simplemente apoyada, L = %s m, apoyos en x = %s y %s m' % (n(a.L), n(viga.xa), n(viga.xb)))
    else:
        Ls.append('Viga en voladizo, L = %s m, empotrada en x = 0' % n(a.L))
    if sec is not None:
        Ls.append('Sección: %s: I = %s cm⁴, W = %s cm³' % (sec['nombre'], g(I_cm4, 4), g(W_cm3, 4)))
    Ls.append('E·I = %s MPa·%s cm⁴ = %s kN·m²' % (miles(E), g(I_cm4, 4), g(EI, 4)))
    Ls.append('Cargas: ' + '; '.join(cargas) + (' (incluye el peso propio del perfil)' if a.peso_propio else ''))
    if a.tipo == 'apoyada':
        Ls.append('Reacciones (ΣFy = 0 y ΣM = 0): RA = %s kN, RB = %s kN (suma %s kN = cargas %s kN)'
                  % (n(r['RA']), n(r['RB']), n(r['RA'] + r['RB']), n(viga.total)))
    else:
        Ls.append('Reacciones en el empotramiento: R = %s kN, M = %s kN·m' % (n(r['R']), n(r['Memp'])))
    Ls.append('Corte máximo: |V| = %s kN en x = %s m' % (n(vabs), n(xv)))
    escala = max(abs(Mmax), abs(Mmin), 1e-12)
    partes = []
    if Mmax > 1e-9 * escala:
        partes.append('máximo positivo %s kN·m en x = %s m' % (n(Mmax), n(xM, 3)))
    if Mmin < -1e-9 * escala:
        partes.append('negativo %s kN·m en x = %s m, sobre el apoyo o el empotramiento' % (n(Mmin), n(xm, 3)))
    Ls.append('Momento flector (positivo: tracción abajo): %s' % '; '.join(partes or ['nulo']))
    if W_cm3:
        r['sigma'] = abs(Mabs) * 1000 / W_cm3
        Ls.append('Tensión de flexión: σ = M/W = %s kN·m/%s cm³ = %s MPa' % (n(abs(Mabs)), g(W_cm3, 4), n(r['sigma'], 1)))
        if a.sadm:
            ok = r['sigma'] <= a.sadm * (1 + 1e-9)
            Ls.append('%s: σ = %s MPa %s σadm = %s MPa' % ('Verifica' if ok else 'NO VERIFICA', n(r['sigma'], 1),
                                                        '≤' if ok else '>', n(a.sadm, 1)))
        if a.fy:
            r['n'] = a.fy / r['sigma']
            Ls.append('Coeficiente de seguridad a la fluencia: n = fy/σ = %s/%s = %s' % (n(a.fy, 0), n(r['sigma'], 1), n(r['n'], 2)))
    if sec is not None:
        A = sec['A']
        if sec['forma'] in ('IPN', 'UPN', 'doble-t'):
            r['tau'] = vabs * 1000 / (sec['h'] * sec['tw'])
            Ls.append('Corte en el alma: τ ≈ V/(h·tw) = %s N/(%s·%s mm²) = %s MPa' % (miles(vabs * 1000), g(sec['h']),
                                                                                    g(sec['tw']), n(r['tau'], 1)))
        elif sec['forma'] == 'rect':
            r['tau'] = 1.5 * vabs * 1000 / A
            Ls.append('Corte máximo en la fibra neutra: τ = 1,5·V/A = %s MPa' % n(r['tau'], 2))
        elif sec['forma'] in ('circ', 'tubo'):
            R2, r2 = (sec['D'] / 2) ** 2, (sec['di'] / 2) ** 2
            f = (R2 + math.sqrt(R2 * r2) + r2) / (R2 + r2)
            r['tau'] = 4 / 3 * vabs * 1000 / A * f
            Ls.append('Corte máximo en la fibra neutra: τ = (4/3)·(V/A)·(R² + R·r + r²)/(R² + r²) = %s MPa' % n(r['tau'], 2))
    luz = (viga.xb - viga.xa) if a.tipo == 'apoyada' else 2 * a.L
    Ls.append('Flecha máxima (integración numérica de M/(E·I), Simpson en %d tramos): %s mm en x = %s m → L/%s'
              % (len(viga.xs) - 1, n(r['f'], 2), n(xf, 3), miles(luz * 1000 / abs(r['f'])) if r['f'] else '∞'))
    if a.limite:
        fadm = luz * 1000 / a.limite
        r['fadm'] = fadm
        ok = abs(r['f']) <= fadm * (1 + 1e-9)
        Ls.append('%s: f = %s mm %s L/%s = %s mm%s' % ('Verifica' if ok else 'NO VERIFICA', n(abs(r['f']), 2),
                                                       '≤' if ok else '>', miles(a.limite), n(fadm, 2),
                                                       ' (en ménsulas, L = 2 veces el voladizo: CIRSOC 301, Tabla A-L.4.1)'
                                                       if a.tipo == 'voladizo' else ''))
        if a.tipo == 'apoyada' and (viga.xa > 0 or viga.xb < a.L):
            Ls.append('AVISO: con voladizos, verificar su flecha con L = 2 veces el voladizo (CIRSOC 301, Tabla A-L.4.1).')
    if a.tipo == 'apoyada':
        ia, ib = viga.xs.index(viga.xa), viga.xs.index(viga.xb)
        Ls.append('Giros en los apoyos: θA = %s rad, θB = %s rad' % (g(viga.th[ia], 3), g(viga.th[ib], 3)))
    else:
        Ls.append('Giro en el extremo libre: θ = %s rad' % g(viga.th[-1], 3))
    return r, Ls


def csv_viga(viga, ruta, decimal='coma'):
    sep, f = (';', lambda v: ('%.6g' % (v + 0.0)).replace('.', ',')) if decimal == 'coma' else (',', lambda v: '%.6g' % (v + 0.0))
    filas = ['x [m]', 'V [kN]', 'M [kN·m]', 'giro [rad]', 'flecha [mm]']
    with open(ruta, 'w', encoding='utf-8', newline='') as fh:
        fh.write(sep.join(filas) + '\n')
        for x, t, yy in zip(viga.xs, viga.th, viga.y):
            vi, vd = viga.V(x, False), viga.V(x, True)
            mi, md = viga.Mf(x, False), viga.Mf(x, True)
            fh.write(sep.join(f(v) for v in (x, vi, mi, t, -yy * 1000)) + '\n')
            if abs(vi - vd) > 1e-12 or abs(mi - md) > 1e-12:
                fh.write(sep.join(f(v) for v in (x, vd, md, t, -yy * 1000)) + '\n')


def elegir_perfil(a, E):
    tabla = {'IPN': IPN, 'UPN': UPN}.get(a.elegir.upper())
    if not tabla:
        raise ValueError('--elegir: IPN o UPN')
    if not a.sadm and not a.limite:
        raise ValueError('--elegir necesita --sadm (o --fy y --n) y/o --limite')
    Ls = []
    for k in sorted(tabla, key=lambda z: tabla[z][5]):
        sec = sec_perfil('%s%d' % (a.elegir.upper(), k))
        r, L = analizar_viga(a, sec, E, silencioso=True)
        motivos = []
        if a.sadm and r['sigma'] > a.sadm * (1 + 1e-9):
            motivos.append('σ = %s MPa > %s' % (n(r['sigma'], 1), n(a.sadm, 1)))
        if a.limite and abs(r['f']) > r['fadm'] * (1 + 1e-9):
            motivos.append('f = %s mm > %s' % (n(abs(r['f']), 1), n(r['fadm'], 1)))
        if motivos:
            Ls.append('  %s %d: no (%s)' % (a.elegir.upper(), k, '; '.join(motivos)))
            continue
        Ls.append('Se adopta el %s %d, el más liviano de la serie que cumple (%s kg/m):' % (a.elegir.upper(), k, n(sec['G'], 1)))
        return r, Ls + L
    raise ValueError('ningún perfil de la serie cumple: usar otra serie, acortar la luz o agregar apoyos')


# ------------------------------------------------------------------------------------------ pandeo
def pandeo(L, sec, K, fy=FY_F24, E=E_ACERO, P=None, Pu=None, tetmajer=None, vinculo=None):
    A, i = sec['A'], sec['imin'] if sec.get('usar_min', True) else sec['iy']
    I = A * i ** 2
    Lk = K * L * 1000
    lam = Lk / i
    Pe = math.pi ** 2 * E * I / Lk ** 2 / 1000
    se = math.pi ** 2 * E / lam ** 2
    lam1 = math.sqrt(2 * math.pi ** 2 * E / fy)
    Ls = ['Columna de %s m, %s → K = %s; longitud de pandeo Lk = K·L = %s m'
          % (n(L), vinculo or 'K dado', n(K, 3), n(Lk / 1000, 3)),
          'Sección: %s: A = %s cm², i mín = %s cm (I = A·i² = %s cm⁴)' % (sec['nombre'], g(A / 100, 4), n(i / 10, 3), g(I / 1e4, 4)),
          'Esbeltez: λ = Lk/i = %s/%s = %s' % (miles(Lk), n(i, 2), n(lam, 1))]
    r = {'lam': lam, 'Pe': Pe, 'sigma_e': se, 'lam1': lam1, 'A': A, 'i': i}
    if lam > 200:
        Ls.append('AVISO: λ > 200, el máximo para barras comprimidas del CIRSOC 301 (B.7).')
    Ls.append('Euler: Pcr = π²·E·I/Lk² = %s kN (σcr = π²·E/λ² = %s MPa)' % (n(Pe, 1), n(se, 1)))
    if lam >= lam1:
        scr = se
        Ls.append('Límite de Euler (Johnson): λ1 = √(2·π²·E/fy) = %s ≤ λ: columna esbelta, vale Euler' % n(lam1, 1))
    else:
        scr = fy - (fy * lam / (2 * math.pi)) ** 2 / E
        Ls.append('Límite de Euler (Johnson): λ1 = √(2·π²·E/fy) = %s > λ: columna intermedia, Euler sobreestima' % n(lam1, 1))
        Ls.append('Johnson: σcr = fy − (fy·λ/(2π))²/E = %s − (%s·%s/(2π))²/%s = %s MPa' % (n(fy, 0), n(fy, 0), n(lam, 1), miles(E), n(scr, 1)))
    Pcr = scr * A / 1000
    r.update(sigma_cr=scr, Pcr=Pcr)
    Ls.append('Carga crítica: Pcr = σcr·A = %s kN' % n(Pcr, 1))
    if P:
        r['n'] = Pcr / P
        Ls.append('Con P = %s kN de servicio: n = Pcr/P = %s' % (n(P, 1), n(r['n'], 2)))
    lc = lam / math.pi * math.sqrt(fy / E)
    fcr = 0.658 ** (lc ** 2) * fy if lc <= 1.5 else 0.877 / lc ** 2 * fy
    phiPn = PHI_C * fcr * A / 1000
    r.update(lc=lc, Fcr=fcr, phiPn=phiPn)
    Ls.append('CIRSOC 301 (E.2): λc = (λ/π)·√(fy/E) = %s → Fcr = %s = %s MPa; φc·Pn = 0,85·Fcr·Ag = %s kN'
              % (n(lc, 3), '0,658^(λc²)·fy' if lc <= 1.5 else '(0,877/λc²)·fy', n(fcr, 1), n(phiPn, 1)))
    if Pu:
        ok = Pu <= phiPn
        Ls.append('%s: Pu = %s kN %s φc·Pn = %s kN (Pu: carga mayorada con las combinaciones del reglamento)'
                  % ('Verifica' if ok else 'NO VERIFICA', n(Pu, 1), '≤' if ok else '>', n(phiPn, 1)))
    if tetmajer:
        ta, tb, l0 = tetmajer
        if lam < l0:
            st = min(fy, ta - tb * lam)
            Ls.append('Tetmajer: σ = min(fy; a − b·λ) = min(%s; %s − %s·%s) = %s MPa → %s kN (coeficientes de tabla: verificar)'
                      % (n(fy, 0), g(ta), g(tb), n(lam, 1), n(st, 1), n(st * A / 1000, 1)))
        else:
            st = se
            Ls.append('Tetmajer: λ ≥ λ0 = %s: vale Euler' % g(l0))
        r['sigma_t'] = st
    if sec.get('forma') == 'angulo':
        Ls.append('Ángulo solo: pandea alrededor del eje v (i mín); con uniones excéntricas, ver el reglamento.')
    return r, Ls


# ------------------------------------------------------------------------------------------ Mohr
def mohr(sx, sy, txy, theta=None, fy=None):
    C = (sx + sy) / 2
    R = math.hypot((sx - sy) / 2, txy)
    s1, s2 = C + R, C - R
    t1 = 0.5 * math.degrees(math.atan2(2 * txy, sx - sy))
    principales = sorted([s1, s2, 0.0], reverse=True)
    tabs = (principales[0] - principales[2]) / 2
    vm = math.sqrt(sx ** 2 - sx * sy + sy ** 2 + 3 * txy ** 2)
    tr = principales[0] - principales[2]
    r = {'C': C, 'R': R, 's1': s1, 's2': s2, 'theta1': t1, 'tmax': R, 'tabs': tabs, 'vm': vm, 'tresca': tr}
    Ls = ['Estado plano: σx = %s, σy = %s, τxy = %s MPa (τxy positiva: en la cara +x apunta a +y)' % (n(sx, 1), n(sy, 1), n(txy, 1)),
          'Círculo de Mohr: centro C = (σx + σy)/2 = %s MPa; radio R = √(((σx − σy)/2)² + τxy²) = %s MPa' % (n(C, 2), n(R, 2)),
          'Principales: σ1 = C + R = %s MPa; σ2 = C − R = %s MPa (σ3 = 0 fuera del plano)' % (n(s1, 2), n(s2, 2)),
          'Dirección de σ1: θ1 = ½·atan2(2·τxy, σx − σy) = %s° desde x (positivo antihorario)' % n(t1, 2),
          'Corte máximo en el plano: τ = R = %s MPa, a 45° de las principales; absoluto (con σ3 = 0): %s MPa' % (n(R, 2), n(tabs, 2)),
          'von Mises: σ\' = √(σx² − σx·σy + σy² + 3·τxy²) = %s MPa; Tresca: σ1 − σ3 = %s MPa' % (n(vm, 2), n(tr, 2))]
    if theta is not None:
        c, s = math.cos(math.radians(2 * theta)), math.sin(math.radians(2 * theta))
        st = C + (sx - sy) / 2 * c + txy * s
        tt = -(sx - sy) / 2 * s + txy * c
        r.update(s_theta=st, t_theta=tt)
        Ls.append('Plano a θ = %s°: σ = C + (σx − σy)/2·cos 2θ + τxy·sen 2θ = %s MPa; τ = −(σx − σy)/2·sen 2θ + τxy·cos 2θ = %s MPa'
                  % (n(theta, 1), n(st, 2), n(tt, 2)))
    if fy:
        r['n_vm'], r['n_tr'] = fy / vm, fy / tr
        Ls.append('Coeficiente de seguridad: n = fy/σ\' = %s (von Mises); fy/(σ1 − σ3) = %s (Tresca, más conservador)'
                  % (n(fy / vm, 2), n(fy / tr, 2)))
    return r, Ls


# ------------------------------------------------------------------------------------------ comando seccion
def compuesta(rects, huecos=()):
    partes = [(1, b, h, y) for b, h, y in rects] + [(-1, b, h, y) for b, h, y in huecos]
    A = sum(s * b * h for s, b, h, _ in partes)
    if A <= 0:
        raise ValueError('el área total tiene que ser positiva')
    yc = sum(s * b * h * y for s, b, h, y in partes) / A
    Ls = ['Rectángulos centrados en el eje vertical; y = altura del centro de cada uno desde la base [mm]',
          'Baricentro: yc = Σ(A·y)/ΣA = %s mm; A = %s mm²' % (n(yc, 2), miles(A, 1))]
    I = 0.0
    for s, b, h, y in partes:
        Ic, d = b * h ** 3 / 12, y - yc
        I += s * (Ic + b * h * d ** 2)
        Ls.append('  %s %s × %s en y = %s: A = %s mm², Ic = b·h³/12 = %s mm⁴, d = %s mm, A·d² = %s mm⁴'
                  % ('+' if s > 0 else '−', med(b), med(h), med(y), miles(b * h), miles(Ic), n(d, 2), miles(b * h * d ** 2)))
    ymax = max(y + h / 2 for s, b, h, y in partes)
    ymin = min(y - h / 2 for s, b, h, y in partes)
    Ls.append('Steiner: I = Σ(Ic + A·d²) = %s mm⁴ = %s cm⁴' % (miles(I), g(I / 1e4, 4)))
    Ls.append('W = I/c: arriba %s cm³ (c = %s mm), abajo %s cm³ (c = %s mm)'
              % (g(I / (ymax - yc) / 1e3, 4), n(ymax - yc, 1), g(I / (yc - ymin) / 1e3, 4), n(yc - ymin, 1)))
    return {'A': A, 'yc': yc, 'I': I, 'Wsup': I / (ymax - yc), 'Winf': I / (yc - ymin)}, Ls


def lineas_seccion(s):
    Ls = ['%s' % s['nombre'],
          'A = %s mm² = %s cm²%s' % (miles(s['A'], 1), g(s['A'] / 100, 4), ('; %s kg/m' % n(s['G'], 1)) if s.get('G') else ''),
          'Eje fuerte y: I = %s cm⁴, W = %s cm³, i = %s cm' % (g(s['Iy'] / 1e4, 4), g(s['Wy'] / 1e3, 4), n(s['iy'] / 10, 3)),
          'Eje z: I = %s cm⁴, W = %s cm³, i = %s cm' % (g(s['Iz'] / 1e4, 4), g(s['Wz'] / 1e3, 4), n(s['iz'] / 10, 3))]
    f = s.get('forma')
    if f == 'rect':
        Ls.insert(1, 'Fórmulas: A = b·h; I = b·h³/12; W = b·h²/6; i = h/√12')
    elif f in ('circ', 'tubo'):
        Ls.insert(1, 'Fórmulas: A = π·(D² − d²)/4; I = π·(D⁴ − d⁴)/64; W = 2·I/D; J = 2·I; i = √(D² + d²)/4')
        Ls.append('Torsión: J = %s cm⁴; Wp = J/(D/2) = %s cm³' % (g(s['J'] / 1e4, 4), g(s['Wp'] / 1e3, 4)))
    elif f == 'doble-t':
        Ls.insert(1, 'Fórmulas: I = (b·h³ − (b − tw)·(h − 2·tf)³)/12; W = 2·I/h (sin radios: da un poco más que el catálogo)')
        Ls.append('Momento estático de media sección: Q = %s cm³ → τ máx = V·Q/(I·tw)' % g(s['Q'] / 1e3, 4))
    elif f == 'angulo':
        Ls.insert(1, 'Calculado con las medidas y los radios (verificar con el catálogo del proveedor)')
        Ls.append('Baricentro a e = %s cm del dorso; W = I/(a − e); ejes principales: Iu = %s cm⁴, Iv = %s cm⁴, iv = %s cm (mínimo)'
                  % (n(s['e'] / 10, 2), g(s['Iu'] / 1e4, 4), g(s['Iv'] / 1e4, 4), n(s['iv'] / 10, 3)))
    if s.get('catalogo'):
        Ls.append('i = √(I/A) calculado con los valores del catálogo.')
    return Ls


def cmd_seccion(a):
    t = a.tipo
    if t == 'rect':
        s = sec_rect(a.b, a.h)
    elif t == 'circ':
        s = sec_tubo(a.d, 0.0)
    elif t == 'tubo':
        di = a.di if a.di is not None else (a.D - 2 * a.e if a.e else None)
        if di is None:
            raise ValueError('tubo: --D y --di o --e')
        s = sec_tubo(a.D, di)
    elif t == 'doble-t':
        s = sec_doble_t(a.b, a.h, a.tw, a.tf)
    elif t == 'angulo':
        s = sec_angulo(a.a, a.t, a.r1, a.r2)
    elif t == 'perfil':
        s = sec_perfil(a.nombre)
    else:
        if not a.parte:
            raise ValueError('compuesta: una o más --parte BxH@Y (y --hueco BxH@Y)')
        return compuesta(a.parte, a.hueco or [])
    return s, lineas_seccion(s)


def parte_rect(s):
    if '@' not in s:
        raise argparse.ArgumentTypeError('se esperaba BxH@Y, por ejemplo 250x20@330: %s' % s)
    bh, y = s.split('@', 1)
    b, h = dupla(bh)
    return b, h, num(y)


def cmd_perfiles(a):
    serie = a.serie.upper()
    Ls = []
    if serie in ('IPN', 'UPN'):
        tabla = IPN if serie == 'IPN' else UPN
        Ls.append('%s  (%s)' % (serie, 'ArcelorMittal, medidas EN 10365:2017' if serie == 'IPN' else 'STAD, valores indicativos'))
        Ls.append('perfil    h    b   tw   tf   A cm²  kg/m   Iy cm⁴  Wy cm³  iy cm  Iz cm⁴  Wz cm³  iz cm')
        filas = [(k, sec_perfil('%s%d' % (serie, k))) for k in sorted(tabla)]
        for k, s in filas:
            h, b, tw, tf, A, G, Iy, Wy, Iz, Wz = tabla[k]
            Ls.append('%s %-4d %4d %4d %4s %4s %7s %5s %8s %7s %6s %7s %7s %6s' % (
                serie, k, h, b, n(tw, 1), n(tf, 1), n(A, 1), n(G, 1), g(Iy, 4), g(Wy, 3), n(s['iy'] / 10, 2), g(Iz, 3),
                g(Wz, 3), n(s['iz'] / 10, 2)))
    elif serie == 'L':
        Ls.append('Ángulos de alas iguales: calculados con las medidas y los radios (verificar con el catálogo)')
        Ls.append('perfil         r1  A cm²  kg/m   e cm   I cm⁴   W cm³   i cm  Iv cm⁴  iv cm')
        filas = []
        for (aa, t), r1 in sorted(ANGULOS.items()):
            s = sec_angulo(aa, t)
            filas.append(('L%dx%d' % (aa, t), s))
            Ls.append('L %3d×%3d×%2d  %3d %6s %5s %6s %7s %7s %6s %7s %6s' % (
                aa, aa, t, r1, n(s['A'] / 100, 2), n(s['G'], 2), n(s['e'] / 10, 2), g(s['Iy'] / 1e4, 4),
                g(s['Wy'] / 1e3, 3), n(s['iy'] / 10, 2), g(s['Iv'] / 1e4, 3), n(s['iv'] / 10, 2)))
    else:
        raise ValueError('series: IPN, UPN o L')
    if a.W or a.I or a.i:
        for k, s in filas:
            if (not a.W or s['Wy'] / 1e3 >= a.W) and (not a.I or s['Iy'] / 1e4 >= a.I) and (not a.i or s['imin'] / 10 >= a.i):
                Ls.append('El más liviano que cumple%s%s%s: %s'
                          % (' W ≥ %s cm³' % med(a.W) if a.W else '', ' I ≥ %s cm⁴' % med(a.I) if a.I else '',
                             ' i mín ≥ %s cm' % med(a.i) if a.i else '', s['nombre']))
                break
        else:
            Ls.append('Ninguno de la serie cumple.')
    return Ls


# ------------------------------------------------------------------------------------------ demo
def cerca(x, y, tol):
    return abs(x - y) <= tol


class _Opc:
    """Opciones de viga para usar desde el demo."""
    def __init__(self, **k):
        base = dict(tipo='apoyada', L=1.0, P=[], q=[], M=[], apoyos=None, I=None, W=None, peso_propio=False,
                    sadm=None, fy=None, limite=None, tramos=400)
        base.update(k)
        self.__dict__.update(base)


def cmd_demo():
    ok = []
    # 1) Ejemplo del SKILL.md: viga de entrepiso de un galpón, IPN 200, L = 5 m, q = 6 kN/m y P = 10 kN a 2 m
    sec = sec_perfil('IPN200')
    r, _ = analizar_viga(_Opc(L=5, P=[(10, 2)], q=[(6, None, None)], sadm=235 / 1.5, fy=235, limite=250), sec)
    EI = 200000 * 2140 * 1e-5
    centro = 5 * 6 * 5 ** 4 / (384 * EI) + 10 * 2 * (3 * 25 - 4 * 4) / (48 * EI)
    ok.append(('viga del SKILL.md: RA = %s, RB = %s kN, M = %s kN·m en x = %s m, σ = %s MPa'
               % (n(r['RA']), n(r['RB']), n(r['Mmax']), n(r['xMmax']), n(r['sigma'], 1)),
               cerca(r['RA'], 21, 1e-9) and cerca(r['RB'], 19, 1e-9) and cerca(r['Mmax'], 30, 1e-9)
               and cerca(r['xMmax'], 2, 1e-9) and cerca(r['sigma'], 140.19, 0.01)))
    yc = -r['viga'].flecha(2.5) * 1000
    ok.append(('  flecha al centro %s mm = superposición 5·q·L⁴/(384·E·I) + P·b·(3·L² − 4·b²)/(48·E·I) = %s mm'
               % (n(yc, 4), n(centro * 1000, 4)), cerca(yc, centro * 1000, 1e-9)))
    ok.append(('  flecha máxima %s mm en x = %s m (≤ L/250 = 20 mm)' % (n(r['f'], 3), n(r['xf'], 3)),
               cerca(r['f'], 17.161, 0.001) and cerca(r['xf'], 2.448, 0.001) and r['f'] <= 20))
    # 2) Fórmulas cerradas de tabla contra la integración numérica (E·I = 1000 kN·m², L = 4 m)
    EIc, Lc, Pc, qc = 1000.0, 4.0, 10.0, 5.0
    casos = [('apoyada, q: 5·q·L⁴/(384·E·I)', 'apoyada', [], [(qc, None, None)], 5 * qc * Lc ** 4 / (384 * EIc), Lc / 2),
             ('apoyada, P al centro: P·L³/(48·E·I)', 'apoyada', [(Pc, 2.0)], [], Pc * Lc ** 3 / (48 * EIc), Lc / 2),
             ('apoyada, P a 3 m: P·b·(L² − b²)^1,5/(9·√3·L·E·I)', 'apoyada', [(Pc, 3.0)], [],
              Pc * 1 * (Lc ** 2 - 1) ** 1.5 / (9 * math.sqrt(3) * Lc * EIc), math.sqrt((Lc ** 2 - 1) / 3)),
             ('voladizo, P en el extremo: P·L³/(3·E·I)', 'voladizo', [(Pc, Lc)], [], Pc * Lc ** 3 / (3 * EIc), Lc),
             ('voladizo, q: q·L⁴/(8·E·I)', 'voladizo', [], [(qc, None, None)], qc * Lc ** 4 / (8 * EIc), Lc),
             ('voladizo, P a 1,5 m: P·a²·(3·L − a)/(6·E·I)', 'voladizo', [(Pc, 1.5)], [],
              Pc * 1.5 ** 2 * (3 * Lc - 1.5) / (6 * EIc), Lc)]
    for nombre, tipo, P, q, f_ref, x_ref in casos:
        v = Viga(tipo, Lc, P, q)
        v.resolver(EIc, 50)
        x, yy = v.flecha_maxima()
        ok.append(('flecha numérica = fórmula, %s: %s mm' % (nombre, n(-yy * 1000, 4)),
                   cerca(-yy, f_ref, 1e-9 * f_ref + 1e-12) and cerca(x, x_ref, 1e-6)))
    v1, v2, v3 = Viga('apoyada', Lc, [(Pc, 1.0)], []), Viga('apoyada', Lc, [], [(qc, 1.0, 3.5)]), \
        Viga('apoyada', Lc, [(Pc, 1.0)], [(qc, 1.0, 3.5)])
    for v in (v1, v2, v3):
        v.resolver(EIc, 40)
    sup = all(cerca(v3.flecha(x), v1.flecha(x) + v2.flecha(x), 1e-12) for x in (0.7, 1.9, 2.6, 3.3))
    equi = cerca(v3.Mf(Lc), 0, 1e-9) and cerca(v3.V(Lc, True), 0, 1e-9)
    vol = Viga('voladizo', Lc, [(Pc, 2.0)], [(qc, None, None)])
    equi = equi and cerca(vol.Mf(Lc), 0, 1e-9) and cerca(vol.V(Lc, True), 0, 1e-9)
    ok.append(('superposición (P + q parcial = P sola + q sola) y equilibrio en los extremos libres', sup and equi))
    # 3) Podut (2018), cap. 3, problema 2: bulón calentado a 250 °C, apretado sin tensión, trabaja a 50 °C
    r, _ = axial(0, 0.3, math.pi * 50 ** 2 / 4, 200000, -200, 11.7e-6, impedida=True)
    ok.append(('Podut cap. 3 prob. 2 (dilatación impedida): σ = %s MPa, ε = %s, F = %s kN (libro: 468 MPa; 0,00234; 919 kN)'
               % (n(r['sigma_t'], 1), n(r['eps_t'] * -1, 5), n(r['F_t'], 1)),
               cerca(r['sigma_t'], 468, 0.05) and cerca(-r['eps_t'], 0.00234, 1e-8) and cerca(r['F_t'], 919, 0.5)))
    # 4) Podut (2018), cap. 9, problema 2: 3500 kW a 160 rpm, eje de 180 mm, 6 bulones de 40 mm en 340 mm
    r, _ = torsion(180, P=3500, rpm=160, L=2, G=85000)
    rc, _ = corte(40, T=r['T'], dp=340, pernos=6)
    ok.append(('Podut cap. 9 prob. 2 (torsión y bulones): τ eje = %s MPa, τ bulón = %s MPa (libro: 182,4 y 162,97)'
               % (n(r['tau'], 2), n(rc['tau'], 2)), cerca(r['tau'], 182.4, 0.05) and cerca(rc['tau'], 162.97, 0.005)))
    # 5) Gere, ejemplo 3-8: eje ABC de 50 mm, motor de 50 kW a 10 Hz en A; engranajes de 35 kW (B) y 15 kW (C)
    rab, _ = torsion(50, P=50, rpm=600, L=1.0, G=80000)
    rbc, _ = torsion(50, P=15, rpm=600, L=1.2, G=80000)
    fi = math.degrees(rab['theta'] + rbc['theta'])
    ok.append(('Gere ej. 3-8: TA = %s N·m, τAB = %s MPa, τBC = %s MPa, φAC = %s° (libro: 796; 32,4; 9,7; 1,26°)'
               % (n(rab['T'], 0), n(rab['tau'], 1), n(rbc['tau'], 1), n(fi, 2)),
               cerca(rab['T'], 796, 0.5) and cerca(rab['tau'], 32.4, 0.05) and cerca(rbc['tau'], 9.7, 0.05) and cerca(fi, 1.26, 0.005)))
    # 6) Pandeo: puntal de tubo 80 × 4 mm, 2,5 m, articulado; teoría de K y continuidad de las curvas
    s = sec_tubo(80, 72)
    r, _ = pandeo(2.5, s, 1.0, 235, 200000, P=50)
    I = math.pi / 64 * (80 ** 4 - 72 ** 4)
    ok.append(('puntal del SKILL.md: λ = %s, Johnson %s MPa → Pcr = %s kN; Euler %s kN; CIRSOC φc·Pn = %s kN'
               % (n(r['lam'], 1), n(r['sigma_cr'], 1), n(r['Pcr'], 1), n(r['Pe'], 1), n(r['phiPn'], 1)),
               cerca(r['lam'], 92.91, 0.01) and cerca(r['sigma_cr'], 174.62, 0.01) and cerca(r['Pcr'], 166.77, 0.01)
               and cerca(r['Pe'], math.pi ** 2 * 200000 * I / 2500 ** 2 / 1000, 1e-9) and cerca(r['phiPn'], 124.08, 0.01)))
    lo, hi = 4.4, 4.6
    for _ in range(100):
        m = (lo + hi) / 2
        lo, hi = (lo, m) if math.tan(m) - m > 0 else (m, hi)
    lam1 = math.sqrt(2 * math.pi ** 2 * 200000 / 235)
    tang = cerca(235 - (235 * lam1 / (2 * math.pi)) ** 2 / 200000, math.pi ** 2 * 200000 / lam1 ** 2, 1e-9)
    cont = abs(0.658 ** 2.25 / (0.877 / 2.25) - 1) < 0.001
    ok.append(('K teórico empotrado-articulado = π/4,4934 = %s; Johnson tangente a Euler en λ1 = %s; CIRSOC continuo en λc = 1,5'
               % (n(math.pi / m, 3), n(lam1, 1)), cerca(math.pi / m, 0.699, 0.001) and tang and cont))
    # 7) Mohr: σx = 80, σy = 0, τxy = −50 MPa
    r, _ = mohr(80, 0, -50, fy=250)
    st, _ = mohr(80, 0, -50, theta=r['theta1'])
    inv = cerca(r['s1'] + r['s2'], 80, 1e-9) and cerca(r['s1'] * r['s2'], -2500, 1e-9)
    vm_p = math.sqrt(r['s1'] ** 2 - r['s1'] * r['s2'] + r['s2'] ** 2)
    ok.append(('Mohr: σ1 = %s, σ2 = %s MPa, θ1 = %s°, von Mises %s MPa; invariantes y τ = 0 en θ1'
               % (n(r['s1'], 2), n(r['s2'], 2), n(r['theta1'], 2), n(r['vm'], 2)),
               cerca(r['s1'], 104.03, 0.005) and cerca(r['s2'], -24.03, 0.005) and cerca(r['theta1'], -25.67, 0.005)
               and inv and cerca(vm_p, r['vm'], 1e-9) and cerca(st['t_theta'], 0, 1e-9) and cerca(st['s_theta'], r['s1'], 1e-9)))
    # 8) Secciones: Steiner contra la fórmula directa y ángulos contra STAD
    dt = sec_doble_t(90, 200, 7.5, 11.3)
    cp, _ = compuesta([(90, 11.3, 200 - 11.3 / 2), (7.5, 200 - 22.6, 100), (90, 11.3, 11.3 / 2)])
    rect = sec_rect(30, 60)
    ok.append(('doble T de chapas: fórmula %s cm⁴ = Steiner %s cm⁴; rectángulo 30 × 60: I = %s cm⁴'
               % (n(dt['Iy'] / 1e4, 1), n(cp['I'] / 1e4, 1), n(rect['Iy'] / 1e4, 1)),
               cerca(dt['Iy'], cp['I'], 1e-6) and cerca(cp['yc'], 100, 1e-9) and cerca(rect['Iy'], 30 * 60 ** 3 / 12, 1e-9)))
    a100, a120 = sec_angulo(100, 10), sec_angulo(120, 12)
    areas = max(abs(sec_angulo(*k)['A'] / 100 / v - 1) for k, v in STAD_AREA_L.items())
    ok.append(('ángulos: L 100×10 I = %s cm⁴, W = %s cm³ (STAD 177; 24,6); L 120×12 I = %s, W = %s, i = %s (368; 42,7; 3,65); áreas ±%s %%'
               % (n(a100['Iy'] / 1e4, 1), n(a100['Wy'] / 1e3, 2), n(a120['Iy'] / 1e4, 1), n(a120['Wy'] / 1e3, 2),
                  n(a120['iy'] / 10, 2), n(100 * areas, 2)),
               cerca(a100['Iy'] / 1e4, 177, 0.5) and cerca(a100['Wy'] / 1e3, 24.6, 0.05) and cerca(a120['Iy'] / 1e4, 368, 0.5)
               and cerca(a120['Wy'] / 1e3, 42.7, 0.05) and cerca(a120['iy'] / 10, 3.65, 0.005) and areas < 0.003))
    # 9) Catálogo: coherencia interna de las tablas IPN y UPN
    peor_w = max(abs(t[7] / (2 * t[6] / (t[0] / 10)) - 1) for tb in (IPN, UPN) for t in tb.values())
    peor_g = max(abs(t[5] / (0.785 * t[4]) - 1) for tb in (IPN, UPN) for t in tb.values())
    ok.append(('tablas IPN y UPN: W = 2·I/h (peor %s %%) y peso = 0,785·A (peor %s %%)' % (n(100 * peor_w, 2), n(100 * peor_g, 2)),
               peor_w < 0.01 and peor_g < 0.02))
    for nombre, bien in ok:
        print('  %s %s' % ('ok ' if bien else 'MAL', nombre))
    todo = all(b for _, b in ok)
    print('DEMO %s' % ('OK' if todo else 'FALLO'))
    return 0 if todo else 1


# ------------------------------------------------------------------------------------------ línea de comandos
class FormatoES(argparse.RawDescriptionHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        return super().add_usage(usage, actions, groups, prefix='uso: ' if prefix is None else prefix)


class ParserES(argparse.ArgumentParser):
    TRADUCIR = [('the following arguments are required', 'faltan estos argumentos'),
                ('one of the arguments', 'falta uno de los argumentos'), ('is required', 'es obligatorio'),
                ('invalid choice', 'opción no válida'), ('choose from', 'elegir entre'),
                ('unrecognized arguments', 'argumentos no reconocidos'), ('expected one argument', 'falta el valor'),
                ('not allowed with argument', 'no se puede usar junto con'), ('invalid', 'valor no válido para'),
                ('argument ', 'argumento '), ('value', '')]

    def __init__(self, *a, **k):
        k.setdefault('formatter_class', FormatoES)
        k.setdefault('add_help', False)
        super().__init__(*a, **k)
        self._positionals.title = 'argumentos'
        self._optionals.title = 'opciones'
        self.add_argument('-h', '--help', action='help', help='muestra esta ayuda y sale')

    def error(self, mensaje):
        for en, es in self.TRADUCIR:
            mensaje = mensaje.replace(en, es)
        self.print_usage(sys.stderr)
        self.exit(2, '%s: error: %s\n' % (self.prog, mensaje))


def _opciones_seccion(p, con_perfil=True):
    if con_perfil:
        p.add_argument('--perfil', help='perfil de catálogo: IPN200, UPN100, L50x5 …')
    p.add_argument('--tubo', type=dupla, metavar='DxE', help='tubo: diámetro exterior × espesor en mm, por ejemplo 80x4')
    p.add_argument('--circ', type=num, metavar='D', help='barra redonda maciza de diámetro D en mm')
    p.add_argument('--rect', type=dupla, metavar='BxH', help='rectángulo de base B y altura H en mm, por ejemplo 100x200')


def construir_parser():
    ap = ParserES(prog='resistencia.py', description=__doc__)
    sp = ap.add_subparsers(dest='cmd', required=True, title='comandos', metavar='COMANDO', parser_class=ParserES)
    p = sp.add_parser('axial', help='tracción, compresión y dilatación térmica', description='Barra con carga axial y dilatación térmica.')
    p.add_argument('--F', type=num, default=0.0, help='fuerza axial en kN (+ tracción, − compresión)')
    p.add_argument('--L', type=num, required=True, help='largo de la barra en m')
    p.add_argument('--A', type=num, help='área en mm²')
    p.add_argument('--d', type=num, help='diámetro de una barra redonda en mm')
    _opciones_seccion(p)
    p.add_argument('--E', type=num, default=E_ACERO, help='módulo de elasticidad en MPa (200 000: acero, CIRSOC 301)')
    p.add_argument('--dT', type=num, help='variación de temperatura en °C (+ calentamiento)')
    p.add_argument('--alfa', type=num, default=ALFA_ACERO, help='coeficiente de dilatación en 1/°C (12e-6: acero)')
    p.add_argument('--impedida', action='store_true', help='los extremos no se pueden mover (apoyos rígidos)')
    p.add_argument('--holgura', type=num, default=0.0, help='holgura en mm antes de que tope (solo al calentar)')
    p.add_argument('--fy', type=num, help='tensión de fluencia en MPa, para el coeficiente de seguridad')
    p = sp.add_parser('corte', help='pernos y pasadores en corte simple o doble, y aplastamiento',
                      description='Corte directo en pernos, bulones y pasadores, y aplastamiento de la chapa.')
    p.add_argument('--F', type=num, help='fuerza total en kN')
    p.add_argument('--T', type=num, help='torque en N·m que transmite un acoplamiento de bridas (con --dp)')
    p.add_argument('--dp', type=num, help='diámetro de la circunferencia de los pernos en mm')
    p.add_argument('--d', type=num, required=True, help='diámetro del perno en la zona de corte, en mm')
    p.add_argument('--planos', type=int, default=1, choices=[1, 2], help='planos de corte: 1 simple, 2 doble')
    p.add_argument('--pernos', type=int, default=1, help='cantidad de pernos que se reparten la fuerza')
    p.add_argument('--t', type=num, help='espesor que apoya, en mm, para el aplastamiento')
    p.add_argument('--fy', type=num, help='fluencia del perno en MPa')
    p = sp.add_parser('torsion', help='ejes macizos y huecos', description='Torsión de ejes circulares macizos o huecos.')
    p.add_argument('--T', type=num, help='torque en N·m')
    p.add_argument('--P', type=num, help='potencia en kW (con --rpm)')
    p.add_argument('--rpm', type=num, help='velocidad en vueltas por minuto')
    p.add_argument('--d', type=num, required=True, help='diámetro exterior en mm')
    p.add_argument('--di', type=num, default=0.0, help='diámetro interior en mm (eje hueco)')
    p.add_argument('--L', type=num, default=1.0, help='largo en m para el ángulo de giro (1 m por defecto)')
    p.add_argument('--G', type=num, default=G_ACERO, help='módulo de corte en MPa (77 200: acero, CIRSOC 301)')
    p.add_argument('--tadm', type=num, help='tensión de corte admisible en MPa: da el diámetro mínimo')
    p.add_argument('--giro-adm', type=num, dest='giro_adm', help='giro admisible en °/m: da el diámetro mínimo por rigidez')
    p.add_argument('--fy', type=num, help='fluencia en MPa, para el coeficiente de seguridad')
    p = sp.add_parser('viga', help='reacciones, diagramas, tensiones y flecha', description=Viga.__doc__)
    p.add_argument('--tipo', required=True, choices=['apoyada', 'voladizo'], help='apoyada (dos apoyos) o voladizo (empotrada en x = 0)')
    p.add_argument('--L', type=num, required=True, help='largo de la viga en m')
    p.add_argument('--P', type=carga_en, action='append', metavar='kN@x', help='carga puntual hacia abajo, por ejemplo 10@2 (se repite)')
    p.add_argument('--q', type=carga_q, action='append', metavar='kN/m[@x1:x2]', help='carga uniforme: 6 (todo el largo) o 6@0:3 (se repite)')
    p.add_argument('--M', type=carga_en, action='append', metavar='kN·m@x', help='par aplicado, antihorario positivo')
    p.add_argument('--apoyos', type=tramo, metavar='x1:x2', help='posición de los apoyos en m (por defecto los extremos)')
    p.add_argument('--I', type=num, help='momento de inercia en cm⁴')
    p.add_argument('--W', type=num, help='módulo resistente en cm³')
    _opciones_seccion(p)
    p.add_argument('--eje', choices=['y', 'z'], default='y', help='eje de flexión del perfil (y fuerte, z débil)')
    p.add_argument('--peso-propio', dest='peso_propio', action='store_true', help='suma el peso del perfil como carga uniforme')
    p.add_argument('--elegir', metavar='SERIE', help='elige el perfil más liviano de la serie IPN o UPN que verifica')
    p.add_argument('--E', type=num, default=E_ACERO, help='módulo de elasticidad en MPa (200 000: acero)')
    p.add_argument('--sadm', type=num, help='tensión admisible en MPa')
    p.add_argument('--fy', type=num, help='fluencia en MPa (con --n da la admisible σadm = fy/n)')
    p.add_argument('--n', type=num, help='coeficiente de seguridad para la admisible')
    p.add_argument('--limite', type=num, help='flecha admisible como L/limite, por ejemplo 250 o 300')
    p.add_argument('--tramos', type=int, default=400, help='tramos de la integración numérica (400)')
    p.add_argument('--csv', metavar='ARCHIVO', help='guarda la tabla x, V, M, giro, flecha')
    p.add_argument('--decimal', choices=['coma', 'punto'], default='coma', help='coma (con ;) para Excel en castellano, o punto')
    p = sp.add_parser('pandeo', help='columnas: Euler, Johnson y CIRSOC 301', description='Pandeo flexional de columnas.')
    p.add_argument('--L', type=num, required=True, help='largo de la columna en m')
    p.add_argument('--vinculos', choices=sorted(VINCULOS), help='art-art (K 1), emp-libre (2), emp-art (0,7), emp-emp (0,5)')
    p.add_argument('--K', type=num, help='factor de longitud efectiva, si no se usa --vinculos')
    _opciones_seccion(p)
    p.add_argument('--A', type=num, help='área en cm² (con --I o --i)')
    p.add_argument('--I', type=num, help='momento de inercia mínimo en cm⁴')
    p.add_argument('--i', type=num, help='radio de giro mínimo en cm')
    p.add_argument('--eje', choices=['min', 'y'], default='min', help='radio de giro: mínimo (por defecto) o del eje fuerte y')
    p.add_argument('--fy', type=num, default=FY_F24, help='fluencia en MPa (235: F-24)')
    p.add_argument('--E', type=num, default=E_ACERO, help='módulo de elasticidad en MPa')
    p.add_argument('--P', type=num, help='carga de servicio en kN: da n = Pcr/P')
    p.add_argument('--Pu', type=num, help='carga mayorada en kN: se compara con φc·Pn del CIRSOC 301')
    p.add_argument('--tetmajer', metavar='a,b,λ0', help='recta de Tetmajer σ = a − b·λ hasta λ0 (de tabla), por ejemplo 310,1.14,105')
    p = sp.add_parser('mohr', help='tensiones principales, von Mises y Tresca', description='Estado plano de tensiones.')
    p.add_argument('--sx', type=num, required=True, help='σx en MPa (+ tracción)')
    p.add_argument('--sy', type=num, default=0.0, help='σy en MPa')
    p.add_argument('--txy', type=num, default=0.0, help='τxy en MPa (+ si en la cara +x apunta a +y)')
    p.add_argument('--theta', type=num, help='ángulo de un plano en grados (antihorario desde x)')
    p.add_argument('--fy', type=num, help='fluencia en MPa, para el coeficiente de seguridad')
    p = sp.add_parser('seccion', help='propiedades de secciones', description='Área, I, W e i; Steiner en la compuesta. Medidas en mm.')
    p.add_argument('tipo', choices=['rect', 'circ', 'tubo', 'doble-t', 'angulo', 'perfil', 'compuesta'])
    for x, ayuda in (('b', 'base o ancho de ala'), ('h', 'altura'), ('d', 'diámetro (círculo)'), ('D', 'diámetro exterior (tubo)'),
                     ('di', 'diámetro interior (tubo)'), ('e', 'espesor de pared (tubo)'), ('tw', 'espesor del alma'),
                     ('tf', 'espesor del ala'), ('a', 'ala del ángulo'), ('t', 'espesor del ángulo'),
                     ('r1', 'radio de raíz del ángulo'), ('r2', 'radio de borde del ángulo')):
        p.add_argument('--' + x, type=num, help=ayuda)
    p.add_argument('--nombre', help='perfil de catálogo: IPN200, UPN100, L50x5')
    p.add_argument('--parte', type=parte_rect, action='append', metavar='BxH@Y', help='rectángulo de la compuesta (Y: altura de su centro)')
    p.add_argument('--hueco', type=parte_rect, action='append', metavar='BxH@Y', help='rectángulo que se resta')
    p = sp.add_parser('perfiles', help='tablas de catálogo y el más liviano que cumple', description='Tablas IPN, UPN y ángulos.')
    p.add_argument('serie', choices=['IPN', 'UPN', 'L', 'ipn', 'upn', 'l'])
    p.add_argument('--W', type=num, help='W mínimo en cm³')
    p.add_argument('--I', type=num, help='I mínimo en cm⁴')
    p.add_argument('--i', type=num, help='radio de giro mínimo en cm')
    sp.add_parser('demo', help='verifica todo contra ejemplos de libro y fórmulas cerradas',
                  description='Reproduce los ejemplos del SKILL.md y de libro; termina en DEMO OK.')
    return ap


def main(argv=None):
    a = construir_parser().parse_args(argv)
    try:
        if a.cmd == 'demo':
            return cmd_demo()
        if a.cmd == 'axial':
            sec = seccion_de(a)
            A = sec['A'] if sec else (a.A if a.A else (math.pi * a.d ** 2 / 4 if a.d else None))
            if not A:
                raise ValueError('falta la sección: --A, --d, --tubo, --rect o --perfil')
            _, L = axial(a.F, a.L, A, a.E, a.dT, a.alfa, a.impedida, a.holgura, a.fy)
        elif a.cmd == 'corte':
            _, L = corte(a.d, a.F, a.T, a.dp, a.planos, a.pernos, a.t, a.fy)
        elif a.cmd == 'torsion':
            _, L = torsion(a.d, a.T, a.P, a.rpm, a.di, a.L, a.G, a.tadm, a.giro_adm, a.fy)
        elif a.cmd == 'viga':
            if a.fy and a.n and not a.sadm:
                a.sadm = a.fy / a.n
            if a.elegir:
                r, L = elegir_perfil(a, a.E)
            else:
                sec = seccion_de(a, a.eje)
                r, L = analizar_viga(a, sec, a.E)
            if a.csv:
                csv_viga(r['viga'], a.csv, a.decimal)
                L.append('Tabla guardada en %s' % a.csv)
        elif a.cmd == 'pandeo':
            if a.vinculos:
                K, vinc = VINCULOS[a.vinculos]
            elif a.K:
                K, vinc = a.K, None
            else:
                raise ValueError('indicá --vinculos o --K')
            sec = seccion_de(a)
            if sec is None:
                if not a.A or not (a.I or a.i):
                    raise ValueError('falta la sección: --perfil, --tubo, --circ, --rect o --A con --I o --i')
                i_mm = a.i * 10 if a.i else math.sqrt(a.I * 1e4 / (a.A * 100))
                sec = {'nombre': 'dada', 'A': a.A * 100, 'imin': i_mm, 'iy': i_mm}
            sec['usar_min'] = a.eje == 'min'
            tet = None
            if a.tetmajer:
                try:
                    tet = [num(x) for x in a.tetmajer.replace(';', ',').split(',')] if a.tetmajer.count(',') == 2 \
                        else [num(x) for x in a.tetmajer.split(';')]
                    assert len(tet) == 3
                except (AssertionError, argparse.ArgumentTypeError):
                    raise ValueError('--tetmajer va como a,b,λ0 con punto decimal (310,1.14,105) o a;b;λ0 con coma')
            _, L = pandeo(a.L, sec, K, a.fy, a.E, a.P, a.Pu, tet, vinc)
        elif a.cmd == 'mohr':
            _, L = mohr(a.sx, a.sy, a.txy, a.theta, a.fy)
        elif a.cmd == 'seccion':
            _, L = cmd_seccion(a)
        else:
            L = cmd_perfiles(a)
    except (ValueError, ZeroDivisionError) as ex:
        print('resistencia.py: %s' % ex, file=sys.stderr)
        return 2
    print('\n'.join(L))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
        sys.stderr.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
