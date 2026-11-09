#!/usr/bin/env python3
"""Calculos de neumatica para trabajos practicos: cilindros, cascada y pandeo.

Subcomandos:
  cilindro  fuerzas de avance y retroceso, consumo de aire libre, velocidad
            y diametro normalizado para una fuerza pedida
  tabla     fuerzas de los diametros usuales a una presion dada
  cascada   grupos del metodo cascada, valvulas memoria, senales de cambio de
            grupo y conflictos del metodo intuitivo para una secuencia
  pandeo    carga critica de Euler del vastago y longitud maxima
  demo      ejemplo resuelto de todo lo anterior

Ejemplos:
  python neumatica.py demo
  python neumatica.py cilindro --D 50 --d 20 --p 6 --carrera 200 --eta 0.7 --ciclos 10
  python neumatica.py cilindro --fuerza 800 --p 6 --eta 0.7 --carrera 150
  python neumatica.py cascada "A+ B+ B- A-"
  python neumatica.py pandeo --d 10 --L 400 --caso 1 --F 206

Convenciones: presiones manometricas en bar (1 bar = 0,1 N/mm2), diametros y
longitudes en mm, fuerzas en N, aire libre en litros a presion atmosferica.
Solo usa la biblioteca estandar (Python 3.9 o posterior).
"""
from __future__ import annotations

import argparse
import math
import re
import sys

P_ATM = 1.013  # bar, presion atmosferica de referencia para pasar a aire libre

# Diametros de embolo usuales en mm (serie de ISO 3320; ISO 6432 cubre 8 a 25 y
# ISO 15552 de 32 a 320). Confirmar siempre en el catalogo del cilindro elegido.
DIAMETROS = [8, 10, 12, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 320]

# Vastago tipico en mm. Coincide con las fuerzas teoricas a 6 bar publicadas por
# Festo para DSNU (ISO 6432, 8 a 25 mm) y DSBC (ISO 15552, 32 a 125 mm).
VASTAGO_TIPICO = {8: 4, 10: 4, 12: 6, 16: 6, 20: 8, 25: 10, 32: 12, 40: 16,
                  50: 20, 63: 20, 80: 25, 100: 25, 125: 32}

# Casos de Euler: factor beta de la longitud libre de pandeo Lk = beta * L
EULER = {
    1: (2.0, "empotrado en un extremo y libre en el otro"),
    2: (1.0, "articulado en los dos extremos"),
    3: (0.7, "empotrado en un extremo y articulado en el otro"),
    4: (0.5, "empotrado en los dos extremos"),
}

ROMANOS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


# ------------------------------------------------------------------ formato

