#!/usr/bin/env python3
"""seguridad.py - calculos de higiene y seguridad en el trabajo en Argentina (solo biblioteca estandar).

Cada comando imprime formula, reemplazo, resultado y la fuente del valor normativo, con coma decimal.
  carga-fuego (--sup m2 | --largo m --ancho m) --material NOMBRE=kg [--material ...] [--riesgo 1-7]
              [--ventilacion natural|mecanica] [--actividad industrial|residencial|espectaculos]
              [--sup-liquido m2] [--electrico]
        carga de fuego en kg/m2 de madera equivalente (Dec. 351/79, Anexo VII), resistencia al fuego,
        potencial extintor minimo y cantidad minima de matafuegos (arts. 176 a 178).
        NOMBRE=kg usa la tabla embebida (ver 'materiales'); NOMBRE=kg:MJkg usa un poder calorifico propio.
  materiales      tabla de poderes calorificos embebida, con su fuente
  ruido --exp dBA:horas [--exp ...] [--criterio formula|tabla] [--nrr dB] [--pico dBC]
        dosis, nivel continuo equivalente y tiempo permitido (Res. MTEySS 295/03, Anexo V: 85 dBA y 3 dB);
        con --nrr, el nivel estimado bajo el protector (OSHA 29 CFR 1910.95, apendice B)
  tgbh --tbh C --tg C [--sol --tbs C] [--ropa verano|tela|doble] [--carga ligero|moderado|pesado] [--regimen 100|75|50|25]
        indice TGBH y valor limite de estres termico (Res. MTEySS 295/03)
  ventilacion --personas N --volumen m3 [--actividad sedentaria|moderada]   caudal minimo (Dec. 351/79, art. 66)
  distancia --kv kV      distancia minima de seguridad a partes con tension (Dec. 351/79, Anexo VI, 1.1.5)
  riesgo --p baja|media|alta --s ld|d|ed      nivel de riesgo y accion (matriz 3 x 3 del INSHT)
  demo                   reproduce los ejemplos del SKILL.md y los controla con cuentas a mano
Orienta un trabajo practico o un estudio previo: no reemplaza al profesional de higiene y seguridad matriculado.
"""
import argparse
import math
import sys

# ------------------------------------------------------------------------------------------ datos
MADERA = 18.41   # MJ/kg, patron de la carga de fuego: Dec. 351/79, Anexo VII, 1.2
KCAL = 4.184     # kJ/kcal (caloria termoquimica): 4400 kcal/kg x 4,184 = 18 410 kJ/kg

T14 = 'RD 2267/2004 (España), Anexo I, tabla 1.4'
# nombre: (poder calorifico en MJ/kg, como figura en la fuente, fuente, riesgo si el Dec. 351/79 lo da como ejemplo en 1.5)
MATERIALES = {
    'madera': (18.41, 'madera (patrón)', 'Dec. 351/79, Anexo VII, 1.2; la tabla 1.4 da 16,7', 3),
    'papel': (16.7, 'papel', T14, 3),
    'carton': (16.7, 'cartón', T14, None),
    'celulosa': (16.7, 'celulosa', T14, None),
    'azucar': (16.7, 'azúcar', T14, None),
    'cereales': (16.7, 'cereales', T14, None),
    'harina': (16.7, 'harina de trigo', T14, None),
    'cafe': (16.7, 'café', T14, None),
    'tabaco': (16.7, 'tabaco', T14, None),
    'leche-en-polvo': (16.7, 'leche en polvo', T14, None),
    'lana': (21.0, 'lana', T14, 4),
    'seda': (21.0, 'seda', T14, None),
    'cuero': (21.0, 'cuero', T14, 4),
    'pvc': (21.0, 'cloruro de polivinilo', T14, None),
    'poliuretano': (25.1, 'poliuretano', T14, None),
    'poliester': (25.1, 'poliéster', T14, None),
    'poliamida': (29.3, 'poliamida', T14, None),
    'polietileno': (42.0, 'polietileno', T14, None),
    'poliestireno': (42.0, 'poliestireno', T14, None),
    'caucho': (42.0, 'caucho', T14, None),
    'carbon': (31.4, 'carbón', T14, None),
    'antracita': (33.5, 'antracita', T14, None),
    'parafina': (46.0, 'parafina', T14, None),
    'grasas': (42.0, 'grasas', T14, None),
    'aceite-mineral': (42.0, 'aceite mineral', T14, None),
    'aceite-oliva': (42.0, 'aceite de oliva', T14, None),
    'aceite-lino': (37.2, 'aceite de lino', T14, None),
    'gasoleo': (42.0, 'gasóleo', T14, None),
    'petroleo': (42.0, 'petróleo', T14, None),
    'bencina': (42.0, 'bencina', T14, None),
    'benzol': (42.0, 'benzol', T14, 2),
    'tolueno': (42.0, 'toluol', T14, None),
    'acetona': (29.3, 'acetona', T14, 2),
    'alcohol-etilico': (25.1, 'alcohol etílico', T14, 2),
    'alcohol-metilico': (21.0, 'alcohol metílico', T14, 2),
    'butano': (46.0, 'butano', T14, None),
    'propano': (46.0, 'propano', T14, None),
    'metano': (50.2, 'metano', T14, None),
    'acetileno': (50.2, 'acetileno', T14, None),
}
RIESGOS = {1: 'explosivo', 2: 'inflamable', 3: 'muy combustible', 4: 'combustible', 5: 'poco combustible',
           6: 'incombustible', 7: 'refractario'}   # Dec. 351/79, Anexo VII, 1.5
