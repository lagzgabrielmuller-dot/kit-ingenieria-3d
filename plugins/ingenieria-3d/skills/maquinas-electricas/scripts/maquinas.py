#!/usr/bin/env python3
"""Calculadora de máquinas eléctricas para trabajos prácticos, ensayos y exámenes.

Solo biblioteca estándar (Python 3.9 o más nuevo). Los números se escriben con coma
o con punto decimal (0,82 o 0.82). Rendimiento y cos(phi) se aceptan en % o en fracción.

Subcomandos:
  motor       placa de un motor asincrónico trifásico: ns, s, f2, In, cupla, pérdidas y Kloss
  balance     balance de potencias del motor asincrónico (P1 -> Pag -> Pmi -> Pu)
  arranque    comparativo: directo, estrella-triángulo, autotransformador y tensión reducida
  trafo       transformador: circuito equivalente desde los ensayos, regulación y rendimiento
  sincronica  pares de polos y velocidad; P y Q de una máquina de rotor liso
  steinmetz   capacitor orientativo para un motor trifásico en red monofásica
  demo        ejemplos resueltos (los mismos que en SKILL.md)

Ejemplos:
  python maquinas.py motor --P 7,5 --U 380 --n 1455 --eta 90,4 --cosphi 0,82 --TmaxTn 2,8
  python maquinas.py balance --P1 8300 --Pcu1 300 --Pfe 200 --s 3 --Pmec 80
  python maquinas.py arranque --P 7,5 --U 380 --n 1455 --eta 90,4 --cosphi 0,82 --IaIn 7 --TaTn 2,3 --Tr 25
  python maquinas.py trafo --S 315 --U1 13200 --U2 400 --U0 400 --I0 6,8 --P0 720 --Ucc 528 --Pcc 3900
  python maquinas.py sincronica --f 50 --n 71,4
  python maquinas.py steinmetz --P 1,5 --U 220
  python maquinas.py demo
"""
from __future__ import annotations

import argparse
import cmath
import math
import sys

RAIZ3 = math.sqrt(3.0)


# ------------------------------------------------------------------ utilidades

def num(texto: str) -> float:
    """Convierte '0,82' o '0.82' a float (para argparse)."""
    try:
        return float(str(texto).replace(",", "."))
    except ValueError:
        raise argparse.ArgumentTypeError(f"no es un número: {texto!r}")


def fraccion(x: float) -> float:
    """90,4 -> 0,904 ; 0,904 -> 0,904 (rendimiento, cos(phi), deslizamiento, k)."""
    return x / 100.0 if x > 1.0 else x


def f(x: float, nd: int = 2) -> str:
    """Formato argentino: punto de miles y coma decimal (11.366,25)."""
    s = f"{x:,.{nd}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def titulo(texto: str) -> None:
    print()
    print(texto)
    print("-" * len(texto))


# ------------------------------------------------------------------ motor asincrónico

def velocidad_sincronica(f_hz: float, pares: int) -> float:
    """ns [rpm] = 60·f / p, con p = pares de polos."""
    return 60.0 * f_hz / pares


def pares_desde_velocidad(f_hz: float, n_rpm: float) -> int:
    """Pares de polos de un motor asincrónico: la ns inmediata superior a n."""
    p = int(60.0 * f_hz / n_rpm)
    if p < 1 or velocidad_sincronica(f_hz, p) <= n_rpm:
        raise ValueError("la velocidad no es compatible con un motor asincrónico a esa frecuencia")
    return p


def kloss_sk(lam: float, s_n: float) -> float:
    """Deslizamiento de cupla máxima desde lambda = Tmax/Tn y el deslizamiento nominal (Kloss)."""
    return s_n * (lam + math.sqrt(lam * lam - 1.0))


def kloss_cupla(s: float, s_k: float, t_max: float) -> float:
    """Fórmula de Kloss simplificada: T = 2·Tmax / (s/sk + sk/s)."""
    return 2.0 * t_max / (s / s_k + s_k / s)


