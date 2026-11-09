#!/usr/bin/env python3
"""Calculadora de ensayos de materiales para trabajos prácticos e informes de laboratorio.

Solo biblioteca estándar (Python 3.9 o más nuevo). Los números se escriben con coma
o con punto decimal (4,12 o 4.12).

Subcomandos:
  brinell   HBW desde la fuerza, la bola y la huella, con las verificaciones de ISO 6506-1
  vickers   HV desde la fuerza y las diagonales, con espesor y distancias mínimas (ISO 6507-1)
  traccion  E, Rp0,2, Rm, Agt, A y Z desde un CSV de fuerza y alargamiento (ISO 6892-1)
  charpy    energía absorbida desde los ángulos del péndulo
  demo      ejemplos resueltos (los mismos que en SKILL.md)

Ejemplos:
  python ensayos.py brinell --kgf 3000 --D 10 --d1 4,10 --d2 4,14 --material acero
  python ensayos.py brinell --material cobre --D 5 --sugerir
  python ensayos.py vickers --kgf 30 --d1 0,512 --d2 0,520
  python ensayos.py traccion ensayo.csv --d0 10 --L0 50 --Lu 62,5 --du 6,2
  python ensayos.py traccion ensayo.csv --d0 10 --L0 50 --E-ref 205000   (sin extensómetro)
  python ensayos.py charpy --E0 300 --alfa 150 --beta 100
  python ensayos.py demo
  python ensayos.py demo --csv traccion_demo.csv      (además guarda el CSV del ejemplo)

CSV de tracción: dos columnas numéricas (fuerza y alargamiento), con o sin encabezado.
Se aceptan separadores ';', ',' o tabulación, y coma decimal si el separador es ';' o tabulación.
Por defecto la fuerza está en N y el alargamiento en mm (ver --unidad-fuerza y --col-*).
Si la planilla usa punto de miles (39.270,5), conviene exportarla sin separador de miles.
"""
from __future__ import annotations

import argparse
import csv
import math
import sys

G = 9.80665  # m/s², 1 kgf = 9,80665 N

# ISO 6506-1, tabla 3: índice 0,102·F/D² recomendado (material, rango de dureza)
RELACIONES_BRINELL = {
    "acero": "30 (aceros, aleaciones de níquel y de titanio)",
    "fundicion": "10 si < 140 HBW; 30 si >= 140 HBW",
    "cobre": "5 si < 35 HBW; 10 entre 35 y 200 HBW; 30 si > 200 HBW",
    "liviano": "2,5 si < 35 HBW; 5, 10 o 15 entre 35 y 80 HBW; 10 o 15 si > 80 HBW",
    "plomo": "1 (plomo y estaño)",
}
RELACION_TIPICA = {"acero": [30], "fundicion": [10, 30], "cobre": [5, 10, 30],
                   "liviano": [2.5, 5, 10, 15], "plomo": [1]}
E_TIPICO = {"acero": 203000.0, "aluminio": 69000.0, "cobre": 110000.0}  # MPa, orientativos a 21 °C


# ------------------------------------------------------------------ utilidades

def num(texto: str) -> float:
    try:
        return float(str(texto).replace(",", "."))
    except ValueError:
        raise argparse.ArgumentTypeError(f"no es un número: {texto!r}")


def f(x: float, nd: int = 2) -> str:
    """Formato argentino: punto de miles y coma decimal."""
    s = f"{x:,.{nd}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def g(x: float) -> str:
    """Número corto: 3000 -> '3000'; 187,5 -> '187,5'; 0,2 -> '0,2'."""
    if abs(x - round(x)) < 0.005:
        return str(int(round(x)))
    return f"{x:.3f}".rstrip("0").rstrip(".").replace(".", ",")


def titulo(texto: str) -> None:
    print()
    print(texto)
    print("-" * len(texto))


def fuerza_N(F=None, kgf=None) -> float:
    if F is None and kgf is None:
        raise ValueError("falta la fuerza: --F en N o --kgf en kgf")
    return F if F is not None else kgf * G