TRAMOS = ['hasta 15 kg/m²', 'desde 16 hasta 30 kg/m²', 'desde 31 hasta 60 kg/m²', 'desde 61 hasta 100 kg/m²',
          'más de 100 kg/m²']   # filas de los cuadros 2.2.1, 2.2.2 y de las tablas 1 y 2 del Anexo VII
# Resistencia al fuego (Anexo VII, cuadros 2.2.1 y 2.2.2), por riesgo 1 a 5 y tramo; None = la celda dice "-"
F_NATURAL = {1: [None] * 5, 2: ['F 60', 'F 90', 'F 120', 'F 180', 'F 180'], 3: ['F 30', 'F 60', 'F 90', 'F 120', 'F 180'],
             4: ['F 30', 'F 30', 'F 60', 'F 90', 'F 120'], 5: [None, 'F 30', 'F 30', 'F 60', 'F 90']}
F_MECANICA = {1: [None] * 5, 2: ['NP'] * 5, 3: ['F 60', 'F 90', 'F 120', 'F 180', 'NP'],
              4: ['F 60', 'F 60', 'F 90', 'F 120', 'F 180'], 5: ['F 30', 'F 60', 'F 60', 'F 90', 'F 120']}
# Potencial extintor minimo (Anexo VII, tablas 1 y 2); 'caso' = se determina en cada caso
POT_A = {1: [None] * 5, 2: [None] * 5, 3: ['1 A', '2 A', '3 A', '6 A', 'caso'], 4: ['1 A', '1 A', '2 A', '4 A', 'caso'],
         5: ['1 A', '1 A', '1 A', '3 A', 'caso']}
POT_B = {1: [None] * 5, 2: ['6 B', '8 B', '10 B', '20 B', 'caso'], 3: ['4 B', '6 B', '8 B', '10 B', 'caso'],
         4: [None] * 5, 5: [None] * 5}
NO_PERMITIDO = {'residencial': (1, 2), 'espectaculos': (1, 2), 'industrial': ()}   # Anexo VII, cuadro 2.1

# Estres termico (Res. MTEySS 295/03; texto vigente del anexo en la biblioteca de AFIP): TGBH limite en °C
TGBH_LIM = {100: {'ligero': 29.5, 'moderado': 27.5, 'pesado': 26.0},
            75: {'ligero': 30.5, 'moderado': 28.5, 'pesado': 27.5},
            50: {'ligero': 31.5, 'moderado': 29.5, 'pesado': 28.5},
            25: {'ligero': 32.5, 'moderado': 31.0, 'pesado': 30.0}}
ROPA = {'verano': 0.0, 'tela': 3.5, 'doble': 5.0}   # °C que se suman al TGBH medido (misma fuente)

# Dec. 351/79, art. 66: cubaje del local por persona [m3] -> caudal de aire por persona [m3/h]
VENTILACION = {'sedentaria': [(3, 43), (6, 29), (9, 21), (12, 15), (15, 12)],
               'moderada': [(3, 65), (6, 43), (9, 31), (12, 23), (15, 18)]}

# Dec. 351/79, Anexo VI, 1.1.5: (tension hasta [kV], distancia minima [m])
DISTANCIAS = [(0.05, None), (1, 0.80), (33, 0.80), (66, 0.90), (132, 1.50), (150, 1.65), (220, 2.10), (330, 2.90),
              (500, 3.60)]

# Matriz de riesgos del INSHT (España), "Evaluación de riesgos laborales": probabilidad x consecuencias
PROB = {'baja': 0, 'media': 1, 'alta': 2}
CONS = {'ld': 0, 'd': 1, 'ed': 2}
NOMBRE_PROB = ['baja', 'media', 'alta']
NOMBRE_CONS = ['ligeramente dañino', 'dañino', 'extremadamente dañino']
MATRIZ = [['trivial', 'tolerable', 'moderado'], ['tolerable', 'moderado', 'importante'],
          ['moderado', 'importante', 'intolerable']]
ACCION = {
    'trivial': 'no se requiere acción específica.',
    'tolerable': 'no hace falta mejorar la acción preventiva, pero se consideran mejoras de bajo costo y se '
                 'comprueba periódicamente que los controles sigan siendo eficaces.',
    'moderado': 'reducir el riesgo con medidas e inversiones definidas, en un plazo determinado; si las '
                'consecuencias son extremadamente dañinas, precisar mejor la probabilidad.',
    'importante': 'no empezar el trabajo hasta reducir el riesgo; si el trabajo ya se hace, remediarlo en menos '
                  'tiempo que un riesgo moderado.',
    'intolerable': 'no empezar ni continuar el trabajo hasta reducir el riesgo; si no se puede reducir, prohibirlo.',
}


# ------------------------------------------------------------------------------------------ formato
def n(x, d=2):
    return ('%.*f' % (d, x)).replace('.', ',')


def miles(x, d=0):
    """Número con espacio como separador de miles (SI) y coma decimal: 174 140 o 9 459,0."""
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


def horas_txt(h):
    if h >= 1:
        return '%s h' % n(h, 2)
    if h * 60 >= 1:
        return '%s min' % n(h * 60, 2)
    return '%s s' % n(h * 3600, 2)


