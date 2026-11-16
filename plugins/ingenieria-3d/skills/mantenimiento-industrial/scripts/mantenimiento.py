#!/usr/bin/env python3
"""mantenimiento.py - indicadores y técnicas de mantenimiento industrial.

Solo biblioteca estándar (Python 3.9 o más nuevo). Los números se escriben con coma o con punto
decimal (0,82 o 0.82); las salidas salen con coma decimal. Las tablas (Pareto, AMFE) salen en
Markdown, listas para pegar en un informe.

Subcomandos:
  indicadores    MTBF, MTTR, MDT, tasa de fallas y disponibilidad inherente y operativa
  confiabilidad  R(t) = e^(-t/MTBF) con tasa de fallas constante; sistemas en serie y en paralelo
  oee            OEE = disponibilidad x rendimiento x calidad, con las pérdidas en horas
  costo          costo directo e indirecto (parada) del mantenimiento, por unidad y sobre el valor de reposición
  pareto         Pareto de fallas desde un registro CSV o JSON, o con --item causa=valor
  amfe           AMFE: NPR = S x O x D desde un CSV o JSON, ordenado, con el NPR después de las acciones
  relubricacion  método SKF: factor de velocidad n·dm, límite, ajustes del intervalo y gramos de grasa
  vibracion      zona de severidad ISO 20816-3 (grupos 1 y 2), ALARMA y DISPARO; frecuencias de rodamiento
  alineacion     desalineación medida contra la guía de SKF (TKSA 20)
  balanceo       desbalance residual admisible para un grado G (ISO 21940-11)
  termografia    acción sugerida por la diferencia de temperatura (ANSI/NETA MTS, tabla 100.18)
  demo           ejemplo resuelto de SKILL.md, verificado (sale con código 1 si algo no coincide)

Ejemplos (los del demo):
  python mantenimiento.py indicadores --operacion 306 --registro ../plantilla/registro-fallas-ejemplo.csv
  python mantenimiento.py oee --planificado 330 --paradas 24 --tasa 100 --total 1562000 --rechazos 31400
  python mantenimiento.py confiabilidad --mtbf 34 --t 8 --objetivo 0,9
  python mantenimiento.py pareto ../plantilla/registro-fallas-ejemplo.csv
  python mantenimiento.py amfe ../plantilla/amfe-ejemplo.csv
  python mantenimiento.py relubricacion --d 340 --D 420 --B 38 --rpm 500 --tipo rigido-bolas --tf 10000
  python mantenimiento.py vibracion --v 3,2 --altura 160 --soporte rigido --base 1,1

Cada subcomando tiene su ayuda: python mantenimiento.py amfe --help
"""
import argparse
import csv
import io
import json
import math
import sys
import unicodedata
from pathlib import Path

# Mensajes de argparse en castellano (si una versión de Python cambia un texto, queda en inglés).
_TRADUCCION = {
    'usage: ': 'uso: ',
    'positional arguments': 'argumentos posicionales',
    'optional arguments': 'opciones',
    'options': 'opciones',
    'show this help message and exit': 'muestra esta ayuda y sale',
    'the following arguments are required: %s': 'faltan estos argumentos: %s',
    'unrecognized arguments: %s': 'argumentos no reconocidos: %s',
    'invalid choice: %(value)r (choose from %(choices)s)': 'opción no válida: %(value)r (elegir entre %(choices)s)',
    'argument %(argument_name)s: %(message)s': 'argumento %(argument_name)s: %(message)s',
    'expected one argument': 'falta el valor',
    'expected at least one argument': 'falta al menos un valor',
    'invalid %(type)s value: %(value)r': 'valor no válido: %(value)r',
    'ambiguous option: %(option)s could match %(matches)s': 'opción ambigua: %(option)s puede ser %(matches)s',
    'not allowed with argument %s': 'no se puede usar junto con %s',
    'one of the arguments %s is required': 'hace falta uno de estos argumentos: %s',
}
argparse._ = lambda texto: _TRADUCCION.get(texto, texto)

# ------------------------------------------------------------------------------------------ datos con fuente
# OEE de clase mundial (Nakajima, Introduction to TPM, 1988), según oee.com/world-class-oee
OEE_CLASE_MUNDIAL = {'A': 0.90, 'P': 0.95, 'Q': 0.99, 'OEE': 0.85}

# SKF, Rolling bearings, PUB BU/P1 17000/1, sección de lubricación, tabla 1: factor del rodamiento bf y
# límite recomendado de n·dm [mm/min] para C/P >= 15, C/P ≈ 8 y C/P ≈ 4 (None: no corresponde)
SKF_BF = {
    'rigido-bolas': ('rígido de bolas', 1.0, (500000, 400000, 300000)),
    'contacto-angular': ('de bolas con contacto angular', 1.0, (500000, 400000, 300000)),
    'oscilante-bolas': ('de bolas a rótula', 1.0, (500000, 400000, 300000)),
    'cil-libre': ('de rodillos cilíndricos, lado libre', 1.5, (450000, 300000, 150000)),
    'cil-fijo-alternante': ('de rodillos cilíndricos, lado fijo, carga axial chica o alternante', 2.0, (300000, 200000, 100000)),
    'cil-fijo-constante': ('de rodillos cilíndricos, lado fijo, carga axial chica constante', 4.0, (200000, 120000, 60000)),
    'cil-lleno': ('de rodillos cilíndricos lleno, sin jaula', 4.0, (None, None, 20000)),
    'agujas': ('de agujas con jaula', 3.0, (350000, 200000, 100000)),
    'conicos': ('de rodillos cónicos', 2.0, (350000, 300000, 200000)),
    'rotula-a': ('de rodillos a rótula, Fa/Fr ≤ e, dm ≤ 800 mm, series 213, 222, 238 y 239', 2.0, (350000, 200000, 100000)),
    'rotula-b': ('de rodillos a rótula, Fa/Fr ≤ e, dm ≤ 800 mm, series 223, 230, 231, 232, 240, 248 y 249', 2.0, (250000, 150000, 80000)),
    'rotula-c': ('de rodillos a rótula, Fa/Fr ≤ e, dm ≤ 800 mm, serie 241', 2.0, (150000, 80000, 50000)),
    'rotula-a-grande': ('de rodillos a rótula, Fa/Fr ≤ e, dm > 800 mm, series 238 y 239', 2.0, (230000, 130000, 65000)),
    'rotula-b-grande': ('de rodillos a rótula, Fa/Fr ≤ e, dm > 800 mm, series 230, 231, 232, 240, 248 y 249', 2.0, (170000, 100000, 50000)),
    'rotula-c-grande': ('de rodillos a rótula, Fa/Fr ≤ e, dm > 800 mm, serie 241', 2.0, (100000, 50000, 30000)),
    'rotula-fa-alta': ('de rodillos a rótula, Fa/Fr > e, todas las series', 6.0, (150000, 50000, 30000)),
    'carb': ('toroidal CARB con jaula', 2.0, (350000, 200000, 100000)),
    'carb-lleno': ('toroidal CARB lleno, sin jaula', 4.0, (None, None, 20000)),
    'axial-bolas': ('axial de bolas', 2.0, (200000, 150000, 100000)),
    'axial-cil': ('axial de rodillos cilíndricos', 10.0, (100000, 60000, 30000)),
    'axial-agujas': ('axial de agujas', 10.0, (100000, 60000, 30000)),
    'axial-rotula': ('axial de rodillos a rótula, con la arandela del eje girando', 4.0, (200000, 120000, 60000)),
}
SIN_EXTENSION = {'cil-lleno', 'carb-lleno', 'axial-bolas', 'axial-cil', 'axial-agujas', 'axial-rotula'}

# ISO 20816-3:2022, anexo A, tablas A.1 (grupo 1) y A.2 (grupo 2): límites de zona A/B, B/C y C/D en
# velocidad eficaz de banda ancha [mm/s], 10 Hz a 1000 Hz (2 Hz a 1000 Hz si la máquina gira a 600 r/min o menos)
ZONAS_ISO20816_3 = {
    (1, 'rigido'): (2.3, 4.5, 7.1),
    (1, 'flexible'): (3.5, 7.1, 11.0),
    (2, 'rigido'): (1.4, 2.8, 4.5),
    (2, 'flexible'): (2.3, 4.5, 7.1),
}
ZONA_TEXTO = {
    'A': 'la de las máquinas recién puestas en servicio',
    'B': 'aceptable para funcionar sin restricciones por largo tiempo',
    'C': 'insatisfactoria para funcionar en forma continua por largo tiempo: se puede seguir un tiempo limitado, '
         'hasta que haya oportunidad de corregir',
    'D': 'lo bastante severa como para dañar la máquina',
}

# SKF TKSA 20, guía rápida MP5370E (2013), anexo 3: desalineación máxima aceptable
# (rpm hasta, desplazamiento paralelo [mm], error angular [mm/100 mm])
SKF_ALINEACION = [(1000, 0.13, 0.10), (2000, 0.10, 0.08), (3000, 0.07, 0.07), (4000, 0.05, 0.06), (6000, 0.03, 0.05)]

