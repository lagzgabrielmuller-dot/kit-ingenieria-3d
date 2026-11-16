#!/usr/bin/env python3
"""organizacion.py - organización industrial y evaluación de proyectos (solo biblioteca estándar).

Cada comando imprime fórmula, reemplazo y resultado con coma decimal, listo para una memoria de cálculo.
En la línea de comandos los decimales van con punto y las listas con coma (o con punto y coma si se
usa coma decimal: 1,20;1,25). Si la lista empieza con un negativo, poner =: --flujos=-70000,26800.

  equilibrio --cf CF --precio p --cv cv [--cantidad Q] [--utilidad U]
        margen de contribución, punto de equilibrio en unidades y en ventas, costo unitario
  amortizacion --valor V0 --vida n [--residual VR]         amortización lineal y valor de libro
  van --flujos=F0,F1,...,Fn --tasa % [--moneda texto]       VAN, TIR, recupero simple y descontado, B/C
  inflacion (--nominal % | --real %) --inflacion %          tasa real o nominal (Fisher)
  inflacion --flujos=F0,...,Fn (--inflacion % | --inflaciones %,%,... | --ipc I0,I1,...)
        pasa flujos en moneda corriente a moneda constante del período 0
  tiempos --obs t1,t2,... --valoracion % [--suplementos %,%,...] [--turno 480] [--confianza 95] [--precision 5]
        tiempo normal, tiempo estándar, producción por turno y observaciones necesarias
  muestreo (--p % | --ocurrencias k --total N) [--error %] [--confianza 95]
        muestreo del trabajo: proporción, intervalo y observaciones necesarias
  capacidad --tiempos t1,t2,... --disponible T [--maquinas 1,2,...] [--nombres a,b,...] [--demanda D]
        capacidad por estación, cuello de botella y utilización
  balanceo ARCHIVO (--ciclo C | --disponible T --demanda D) [--regla sucesoras|peso|tiempo]
        balanceo de línea: tiempo de ciclo, estaciones mínimas, asignación, eficiencia
  cpm ARCHIVO [--plazo T] [--probabilidad 0.95] [--gantt]
        fechas tempranas y tardías, holguras, camino crítico; PERT si hay tiempos a, m y b
  calidad (ARCHIVO | --datos "x x x; x x x") [--lei LEI] [--les LES]
        gráficos X̄-R, reglas de Western Electric, Cp, Cpk, Pp y Ppk
  pareto (ARCHIVO | --categorias a,b,c --cantidades 10,5,3) [--corte 80]
  demo  reproduce el ejemplo resuelto del SKILL.md y lo compara con los valores esperados

Archivos de entrada: CSV (separado por coma, punto y coma o tabulador) o JSON.
`balanceo --ejemplo`, `cpm --ejemplo` y `calidad --ejemplo` muestran un archivo de muestra.
"""
import argparse
import csv
import io
import json
import math
import re
import sys
import unicodedata
from statistics import NormalDist

# Textos fijos de argparse en español (argparse los pide a gettext; lo que no está queda como viene).
_ES = {
    'usage: ': 'uso: ',
    'positional arguments': 'argumentos',
    'optional arguments': 'opciones',
    'options': 'opciones',
    'show this help message and exit': 'muestra esta ayuda y termina',
    'the following arguments are required: %s': 'faltan estos argumentos: %s',
    'argument %(argument_name)s: %(message)s': 'argumento %(argument_name)s: %(message)s',
    'expected one argument': 'falta el valor',
    'unrecognized arguments: %s': 'argumentos desconocidos: %s',
    'invalid %(type)s value: %(value)r': 'valor inválido: %(value)r',
    'invalid choice: %(value)r (choose from %(choices)s)': 'opción inválida: %(value)r (elegir entre %(choices)s)',
    'not allowed with argument %s': 'no va junto con %s',
}
argparse._ = lambda texto: _ES.get(texto, texto)

# ------------------------------------------------------------------------------------------ datos con fuente
# Factores para los gráficos X̄ y R (A2, D3, D4) según el tamaño del subgrupo n:
# NIST/SEMATECH e-Handbook of Statistical Methods, sección 6.3.2.1. El demo los recalcula.
CONSTANTES_XR = {2: (1.880, 0.0, 3.267), 3: (1.023, 0.0, 2.575), 4: (0.729, 0.0, 2.282), 5: (0.577, 0.0, 2.115),
                 6: (0.483, 0.0, 2.004), 7: (0.419, 0.076, 1.924), 8: (0.373, 0.136, 1.864),
                 9: (0.337, 0.184, 1.816), 10: (0.308, 0.223, 1.777)}
# d2 = valor medio del rango de n valores normales en unidades de σ (σ̂ = R̄/d2). Cumple A2 = 3/(d2·√n)
# con la tabla anterior y el demo lo recalcula por integración numérica.
D2 = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078}
EPS = 1e-9


# ------------------------------------------------------------------------------------------ formato
def n(x, d=2):
    if abs(x) < 0.5 * 10 ** (-d):
        x = 0.0
    return ('%.*f' % (d, x)).replace('.', ',')


def miles(x, d=0):
    """Número con espacio como separador de miles (SI) y coma decimal: 37 956,54."""
    if abs(x) < 0.5 * 10 ** (-d):
        x = 0.0
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


def pct(x, d=2):
    return n(100 * x, d) + ' %'


def numero(texto):
    t = str(texto).strip().replace(' ', '')
    if ',' in t and '.' not in t:
        t = t.replace(',', '.')
    return float(t)


def lista(texto, nombre='lista'):
    """'1.2,1.3 1.4' o, con coma decimal, '1,2;1,3' → [1.2, 1.3, 1.4]."""
    if isinstance(texto, (list, tuple)):
        return [float(x) for x in texto]
    sep = r'[;\s]+' if ';' in texto else r'[,\s]+'
    partes = [p for p in re.split(sep, texto.strip()) if p]
    try:
        return [numero(p) for p in partes]
    except ValueError:
        raise ValueError('%s: «%s» no es una lista de números (punto decimal y coma entre valores, '
                         'o coma decimal y punto y coma entre valores)' % (nombre, texto))


def phi(z):
    return NormalDist().cdf(z)


# ------------------------------------------------------------------------------------------ costos
def equilibrio(CF, p, cv, Q=None, U=None):
    if p <= cv:
        raise ValueError('el precio (%s) no supera el costo variable unitario (%s): no hay punto de equilibrio' % (n(p), n(cv)))
    if CF < 0:
        raise ValueError('los costos fijos no pueden ser negativos')
    mc = p - cv
    rc = mc / p
    Qe = CF / mc
    Ve = CF / rc
    L = ['Margen de contribución unitario: mc = p − cv = %s − %s = %s por unidad; razón de contribución mc/p = %s'
         % (n(p), n(cv), n(mc), pct(rc, 1)),
         'Punto de equilibrio en unidades: Qe = CF/(p − cv) = %s/%s = %s unidades por período%s'
         % (miles(CF, 2), n(mc), miles(Qe, 1), '' if abs(Qe - round(Qe)) < EPS else ' → vender %s' % miles(math.ceil(Qe))),
         'Punto de equilibrio en ventas: Ve = CF/(1 − cv/p) = %s/%s = %s (igual a Qe·p = %s)'
         % (miles(CF, 2), n(rc, 4), miles(Ve, 2), miles(Qe * p, 2))]
    r = {'mc': mc, 'rc': rc, 'Qe': Qe, 'Ve': Ve}
    if Q:
        ct = CF + cv * Q
        Ut = Q * mc - CF
        cu = cv + CF / Q
        ms = (Q - Qe) / Q
        r.update({'U': Ut, 'cu': cu, 'ms': ms, 'CT': ct})
        L.append('Con Q = %s unidades: ventas Q·p = %s; costo total CF + cv·Q = %s; utilidad U = Q·mc − CF = %s'
                 % (miles(Q), miles(Q * p, 2), miles(ct, 2), miles(Ut, 2)))
        L.append('Costo unitario total: cu = cv + CF/Q = %s + %s/%s = %s; margen de seguridad (Q − Qe)/Q = %s'
                 % (n(cv), miles(CF, 2), miles(Q), n(cu), pct(ms, 1)))
        if Ut < 0:
            L.append('AVISO: con esa cantidad el proyecto pierde plata; hace falta vender al menos Qe.')
    if U is not None:
        Qu = (CF + U) / mc
        r['Q_U'] = Qu
        L.append('Cantidad para una utilidad de %s: Q = (CF + U)/mc = (%s + %s)/%s = %s unidades'
                 % (miles(U, 2), miles(CF, 2), miles(U, 2), n(mc), miles(Qu, 1)))
    L.append('CF incluye las amortizaciones. Con varios productos, usar el margen de contribución promedio ponderado por la mezcla de ventas.')
    return r, L


def amortizacion(V0, vida, VR=0.0):
    if V0 <= 0 or vida < 1:
        raise ValueError('hacen falta un valor de origen positivo y una vida útil de al menos 1 año')
    if not 0 <= VR < V0:
        raise ValueError('el valor residual tiene que estar entre 0 y el valor de origen')
    A = (V0 - VR) / vida
    L = ['Amortización lineal: A = (V0 − VR)/n = (%s − %s)/%d = %s por año (%s del valor amortizable por año)'
         % (miles(V0, 2), miles(VR, 2), vida, miles(A, 2), pct(1 / vida, 2)),
         '  Año    Amortización      Acumulada   Valor de libro']
    libro = []
    for k in range(1, vida + 1):
        vl = V0 - A * k
        libro.append(vl)
        L.append('%5d %15s %14s %16s' % (k, miles(A, 2), miles(A * k, 2), miles(vl, 2)))
    L.append('La amortización no es una salida de caja: baja la utilidad y el impuesto (ahorro t·A por año). '
             'Otros métodos: suma de los dígitos de los años, saldo decreciente y por unidades producidas u horas de uso.')
    return {'A': A, 'libro': libro}, L