# ------------------------------------------------------------------ Brinell

def brinell(F_N: float, D: float, d: float) -> dict:
    if d >= D:
        raise ValueError("el diámetro de la huella tiene que ser menor que el de la bola")
    h = (D - math.sqrt(D * D - d * d)) / 2.0             # profundidad de la huella [mm]
    hbw = (F_N / G) / (math.pi * D * h)                  # = 0,102·2F/(πD(D - √(D² - d²)))
    return {"HBW": hbw, "h": h, "relacion": F_N / G / D ** 2, "d": d, "D": D, "F": F_N,
            "dD": d / D, "espesor_min": 8.0 * h, "entre_centros": 3.0 * d, "al_borde": 2.5 * d}


def rm_desde_hb(hb: float) -> float:
    """Aproximación para aceros: Rm ≈ 3,55·HB (HB <= 175) o 3,38·HB (HB > 175)."""
    return (3.55 if hb <= 175 else 3.38) * hb


def imprimir_brinell(r: dict, material=None, tiempo=None) -> None:
    titulo("Dureza Brinell (ISO 6506-1)")
    kgf = r["F"] / G
    print(f"F = {f(r['F'], 1)} N ({g(kgf)} kgf); D = {g(r['D'])} mm; d medio = {f(r['d'], 3)} mm")
    print(f"HBW = 0,102·2F / (π·D·(D - √(D² - d²))) = {f(r['HBW'], 1)}")
    desig = f"{round(r['HBW']):d} HBW {g(r['D'])}/{g(kgf)}" + (f"/{g(tiempo)}" if tiempo and not 10 <= tiempo <= 15 else "")
    print(f"Se informa: {desig}")
    print(f"Índice de carga 0,102·F/D² = {f(r['relacion'], 2)}", end="")
    if material:
        print(f"; recomendado para {material}: {RELACIONES_BRINELL[material]}")
        if not any(abs(r["relacion"] - k) < 0.05 * k for k in RELACION_TIPICA[material]):
            print("  Atención: el índice no es uno de los recomendados para ese material.")
    else:
        print()
    ok = 0.24 <= r["dD"] <= 0.6
    print(f"d/D = {f(r['dD'], 3)} -> {'válido' if ok else 'FUERA del rango 0,24·D a 0,6·D: repetir con otra fuerza o bola'}")
    print(f"Profundidad h = (D - √(D² - d²))/2 = {f(r['h'], 3)} mm -> espesor mínimo de la pieza 8·h = {f(r['espesor_min'], 2)} mm")
    print(f"Distancias mínimas: entre centros 3·d = {f(r['entre_centros'], 1)} mm; centro al borde 2,5·d = {f(r['al_borde'], 1)} mm")
    print(f"Tiempos: carga en 2 a 8 s; mantener la fuerza 10 a 15 s. Máximo del método: 650 HBW.")
    if material in (None, "acero"):
        print(f"Solo aceros, aproximado: Rm ≈ {f(rm_desde_hb(r['HBW']), 0)} MPa "
              f"({'3,55' if r['HBW'] <= 175 else '3,38'}·HB). Para un valor formal usar las tablas de ISO 18265.")


def sugerir_brinell(material: str, D: float) -> None:
    titulo(f"Fuerzas Brinell recomendadas para {material} con bola de {g(D)} mm")
    for k in RELACION_TIPICA[material]:
        F = k * D * D * G
        print(f"índice {g(k)}: F = {g(k)}·D²·9,80665 = {f(F, 1)} N ({g(k * D * D)} kgf) -> HBW {g(D)}/{g(k * D * D)}")
    print(f"Criterio de elección: {RELACIONES_BRINELL[material]}. La huella tiene que quedar entre "
          f"{f(0.24 * D, 2)} y {f(0.6 * D, 2)} mm.")


# ------------------------------------------------------------------ Vickers