# ANSI/NETA MTS-2007, tabla 100.18 (nota de aplicación de Fluke 3358415B, 2010): acciones por ΔT [°C]
NETA_ACCIONES = {
    4: 'posible deficiencia: investigar',
    3: 'deficiencia probable: reparar cuando se pueda',
    2: 'vigilar hasta poder corregir',
    1: 'discrepancia mayor: reparar de inmediato',
}


# ------------------------------------------------------------------------------------------ utilidades
def num(texto):
    """'0,82' o '0.82' a float (tipo para argparse)."""
    try:
        return float(str(texto).strip().replace(',', '.'))
    except ValueError:
        raise argparse.ArgumentTypeError('no es un número: %r' % texto)


def fraccion(x):
    """90 → 0,90; 0,9 → 0,9 (porcentajes o fracciones)."""
    return x / 100.0 if x > 1.0 else x


def n(x, d=2):
    """Coma decimal y espacio de miles (si la parte entera tiene más de 4 cifras): 1 530 600,00."""
    s = '%.*f' % (d, x)
    signo = '-' if s.startswith('-') else ''
    ent, _, dec = s.lstrip('-').partition('.')
    if len(ent) > 4:
        grupos = []
        while len(ent) > 3:
            grupos.insert(0, ent[-3:])
            ent = ent[:-3]
        grupos.insert(0, ent)
        ent = ' '.join(grupos)
    return signo + ent + (',' + dec if dec else '')


def pct(x, d=1):
    return n(100.0 * x, d) + ' %'


def sin_tildes(texto):
    t = unicodedata.normalize('NFKD', str(texto))
    return ''.join(c for c in t if not unicodedata.combining(c)).lower().strip()


def leer_filas(ruta=None, texto=None, json_=False):
    """Filas (lista de dict con claves en minúsculas y sin tildes) de un CSV (separado por ; , o tab) o JSON."""
    if texto is None:
        p = Path(ruta)
        if not p.is_file():
            raise ValueError('no existe el archivo %s' % ruta)
        texto = p.read_text(encoding='utf-8-sig')
        json_ = p.suffix.lower() == '.json'
    if json_:
        datos = json.loads(texto)
        if isinstance(datos, dict):
            datos = datos.get('filas', [])
        if not isinstance(datos, list) or not all(isinstance(f, dict) for f in datos):
            raise ValueError('el JSON tiene que ser una lista de objetos (o {"filas": [...]})')
        filas = datos
    else:
        primera = texto.splitlines()[0] if texto.strip() else ''
        sep = ';' if ';' in primera else ('\t' if '\t' in primera else ',')
        filas = list(csv.DictReader(io.StringIO(texto), delimiter=sep))
    limpias = []
    for f in filas:
        g = {sin_tildes(k): ('' if v is None else str(v).strip()) for k, v in f.items() if k is not None}
        if any(g.values()):
            limpias.append(g)
    if not limpias:
        raise ValueError('el archivo no tiene filas con datos')
    return limpias


def valor(fila, *claves, defecto=None):
    for c in claves:
        if c in fila and fila[c] != '':
            return fila[c]
    return defecto


# ------------------------------------------------------------------------------------------ indicadores
def leer_registro(ruta=None, texto=None):
    """Registro de fallas: una fila por falla, columnas reparacion_h y espera_h (opcional)."""
    filas = leer_filas(ruta, texto)
    rep = esp = 0.0
    for i, f in enumerate(filas, 1):
        r = valor(f, 'reparacion_h', 'reparacion', 'ttr_h')
        if r is None:
            raise ValueError('fila %d del registro sin reparacion_h' % i)
        rep += num(r)
        esp += num(valor(f, 'espera_h', 'espera', defecto='0'))
    return len(filas), rep, esp, filas


def indicadores(operacion, fallas, reparacion, espera=0.0, preventivos=0, t_preventivo=0.0):
    if operacion <= 0 or fallas < 1:
        raise ValueError('hacen falta horas de funcionamiento > 0 y al menos una falla')
    if preventivos and t_preventivo <= 0:
        raise ValueError('con --preventivos va también --t-preventivo (horas totales)')
    mtbf = operacion / fallas
    mttr = reparacion / fallas
    ai = mtbf / (mtbf + mttr)
    intervenciones = fallas + preventivos
    parada = reparacion + espera + t_preventivo
    mtbm = operacion / intervenciones
    mdt = parada / intervenciones
    ao = mtbm / (mtbm + mdt)
    r = {'MTBF': mtbf, 'MTTR': mttr, 'lambda': 1 / mtbf, 'Ai': ai, 'MTBM': mtbm, 'MDT': mdt, 'Ao': ao,
         'Ao_tiempos': operacion / (operacion + parada)}
    L = ['Datos: %s h de funcionamiento, %d fallas, %s h de reparación activa, %s h de espera (repuestos, personal, permisos)'
         % (n(operacion, 1), fallas, n(reparacion, 2), n(espera, 2))
         + (', %d preventivos con %s h' % (preventivos, n(t_preventivo, 2)) if preventivos else ''),
         'MTBF = tiempo de funcionamiento / fallas = %s/%d = %s h' % (n(operacion, 1), fallas, n(mtbf, 2)),
         'MTTR = reparación activa / fallas = %s/%d = %s h' % (n(reparacion, 2), fallas, n(mttr, 2)),
         'Tasa de fallas: λ = 1/MTBF = %s fallas/h' % n(r['lambda'], 5),
         'Disponibilidad inherente: Ai = MTBF/(MTBF + MTTR) = %s/(%s + %s) = %s' % (n(mtbf, 2), n(mtbf, 2), n(mttr, 2), pct(ai, 2))]
    if preventivos:
        L.append('MTBM = funcionamiento / intervenciones (fallas + preventivos) = %s/%d = %s h' % (n(operacion, 1), intervenciones, n(mtbm, 2)))
    L += ['MDT = (reparación + espera%s)/%s = %s/%d = %s h' % (' + preventivo' if preventivos else '',
                                                                'intervenciones' if preventivos else 'fallas',
                                                                n(parada, 2), intervenciones, n(mdt, 2)),
          'Disponibilidad operativa: Ao = %s/(%s + MDT) = %s/(%s + %s) = %s' % (
              'MTBM' if preventivos else 'MTBF', 'MTBM' if preventivos else 'MTBF', n(mtbm, 2), n(mtbm, 2), n(mdt, 2), pct(ao, 2)),
          'Control: Ao = funcionamiento/(funcionamiento + paradas de mantenimiento) = %s/(%s + %s) = %s'
          % (n(operacion, 1), n(operacion, 1), n(parada, 2), pct(r['Ao_tiempos'], 2)),
          'Ai mide la máquina y su mantenibilidad; Ao suma la logística y la organización. La diferencia entre las dos '
          'es lo que se pierde esperando.']
    return r, L


def confiabilidad(t, mtbf=None, objetivo=None, componentes=None, conexion='serie'):
    L, r = [], {}
    if mtbf:
        lam = 1 / mtbf
        R = math.exp(-lam * t)
        r.update({'lambda': lam, 'R': R, 'F': 1 - R})
        L += ['Tasa de fallas constante: λ = 1/MTBF = 1/%s = %s fallas/h' % (n(mtbf, 2), n(lam, 5)),
              'Confiabilidad: R(t) = e^(−λ·t) = e^(−%s/%s) = %s (probabilidad de funcionar %s h sin fallar)'
              % (n(t, 2), n(mtbf, 2), pct(R, 2), n(t, 2)),
              'Probabilidad de fallar antes: F(t) = 1 − R(t) = %s' % pct(1 - R, 2)]
        if objetivo:
            obj = fraccion(objetivo)
            if not 0 < obj < 1:
                raise ValueError('el objetivo de confiabilidad va entre 0 y 1 (o entre 0 y 100 %)')
            r['t_obj'] = -mtbf * math.log(obj)
            L.append('Tiempo para R = %s: t = −MTBF·ln R = −%s·ln %s = %s h' % (pct(obj, 1), n(mtbf, 2), n(obj, 3), n(r['t_obj'], 2)))
        L.append('Vale para fallas aleatorias (tramo plano de la curva de la bañera); si hay desgaste, la tasa crece '
                 'y R(t) real es menor.')
    if componentes:
        Rs = [math.exp(-t / m) for m in componentes]
        if conexion == 'serie':
            Rsis = 1.0
            for x in Rs:
                Rsis *= x
            lam_s = sum(1 / m for m in componentes)
            r.update({'R_sis': Rsis, 'MTBF_sis': 1 / lam_s})
            L += ['Serie (falla uno y para todo): R = R1·R2·… = %s = %s' % (' · '.join(n(x, 4) for x in Rs), pct(Rsis, 2)),
                  'λ del sistema = Σ λi = %s fallas/h → MTBF del sistema = %s h' % (n(lam_s, 5), n(1 / lam_s, 2))]
        else:
            prod = 1.0
            for x in Rs:
                prod *= (1 - x)
            Rsis = 1 - prod
            r['R_sis'] = Rsis
            L.append('Paralelo (redundancia, alcanza con uno): R = 1 − (1 − R1)·(1 − R2)·… = 1 − %s = %s'
                     % (n(prod, 6), pct(Rsis, 3)))
    if not L:
        raise ValueError('indicá --mtbf o --componentes')
    return r, L