def motor_placa(P_kW, U, n, eta, cosphi, f_hz=50.0, pares=None):
    eta, cosphi = fraccion(eta), fraccion(cosphi)
    p = pares or pares_desde_velocidad(f_hz, n)
    ns = velocidad_sincronica(f_hz, p)
    s = (ns - n) / ns
    P = P_kW * 1000.0
    P1 = P / eta
    In = P / (RAIZ3 * U * eta * cosphi)
    w = 2.0 * math.pi * n / 60.0
    Tn = P / w
    S = RAIZ3 * U * In
    Q = S * math.sqrt(1.0 - cosphi ** 2)
    return {"p": p, "polos": 2 * p, "ns": ns, "s": s, "f2": s * f_hz, "In": In, "Tn": Tn,
            "P": P, "P1": P1, "perdidas": P1 - P, "S": S, "Q": Q, "w": w, "n": n,
            "eta": eta, "cosphi": cosphi, "U": U, "f": f_hz}


def imprimir_motor(m, IaIn=None, TaTn=None, TmaxTn=None):
    titulo("Motor asincrónico trifásico (datos de placa)")
    print(f"Pares de polos p = {m['p']} ({m['polos']} polos); ns = 60·f/p = {f(m['ns'], 1)} rpm")
    print(f"Deslizamiento s = (ns - n)/ns = {f(m['s'] * 100, 2)} %; frecuencia rotórica f2 = s·f = {f(m['f2'], 2)} Hz")
    print(f"Corriente nominal In = P/(√3·U·η·cosφ) = {f(m['In'], 2)} A")
    print(f"Cupla nominal Tn = P/ω = 9550·P[kW]/n = {f(m['Tn'], 2)} N·m (ω = {f(m['w'], 2)} rad/s)")
    print(f"Potencia absorbida P1 = P/η = {f(m['P1'], 0)} W; pérdidas totales = {f(m['perdidas'], 0)} W")
    print(f"Potencia aparente S = {f(m['S'], 0)} VA; reactiva Q = {f(m['Q'], 0)} var")
    if IaIn:
        print(f"Corriente de arranque directo Ia = {f(IaIn, 2)}·In = {f(IaIn * m['In'], 1)} A")
    if TaTn:
        print(f"Cupla de arranque (catálogo) Ta = {f(TaTn, 2)}·Tn = {f(TaTn * m['Tn'], 1)} N·m")
    if TmaxTn:
        sk = kloss_sk(TmaxTn, m["s"])
        tmax = TmaxTn * m["Tn"]
        t1 = kloss_cupla(1.0, sk, tmax)
        print(f"Kloss: sk = sn·(λ + √(λ² - 1)) = {f(sk, 4)} -> cupla máxima {f(tmax, 1)} N·m a "
              f"n = {f(m['ns'] * (1 - sk), 0)} rpm")
        print(f"Kloss en s = 1 da {f(t1, 1)} N·m ({f(t1 / m['Tn'], 2)}·Tn). Para el arranque usar la Ta del "
              f"catálogo: Kloss con parámetros constantes no representa el rotor de barras profundas.")


def balance_potencias(P1, Pcu1, Pfe, s, Pmec, f_hz=50.0, pares=2):
    s = fraccion(s)
    Pag = P1 - Pcu1 - Pfe
    Pcu2 = s * Pag
    Pmi = (1.0 - s) * Pag
    Pu = Pmi - Pmec
    ns = velocidad_sincronica(f_hz, pares)
    ws = 2.0 * math.pi * ns / 60.0
    w = ws * (1.0 - s)
    return {"Pag": Pag, "Pcu2": Pcu2, "Pmi": Pmi, "Pu": Pu, "eta": Pu / P1, "Tem": Pag / ws,
            "Tu": Pu / w, "ns": ns, "n": ns * (1 - s), "s": s}