# ------------------------------------------------------------------------------------------ carga de fuego
def leer_material(texto):
    """'madera=4000' (tabla) o 'resina=200:25' (poder calorífico propio en MJ/kg)."""
    if '=' not in texto:
        raise ValueError('material «%s»: se escribe NOMBRE=kg o NOMBRE=kg:MJkg' % texto)
    nombre, valor = texto.split('=', 1)
    nombre = nombre.strip().lower()
    if ':' in valor:
        kg, pc = valor.split(':', 1)
        return nombre, float(kg), float(pc), 'dato propio'
    if nombre not in MATERIALES:
        raise ValueError('«%s» no está en la tabla (ver el comando materiales) o indicá NOMBRE=kg:MJkg' % nombre)
    return nombre, float(valor), MATERIALES[nombre][0], MATERIALES[nombre][2]


def tramo(qf):
    """Índice de fila: los tramos se escriben en enteros; un valor como 15,4 va al tramo siguiente (lado seguro)."""
    for i, tope in enumerate((15, 30, 60, 100)):
        if qf <= tope:
            return i
    return 4


def carga_fuego(materiales, S, riesgo=None, ventilacion='natural', actividad='industrial', sup_liquido=None,
                electrico=False):
    if S <= 0:
        raise ValueError('la superficie del sector tiene que ser mayor que 0')
    if not materiales:
        raise ValueError('falta al menos un --material')
    L = ['Sector de incendio: S = %s m²' % n(S, 2)]
    Q = 0.0
    for nombre, kg, pc, fuente in materiales:
        if kg < 0 or pc <= 0:
            raise ValueError('masa y poder calorífico tienen que ser positivos (%s)' % nombre)
        Q += kg * pc
        L.append('  %s: %s kg · %s MJ/kg = %s MJ (%s)' % (nombre, miles(kg, 0), n(pc, 2), miles(kg * pc), fuente))
    meq = Q / MADERA
    qf = meq / S
    i = tramo(qf)
    L += ['Calor total: Q = Σ(Pi·PCi) = %s MJ' % miles(Q),
          'Madera equivalente: Q/18,41 MJ/kg = %s kg (patrón del Dec. 351/79, Anexo VII, 1.2)' % miles(meq, 1),
          'Carga de fuego: Qf = Σ(Pi·PCi)/(18,41·S) = %s/(18,41·%s) = %s kg/m² → tramo «%s»'
          % (miles(Q), n(S, 2), n(qf, 2), TRAMOS[i])]
    nmat = math.ceil(S / 200 - 1e-9)
    r = {'Q': Q, 'meq': meq, 'qf': qf, 'tramo': i, 'nmat': nmat}
    if riesgo is not None:
        if riesgo not in RIESGOS:
            raise ValueError('riesgo: un entero de 1 a 7 (Anexo VII, 1.5)')
        if riesgo in NO_PERMITIDO[actividad]:
            L.append('AVISO: riesgo %d NO PERMITIDO en actividad %s (Anexo VII, cuadro 2.1).' % (riesgo, actividad))
        if riesgo <= 5:
            cuadro = F_NATURAL if ventilacion == 'natural' else F_MECANICA
            F = cuadro[riesgo][i]
            r.update({'F': F, 'A': POT_A[riesgo][i], 'B': POT_B[riesgo][i]})
            L.append('Riesgo %d (%s), ventilación %s: resistencia al fuego %s (cuadro %s del Anexo VII)*'
                     % (riesgo, RIESGOS[riesgo], ventilacion, F or 'sin valor en el cuadro',
                        '2.2.1' if ventilacion == 'natural' else '2.2.2'))
            if riesgo == 1:
                L.append('El riesgo 1 (explosivo) se considera solo como fuente de ignición: los cuadros no dan valores.')
            pa = r['A'] if r['A'] != 'caso' else 'a determinar en cada caso'
            pb = r['B'] if r['B'] != 'caso' else 'a determinar en cada caso'
            L.append('Potencial extintor mínimo: clase A %s (tabla 1); clase B %s (tabla 2, si puede haber fuego B)'
                     % (pa or 'sin valor en la tabla', pb or 'sin valor en la tabla'))
        else:
            L.append('Riesgo %d (%s): los cuadros y las tablas del Anexo VII no fijan valores.' % (riesgo, RIESGOS[riesgo]))
    else:
        L.append('Para la resistencia al fuego y el potencial extintor, indicar --riesgo (1 a 7) según la actividad predominante.')
    L.append('Matafuegos: como mínimo 1 cada 200 m² → ⌈%s/200⌉ = %d, con un recorrido máximo de 20 m hasta uno '
             'para fuego A y de 15 m para fuego B (Dec. 351/79, art. 176)' % (n(S, 2), nmat))
    if sup_liquido:
        if sup_liquido > 1:
            r['B_liq'] = math.ceil(sup_liquido / 0.1 - 1e-9)
            L.append('Líquidos inflamables con %s m² de superficie: 1 unidad B cada 0,1 m² → %d B en el área de mayor '
                     'riesgo (art. 177)' % (n(sup_liquido, 2), r['B_liq']))
        else:
            L.append('Superficie de líquido de hasta 1 m²: rige la tabla 2 (art. 177 se aplica a más de 1 m²).')
    if electrico:
        L.append('Hay equipos con tensión: los matafuegos tienen que ser aptos para fuego clase C (art. 178).')
    if riesgo is not None and riesgo <= 5:
        L.append('* El Boletín Oficial publicó los cuadros 2.2.1 y 2.2.2 sin rotular; se toma 2.2.1 = ventilación natural '
                 'y 2.2.2 = mecánica (verificar en la norma vigente).')
    L.append('Estudio orientativo: lo firma el profesional de higiene y seguridad del establecimiento.')
    return r, L