def vickers(F_N: float, d1: float, d2: float) -> dict:
    d = (d1 + d2) / 2.0
    hv = 2.0 * math.sin(math.radians(68.0)) * (F_N / G) / d ** 2   # = 0,1891·F/d²
    return {"HV": hv, "d": d, "F": F_N, "espesor_min": 1.5 * d}


def imprimir_vickers(r: dict, liviano=False, tiempo=None) -> None:
    titulo("Dureza Vickers (ISO 6507-1)")
    kgf = r["F"] / G
    tipo = ("ensayo Vickers" if r["F"] >= 49.03 else
            "Vickers de baja fuerza" if r["F"] >= 1.961 else "microdureza Vickers")
    print(f"F = {f(r['F'], 3)} N (HV {g(kgf)}, {tipo}); diagonal media d = {f(r['d'], 4)} mm")
    print(f"HV = 0,1891·F/d² = {f(r['HV'], 1)}")
    desig = f"{round(r['HV']):d} HV {g(kgf)}" + (f"/{g(tiempo)}" if tiempo and not 10 <= tiempo <= 15 else "")
    print(f"Se informa: {desig}")
    print(f"Espesor mínimo de la pieza: 1,5·d = {f(r['espesor_min'], 3)} mm")
    if liviano:
        print(f"Metales livianos, plomo y estaño: centro al borde >= 3·d = {f(3 * r['d'], 3)} mm; "
              f"entre centros >= 6·d = {f(6 * r['d'], 3)} mm")
    else:
        print(f"Acero y cobre: centro al borde >= 2,5·d = {f(2.5 * r['d'], 3)} mm; "
              f"entre centros >= 3·d = {f(3 * r['d'], 3)} mm")


# ------------------------------------------------------------------ Tracción

def a_float(texto: str) -> float:
    """'39270,5', '39.270,5', '39270.5' o '39,270.5' -> 39270.5 (el último separador es el decimal)."""
    s = texto.strip().replace(" ", "").replace(" ", "")
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    else:
        s = s.replace(",", ".")
    return float(s)


def leer_csv(ruta: str, col_f: int = 0, col_l: int = 1):
    with open(ruta, encoding="utf-8-sig", newline="") as fh:
        texto = fh.read()
    muestra = texto[:4000]
    sep = ";" if ";" in muestra else ("\t" if "\t" in muestra else ",")
    F, L = [], []
    for fila in csv.reader(texto.splitlines(), delimiter=sep):
        if len(fila) <= max(col_f, col_l):
            continue
        try:
            a = a_float(fila[col_f])
            b = a_float(fila[col_l])
        except ValueError:
            continue  # encabezados, unidades o filas vacías
        F.append(a)
        L.append(b)
    if len(F) < 10:
        raise ValueError(f"el CSV tiene {len(F)} fila(s) numérica(s) en las columnas elegidas; hacen falta al menos 10")
    return F, L


def regresion(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    pend = sxy / sxx
    ord0 = my - pend * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (pend * x + ord0)) ** 2 for x, y in zip(xs, ys))
    return pend, ord0, (1.0 - ss_res / ss_tot) if ss_tot else 1.0