# ------------------------------------------------------------------------------------------ evaluación de proyectos
def vna(F, i):
    return sum(f / (1 + i) ** t for t, f in enumerate(F))


def dvna(F, i):
    return sum(-t * f / (1 + i) ** (t + 1) for t, f in enumerate(F))


def tir_biseccion(F, lo, hi, tol=1e-13):
    flo = vna(F, lo)
    for _ in range(400):
        mid = (lo + hi) / 2
        fm = vna(F, mid)
        if (fm < 0) == (flo < 0):
            lo, flo = mid, fm
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2


def tirs(F):
    """Todas las tasas entre −99 % y 1000 % donde el VAN cambia de signo, refinadas por bisección."""
    a, b, pasos = math.log(0.01), math.log(11.0), 4000
    rs = [math.exp(a + k * (b - a) / pasos) - 1 for k in range(pasos + 1)]
    vals = [vna(F, r) for r in rs]
    raices = []
    for k in range(pasos):
        if vals[k] == 0:
            raices.append(rs[k])
        elif (vals[k] < 0) != (vals[k + 1] < 0):
            raices.append(tir_biseccion(F, rs[k], rs[k + 1]))
    return raices


def tir_newton(F, r0=0.1):
    r = r0
    for it in range(1, 101):
        d = dvna(F, r)
        if d == 0:
            return None, it
        r1 = r - vna(F, r) / d
        if r1 <= -0.99:
            r1 = (r - 0.99) / 2
        if abs(r1 - r) < 1e-13:
            return r1, it
        r = r1
    return None, 100


def recupero(valores):
    """Períodos hasta que el acumulado llega a cero, interpolando dentro del período; None si no se recupera."""
    acum = 0.0
    for t, v in enumerate(valores):
        previo = acum
        acum += v
        if acum >= -EPS and t == 0:
            return 0.0
        if acum >= -EPS and previo < 0:
            return t - 1 + (-previo) / v
    return None


def cambios_de_signo(F):
    s = [f for f in F if abs(f) > EPS]
    return sum(1 for x, y in zip(s, s[1:]) if (x < 0) != (y < 0))


def evaluar(F, tasa, moneda='la moneda de los flujos'):
    if len(F) < 2:
        raise ValueError('hacen falta al menos dos flujos (año 0 y año 1)')
    if len(F) > 101:
        raise ValueError('el horizonte máximo es de 100 períodos')
    i = tasa / 100
    if i <= -1:
        raise ValueError('la tasa tiene que ser mayor que −100 %')
    VA = [f / (1 + i) ** t for t, f in enumerate(F)]
    VAN = sum(VA)
    L = ['Flujos en %s; tasa de descuento i = %s por período. VAN = Σ Ft/(1 + i)^t' % (moneda, pct(i, 2)),
         '  Año           Flujo   1/(1+i)^t    Valor actual       Acumulado   Acum. descontado']
    acum = acum_d = 0.0
    for t, (f, va) in enumerate(zip(F, VA)):
        acum += f
        acum_d += va
        L.append('%5d %15s %11s %15s %15s %18s' % (t, miles(f, 2), n(1 / (1 + i) ** t, 4), miles(va, 2), miles(acum, 2), miles(acum_d, 2)))
    L.append('VAN = %s' % miles(VAN, 2))
    r = {'VAN': VAN, 'VA': VA}
    raices = tirs(F)
    cs = cambios_de_signo(F)
    r['TIRs'] = raices
    if len(raices) == 1:
        tir = raices[0]
        tn, it = tir_newton(F, 0.1)
        r.update({'TIR': tir, 'TIR_newton': tn})
        L.append('TIR (tasa que anula el VAN, por bisección) = %s; por Newton desde 10 %%: %s en %d iteraciones; VAN a la TIR = %s'
                 % (pct(tir, 3), pct(tn, 3) if tn is not None else 'no converge', it, miles(vna(F, tir), 4)))
    elif raices:
        r['TIR'] = None
        L.append('AVISO: el flujo cambia %d veces de signo y hay %d TIR (%s): la TIR no sirve para decidir; usar el VAN.'
                 % (cs, len(raices), ', '.join(pct(x, 2) for x in raices)))
    else:
        r['TIR'] = None
        L.append('No hay TIR entre −99 % y 1000 % (el VAN no cambia de signo).')
    prs, prd = recupero(F), recupero(VA)
    r.update({'PRs': prs, 'PRd': prd})
    L.append('Período de recupero simple: %s; descontado (con los valores actuales): %s'
             % ('%s períodos' % n(prs, 2) if prs is not None else 'no se recupera en el horizonte',
                '%s períodos' % n(prd, 2) if prd is not None else 'no se recupera en el horizonte'))
    pos = sum(v for v in VA if v > 0)
    neg = -sum(v for v in VA if v < 0)
    if neg > 0:
        r['BC'] = pos / neg
        L.append('Relación beneficio/costo (con flujos netos) = VA de los flujos positivos / VA de los negativos = %s/%s = %s'
                 % (miles(pos, 2), miles(neg, 2), n(pos / neg, 3)))
    if VAN > 0:
        L.append('Decisión: VAN > 0%s: a la tasa del %s el proyecto es rentable (gana más que la alternativa).'
                 % (' y TIR > i' if r.get('TIR') is not None else '', pct(i, 2)))
    else:
        L.append('Decisión: VAN ≤ 0: a la tasa del %s el proyecto no cubre el costo de oportunidad.' % pct(i, 2))
    L.append('Aclarar en el informe la moneda (dólares o moneda constante de un año base) y que la tasa es real si los flujos son constantes.')
    return r, L


def tasas_fisher(inflacion, nominal=None, real=None):
    pi = inflacion / 100
    if pi <= -1:
        raise ValueError('la inflación tiene que ser mayor que −100 %')
    if (nominal is None) == (real is None):
        raise ValueError('indicá --nominal o --real (una de las dos)')
    if nominal is not None:
        i = nominal / 100
        r = (1 + i) / (1 + pi) - 1
        L = ['Tasa real (Fisher): r = (1 + i)/(1 + π) − 1 = (1 + %s)/(1 + %s) − 1 = %s'
             % (n(i, 4), n(pi, 4), pct(r, 2))]
    else:
        r = real / 100
        i = (1 + r) * (1 + pi) - 1
        L = ['Tasa nominal (Fisher): i = (1 + r)·(1 + π) − 1 = (1 + %s)·(1 + %s) − 1 = %s'
             % (n(r, 4), n(pi, 4), pct(i, 2))]
    if nominal is not None:
        L.append('La aproximación r ≈ i − π daría %s: %s puntos de diferencia; con inflación alta usar la fórmula exacta.'
                 % (pct(i - pi, 2), n(100 * abs(i - pi - r), 2)))
    else:
        L.append('La aproximación i ≈ r + π daría %s: %s puntos de diferencia; con inflación alta usar la fórmula exacta.'
                 % (pct(r + pi, 2), n(100 * abs(r + pi - i), 2)))
    L.append('Flujos en moneda corriente → tasa nominal; flujos en moneda constante o en dólares constantes → tasa real.')
    return {'i': i, 'r': r}, L


def deflactar(F, inflacion=None, inflaciones=None, ipc=None):
    T = len(F)
    if ipc is not None:
        if len(ipc) != T:
            raise ValueError('--ipc: hace falta un índice por cada flujo (del período 0 al %d)' % (T - 1))
        fac = [ipc[0] / x for x in ipc]
        como = 'Ft·IPC0/IPCt'
    else:
        if inflaciones is None:
            if inflacion is None:
                raise ValueError('indicá --inflacion, --inflaciones o --ipc')
            inflaciones = [inflacion] * (T - 1)
        if len(inflaciones) != T - 1:
            raise ValueError('--inflaciones: hace falta una tasa por período (%d)' % (T - 1))
        fac, acum = [1.0], 1.0
        for x in inflaciones:
            acum *= 1 + x / 100
            fac.append(1 / acum)
        como = 'Ft/Π(1 + πk)'
    C = [f * k for f, k in zip(F, fac)]
    L = ['Moneda constante del período 0: Ct = %s' % como, '  Año        Corriente     Factor       Constante']
    for t, (f, k, c) in enumerate(zip(F, fac, C)):
        L.append('%5d %16s %10s %15s' % (t, miles(f, 2), n(k, 4), miles(c, 2)))
    L.append('Los flujos en moneda constante se descuentan con la tasa real. El IPC oficial lo publica el INDEC.')
    return {'constantes': C}, L


# ------------------------------------------------------------------------------------------ estadística
def _betacf(a, b, x):
    MAXIT, PREC, MINIMO = 300, 3e-15, 1e-300
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > MINIMO else MINIMO)
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        d = d if abs(d) > MINIMO else MINIMO
        c = 1 + aa / c
        c = c if abs(c) > MINIMO else MINIMO
        d = 1 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        d = d if abs(d) > MINIMO else MINIMO
        c = 1 + aa / c
        c = c if abs(c) > MINIMO else MINIMO
        d = 1 / d
        de = d * c
        h *= de
        if abs(de - 1) < PREC:
            break
    return h