def imprimir_balance(b, P1):
    titulo("Balance de potencias del motor asincrónico")
    print(f"Potencia en el entrehierro Pag = P1 - Pcu1 - Pfe = {f(b['Pag'], 0)} W")
    print(f"Pérdidas en el cobre del rotor Pcu2 = s·Pag = {f(b['Pcu2'], 0)} W")
    print(f"Potencia mecánica interna Pmi = (1 - s)·Pag = {f(b['Pmi'], 0)} W")
    print(f"Potencia útil Pu = Pmi - Pmec = {f(b['Pu'], 0)} W; rendimiento η = Pu/P1 = {f(b['eta'] * 100, 2)} %")
    print(f"Cupla electromagnética T = Pag/ωs = Pmi/ω = {f(b['Tem'], 2)} N·m; cupla útil Tu = Pu/ω = {f(b['Tu'], 2)} N·m")
    print(f"(ns = {f(b['ns'], 0)} rpm, n = {f(b['n'], 0)} rpm)")


def arranques(In, Tn, IaIn, TaTn, ks=(0.5, 0.65, 0.8), limite=None):
    Ia, Ta = IaIn * In, TaTn * Tn
    filas = [("Directo", Ia, Ta), ("Estrella-triángulo", Ia / 3.0, Ta / 3.0)]
    for k in ks:
        k = fraccion(k)
        filas.append((f"Autotransformador {f(k * 100, 0)} % (k² = {f(k * k, 3)})", k * k * Ia, k * k * Ta))
    if limite:
        x = limite / IaIn
        filas.append((f"Tensión reducida a {f(x * 100, 1)} % (suave o resistencias, I = {f(limite, 1)}·In)",
                      x * Ia, x * x * Ta))
    return filas


def imprimir_arranques(filas, In, Tn, Tr=None):
    titulo("Comparativo de arranques (corriente de línea y cupla al arrancar)")
    ancho = max(len(r[0]) for r in filas)
    print(f"{'Método':<{ancho}}  {'I línea [A]':>11}  {'I/In':>5}  {'T [N·m]':>8}  {'T/Tn':>5}" +
          ("  ¿Arranca?" if Tr else ""))
    for nombre, i, t in filas:
        extra = ""
        if Tr:
            extra = "  sí" if t > Tr else "  NO"
        print(f"{nombre:<{ancho}}  {f(i, 1):>11}  {f(i / In, 2):>5}  {f(t, 1):>8}  {f(t / Tn, 2):>5}{extra}")
    print("Estrella-triángulo solo si el motor trabaja en triángulo a la tensión de red (placa 380/660 V "
          "o 400/690 V en red de 380 o 400 V).")
    print("Con la misma corriente de línea, el autotransformador da la misma cupla que la estrella-triángulo "
          "(k = 1/√3 = 57,7 %); la tensión reducida con resistencias o arrancador suave da menos.")
    if Tr:
        print(f"Cupla resistente al arranque: {f(Tr, 1)} N·m. Además tiene que sobrar cupla en toda la "
              "aceleración, no solo en n = 0.")


# ------------------------------------------------------------------ transformador