def analizar_traccion(F, dL, S0, L0, rango=(0.10, 0.40), E_ref=None, offset=0.002):
    sig = [x / S0 for x in F]
    eps = [x / L0 for x in dL]
    imax = max(range(len(F)), key=lambda i: F[i])
    Fmax, Rm = F[imax], F[imax] / S0
    pts = [(e, s) for e, s in zip(eps[:imax + 1], sig[:imax + 1]) if rango[0] * Rm <= s <= rango[1] * Rm]
    if len(pts) < 3:
        raise ValueError("pocos puntos en el tramo elástico: revisar --rango o las unidades")
    E_fit, b, R2 = regresion([p[0] for p in pts], [p[1] for p in pts])
    eps0 = -b / E_fit                                     # corrección del pie de la curva
    E = E_fit
    if E_ref:                                              # corrección de la deformación de la máquina
        eps = [e - s / E_fit + s / E_ref for e, s in zip(eps, sig)]
        E = E_ref
    # Rp: intersección con la recta paralela desplazada 'offset'
    rp = None
    for i in range(1, imax + 1):
        g0 = sig[i - 1] - E * (eps[i - 1] - eps0 - offset)
        g1 = sig[i] - E * (eps[i] - eps0 - offset)
        if g0 > 0 >= g1:
            t = g0 / (g0 - g1)
            rp = sig[i - 1] + t * (sig[i] - sig[i - 1])
            break
    # fluencia discontinua (indicativo): primer máximo local seguido de una caída > 0,5 %
    reh = rel = None
    for i in range(1, imax):
        if sig[i] >= sig[i - 1] and sig[i] > sig[i + 1] and sig[i] < 0.98 * Rm and sig[i] > rango[1] * Rm:
            j = i + 1
            while j < imax and sig[j] <= sig[i]:
                j += 1
            tramo = sig[i + 1:j]
            if tramo and min(tramo) < 0.995 * sig[i]:
                # mínimos locales de la meseta; el primero es el efecto transitorio inicial y se ignora
                minimos = [tramo[k] for k in range(len(tramo))
                           if (k == 0 or tramo[k] <= tramo[k - 1]) and (k == len(tramo) - 1 or tramo[k] <= tramo[k + 1])]
                reh = sig[i]
                rel = min(minimos[1:]) if len(minimos) >= 2 else min(tramo)
            break
    ifr = max(i for i in range(len(F)) if F[i] >= 0.1 * Fmax)
    sf = sig[ifr]
    A_curva = (eps[ifr] - eps0 - sf / E) * 100.0
    Agt = (eps[imax] - eps0) * 100.0
    return {"S0": S0, "L0": L0, "Fmax": Fmax, "Rm": Rm, "E": E, "E_fit": E_fit, "R2": R2, "npts": len(pts),
            "eps0": eps0, "Rp": rp, "ReH": reh, "ReL": rel, "A_curva": A_curva, "Agt": Agt,
            "Ag": Agt - Rm / E * 100.0, "sf": sf, "E_ref": E_ref, "offset": offset}


def imprimir_traccion(r, Lu=None, Su=None, du=None, material=None):
    titulo("Ensayo de tracción (ISO 6892-1)")
    k = r["L0"] / math.sqrt(r["S0"])
    tipo = ("proporcional corta (k = 5,65)" if abs(k - 5.65) < 0.1 else
            "proporcional larga (k = 11,3): informar A11,3" if abs(k - 11.3) < 0.2 else
            f"no proporcional: informar A{g(r['L0'])}mm")
    print(f"S0 = {f(r['S0'], 2)} mm²; L0 = {f(r['L0'], 2)} mm; k = L0/√S0 = {f(k, 2)} -> probeta {tipo}")
    print(f"Fmax = {f(r['Fmax'] / 1000, 2)} kN -> Rm = Fmax/S0 = {f(r['Rm'], 1)} MPa")
    print(f"Módulo E (regresión en el tramo recto, {r['npts']} puntos, R² = {f(r['R2'], 5)}): "
          f"{f(r['E_fit'] / 1000, 1)} GPa")
    if r["E_ref"]:
        print(f"Deformación corregida con E de referencia = {f(r['E_ref'] / 1000, 1)} GPa (sin extensómetro): "
              "se saca la deformación elástica de la máquina. Rp y A siguen siendo estimaciones, porque el "
              "travesaño también mide la deformación plástica fuera de L0; A se informa medido sobre la probeta.")
    ref = E_TIPICO.get(material) if material else None
    if ref and not r["E_ref"] and r["E_fit"] < 0.8 * ref:
        print(f"Atención: E sale muy por debajo del típico ({f(ref / 1000, 0)} GPa). Si el alargamiento es del "
              "travesaño y no de un extensómetro, E no es válido; usar --E-ref para estimar Rp y A.")
    if r["Rp"]:
        print(f"Rp{g(r['offset'] * 100)} (recta paralela desplazada {g(r['offset'] * 100)} %) = {f(r['Rp'], 1)} MPa")
    if r["ReH"]:
        print(f"Posible fluencia discontinua: ReH ≈ {f(r['ReH'], 1)} MPa; ReL ≈ {f(r['ReL'], 1)} MPa "
              "(sin el transitorio inicial). Verificar en el gráfico: con meseta se informan ReH y ReL, no Rp0,2.")
    print(f"Agt (alargamiento total a fuerza máxima) = {f(r['Agt'], 1)} %; Ag (plástico) = {f(r['Ag'], 1)} %")
    print(f"A desde la curva (alargamiento a la rotura menos la parte elástica σf/E) = {f(r['A_curva'], 1)} %")
    if Lu:
        A = (Lu - r["L0"]) / r["L0"] * 100.0
        print(f"A medido sobre la probeta = (Lu - L0)/L0·100 = ({g(Lu)} - {g(r['L0'])})/{g(r['L0'])}·100 = {f(A, 1)} % (este se informa)")
    if du and not Su:
        Su = math.pi * du ** 2 / 4.0
    if Su:
        Z = (r["S0"] - Su) / r["S0"] * 100.0
        print(f"Su = {f(Su, 2)} mm² -> Z = (S0 - Su)/S0·100 = {f(Z, 1)} %")
    if r["Rp"]:
        print(f"Relación Rp/Rm = {f(r['Rp'] / r['Rm'], 3)} (Rm/Rp = {f(r['Rm'] / r['Rp'], 3)})")


