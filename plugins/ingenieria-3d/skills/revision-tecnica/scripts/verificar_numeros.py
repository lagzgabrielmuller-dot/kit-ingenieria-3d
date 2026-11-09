#!/usr/bin/env python3
"""verificar_numeros.py: recalcula los números de un informe y marca los que no coinciden.

Se escribe un JSON con los datos de partida y, por cada resultado del informe, la fórmula
con la que se recalcula. El script evalúa cada fórmula (solo aritmética y funciones de math,
sin acceso a nada más), compara con lo que dice el informe y muestra la diferencia.

  python verificar_numeros.py chequeos.json
  python verificar_numeros.py chequeos.json --tol 0.5     (tolerancia en %, por defecto 1)
  python verificar_numeros.py demo

Formato del JSON:
{
  "datos": {"P": 7500, "U": 380, "cosphi": 0.85, "eta": 0.88},
  "chequeos": [
    {"nombre": "Corriente nominal", "donde": "Tabla 3", "informe": 15.3, "unidad": "A",
     "formula": "P / (sqrt(3) * U * cosphi * eta)", "guardar_como": "In"},
    {"nombre": "Corriente de arranque", "informe": 104, "unidad": "A", "formula": "6.8 * In", "tol": 2}
  ]
}
"guardar_como" deja el valor recalculado disponible para los chequeos siguientes.
Funciones y constantes: sqrt, sin, cos, tan, asin, acos, atan, atan2, exp, log, log10, pi, e,
radians, degrees, hypot, abs, min, max, round. Operadores: + - * / ** % y paréntesis.
"""
from __future__ import annotations

import argparse
import ast
import json
import math
import operator
import sys

FUNCIONES = {
    n: getattr(math, n) for n in (
        "sqrt", "sin", "cos", "tan", "asin", "acos", "atan", "atan2", "exp", "log", "log10",
        "radians", "degrees", "hypot", "floor", "ceil")
}
FUNCIONES.update({"abs": abs, "min": min, "max": max, "round": round})
CONSTANTES = {"pi": math.pi, "e": math.e}
OPERADORES = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.Mod: operator.mod, ast.USub: operator.neg, ast.UAdd: operator.pos,
}

DEMO = {
    "datos": {"P": 7500, "U": 380, "cosphi": 0.85, "eta": 0.88, "f": 50, "p": 2, "n": 1450},
    "chequeos": [
        {"nombre": "Corriente nominal", "donde": "punto 2", "informe": 15.3, "unidad": "A",
         "formula": "P / (sqrt(3) * U * cosphi * eta)", "guardar_como": "In"},
        {"nombre": "Velocidad sincrónica", "donde": "punto 2", "informe": 1500, "unidad": "rpm",
         "formula": "60 * f / p", "guardar_como": "ns"},
        {"nombre": "Deslizamiento nominal", "donde": "punto 2", "informe": 3.33, "unidad": "%",
         "formula": "100 * (ns - n) / ns"},
        {"nombre": "Cupla nominal", "donde": "punto 3", "informe": 49.4, "unidad": "N·m",
         "formula": "P / (2 * pi * n / 60)", "guardar_como": "Tn"},
        {"nombre": "Corriente de arranque en estrella-triángulo", "donde": "punto 4", "informe": 51.8, "unidad": "A",
         "formula": "6.8 * In / 3", "tol": 2},
    ],
}


class FormulaInvalida(ValueError):
    pass