def trafo_ensayos(S_kVA, U1, U2, fases=3, U0=None, I0=None, P0=None, lado0="BT",
                  Ucc=None, Icc=None, Pcc=None, ladocc="AT"):
    S = S_kVA * 1000.0
    m = 3 if fases == 3 else 1
    raiz = RAIZ3 if m == 3 else 1.0
    In1, In2 = S / (raiz * U1), S / (raiz * U2)
    a = U1 / U2
    r = {"S": S, "U1": U1, "U2": U2, "In1": In1, "In2": In2, "a": a, "m": m, "raiz": raiz}
    if Ucc is not None and Pcc is not None:
        Ulado, Inlado = (U1, In1) if ladocc == "AT" else (U2, In2)
        Icc = Icc or Inlado
        Ucc_n = Ucc * Inlado / Icc            # llevado a corriente nominal
        Pcc_n = Pcc * (Inlado / Icc) ** 2
        Zcc = (Ucc_n / raiz) / Inlado          # por fase, estrella equivalente
        Rcc = (Pcc_n / m) / Inlado ** 2
        Xcc = math.sqrt(max(Zcc ** 2 - Rcc ** 2, 0.0))
        ref = a * a if ladocc == "BT" else 1.0 / (a * a)   # pasar al otro lado
        ucc = Ucc_n / Ulado * 100.0
        uR = Pcc_n / S * 100.0
        uX = math.sqrt(max(ucc ** 2 - uR ** 2, 0.0))
        r.update({"Icc_ens": Icc, "Ucc_n": Ucc_n, "Pcc_n": Pcc_n, "ucc": ucc, "uR": uR, "uX": uX,
                  "ladocc": ladocc, "Zcc": Zcc, "Rcc": Rcc, "Xcc": Xcc,
                  "Zcc_o": Zcc * ref, "Rcc_o": Rcc * ref, "Xcc_o": Xcc * ref})
    if U0 is not None and I0 is not None and P0 is not None:
        Ulado, Inlado = (U2, In2) if lado0 == "BT" else (U1, In1)
        cos0 = P0 / (raiz * U0 * I0)
        sen0 = math.sqrt(max(1.0 - cos0 ** 2, 0.0))
        Vf = U0 / raiz
        Rfe = Vf / (I0 * cos0)
        Xm = Vf / (I0 * sen0)
        ref = a * a if lado0 == "BT" else 1.0 / (a * a)
        r.update({"U0": U0, "I0": I0, "P0": P0, "lado0": lado0, "cos0": cos0, "IFe": I0 * cos0,
                  "Imu": I0 * sen0, "I0pc": I0 / Inlado * 100.0, "Rfe": Rfe, "Xm": Xm,
                  "Rfe_o": Rfe * ref, "Xm_o": Xm * ref, "U0_ok": abs(U0 - Ulado) / Ulado < 0.01})
    return r


def regulacion_aprox(C, uR, uX, cosphi, capacitivo=False):
    """Caída de tensión % (fórmula con término de 2.º orden); C = I/In."""
    sen = math.sqrt(1.0 - cosphi ** 2) * (-1.0 if capacitivo else 1.0)
    return C * (uR * cosphi + uX * sen) + C ** 2 * (uX * cosphi - uR * sen) ** 2 / 200.0


def regulacion_exacta(C, uR, uX, cosphi, capacitivo=False):
    """Primario a tensión nominal (1 pu); carga con corriente C pu y cos(phi). Devuelve caída %."""
    phi = math.acos(cosphi) * (-1.0 if capacitivo else 1.0)
    w = C * cmath.exp(-1j * phi) * complex(uR, uX) / 100.0
    v2 = -w.real + math.sqrt(1.0 - w.imag ** 2)
    return (1.0 - v2) * 100.0


def rendimiento(C, S, cosphi, P0, Pcc_n):
    P2 = C * S * cosphi
    return P2 / (P2 + P0 + C * C * Pcc_n)