def curva_demo(S0=math.pi * 25.0, L0=50.0, E=205000.0, rp=350.0, slp=200.0, n=6.2, Rm=500.0,
               sf=400.0, A=25.0):
    """Curva sintética de un acero: recta hasta slp, plástico tipo Ramberg-Osgood (εp = 0,002 en rp)
    hasta 490 MPa, parábola hasta el máximo (Rm) y estricción hasta la rotura (σf, A)."""
    pts = []
    sa = Rm - 10.0
    for i in range(0, 241):
        s = sa * i / 240.0
        pts.append((s / E + plastica(s, rp, slp, n), s))
    ea = pts[-1][0]
    pend = 1.0 / (1.0 / E + n * plastica(sa, rp, slp, n) / (sa - slp))   # dσ/dε al final del tramo
    delta = 2.0 * (Rm - sa) / pend
    c1 = pend / (2.0 * delta)
    eu = ea + delta
    for i in range(1, 61):
        e = ea + delta * i / 60.0
        pts.append((e, Rm - c1 * (eu - e) ** 2))
    ef = A / 100.0 + sf / E
    c2 = (Rm - sf) / (ef - eu) ** 2
    for i in range(1, 101):
        e = eu + (ef - eu) * i / 100.0
        pts.append((e, Rm - c2 * (e - eu) ** 2))
    F = [s * S0 for e, s in pts]
    dL = [e * L0 for e, s in pts]
    return F, dL


def plastica(s, rp, slp, n):
    """Deformación plástica: 0 hasta slp; 0,002 justo en rp."""
    return 0.0 if s <= slp else 0.002 * ((s - slp) / (rp - slp)) ** n


# ------------------------------------------------------------------ Charpy

def charpy(E0=None, alfa=None, beta=None, WL=None, beta0=None):
    """Energía absorbida K = W·L·(cos β - cos α); con β0 (vuelo libre) corrige rozamiento: W·L·(cos β - cos β0)."""
    a, b = math.radians(alfa), math.radians(beta)
    if WL is None:
        WL = E0 / (1.0 - math.cos(a))
    E0 = WL * (1.0 - math.cos(a))
    K = WL * (math.cos(b) - math.cos(a))
    Kc = WL * (math.cos(b) - math.cos(math.radians(beta0))) if beta0 is not None else None
    return {"WL": WL, "E0": E0, "K": K, "Kc": Kc}