def cmd_materiales():
    print('Poder calorífico de la tabla embebida (MJ/kg). Riesgo: solo si el Dec. 351/79 (Anexo VII, 1.5) nombra el material.')
    for k in sorted(MATERIALES):
        pc, nom, fuente, rg = MATERIALES[k]
        print('  %-17s %7s  %-24s %s%s' % (k, n(pc, 2), nom, fuente, ('; riesgo %d' % rg) if rg else ''))
    print('Tabla 1.4 del Anexo I del RD 2267/2004 (BOE n.º 303, 17/12/2004), derogado desde el 10/05/2025 por el '
          'RD 164/2025: se usa solo como tabla de datos. Si la cátedra da otros valores, usar NOMBRE=kg:MJkg.')
    return 0


# ------------------------------------------------------------------------------------------ ruido
def nivel_tabla(L):
    """Nivel de la fila de tabla inmediata superior (82, 85, 88, ...), como la guía práctica N.º 2 de la SRT."""
    if L <= 82:
        return 82.0
    return 85.0 + 3.0 * math.ceil((L - 85.0) / 3.0 - 1e-9)


def t_permitido(L, criterio='formula'):
    """Horas permitidas por día con la regla de 85 dBA en 8 h e intercambio de 3 dB."""
    if criterio == 'tabla':
        L = nivel_tabla(L)
    return 8.0 / 2 ** ((L - 85.0) / 3.0)


def leer_exposicion(texto):
    """'94:2' = 2 h a 94 dBA; '88:90min' = 90 minutos a 88 dBA."""
    if ':' not in texto:
        raise ValueError('exposición «%s»: se escribe dBA:horas (por ejemplo 94:2 o 88:90min)' % texto)
    nivel, tiempo = texto.split(':', 1)
    tiempo = tiempo.strip().lower()
    horas = float(tiempo[:-3]) / 60 if tiempo.endswith('min') else float(tiempo.rstrip('h'))
    return float(nivel), horas


def ruido(exposiciones, criterio='formula', nrr=None, pico=None):
    if not exposiciones:
        raise ValueError('falta al menos un --exp dBA:horas')
    if criterio not in ('formula', 'tabla'):
        raise ValueError('criterio: formula o tabla')
    L = ['Criterio: 85 dBA para 8 h, intercambio de 3 dB, dosis ≤ 1; se cuentan las exposiciones de 80 dBA o más '
         '(Res. MTEySS 295/03, Anexo V)',
         'Tiempo permitido: T = 8 h/2^((L − 85)/3)%s' % (
             '' if criterio == 'formula' else ', con L llevado a la fila de tabla inmediata superior (guía práctica N.º 2 de la SRT)')]
    D, energia, Te = 0.0, 0.0, 0.0
    for nivel, h in exposiciones:
        if h <= 0:
            raise ValueError('el tiempo de exposición tiene que ser mayor que 0')
        if criterio == 'tabla' and nivel > 139:
            raise ValueError('%s dBA está por encima de la última fila de la tabla (139 dBA)' % n(nivel, 1))
        Te += h
        energia += h * 10 ** (nivel / 10)
        if nivel < 80:
            L.append('  %s dBA durante %s: no se cuenta en la dosis (menos de 80 dBA)' % (n(nivel, 1), horas_txt(h)))
            continue
        T = t_permitido(nivel, criterio)
        D += h / T
        extra = ' (fila de %s dBA)' % n(nivel_tabla(nivel), 0) if criterio == 'tabla' and nivel_tabla(nivel) != nivel else ''
        L.append('  %s dBA durante %s: T = %s%s → C/T = %s' % (n(nivel, 1), horas_txt(h), horas_txt(T), extra, n(h / T, 4)))
    Leq = 10 * math.log10(energia / Te)
    L8 = 10 * math.log10(energia / 8)
    Tp = t_permitido(Leq, 'formula')
    r = {'D': D, 'Leq': Leq, 'L8': L8, 'Te': Te, 'Tp': Tp}
    L += ['Dosis: D = Σ(Ci/Ti) = %s = %s %% → %s' % (n(D, 4), n(100 * D, 1),
                                                    'VERIFICA (D ≤ 1)' if D <= 1 + 1e-9 else 'SUPERA EL LÍMITE (D > 1)'),
          'Nivel continuo equivalente: LAeq,Te = 10·log(Σ ti·10^(Li/10)/Te) = %s dBA en Te = %s' % (n(Leq, 1), horas_txt(Te)),
          'Referido a 8 h: LAeq,8h = 10·log(Σ ti·10^(Li/10)/8 h) = %s dBA (≈ 85 + 10·log D = %s dBA)'
          % (n(L8, 1), n(85 + 10 * math.log10(D), 1) if D > 0 else '—'),
          'Tiempo permitido a %s dBA: %s por día' % (n(Leq, 1), horas_txt(Tp))]
    if nrr is not None:
        aten = nrr - 7
        D2 = sum(h / t_permitido(nv - aten, criterio) for nv, h in exposiciones if nv - aten >= 80)
        r.update({'L8_prot': L8 - aten, 'D_prot': D2})
        L += ['Con protector de NRR %s dB (medición en dBA): atenuación estimada NRR − 7 = %s dB '
              '(OSHA 29 CFR 1910.95, apéndice B)' % (n(nrr, 0), n(aten, 0)),
              '  LAeq,8h bajo el protector ≈ %s dBA; dosis ≈ %s %%%s → %s' % (
                  n(L8 - aten, 1), n(100 * D2, 1), ' (ninguna exposición llega a 80 dBA)' if D2 == 0 else '',
                  'verifica' if D2 <= 1 + 1e-9 else 'NO verifica'),
              '  El valor real depende de la colocación y del uso todo el turno: el EPP es la última barrera.']
    if pico is not None:
        r['pico_ok'] = pico <= 140
        L.append('Nivel pico: %s dBC %s 140 dBC (Res. 295/03: no se permite sin protector por encima de 140 dBC)'
                 % (n(pico, 1), '≤' if pico <= 140 else '>'))
    L.append('La medición válida es la del protocolo de la Res. SRT 85/12, con sonómetro integrador o dosímetro.')
    return r, L