def imprimir_trafo(r, C=1.0, cosphi=0.8, capacitivo=False, conexion=None):
    titulo("Transformador: datos nominales")
    print(f"Sn = {f(r['S'] / 1000, 1)} kVA; U1 = {f(r['U1'], 0)} V; U2 = {f(r['U2'], 0)} V; "
          f"relación de tensiones de línea a = U1/U2 = {f(r['a'], 3)}")
    print(f"In1 = {f(r['In1'], 2)} A (AT); In2 = {f(r['In2'], 2)} A (BT)")
    if conexion and r["m"] == 3:
        c = conexion.strip()
        lado_at, lado_bt = c[0].upper(), c[1].lower()
        u1f = r["U1"] if lado_at == "D" else r["U1"] / RAIZ3
        if lado_bt in "dy":
            u2f = r["U2"] if lado_bt == "d" else r["U2"] / RAIZ3
            print(f"Conexión {c}: tensión por bobina AT {f(u1f, 1)} V, BT {f(u2f, 1)} V -> "
                  f"relación de espiras N1/N2 = {f(u1f / u2f, 2)} (no es igual a U1/U2 si las conexiones difieren)")
        indice = "".join(ch for ch in c if ch.isdigit())
        if indice:
            print(f"Índice horario {indice}: la BT atrasa {int(indice) * 30}° respecto de la AT "
                  f"(= adelanta {360 - int(indice) * 30}°)" if int(indice) else "Índice 0: sin desfase")
    if "ucc" in r:
        titulo("Ensayo de cortocircuito")
        lado = r["ladocc"]
        print(f"Medido del lado {lado}; llevado a corriente nominal: Ucc = {f(r['Ucc_n'], 1)} V, Pcc = {f(r['Pcc_n'], 0)} W")
        print(f"ucc = {f(r['ucc'], 2)} %; uR = Pcc/Sn = {f(r['uR'], 3)} %; uX = √(ucc² - uR²) = {f(r['uX'], 3)} %")
        otro = "BT" if lado == "AT" else "AT"
        por_fase = "Por fase (estrella equivalente)" if r["m"] == 3 else "Monofásico"
        print(f"{por_fase}, referidos a {lado}: Zcc = {f(r['Zcc'], 3)} Ω; "
              f"Rcc = {f(r['Rcc'], 3)} Ω; Xcc = {f(r['Xcc'], 3)} Ω")
        print(f"Referidos a {otro}: Zcc = {f(r['Zcc_o'] * 1000, 2)} mΩ; Rcc = {f(r['Rcc_o'] * 1000, 2)} mΩ; "
              f"Xcc = {f(r['Xcc_o'] * 1000, 2)} mΩ" if r["Zcc_o"] < 1 else
              f"Referidos a {otro}: Zcc = {f(r['Zcc_o'], 3)} Ω; Rcc = {f(r['Rcc_o'], 3)} Ω; Xcc = {f(r['Xcc_o'], 3)} Ω")
        print(f"Corriente de cortocircuito permanente (red de potencia infinita): Icc = In·100/ucc -> "
              f"{f(r['In1'] * 100 / r['ucc'], 1)} A en AT; {f(r['In2'] * 100 / r['ucc'], 0)} A en BT")
    if "Rfe" in r:
        titulo("Ensayo de vacío")
        if not r["U0_ok"]:
            print("Atención: el ensayo de vacío no se hizo a la tensión nominal de ese lado; P0 no es la de servicio.")
        print(f"Medido del lado {r['lado0']} a {f(r['U0'], 0)} V: I0 = {f(r['I0'], 2)} A ({f(r['I0pc'], 2)} % de In); "
              f"P0 = {f(r['P0'], 0)} W (≈ pérdidas en el hierro)")
        print(f"cosφ0 = {f(r['cos0'], 4)}; IFe = {f(r['IFe'], 3)} A; Iμ = {f(r['Imu'], 3)} A")
        otro = "AT" if r["lado0"] == "BT" else "BT"
        print(f"{'Por fase' if r['m'] == 3 else 'Monofásico'}, referidos a {r['lado0']}: "
              f"RFe = {f(r['Rfe'], 1)} Ω; Xμ = {f(r['Xm'], 2)} Ω; "
              f"referidos a {otro}: RFe = {f(r['Rfe_o'] / 1000, 1)} kΩ; Xμ = {f(r['Xm_o'] / 1000, 2)} kΩ")
    if "ucc" in r:
        titulo(f"Carga: C = {f(C, 2)} de In, cosφ = {f(cosphi, 2)} {'capacitivo' if capacitivo else 'inductivo'}")
        ea = regulacion_aprox(C, r["uR"], r["uX"], cosphi, capacitivo)
        ex = regulacion_exacta(C, r["uR"], r["uX"], cosphi, capacitivo)
        print(f"Caída de tensión ε ≈ C·(uR·cosφ + uX·senφ) + C²·(uX·cosφ - uR·senφ)²/200 = {f(ea, 3)} % "
              f"(fasorial exacta: {f(ex, 3)} %)")
        print(f"Tensión secundaria en carga ≈ {f(r['U2'] * (1 - ex / 100), 1)} V")
        if "P0" in r:
            eta = rendimiento(C, r["S"], cosphi, r["P0"], r["Pcc_n"])
            copt = math.sqrt(r["P0"] / r["Pcc_n"])
            etam = rendimiento(copt, r["S"], cosphi, r["P0"], r["Pcc_n"])
            print(f"Rendimiento η = C·Sn·cosφ / (C·Sn·cosφ + P0 + C²·Pcc) = {f(eta * 100, 2)} %")
            print(f"Rendimiento máximo con C = √(P0/Pcc) = {f(copt, 3)} (Pcu = PFe): "
                  f"η máx = {f(etam * 100, 2)} % con este cosφ")