def oee(planificado, paradas, total, buenas=None, rechazos=None, tasa=None, ciclo=None):
    if (tasa is None) == (ciclo is None):
        raise ValueError('indicá --tasa (unidades/min) o --ciclo (s por unidad), uno de los dos')
    if (buenas is None) == (rechazos is None):
        raise ValueError('indicá --buenas o --rechazos, uno de los dos')
    ciclo_s = ciclo if ciclo else 60.0 / tasa
    if buenas is None:
        buenas = total - rechazos
    if not 0 <= paradas < planificado:
        raise ValueError('las paradas tienen que ser menores que el tiempo planificado')
    if not 0 <= buenas <= total:
        raise ValueError('las unidades buenas van entre 0 y el total')
    marcha = planificado - paradas
    A = marcha / planificado
    P = total * ciclo_s / (marcha * 3600)
    if P > 1.0001:
        raise ValueError('rendimiento de %s: la tasa o el ciclo ideal están mal (tienen que ser los de la velocidad '
                         'máxima de la máquina, no los de un día bueno)' % pct(P, 1))
    Q = buenas / total if total else 0.0
    OEE = A * P * Q
    simple = buenas * ciclo_s / (planificado * 3600)
    perd_P = marcha - total * ciclo_s / 3600
    perd_Q = (total - buenas) * ciclo_s / 3600
    util = buenas * ciclo_s / 3600
    r = {'A': A, 'P': P, 'Q': Q, 'OEE': OEE, 'simple': simple, 'marcha': marcha, 'perd_A': paradas,
         'perd_P': perd_P, 'perd_Q': perd_Q, 'util': util}
    L = ['Tiempo planificado de producción: %s h (sin pausas ni paradas programadas fuera de producción)' % n(planificado, 2),
         'Tiempo en marcha = planificado − paradas (fallas, cambios de formato, ajustes) = %s − %s = %s h'
         % (n(planificado, 2), n(paradas, 2), n(marcha, 2)),
         'Disponibilidad: A = marcha/planificado = %s/%s = %s' % (n(marcha, 2), n(planificado, 2), pct(A, 2)),
         'Rendimiento: P = ciclo ideal·total/marcha = %s s·%s/(%s h·3600) = %s' % (n(ciclo_s, 3), n(total, 0), n(marcha, 2), pct(P, 2)),
         'Calidad: Q = buenas/total = %s/%s = %s' % (n(buenas, 0), n(total, 0), pct(Q, 2)),
         'OEE = A·P·Q = %s·%s·%s = %s' % (n(A, 4), n(P, 4), n(Q, 4), pct(OEE, 2)),
         'Control: OEE = buenas·ciclo ideal/planificado = %s·%s s/(%s h·3600) = %s' % (n(buenas, 0), n(ciclo_s, 3), n(planificado, 2), pct(simple, 2)),
         'Horas perdidas: por disponibilidad %s h, por rendimiento %s h, por calidad %s h; productivas %s h (suman %s h)'
         % (n(paradas, 2), n(perd_P, 2), n(perd_Q, 2), n(util, 2), n(paradas + perd_P + perd_Q + util, 2))]
    ref = OEE_CLASE_MUNDIAL
    L.append('Referencia de clase mundial (Nakajima, según oee.com): A %s, P %s, Q %s, OEE %s → acá: A %s, P %s, Q %s'
             % (pct(ref['A'], 0), pct(ref['P'], 0), pct(ref['Q'], 0), pct(ref['OEE'], 0),
                'cumple' if A >= ref['A'] else 'no llega', 'cumple' if P >= ref['P'] else 'no llega',
                'cumple' if Q >= ref['Q'] else 'no llega'))
    mayor = max((('disponibilidad', paradas), ('rendimiento', perd_P), ('calidad', perd_Q)), key=lambda x: x[1])
    L.append('La mayor pérdida es la de %s: por ahí conviene empezar.' % mayor[0])
    return r, L


def costo(hh=0.0, costo_hh=0.0, materiales=0.0, terceros=0.0, parada=0.0, costo_parada=0.0, unidades=None,
          reposicion=None, meses=1.0):
    mo = hh * costo_hh
    directo = mo + materiales + terceros
    indirecto = parada * costo_parada
    total = directo + indirecto
    r = {'mano_obra': mo, 'directo': directo, 'indirecto': indirecto, 'total': total}
    L = ['Mano de obra: %s h-h · $ %s = $ %s' % (n(hh, 1), n(costo_hh, 0), n(mo, 0)),
         'Costo directo = mano de obra + repuestos y materiales + servicios de terceros = %s + %s + %s = $ %s'
         % (n(mo, 0), n(materiales, 0), n(terceros, 0), n(directo, 0)),
         'Costo indirecto (de la parada) = horas de parada no planificada · costo de la hora parada = %s · %s = $ %s'
         % (n(parada, 1), n(costo_parada, 0), n(indirecto, 0)),
         'Costo total del período = $ %s (el indirecto es el %s del total)' % (n(total, 0), pct(indirecto / total if total else 0, 1))]
    if unidades:
        r['por_unidad'] = total / unidades
        r['directo_por_unidad'] = directo / unidades
        L.append('Por unidad buena: total $ %s; solo directo $ %s' % (n(r['por_unidad'], 3), n(r['directo_por_unidad'], 3)))
    if reposicion:
        anual = directo * 12.0 / meses
        r['anual'] = anual
        r['sobre_reposicion'] = anual / reposicion
        L.append('Costo directo anual = %s · 12/%s = $ %s → sobre el valor de reposición del activo ($ %s): %s'
                 % (n(directo, 0), n(meses, 0), n(anual, 0), n(reposicion, 0), pct(r['sobre_reposicion'], 2)))
        L.append('Indicador del tipo de los de la EN 15341 (código y definición exactos: verificar en la norma vigente).')
    return r, L


# ------------------------------------------------------------------------------------------ análisis de fallas
def pareto_desde_filas(filas, agrupar=None, columna=None, contar=False):
    claves = set(filas[0])
    if agrupar:
        campos = [sin_tildes(c) for c in agrupar.split(',')]
    elif {'equipo', 'causa'} <= claves:
        campos = ['equipo', 'causa']
    else:
        campos = [next((c for c in ('causa', 'categoria', 'equipo', 'modo') if c in claves), None)]
    if None in campos or not all(c in claves for c in campos):
        raise ValueError('no encuentro la columna para agrupar (causa, equipo…): usar --agrupar')
    datos = {}
    for f in filas:
        nombre = ' — '.join(f[c] for c in campos)
        if contar:
            v = 1.0
        elif columna:
            v = num(f[sin_tildes(columna)])
        elif 'valor' in f:
            v = num(f['valor'])
        elif 'reparacion_h' in f:
            v = num(f['reparacion_h']) + num(valor(f, 'espera_h', defecto='0'))
        else:
            raise ValueError('no encuentro el valor: usar --columna o --contar')
        datos[nombre] = datos.get(nombre, 0.0) + v
    return list(datos.items())


def pareto(items, umbral=80.0, unidad='h'):
    if not items:
        raise ValueError('no hay datos')
    orden = sorted(enumerate(items), key=lambda x: (-x[1][1], x[0]))
    total = sum(v for _, (_, v) in orden)
    if total <= 0:
        raise ValueError('la suma de los valores tiene que ser mayor que cero')
    filas, acum, vitales = [], 0.0, 0
    for _, (nombre, v) in orden:
        previo = acum
        acum += v
        clase = 'vital' if previo < umbral / 100 * total - 1e-9 else 'resto'
        if clase == 'vital':
            vitales += 1
        filas.append((nombre, v, v / total, acum / total, clase))
    dec = 0 if all(float(v).is_integer() for _, v, _, _, _ in filas) else 2
    L = ['| Causa | Valor [%s] | %% | %% acumulado | Clase |' % unidad, '|---|---:|---:|---:|---|']
    for nombre, v, p, a, c in filas:
        L.append('| %s | %s | %s | %s | %s |' % (nombre, n(v, dec), pct(p, 1), pct(a, 1), c))
    L.append('| **Total** | **%s** | 100 %% | | |' % n(total, dec))
    L.append('')
    L.append('Pocas vitales: %d de %d causas explican el %s del total (umbral %s %%): se atacan primero.'
             % (vitales, len(filas), pct(filas[vitales - 1][3], 1), n(umbral, 0)))
    return {'filas': filas, 'total': total, 'vitales': vitales}, L


def entero_1_10(texto, campo, fila):
    try:
        x = float(str(texto).replace(',', '.'))
    except ValueError:
        raise ValueError('fila %d: %s = %r no es un número' % (fila, campo, texto))
    if x != int(x) or not 1 <= x <= 10:
        raise ValueError('fila %d: %s = %s tiene que ser un entero de 1 a 10' % (fila, campo, texto))
    return int(x)


