#!/usr/bin/env python3
"""Valida el modelo del ejemplo de la plantilla (fórmula de Kloss) y genera casos.json.

Uso:
    python validar_modelo_kloss.py [casos.json]

Es el patrón a copiar para cada simulador nuevo:
  1. el mismo modelo que en el HTML, escrito en Python;
  2. un caso resuelto a mano (con los redondeos de la carpeta) que el modelo tiene que reproducir;
  3. una verificación por otro método (acá, el punto de trabajo por bisección y la coherencia de la curva);
  4. casos.json con los valores exactos, para que probar_simulador.py compruebe que la página da lo mismo.
"""
import json
import math
import sys


def modelo(p, Pn, nN, lam, carga, U, f=50):
    ns = 60 * f / p                                   # rpm
    Tn = 60 * Pn * 1000 / (2 * math.pi * nN)          # N·m
    sN = (ns - nN) / ns
    u = U / 100
    Tmax = lam * Tn * u * u                           # N·m
    sk = sN * (lam + math.sqrt(lam ** 2 - 1))
    kloss = lambda s: 0.0 if s == 0 else 2 * Tmax / (s / sk + sk / s)
    TL = carga / 100 * Tn
    a = Tmax / TL
    s = sk / (a + math.sqrt(a * a - 1))               # rama estable (a >= 1)
    n = ns * (1 - s)
    return dict(ns=ns, Tn=Tn, sN=sN, Tmax=Tmax, sk=sk, Ta=kloss(1), TL=TL, a=a, s=s, n=n,
                P=2 * math.pi * n * TL / 60000, kloss=kloss)


def biseccion(f, a, b, tol=1e-12):
    fa = f(a)
    for _ in range(200):
        m = (a + b) / 2
        if (f(m) > 0) == (fa > 0):
            a, fa = m, f(m)
        else:
            b = m
        if b - a < tol:
            break
    return (a + b) / 2


# 1) Caso resuelto a mano: motor de 5,5 kW, 4 polos, 1.450 rpm, λ = 2,5, carga del 80 %, tensión nominal
A_MANO = dict(ns=1500, Tn=36.22, sN=0.0333, Tmax=90.55, sk=0.1597, Ta=28.20, TL=28.98, a=3.125, s=0.02624, n=1460.6)
r = modelo(2, 5.5, 1450, 2.5, 80, 100)
for clave, valor in A_MANO.items():
    error = abs(r[clave] - valor) / abs(valor)
    assert error < 0.005, f"{clave}: modelo {r[clave]:.6g}, a mano {valor} ({error:.2%})"
print("Caso a mano: coincide (diferencias menores que 0,5 %, del redondeo).")

# 2) Otro método: el cruce de la curva con la carga, buscado numéricamente entre s = 0 y s_k
s_num = biseccion(lambda s: r["kloss"](s) - r["TL"], 1e-9, r["sk"])
assert abs(s_num - r["s"]) < 1e-9, (s_num, r["s"])
print(f"Bisección: s = {s_num:.6f}, igual a la fórmula cerrada.")

# 3) Coherencia: la curva pasa por el punto nominal y su máximo es T_máx en s_k
assert abs(r["kloss"](r["sN"]) - r["Tn"]) < 1e-9
assert abs(r["kloss"](r["sk"]) - r["Tmax"]) < 1e-9
assert max(r["kloss"](i / 10000) for i in range(1, 10001)) <= r["Tmax"] + 1e-9
print("Coherencia: T(s_N) = T_n y el máximo de la curva es T_máx.")

# 4) Casos para el simulador (los parámetros usan los id del HTML)
casos = []
for nombre, (p, Pn, nN, lam, carga, U) in {
    "Caso a mano (80 % de carga)": (2, 5.5, 1450, 2.5, 80, 100),
    "Plena carga": (2, 5.5, 1450, 2.5, 100, 100),
    "Arranque en estrella con 25 % de carga": (2, 5.5, 1450, 2.5, 25, 58),
    "Motor de 1,5 kW y 2 polos": (1, 1.5, 2850, 2.8, 100, 100),
}.items():
    m = modelo(p, Pn, nN, lam, carga, U)
    casos.append({"nombre": nombre,
                  "parametros": {"p": p, "Pn": Pn, "nN": nN, "lambda": lam, "carga": carga, "U": U},
                  "esperado": {k: m[k] for k in ("ns", "Tn", "sN", "Tmax", "sk", "Ta", "TL", "s", "n", "P")},
                  "tolerancia": 1e-6})
destino = sys.argv[1] if len(sys.argv) > 1 else "casos.json"
with open(destino, "w", encoding="utf-8") as f:
    json.dump(casos, f, ensure_ascii=False, indent=1)
print(f"Se guardaron {len(casos)} casos en {destino}.")