def num(x: float, dec: int = 1) -> str:
    """Numero con coma decimal y punto de miles (1.178,1)."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def mov_txt(m) -> str:
    return f"{m[0]}{m[1]}"


def sensor_txt(s) -> str:
    return f"{s[0].lower()}{s[1]}"


# ------------------------------------------------------------------ cilindro

def area_mm2(diam_mm: float) -> float:
    return math.pi * diam_mm ** 2 / 4.0


def calc_cilindro(D, d, p, carrera, eta=1.0, ciclos=None, simple=False,
                  tiempo=None, patm=P_ATM):
    """Fuerzas [N], consumo [l de aire libre] y caudal de un cilindro."""
    if D <= 0 or p <= 0 or carrera <= 0:
        raise ValueError("D, p y carrera tienen que ser positivos")
    if d is not None and not (0 <= d < D):
        raise ValueError("el vastago tiene que ser menor que el embolo")
    ae = area_mm2(D)                        # mm2, lado del embolo
    ar = ae - area_mm2(d) if d else None    # mm2, area anular (lado vastago)
    pres = p * 0.1                          # N/mm2
    relacion = (p + patm) / patm            # relacion de compresion
    r = {
        "D": D, "d": d, "p": p, "carrera": carrera, "eta": eta, "patm": patm,
        "Ae_cm2": ae / 100.0, "Ar_cm2": ar / 100.0 if ar else None,
        "Fav_teo": pres * ae, "Fav": eta * pres * ae,
        "Fret_teo": pres * ar if ar else None,
        "Fret": eta * pres * ar if ar else None,
        "relacion": relacion,
        "V_av_l": ae * carrera * 1e-6 * relacion,            # l aire libre
        "V_ret_l": ar * carrera * 1e-6 * relacion if ar else None,
    }
    if simple:
        r["V_ciclo_l"] = r["V_av_l"]
    else:
        if ar is None:
            raise ValueError("para doble efecto hace falta el diametro del vastago (--d)")
        r["V_ciclo_l"] = r["V_av_l"] + r["V_ret_l"]
    if ciclos:
        r["Q_lmin"] = r["V_ciclo_l"] * ciclos
        r["Q_m3h"] = r["Q_lmin"] * 60.0 / 1000.0
    if tiempo:
        v = carrera / 1000.0 / tiempo                          # m/s
        r["v_ms"] = v
        # caudal de aire libre durante el avance a esa velocidad media
        r["Q_av_lmin"] = ae * 1e-6 * v * relacion * 60000.0
    return r


def diametro_para(F, p, eta=1.0):
    """Diametro minimo [mm] y el normalizado inmediato superior."""
    if F <= 0 or p <= 0 or eta <= 0:
        raise ValueError("F, p y eta tienen que ser positivos")
    dmin = math.sqrt(4.0 * F / (math.pi * p * 0.1 * eta))
    adoptado = next((x for x in DIAMETROS if x >= dmin), None)
    return dmin, adoptado


def imprimir_cilindro(r, simple=False):
    print(f"Cilindro Ø{num(r['D'], 0)} mm" + (f", vástago Ø{num(r['d'], 0)} mm" if r['d'] else "")
          + f", p = {num(r['p'], 1)} bar, carrera {num(r['carrera'], 0)} mm, eta = {num(r['eta'], 2)}")
    print(f"  Área del émbolo   Ae = pi·D²/4        = {num(r['Ae_cm2'], 2)} cm²")
    if r["Ar_cm2"]:
        print(f"  Área anular       Ar = pi·(D² - d²)/4 = {num(r['Ar_cm2'], 2)} cm²")
    print(f"  Fuerza de avance:    teórica {num(r['Fav_teo'], 1)} N  -> útil (eta) {num(r['Fav'], 1)} N")
    if simple:
        print("  Simple efecto: retrocede por resorte; a la fuerza de avance hay que restarle"
              " la fuerza del resorte al final de la carrera (dato del catálogo).")
    elif r["Fret_teo"] is not None:
        print(f"  Fuerza de retroceso: teórica {num(r['Fret_teo'], 1)} N  -> útil (eta) {num(r['Fret'], 1)} N")
    print(f"  Relación de compresión (p + patm)/patm = {num(r['relacion'], 3)}  (patm = {num(r['patm'], 3)} bar)")
    print(f"  Aire libre por carrera: avance {num(r['V_av_l'], 3)} l"
          + (f", retroceso {num(r['V_ret_l'], 3)} l" if r['V_ret_l'] is not None and not simple else ""))
    print(f"  Aire libre por ciclo: {num(r['V_ciclo_l'], 3)} l" + ("  (simple efecto: solo el avance)" if simple else ""))
    if "Q_lmin" in r:
        print(f"  Consumo: {num(r['Q_lmin'], 1)} l/min = {num(r['Q_m3h'], 2)} m³/h de aire libre"
              " (sin mangueras ni volúmenes muertos)")
    if "v_ms" in r:
        print(f"  Velocidad media de avance: {num(r['v_ms'], 3)} m/s -> caudal de aire libre durante el avance:"
              f" {num(r['Q_av_lmin'], 1)} l/min")


# ------------------------------------------------------------------ tabla

def imprimir_tabla(p, eta):
    print(f"Fuerzas a {num(p, 1)} bar (teórica y útil con eta = {num(eta, 2)}); vástago típico de catálogo")
    print("   D [mm]  d [mm]   F avance teo/útil [N]    F retroceso teo/útil [N]")
    for D in DIAMETROS:
        d = VASTAGO_TIPICO.get(D)
        if d is None:
            continue
        r = calc_cilindro(D, d, p, 100, eta)
        print(f"   {D:>6}  {d:>6}   {num(r['Fav_teo'], 0):>9} / {num(r['Fav'], 0):<9}"
              f"   {num(r['Fret_teo'], 0):>9} / {num(r['Fret'], 0):<9}")
    print("   (160 a 320 mm: ver el vástago en el catálogo del fabricante)")


# ------------------------------------------------------------------ pandeo

def calc_pandeo(d, L=None, beta=1.0, E=210000.0, nu=3.5, F=None):
    """Euler: Fk = pi²·E·I/Lk², I = pi·d^4/64, Lk = beta·L. Unidades N y mm."""
    if d <= 0 or E <= 0 or nu <= 0 or beta <= 0:
        raise ValueError("d, E, nu y beta tienen que ser positivos")
    inercia = math.pi * d ** 4 / 64.0                 # mm4
    r = {"d": d, "I": inercia, "beta": beta, "E": E, "nu": nu, "F": F}
    if L is not None:
        lk = beta * L
        fk = math.pi ** 2 * E * inercia / lk ** 2
        r.update({"L": L, "Lk": lk, "Fk": fk, "Fadm": fk / nu, "esbeltez": 4.0 * lk / d})
    elif F is not None:
        lk_max = math.pi * math.sqrt(E * inercia / (nu * F))
        r.update({"Lk_max": lk_max, "L_max": lk_max / beta, "esbeltez_max": 4.0 * lk_max / d})
    else:
        raise ValueError("hace falta --L (para verificar) o --F (para la longitud máxima)")
    return r


def imprimir_pandeo(r, caso=None):
    desc = f"caso {caso} de Euler ({EULER[caso][1]})" if caso else f"beta = {num(r['beta'], 2)}"
    print(f"Pandeo del vástago Ø{num(r['d'], 1)} mm, {desc}, E = {num(r['E'], 0)} N/mm², seguridad nu = {num(r['nu'], 1)}")
    print(f"  Momento de inercia  I = pi·d^4/64 = {num(r['I'], 1)} mm^4")
    if "Fk" in r:
        print(f"  Longitud libre de pandeo  Lk = beta·L = {num(r['beta'], 2)} · {num(r['L'], 0)} = {num(r['Lk'], 0)} mm")
        print(f"  Carga crítica  Fk = pi²·E·I/Lk² = {num(r['Fk'], 0)} N")
        print(f"  Carga admisible  Fadm = Fk/nu = {num(r['Fadm'], 0)} N")
        print(f"  Esbeltez  4·Lk/d = {num(r['esbeltez'], 0)}")
        if r["esbeltez"] < 100:
            print("  ATENCIÓN: esbeltez menor que 100: Euler sobreestima la carga crítica;"
                  " usar el diagrama de pandeo del fabricante o un método inelástico (Tetmajer, Johnson).")
        if r["F"] is not None:
            ok = r["F"] <= r["Fadm"]
            print(f"  Fuerza axial {num(r['F'], 0)} N {'<=' if ok else '>'} Fadm -> "
                  + ("VERIFICA" if ok else "NO VERIFICA: aumentar el vástago, guiar la carga o acortar"))
    else:
        print(f"  Para F = {num(r['F'], 0)} N: Lk máx = pi·raíz(E·I/(nu·F)) = {num(r['Lk_max'], 0)} mm"
              f" -> L máx = Lk/beta = {num(r['L_max'], 0)} mm")
        print(f"  Esbeltez en ese límite: {num(r['esbeltez_max'], 0)}"
              + ("  (menor que 100: Euler no es confiable, ver el fabricante)" if r["esbeltez_max"] < 100 else ""))


# ------------------------------------------------------------------ cascada

PATRON_MOV = re.compile(r"([A-Za-z])\s*([+\-−–])")


def parsear_secuencia(texto: str):
    if "(" in texto or "/" in texto:
        raise ValueError("los movimientos simultáneos no están soportados: escribir la secuencia"
                         " de a un movimiento (resolver los simultáneos a mano)")
    resto = PATRON_MOV.sub(" ", texto).replace(",", " ").replace(";", " ").strip()
    if resto:
        raise ValueError(f"no se entiende '{resto}': usar movimientos como A+ B+ B- A-")
    movs = [(c.upper(), "+" if s == "+" else "-") for c, s in PATRON_MOV.findall(texto)]
    if len(movs) < 2:
        raise ValueError("la secuencia necesita al menos dos movimientos")
    for cil in sorted({c for c, _ in movs}):
        dirs = [s for c, s in movs if c == cil]
        if dirs.count("+") != dirs.count("-"):
            raise ValueError(f"el cilindro {cil} no vuelve a su posición inicial (cantidad de + y - distinta)")
        for i in range(len(dirs)):
            if dirs[i] == dirs[i - 1]:
                raise ValueError(f"el cilindro {cil} tiene dos movimientos seguidos en el mismo sentido")
    return movs


def fin_de(m):
    """Sensor que se activa al terminar el movimiento m: A+ -> a1, A- -> a0."""
    return (m[0], 1 if m[1] == "+" else 0)


def posicion_inicial(movs):
    pos = {}
    for c, s in movs:
        if c not in pos:
            pos[c] = 0 if s == "+" else 1
    return pos


def analizar_intuitivo(movs):
    """Mandos del método intuitivo y señales en conflicto (válvulas biestables)."""
    n = len(movs)
    mando = [fin_de(movs[i - 1]) for i in range(n)]   # mando[0] va en serie con Marcha
    estado = posicion_inicial(movs)
    conflictos = []
    for i, (c, s) in enumerate(movs):
        for j, (c2, s2) in enumerate(movs):
            if c2 != c or s2 == s or j == 0:   # j == 0: lleva Marcha (pulsador que se suelta)
                continue
            cil, val = mando[j]
            if estado[cil] == val and (movs[i], movs[j], mando[j]) not in conflictos:
                conflictos.append((movs[i], movs[j], mando[j]))
        estado[c] = 1 if s == "+" else 0
    repetidos = []
    for i in range(1, n):
        for k in range(i + 1, n):
            if mando[i] == mando[k] and movs[i] != movs[k]:
                repetidos.append((mando[i], movs[i], movs[k]))
    return mando, conflictos, repetidos


def agrupar(movs):
    grupos, actual = [], []
    for m in movs:
        if m[0] in {c for c, _ in actual}:
            grupos.append(actual)
            actual = []
        actual.append(m)
    grupos.append(actual)
    return grupos


def se_pueden_unir(grupos):
    if len(grupos) < 3:
        return False
    a = {c for c, _ in grupos[-1]}
    b = {c for c, _ in grupos[0]}
    return not (a & b)


def analizar_cascada(movs, unir_extremos=False):
    grupos = agrupar(movs)
    unidos = False
    if unir_extremos and se_pueden_unir(grupos):
        grupos = [grupos[-1] + grupos[0]] + grupos[1:-1]
        unidos = True
    n = len(grupos)
    if n > len(ROMANOS):
        raise ValueError("demasiados grupos")
    primero = movs[0]
    cambios, mandos = [], []
    for k, g in enumerate(grupos):
        siguiente = (k + 1) % n
        sensor = fin_de(g[-1])
        con_marcha = (siguiente == 0) and not unidos
        cambios.append((sensor, ROMANOS[k], ROMANOS[siguiente], con_marcha))
        for idx, m in enumerate(g):
            if idx == 0:
                if m == primero and unidos:
                    raise AssertionError("no debería pasar")
                mandos.append((m, None, ROMANOS[k], False))
            else:
                marcha = unidos and m == primero
                mandos.append((m, fin_de(g[idx - 1]), ROMANOS[k], marcha))
    return grupos, unidos, cambios, mandos


def imprimir_cascada(texto, unir_extremos=False):
    movs = parsear_secuencia(texto)
    cil = sorted({c for c, _ in movs})
    pos = posicion_inicial(movs)
    print("Secuencia: " + " ".join(mov_txt(m) for m in movs)
          + f"  ({len(movs)} movimientos, cilindros {', '.join(cil)})")
    print("Reposo: " + ", ".join(f"{c} {'retraído' if pos[c] == 0 else 'extendido'}"
                                 f" ({c.lower()}{pos[c]} activo)" for c in cil))

    mando, conflictos, repetidos = analizar_intuitivo(movs)
    print("\nMétodo intuitivo (cada movimiento lo manda el fin de carrera del anterior):")
    for i, m in enumerate(movs):
        pre = "Marcha · " if i == 0 else ""
        print(f"  {mov_txt(m):<3} <- {pre}{sensor_txt(mando[i])}")
    if not conflictos and not repetidos:
        print("  Sin señales en conflicto: el método intuitivo alcanza (válvulas biestables).")
    else:
        for quiere, opuesto, s in conflictos:
            print(f"  CONFLICTO en {quiere[0]}: cuando tiene que hacer {mov_txt(quiere)} sigue activa"
                  f" {sensor_txt(s)}, que manda {mov_txt(opuesto)}.")
        for s, m1, m2 in repetidos:
            print(f"  AMBIGÜEDAD: {sensor_txt(s)} mandaría a la vez {mov_txt(m1)} y {mov_txt(m2)}.")
        print("  -> Hace falta anular señales: método cascada, paso a paso o relés/PLC.")

    grupos, unidos, cambios, mandos = analizar_cascada(movs, unir_extremos)
    n = len(grupos)
    print("\nMétodo cascada:")
    print("  Grupos (ninguna letra se repite dentro de un grupo): "
          + "   ".join(f"{ROMANOS[k]} = [{' '.join(mov_txt(m) for m in g)}]" for k, g in enumerate(grupos)))
    if unidos:
        print("  (se unieron el último y el primer grupo: el ciclo arranca dentro del grupo I)")
    print(f"  Líneas de presión: {n}   Válvulas memoria (4/2 o 5/2 biestables): {n - 1}")
    print("  Cambios de grupo (el sensor se alimenta de la línea del grupo que termina):")
    for s, desde, hasta, marcha in cambios:
        pre = "Marcha · " if marcha else ""
        print(f"    {pre}{sensor_txt(s)} (línea {desde}) -> activa la línea {hasta}")
    print("  Mando de cada movimiento:")
    for m, s, linea, marcha in mandos:
        if s is None:
            print(f"    {mov_txt(m):<3}: directo de la línea {linea}")
        else:
            pre = "Marcha · " if marcha else ""
            print(f"    {mov_txt(m):<3}: {pre}{sensor_txt(s)} alimentado por la línea {linea}")
    reposo = "I" if unidos else ROMANOS[n - 1]
    print(f"  En reposo queda con presión la línea {reposo}.")
    if not unidos and se_pueden_unir(agrupar(movs)):
        print("  Nota: el último y el primer grupo no comparten cilindros; con --unir-extremos"
              " queda un grupo menos.")
    if n == 2:
        print("  Con una sola memoria 5/2: línea I en la salida 4 (se activa con el pilotaje 14)"
              " y línea II en la salida 2 (pilotaje 12).")
    print("\nOtros métodos:")
    if n >= 3:
        print(f"  Paso a paso neumático: una memoria por paso -> {n} memorias con estos grupos,"
              f" o {len(movs)} con un paso por movimiento.")
    else:
        print(f"  Paso a paso neumático: una memoria por paso y como mínimo 3 pasos (con 2, el paso"
              f" anterior y el siguiente serían la misma memoria) -> {len(movs)} memorias con un paso"
              f" por movimiento.")
    reles = f"{n - 1} relé" + ("s" if n - 1 > 1 else "")
    print(f"  Electroneumática: cascada con {reles} con autorretención, o paso a paso"
          f" con un relé por paso; en PLC, una marca (etapa de GRAFCET) por paso.")


# ------------------------------------------------------------------ demo

def demo():
    print("=" * 78)
    print("1) Cilindro de doble efecto Ø50/20, 6 bar, carrera 200 mm, eta 0,7, 10 ciclos/min")
    print("=" * 78)
    r = calc_cilindro(50, 20, 6, 200, eta=0.7, ciclos=10, tiempo=0.5)
    imprimir_cilindro(r)
    print()
    print("=" * 78)
    print("2) Diámetro para empujar 800 N a 6 bar con eta 0,7 (operación dinámica: eta <= 0,5 según SMC)")
    print("=" * 78)
    for eta in (0.7, 0.5):
        dmin, dad = diametro_para(800, 6, eta)
        print(f"  eta = {num(eta, 1)}: D mín = raíz(4·F/(pi·p·eta)) = {num(dmin, 1)} mm -> se adopta Ø{dad} mm")
    print()
    print("=" * 78)
    print('3) Cascada para "A+ B+ B- A-"')
    print("=" * 78)
    imprimir_cascada("A+ B+ B- A-")
    print()
    print("=" * 78)
    print("4) Pandeo: vástago Ø10 (cilindro Ø25), L = 400 mm, caso 1, fuerza 295 N")
    print("=" * 78)
    imprimir_pandeo(calc_pandeo(10, L=400, beta=EULER[1][0], F=295), caso=1)
    print()
    imprimir_pandeo(calc_pandeo(10, beta=EULER[1][0], F=295), caso=1)


# ------------------------------------------------------------------ CLI

def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(
        prog="neumatica.py",
        description="Cálculos de neumática: cilindros, tabla de fuerzas, método cascada y pandeo (Euler).",
        epilog="Ejemplo resuelto: python neumatica.py demo")
    sub = ap.add_subparsers(dest="cmd")

    c = sub.add_parser("cilindro", help="fuerzas, consumo y velocidad de un cilindro")
    c.add_argument("--D", type=float, help="diámetro del émbolo [mm]")
    c.add_argument("--d", type=float, help="diámetro del vástago [mm] (si falta, el típico de catálogo)")
    c.add_argument("--p", type=float, required=True, help="presión manométrica de trabajo [bar]")
    c.add_argument("--carrera", type=float, default=100.0, help="carrera [mm] (100 por defecto)")
    c.add_argument("--eta", type=float, default=1.0, help="rendimiento o factor de carga (1 = fuerza teórica)")
    c.add_argument("--ciclos", type=float, help="ciclos por minuto, para el consumo")
    c.add_argument("--tiempo", type=float, help="tiempo de avance [s], para velocidad y caudal")
    c.add_argument("--simple", action="store_true", help="simple efecto (retorno por resorte)")
    c.add_argument("--fuerza", type=float, help="fuerza útil pedida [N]: calcula el diámetro normalizado")
    c.add_argument("--patm", type=float, default=P_ATM, help="presión atmosférica [bar] (1,013)")

    t = sub.add_parser("tabla", help="fuerzas de los diámetros usuales")
    t.add_argument("--p", type=float, default=6.0, help="presión manométrica [bar] (6)")
    t.add_argument("--eta", type=float, default=1.0, help="rendimiento o factor de carga (1)")

    k = sub.add_parser("cascada", help="grupos de cascada y conflictos de una secuencia")
    k.add_argument("secuencia", help='secuencia entre comillas, por ejemplo "A+ B+ B- A-"')
    k.add_argument("--unir-extremos", action="store_true",
                   help="unir el último y el primer grupo si no comparten cilindros")

    pz = sub.add_parser("pandeo", help="pandeo del vástago por Euler")
    pz.add_argument("--d", type=float, required=True, help="diámetro del vástago [mm]")
    pz.add_argument("--L", type=float, help="longitud de pandeo sin el factor del caso [mm]")
    pz.add_argument("--caso", type=int, choices=[1, 2, 3, 4], default=2,
                    help="caso de Euler: 1 empotrado-libre, 2 articulado-articulado (defecto),"
                         " 3 empotrado-articulado, 4 empotrado-empotrado")
    pz.add_argument("--F", type=float, help="fuerza axial de compresión [N]")
    pz.add_argument("--E", type=float, default=210000.0, help="módulo de elasticidad [N/mm²] (acero 210000)")
    pz.add_argument("--seguridad", type=float, default=3.5, help="coeficiente de seguridad (3,5)")

    sub.add_parser("demo", help="ejemplo resuelto")

    a = ap.parse_args(argv)
    try:
        if a.cmd == "cilindro":
            if a.fuerza:
                dmin, dad = diametro_para(a.fuerza, a.p, a.eta)
                print(f"Para {num(a.fuerza, 0)} N útiles a {num(a.p, 1)} bar con eta = {num(a.eta, 2)}:"
                      f" D mín = {num(dmin, 1)} mm -> Ø normalizado {dad if dad else 'mayor que 320'} mm")
                if a.D is None:
                    a.D = dad
                print()
            if a.D is None:
                ap.error("falta --D (o --fuerza)")
            d = a.d if a.d is not None else VASTAGO_TIPICO.get(int(a.D)) if a.D == int(a.D) else None
            if d is None and not a.simple:
                ap.error("falta --d: no hay vástago típico cargado para ese diámetro")
            if a.d is None and d is not None:
                print(f"(vástago típico de catálogo para Ø{int(a.D)}: Ø{d} mm; confirmarlo con el cilindro elegido)")
            r = calc_cilindro(a.D, d, a.p, a.carrera, a.eta, a.ciclos, a.simple, a.tiempo, a.patm)
            imprimir_cilindro(r, a.simple)
        elif a.cmd == "tabla":
            imprimir_tabla(a.p, a.eta)
        elif a.cmd == "cascada":
            imprimir_cascada(a.secuencia, a.unir_extremos)
        elif a.cmd == "pandeo":
            r = calc_pandeo(a.d, a.L, EULER[a.caso][0], a.E, a.seguridad, a.F)
            imprimir_pandeo(r, a.caso)
        elif a.cmd == "demo":
            demo()
        else:
            ap.print_help()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