def amfe(filas, umbral=None):
    items = []
    for i, f in enumerate(filas, 1):
        s = entero_1_10(valor(f, 's', 'severidad', defecto=''), 'S', i)
        o = entero_1_10(valor(f, 'o', 'ocurrencia', defecto=''), 'O', i)
        d = entero_1_10(valor(f, 'd', 'deteccion', defecto=''), 'D', i)
        it = {'n': i, 'componente': valor(f, 'componente', 'elemento', 'funcion', defecto='?'),
              'modo': valor(f, 'modo', 'modo de falla', 'modo_falla', defecto='?'), 'efecto': valor(f, 'efecto', defecto=''),
              'causa': valor(f, 'causa', defecto=''), 'accion': valor(f, 'accion', 'acciones', defecto=''),
              'S': s, 'O': o, 'D': d, 'NPR': s * o * d}
        nuevos = [valor(f, k, defecto='') for k in ('s2', 'o2', 'd2')]
        if any(nuevos):
            if not all(nuevos):
                raise ValueError('fila %d: S2, O2 y D2 van los tres juntos' % i)
            s2, o2, d2 = (entero_1_10(x, c, i) for x, c in zip(nuevos, ('S2', 'O2', 'D2')))
            it.update({'S2': s2, 'O2': o2, 'D2': d2, 'NPR2': s2 * o2 * d2})
        items.append(it)
    items.sort(key=lambda x: (-x['NPR'], -x['S'], x['n']))
    con_nuevo = any('NPR2' in x for x in items)
    cab = '| N.º | Componente | Modo de falla | S | O | D | NPR |' + (" S' | O' | D' | NPR' | Baja |" if con_nuevo else '')
    sep = '|---:|---|---|---:|---:|---:|---:|' + ('---:|---:|---:|---:|---:|' if con_nuevo else '')
    L = [cab, sep]
    for x in items:
        fila = '| %d | %s | %s | %d | %d | %d | %d |' % (x['n'], x['componente'], x['modo'], x['S'], x['O'], x['D'], x['NPR'])
        if con_nuevo:
            if 'NPR2' in x:
                fila += ' %d | %d | %d | %d | %s |' % (x['S2'], x['O2'], x['D2'], x['NPR2'], pct(1 - x['NPR2'] / x['NPR'], 1))
            else:
                fila += ' | | | | |'
        L.append(fila)
    L.append('')
    L.append('NPR = S·O·D (cada uno de 1 a 10, así que va de 1 a 1000). Orden: NPR de mayor a menor; con igual NPR, mayor S.')
    altos = [x for x in items if x['S'] >= 9]
    for x in altos:
        L.append('ATENCIÓN fila %d: S = %d (seguridad o reglamentación): se trata aunque el NPR sea bajo.' % (x['n'], x['S']))
    if umbral:
        sobre = [str(x['n']) for x in items if x['NPR'] >= umbral]
        L.append('Con el umbral de la empresa (NPR ≥ %d): actuar en las filas %s.' % (umbral, ', '.join(sobre) if sobre else 'ninguna'))
    r = {'items': items, 'NPR_total': sum(x['NPR'] for x in items)}
    if con_nuevo:
        r['NPR2_total'] = sum(x.get('NPR2', x['NPR']) for x in items)
        r['baja'] = 1 - r['NPR2_total'] / r['NPR_total']
        L.append('Suma de NPR: %d antes y %d después de las acciones (baja %s).' % (r['NPR_total'], r['NPR2_total'], pct(r['baja'], 1)))
        sin_s = [str(x['n']) for x in items if 'S2' in x and x['S2'] < x['S']]
        if sin_s:
            L.append('Filas %s: bajar S exige cambiar el diseño o el proceso; verificar que la acción lo haga.' % ', '.join(sin_s))
    return r, L


# ------------------------------------------------------------------------------------------ relubricación (SKF)
def relubricacion(d, D, B, rpm, tipo='rigido-bolas', cp=15.0, tf=None, temp=70.0, vertical=False,
                  gira_exterior=False, jaula_especial=False, horas_dia=None):
    if tipo not in SKF_BF:
        raise ValueError('tipo de rodamiento: %s' % ', '.join(SKF_BF))
    if not 0 < d < D:
        raise ValueError('tiene que ser 0 < d < D (agujero menor que el diámetro exterior)')
    nombre, bf, limites = SKF_BF[tipo]
    dm = 0.5 * (d + D)
    A = rpm * (D if gira_exterior else dm)
    Abf = A * bf
    if cp >= 15:
        col, etiqueta = 0, 'C/P ≥ 15'
    elif cp >= 8:
        col, etiqueta = 1, 'C/P ≈ 8'
    else:
        col, etiqueta = 2, 'C/P ≈ 4'
    limite = limites[col]
    gp_lado, gp_centro = 0.005 * D * B, 0.002 * D * B
    r = {'dm': dm, 'A': A, 'Abf': Abf, 'bf': bf, 'limite': limite, 'Gp_lado': gp_lado, 'Gp_centro': gp_centro}
    L = ['Rodamiento %s: d = %s mm, D = %s mm, B = %s mm; dm = (d + D)/2 = %s mm' % (nombre, n(d, 0), n(D, 0), n(B, 0), n(dm, 1)),
         'Factor de velocidad: A = n·%s = %s·%s = %s mm/min; bf = %s → A·bf = %s mm/min'
         % ('D (gira el aro exterior)' if gira_exterior else 'dm', n(rpm, 0), n(D if gira_exterior else dm, 1), n(A, 0), n(bf, 1), n(Abf, 0))]
    if limite is None:
        L.append('Para %s la tabla de SKF no da límite con %s: solo cargas altas (C/P ≈ 4) o consultar a SKF.' % (nombre, etiqueta))
    else:
        L.append('Límite recomendado de n·dm con %s (tabla 1 de SKF): %s mm/min → %s' % (
            etiqueta, n(limite, 0), 'la grasa sirve' if A <= limite else 'SUPERADO: grasa especial, aceite o consultar a SKF'))
    if cp < 4:
        L.append('AVISO: C/P menor que 4 (carga muy alta): fuera del diagrama de SKF, consultar al fabricante.')
    if tf:
        f_temp = 1.0
        if temp > 70:
            f_temp = 0.5 ** ((temp - 70.0) / 15.0)
            t_txt = 'a %s °C: × 0,5^((%s − 70)/15) = × %s (la mitad cada 15 °C sobre 70 °C)' % (n(temp, 0), n(temp, 0), n(f_temp, 3))
        elif temp <= 55 and tipo not in SIN_EXTENSION:
            f_temp = 2.0
            t_txt = 'a %s °C (15 °C o más por debajo de 70 °C): × 2, una sola vez' % n(temp, 0)
        else:
            t_txt = 'a %s °C: sin cambio%s' % (n(temp, 0), ' (lleno o axial: SKF no permite alargarlo)' if temp <= 55 else '')
        factores = [('temperatura ' + t_txt, f_temp)]
        if vertical:
            factores.append(('eje vertical (la grasa se escurre): × 0,5', 0.5))
        if d > 300:
            factores.append(('agujero d > 300 mm: × 0,5', 0.5))
        if jaula_especial:
            factores.append(('rodillos cilíndricos con jaula J, JA, JB, MA, MB, ML, MP o PHA: × 0,5', 0.5))
        f_total = 1.0
        for _, f in factores:
            f_total *= f
        tf_aj = tf * f_total
        r.update({'tf': tf, 'f_total': f_total, 'tf_aj': tf_aj})
        L.append('Intervalo leído en el diagrama de SKF (70 °C, eje horizontal, ambiente limpio): tf = %s h de funcionamiento' % n(tf, 0))
        for texto, _ in factores:
            L.append('  ajuste por ' + texto)
        L.append('Intervalo ajustado: tf = %s·%s = %s h' % (n(tf, 0), n(f_total, 3), n(tf_aj, 0)))
        if tf_aj > 30000:
            r['tf_aj'] = 30000.0
            L.append('SKF no aconseja intervalos de más de 30 000 h: se adopta 30 000 h.')
        if horas_dia:
            L.append('Con %s h de marcha por día: cada %s días (unas %s semanas)' % (
                n(horas_dia, 0), n(r['tf_aj'] / horas_dia, 0), n(r['tf_aj'] / horas_dia / 7, 1)))
        L.append('Vibraciones, arranques frecuentes o contaminación acortan el intervalo (SKF no da un factor: criterio y tendencia).')
    else:
        L.append('Con A·bf y la curva de C/P se lee tf en el diagrama de relubricación del catálogo SKF y se pasa con --tf.')
    if tipo in ('cil-lleno', 'carb-lleno'):
        L.append('Nota de la tabla 1 de SKF para rodamientos llenos: el tf del diagrama se divide por 10 (verificar en el catálogo).')
    L.append('Grasa a reponer por el costado: Gp = 0,005·D·B = 0,005·%s·%s = %s g' % (n(D, 0), n(B, 0), n(gp_lado, 1)))
    L.append('Grasa por la ranura y los agujeros del aro exterior: Gp = 0,002·D·B = %s g (B: ancho total; T en cónicos, H en axiales)'
             % n(gp_centro, 1))
    L.append('Si el motor o la máquina trae placa o manual con intervalo y gramos de grasa, manda eso.')
    return r, L