# ------------------------------------------------------------------ sincrónica y Steinmetz

def imprimir_sincronica(f_hz, n=None, pares=None, E=None, V=None, Xs=None, delta=None, P=None):
    titulo("Máquina sincrónica")
    if pares is None and n is not None:
        p_calc = 60.0 * f_hz / n
        pares = round(p_calc)
        print(f"p = 60·f/n = 60·{f(f_hz, 0)}/{f(n, 2)} = {f(p_calc, 3)} -> {pares} pares de polos ({2 * pares} polos)")
    if pares:
        print(f"Velocidad de sincronismo exacta n = 60·f/p = {f(60.0 * f_hz / pares, 2)} rpm")
    if E and V and Xs:
        pmax = E * V / Xs
        if delta is None and P is not None:
            delta = math.degrees(math.asin(P / pmax))
        if delta is not None:
            d = math.radians(delta)
            Pd = pmax * math.sin(d)
            Q = (E * V * math.cos(d) - V * V) / Xs
            print(f"Con E = {f(E, 0)} V, V = {f(V, 0)} V (valores de línea), Xs = {f(Xs, 3)} Ω por fase, δ = {f(delta, 2)}°:")
            print(f"P = E·V·senδ/Xs = {f(Pd / 1e6, 3)} MW; Q = (E·V·cosδ - V²)/Xs = {f(Q / 1e6, 3)} Mvar "
                  f"({'entrega reactivo: sobreexcitada' if Q > 0 else 'absorbe reactivo: subexcitada'})")
            print(f"Potencia máxima (límite de estabilidad estática, δ = 90°): {f(pmax / 1e6, 3)} MW")


def imprimir_steinmetz(P_kW, U=230.0):
    titulo("Conexión Steinmetz (motor trifásico en red monofásica)")
    c = 70.0 * P_kW * (230.0 / U) ** 2
    print(f"Capacitor de marcha ≈ 70 µF por kW a 230 V -> {f(c, 0)} µF para {f(P_kW, 2)} kW a {f(U, 0)} V "
          f"(escalado con (230/U)², porque Q = ω·C·U²)")
    print(f"Capacitor de arranque adicional (si hace falta cupla): hasta ≈ 2 veces el de marcha -> {f(2 * c, 0)} µF")
    print(f"Potencia disponible ≈ 70 a 80 % de la nominal -> {f(0.7 * P_kW, 2)} a {f(0.8 * P_kW, 2)} kW")
    print("El motor va en la conexión que corresponde a la tensión monofásica (220/380 V -> triángulo en 220 V).")
    print("El capacitor va entre la tercera fase del motor y uno de los dos bornes de red; pasarlo al otro borne invierte el giro.")


# ------------------------------------------------------------------ demo