# ------------------------------------------------------------------------------------------ estres termico
def tgbh(tbh, tg, tbs=None, sol=False, ropa='verano', carga='moderado', regimen=100):
    if ropa not in ROPA:
        raise ValueError('ropa: %s' % ', '.join(ROPA))
    if carga not in TGBH_LIM[100]:
        raise ValueError('carga: ligero, moderado o pesado (para muy pesado, la Res. 295/03 pide un análisis detallado)')
    if regimen not in TGBH_LIM:
        raise ValueError('régimen: 100, 75, 50 o 25 (%% de trabajo en cada hora)')
    if sol:
        if tbs is None:
            raise ValueError('con --sol hace falta --tbs (temperatura de bulbo seco)')
        t = 0.7 * tbh + 0.2 * tg + 0.1 * tbs
        L = ['TGBH con carga solar = 0,7·TBH + 0,2·TG + 0,1·TBS = 0,7·%s + 0,2·%s + 0,1·%s = %s °C'
             % (n(tbh, 1), n(tg, 1), n(tbs, 1), n(t, 2))]
    else:
        t = 0.7 * tbh + 0.3 * tg
        L = ['TGBH sin carga solar = 0,7·TBH + 0,3·TG = 0,7·%s + 0,3·%s = %s °C' % (n(tbh, 1), n(tg, 1), n(t, 2))]
    tc = t + ROPA[ropa]
    lim = TGBH_LIM[regimen][carga]
    ok = tc <= lim + 1e-9
    L += ['Corrección por ropa (%s): + %s °C → TGBH = %s °C' % (ropa, n(ROPA[ropa], 1), n(tc, 2)),
          'Límite para trabajo %s con %d %% de trabajo por hora: %s °C → %s' % (carga, regimen, n(lim, 1),
                                                                             'VERIFICA' if ok else 'NO VERIFICA')]
    sirven = [g for g in (100, 75, 50, 25) if tc <= TGBH_LIM[g][carga] + 1e-9]
    L.append('Regímenes trabajo-descanso que verifican con ese TGBH: %s'
             % (', '.join('%d %%' % g for g in sirven) if sirven else 'ninguno: bajar la carga térmica o la exigencia'))
    L.append('Fuente: Res. MTEySS 295/03 (estrés térmico); la medición sigue el protocolo vigente de la SRT.')
    return {'t': t, 'tc': tc, 'lim': lim, 'ok': ok, 'sirven': sirven}, L


# ------------------------------------------------------------------------------------------ ventilacion
def ventilacion(personas, volumen, actividad='sedentaria'):
    if actividad not in VENTILACION:
        raise ValueError('actividad: sedentaria o moderada')
    if personas <= 0 or volumen <= 0:
        raise ValueError('personas y volumen tienen que ser positivos')
    cub = volumen / personas
    filas = VENTILACION[actividad]
    L = ['Cubaje por persona: V/N = %s/%d = %s m³' % (n(volumen, 1), personas, n(cub, 2))]
    if cub < filas[0][0]:
        fila = filas[0]
        L.append('AVISO: menos de 3 m³ por persona, fuera de la tabla del art. 66: se usa la primera fila y conviene revisar el local.')
    else:
        fila = [f for f in filas if f[0] <= cub + 1e-9][-1]
    q = fila[1]
    Q = q * personas
    L += ['Fila del art. 66 (actividad %s): %d m³ por persona → %d m³/h por persona (la fila de cubaje inmediata '
          'inferior, del lado seguro)' % (actividad, fila[0], q),
          'Caudal mínimo: Q = N·q = %d·%d = %d m³/h → %s renovaciones por hora' % (personas, q, Q, n(Q / volumen, 2)),
          'Fuente: Dec. 351/79, art. 66; con contaminantes, el caudal sale de los valores de la Res. 295/03.']
    return {'cub': cub, 'q': q, 'Q': Q, 'ren': Q / volumen}, L