# ------------------------------------------------------------------------------------------ vibraciones (ISO 20816-3)
def grupo_iso(grupo=None, potencia=None, altura=None):
    if grupo:
        return grupo, 'indicado'
    if altura is not None:
        if altura >= 315:
            return 1, 'máquina eléctrica con altura de eje H = %s mm ≥ 315 mm' % n(altura, 0)
        if altura >= 160:
            return 2, 'máquina eléctrica con 160 mm ≤ H = %s mm < 315 mm' % n(altura, 0)
    if potencia is not None:
        if potencia > 300:
            return 1, 'potencia %s kW > 300 kW' % n(potencia, 1)
        if potencia > 15:
            return 2, 'potencia de más de 15 kW hasta 300 kW (%s kW)' % n(potencia, 1)
    return None, 'fuera del alcance de ISO 20816-3 (15 kW o menos, o H < 160 mm)'


def zona(v, limites):
    ab, bc, cd = limites
    if v <= ab:
        return 'A'
    if v <= bc:
        return 'B'
    if v <= cd:
        return 'C'
    return 'D'


def frecuencias_rodamiento(rpm, bolas, dbola, dprim, angulo=0.0):
    fr = rpm / 60.0
    k = dbola / dprim * math.cos(math.radians(angulo))
    return {'fr': fr, 'BPFO': bolas / 2 * fr * (1 - k), 'BPFI': bolas / 2 * fr * (1 + k),
            'FTF': fr / 2 * (1 - k), 'BSF': dprim / (2 * dbola) * fr * (1 - k * k)}


def vibracion(v=None, grupo=None, soporte='rigido', potencia=None, altura=None, base=None, rpm=None, bolas=None,
              dbola=None, dprim=None, angulo=0.0):
    r, L = {}, []
    if v is not None:
        g, motivo = grupo_iso(grupo, potencia, altura)
        if g is None:
            L += ['Grupo: %s.' % motivo,
                  'Para máquinas chicas no hay tabla en ISO 20816-3: comparar con la línea de base de la misma máquina '
                  '(tendencia), el criterio del fabricante e ISO 20816-1 (verificar en la norma vigente).']
            r['zona'] = None
        else:
            lim = ZONAS_ISO20816_3[(g, soporte)]
            z = zona(v, lim)
            r.update({'grupo': g, 'zona': z, 'limites': lim})
            L += ['ISO 20816-3, grupo %d (%s), soporte %s: límites A/B %s, B/C %s y C/D %s mm/s eficaces (10 Hz a 1000 Hz)'
                  % (g, motivo, 'rígido' if soporte == 'rigido' else soporte, n(lim[0], 1), n(lim[1], 1), n(lim[2], 1)),
                  'Medido: %s mm/s eficaces (el mayor de las direcciones radiales de cada cojinete) → zona %s: %s.'
                  % (n(v, 2), z, ZONA_TEXTO[z])]
            disparo = 1.25 * lim[2]
            r['disparo_max'] = disparo
            if base is not None:
                alarma = base + 0.25 * lim[1]
                alarma_max = 1.25 * lim[1]
                cambio = v - base
                r.update({'alarma': min(alarma, alarma_max), 'cambio': cambio, 'cambio_lim': 0.25 * lim[1]})
                L.append('ALARMA = línea de base + 25 %% del límite B/C = %s + 0,25·%s = %s mm/s (sin pasar 1,25·B/C = %s mm/s)'
                         % (n(base, 2), n(lim[1], 1), n(alarma, 2), n(alarma_max, 2)))
                L.append('Cambio respecto de la base: %s mm/s %s 25 %% de B/C (%s mm/s) → %s' % (
                    n(cambio, 2), '>' if abs(cambio) > 0.25 * lim[1] else '≤', n(0.25 * lim[1], 2),
                    'cambio significativo: investigar la causa aunque la zona sea A o B' if abs(cambio) > 0.25 * lim[1] else 'sin cambio significativo'))
            L.append('DISPARO: dentro de la zona C o D, sin pasar 1,25·C/D = %s mm/s (lo fija el fabricante y la experiencia).' % n(disparo, 1))
    if rpm and bolas and dbola and dprim:
        f = frecuencias_rodamiento(rpm, bolas, dbola, dprim, angulo)
        r['frec'] = f
        L += ['Frecuencias de defecto del rodamiento (%d elementos, d = %s mm, dm = %s mm, ángulo %s°), a %s rpm (fr = %s Hz):'
              % (bolas, n(dbola, 2), n(dprim, 2), n(angulo, 0), n(rpm, 0), n(f['fr'], 2)),
              '  aro exterior BPFO = (Z/2)·fr·(1 − (d/dm)·cos α) = %s Hz (%s × fr)' % (n(f['BPFO'], 2), n(f['BPFO'] / f['fr'], 3)),
              '  aro interior BPFI = (Z/2)·fr·(1 + (d/dm)·cos α) = %s Hz (%s × fr)' % (n(f['BPFI'], 2), n(f['BPFI'] / f['fr'], 3)),
              '  jaula FTF = (fr/2)·(1 − (d/dm)·cos α) = %s Hz; elemento rodante BSF = (dm/(2·d))·fr·(1 − ((d/dm)·cos α)²) = %s Hz'
              % (n(f['FTF'], 2), n(f['BSF'], 2))]
    if not L:
        raise ValueError('indicá --v (velocidad eficaz) o los datos del rodamiento (--rpm --bolas --dbola --dprim)')
    return r, L


# ------------------------------------------------------------------------------------------ alineación, balanceo, termografía
def alineacion(rpm, paralela, angular):
    fila = next((f for f in SKF_ALINEACION if rpm <= f[0]), None)
    if fila is None:
        raise ValueError('la tabla de SKF llega hasta 6000 rpm: usar la tolerancia del fabricante')
    hasta, p_max, a_max = fila
    desde = max([0] + [f[0] for f in SKF_ALINEACION if f[0] < hasta])
    ok_p, ok_a = abs(paralela) <= p_max, abs(angular) <= a_max
    r = {'p_max': p_max, 'a_max': a_max, 'ok': ok_p and ok_a}
    L = ['Guía de SKF (TKSA 20, anexo 3) para %s rpm (tramo %d a %d rpm): paralelo ≤ %s mm, angular ≤ %s mm/100 mm'
         % (n(rpm, 0), desde, hasta, n(p_max, 2), n(a_max, 2)),
         'Paralelo medido %s mm → %s; angular medido %s mm/100 mm → %s' % (
             n(paralela, 3), 'bien' if ok_p else 'FUERA', n(angular, 3), 'bien' if ok_a else 'FUERA'),
         'Resultado: %s. Si el fabricante del acoplamiento o de la máquina da otra tolerancia, manda esa.'
         % ('alineado dentro de la guía' if r['ok'] else 'hay que corregir')]
    return r, L


def balanceo(G, masa, rpm, planos=1, radio=None):
    omega = 2 * math.pi * rpm / 60
    eper = 1000 * G / omega
    uper = eper * masa
    r = {'omega': omega, 'eper': eper, 'Uper': uper, 'por_plano': uper / planos}
    L = ['Ω = 2π·n/60 = %s rad/s; grado G %s → e = 1000·G/Ω = %s g·mm/kg (µm)' % (n(omega, 2), n(G, 1), n(eper, 2)),
         'Desbalance residual admisible: Uper = e·m = %s·%s kg = %s g·mm (= 9549·G·m/n)' % (n(eper, 2), n(masa, 1), n(uper, 1))]
    if planos > 1:
        L.append('Repartido en %d planos (rotor simétrico, reparto simple; verificar el reparto en la norma): %s g·mm por plano'
                 % (planos, n(r['por_plano'], 1)))
    if radio:
        r['masa_radio'] = r['por_plano'] / radio
        L.append('Masa equivalente a %s mm del eje: %s g por plano' % (n(radio, 0), n(r['masa_radio'], 2)))
    return r, L


def termografia(similar=None, ambiente=None):
    if similar is None and ambiente is None:
        raise ValueError('indicá --similar o --ambiente (ΔT en °C)')
    prios = []
    L = []
    if similar is not None:
        p = None if similar < 1 else 4 if similar <= 3 else 3 if similar <= 15 else 1
        prios.append(p)
        L.append('ΔT entre componentes similares con carga similar: %s °C → %s' % (
            n(similar, 1), 'por debajo de la tabla (menos de 1 °C)' if p is None else 'prioridad %d, %s' % (p, NETA_ACCIONES[p])))
    if ambiente is not None:
        p = None if ambiente < 1 else 4 if ambiente <= 10 else 3 if ambiente <= 20 else 2 if ambiente <= 40 else 1
        prios.append(p)
        L.append('ΔT del componente sobre el aire ambiente: %s °C → %s' % (
            n(ambiente, 1), 'por debajo de la tabla (menos de 1 °C)' if p is None else 'prioridad %d, %s' % (p, NETA_ACCIONES[p])))
    validas = [p for p in prios if p is not None]
    peor = min(validas) if validas else None
    if peor:
        L.append('Se toma la más severa: %s (ANSI/NETA MTS, tabla 100.18; verificar en la edición vigente).' % NETA_ACCIONES[peor])
    L.append('Medir con carga (el calentamiento va con el cuadrado de la corriente), anotar la carga y ajustar la emisividad.')
    return {'prioridad': peor}, L