def beta_incompleta(a, b, x):
    """Función beta incompleta regularizada I_x(a, b) por fracción continua."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_cdf(t, gl):
    p = 0.5 * beta_incompleta(gl / 2, 0.5, gl / (gl + t * t))
    return 1 - p if t > 0 else p


def t_inv(p, gl):
    """Cuantil de la t de Student (por bisección sobre la función de distribución)."""
    lo, hi = -1e4, 1e4
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_cdf(mid, gl) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def z_bilateral(confianza):
    if not 50 <= confianza < 100:
        raise ValueError('la confianza va en %, entre 50 y 99,9')
    return NormalDist().inv_cdf(1 - (1 - confianza / 100) / 2)


# ------------------------------------------------------------------------------------------ métodos y tiempos
def tiempos(obs, valoracion, suplementos=(), turno=None, confianza=95.0, precision=5.0, modo='normal', unidad='min'):
    N = len(obs)
    if N < 1 or any(x <= 0 for x in obs):
        raise ValueError('--obs: hacen falta tiempos observados positivos')
    TO = sum(obs) / N
    if len(valoracion) == 1:
        V = valoracion[0]
        TN = TO * V / 100
        L = ['Tiempo observado medio: TO = Σt/N = %s/%d = %s %s' % (n(sum(obs), 3), N, n(TO, 4), unidad),
             'Tiempo normal (básico): TN = TO·V/100 = %s·%s/100 = %s %s (V = 100 %% es el ritmo normal)'
             % (n(TO, 4), n(V, 0), n(TN, 4), unidad)]
    elif len(valoracion) == N:
        TN = sum(o * v / 100 for o, v in zip(obs, valoracion)) / N
        L = ['Tiempo observado medio: TO = %s %s' % (n(TO, 4), unidad),
             'Tiempo normal con una valoración por ciclo: TN = Σ(ti·Vi/100)/N = %s %s' % (n(TN, 4), unidad)]
    else:
        raise ValueError('--valoracion: un valor para todo el estudio o uno por observación (%d)' % N)
    S = sum(suplementos) / 100
    if modo == 'normal':
        TS = TN * (1 + S)
        L.append('Suplementos: S = %s%s del tiempo normal; tiempo estándar TS = TN·(1 + S) = %s·%s = %s %s'
                 % (' + '.join(n(s, 0) for s in suplementos) + ' = ' if len(suplementos) > 1 else '', pct(S, 0), n(TN, 4), n(1 + S, 2), n(TS, 4), unidad))
    else:
        if S >= 1:
            raise ValueError('con suplementos sobre la jornada, S tiene que ser menor que 100 %')
        TS = TN / (1 - S)
        L.append('Suplementos sobre la jornada: S = %s; TS = TN/(1 − S) = %s/%s = %s %s' % (pct(S, 0), n(TN, 4), n(1 - S, 2), n(TS, 4), unidad))
    r = {'TO': TO, 'TN': TN, 'TS': TS, 'S': S}
    if turno:
        piezas = math.floor(turno / TS + EPS)
        r['piezas'] = piezas
        L.append('Producción por turno: %s/%s = %s → %d piezas (%s piezas por hora si los tiempos están en min)'
                 % (n(turno, 0), n(TS, 4), n(turno / TS, 2), piezas, n(60 / TS, 2)))
    if N >= 2:
        s = math.sqrt(sum((x - TO) ** 2 for x in obs) / (N - 1))
        t = t_inv(1 - (1 - confianza / 100) / 2, N - 1)
        k = precision / 100
        nreq = (t * s / (k * TO)) ** 2
        r.update({'s': s, 't': t, 'n_req': nreq})
        L.append('Observaciones necesarias (Niebel y Freivalds): n = (t·s/(k·x̄))² = (%s·%s/(%s·%s))² = %s → %d; %s'
                 % (n(t, 3), n(s, 4), n(k, 2), n(TO, 4), n(nreq, 2), math.ceil(nreq - EPS),
                    'las %d tomadas alcanzan' % N if N >= math.ceil(nreq - EPS) else 'faltan %d' % (math.ceil(nreq - EPS) - N)))
        L.append('  (t de Student con %d grados de libertad y %s %% de confianza; k = ±%s %% de la media)' % (N - 1, n(confianza, 0), n(precision, 0)))
    L.append('Los suplementos salen de la tabla de la OIT (references/metodos-y-tiempos.md) o de la que use la empresa.')
    return r, L


def muestreo(p=None, ocurrencias=None, total=None, error=None, confianza=95.0):
    if p is None:
        if not ocurrencias or not total or not 0 < ocurrencias <= total:
            raise ValueError('indicá --p o --ocurrencias y --total (0 < ocurrencias ≤ total)')
        p = ocurrencias / total
    else:
        p = p / 100
    if not 0 < p < 1:
        raise ValueError('la proporción tiene que estar entre 0 y 100 %')
    z = z_bilateral(confianza)
    r = {'p': p, 'z': z}
    L = ['Proporción observada: p = %s%s' % (pct(p, 2), ' (%d de %d observaciones)' % (ocurrencias, total) if ocurrencias else '')]
    if total:
        semi = z * math.sqrt(p * (1 - p) / total)
        r['semi'] = semi
        L.append('Intervalo con %s %% de confianza: p ± z·√(p·(1 − p)/N) = %s ± %s·%s = %s a %s'
                 % (n(confianza, 0), pct(p, 2), n(z, 3), n(math.sqrt(p * (1 - p) / total), 4), pct(p - semi, 2), pct(p + semi, 2)))
    if error:
        e = error / 100
        nreq = z ** 2 * p * (1 - p) / e ** 2
        r['n_req'] = nreq
        L.append('Observaciones necesarias para ±%s: N = z²·p·(1 − p)/e² = %s²·%s·%s/%s² = %s → %d'
                 % (pct(e, 1), n(z, 3), n(p, 3), n(1 - p, 3), n(e, 3), n(nreq, 1), math.ceil(nreq - EPS)))
    L.append('Las observaciones se toman en momentos al azar a lo largo de varios turnos; si p cambia mucho, recalcular N.')
    return r, L


# ------------------------------------------------------------------------------------------ capacidad y balanceo
def capacidad(tiempos_u, disponible, maquinas=None, nombres=None, demanda=None, rendimiento=1.0):
    k = len(tiempos_u)
    maquinas = maquinas or [1] * k
    nombres = nombres or ['E%d' % (j + 1) for j in range(k)]
    if len(maquinas) != k or len(nombres) != k:
        raise ValueError('--maquinas y --nombres tienen que tener un valor por estación (%d)' % k)
    if any(t <= 0 for t in tiempos_u) or any(m <= 0 for m in maquinas) or not 0 < rendimiento <= 1:
        raise ValueError('tiempos y máquinas positivos; rendimiento entre 0 y 1')
    caps = [m * disponible * rendimiento / t for t, m in zip(tiempos_u, maquinas)]
    L = ['Capacidad de cada estación: C = m·T·η/t (T = %s por período, η = %s)' % (n(disponible, 0), n(rendimiento, 2))]
    for nom, t, m, c in zip(nombres, tiempos_u, maquinas, caps):
        L.append('  %-14s %d·%s·%s/%s = %s u por período' % (nom, m, n(disponible, 0), n(rendimiento, 2), n(t, 3), n(c, 1)))
    orden = sorted(range(k), key=lambda j: caps[j])
    cb = orden[0]
    r = {'caps': caps, 'cuello': nombres[cb], 'sistema': caps[cb]}
    L.append('Cuello de botella: %s (%s u por período): fija la capacidad de toda la línea.' % (nombres[cb], n(caps[cb], 1)))
    if k > 1:
        r['siguiente'] = nombres[orden[1]]
        L.append('Si se agranda el cuello de botella, el próximo es %s (%s u por período).' % (nombres[orden[1]], n(caps[orden[1]], 1)))
    if demanda:
        prod = min(demanda, caps[cb])
        utils = [prod * t / (m * disponible) for t, m in zip(tiempos_u, maquinas)]
        r['util'] = utils
        L.append('Utilización con %s u por período: U = Q·t/(m·T): %s'
                 % (n(prod, 0), '; '.join('%s %s' % (nom, pct(u, 1)) for nom, u in zip(nombres, utils))))
        if demanda > caps[cb] + EPS:
            falta = demanda - caps[cb]
            r['falta'] = falta
            L.append('NO ALCANZA: faltan %s u por período; en %s hacen falta %s más de trabajo por período (en la unidad de los tiempos) '
                     '(otra máquina, horas extra, otro turno o mejorar el método en el cuello de botella).'
                     % (n(falta, 1), nombres[cb], n(falta * tiempos_u[cb] / (maquinas[cb] * rendimiento), 1)))
    return r, L


def _normalizar(texto):
    t = unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[\s_\-.()\[\]]+', '', t)


SINONIMOS = {
    'id': ('id', 'actividad', 'tarea', 'codigo', 'cod', 'nombre', 'elemento'),
    'duracion': ('duracion', 'tiempo', 'd', 't', 'te', 'dias', 'semanas', 'min', 's', 'seg', 'segundos', 'minutos'),
    'a': ('a', 'optimista', 'to'),
    'm': ('m', 'probable', 'masprobable', 'tm'),
    'b': ('b', 'pesimista', 'tp'),
    'precedentes': ('precedentes', 'precedente', 'predecesoras', 'predecesores', 'precedencias', 'precedencia',
                    'antecesoras', 'anteriores', 'depende', 'dependencias', 'requiere'),
    'descripcion': ('descripcion', 'detalle'),
}


def _clave(encabezado):
    e = _normalizar(encabezado)
    for clave, nombres in SINONIMOS.items():
        if e in nombres:
            return clave
    return e


def _texto_archivo(ruta):
    try:
        with open(ruta, encoding='utf-8-sig') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(ruta, encoding='latin-1') as f:
            return f.read()
    except OSError as ex:
        raise ValueError('no se puede leer %s: %s' % (ruta, ex.strerror))


def _filas_csv(texto):
    primera = texto.strip().splitlines()[0] if texto.strip() else ''
    delim = '\t' if '\t' in primera else (';' if ';' in primera else ',')
    return [f for f in csv.reader(io.StringIO(texto), delimiter=delim) if any(c.strip() for c in f)]


def leer_actividades(ruta=None, texto=None):
    """Actividades o tareas desde CSV (con encabezado) o JSON: lista de {id, duracion | a, m, b, precedentes}."""
    texto = texto if texto is not None else _texto_archivo(ruta)
    if texto.lstrip().startswith(('[', '{')):
        datos = json.loads(texto)
        if isinstance(datos, dict):
            datos = next((datos[k] for k in ('actividades', 'tareas', 'datos') if k in datos), None)
        if not isinstance(datos, list):
            raise ValueError('el JSON tiene que ser una lista de actividades o {"actividades": [...]}')
        filas = [{_clave(k): v for k, v in d.items()} for d in datos]
    else:
        crudas = _filas_csv(texto)
        if len(crudas) < 2:
            raise ValueError('el CSV necesita un encabezado y al menos una fila')
        enc = [_clave(c) for c in crudas[0]]
        filas = [dict(zip(enc, f)) for f in crudas[1:]]
    acts = []
    for k, f in enumerate(filas, 1):
        ident = str(f.get('id', '')).strip()
        if not ident:
            raise ValueError('fila %d: falta el código de la actividad' % k)
        prec = f.get('precedentes', '')
        if isinstance(prec, (list, tuple)):
            prec = [str(p).strip() for p in prec]
        else:
            prec = [p for p in re.split(r'[\s,;|/+]+', str(prec).strip()) if p and p not in ('-', '—', '–', 'ninguna', 'ninguno')]
        act = {'id': ident, 'prec': prec, 'desc': str(f.get('descripcion', '')).strip()}
        try:
            if all(str(f.get(x, '')).strip() != '' for x in ('a', 'm', 'b')):
                a, m, b = (numero(f[x]) for x in ('a', 'm', 'b'))
                if not 0 <= a <= m <= b:
                    raise ValueError('fila %d (%s): tiene que ser 0 ≤ a ≤ m ≤ b' % (k, ident))
                act.update({'a': a, 'm': m, 'b': b, 'd': (a + 4 * m + b) / 6, 'var': ((b - a) / 6) ** 2})
            elif str(f.get('duracion', '')).strip() != '':
                act.update({'d': numero(f['duracion']), 'var': 0.0})
            else:
                raise ValueError('fila %d (%s): falta la duración (o los tiempos a, m y b)' % (k, ident))
        except (TypeError, ValueError) as ex:
            raise ValueError(str(ex) if 'fila' in str(ex) else 'fila %d (%s): número inválido' % (k, ident))
        if act['d'] < 0:
            raise ValueError('fila %d (%s): duración negativa' % (k, ident))
        acts.append(act)
    ids = [a['id'] for a in acts]
    repetidas = sorted({x for x in ids if ids.count(x) > 1})
    if repetidas:
        raise ValueError('códigos repetidos: %s' % ', '.join(repetidas))
    for a in acts:
        faltan = [p for p in a['prec'] if p not in ids]
        if faltan:
            raise ValueError('%s tiene precedentes que no existen: %s' % (a['id'], ', '.join(faltan)))
    return acts


def orden_topologico(acts):
    prec = {a['id']: list(a['prec']) for a in acts}
    pend = {k: len(v) for k, v in prec.items()}
    suc = {k: [] for k in prec}
    for k, v in prec.items():
        for p in v:
            suc[p].append(k)
    cola = [a['id'] for a in acts if pend[a['id']] == 0]
    orden = []
    while cola:
        k = cola.pop(0)
        orden.append(k)
        for j in suc[k]:
            pend[j] -= 1
            if pend[j] == 0:
                cola.append(j)
    if len(orden) != len(acts):
        raise ValueError('las precedencias forman un ciclo: %s' % ', '.join(k for k in prec if k not in orden))
    return orden, suc


def balanceo(tareas, ciclo, regla='sucesoras'):
    orden, suc = orden_topologico(tareas)
    t = {a['id']: a['d'] for a in tareas}
    prec = {a['id']: a['prec'] for a in tareas}
    pos = {a['id']: k for k, a in enumerate(tareas)}
    if ciclo <= 0:
        raise ValueError('el tiempo de ciclo tiene que ser positivo')
    largas = [k for k in t if t[k] > ciclo + EPS]
    if largas:
        raise ValueError('%s dura más que el ciclo (%s): dividir la tarea o poner estaciones en paralelo'
                         % (', '.join(largas), n(ciclo, 2)))
    desc = {}
    for k in reversed(orden):
        s = set()
        for j in suc[k]:
            s |= {j} | desc[j]
        desc[k] = s
    clave = {'sucesoras': lambda k: len(desc[k]),
             'peso': lambda k: t[k] + sum(t[j] for j in desc[k]),
             'tiempo': lambda k: t[k]}[regla]
    total = sum(t.values())
    Nt = math.ceil(total / ciclo - EPS)
    asignadas, estaciones = set(), []
    while len(asignadas) < len(t):
        carga, est = 0.0, []
        while True:
            cand = [k for k in t if k not in asignadas and all(p in asignadas for p in prec[k]) and carga + t[k] <= ciclo + EPS]
            if not cand:
                break
            k = max(cand, key=lambda k: (clave(k), t[k], -pos[k]))
            est.append(k)
            asignadas.add(k)
            carga += t[k]
        estaciones.append((est, carga))
    N = len(estaciones)
    E = total / (N * ciclo)
    nombre_regla = {'sucesoras': 'mayor cantidad de tareas sucesoras', 'peso': 'mayor peso posicional',
                    'tiempo': 'mayor tiempo'}[regla]
    L = ['Suma de tiempos Σt = %s; tiempo de ciclo C = %s' % (n(total, 2), n(ciclo, 2)),
         'Estaciones mínimas teóricas: Nt = Σt/C = %s/%s = %s → %d' % (n(total, 2), n(ciclo, 2), n(total / ciclo, 2), Nt),
         'Asignación por la regla de %s (desempate: mayor tiempo):' % nombre_regla]
    for j, (est, carga) in enumerate(estaciones, 1):
        L.append('  Estación %d: %-24s tiempo %s, ocioso %s' % (j, ', '.join(est), n(carga, 2), n(ciclo - carga, 2)))
    L.append('Eficiencia: E = Σt/(N·C) = %s/(%d·%s) = %s; retraso del balance 1 − E = %s; tiempo ocioso N·C − Σt = %s por ciclo'
             % (n(total, 2), N, n(ciclo, 2), pct(E, 1), pct(1 - E, 1), n(N * ciclo - total, 2)))
    if N > Nt:
        L.append('Con %d estaciones no alcanza el mínimo teórico (%d): probar otra regla (--regla) o revisar si las precedencias lo impiden.' % (N, Nt))
    L.append('La regla es heurística: no garantiza el mínimo de estaciones. Producción con este ciclo: 1 unidad cada %s.' % n(ciclo, 2))
    return {'C': ciclo, 'Nt': Nt, 'N': N, 'E': E, 'estaciones': estaciones}, L


# ------------------------------------------------------------------------------------------ CPM y PERT
def cpm(acts, plazo=None, probabilidad=None, gantt=False, unidad='días'):
    orden, suc = orden_topologico(acts)
    A = {a['id']: a for a in acts}
    ES, EF, LS, LF = {}, {}, {}, {}
    for k in orden:
        ES[k] = max((EF[p] for p in A[k]['prec']), default=0.0)
        EF[k] = ES[k] + A[k]['d']
    T = max(EF.values())
    for k in reversed(orden):
        LF[k] = min((LS[j] for j in suc[k]), default=T)
        LS[k] = LF[k] - A[k]['d']
    HT = {k: LS[k] - ES[k] for k in orden}
    HL = {k: min((ES[j] for j in suc[k]), default=T) - EF[k] for k in orden}
    crit = {k for k in orden if abs(HT[k]) < 1e-7}
    caminos = []

    def seguir(k, camino):
        if len(caminos) >= 20:
            return
        sig = [j for j in suc[k] if j in crit and abs(ES[j] - EF[k]) < 1e-7]
        if not sig:
            if abs(EF[k] - T) < 1e-7:
                caminos.append(camino)
            return
        for j in sig:
            seguir(j, camino + [j])

    for k in orden:
        if k in crit and abs(ES[k]) < 1e-7:
            seguir(k, [k])
    pert = any('a' in a for a in acts)
    L = []
    if pert:
        L.append('PERT: te = (a + 4·m + b)/6 y σ² = ((b − a)/6)² para cada actividad')
    L.append('  Act.  Prec.        Dur.     IT      FT      IR      FR      HT      HL%s' % ('      σ²' if pert else ''))
    for k in orden:
        L.append('  %-5s %-10s %6s %7s %7s %7s %7s %7s %7s%s%s'
                 % (k, ','.join(A[k]['prec']) or '—', n(A[k]['d'], 2), n(ES[k], 2), n(EF[k], 2), n(LS[k], 2), n(LF[k], 2),
                    n(HT[k], 2), n(HL[k], 2), ' %7s' % n(A[k]['var'], 3) if pert else '', '  crítica' if k in crit else ''))
    L.append('IT/FT: inicio y fin más tempranos; IR/FR: inicio y fin más tardíos; HT = IR − IT (holgura total); HL = min(IT de las siguientes) − FT (holgura libre).')
    L.append('Duración del proyecto: %s %s. Camino crítico: %s'
             % (n(T, 2), unidad, ' | '.join('–'.join(c) for c in caminos) if caminos else '—'))
    r = {'T': T, 'ES': ES, 'EF': EF, 'LS': LS, 'LF': LF, 'HT': HT, 'HL': HL, 'criticas': crit, 'caminos': caminos}
    if pert and caminos:
        varianzas = [sum(A[k]['var'] for k in c) for c in caminos]
        j = max(range(len(caminos)), key=lambda x: varianzas[x])
        sigma = math.sqrt(varianzas[j])
        r['sigma'] = sigma
        L.append('Desvío del camino crítico%s: σ = √Σσ² = √%s = %s %s'
                 % (' de mayor varianza' if len(caminos) > 1 else '', n(varianzas[j], 3), n(sigma, 3), unidad))
        if plazo is not None and sigma > 0:
            z = (plazo - T) / sigma
            r['P'] = phi(z)
            L.append('Probabilidad de terminar en %s %s: z = (%s − %s)/%s = %s → P = Φ(z) = %s'
                     % (n(plazo, 1), unidad, n(plazo, 2), n(T, 2), n(sigma, 3), n(z, 3), pct(phi(z), 1)))
        if probabilidad is not None and sigma > 0:
            if not 0 < probabilidad < 1:
                raise ValueError('--probabilidad va entre 0 y 1 (por ejemplo 0.95)')
            plazo_p = T + NormalDist().inv_cdf(probabilidad) * sigma
            r['plazo_p'] = plazo_p
            L.append('Plazo con %s de probabilidad: T + z·σ = %s + %s·%s = %s %s'
                     % (pct(probabilidad, 0), n(T, 2), n(NormalDist().inv_cdf(probabilidad), 3), n(sigma, 3), n(plazo_p, 2), unidad))
        L.append('PERT toma un solo camino: si hay caminos casi críticos, la probabilidad real de cumplir es menor.')
    if gantt:
        ancho = 60
        esc = T / ancho if T > ancho else 1.0
        L.append('Gantt (# crítica, = no crítica, . holgura total; 1 carácter = %s %s):' % (n(esc, 2), unidad))
        for k in orden:
            ini, lar, hol = int(round(ES[k] / esc)), max(1, int(round(A[k]['d'] / esc))), int(round(HT[k] / esc))
            L.append('  %-5s |%s%s%s' % (k, ' ' * ini, ('#' if k in crit else '=') * lar, '.' * hol))
        L.append('        +%s %s' % ('-' * int(round(T / esc)), n(T, 1)))
    return r, L


# ------------------------------------------------------------------------------------------ calidad
def leer_subgrupos(ruta=None, texto=None):
    if texto is None:
        texto = _texto_archivo(ruta)
        if texto.lstrip().startswith(('[', '{')):
            datos = json.loads(texto)
            if isinstance(datos, dict):
                datos = datos.get('subgrupos', datos.get('datos'))
            return [[float(x) for x in g] for g in datos]
        filas = _filas_csv(texto)
        grupos = []
        for f in filas:
            vals = []
            for c in f:
                try:
                    vals.append(numero(c))
                except ValueError:
                    pass
            if vals:
                grupos.append(vals)
        return grupos
    return [lista(g, 'subgrupo') for g in texto.split(';') if g.strip()] if ';' in texto else [lista(texto)]


def reglas_western_electric(valores, centro, sigma):
    """Subgrupos (desde 1) donde salta cada regla; zonas a 1, 2 y 3 σ de la línea central."""
    z = [(v - centro) / sigma for v in valores]
    hallado = {1: [], 2: [], 3: [], 4: []}
    for k in range(len(z)):
        if abs(z[k]) > 3:
            hallado[1].append(k + 1)
        for regla, (m, tot, lim) in {2: (2, 3, 2), 3: (4, 5, 1), 4: (8, 8, 0)}.items():
            if k + 1 >= tot:
                vent = z[k - tot + 1:k + 1]
                for signo in (1, -1):
                    if sum(1 for x in vent if signo * x > lim) >= m and signo * z[k] > lim:
                        hallado[regla].append(k + 1)
    return {k: sorted(set(v)) for k, v in hallado.items()}


def calidad(grupos, lei=None, les=None):
    if len(grupos) < 2:
        raise ValueError('hacen falta al menos 2 subgrupos (lo recomendable es 20 a 25)')
    tam = {len(g) for g in grupos}
    if len(tam) != 1:
        raise ValueError('todos los subgrupos tienen que tener el mismo tamaño (hay %s)' % sorted(tam))
    m = tam.pop()
    if m not in CONSTANTES_XR:
        raise ValueError('tamaño de subgrupo %d: la tabla va de 2 a 10 (con más de 10 conviene el gráfico X̄-S)' % m)
    A2, D3, D4 = CONSTANTES_XR[m]
    d2 = D2[m]
    xb = [sum(g) / m for g in grupos]
    R = [max(g) - min(g) for g in grupos]
    k = len(grupos)
    X = sum(xb) / k
    Rb = sum(R) / k
    lcs, lci = X + A2 * Rb, X - A2 * Rb
    lcsr, lcir = D4 * Rb, D3 * Rb
    L = ['%d subgrupos de n = %d; constantes A2 = %s, D3 = %s, D4 = %s, d2 = %s (NIST/SEMATECH, 6.3.2.1)'
         % (k, m, n(A2, 3), n(D3, 3), n(D4, 3), n(d2, 3)),
         'Gráfico X̄: línea central X̿ = %s; LCS = X̿ + A2·R̄ = %s + %s·%s = %s; LCI = X̿ − A2·R̄ = %s'
         % (n(X, 4), n(X, 4), n(A2, 3), n(Rb, 4), n(lcs, 4), n(lci, 4)),
         'Gráfico R: línea central R̄ = %s; LCS = D4·R̄ = %s; LCI = D3·R̄ = %s' % (n(Rb, 4), n(lcsr, 4), n(lcir, 4))]
    reg = reglas_western_electric(xb, X, (lcs - X) / 3)
    fuera_r = [j + 1 for j, v in enumerate(R) if v > lcsr + EPS or v < lcir - EPS]
    textos = {1: 'un punto fuera de los límites', 2: '2 de 3 más allá de 2σ', 3: '4 de 5 más allá de 1σ',
              4: '8 seguidos del mismo lado'}
    senales = ['%s (subgrupos %s)' % (textos[j], ', '.join(map(str, v))) for j, v in reg.items() if v]
    if fuera_r:
        senales.append('R fuera de límites (subgrupos %s)' % ', '.join(map(str, fuera_r)))
    L.append('Control: %s' % ('; '.join(senales) + ': buscar la causa asignable; si se corrige, recalcular sin esos subgrupos'
                               if senales else 'ningún punto fuera de los límites ni rachas (reglas de Western Electric): proceso bajo control'))
    r = {'X': X, 'Rb': Rb, 'LCS': lcs, 'LCI': lci, 'LCSR': lcsr, 'LCIR': lcir, 'xb': xb, 'R': R, 'reglas': reg, 'fuera_R': fuera_r}
    if lei is not None or les is not None:
        sig = Rb / d2
        todos = [x for g in grupos for x in g]
        mu = sum(todos) / len(todos)
        s = math.sqrt(sum((x - mu) ** 2 for x in todos) / (len(todos) - 1))
        r.update({'sigma': sig, 's': s})
        L.append('σ dentro de los subgrupos: σ̂ = R̄/d2 = %s/%s = %s; σ total (todas las mediciones): s = %s' % (n(Rb, 4), n(d2, 3), n(sig, 5), n(s, 5)))
        if lei is not None and les is not None:
            if les <= lei:
                raise ValueError('LES tiene que ser mayor que LEI')
            r['Cp'] = (les - lei) / (6 * sig)
            r['Pp'] = (les - lei) / (6 * s)
            L.append('Cp = (LES − LEI)/(6·σ̂) = (%s − %s)/(6·%s) = %s' % (n(les, 4), n(lei, 4), n(sig, 5), n(r['Cp'], 3)))
        cands = []
        if les is not None:
            cands.append(('Cpu', (les - X) / (3 * sig), (les - X) / (3 * s)))
        if lei is not None:
            cands.append(('Cpl', (X - lei) / (3 * sig), (X - lei) / (3 * s)))
        r['Cpk'] = min(c[1] for c in cands)
        r['Ppk'] = min(c[2] for c in cands)
        L.append('Cpk = min[(LES − X̿)/(3·σ̂); (X̿ − LEI)/(3·σ̂)] = min(%s) = %s; con s: Pp = %s, Ppk = %s'
                 % ('; '.join('%s %s' % (c[0], n(c[1], 3)) for c in cands), n(r['Cpk'], 3),
                    n(r['Pp'], 3) if 'Pp' in r else '—', n(r['Ppk'], 3)))
        nd = NormalDist(X, sig)
        frac = (nd.cdf(lei) if lei is not None else 0.0) + (1 - nd.cdf(les) if les is not None else 0.0)
        r['ppm'] = 1e6 * frac
        L.append('Fuera de tolerancia estimado (distribución normal): %s ppm (%s)' % (miles(1e6 * frac), pct(frac, 3)))
        if 'Cp' in r and r['Cp'] - r['Cpk'] > 0.1:
            L.append('Cp > Cpk: el proceso está descentrado; centrarlo en %s mejora el Cpk hasta %s.' % (n((les + lei) / 2, 4), n(r['Cp'], 3)))
        L.append('Cp y Cpk solo tienen sentido con el proceso bajo control. El mínimo aceptable lo fija el cliente (suele pedirse 1,33 o más: verificar el requisito).')
    return r, L


def pareto(categorias, cantidades, corte=80.0):
    if len(categorias) != len(cantidades) or not categorias:
        raise ValueError('hace falta una cantidad por categoría')
    if any(c < 0 for c in cantidades):
        raise ValueError('las cantidades no pueden ser negativas')
    tot = sum(cantidades)
    if tot <= 0:
        raise ValueError('la suma de las cantidades es cero')
    datos = sorted(zip(categorias, cantidades), key=lambda x: -x[1])
    ancho = max(len(c) for c in categorias)
    L = ['%-*s  Cantidad       %%  Acumulado' % (ancho, 'Categoría')]
    acum, vitales = 0.0, []
    for c, v in datos:
        previo = acum
        acum += v
        if previo / tot < corte / 100 - EPS:
            vitales.append(c)
        L.append('%-*s %9s %7s %10s  %s' % (ancho, c, miles(v), n(100 * v / tot, 1), n(100 * acum / tot, 1), '█' * int(round(30 * v / datos[0][1]))))
    L.append('Pocos vitales (hasta el %s %% acumulado): %s. Atacar primero esas causas (Ishikawa para buscar por qué pasan).'
             % (n(corte, 0), ', '.join(vitales)))
    return {'vitales': vitales, 'orden': [c for c, _ in datos]}, L


def leer_pareto(ruta):
    texto = _texto_archivo(ruta)
    cats, cants = [], []
    if texto.lstrip().startswith(('[', '{')):
        datos = json.loads(texto)
        pares = datos.items() if isinstance(datos, dict) else datos
        for c, v in pares:
            cats.append(str(c))
            cants.append(float(v))
        return cats, cants
    for f in _filas_csv(texto):
        if len(f) < 2:
            continue
        try:
            v = numero(f[1])
        except ValueError:
            continue  # encabezado
        cats.append(f[0].strip())
        cants.append(v)
    return cats, cants


# ------------------------------------------------------------------------------------------ ejemplos (los del SKILL.md)
EJEMPLO_BALANCEO = """tarea,tiempo,precedentes,descripcion
A,40,,corte de perfiles
B,30,A,agujereado
C,50,A,plegado de la base
D,20,B,roscado
E,35,B C,punteado
F,25,C,desbarbado
G,15,D E,soldadura de refuerzos
H,45,E F,soldadura final
I,30,G H,pintura
J,10,I,control y embalaje
"""
EJEMPLO_CPM = """actividad,a,m,b,precedentes,descripcion
A,2,4,6,,relevamiento y proyecto
B,6,9,18,A,compra de la máquina
C,3,5,7,A,base de hormigón
D,2,3,4,A,instalación eléctrica
E,2,3,4,B C,montaje mecánico
F,1,2,3,D E,conexionado
G,1,2,3,F,puesta en marcha y pruebas
H,1,1,1,F,capacitación de operarios
"""
EJEMPLO_CALIDAD = [[19.994, 20.017, 20.022, 20.017, 20.025], [20.008, 19.991, 20.007, 20.014, 20.013],
                   [20.001, 19.983, 20.033, 20.008, 20.014], [20.000, 19.998, 20.016, 20.019, 19.997],
                   [20.001, 20.000, 19.995, 19.998, 20.007], [19.987, 20.034, 19.991, 20.003, 20.029],
                   [20.003, 20.009, 20.015, 20.028, 19.997], [20.026, 19.995, 20.031, 20.022, 20.015],
                   [20.004, 20.027, 20.019, 20.023, 19.992], [20.008, 20.012, 20.015, 19.988, 19.989]]
FLUJOS_EJEMPLO = [-70000, 26800, 26800, 26800, 26800, 46800]
OBS_EJEMPLO = [1.20, 1.25, 1.18, 1.22, 1.30, 1.24, 1.19, 1.21, 1.26, 1.25]


# ------------------------------------------------------------------------------------------ demo
def cerca(x, y, tol):
    return x is not None and abs(x - y) <= tol


def constantes_rango(m, h=0.04, lim=8.0):
    """d2 = E(R/σ) y d3 = desvío(R/σ) del rango de m valores normales, por integración numérica (Simpson)."""
    pasos = int(round(2 * lim / h))
    pasos += pasos % 2
    pasos_w = int(round(12.0 / h))
    pasos_w += pasos_w % 2
    Phi = [phi(-lim + j * h) for j in range(pasos + pasos_w + 1)]
    dens = [math.exp(-(-lim + j * h) ** 2 / 2) / math.sqrt(2 * math.pi) for j in range(pasos + 1)]

    def simpson(v):
        return (v[0] + v[-1] + 4 * sum(v[1:-1:2]) + 2 * sum(v[2:-1:2])) * h / 3

    d2 = simpson([1 - Phi[j] ** m - (1 - Phi[j]) ** m for j in range(pasos + 1)])
    cola = [1 - m * simpson([dens[j] * (Phi[j + w] - Phi[j]) ** (m - 1) for j in range(pasos + 1)]) for w in range(pasos_w + 1)]
    ew2 = simpson([2 * w * h * c for w, c in enumerate(cola)])
    return d2, math.sqrt(ew2 - d2 ** 2)


def cmd_demo():
    ok = []
    # 1. costos y punto de equilibrio
    r, _ = equilibrio(48000, 25, 13, Q=6000)
    ok.append(('equilibrio: Qe = %s u, Ve = %s (CF/(1 − cv/p) = Qe·p), U = %s, cu = %s, margen de seguridad %s'
               % (miles(r['Qe']), miles(r['Ve']), miles(r['U']), n(r['cu']), pct(r['ms'], 1)),
               cerca(r['Qe'], 4000, 1e-9) and cerca(r['Ve'], 4000 * 25, 1e-6) and cerca(r['U'], 24000, 1e-6)
               and cerca(r['cu'], 21, 1e-9) and cerca(r['ms'], 1 / 3, 1e-12)))
    # 2. amortización lineal
    r, _ = amortizacion(60000, 5, 10000)
    ok.append(('amortización lineal: A = %s por año y valor de libro final = valor residual' % miles(r['A']),
               cerca(r['A'], 10000, 1e-9) and cerca(r['libro'][-1], 10000, 1e-6)))
    # 3. VAN y TIR del ejemplo (flujo armado en el SKILL.md: (150 000 − 78 000 − 38 000 − 10 000)·0,7 + 10 000 = 26 800)
    fo = (6000 * 25 - 6000 * 13 - 38000 - 10000) * (1 - 0.30) + 10000
    F = [-70000] + [fo] * 4 + [fo + 10000 + 10000]
    r, _ = evaluar(F, 12)
    fa = (1 - 1.12 ** -5) / 0.12
    van_anualidad = -70000 + fo * fa + 20000 / 1.12 ** 5
    ok.append(('flujo operativo = %s; VAN al 12 %% = %s, igual por la fórmula de la anualidad (FA = %s)'
               % (miles(fo), miles(r['VAN'], 2), n(fa, 4)), F == FLUJOS_EJEMPLO and cerca(r['VAN'], van_anualidad, 1e-6)
               and cerca(r['VAN'], 37956.54, 0.01)))
    ok.append(('TIR = %s por bisección y por Newton, con VAN(TIR) = 0' % pct(r['TIR'], 3),
               cerca(r['TIR'], r['TIR_newton'], 1e-9) and abs(vna(F, r['TIR'])) < 1e-6 and cerca(r['TIR'], 0.304563, 1e-6)))
    ok.append(('recupero simple %s y descontado %s años; B/C = %s' % (n(r['PRs']), n(r['PRd']), n(r['BC'], 3)),
               cerca(r['PRs'], 2 + 16400 / 26800, 1e-9) and cerca(r['PRd'], 3.3306, 1e-4) and cerca(r['BC'], 1 + r['VAN'] / 70000, 1e-9)))
    # 4. inflación: el mismo proyecto en moneda corriente con 30 % anual y la tasa nominal da el mismo VAN
    rf, _ = tasas_fisher(30, real=12)
    rr, _ = tasas_fisher(30, nominal=100 * rf['i'])
    rn, _ = evaluar([f * 1.3 ** t for t, f in enumerate(F)], 100 * rf['i'])
    ok.append(('Fisher: (1,12)·(1,30) − 1 = %s y vuelve a 12 %%; VAN en corriente a esa tasa = VAN real' % pct(rf['i'], 1),
               cerca(rf['i'], 0.456, 1e-12) and cerca(rr['r'], 0.12, 1e-12) and cerca(rn['VAN'], r['VAN'], 1e-6)))
    # 5. estudio de tiempos
    rt, _ = tiempos(OBS_EJEMPLO, [110], [5, 4, 2, 2], turno=480)
    ok.append(('tiempos: TO = %s, TN = %s, TS = %s min, %d piezas por turno, alcanzan %s observaciones'
               % (n(rt['TO'], 3), n(rt['TN'], 3), n(rt['TS'], 4), rt['piezas'], n(rt['n_req'], 2)),
               cerca(rt['TO'], 1.23, 1e-12) and cerca(rt['TN'], 1.353, 1e-12) and cerca(rt['TS'], 1.52889, 1e-9)
               and rt['piezas'] == 313 and cerca(rt['n_req'], 1.83406, 1e-4)))
    ok.append(('t de Student: t(0,975; 24) = %s y t(0,975; 9) = %s (tabla NIST 1.3.6.7.2: 2,064 y 2,262)'
               % (n(t_inv(0.975, 24), 4), n(t_inv(0.975, 9), 4)),
               cerca(t_inv(0.975, 24), 2.064, 5e-4) and cerca(t_inv(0.975, 9), 2.262, 5e-4)))
    n101 = (2.064 * 0.09 / (0.05 * 0.30)) ** 2
    ok.append(('Niebel y Freivalds, ejemplo 10.1: n = (2,064·0,09/(0,05·0,30))² = %s → %d observaciones' % (n(n101, 1), math.ceil(n101)),
               math.ceil(n101) == 154))
    rm, _ = muestreo(ocurrencias=60, total=400, error=3)
    ok.append(('muestreo: p = 15 %%, ±%s con 400 observaciones; para ±3 %% hacen falta %d' % (pct(rm['semi'], 1), math.ceil(rm['n_req'])),
               cerca(rm['semi'], 0.034992, 1e-5) and math.ceil(rm['n_req']) == 545))
    # 6. capacidad y balanceo
    rc, _ = capacidad([1.2, 1.53, 2.0, 0.9], 480, nombres=['corte', 'agujereado', 'plegado', 'pintura'], demanda=260)
    ok.append(('capacidad: cuello de botella %s (%s u por turno), le sigue %s; faltan %s u'
               % (rc['cuello'], n(rc['sistema'], 0), rc['siguiente'], n(rc['falta'], 0)),
               rc['cuello'] == 'plegado' and cerca(rc['sistema'], 240, 1e-9) and rc['siguiente'] == 'agujereado' and cerca(rc['falta'], 20, 1e-9)))
    tareas = leer_actividades(texto=EJEMPLO_BALANCEO)
    rb, _ = balanceo(tareas, 7 * 3600 / 420)
    asign = {k: j for j, (est, _) in enumerate(rb['estaciones']) for k in est}
    t = {a['id']: a['d'] for a in tareas}
    respeta = all(asign[p] <= asign[a['id']] for a in tareas for p in a['prec'])
    ok.append(('balanceo: C = %s s, Nt = %d, %d estaciones, E = %s; precedencias y ciclo respetados'
               % (n(rb['C'], 0), rb['Nt'], rb['N'], pct(rb['E'], 1)),
               cerca(rb['C'], 60, 1e-9) and rb['Nt'] == 5 and rb['N'] == 6 and cerca(rb['E'], 300 / 360, 1e-12) and respeta
               and all(sum(t[k] for k in est) <= 60 + EPS for est, _ in rb['estaciones'])))
    # con 5 estaciones sería E = 100 %: la primera estación no se puede completar (después de A solo entran B o C, que no caben)
    ok.append(('balanceo: con C = 60 s no hay 5 estaciones posibles (ninguna tarea de 20 s queda disponible después de A)',
               all(t[k] > 20 for a in tareas if a['prec'] == ['A'] for k in [a['id']])))
    # 7. CPM y PERT
    acts = leer_actividades(texto=EJEMPLO_CPM)
    rp, _ = cpm(acts, plazo=24, probabilidad=0.95)
    suc = {a['id']: [b['id'] for b in acts if a['id'] in b['prec']] for a in acts}
    largos = []

    def caminos(k, total):
        total += next(a['d'] for a in acts if a['id'] == k)
        if not suc[k]:
            largos.append(total)
        for j in suc[k]:
            caminos(j, total)

    for a in acts:
        if not a['prec']:
            caminos(a['id'], 0.0)
    ok.append(('CPM: T = %s días = el más largo de los %d caminos; camino crítico %s'
               % (n(rp['T'], 0), len(largos), '–'.join(rp['caminos'][0])),
               cerca(rp['T'], 21, 1e-9) and cerca(max(largos), rp['T'], 1e-9) and rp['caminos'] == [['A', 'B', 'E', 'F', 'G']]))
    ok.append(('holguras totales: C = %s, D = %s, H = %s días' % (n(rp['HT']['C'], 0), n(rp['HT']['D'], 0), n(rp['HT']['H'], 0)),
               cerca(rp['HT']['C'], 5, 1e-9) and cerca(rp['HT']['D'], 10, 1e-9) and cerca(rp['HT']['H'], 1, 1e-9)))
    ok.append(('PERT: σ = %s días, P(T ≤ 24) = %s, plazo al 95 %% = %s días' % (n(rp['sigma'], 3), pct(rp['P'], 1), n(rp['plazo_p'], 2)),
               cerca(rp['sigma'], math.sqrt(4 / 9 + 4 + 3 / 9), 1e-9) and cerca(rp['P'], 0.91504, 1e-4) and cerca(rp['plazo_p'], 24.5953, 1e-3)))
    # 8. constantes de los gráficos de control recalculadas contra la tabla del NIST
    peor = 0.0
    for m, (A2, D3, D4) in CONSTANTES_XR.items():
        d2, d3 = constantes_rango(m)
        peor = max(peor, abs(3 / (d2 * math.sqrt(m)) - A2), abs(max(0.0, 1 - 3 * d3 / d2) - D3), abs(1 + 3 * d3 / d2 - D4),
                   abs(d2 - D2[m]))
    ok.append(('A2, D3, D4 (n = 2 a 10) recalculados desde d2 y d3 por integración: diferencia máxima con la tabla %s' % n(peor, 4),
               peor < 6e-4))
    rq, _ = calidad(EJEMPLO_CALIDAD, 19.95, 20.05)
    ok.append(('X̄-R: X̿ = %s, R̄ = %s, LCS = %s, LCI = %s, LCS(R) = %s, bajo control'
               % (n(rq['X'], 4), n(rq['Rb'], 4), n(rq['LCS'], 4), n(rq['LCI'], 4), n(rq['LCSR'], 4)),
               cerca(rq['X'], 20.0088, 1e-9) and cerca(rq['Rb'], 0.0314, 1e-9) and cerca(rq['LCS'], 20.0269178, 1e-6)
               and not any(rq['reglas'].values()) and not rq['fuera_R']))
    ok.append(('capacidad del proceso: Cp = %s y Cpk = %s (descentrado)' % (n(rq['Cp'], 2), n(rq['Cpk'], 2)),
               cerca(rq['Cp'], 0.1 / (6 * 0.0314 / 2.326), 1e-9) and cerca(rq['Cpk'], (20.05 - 20.0088) / (3 * 0.0314 / 2.326), 1e-9)))
    cpk_nist = min(20 - 16, 16 - 8) / (3 * 2)
    ok.append(('NIST 6.1.6: LES 20, LEI 8, media 16, σ 2 → Cp = %s, Cpk = %s (libro: 1,0 y 0,6667)' % (n((20 - 8) / 12, 1), n(cpk_nist, 4)),
               cerca(cpk_nist, 0.6667, 5e-5)))
    racha = reglas_western_electric([1.0] * 8, 0.0, 2.0)
    ok.append(('regla 4 de Western Electric: 8 puntos seguidos del mismo lado se detectan', racha[4] == [8] and not racha[1]))
    rpa, _ = pareto(['Pintura', 'Rebabas', 'Rayas', 'Medida fuera de tolerancia', 'Porosidad'], [4, 52, 10, 28, 6])
    ok.append(('Pareto: pocos vitales = %s (80 %% de los defectos)' % ', '.join(rpa['vitales']),
               rpa['vitales'] == ['Rebabas', 'Medida fuera de tolerancia']))
    for nombre, bien in ok:
        print('  %s %s' % ('ok ' if bien else 'MAL', nombre))
    todo = all(b for _, b in ok)
    print('DEMO %s' % ('OK' if todo else 'FALLO'))
    return 0 if todo else 1


# ------------------------------------------------------------------------------------------ línea de comandos
def construir_parser():
    ap = argparse.ArgumentParser(prog='organizacion.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', metavar='comando', title='comandos')
    sp.required = True

    def sub(nombre, ayuda):
        return sp.add_parser(nombre, help=ayuda, description=ayuda)

    p = sub('equilibrio', 'punto de equilibrio, margen de contribución y costo unitario')
    p.add_argument('--cf', type=float, required=True, metavar='CF', help='costos fijos del período (con amortizaciones)')
    p.add_argument('--precio', type=float, required=True, metavar='p', help='precio de venta unitario')
    p.add_argument('--cv', type=float, required=True, metavar='cv', help='costo variable unitario')
    p.add_argument('--cantidad', type=float, metavar='Q', help='cantidad prevista por período (utilidad y margen de seguridad)')
    p.add_argument('--utilidad', type=float, metavar='U', help='utilidad objetivo: calcula la cantidad necesaria')

    p = sub('amortizacion', 'amortización lineal y valor de libro año por año')
    p.add_argument('--valor', type=float, required=True, metavar='V0', help='valor de origen del bien')
    p.add_argument('--vida', type=int, required=True, metavar='n', help='vida útil en años')
    p.add_argument('--residual', type=float, default=0.0, metavar='VR', help='valor residual al final de la vida útil (0 si no se indica)')

    p = sub('van', 'VAN, TIR, período de recupero y relación beneficio/costo')
    p.add_argument('--flujos', required=True, metavar='F0,F1,...', help='flujos netos desde el año 0 (con =: --flujos=-70000,26800,...)')
    p.add_argument('--tasa', type=float, required=True, metavar='%', help='tasa de descuento por período, en %%')
    p.add_argument('--moneda', default='la moneda de los flujos', help='texto para el informe, por ejemplo "USD constantes de 2026"')

    p = sub('inflacion', 'tasa real o nominal (Fisher) y flujos en moneda constante')
    p.add_argument('--inflacion', type=float, metavar='%', help='inflación por período, en %%')
    p.add_argument('--nominal', type=float, metavar='%', help='tasa nominal en %% (calcula la real)')
    p.add_argument('--real', type=float, metavar='%', help='tasa real en %% (calcula la nominal)')
    p.add_argument('--flujos', metavar='F0,F1,...', help='flujos en moneda corriente para pasar a moneda constante')
    p.add_argument('--inflaciones', metavar='%,%,...', help='una inflación por período (del 1 al n), en %%')
    p.add_argument('--ipc', metavar='I0,I1,...', help='índice de precios de cada período (por ejemplo el IPC del INDEC)')

    p = sub('tiempos', 'estudio de tiempos: tiempo normal, estándar, producción y observaciones necesarias')
    p.add_argument('--obs', required=True, metavar='t1,t2,...', help='tiempos observados de cada ciclo (por ejemplo en min)')
    p.add_argument('--valoracion', required=True, metavar='%', help='valoración del ritmo en %% (100 = normal): una o una por ciclo')
    p.add_argument('--suplementos', default='', metavar='%,%,...', help='suplementos en %% que se suman (tabla de la OIT)')
    p.add_argument('--turno', type=float, metavar='T', help='tiempo del turno en la misma unidad (480 min = 8 h)')
    p.add_argument('--confianza', type=float, default=95.0, metavar='%', help='confianza para el número de observaciones (95)')
    p.add_argument('--precision', type=float, default=5.0, metavar='%', help='error admitido sobre la media, en %% (5)')
    p.add_argument('--modo', choices=['normal', 'jornada'], default='normal',
                   help='suplementos en %% del tiempo normal (OIT, por defecto) o de la jornada')
    p.add_argument('--unidad', default='min', help='unidad de los tiempos, solo para el texto (min)')

    p = sub('muestreo', 'muestreo del trabajo: proporción, intervalo y observaciones necesarias')
    p.add_argument('--p', type=float, metavar='%', help='proporción estimada en %%')
    p.add_argument('--ocurrencias', type=int, metavar='k', help='veces que se observó la actividad')
    p.add_argument('--total', type=int, metavar='N', help='observaciones totales')
    p.add_argument('--error', type=float, metavar='%', help='error absoluto admitido en puntos de %% (por ejemplo 3)')
    p.add_argument('--confianza', type=float, default=95.0, metavar='%', help='nivel de confianza en %% (95)')

    p = sub('capacidad', 'capacidad por estación, cuello de botella y utilización')
    p.add_argument('--tiempos', required=True, metavar='t1,t2,...', help='tiempo por unidad en cada estación')
    p.add_argument('--disponible', type=float, required=True, metavar='T', help='tiempo disponible por período, en la misma unidad')
    p.add_argument('--maquinas', metavar='m1,m2,...', help='máquinas o puestos iguales en cada estación (1)')
    p.add_argument('--nombres', metavar='a,b,...', help='nombre de cada estación')
    p.add_argument('--demanda', type=float, metavar='D', help='unidades pedidas por período')
    p.add_argument('--rendimiento', type=float, default=1.0, metavar='η',
                   help='fracción del tiempo que se produce de verdad (paradas, cambios); ver OEE en mantenimiento-industrial')

    p = sub('balanceo', 'balanceo de línea con una regla heurística')
    p.add_argument('archivo', nargs='?', help='CSV o JSON con tarea, tiempo y precedentes')
    p.add_argument('--ciclo', type=float, metavar='C', help='tiempo de ciclo, en la unidad de los tiempos')
    p.add_argument('--disponible', type=float, metavar='T', help='tiempo productivo por período (con --demanda: C = T/D)')
    p.add_argument('--demanda', type=float, metavar='D', help='unidades por período')
    p.add_argument('--regla', choices=['sucesoras', 'peso', 'tiempo'], default='sucesoras',
                   help='prioridad: más tareas sucesoras (por defecto), mayor peso posicional o mayor tiempo')
    p.add_argument('--ejemplo', action='store_true', help='muestra un archivo de ejemplo y termina')

    p = sub('cpm', 'CPM y PERT: fechas, holguras, camino crítico, probabilidad y Gantt')
    p.add_argument('archivo', nargs='?', help='CSV o JSON con actividad, duración (o a, m, b) y precedentes')
    p.add_argument('--plazo', type=float, metavar='T', help='plazo para calcular la probabilidad de cumplirlo (PERT)')
    p.add_argument('--probabilidad', type=float, metavar='P', help='probabilidad deseada (0.95): calcula el plazo (PERT)')
    p.add_argument('--gantt', action='store_true', help='dibuja un diagrama de Gantt en texto')
    p.add_argument('--unidad', default='días', help='unidad de las duraciones, solo para el texto (días)')
    p.add_argument('--ejemplo', action='store_true', help='muestra un archivo de ejemplo y termina')

    p = sub('calidad', 'gráficos de control X̄-R, Cp y Cpk')
    p.add_argument('archivo', nargs='?', help='CSV con un subgrupo por fila, o JSON con una lista de subgrupos')
    p.add_argument('--datos', metavar='"x x x; x x x"', help='subgrupos separados por punto y coma')
    p.add_argument('--lei', type=float, metavar='LEI', help='límite de especificación inferior (tolerancia)')
    p.add_argument('--les', type=float, metavar='LES', help='límite de especificación superior (tolerancia)')
    p.add_argument('--ejemplo', action='store_true', help='muestra un archivo de ejemplo y termina')

    p = sub('pareto', 'diagrama de Pareto con los pocos vitales')
    p.add_argument('archivo', nargs='?', help='CSV o JSON con categoría y cantidad')
    p.add_argument('--categorias', metavar='a,b,c', help='nombres de las categorías, separados por coma')
    p.add_argument('--cantidades', metavar='n1,n2,...', help='cantidad de cada categoría')
    p.add_argument('--corte', type=float, default=80.0, metavar='%', help='porcentaje acumulado de corte (80)')

    sub('demo', 'reproduce el ejemplo resuelto del SKILL.md y termina en DEMO OK')
    return ap


def main(argv=None):
    a = construir_parser().parse_args(argv)
    try:
        if a.cmd == 'demo':
            return cmd_demo()
        if a.cmd == 'equilibrio':
            _, L = equilibrio(a.cf, a.precio, a.cv, a.cantidad, a.utilidad)
        elif a.cmd == 'amortizacion':
            _, L = amortizacion(a.valor, a.vida, a.residual)
        elif a.cmd == 'van':
            _, L = evaluar(lista(a.flujos, '--flujos'), a.tasa, a.moneda)
        elif a.cmd == 'inflacion':
            if a.flujos:
                _, L = deflactar(lista(a.flujos, '--flujos'), a.inflacion,
                                 lista(a.inflaciones, '--inflaciones') if a.inflaciones else None,
                                 lista(a.ipc, '--ipc') if a.ipc else None)
            else:
                if a.inflacion is None:
                    raise ValueError('indicá --inflacion')
                _, L = tasas_fisher(a.inflacion, a.nominal, a.real)
        elif a.cmd == 'tiempos':
            _, L = tiempos(lista(a.obs, '--obs'), lista(a.valoracion, '--valoracion'),
                           lista(a.suplementos, '--suplementos') if a.suplementos else [], a.turno, a.confianza, a.precision, a.modo, a.unidad)
        elif a.cmd == 'muestreo':
            _, L = muestreo(a.p, a.ocurrencias, a.total, a.error, a.confianza)
        elif a.cmd == 'capacidad':
            _, L = capacidad(lista(a.tiempos, '--tiempos'), a.disponible,
                             [int(x) for x in lista(a.maquinas, '--maquinas')] if a.maquinas else None,
                             [x.strip() for x in a.nombres.split(',')] if a.nombres else None, a.demanda, a.rendimiento)
        elif a.cmd in ('balanceo', 'cpm', 'calidad') and a.ejemplo:
            print({'balanceo': EJEMPLO_BALANCEO, 'cpm': EJEMPLO_CPM,
                   'calidad': '\n'.join(','.join('%.3f' % x for x in g) for g in EJEMPLO_CALIDAD) + '\n'}[a.cmd], end='')
            return 0
        elif a.cmd == 'balanceo':
            if not a.archivo:
                raise ValueError('falta el archivo de tareas (ver --ejemplo)')
            if a.ciclo:
                C = a.ciclo
            elif a.disponible and a.demanda:
                C = a.disponible / a.demanda
                print('Tiempo de ciclo: C = T/D = %s/%s = %s' % (miles(a.disponible), miles(a.demanda), n(C, 2)))
            else:
                raise ValueError('indicá --ciclo, o --disponible y --demanda')
            _, L = balanceo(leer_actividades(a.archivo), C, a.regla)
        elif a.cmd == 'cpm':
            if not a.archivo:
                raise ValueError('falta el archivo de actividades (ver --ejemplo)')
            _, L = cpm(leer_actividades(a.archivo), a.plazo, a.probabilidad, a.gantt, a.unidad)
        elif a.cmd == 'calidad':
            if a.datos:
                grupos = leer_subgrupos(texto=a.datos)
            elif a.archivo:
                grupos = leer_subgrupos(a.archivo)
            else:
                raise ValueError('indicá un archivo o --datos (ver --ejemplo)')
            _, L = calidad(grupos, a.lei, a.les)
        else:
            if a.archivo:
                cats, cants = leer_pareto(a.archivo)
            elif a.categorias and a.cantidades:
                cats, cants = [x.strip() for x in a.categorias.split(',')], lista(a.cantidades, '--cantidades')
            else:
                raise ValueError('indicá un archivo, o --categorias y --cantidades')
            _, L = pareto(cats, cants, a.corte)
    except (ValueError, json.JSONDecodeError) as ex:
        print('organizacion.py: %s' % ex, file=sys.stderr)
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