# ------------------------------------------------------------------------------------------ distancia
def distancia(kv):
    if kv < 0:
        raise ValueError('la tensión no puede ser negativa')
    for tope, d in DISTANCIAS:
        if kv <= tope + 1e-12:
            break
    else:
        raise ValueError('la tabla del Anexo VI llega a 500 kV')
    if d is None:
        L = ['Hasta 50 V: la tabla no exige distancia mínima (muy baja tensión, Anexo VI, 1.1.1).']
    else:
        L = ['Distancia mínima de seguridad para %s kV: %s m (Dec. 351/79, Anexo VI, 1.1.5)' % (n(kv, 3).rstrip('0').rstrip(','), n(d, 2))]
        if 1 < kv <= 33:
            L.append('Nota 1 de la tabla: puede bajar a 0,60 m con pantallas aislantes adecuadas sobre las partes con tensión.')
        if kv > 33:
            L.append('Nota 2 de la tabla: para trabajos a distancia; no se aplica a trabajos a potencial.')
    L.append('Antes de trabajar sin tensión: consignar (Anexo VI, 1.1.4): corte visible, bloqueo, verificación de '
             'ausencia de tensión, puesta a tierra y en cortocircuito, señalización y delimitación.')
    return {'d': d}, L


# ------------------------------------------------------------------------------------------ riesgo
def riesgo(p, s):
    p, s = str(p).lower(), str(s).lower()
    alias_p = {'1': 'baja', '2': 'media', '3': 'alta'}
    alias_s = {'1': 'ld', '2': 'd', '3': 'ed'}
    p, s = alias_p.get(p, p), alias_s.get(s, s)
    if p not in PROB or s not in CONS:
        raise ValueError('probabilidad: baja, media o alta (1 a 3); severidad: ld, d o ed (1 a 3)')
    nivel = MATRIZ[PROB[p]][CONS[s]]
    L = ['Probabilidad %s × consecuencias %s → riesgo %s' % (p, NOMBRE_CONS[CONS[s]], nivel.upper()),
         'Acción: %s' % ACCION[nivel],
         'Controles en este orden: eliminar, sustituir, ingeniería (resguardos, aislación), administrativos '
         '(procedimientos, señalización, capacitación) y, al final, EPP.',
         'Escala: matriz 3 × 3 del INSHT, «Evaluación de riesgos laborales» (verificar en la fuente); la empresa o la '
         'cátedra pueden usar otra.']
    return {'nivel': nivel}, L


# ------------------------------------------------------------------------------------------ demo
def cerca(x, y, tol):
    return abs(x - y) <= tol