# ------------------------------------------------------------------------------------------ demo
REGISTRO_DEMO = """fecha;equipo;causa;reparacion_h;espera_h
2026-03-03;Llenadora;Válvulas de llenado (goteo);1,5;0,5
2026-03-05;Tapadora;Embrague del cabezal;2,0;0,5
2026-03-09;Etiquetadora;Sensor de etiqueta;0,75;0
2026-03-11;Llenadora;Válvulas de llenado (goteo);1,5;0,5
2026-03-16;Transportador;Cadena trabada;3,0;1,0
2026-03-18;Encajonadora;Ventosas;1,0;0,5
2026-03-23;Tapadora;Embrague del cabezal;2,0;0,5
2026-03-25;Etiquetadora;Sensor de etiqueta;0,75;0
2026-03-30;Llenadora;Válvulas de llenado (goteo);1,0;1,0
"""

AMFE_DEMO = """componente;modo;efecto;causa;control;S;O;D;accion;S2;O2;D2
Motor principal (rodamiento lado acople);Rodamiento dañado;Parada de 4 a 8 h para cambiarlo;Relubricación sin plan;Ninguno: se detecta por ruido;7;4;8;Plan de relubricación (método SKF) y medición mensual de vibraciones con alarma;7;3;3
Válvulas de llenado;Junta desgastada: la válvula gotea;Envases con bajo nivel y parada de 1 a 4 h;Juntas que se cambian solo cuando fallan;Inspección visual al inicio del turno;6;7;5;Cambio preventivo de juntas cada 250 h y control de nivel en la planilla;6;4;4
Sensor de nivel (fotocélula);Lente sucia o desalineada;Pasan envases mal llenados durante 1 a 2 h;Salpicaduras de producto y limpieza no programada;Control de peso por muestreo cada 2 h;6;5;6;Limpieza y prueba con envase patrón en cada cambio de turno;6;3;3
Cadena de la estrella de transferencia;Cadena estirada o sin lubricar;Trabado y parada de 1 a 4 h;Lubricación irregular;Inspección semanal;6;5;4;Lubricación en la ruta diaria y medición mensual del estiramiento;6;3;4
"""


def cerca(x, y, tol):
    return x is not None and abs(x - y) <= tol


def cmd_demo():
    ok = []
    # Línea de envasado: 22 días × 2 turnos × 8 h = 352 h; pausas y limpieza 22 h → planificado 330 h;
    # 9 fallas (18 h de parada) y 4 cambios de formato (6 h) → funcionamiento 306 h
    nf, rep, esp, filas = leer_registro(texto=REGISTRO_DEMO)
    ok.append(('registro: %d fallas, %s h de reparación y %s h de espera' % (nf, n(rep, 2), n(esp, 2)),
               nf == 9 and cerca(rep, 13.5, 1e-9) and cerca(esp, 4.5, 1e-9)))
    r, _ = indicadores(306, nf, rep, esp)
    ok.append(('MTBF %s h, MTTR %s h, MDT %s h' % (n(r['MTBF'], 2), n(r['MTTR'], 2), n(r['MDT'], 2)),
               cerca(r['MTBF'], 34.0, 1e-9) and cerca(r['MTTR'], 1.5, 1e-9) and cerca(r['MDT'], 2.0, 1e-9)))
    ok.append(('Ai = 34/35,5 = %s y Ao = 34/36 = %s = 306/(306 + 18)' % (pct(r['Ai'], 2), pct(r['Ao'], 2)),
               cerca(r['Ai'], 34 / 35.5, 1e-12) and cerca(r['Ao'], 34 / 36, 1e-12) and cerca(r['Ao_tiempos'], r['Ao'], 1e-12)))
    r2, _ = indicadores(306, 9, 13.5, 4.5, preventivos=2, t_preventivo=3.0)
    ok.append(('con 2 preventivos de 1,5 h: Ao = MTBM/(MTBM + MDT) = %s = 306/(306 + 21)' % pct(r2['Ao'], 2),
               cerca(r2['Ao'], 306 / 327, 1e-12) and cerca(r2['MTBM'], 306 / 11, 1e-12)))
    r, _ = confiabilidad(8, mtbf=34, objetivo=0.9)
    ok.append(('R(8 h) = e^(−8/34) = %s; para R = 90 %%, t = %s h' % (pct(r['R'], 2), n(r['t_obj'], 2)),
               cerca(r['R'], 0.790338, 1e-6) and cerca(r['t_obj'], 3.58226, 1e-5) and cerca(r['F'], 1 - r['R'], 1e-15)))
    rs, _ = confiabilidad(10, componentes=[100, 200], conexion='serie')
    rp, _ = confiabilidad(10, componentes=[100, 200], conexion='paralelo')
    ok.append(('serie e^(−0,15) = %s y paralelo = %s' % (n(rs['R_sis'], 5), n(rp['R_sis'], 5)),
               cerca(rs['R_sis'], math.exp(-0.15), 1e-12) and cerca(rs['MTBF_sis'], 200 / 3, 1e-9)
               and cerca(rp['R_sis'], 1 - (1 - math.exp(-0.1)) * (1 - math.exp(-0.05)), 1e-12)))
    r, _ = oee(330, 24, 1562000, rechazos=31400, tasa=100)
    ok.append(('OEE: A %s, P %s, Q %s → %s' % (pct(r['A'], 2), pct(r['P'], 2), pct(r['Q'], 2), pct(r['OEE'], 2)),
               cerca(r['A'], 306 / 330, 1e-12) and cerca(r['P'], 1562000 / 1836000, 1e-12)
               and cerca(r['Q'], 1530600 / 1562000, 1e-12) and cerca(r['OEE'], 0.773030, 1e-6)))
    ok.append(('OEE por la fórmula simple = producto, y las horas suman 330 (productivas %s h)' % n(r['util'], 2),
               cerca(r['simple'], r['OEE'], 1e-12) and cerca(r['perd_A'] + r['perd_P'] + r['perd_Q'] + r['util'], 330, 1e-9)))
    r, _ = oee(7, 47 / 60, 19271, rechazos=423, ciclo=1.0)
    ok.append(('ejemplo publicado por oee.com (420 min, 47 min parado, 1 s, 19 271 y 423): OEE %s (publicado 74,79 %%)' % pct(r['OEE'], 2),
               cerca(r['A'], 0.8881, 5e-5) and cerca(r['P'], 0.8611, 5e-5) and cerca(r['Q'], 0.9780, 5e-5) and cerca(r['OEE'], 0.7479, 5e-5)))
    r, _ = costo(67, 15000, 1600000, 400000, 18, 180000, unidades=1530600, reposicion=1.5e9, meses=1)
    ok.append(('costo: directo $ %s, indirecto $ %s, total $ %s, %s del valor de reposición'
               % (n(r['directo'], 0), n(r['indirecto'], 0), n(r['total'], 0), pct(r['sobre_reposicion'], 2)),
               cerca(r['directo'], 3005000, 1e-6) and cerca(r['indirecto'], 3240000, 1e-6) and cerca(r['total'], 6245000, 1e-6)
               and cerca(r['por_unidad'], 6245000 / 1530600, 1e-12) and cerca(r['sobre_reposicion'], 0.02404, 1e-9)))
    r, _ = pareto(pareto_desde_filas(filas))
    orden = [f[0].split(' — ')[0] for f in r['filas']]
    ok.append(('Pareto: %s; las 3 primeras suman %s' % (', '.join(orden), pct(r['filas'][2][3], 1)),
               orden == ['Llenadora', 'Tapadora', 'Transportador', 'Etiquetadora', 'Encajonadora'] and r['vitales'] == 3
               and cerca(r['total'], 18.0, 1e-9) and cerca(r['filas'][2][3], 15 / 18, 1e-12)))
    rc, _ = pareto(pareto_desde_filas(filas, contar=True), unidad='fallas')
    ok.append(('Pareto por cantidad: %d fallas, la llenadora primero con 3' % rc['total'],
               cerca(rc['total'], 9, 1e-9) and rc['filas'][0][1] == 3))
    r, _ = amfe(leer_filas(texto=AMFE_DEMO))
    nprs = [x['NPR'] for x in r['items']]
    nuevos = [x['NPR2'] for x in r['items']]
    ok.append(('AMFE: NPR %s antes y %s después (baja %s)' % (nprs, nuevos, pct(r['baja'], 1)),
               nprs == [224, 210, 180, 120] and nuevos == [63, 96, 54, 72] and r['NPR_total'] == 734
               and r['NPR2_total'] == 285 and cerca(r['baja'], 1 - 285 / 734, 1e-12)))
    try:
        amfe(leer_filas(texto='componente;modo;S;O;D\nX;Y;11;2;3\n'))
        rechaza = False
    except ValueError:
        rechaza = True
    ok.append(('AMFE: rechaza S = 11 (la escala va de 1 a 10)', rechaza))
    # Relubricación: ejemplo del curso de SKF (61868 MA a 500 rpm, dm = 380 mm, carga liviana → tf ≈ 10 000 h)
    r, _ = relubricacion(340, 420, 38, 500, 'rigido-bolas', cp=15, tf=10000)
    ok.append(('SKF 61868 MA: A = %s mm/min (curso de SKF: 190 000), Gp = %s g; d > 300 mm → %s h'
               % (n(r['A'], 0), n(r['Gp_lado'], 1), n(r['tf_aj'], 0)),
               cerca(r['A'], 190000, 1e-6) and r['limite'] == 500000 and cerca(r['Gp_lado'], 79.8, 1e-9)
               and cerca(r['Gp_centro'], 31.92, 1e-9) and cerca(r['tf_aj'], 5000, 1e-6)))
    r85, _ = relubricacion(45, 100, 25, 1480, 'rigido-bolas', tf=8000, temp=85)
    r100, _ = relubricacion(45, 100, 25, 1480, 'rigido-bolas', tf=8000, temp=100)
    r50, _ = relubricacion(45, 100, 25, 1480, 'rigido-bolas', tf=8000, temp=50)
    rax, _ = relubricacion(45, 100, 25, 1480, 'axial-cil', tf=8000, temp=50)
    ok.append(('6309 a 1480 rpm: A = %s mm/min, Gp = %s g; tf × 0,5 a 85 °C, × 0,25 a 100 °C, × 2 a 50 °C (axial: × 1)'
               % (n(r85['A'], 0), n(r85['Gp_lado'], 1)),
               cerca(r85['A'], 107300, 1e-6) and cerca(r85['Gp_lado'], 12.5, 1e-9) and cerca(r85['tf_aj'], 4000, 1e-6)
               and cerca(r100['tf_aj'], 2000, 1e-6) and cerca(r50['tf_aj'], 16000, 1e-6) and cerca(rax['tf_aj'], 8000, 1e-6)))
    # Vibraciones: motor de la llenadora, carcasa 160 (H = 160 mm → grupo 2), base rígida
    r, _ = vibracion(3.2, altura=160, soporte='rigido', base=1.1)
    ok.append(('ISO 20816-3: 3,2 mm/s en grupo 2 rígido → zona %s; ALARMA %s mm/s; DISPARO hasta %s mm/s'
               % (r['zona'], n(r['alarma'], 2), n(r['disparo_max'], 2)),
               r['grupo'] == 2 and r['zona'] == 'C' and cerca(r['alarma'], 1.8, 1e-9) and cerca(r['disparo_max'], 5.625, 1e-9)
               and r['cambio'] > r['cambio_lim']))
    zonas = [vibracion(v, grupo=g, soporte=s)[0]['zona'] for v, g, s in
             ((1.4, 2, 'rigido'), (1.41, 2, 'rigido'), (11.0, 1, 'flexible'), (11.1, 1, 'flexible'), (4.6, 1, 'rigido'))]
    ok.append(('bordes de zona: %s' % ', '.join(zonas), zonas == ['A', 'B', 'C', 'D', 'C']))
    f = frecuencias_rodamiento(1500, 9, 12.0, 60.0, 0)
    ok.append(('frecuencias de rodamiento: BPFO + BPFI = Z·fr y Z·FTF = BPFO',
               cerca(f['BPFO'] + f['BPFI'], 9 * 25.0, 1e-9) and cerca(9 * f['FTF'], f['BPFO'], 1e-9)
               and cerca(f['BSF'], 60 / 24 * 25 * (1 - 0.04), 1e-9)))
    r, _ = alineacion(1480, 0.08, 0.06)
    r2, _ = alineacion(3500, 0.08, 0.04)
    ok.append(('alineación a 1480 rpm (≤ 0,10 mm y 0,08 mm/100 mm): bien; a 3500 rpm, 0,08 mm: fuera',
               r['ok'] and r['p_max'] == 0.10 and r['a_max'] == 0.08 and not r2['ok']))
    r, _ = balanceo(6.3, 25, 1480, planos=2, radio=200)
    oz_in = balanceo(6.3, 500 * 0.45359237, 900)[0]['Uper'] / (28.349523125 * 25.4)
    ok.append(('balanceo G 6,3, 25 kg, 1480 rpm: Uper = %s g·mm = 9549·G·m/n; ejemplo de IRD: %s oz·in (publicado 21)'
               % (n(r['Uper'], 1), n(oz_in, 1)),
               cerca(r['Uper'], 60000 / (2 * math.pi) * 6.3 * 25 / 1480, 1e-9) and cerca(r['Uper'], 9549 * 6.3 * 25 / 1480, 0.1)
               and cerca(r['masa_radio'], r['Uper'] / 2 / 200, 1e-12) and cerca(oz_in, 21.0, 0.1)))
    t1 = termografia(similar=12)[0]['prioridad']
    t2 = termografia(ambiente=45)[0]['prioridad']
    t3 = termografia(similar=2, ambiente=25)[0]['prioridad']
    ok.append(('termografía NETA: ΔT 12 °C entre similares → %s; 45 °C sobre ambiente → %s; 2 y 25 °C → %s' % (t1, t2, t3),
               (t1, t2, t3) == (3, 1, 2)))
    # Las plantillas CSV de la skill tienen que dar lo mismo que los datos de arriba
    carpeta = Path(__file__).resolve().parent.parent / 'plantilla'
    reg, am = carpeta / 'registro-fallas-ejemplo.csv', carpeta / 'amfe-ejemplo.csv'
    if reg.is_file() and am.is_file():
        iguales = (leer_registro(reg)[:3] == leer_registro(texto=REGISTRO_DEMO)[:3]
                   and [x['NPR'] for x in amfe(leer_filas(am))[0]['items']] == nprs)
        ok.append(('las plantillas CSV de la skill coinciden con el ejemplo', iguales))
    for nombre, bien in ok:
        print('  %s %s' % ('ok ' if bien else 'MAL', nombre))
    todo = all(b for _, b in ok)
    print('DEMO %s' % ('OK' if todo else 'FALLO'))
    return 0 if todo else 1