def evaluar(expresion: str, variables: dict) -> float:
    try:
        arbol = ast.parse(expresion, mode="eval")
    except SyntaxError as error:
        raise FormulaInvalida(f"no se entiende la fórmula: {error.msg}") from None

    def ev(nodo):
        if isinstance(nodo, ast.Expression):
            return ev(nodo.body)
        if isinstance(nodo, ast.Constant) and isinstance(nodo.value, (int, float)):
            return nodo.value
        if isinstance(nodo, ast.Name):
            if nodo.id in variables:
                return variables[nodo.id]
            if nodo.id in CONSTANTES:
                return CONSTANTES[nodo.id]
            raise FormulaInvalida(f"no hay un dato llamado «{nodo.id}»")
        if isinstance(nodo, ast.BinOp) and type(nodo.op) in OPERADORES:
            return OPERADORES[type(nodo.op)](ev(nodo.left), ev(nodo.right))
        if isinstance(nodo, ast.UnaryOp) and type(nodo.op) in OPERADORES:
            return OPERADORES[type(nodo.op)](ev(nodo.operand))
        if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name) and nodo.func.id in FUNCIONES and not nodo.keywords:
            return FUNCIONES[nodo.func.id](*[ev(a) for a in nodo.args])
        raise FormulaInvalida(f"elemento no permitido en la fórmula: {ast.dump(nodo)[:60]}")

    return float(ev(arbol))


def numero(valor: float, decimales: int = 4) -> str:
    texto = f"{valor:,.{decimales}f}".rstrip("0").rstrip(".")
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def verificar(config: dict, tol_defecto: float) -> int:
    variables = {k: float(v) for k, v in config.get("datos", {}).items()}
    filas, problemas = [], 0
    for i, c in enumerate(config.get("chequeos", []), start=1):
        nombre = c.get("nombre", f"chequeo {i}")
        try:
            valor = evaluar(c["formula"], variables)
        except (FormulaInvalida, KeyError, ZeroDivisionError, ValueError, OverflowError) as error:
            filas.append((nombre, c.get("donde", ""), c.get("informe", ""), "-", "-", f"ERROR: {error}"))
            problemas += 1
            continue
        if c.get("guardar_como"):
            variables[c["guardar_como"]] = valor
        tol = float(c.get("tol", tol_defecto))
        unidad = c.get("unidad", "")
        informe = c.get("informe")
        if informe is None:
            filas.append((nombre, c.get("donde", ""), "-", f"{numero(valor)} {unidad}".strip(), "-", "(sin valor del informe)"))
            continue
        informe = float(informe)
        dif = abs(valor - informe) / abs(valor) * 100 if valor else abs(informe) * 100
        estado = "OK" if dif <= tol else "REVISAR"
        problemas += estado != "OK"
        filas.append((nombre, c.get("donde", ""), f"{numero(informe)} {unidad}".strip(),
                      f"{numero(valor)} {unidad}".strip(), f"{numero(dif, 2)} %", estado))
    anchos = [max(len(str(f[i])) for f in filas + [("Chequeo", "Dónde", "Informe", "Recalculado", "Dif.", "Estado")]) for i in range(6)]
    encabezado = ("Chequeo", "Dónde", "Informe", "Recalculado", "Dif.", "Estado")
    print("  ".join(str(t).ljust(a) for t, a in zip(encabezado, anchos)))
    print("  ".join("-" * a for a in anchos))
    for f in filas:
        print("  ".join(str(t).ljust(a) for t, a in zip(f, anchos)))
    print(f"\n{len(filas)} chequeos, {problemas} para revisar (tolerancia por defecto {numero(tol_defecto, 2)} %).")
    return 1 if problemas else 0


def main(argv=None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description="Recalcula los números de un informe a partir de sus datos y fórmulas.")
    parser.add_argument("archivo", help="JSON con datos y chequeos, o «demo»")
    parser.add_argument("--tol", type=float, default=1.0, help="tolerancia en %% (por defecto 1)")
    args = parser.parse_args(argv)
    if args.archivo == "demo":
        print("Demo: motor de 7,5 kW, 380 V, 4 polos, 1450 rpm, Ia = 6,8·In.")
        print("El último valor del «informe» está mal a propósito: dividió por 2 en vez de por 3.\n")
        verificar(DEMO, args.tol)
        return 0
    try:
        with open(args.archivo, encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, json.JSONDecodeError) as error:
        print(f"No pude leer {args.archivo}: {error}", file=sys.stderr)
        return 2
    return verificar(config, args.tol)


if __name__ == "__main__":
    sys.exit(main())