def cmd_demo():
    ok = []
    ok.append(('18,41 MJ/kg equivalen a 4400 kcal/kg (4400·4,184 kJ = %s MJ)' % n(4400 * KCAL / 1000, 4),
               cerca(4400 * KCAL / 1000, MADERA, 0.005)))
    # Ejemplo del SKILL.md: depósito de 15 m x 30 m
    mats = [leer_material('madera=4000'), leer_material('carton=3000'), leer_material('polietileno=1200')]
    r, _ = carga_fuego(mats, 15 * 30, riesgo=3)
    Q = 4000 * 18.41 + 3000 * 16.7 + 1200 * 42
    ok.append(('depósito de 450 m²: Q = %s MJ, Qf = %s kg/m² (a mano: Q/(18,41·450))' % (miles(r['Q']), n(r['qf'], 2)),
               cerca(r['Q'], Q, 1e-6) and cerca(r['qf'], Q / (18.41 * 450), 1e-9) and cerca(r['qf'], 21.02, 0.005)))
    ok.append(('tramo 16 a 30 kg/m², riesgo 3: F 60, 2 A, 6 B y 3 matafuegos (⌈450/200⌉)',
               r['tramo'] == 1 and r['F'] == 'F 60' and r['A'] == '2 A' and r['B'] == '6 B' and r['nmat'] == 3))
    r2, _ = carga_fuego(mats, 15 * 30, riesgo=3, ventilacion='mecanica', sup_liquido=2.5)
    ok.append(('con ventilación mecánica F 90 y 2,5 m² de líquido → 25 B (art. 177)', r2['F'] == 'F 90' and r2['B_liq'] == 25))
    ok.append(('tramos: 15 → hasta 15; 15,4 → 16 a 30; 100,5 → más de 100', tramo(15) == 0 and tramo(15.4) == 1 and tramo(100.5) == 4))
    # Ruido: 2 h a 94 dBA + 3 h a 88 dBA + 3 h a 82 dBA
    r, _ = ruido([(94, 2), (88, 3), (82, 3)])
    D = 2 / 1 + 3 / 4 + 3 / 16
    L8 = 10 * math.log10((2 * 10 ** 9.4 + 3 * 10 ** 8.8 + 3 * 10 ** 8.2) / 8)
    ok.append(('ruido: D = %s (2/1 + 3/4 + 3/16 = 2,9375) y LAeq,8h = %s dBA' % (n(r['D'], 4), n(r['L8'], 2)),
               cerca(r['D'], D, 1e-9) and cerca(r['L8'], L8, 1e-9) and cerca(r['L8'], 89.66, 0.005)))
    ok.append(('tiempos de la regla de 3 dB: 82 → 16 h, 88 → 4 h, 91 → 2 h, 94 → 1 h (guía de la SRT)',
               all(cerca(t_permitido(a), b, 1e-9) for a, b in ((82, 16), (88, 4), (91, 2), (94, 1)))))
    ok.append(('la dosis por 2^ y por energía difieren menos de 1 %% (%s y %s)' % (n(r['D'], 4), n(10 ** ((r['L8'] - 85) / 10), 4)),
               abs(10 ** ((r['L8'] - 85) / 10) / r['D'] - 1) < 0.01))
    ok.append(('tiempo permitido a %s dBA: %s h (8/2^((L − 85)/3))' % (n(r['Leq'], 2), n(r['Tp'], 2)),
               cerca(r['Tp'], 8 / 2 ** ((r['Leq'] - 85) / 3), 1e-12) and cerca(r['Tp'], 2.72, 0.01)))
    # Guía práctica N.º 2 de la SRT, ejemplos 1 y 2 (criterio de tabla)
    rg, _ = ruido([(88, 1), (91, 1), (82, 4), (87, 2)], criterio='tabla')
    ok.append(('guía SRT, ejemplo 1 con la tabla: 1/4 + 1/2 + 4/16 + 2/4 = %s (87 dBA → fila de 88)' % n(rg['D'], 2),
               cerca(rg['D'], 1.5, 1e-9)))
    ok.append(('guía SRT, ejemplo 2: 90 dBA → fila de 91 dBA → 2 h', cerca(t_permitido(90, 'tabla'), 2, 1e-9)))
    rp, _ = ruido([(94, 2), (88, 3), (82, 3)], nrr=25)
    ok.append(('protector NRR 25: LAeq,8h − (25 − 7) = %s dBA' % n(rp['L8_prot'], 2), cerca(rp['L8_prot'], L8 - 18, 1e-9)))
    # Estrés térmico
    rt, _ = tgbh(24, 32, carga='moderado', regimen=100)
    ok.append(('TGBH interior: 0,7·24 + 0,3·32 = %s °C ≤ 27,5 °C (moderado, 100 %%)' % n(rt['t'], 1),
               cerca(rt['t'], 26.4, 1e-9) and rt['ok']))
    rt2, _ = tgbh(24, 32, ropa='tela', carga='moderado', regimen=100)
    ok.append(('con buzo de tela + 3,5 °C = %s °C: no verifica al 100 %%; sí con 25 %% de trabajo (31 °C)' % n(rt2['tc'], 1),
               cerca(rt2['tc'], 29.9, 1e-9) and not rt2['ok'] and rt2['sirven'] == [25]))
    rs, _ = tgbh(25, 40, tbs=33, sol=True)
    ok.append(('TGBH con sol: 0,7·25 + 0,2·40 + 0,1·33 = %s °C' % n(rs['t'], 1), cerca(rs['t'], 28.8, 1e-9)))
    # Ventilación
    rv, _ = ventilacion(6, 60, 'sedentaria')
    ok.append(('ventilación: 6 personas en 60 m³ → 10 m³ c/u → fila 9 → 21 m³/h·persona = %d m³/h' % rv['Q'],
               rv['q'] == 21 and rv['Q'] == 126 and cerca(rv['ren'], 2.1, 1e-9)))
    # Distancias
    ok.append(('distancias del Anexo VI: 0,38 kV y 13,2 kV → 0,80 m; 132 kV → 1,50 m; 500 kV → 3,60 m',
               distancia(0.38)[0]['d'] == 0.80 and distancia(13.2)[0]['d'] == 0.80 and distancia(132)[0]['d'] == 1.50
               and distancia(500)[0]['d'] == 3.60 and distancia(0.024)[0]['d'] is None))
    # Matriz de riesgos (INSHT)
    esperado = {('baja', 'ld'): 'trivial', ('baja', 'd'): 'tolerable', ('baja', 'ed'): 'moderado',
                ('media', 'ld'): 'tolerable', ('media', 'd'): 'moderado', ('media', 'ed'): 'importante',
                ('alta', 'ld'): 'moderado', ('alta', 'd'): 'importante', ('alta', 'ed'): 'intolerable'}
    ok.append(('matriz 3 × 3: las 9 celdas (media × dañino = moderado; alta × extremadamente dañino = intolerable)',
               all(riesgo(p, s)[0]['nivel'] == v for (p, s), v in esperado.items())))
    for nombre, bien in ok:
        print('  %s %s' % ('ok ' if bien else 'MAL', nombre))
    todo = all(b for _, b in ok)
    print('DEMO %s' % ('OK' if todo else 'FALLO'))
    return 0 if todo else 1