def imprimir_charpy(r, alfa, beta, beta0=None):
    titulo("Impacto Charpy (ISO 148-1)")
    print(f"W·L = {f(r['WL'], 2)} J; energía inicial E0 = W·L·(1 - cos α) = {f(r['E0'], 1)} J (α = {g(alfa)}°)")
    print(f"Energía absorbida K = W·L·(cos β - cos α) = {f(r['K'], 1)} J (β = {g(beta)}°)")
    if r["Kc"] is not None:
        print(f"Corregida por rozamiento con el vuelo libre (β0 = {g(beta0)}°): K ≈ {f(r['Kc'], 1)} J")
    k = r["Kc"] if r["Kc"] is not None else r["K"]
    if k > 0.8 * r["E0"]:
        print("Atención: K supera el 80 % de la energía inicial: resultado aproximado; usar un péndulo de más energía.")
    print("Se informa como KV2 o KV8 (entalla en V, percutor de 2 u 8 mm) o KU2/KU8, con la temperatura de ensayo.")


# ------------------------------------------------------------------ demo

def demo(csv_salida=None):
    print("DEMO: ejemplos resueltos de la skill ensayos-materiales")
    imprimir_brinell(brinell(3000 * G, 10.0, (4.10 + 4.14) / 2), material="acero")
    imprimir_vickers(vickers(30 * G, 0.512, 0.520))
    F, dL = curva_demo()
    if csv_salida:
        with open(csv_salida, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter=";")
            w.writerow(["fuerza_N", "alargamiento_mm"])
            for a, b in zip(F, dL):
                w.writerow([f"{a:.1f}".replace(".", ","), f"{b:.5f}".replace(".", ",")])
        print(f"\n(CSV del ejemplo guardado en {csv_salida})")
    r = analizar_traccion(F, dL, math.pi * 25.0, 50.0)
    imprimir_traccion(r, Lu=62.5, du=6.2, material="acero")
    imprimir_charpy(charpy(E0=300.0, alfa=150.0, beta=100.0), 150.0, 100.0)