# ------------------------------------------------------------------------------------------ línea de comandos
def construir_parser():
    ap = argparse.ArgumentParser(prog='mantenimiento.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True, title='subcomandos', metavar='SUBCOMANDO')

    p = sp.add_parser('indicadores', help='MTBF, MTTR, MDT y disponibilidad inherente y operativa',
                      description='MTBF, MTTR, MDT, tasa de fallas y disponibilidad inherente (Ai) y operativa (Ao) de un período.')
    p.add_argument('--operacion', type=num, required=True, help='horas de funcionamiento en el período')
    p.add_argument('--registro', help='CSV o JSON con una fila por falla (columnas reparacion_h y espera_h): reemplaza a --fallas, --reparacion y --espera')
    p.add_argument('--fallas', type=int, help='cantidad de fallas')
    p.add_argument('--reparacion', type=num, help='horas de reparación activa, total del período')
    p.add_argument('--espera', type=num, default=0.0, help='horas de espera de repuestos, personal o permisos, total (0)')
    p.add_argument('--preventivos', type=int, default=0, help='intervenciones preventivas dentro del tiempo requerido (0)')
    p.add_argument('--t-preventivo', type=num, default=0.0, help='horas totales de esas intervenciones (0)')

    p = sp.add_parser('confiabilidad', help='R(t) con tasa de fallas constante; serie y paralelo',
                      description='Confiabilidad R(t) = e^(-t/MTBF) para fallas aleatorias (tasa constante).')
    p.add_argument('--t', type=num, required=True, help='tiempo de misión [h]')
    p.add_argument('--mtbf', type=num, help='MTBF [h]')
    p.add_argument('--objetivo', type=num, help='confiabilidad buscada (0,9 o 90): devuelve el tiempo')
    p.add_argument('--componentes', type=num, nargs='+', help='MTBF de cada componente [h]')
    p.add_argument('--conexion', choices=['serie', 'paralelo'], default='serie', help='cómo están conectados (serie)')

    p = sp.add_parser('oee', help='OEE = disponibilidad x rendimiento x calidad',
                      description='OEE de un período con las pérdidas en horas (definiciones de oee.com, origen en Nakajima).')
    p.add_argument('--planificado', type=num, required=True, help='tiempo planificado de producción [h] (turnos menos pausas)')
    p.add_argument('--paradas', type=num, required=True, help='paradas dentro del tiempo planificado [h]: fallas, cambios, ajustes')
    p.add_argument('--total', type=num, required=True, help='unidades producidas (buenas + malas)')
    p.add_argument('--buenas', type=num, help='unidades buenas a la primera')
    p.add_argument('--rechazos', type=num, help='unidades malas (descarte o retrabajo)')
    p.add_argument('--tasa', type=num, help='velocidad ideal [unidades/min]')
    p.add_argument('--ciclo', type=num, help='tiempo de ciclo ideal [s por unidad]')

    p = sp.add_parser('costo', help='costo directo, indirecto (parada) y total del mantenimiento',
                      description='Costo del mantenimiento de un período (valores en $, los que dé la empresa).')
    p.add_argument('--hh', type=num, default=0.0, help='horas-hombre de mantenimiento')
    p.add_argument('--costo-hh', type=num, default=0.0, help='costo de la hora-hombre [$/h]')
    p.add_argument('--materiales', type=num, default=0.0, help='repuestos y materiales [$]')
    p.add_argument('--terceros', type=num, default=0.0, help='servicios de terceros [$]')
    p.add_argument('--parada', type=num, default=0.0, help='horas de parada no planificada')
    p.add_argument('--costo-parada', type=num, default=0.0, help='costo de la hora parada [$/h] (margen perdido + costos que siguen)')
    p.add_argument('--unidades', type=num, help='unidades buenas del período (para el costo por unidad)')
    p.add_argument('--reposicion', type=num, help='valor de reposición del activo [$]')
    p.add_argument('--meses', type=num, default=1.0, help='meses que abarca el período (1)')

    p = sp.add_parser('pareto', help='Pareto de fallas desde un registro CSV o JSON',
                      description='Pareto: ordena, calcula el % acumulado y marca las causas vitales.')
    p.add_argument('archivo', nargs='?', help='CSV (; , o tab) o JSON; con registro de fallas suma reparacion_h + espera_h por equipo y causa')
    p.add_argument('--item', action='append', default=[], help='causa=valor (se puede repetir), en vez de archivo')
    p.add_argument('--agrupar', help='columnas para agrupar, separadas por coma (equipo,causa)')
    p.add_argument('--columna', help='columna numérica a sumar (valor, horas, costo...)')
    p.add_argument('--contar', action='store_true', help='contar filas (cantidad de fallas) en vez de sumar')
    p.add_argument('--umbral', type=num, default=80.0, help='%% acumulado que define las vitales (80)')
    p.add_argument('--unidad', default='h', help='unidad del valor para el encabezado (h)')

    p = sp.add_parser('amfe', help='AMFE: NPR = S x O x D, ordenado',
                      description='AMFE desde un CSV o JSON con columnas componente, modo, efecto, causa, control, S, O, D, '
                                  'accion y, si ya se definieron acciones, S2, O2 y D2.')
    p.add_argument('archivo', help='CSV (; , o tab) o JSON (lista de objetos)')
    p.add_argument('--umbral', type=int, help='NPR desde el que la empresa exige acción (no hay un valor universal)')

    p = sp.add_parser('relubricacion', help='método SKF: n·dm, límite, ajustes del intervalo y gramos de grasa',
                      description='Relubricación de rodamientos con grasa por el método del catálogo SKF.')
    p.add_argument('--d', type=num, required=True, metavar='MM', help='diámetro del agujero [mm]')
    p.add_argument('--D', type=num, required=True, metavar='MM', help='diámetro exterior [mm]')
    p.add_argument('--B', type=num, required=True, metavar='MM', help='ancho total [mm] (T en cónicos, H en axiales)')
    p.add_argument('--rpm', type=num, required=True, help='velocidad [rpm]')
    p.add_argument('--tipo', default='rigido-bolas', choices=sorted(SKF_BF), metavar='TIPO',
                   help='tipo de rodamiento (rigido-bolas): ' + ', '.join(sorted(SKF_BF)))
    p.add_argument('--cp', type=num, default=15.0, help='relación de carga C/P (15)')
    p.add_argument('--tf', type=num, help='intervalo leído en el diagrama de SKF [h], para aplicar los ajustes')
    p.add_argument('--temp', type=num, default=70.0, help='temperatura de funcionamiento del rodamiento [°C] (70)')
    p.add_argument('--eje-vertical', action='store_true', help='rodamiento en eje vertical')
    p.add_argument('--gira-exterior', action='store_true', help='gira el aro exterior (se usa n·D)')
    p.add_argument('--jaula-especial', action='store_true', help='rodillos cilíndricos con jaula J, JA, JB, MA, MB, ML, MP o PHA')
    p.add_argument('--horas-dia', type=num, help='horas de marcha por día, para pasar a días')

    p = sp.add_parser('vibracion', help='zona ISO 20816-3, ALARMA y DISPARO; frecuencias de rodamiento',
                      description='Severidad de vibración por velocidad eficaz (ISO 20816-3, máquinas de más de 15 kW).')
    p.add_argument('--v', type=num, help='velocidad eficaz de banda ancha [mm/s], la mayor radial')
    p.add_argument('--grupo', type=int, choices=[1, 2], help='grupo de la norma (si no, sale de --potencia o --altura)')
    p.add_argument('--potencia', type=num, help='potencia nominal [kW]')
    p.add_argument('--altura', type=num, help='altura de eje H de la máquina eléctrica [mm]')
    p.add_argument('--soporte', choices=['rigido', 'flexible'], default='rigido', help='clase de soporte (rigido)')
    p.add_argument('--base', type=num, help='valor de referencia de la misma máquina en buen estado [mm/s]')
    p.add_argument('--rpm', type=num, help='velocidad del eje [rpm] (frecuencias del rodamiento)')
    p.add_argument('--bolas', type=int, help='cantidad de elementos rodantes Z')
    p.add_argument('--dbola', type=num, help='diámetro del elemento rodante [mm]')
    p.add_argument('--dprim', type=num, help='diámetro primitivo dm [mm]')
    p.add_argument('--angulo', type=num, default=0.0, help='ángulo de contacto [°] (0)')

    p = sp.add_parser('alineacion', help='desalineación contra la guía de SKF',
                      description='Compara la desalineación medida con la guía de SKF (TKSA 20, anexo 3).')
    p.add_argument('--rpm', type=num, required=True, help='velocidad [rpm]')
    p.add_argument('--paralela', type=num, required=True, help='desplazamiento paralelo medido [mm]')
    p.add_argument('--angular', type=num, required=True, help='error angular medido [mm/100 mm]')

    p = sp.add_parser('balanceo', help='desbalance residual admisible (ISO 21940-11)',
                      description='Desbalance residual admisible de un rotor rígido para un grado de calidad G.')
    p.add_argument('--G', type=num, required=True, help='grado de calidad G [mm/s] (6,3; 2,5…)')
    p.add_argument('--masa', type=num, required=True, help='masa del rotor [kg]')
    p.add_argument('--rpm', type=num, required=True, help='velocidad máxima de servicio [rpm]')
    p.add_argument('--planos', type=int, default=1, help='planos de corrección (1)')
    p.add_argument('--radio', type=num, help='radio de corrección [mm], para pasar a gramos')

    p = sp.add_parser('termografia', help='acción por ΔT (ANSI/NETA MTS, tabla 100.18)',
                      description='Prioridad sugerida por la diferencia de temperatura en equipos eléctricos.')
    p.add_argument('--similar', type=num, help='ΔT contra un componente similar con carga similar [°C]')
    p.add_argument('--ambiente', type=num, help='ΔT del componente sobre el aire ambiente [°C]')

    sp.add_parser('demo', help='ejemplo resuelto de SKILL.md, verificado', description='Reproduce y verifica el ejemplo de SKILL.md.')
    return ap


def main(argv=None):
    a = construir_parser().parse_args(argv)
    try:
        if a.cmd == 'demo':
            return cmd_demo()
        if a.cmd == 'indicadores':
            if a.registro:
                nf, rep, esp, _ = leer_registro(a.registro)
            else:
                if a.fallas is None or a.reparacion is None:
                    raise ValueError('indicá --registro, o --fallas y --reparacion')
                nf, rep, esp = a.fallas, a.reparacion, a.espera
            _, L = indicadores(a.operacion, nf, rep, esp, a.preventivos, a.t_preventivo)
        elif a.cmd == 'confiabilidad':
            _, L = confiabilidad(a.t, a.mtbf, a.objetivo, a.componentes, a.conexion)
        elif a.cmd == 'oee':
            _, L = oee(a.planificado, a.paradas, a.total, a.buenas, a.rechazos, a.tasa, a.ciclo)
        elif a.cmd == 'costo':
            _, L = costo(a.hh, a.costo_hh, a.materiales, a.terceros, a.parada, a.costo_parada, a.unidades, a.reposicion, a.meses)
        elif a.cmd == 'pareto':
            if a.item:
                items = []
                for it in a.item:
                    nombre, sep, v = it.rpartition('=')
                    if not sep or not nombre:
                        raise ValueError('--item va como causa=valor: %r' % it)
                    items.append((nombre.strip(), num(v)))
            elif a.archivo:
                items = pareto_desde_filas(leer_filas(a.archivo), a.agrupar, a.columna, a.contar)
            else:
                raise ValueError('indicá un archivo o --item causa=valor')
            _, L = pareto(items, a.umbral, 'fallas' if a.contar else a.unidad)
        elif a.cmd == 'amfe':
            _, L = amfe(leer_filas(a.archivo), a.umbral)
        elif a.cmd == 'relubricacion':
            _, L = relubricacion(a.d, a.D, a.B, a.rpm, a.tipo, a.cp, a.tf, a.temp, a.eje_vertical, a.gira_exterior,
                                 a.jaula_especial, a.horas_dia)
        elif a.cmd == 'vibracion':
            _, L = vibracion(a.v, a.grupo, a.soporte, a.potencia, a.altura, a.base, a.rpm, a.bolas, a.dbola, a.dprim, a.angulo)
        elif a.cmd == 'alineacion':
            _, L = alineacion(a.rpm, a.paralela, a.angular)
        elif a.cmd == 'balanceo':
            _, L = balanceo(a.G, a.masa, a.rpm, a.planos, a.radio)
        else:
            _, L = termografia(a.similar, a.ambiente)
    except (ValueError, KeyError, json.JSONDecodeError, argparse.ArgumentTypeError) as ex:
        print('mantenimiento.py: %s' % ex, file=sys.stderr)
        return 2
    print('\n'.join(L))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