# ------------------------------------------------------------------------------------------ principal
class Formato(argparse.RawDescriptionHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        return super().add_usage(usage, actions, groups, 'uso: ' if prefix is None else prefix)


def nuevo(sp, nombre, ayuda):
    p = sp.add_parser(nombre, help=ayuda, description=ayuda, formatter_class=Formato, add_help=False)
    p._optionals.title = 'opciones'
    p.add_argument('-h', '--help', action='help', help='mostrar esta ayuda y salir')
    return p


def construir_parser():
    ap = argparse.ArgumentParser(prog='seguridad.py', description=__doc__, formatter_class=Formato, add_help=False)
    ap._optionals.title = 'opciones'
    ap._positionals.title = 'comandos'
    ap.add_argument('-h', '--help', action='help', help='mostrar esta ayuda y salir')
    sp = ap.add_subparsers(dest='cmd', metavar='COMANDO')
    sp.required = True
    p = nuevo(sp, 'carga-fuego', 'carga de fuego, resistencia al fuego, potencial extintor y cantidad de matafuegos')
    p.add_argument('--sup', type=float, help='superficie del sector de incendio [m²]')
    p.add_argument('--largo', type=float, help='largo del sector [m] (con --ancho, en lugar de --sup)')
    p.add_argument('--ancho', type=float, help='ancho del sector [m]')
    p.add_argument('--material', action='append', default=[], metavar='NOMBRE=kg[:MJkg]',
                   help='material y masa; repetir por cada material (nombres: comando materiales)')
    p.add_argument('--riesgo', type=int, choices=range(1, 8), metavar='1-7', help='riesgo del sector (Anexo VII, 1.5)')
    p.add_argument('--ventilacion', default='natural', choices=['natural', 'mecanica'], help='ventilación del local')
    p.add_argument('--actividad', default='industrial', choices=['industrial', 'residencial', 'espectaculos'],
                   help='actividad predominante (cuadro 2.1): industrial incluye comercial y depósito')
    p.add_argument('--sup-liquido', type=float, help='superficie de líquido inflamable expuesto [m²] (art. 177)')
    p.add_argument('--electrico', action='store_true', help='hay equipos con tensión (fuego clase C, art. 178)')
    nuevo(sp, 'materiales', 'tabla de poderes caloríficos embebida, con su fuente')
    p = nuevo(sp, 'ruido', 'dosis, LAeq y tiempo permitido (85 dBA, 3 dB)')
    p.add_argument('--exp', action='append', default=[], metavar='dBA:horas',
                   help='nivel y duración de cada exposición de la jornada (94:2 o 88:90min); repetir')
    p.add_argument('--criterio', default='formula', choices=['formula', 'tabla'],
                   help='formula: regla de 3 dB continua; tabla: fila inmediata superior, como la guía de la SRT')
    p.add_argument('--nrr', type=float, help='NRR del protector auditivo [dB] (medición en dBA)')
    p.add_argument('--pico', type=float, help='nivel pico medido [dBC], contra 140 dBC')
    p = nuevo(sp, 'tgbh', 'índice TGBH y valor límite de estrés térmico')
    p.add_argument('--tbh', type=float, required=True, help='temperatura de bulbo húmedo natural [°C]')
    p.add_argument('--tg', type=float, required=True, help='temperatura de globo [°C]')
    p.add_argument('--tbs', type=float, help='temperatura de bulbo seco [°C] (solo con --sol)')
    p.add_argument('--sol', action='store_true', help='exterior con carga solar')
    p.add_argument('--ropa', default='verano', choices=sorted(ROPA), help='verano: 0 °C; tela: + 3,5 °C; doble: + 5 °C')
    p.add_argument('--carga', default='moderado', choices=['ligero', 'moderado', 'pesado'], help='carga de trabajo')
    p.add_argument('--regimen', type=int, default=100, choices=[100, 75, 50, 25], help='%% de trabajo en cada hora')
    p = nuevo(sp, 'ventilacion', 'caudal mínimo de aire por persona (Dec. 351/79, art. 66)')
    p.add_argument('--personas', type=int, required=True, help='cantidad de personas en el local')
    p.add_argument('--volumen', type=float, required=True, help='volumen del local [m³]')
    p.add_argument('--actividad', default='sedentaria', choices=['sedentaria', 'moderada'], help='tipo de actividad')
    p = nuevo(sp, 'distancia', 'distancia mínima de seguridad a partes con tensión (Anexo VI)')
    p.add_argument('--kv', type=float, required=True, help='tensión nominal [kV]')
    p = nuevo(sp, 'riesgo', 'nivel de riesgo con la matriz probabilidad × consecuencias')
    p.add_argument('--p', required=True, help='probabilidad: baja, media o alta (o 1, 2, 3)')
    p.add_argument('--s', required=True, help='consecuencias: ld (ligeramente dañino), d (dañino) o ed (extremadamente dañino)')
    nuevo(sp, 'demo', 'reproduce los ejemplos del SKILL.md y termina en DEMO OK')
    return ap


def main(argv=None):
    a = construir_parser().parse_args(argv)
    try:
        if a.cmd == 'demo':
            return cmd_demo()
        if a.cmd == 'materiales':
            return cmd_materiales()
        if a.cmd == 'carga-fuego':
            if a.sup is None:
                if a.largo is None or a.ancho is None:
                    raise ValueError('indicá --sup o --largo y --ancho del sector de incendio')
                a.sup = a.largo * a.ancho
            _, L = carga_fuego([leer_material(m) for m in a.material], a.sup, a.riesgo, a.ventilacion, a.actividad,
                               a.sup_liquido, a.electrico)
        elif a.cmd == 'ruido':
            _, L = ruido([leer_exposicion(e) for e in a.exp], a.criterio, a.nrr, a.pico)
        elif a.cmd == 'tgbh':
            _, L = tgbh(a.tbh, a.tg, a.tbs, a.sol, a.ropa, a.carga, a.regimen)
        elif a.cmd == 'ventilacion':
            _, L = ventilacion(a.personas, a.volumen, a.actividad)
        elif a.cmd == 'distancia':
            _, L = distancia(a.kv)
        else:
            _, L = riesgo(a.p, a.s)
    except ValueError as ex:
        print('seguridad.py: %s' % ex, file=sys.stderr)
        return 2
    print('\n'.join(L))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