# ------------------------------------------------------------------ CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")

    sp = sub.add_parser("brinell", help="dureza Brinell HBW")
    sp.add_argument("--F", type=num, help="fuerza [N]")
    sp.add_argument("--kgf", type=num, help="fuerza [kgf] (3000, 1000, 750...)")
    sp.add_argument("--D", type=num, required=True, help="diámetro de la bola [mm] (10, 5, 2,5 o 1)")
    sp.add_argument("--d", type=num, help="diámetro medio de la huella [mm]")
    sp.add_argument("--d1", type=num, help="diámetro de la huella, primera lectura [mm]")
    sp.add_argument("--d2", type=num, help="diámetro de la huella a 90° [mm]")
    sp.add_argument("--material", choices=sorted(RELACIONES_BRINELL), help="para verificar el índice de carga")
    sp.add_argument("--tiempo", type=num, help="tiempo de mantenimiento [s] (si no es 10 a 15 s va en la designación)")
    sp.add_argument("--sugerir", action="store_true", help="listar las fuerzas recomendadas para el material y la bola")

    sp = sub.add_parser("vickers", help="dureza Vickers HV")
    sp.add_argument("--F", type=num, help="fuerza [N]")
    sp.add_argument("--kgf", type=num, help="fuerza [kgf] (30 para HV 30)")
    sp.add_argument("--d1", type=num, required=True, help="primera diagonal [mm]")
    sp.add_argument("--d2", type=num, required=True, help="segunda diagonal [mm]")
    sp.add_argument("--liviano", action="store_true", help="metales livianos, plomo o estaño (distancias mayores)")
    sp.add_argument("--tiempo", type=num, help="tiempo de mantenimiento [s]")

    sp = sub.add_parser("traccion", help="E, Rp0,2, Rm, A y Z desde un CSV")
    sp.add_argument("csv", help="archivo CSV con fuerza y alargamiento")
    sp.add_argument("--d0", type=num, help="diámetro inicial [mm] (probeta redonda)")
    sp.add_argument("--a0", type=num, help="espesor inicial [mm] (probeta plana)")
    sp.add_argument("--b0", type=num, help="ancho inicial [mm] (probeta plana)")
    sp.add_argument("--S0", type=num, help="sección inicial [mm²]")
    sp.add_argument("--L0", type=num, required=True, help="longitud inicial entre marcas [mm]")
    sp.add_argument("--Lu", type=num, help="longitud final entre marcas medida [mm]")
    sp.add_argument("--du", type=num, help="diámetro mínimo en la rotura [mm]")
    sp.add_argument("--Su", type=num, help="sección mínima en la rotura [mm²]")
    sp.add_argument("--unidad-fuerza", choices=("N", "kN", "kgf"), default="N")
    sp.add_argument("--col-fuerza", type=int, default=1, help="número de columna de la fuerza (1)")
    sp.add_argument("--col-alargamiento", type=int, default=2, help="número de columna del alargamiento en mm (2)")
    sp.add_argument("--rango", type=num, nargs=2, default=[0.10, 0.40],
                    help="tramo para E como fracción de Rm (0,10 0,40)")
    sp.add_argument("--E-ref", dest="E_ref", type=num, help="E de referencia [MPa] si no hubo extensómetro")
    sp.add_argument("--material", choices=sorted(E_TIPICO), help="para comparar E con el típico")

    sp = sub.add_parser("charpy", help="energía absorbida desde los ángulos del péndulo")
    sp.add_argument("--E0", type=num, help="energía inicial del péndulo [J]")
    sp.add_argument("--WL", type=num, help="peso por distancia al centro de masa W·L [J] (en lugar de E0)")
    sp.add_argument("--alfa", type=num, required=True, help="ángulo de caída desde la vertical [°]")
    sp.add_argument("--beta", type=num, required=True, help="ángulo de subida después de romper [°]")
    sp.add_argument("--beta0", type=num, help="ángulo de subida en vuelo libre, sin probeta [°]")

    sp = sub.add_parser("demo", help="ejemplos resueltos")
    sp.add_argument("--csv", help="guardar el CSV de tracción del ejemplo")

    a = ap.parse_args(argv)
    try:
        if a.cmd == "brinell":
            if a.sugerir:
                sugerir_brinell(a.material or "acero", a.D)
                return 0
            d = a.d if a.d is not None else ((a.d1 + a.d2) / 2 if a.d1 and a.d2 else None)
            if d is None:
                raise ValueError("falta la huella: --d, o --d1 y --d2")
            imprimir_brinell(brinell(fuerza_N(a.F, a.kgf), a.D, d), a.material, a.tiempo)
        elif a.cmd == "vickers":
            imprimir_vickers(vickers(fuerza_N(a.F, a.kgf), a.d1, a.d2), a.liviano, a.tiempo)
        elif a.cmd == "traccion":
            if a.S0:
                S0 = a.S0
            elif a.d0:
                S0 = math.pi * a.d0 ** 2 / 4.0
            elif a.a0 and a.b0:
                S0 = a.a0 * a.b0
            else:
                raise ValueError("falta la sección: --d0, o --a0 y --b0, o --S0")
            F, dL = leer_csv(a.csv, a.col_fuerza - 1, a.col_alargamiento - 1)
            esc = {"N": 1.0, "kN": 1000.0, "kgf": G}[a.unidad_fuerza]
            F = [x * esc for x in F]
            r = analizar_traccion(F, dL, S0, a.L0, tuple(a.rango), a.E_ref)
            imprimir_traccion(r, a.Lu, a.Su, a.du, a.material)
        elif a.cmd == "charpy":
            if a.E0 is None and a.WL is None:
                raise ValueError("falta --E0 o --WL")
            imprimir_charpy(charpy(a.E0, a.alfa, a.beta, a.WL, a.beta0), a.alfa, a.beta, a.beta0)
        elif a.cmd == "demo":
            demo(a.csv)
        else:
            ap.print_help()
    except (ValueError, OSError, ZeroDivisionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