def demo() -> None:
    print("DEMO: ejemplos resueltos de la skill maquinas-electricas")
    m = motor_placa(7.5, 380, 1455, 90.4, 0.82)
    imprimir_motor(m, IaIn=7.0, TaTn=2.3, TmaxTn=2.8)
    b = balance_potencias(8300, 300, 200, 0.03, 80, pares=2)
    imprimir_balance(b, 8300)
    filas = arranques(m["In"], m["Tn"], 7.0, 2.3, ks=(0.65, 0.8), limite=3.0)
    imprimir_arranques(filas, m["In"], m["Tn"], Tr=25.0)
    r = trafo_ensayos(315, 13200, 400, U0=400, I0=6.8, P0=720, lado0="BT", Ucc=528, Pcc=3900, ladocc="AT")
    imprimir_trafo(r, C=1.0, cosphi=0.8, conexion="Dyn11")
    imprimir_sincronica(50, n=71.4)
    imprimir_sincronica(50, pares=1, E=16000, V=13200, Xs=4.0, delta=20)
    imprimir_steinmetz(1.5, 220)


# ------------------------------------------------------------------ CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")

    def placa(sp):
        sp.add_argument("--P", type=num, required=True, help="potencia útil en el eje [kW] (la de placa)")
        sp.add_argument("--U", type=num, required=True, help="tensión de línea [V]")
        sp.add_argument("--n", type=num, required=True, help="velocidad nominal [rpm]")
        sp.add_argument("--eta", type=num, required=True, help="rendimiento [%% o fracción]")
        sp.add_argument("--cosphi", type=num, required=True, help="factor de potencia nominal")
        sp.add_argument("--f", type=num, default=50.0, help="frecuencia [Hz] (50)")
        sp.add_argument("--pares", type=int, help="pares de polos (si no, se deducen de n)")

    sp = sub.add_parser("motor", help="placa de un motor asincrónico trifásico")
    placa(sp)
    sp.add_argument("--IaIn", type=num, help="Ia/In de catálogo")
    sp.add_argument("--TaTn", type=num, help="Ta/Tn de catálogo")
    sp.add_argument("--TmaxTn", type=num, help="Tmax/Tn de catálogo (para Kloss)")

    sp = sub.add_parser("balance", help="balance de potencias del motor asincrónico")
    sp.add_argument("--P1", type=num, required=True, help="potencia absorbida [W]")
    sp.add_argument("--Pcu1", type=num, required=True, help="pérdidas en el cobre del estator [W]")
    sp.add_argument("--Pfe", type=num, required=True, help="pérdidas en el hierro [W]")
    sp.add_argument("--s", type=num, required=True, help="deslizamiento [%% o fracción]")
    sp.add_argument("--Pmec", type=num, default=0.0, help="pérdidas mecánicas (rozamiento y ventilación) [W]")
    sp.add_argument("--f", type=num, default=50.0, help="frecuencia [Hz] (50)")
    sp.add_argument("--pares", type=int, default=2, help="pares de polos (2)")

    sp = sub.add_parser("arranque", help="comparativo de métodos de arranque")
    placa(sp)
    sp.add_argument("--IaIn", type=num, required=True, help="Ia/In de catálogo (arranque directo)")
    sp.add_argument("--TaTn", type=num, required=True, help="Ta/Tn de catálogo (arranque directo)")
    sp.add_argument("--k", type=num, nargs="*", default=[0.5, 0.65, 0.8],
                    help="tomas del autotransformador (0,65 o 65)")
    sp.add_argument("--limite", type=num, help="corriente límite del arrancador suave [veces In]")
    sp.add_argument("--Tr", type=num, help="cupla resistente de la carga al arrancar [N·m]")

    sp = sub.add_parser("trafo", help="transformador desde los ensayos de vacío y cortocircuito")
    sp.add_argument("--S", type=num, required=True, help="potencia nominal [kVA]")
    sp.add_argument("--U1", type=num, required=True, help="tensión nominal de línea de AT [V]")
    sp.add_argument("--U2", type=num, required=True, help="tensión nominal de línea de BT [V]")
    sp.add_argument("--fases", type=int, default=3, choices=(1, 3))
    sp.add_argument("--conexion", help="grupo de conexión, p. ej. Dyn11")
    sp.add_argument("--U0", type=num, help="tensión del ensayo de vacío [V]")
    sp.add_argument("--I0", type=num, help="corriente de vacío [A]")
    sp.add_argument("--P0", type=num, help="potencia de vacío [W]")
    sp.add_argument("--lado0", default="BT", choices=("AT", "BT"), help="lado alimentado en vacío (BT)")
    sp.add_argument("--Ucc", type=num, help="tensión del ensayo de cortocircuito [V]")
    sp.add_argument("--Icc", type=num, help="corriente del ensayo de cortocircuito [A] (nominal)")
    sp.add_argument("--Pcc", type=num, help="potencia de cortocircuito [W]")
    sp.add_argument("--ladocc", default="AT", choices=("AT", "BT"), help="lado alimentado en cortocircuito (AT)")
    sp.add_argument("--C", type=num, default=1.0, help="índice de carga I/In (1)")
    sp.add_argument("--cosphi", type=num, default=0.8, help="cosφ de la carga (0,8)")
    sp.add_argument("--capacitivo", action="store_true", help="carga capacitiva")

    sp = sub.add_parser("sincronica", help="polos y velocidad; P y Q de rotor liso")
    sp.add_argument("--f", type=num, default=50.0, help="frecuencia [Hz] (50)")
    sp.add_argument("--n", type=num, help="velocidad [rpm]")
    sp.add_argument("--pares", type=int, help="pares de polos")
    sp.add_argument("--E", type=num, help="fem de línea equivalente [V]")
    sp.add_argument("--V", type=num, help="tensión de línea en bornes [V]")
    sp.add_argument("--Xs", type=num, help="reactancia sincrónica por fase [Ω]")
    sp.add_argument("--delta", type=num, help="ángulo de carga [°]")
    sp.add_argument("--Pot", type=num, help="potencia activa [W] (en lugar de delta)")

    sp = sub.add_parser("steinmetz", help="capacitor orientativo para la conexión Steinmetz")
    sp.add_argument("--P", type=num, required=True, help="potencia del motor [kW]")
    sp.add_argument("--U", type=num, default=230.0, help="tensión monofásica [V] (230)")

    sub.add_parser("demo", help="ejemplos resueltos")

    a = ap.parse_args(argv)
    try:
        if a.cmd == "motor":
            m = motor_placa(a.P, a.U, a.n, a.eta, a.cosphi, a.f, a.pares)
            imprimir_motor(m, a.IaIn, a.TaTn, a.TmaxTn)
        elif a.cmd == "balance":
            imprimir_balance(balance_potencias(a.P1, a.Pcu1, a.Pfe, a.s, a.Pmec, a.f, a.pares), a.P1)
        elif a.cmd == "arranque":
            m = motor_placa(a.P, a.U, a.n, a.eta, a.cosphi, a.f, a.pares)
            imprimir_motor(m, a.IaIn, a.TaTn)
            imprimir_arranques(arranques(m["In"], m["Tn"], a.IaIn, a.TaTn, a.k, a.limite), m["In"], m["Tn"], a.Tr)
        elif a.cmd == "trafo":
            r = trafo_ensayos(a.S, a.U1, a.U2, a.fases, a.U0, a.I0, a.P0, a.lado0, a.Ucc, a.Icc, a.Pcc, a.ladocc)
            imprimir_trafo(r, a.C, fraccion(a.cosphi), a.capacitivo, a.conexion)
        elif a.cmd == "sincronica":
            imprimir_sincronica(a.f, a.n, a.pares, a.E, a.V, a.Xs, a.delta, a.Pot)
        elif a.cmd == "steinmetz":
            imprimir_steinmetz(a.P, a.U)
        elif a.cmd == "demo":
            demo()
        else:
            ap.print_help()
    except (ValueError, ZeroDivisionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
