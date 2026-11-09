#!/usr/bin/env python3
"""Programación CNC de torno y fresadora con código ISO (G y M), estilo Fanuc.

Solo biblioteca estándar (Python 3.9 o más nuevo). Los números se escriben con coma
o con punto decimal (0,2 o 0.2).

Subcomandos:
  corte    velocidad de giro n, avance Vf, tiempo, caudal de viruta y potencia aproximada
  perfil   programa de torneado exterior de un perfil dado por puntos diámetro;z
           (desbaste con G71 o con pasadas explícitas, terminación, encabezado y cierre)
  revisar  chequeos de un archivo .nc: husillo antes de mecanizar, F antes de G01/G02/G03,
           G96 con límite de rpm, retiro antes de cambiar herramienta, M30 al final,
           coordenadas fuera de rango y otros avisos
  demo     ejemplo completo (corte, perfil y revisar juntos); también sirve de prueba

Ejemplos:
  python cnc.py corte --vc 200 --d 40 --f 0,2 --ap 2 --l 60 --material acero-bajo-c
  python cnc.py corte --maquina fresadora --vc 150 --d 10 --z 3 --fz 0,09 --ap 8 --ae 2 --l 200 --material acero-bajo-c
  python cnc.py perfil --puntos "16;0 20;-2 20;-15 30;-25 30;-40" --bruto 34 --salida pieza.nc
  python cnc.py revisar pieza.nc --rango "X0:110,Z-41:110"
  python cnc.py demo carpeta_salida

Los datos de corte y los valores de kc son orientativos: mandan el catálogo de la
herramienta, el manual de la máquina y el profesor. Todo programa se simula y se prueba
en vacío antes de cortar.
"""
from __future__ import annotations

import argparse
import math
import os
import re
import sys
from dataclasses import dataclass, field

# kc1 [N/mm²] y mc de la fórmula de Kienzle kc = kc1 · h^(-mc), con h en mm.
# Fuente: tabla de grupos de materiales de ISCAR (catálogo Multi-Master 2018, p. 88, y
# "Materials group", iscar.com). Orientativos: otros fabricantes publican valores distintos.
MATERIALES = {
    "acero-bajo-c": ("acero no aleado C < 0,25 %, recocido, 125 HB (ISCAR grupo 1)", 1350, 0.21),
    "acero-medio-c": ("acero no aleado C >= 0,25 %, recocido, 190 HB (ISCAR grupo 2)", 1500, 0.22),
    "acero-aleado": ("acero de baja aleación, recocido, 200 HB (ISCAR grupo 6)", 1775, 0.24),
    "inoxidable": ("inoxidable austenítico, 180 HB (ISCAR grupo 14)", 2150, 0.20),
    "fundicion-gris": ("fundición gris ferrítica/perlítica, 180 HB (ISCAR grupo 15)", 1150, 0.20),
    "aluminio": ("aluminio forjado no bonificable, 60 HB (ISCAR grupo 21)", 700, 0.25),
    "laton": ("latón, 90 HB (ISCAR grupo 27)", 700, 0.27),
}

ETA_SUPUESTO = 0.8  # rendimiento de la transmisión de la máquina: supuesto, cambiar con --eta


# ------------------------------------------------------------------ utilidades

def num(texto):
    """Convierte '0,2' o '0.2' en float (para argparse)."""
    try:
        return float(str(texto).replace(",", "."))
    except ValueError:
        raise argparse.ArgumentTypeError(f"no es un número: {texto}")


def coma(x, dec=2):
    """Número para mostrar, con coma decimal (no se usa en el código G)."""
    return f"{x:.{dec}f}".replace(".", ",")


def legible(x):
    """Número corto para mensajes: 10, -0,5, 46."""
    return f"{x:g}".replace(".", ",")


def g(x):
    """Número para el código G: siempre con punto decimal (20. / -2.5 / 0.)."""
    x = round(x, 3)
    if abs(x) < 0.0005:
        x = 0.0
    return f"{x:.3f}".rstrip("0")


def _salida_segura():
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            try:
                flujo.reconfigure(errors="replace")
            except (ValueError, OSError):
                pass


# ------------------------------------------------------------------ corte

def calcular_corte(maquina, vc, d, f=None, fz=None, z=None, ap=None, ae=None, l=None,
                   pasadas=1, kc=None, kc1=None, mc=None, kr=90.0, eta=ETA_SUPUESTO, nmax=None):
    """Devuelve un dict con n, Vc real, Vf, tiempo, Q, h, kc, Pc, P motor y par."""
    if vc <= 0 or d <= 0:
        raise ValueError("Vc y D tienen que ser positivos")
    r = {"maquina": maquina, "vc": vc, "d": d, "kr": kr, "eta": eta, "pasadas": pasadas}
    n = 1000 * vc / (math.pi * d)                      # rpm
    r["n_calc"] = n
    r["limitada"] = bool(nmax and n > nmax)
    if r["limitada"]:
        n = nmax
    r["n"] = n
    r["vc_real"] = math.pi * d * n / 1000              # m/min
    sen_kr = math.sin(math.radians(kr))
    if maquina == "torno":
        if not f or f <= 0:
            raise ValueError("en torno hace falta el avance por vuelta --f (mm/v)")
        r["f"] = f
        r["vf"] = f * n                                # mm/min
        r["h"] = f * sen_kr                            # espesor de viruta (mm)
    else:
        if not fz or fz <= 0 or not z or z <= 0:
            raise ValueError("en fresadora hacen falta --fz (mm/diente) y --z (dientes)")
        r["fz"], r["z"] = fz, z
        r["vf"] = fz * z * n                           # mm/min
        r["ae"] = ae if ae else d                      # sin ae se supone ranurado (ae = D)
        r["ae_supuesto"] = not ae
        ae_ = min(r["ae"], d)
        phi = math.acos(1 - 2 * ae_ / d)               # ángulo de contacto (rad)
        r["phi_grados"] = math.degrees(phi)
        r["h"] = fz * (1 - math.cos(phi)) / phi * sen_kr   # espesor medio de viruta (mm)
    if kc is None and kc1:
        kc = kc1 * r["h"] ** (-mc)
    r["kc"] = kc
    r["l"] = l
    r["t"] = l / r["vf"] * pasadas if l else None      # min
    r["ap"] = ap
    if ap:
        if maquina == "torno":
            r["q"] = r["vc_real"] * ap * f              # cm³/min
        else:
            r["q"] = ap * r["ae"] * r["vf"] / 1000       # cm³/min
    if ap and kc:
        if maquina == "torno":
            r["pc"] = r["vc_real"] * ap * f * kc / 60e3          # kW
        else:
            r["pc"] = ap * r["ae"] * r["vf"] * kc / 60e6         # kW
        r["p_motor"] = r["pc"] / eta
        r["par"] = r["pc"] * 30e3 / (math.pi * n)              # N·m
    return r


def imprimir_corte(r, origen_kc=""):
    m = r["maquina"]

    def fila(nombre, valor):
        print(f"  {(nombre + ' ').ljust(24, '.')} {valor}")
    print(f"Datos de corte ({m})")
    fila("D de la pieza" if m == "torno" else "D de la herramienta", f"{coma(r['d'], 1)} mm")
    fila("Vc", f"{coma(r['vc'], 0)} m/min")
    fila("n = 1000*Vc/(pi*D)", f"{r['n_calc']:.0f} rpm")
    if r["limitada"]:
        fila("n limitada", f"{r['n']:.0f} rpm (máximo de la máquina): Vc real = "
                           f"{coma(r['vc_real'], 0)} m/min")
    if m == "torno":
        fila("f", f"{coma(r['f'], 3)} mm/v")
        fila("Vf = f*n", f"{r['vf']:.0f} mm/min")
    else:
        fila("fz, z", f"{coma(r['fz'], 3)} mm/diente, {r['z']:g} dientes")
        fila("Vf = fz*z*n", f"{r['vf']:.0f} mm/min")
    if r["t"] is not None:
        fila("t = L/Vf", f"{coma(r['t'], 2)} min ({r['t'] * 60:.0f} s) para L = "
                         f"{legible(r['l'])} mm y {r['pasadas']} pasada(s)")
    if r.get("q") is not None:
        fila("Caudal de viruta Q", f"{coma(r['q'], 1)} cm³/min")
    if m == "torno":
        fila("h = f*sen(kr)", f"{coma(r['h'], 3)} mm (kr = {r['kr']:g}°)")
    else:
        sup = " (ae no dado: se supone ranurado, ae = D)" if r["ae_supuesto"] else ""
        fila("ae, ángulo de contacto", f"{coma(r['ae'], 2)} mm, {coma(r['phi_grados'], 1)}°{sup}")
        fila("hm (espesor medio)", f"{coma(r['h'], 4)} mm")
    if r["kc"]:
        fila("kc", f"{r['kc']:.0f} N/mm² {origen_kc}".rstrip())
    if r.get("pc") is not None:
        fila("Potencia de corte Pc", f"{coma(r['pc'], 2)} kW")
        fila("Potencia en el motor", f"{coma(r['p_motor'], 2)} kW (eta = {coma(r['eta'], 2)}"
                                     f"{', supuesto: cambiar con --eta' if r['eta'] == ETA_SUPUESTO else ''})")
        fila("Par en el husillo", f"{coma(r['par'], 1)} N·m")
    elif r["ap"] is None:
        print("  (para potencia y caudal de viruta: --ap y --material o --kc)")
    avance = coma(r["f"], 3) if m == "torno" else coma(r["fz"], 3) + "/diente"
    t = coma(r["t"], 2) if r["t"] is not None else "(completar)"
    ap = coma(r["ap"], 2) if r["ap"] else "(completar)"
    largo = coma(r["l"], 0) if r["l"] else "(completar)"
    print("Fila para la hoja de proceso:")
    print(f"| (n.º) | (operación) | (herramienta) | {coma(r['vc_real'], 0)} | {r['n']:.0f} | "
          f"{avance} | {ap} | {r['vf']:.0f} | {largo} | {r['pasadas']} | {t} | |")


def cmd_corte(a):
    kc, kc1, mc, origen = a.kc, a.kc1, a.mc, ""
    if a.material:
        desc, kc1, mc = MATERIALES[a.material]
        origen = f"({a.material}: {desc}; kc1 = {kc1}, mc = {coma(mc, 2)})"
    elif kc1:
        if mc is None:
            sys.exit("con --kc1 hace falta --mc")
        origen = f"(kc1 = {kc1:g}, mc = {coma(mc, 2)})"
    elif kc:
        origen = "(dato)"
    try:
        r = calcular_corte(a.maquina, a.vc, a.d, f=a.f, fz=a.fz, z=a.z, ap=a.ap, ae=a.ae, l=a.l,
                           pasadas=a.pasadas, kc=kc, kc1=kc1, mc=mc, kr=a.kr, eta=a.eta,
                           nmax=a.nmax)
    except ValueError as e:
        sys.exit(f"Error: {e}")
    imprimir_corte(r, origen)


# ------------------------------------------------------------------ perfil

def leer_puntos(texto):
    """'16;0 20;-2 ...' (o un punto por renglón) -> [(d, z), ...]."""
    pts = []
    for par in texto.split():
        if ";" not in par:
            raise ValueError(f"punto mal escrito: {par} (usar diámetro;z, por ejemplo 20;-15)")
        d, z = par.split(";", 1)
        pts.append((num(d), num(z)))
    return pts


def validar_perfil(pts, bruto):
    if len(pts) < 2:
        raise ValueError("hacen falta al menos dos puntos")
    for d, _ in pts:
        if d < 0:
            raise ValueError("los diámetros no pueden ser negativos")
    for (d0, z0), (d1, z1) in zip(pts, pts[1:]):
        if z1 > z0 + 1e-9:
            raise ValueError(f"Z tiene que ir de la cara hacia el plato (bajar): {z0:g} -> {z1:g}")
        if d1 < d0 - 1e-9:
            raise ValueError(f"el diámetro baja de {d0:g} a {d1:g}: el perfil no es monótono "
                             "(G71 tipo I no lo admite; usar G73 o separar el perfil)")
        if abs(d1 - d0) < 1e-9 and abs(z1 - z0) < 1e-9:
            raise ValueError(f"punto repetido: {d0:g};{z0:g}")
    if max(d for d, _ in pts) > bruto + 1e-9:
        raise ValueError(f"el perfil tiene diámetros mayores que el bruto ({bruto:g} mm)")


def hacia_arriba(x):
    """Redondea a 0,001 hacia arriba: diámetro mayor o Z hacia la cara (lado seguro)."""
    return math.ceil(x * 1000 - 1e-6) / 1000


def z_fin_pasada(perfil, dp):
    """Z donde la pasada a diámetro dp toca el perfil (monótono, con la salida final)."""
    for (d0, z0), (d1, z1) in zip(perfil, perfil[1:]):
        if d1 > dp + 1e-9:
            t = 0.0 if d1 - d0 < 1e-12 else max(0.0, min(1.0, (dp - d0) / (d1 - d0)))
            return z0 + t * (z1 - z0)
    return perfil[-1][1]


def contorno(pts, x_salida, f, primero_g00=True):
    """Bloques del contorno: G00 X (solo X, tipo I), G01 Z F, puntos y salida en X."""
    d0, z0 = pts[0]
    b = [f"G00 X{g(d0)}" if primero_g00 else f"G01 X{g(d0)}", f"G01 Z{g(z0)} F{g(f)}"]
    prev = (d0, z0)
    for d, z in pts[1:]:
        palabras = []
        if abs(d - prev[0]) > 1e-9:
            palabras.append("X" + g(d))
        if abs(z - prev[1]) > 1e-9:
            palabras.append("Z" + g(z))
        b.append(" ".join(palabras))
        prev = (d, z)
    if abs(x_salida - prev[0]) > 1e-9:
        b.append("X" + g(x_salida))
    return b


def tiempo_corte(segmentos, f, vc, nmax):
    """Tiempo [min] de recorridos a avance f [mm/v] con Vc constante limitada a nmax."""
    t = 0.0
    for (d0, z0), (d1, z1), _ in segmentos:
        largo = math.hypot((d1 - d0) / 2, z1 - z0)       # X en diámetro -> radio
        if largo < 1e-12:
            continue
        pasos = 50
        for i in range(pasos):
            dm = d0 + (d1 - d0) * (i + 0.5) / pasos
            n = nmax if dm <= 1e-9 else min(1000 * vc / (math.pi * dm), nmax)
            t += (largo / pasos) / (f * n)
    return t


@dataclass
class Programa:
    bloques: list = field(default_factory=list)   # [texto, comentario, marca]

    def add(self, texto, comentario=None, marca=None):
        self.bloques.append([texto, comentario, marca])

    def texto(self, encabezado, paso=10):
        numeros = {}
        lineas = []
        for i, (_, _, marca) in enumerate(self.bloques):
            if marca:
                numeros[marca] = (i + 1) * paso
        for i, (txt, com, _) in enumerate(self.bloques):
            txt = txt.format(**numeros)
            linea = f"N{(i + 1) * paso} {txt}".rstrip()
            if com:
                linea += f" ({com})"
            lineas.append(linea)
        return "\n".join(["%", encabezado] + lineas + ["%"]) + "\n"


def generar_perfil(pts, bruto, ap=1.0, sx=0.4, sz=0.1, vc=180.0, vc_term=None, f=0.25,
                   f_term=0.1, nmax=2000, t="T0101", t_term=None, cambio=(100.0, 100.0),
                   modo="g71", programa="O0001", nombre="PERFIL", g42=False, giro="M03",
                   e=0.5, holgura=1.0, z_seg=2.0, refrigerante=True):
    """Programa Fanuc de torneado exterior. Devuelve (texto, resumen)."""
    validar_perfil(pts, bruto)
    if ap <= 0 or f <= 0 or f_term <= 0 or vc <= 0 or nmax <= 0:
        raise ValueError("ap, f, Vc y el límite de rpm tienen que ser positivos")
    if not 0 <= sz < z_seg or sx < 0:
        raise ValueError("sobremetales no válidos (sz tiene que ser menor que la distancia de seguridad)")
    vc_term = vc_term or vc
    x_ini = bruto + 2 * holgura                     # punto de partida, fuera del bruto
    z_ini = pts[0][1] + z_seg                       # delante de la cara
    if cambio[0] < x_ini or cambio[1] < z_ini:
        raise ValueError(f"el punto de cambio tiene que quedar fuera de la pieza "
                         f"(X >= {g(x_ini)}, Z >= {g(z_ini)})")
    m08 = " M08" if refrigerante else ""
    m09 = " M09" if refrigerante else ""

    # perfil desplazado por el sobremetal (como hace G71: X + U, Z + W) y salida al bruto
    sp = [(d + sx, z + sz) for d, z in pts]
    sp_ext = sp + [(x_ini, sp[-1][1])]
    pts_ext = pts + [(x_ini, pts[-1][1])]
    total = max(0.0, (bruto - sp[0][0]) / 2)           # radial a sacar
    npas = math.ceil(total / ap - 1e-9) if total > 1e-9 else 0
    prof = total / npas if npas else 0.0
    # diámetros y finales de pasada redondeados hacia el lado seguro (no muerden el sobremetal)
    diams = [hacia_arriba(bruto - 2 * prof * k) for k in range(1, npas + 1)]
    # una pasada que termina delante de la cara corta solo aire: se saltea
    diams = [dp for dp in diams if z_fin_pasada(sp_ext, dp) < pts[0][1] - 1e-6]
    finales = [hacia_arriba(z_fin_pasada(sp_ext, dp)) for dp in diams]
    npas = len(diams)

    # recorridos a avance (para estimar el tiempo y para el modo de pasadas explícitas)
    desbaste, semi, term = [], [], []
    for dp, zf in zip(diams, finales):
        desbaste.append(((dp, z_ini), (dp, zf), "corte"))
        desbaste.append(((dp, zf), (dp + 2 * e, min(zf + e, z_ini)), "escape"))
    for lista, perfil in ((semi, sp_ext), (term, pts_ext)):
        lista.append(((perfil[0][0], z_ini), perfil[0], "entrada"))
        for p0, p1 in zip(perfil, perfil[1:]):
            lista.append((p0, p1, "perfil"))
    t_des = tiempo_corte(desbaste, f, vc, nmax) + tiempo_corte(semi, f, vc, nmax)
    t_ter = tiempo_corte(term, f_term, vc_term, nmax)

    p = Programa()
    p.add("G21 G40 G97 G99", "MM - SIN COMPENSACION - RPM FIJAS - MM/V")
    p.add(f"G00 X{g(cambio[0])} Z{g(cambio[1])}", "PUNTO DE CAMBIO")
    p.add(t, "DESBASTE")
    p.add(f"G50 S{nmax:.0f}", "LIMITE DE RPM PARA G96")
    p.add(f"G96 S{vc:.0f} {giro}", "VC CONSTANTE")
    p.add(f"G00 X{g(x_ini)} Z{g(z_ini)}{m08}", "PUNTO DE PARTIDA")
    if modo == "g71":
        p.add(f"G71 U{g(ap)} R{g(e)}")
        p.add(f"G71 P{{ns}} Q{{nf}} U{g(sx)} W{g(sz)} F{g(f)}")
        bl = contorno(pts, x_ini, f_term)
        for i, txt in enumerate(bl):
            marca = "ns" if i == 0 else ("nf" if i == len(bl) - 1 else None)
            p.add(txt, "CONTORNO" if i == 0 else None, marca)
    else:
        for k, (dp, zf) in enumerate(zip(diams, finales), 1):
            p.add(f"G00 X{g(dp)}", f"PASADA {k} DE {npas}")
            p.add(f"G01 Z{g(zf)} F{g(f)}")
            p.add(f"X{g(dp + 2 * e)} Z{g(min(zf + e, z_ini))}")
            p.add(f"G00 Z{g(z_ini)}")
        bl = contorno(sp, x_ini, f)
        p.add(bl[0], f"SEMITERMINACION CON SOBREMETAL X{g(sx)} Z{g(sz)}")
        for txt in bl[1:]:
            p.add(txt)
        p.add(f"G00 Z{g(z_ini)}")
    # terminación
    if t_term:
        p.add(f"G00 X{g(cambio[0])}", "RETIRO EN X")
        p.add(f"Z{g(cambio[1])}")
        p.add(t_term, "TERMINACION")
        p.add(f"G50 S{nmax:.0f}")
        p.add(f"G96 S{vc_term:.0f} {giro}")
        arranque = f"G00 {'G42 ' if g42 else ''}X{g(x_ini)} Z{g(z_ini)}{m08}"
    else:
        p.add(f"G96 S{vc_term:.0f}", "TERMINACION")
        arranque = f"G00 G42 X{g(x_ini)} Z{g(z_ini + 1)}" if g42 else None
    if arranque:
        p.add(arranque, "COMPENSACION DE RADIO DE PUNTA" if g42 else "PUNTO DE PARTIDA")
    if modo == "g71":
        p.add("G70 P{ns} Q{nf}")
    else:
        bl = contorno(pts, x_ini, f_term)
        p.add(bl[0], "CONTORNO FINAL")
        for txt in bl[1:]:
            p.add(txt)
    p.add(f"G00 {'G40 ' if g42 else ''}X{g(cambio[0])}{m09}", "RETIRO: PRIMERO X")
    p.add(f"Z{g(cambio[1])}")
    p.add("M05")
    p.add("M30")
    encabezado = f"{programa} ({nombre.upper()})"
    resumen = {
        "modo": modo, "ap": ap,
        "pasadas": npas, "prof": prof, "diametros": diams, "x_ini": x_ini, "z_ini": z_ini,
        "t_desbaste": t_des, "t_terminacion": t_ter,
        "n_min_d": min(1000 * vc_term / (math.pi * pts[0][0]), nmax) if pts[0][0] > 0 else nmax,
        "limita": pts[0][0] <= 0 or 1000 * max(vc, vc_term) / (math.pi * pts[0][0]) > nmax,
    }
    return p.texto(encabezado), resumen


def cmd_perfil(a):
    if a.archivo:
        with open(a.archivo, encoding="utf-8", errors="replace") as fh:
            texto = fh.read()
    elif a.puntos:
        texto = a.puntos
    else:
        sys.exit("Error: dar --puntos \"d;z d;z ...\" o --archivo con un punto d;z por renglón")
    cambio = leer_cambio(a.cambio)
    try:
        pts = leer_puntos(texto)
        prog, res = generar_perfil(pts, a.bruto, ap=a.ap, sx=a.sx, sz=a.sz, vc=a.vc,
                                   vc_term=a.vc_term, f=a.f, f_term=a.f_term, nmax=a.nmax,
                                   t=a.t, t_term=a.t_term, cambio=cambio, modo=a.modo,
                                   programa=a.programa, nombre=a.nombre, g42=a.g42,
                                   giro="M04" if a.m04 else "M03", e=a.retiro,
                                   holgura=a.holgura, refrigerante=not a.sin_refrigerante)
    except ValueError as e:
        sys.exit(f"Error: {e}")
    if a.salida:
        os.makedirs(os.path.dirname(os.path.abspath(a.salida)), exist_ok=True)
        with open(a.salida, "w", encoding="ascii", errors="replace") as fh:
            fh.write(prog)
    else:
        print(prog, end="")
    imprimir_resumen_perfil(res, a.salida)


def imprimir_resumen_perfil(res, salida=None, destino=sys.stderr):
    def p(txt):
        print(txt, file=destino)
    if salida:
        p(f"Programa guardado en {salida}")
    if res["modo"] == "g71":
        p(f"Desbaste con G71 U{g(res['ap'])}: el control reparte las pasadas desde el punto de "
          f"partida X{g(res['x_ini'])}; el tiempo se estimó con {res['pasadas']} pasadas de "
          f"{coma(res['prof'], 3)} mm más el perfilado con sobremetal")
    elif res["pasadas"]:
        p(f"Desbaste: {res['pasadas']} pasadas de {coma(res['prof'], 3)} mm (radial), "
          f"diámetros {', '.join(coma(d, 2) for d in res['diametros'])}, y perfilado con sobremetal")
    else:
        p("Desbaste: no hace falta (el bruto está casi a medida); perfilado y terminación")
    p(f"Tiempo estimado a avance: desbaste {coma(res['t_desbaste'], 2)} min, terminación "
      f"{coma(res['t_terminacion'], 2)} min (sin rápidos ni cambios; G71 puede repartir distinto)")
    if res["limita"]:
        p(f"Con G96, en el diámetro menor la máquina queda en el límite G50 S "
          f"({res['n_min_d']:.0f} rpm)")
    p("Antes de la máquina: simular, probar en vacío y bloque a bloque (ver SKILL.md).")


def leer_cambio(texto):
    m = re.fullmatch(r"\s*X\s*(-?[\d.,]+)\s*,?\s*Z\s*(-?[\d.,]+)\s*", texto.upper())
    if not m:
        sys.exit("Error: --cambio se escribe como \"X100 Z100\"")
    return num(m.group(1)), num(m.group(2))


# ------------------------------------------------------------------ revisar

PALABRA = re.compile(r"([A-Z])([+-]?(?:\d+\.?\d*|\.\d+))")
CICLOS_FRES = {73, 74, 76, 81, 82, 83, 84, 85, 86, 87, 88, 89}
MOV_TORNO = {0, 1, 2, 3, 32, 90, 92, 94}
EJES_DEC_TORNO = "XZUWIKR"      # Q en G32/G92/G76 es ángulo de entrada, sin punto
EJES_DEC_FRES = "XYZIJKRQ"


@dataclass
class Bloque:
    linea: int
    texto: str
    palabras: list
    resto: str

    def valores(self, letra):
        return [v for l, v in self.palabras if l == letra]

    def val(self, letra):
        vs = self.valores(letra)
        return float(vs[0]) if vs else None

    def tiene(self, letra):
        return any(l == letra for l, _ in self.palabras)

    @property
    def gs(self):
        return [float(v) for l, v in self.palabras if l == "G"]

    @property
    def ms(self):
        return [int(float(v)) for l, v in self.palabras if l == "M"]

    @property
    def n(self):
        v = self.val("N")
        return int(v) if v is not None else None


def parsear(texto):
    bloques = []
    for nlin, cruda in enumerate(texto.splitlines(), 1):
        s = re.sub(r"\([^)]*\)", " ", cruda.upper())    # comentarios
        s = s.split(";", 1)[0]                          # ';' es fin de bloque en Fanuc
        s = re.sub(r"\s+", "", s)
        if not s or s.startswith("%"):
            continue
        if s.startswith("/"):
            s = s[1:]                                   # salto de bloque opcional
        bloques.append(Bloque(nlin, cruda.strip(), PALABRA.findall(s), PALABRA.sub("", s)))
    return bloques


def detectar_maquina(bloques):
    letras = {l for b in bloques for l, _ in b.palabras}
    gs = {x for b in bloques for x in b.gs}
    ms = {x for b in bloques for x in b.ms}
    t4 = any(len(v.split(".")[0].lstrip("+-")) >= 3 for b in bloques for v in b.valores("T"))
    fres = "Y" in letras or 6 in ms or bool(gs & {17, 43, 44, 49, 81, 82})
    torno = bool(letras & {"U", "W"}) or bool(gs & {50, 70, 71, 72, 96}) or t4
    if fres != torno:
        return "fresadora" if fres else "torno"
    return "fresadora" if "Y" in letras else "torno"


@dataclass
class Hallazgo:
    nivel: str
    linea: int
    texto: str


class Revisor:
    def __init__(self, maquina, rango=None, x_seguro=None, z_seguro=10.0):
        self.maquina = maquina
        self.torno = maquina == "torno"
        self.rango = rango or {}
        self.x_seguro = x_seguro
        self.z_seguro = z_seguro
        self.hallazgos = []
        self._vistos = set()

    # -- registro
    def h(self, nivel, b, texto, clave=None):
        if clave is not None:
            if clave in self._vistos:
                return
            self._vistos.add(clave)
        self.hallazgos.append(Hallazgo(nivel, b.linea if b else 0, texto))

    def error(self, b, texto, clave=None):
        self.h("ERROR", b, texto, clave)

    def aviso(self, b, texto, clave=None):
        self.h("AVISO", b, texto, clave)

    # -- revisión de todo el archivo
    def revisar(self, bloques):
        programas, actual = [], []
        for b in bloques:
            if b.palabras and b.palabras[0][0] == "O" and actual:
                programas.append(actual)
                actual = []
            actual.append(b)
        if actual:
            programas.append(actual)
        self.nombres = {int(b.val("O")) for prog in programas for b in prog if b.tiene("O")}
        for prog in programas:
            ms = {m for b in prog for m in b.ms}
            es_sub = 99 in ms and not ms & {2, 30}
            self.revisar_programa(prog, es_sub)
        return self.hallazgos

    def revisar_programa(self, prog, es_sub):
        self.es_sub = es_sub
        self.pos = {"X": None, "Y": None, "Z": None}
        self.absoluto = True
        self.mov = 0
        self.husillo = None
        self.f_def = False
        self.g96 = False
        self.limite_rpm = False
        self.comp = 40
        self.herr = None
        self.corto = False
        self.x_max_corte = None
        self.g43 = False
        self.z_sin_g43_avisado = False
        self.ciclo = None
        self.ciclo_z_ini = None
        self.ciclo_r = None
        self.ciclo_z = None
        self.retorno = 98
        self.unidades = False
        self.feed_modo = None
        self.t_pre = None
        self.fin = None
        indice_n = {}
        for i, b in enumerate(prog):
            if b.n is not None:
                indice_n.setdefault(b.n, i)
        self.prog, self.indice_n = prog, indice_n
        contorno = set()
        for b in prog:
            gs = b.gs
            if any(c in gs for c in (70, 71, 72, 73)) and self.torno and b.tiene("P") and b.tiene("Q"):
                i0, i1 = indice_n.get(int(b.val("P"))), indice_n.get(int(b.val("Q")))
                if i0 is not None and i1 is not None and i0 <= i1:
                    contorno.update(range(i0, i1 + 1))
        for i, b in enumerate(prog):
            if self.fin is not None:
                if b.palabras and not (len(b.palabras) == 1 and b.palabras[0][0] == "N"):
                    self.aviso(b, "hay bloques después del fin de programa: no se ejecutan",
                               ("tras_fin", id(prog)))
                continue
            if b.resto:
                self.aviso(b, f"texto no interpretado ({b.resto[:20]}): macro o error de tipeo, "
                              "no se revisa este bloque")
                continue
            self.decimales(b)
            if i in contorno:
                continue        # lo ejecuta el ciclo; se revisa desde el bloque del ciclo
            self.bloque(b)
        ultimo = prog[-1] if prog else None
        if es_sub:
            if not any(99 in b.ms for b in prog):
                self.error(ultimo, "el subprograma no termina con M99")
            return
        if self.fin is None:
            self.error(ultimo, "falta M30 al final del programa")
        elif self.fin == 2:
            self.aviso(ultimo, "termina con M02: en muchos controles M30 además vuelve al inicio "
                               "(y en algunos apaga husillo y refrigerante); conviene M30")
        if not self.unidades:
            self.aviso(prog[0] if prog else None, "no se programa G21 (mm) ni G20 (pulgadas): "
                                                  "conviene G21 en el encabezado")

    # -- utilidades de bloque
    def decimales(self, b):
        gs = b.gs
        if any(c in gs for c in (70, 71, 72, 73, 74, 75, 76, 4, 10, 65)):
            if any(c in gs for c in (74, 75, 76)) and self.torno and (b.tiene("X") or b.tiene("U")):
                letras = "XZUW"          # segundo bloque de G74, G75 o G76: punto final
            else:
                return
        elif not self.torno and (self.ciclo or any(c in CICLOS_FRES for c in gs)):
            letras = "XYZRQ"             # en ciclos de fresadora, K es cantidad de repeticiones
        else:
            letras = EJES_DEC_TORNO if self.torno else EJES_DEC_FRES
        for l, v in b.palabras:
            if l in letras and "." not in v and float(v) != 0:
                self.aviso(b, f"{l}{v} sin punto decimal: en Fanuc vale en la unidad mínima "
                              f"({l}{v} = {coma(float(v) / 1000, 3)} mm), salvo el modo calculadora "
                              f"(parámetro DPI); escribir {l}{v}.")

    def coords(self, b, ejes_inc=True):
        """Posición final (dict) de un bloque con ejes, sin modificar el estado."""
        nueva = dict(self.pos)
        if self.torno:
            for eje, inc in (("X", "U"), ("Z", "W")):
                if b.tiene(eje):
                    nueva[eje] = b.val(eje)
                elif ejes_inc and b.tiene(inc):
                    base = nueva[eje]
                    nueva[eje] = None if base is None else base + b.val(inc)
        else:
            for eje in "XYZ":
                if b.tiene(eje):
                    v = b.val(eje)
                    if self.absoluto:
                        nueva[eje] = v
                    else:
                        nueva[eje] = None if nueva[eje] is None else nueva[eje] + v
        return nueva

    def en_rango(self, b, puntos):
        for p in puntos:
            for eje, (lo, hi) in self.rango.items():
                v = p.get(eje)
                if v is not None and not lo - 1e-6 <= v <= hi + 1e-6:
                    self.error(b, f"{eje} = {legible(round(v, 3))} fuera del rango permitido "
                                  f"({eje} de {legible(lo)} a {legible(hi)})")

    def marcar_corte(self, b, puntos):
        self.corto = True
        for p in puntos:
            if self.torno and p.get("X") is not None:
                self.x_max_corte = p["X"] if self.x_max_corte is None else max(self.x_max_corte, p["X"])

    def exigir_husillo_y_f(self, b, que, necesita_f=True):
        if self.es_sub:
            return
        if self.husillo is None:
            self.error(b, f"{que} sin el husillo girando: falta M03 o M04 antes", ("husillo", self.herr))
        if necesita_f and not self.f_def and not b.tiene("F"):
            self.error(b, f"{que} sin avance F definido antes", ("avance",))

    def seguro_para_cambio(self):
        if not self.corto:
            return True, ""
        x, z = self.pos["X"], self.pos["Z"]
        zs = self.z_seguro
        if self.torno:
            xs = self.x_seguro
            if xs is None:
                xs = (self.x_max_corte or 0) + 10
            ok = x is not None and z is not None and x >= xs - 1e-6 and z >= zs - 1e-6
            crit = f"X >= {legible(xs)} y Z >= {legible(zs)}"
        else:
            ok = z is not None and z >= zs - 1e-6
            crit = f"Z >= {legible(zs)}"
        return ok, crit

    # -- un bloque
    def bloque(self, b):
        gs, ms = b.gs, b.ms
        if 20 in gs or 21 in gs:
            self.unidades = True
        if not self.torno:
            if 90 in gs:
                self.absoluto = True
            if 91 in gs:
                self.absoluto = False
            if 94 in gs or 95 in gs:
                self.feed_modo = 95 if 95 in gs else 94
            if 98 in gs:
                self.retorno = 98
            if 99 in gs:
                self.retorno = 99
            if b.tiene("T"):
                self.t_pre = int(b.val("T"))
        elif 98 in gs or 99 in gs:
            self.feed_modo = 99 if 99 in gs else 98
        if b.tiene("F") and b.val("F") > 0 and not any(c in gs for c in (32, 76, 92)):
            fv = b.val("F")
            por_vuelta = 99 if self.torno else 95
            por_minuto = 98 if self.torno else 94
            if self.torno and self.feed_modo is None and fv < 5 and not self.es_sub:
                self.aviso(b, f"F{g(fv)} sin G99 programado: si el control arranca en G98 (mm/min, "
                              "como varios GSK) la herramienta casi no avanza; programar G99",
                           ("g99",))
            elif self.feed_modo == por_minuto and fv < 5:
                self.aviso(b, f"F{g(fv)} con G{por_minuto} (mm/min): casi no avanza; "
                              f"para mm/v va G{por_vuelta}", ("fmin", b.linea))
            elif self.feed_modo == por_vuelta and fv > 5:
                self.aviso(b, f"F{g(fv)} con G{por_vuelta} (mm/v): avance enorme; "
                              f"para mm/min va G{por_minuto}", ("fvue", b.linea))
        # cambio de herramienta (antes del movimiento del bloque, por seguridad)
        cambio = None
        if self.torno and b.tiene("T"):
            digitos = b.valores("T")[0].split(".")[0].lstrip("+-")
            herr = int(digitos[:-2]) if len(digitos) >= 3 else int(digitos[:1] or 0)
            if herr and herr != self.herr:
                cambio = herr
        if not self.torno and 6 in ms:
            cambio = self.t_pre if self.t_pre is not None else (self.herr or 0) + 1
        if cambio is not None:
            ok, crit = self.seguro_para_cambio()
            if not ok:
                self.error(b, f"cambio de herramienta sin retiro seguro antes (criterio: {crit} o G28)")
            self.herr = cambio
            self.corto = False
            self.g43 = False
            self.z_sin_g43_avisado = False
        if 43 in gs or 44 in gs:
            self.g43 = True
        if 49 in gs:
            self.g43 = False
        # husillo
        if 3 in ms or 4 in ms:
            self.husillo = 3 if 3 in ms else 4
        # límite de rpm y G96
        if self.torno and 50 in gs and b.tiene("S"):
            self.limite_rpm = True
        if 96 in gs:
            if not self.limite_rpm and not self.es_sub:
                if self.torno:
                    self.error(b, "G96 sin límite de rpm: programar G50 S... antes "
                                  "(en el diámetro chico las rpm se disparan)")
                else:
                    self.aviso(b, "G96 en fresadora: verificar el límite de rpm en el manual")
            self.g96 = True
        if 97 in gs:
            self.g96 = False
        # compensación de radio
        for c in (40, 41, 42):
            if c in gs:
                if c in (41, 42) and (2 in gs or 3 in gs or (self.mov in (2, 3) and not
                                                           any(x in gs for x in (0, 1)))):
                    self.error(b, f"G{c} se activa en un arco: la entrada de compensación va "
                                  "en un bloque G00 o G01 (alarma en Fanuc)")
                self.comp = c
        # referencia y sistema de coordenadas
        if 28 in gs or 30 in gs:
            self.pos = {"X": None, "Y": None, "Z": None}
            self.corto = False
            self.ciclo = None
            if b.tiene("F"):
                self.f_def = True
            self.fin_bloque(b, ms)
            return
        if self.torno and 50 in gs and (b.tiene("X") or b.tiene("Z")):
            for eje in "XZ":
                if b.tiene(eje):
                    self.pos[eje] = b.val(eje)
            self.fin_bloque(b, ms)
            return
        if 4 in gs or 10 in gs or 65 in gs:
            self.fin_bloque(b, ms)
            return
        # movimientos y ciclos
        if self.torno:
            self.mov_torno(b, gs)
        else:
            self.mov_fresadora(b, gs, ms)
        if b.tiene("F") and b.val("F") > 0:
            self.f_def = True
        self.fin_bloque(b, ms)

    def fin_bloque(self, b, ms):
        if 5 in ms:
            self.husillo = None
        if 98 in ms and b.tiene("P"):
            p = str(int(b.val("P")))
            prog = int(p[-4:])
            if prog not in self.nombres:
                self.aviso(b, f"M98 llama a O{prog:04d}, que no está en este archivo "
                              "(puede estar en la memoria del control)")
        if 30 in ms or 2 in ms:
            if self.husillo is not None:
                self.aviso(b, "el programa termina con el husillo girando: conviene M05 (y M09) antes")
            self.fin = 30 if 30 in ms else 2

    # -- torno
    def mov_torno(self, b, gs):
        for c in gs:
            if c in MOV_TORNO:
                self.mov = int(c)
        tiene_ejes = any(b.tiene(e) for e in "XZUW")
        if (90 in gs or 91 in gs) and not tiene_ejes:
            self.aviso(b, "G90/G91 sin ejes en torno: en Fanuc sistema A G90 es el ciclo de "
                          "cilindrado y lo incremental se escribe con U y W (G90/G91 como absoluto/"
                          "incremental es de los sistemas B y C): verificar el sistema del control")
        if any(c in gs for c in (70, 71, 72, 73)):
            self.ciclo_multiple(b, gs)
            return
        if any(c in gs for c in (74, 75, 76)):
            c = next(int(c) for c in gs if c in (74, 75, 76))
            if not tiene_ejes:
                return                                  # primer bloque: parámetros
            nombre = {74: "G74", 75: "G75", 76: "G76"}[c]
            self.exigir_husillo_y_f(b, nombre, necesita_f=c != 76)
            for l in "PQ":
                for v in b.valores(l):
                    if "." in v:
                        if c in (74, 75):
                            self.error(b, f"{nombre}: {l}{v} no admite punto decimal "
                                          "(va en unidad mínima, sin punto)")
                        else:
                            self.aviso(b, f"G76: {l}{v} va en unidad mínima, sin punto decimal "
                                          "(verificar en el manual)")
            if c == 76:
                self.roscado(b, "G76")
            fin = self.coords(b)
            self.en_rango(b, [fin])
            self.marcar_corte(b, [fin])
            return
        if not tiene_ejes:
            return
        if self.mov in (90, 92, 94):
            nombre = f"G{self.mov}"
            self.exigir_husillo_y_f(b, nombre, necesita_f=self.mov != 92)
            if self.mov == 92:
                self.roscado(b, "G92")
            fin = self.coords(b)
            self.en_rango(b, [fin])
            self.marcar_corte(b, [fin])
            return                                      # vuelve al punto de partida
        fin = self.coords(b)
        if self.mov in (1, 2, 3, 32):
            self.exigir_husillo_y_f(b, f"G{self.mov:02d}", necesita_f=self.mov != 32)
            if self.mov == 32:
                self.roscado(b, "G32")
            self.marcar_corte(b, [fin])
        self.en_rango(b, [fin])
        self.pos.update({k: v for k, v in fin.items() if k in "XZ"})

    def roscado(self, b, nombre):
        if self.g96:
            self.aviso(b, f"{nombre} con G96 activo: para roscar se usa G97 (rpm fijas)", ("rosca96",))
        if not b.tiene("F"):
            self.aviso(b, f"{nombre} sin F en el bloque: F es el paso de la rosca")

    def ciclo_multiple(self, b, gs):
        c = next(int(x) for x in gs if x in (70, 71, 72, 73))
        if c != 70 and not (b.tiene("P") and b.tiene("Q")):
            return                                      # primer bloque de G71/G72/G73
        if not (b.tiene("P") and b.tiene("Q")):
            self.error(b, f"G{c} sin P y Q (bloques de inicio y fin del contorno)")
            return
        ns, nf = int(b.val("P")), int(b.val("Q"))
        i0, i1 = self.indice_n.get(ns), self.indice_n.get(nf)
        if i0 is None or i1 is None or i0 > i1:
            falta = ns if i0 is None else nf
            self.error(b, f"G{c} P{ns} Q{nf}: no se encuentra el bloque N{falta} del contorno")
            return
        self.exigir_husillo_y_f(b, f"G{c}", necesita_f=c != 70)
        # simular el contorno desde el punto de partida (la herramienta vuelve ahí)
        guardado = dict(self.pos)
        puntos = []
        for j in range(i0, i1 + 1):
            bc = self.prog[j]
            if any(e in "XZUW" for e, _ in bc.palabras):
                self.pos = self.coords(bc)
                puntos.append(dict(self.pos))
        self.pos = guardado
        self.en_rango(b, puntos)
        self.marcar_corte(b, puntos)
        if c == 71:
            primero = self.prog[i0]
            if primero.tiene("Z") or primero.tiene("W"):
                self.aviso(b, f"G71: el bloque N{ns} tiene Z o W, eso es tipo II "
                              "(verificar que el control lo admita); el tipo I lleva solo X")
            xs = [p["X"] for p in puntos[1:] if p["X"] is not None]
            zs = [p["Z"] for p in puntos[1:] if p["Z"] is not None]

            def monotona(v):
                d = [v1 - v0 for v0, v1 in zip(v, v[1:])]
                return all(x >= -1e-9 for x in d) or all(x <= 1e-9 for x in d)
            if not (monotona(xs) and monotona(zs)):
                self.aviso(b, "G71 tipo I necesita un contorno monótono en X y en Z "
                              "(sin rebajes); si no, usar G73 o tipo II")

    # -- fresadora
    def mov_fresadora(self, b, gs, ms):
        for c in gs:
            if c in (0, 1, 2, 3):
                self.mov = int(c)
                self.ciclo = None                       # el grupo 01 cancela el ciclo fijo
        if 80 in gs:
            self.ciclo = None
        nuevo_ciclo = next((int(c) for c in gs if c in CICLOS_FRES), None)
        if nuevo_ciclo:
            self.ciclo = nuevo_ciclo
            self.ciclo_z_ini = self.pos["Z"]
            self.ciclo_r = self.ciclo_z = None
        if self.ciclo:
            if b.tiene("R"):
                self.ciclo_r = b.val("R")
            if b.tiene("Z"):
                self.ciclo_z = b.val("Z")
            if nuevo_ciclo or b.tiene("X") or b.tiene("Y"):
                self.agujero(b)
            return
        if not any(b.tiene(e) for e in "XYZ"):
            return
        fin = self.coords(b)
        if b.tiene("Z") and self.herr is not None and not self.g43 and not self.z_sin_g43_avisado:
            self.aviso(b, "movimiento en Z sin G43 H.. después del cambio de herramienta "
                          "(sin compensación de largo)")
            self.z_sin_g43_avisado = True
        if self.mov in (1, 2, 3):
            self.exigir_husillo_y_f(b, f"G{self.mov:02d}")
            self.marcar_corte(b, [fin])
        self.en_rango(b, [fin])
        self.pos = fin

    def agujero(self, b):
        nombre = f"G{self.ciclo}"
        self.exigir_husillo_y_f(b, nombre)
        if self.ciclo == 84 and self.husillo == 4:
            self.error(b, "G84 (roscado a derecha) con el husillo en M04: va con M03")
        if self.ciclo == 74 and self.husillo == 3:
            self.error(b, "G74 (roscado a izquierda) con el husillo en M03: va con M04")
        xy = self.coords(b)
        z_ini = self.ciclo_z_ini
        if self.absoluto:
            r_abs, z_abs = self.ciclo_r, self.ciclo_z
        else:
            r_abs = None if z_ini is None or self.ciclo_r is None else z_ini + self.ciclo_r
            z_abs = None if r_abs is None or self.ciclo_z is None else r_abs + self.ciclo_z
        if self.ciclo_z is None or self.ciclo_r is None:
            self.aviso(b, f"{nombre} sin Z (fondo) o sin R (plano R)", ("ciclo_zr", b.linea))
        puntos = [{"X": xy["X"], "Y": xy["Y"], "Z": z} for z in (z_abs, r_abs) if z is not None]
        self.en_rango(b, puntos)
        self.marcar_corte(b, puntos)
        self.pos["X"], self.pos["Y"] = xy["X"], xy["Y"]
        self.pos["Z"] = z_ini if self.retorno == 98 else (r_abs if r_abs is not None else z_ini)


def leer_rango(texto):
    if not texto:
        return {}
    rango = {}
    for eje, lo, hi in re.findall(r"([XYZ])\s*(-?\d+(?:\.\d+)?)\s*:\s*(-?\d+(?:\.\d+)?)", texto.upper()):
        lo, hi = float(lo), float(hi)
        rango[eje] = (min(lo, hi), max(lo, hi))
    if not rango:
        sys.exit("Error: --rango se escribe como \"X0:60,Z-80:5\" (en torno, X en diámetro)")
    return rango


def revisar_texto(texto, maquina=None, rango=None, x_seguro=None, z_seguro=10.0):
    bloques = parsear(texto)
    maquina = maquina or detectar_maquina(bloques)
    rev = Revisor(maquina, rango, x_seguro, z_seguro)
    rev.nombres = set()
    hallazgos = rev.revisar(bloques) if bloques else [Hallazgo("ERROR", 0, "archivo vacío")]
    return maquina, len(bloques), hallazgos


def imprimir_revision(nombre, maquina, nbloques, hallazgos, rango, x_seguro, z_seguro):
    print(f"Revisión de {nombre} ({maquina}, {nbloques} bloques)")
    crit = f"Z >= {legible(z_seguro)}"
    if maquina == "torno":
        crit = (f"X >= {legible(x_seguro)}" if x_seguro is not None else
                "X >= diámetro máximo cortado + 10") + " y " + crit
    print(f"  Retiro para cambiar herramienta: {crit} (o G28)")
    if rango:
        print("  Rango permitido: " + ", ".join(f"{e} de {legible(lo)} a {legible(hi)}"
                                               for e, (lo, hi) in rango.items()))
    for nivel in ("ERROR", "AVISO"):
        lista = [x for x in hallazgos if x.nivel == nivel]
        if not lista:
            continue
        print(f"{'ERRORES' if nivel == 'ERROR' else 'AVISOS'} ({len(lista)})")
        for x in lista[:40]:
            print(f"  línea {x.linea}: {x.texto}")
        if len(lista) > 40:
            print(f"  ... y {len(lista) - 40} más")
    ne = sum(x.nivel == "ERROR" for x in hallazgos)
    na = len(hallazgos) - ne
    print(f"Resultado: {ne} error(es), {na} aviso(s). "
          + ("Corregir antes de simular." if ne else "Igual hay que simular y probar en vacío."))
    return ne


def cmd_revisar(a):
    try:
        with open(a.archivo, encoding="utf-8", errors="replace") as fh:
            texto = fh.read()
    except OSError as e:
        sys.exit(f"Error: {e}")
    rango = leer_rango(a.rango)
    maquina, nb, hallazgos = revisar_texto(texto, a.maquina, rango, a.x_seguro, a.z_seguro)
    ne = imprimir_revision(a.archivo, maquina, nb, hallazgos, rango, a.x_seguro, a.z_seguro)
    sys.exit(1 if ne else 0)


# ------------------------------------------------------------------ demo

PROGRAMA_CON_ERRORES = """%
O0002 (CON ERRORES A PROPOSITO)
N10 G21 G99
N20 T0101
N30 G96 S200 M03
N40 G00 X36. Z2.
N50 G01 X30. Z-20.
N60 F0.2
N70 Z-150.
N80 T0202
N90 G00 X40 Z5.
N100 M05
N110 G01 X20. F0.1
%
"""


def demo(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    ok = True
    print("=" * 72)
    print("1) Datos de corte: cilindrado de acero de bajo carbono con plaquita de metal duro")
    r = calcular_corte("torno", 200, 40, f=0.2, ap=2, l=60, kc1=1350, mc=0.21)
    imprimir_corte(r, "(acero-bajo-c, ISCAR grupo 1)")
    ok &= round(r["n"]) == 1592 and round(r["vf"]) == 318 and abs(r["pc"] - 2.52) < 0.01
    print()
    print("2) Datos de corte: fresado lateral con fresa de 3 filos Ø10 en acero")
    r = calcular_corte("fresadora", 150, 10, fz=0.09, z=3, ap=8, ae=2, l=200, kc1=1350, mc=0.21)
    imprimir_corte(r, "(acero-bajo-c, ISCAR grupo 1)")
    ok &= round(r["n"]) == 4775 and round(r["vf"]) == 1289
    puntos = leer_puntos("16;0 20;-2 20;-15 30;-25 30;-40")
    rango = leer_rango("X0:110,Z-41:110")
    for modo, archivo, extra in (("g71", "perfil_g71.nc", {"t_term": "T0202", "vc_term": 220}),
                                 ("pasadas", "perfil_pasadas.nc", {"vc_term": 220})):
        print()
        print("=" * 72)
        print(f"3) Perfil {modo}: puntos 16;0 20;-2 20;-15 30;-25 30;-40, bruto Ø34")
        prog, res = generar_perfil(puntos, 34, ap=1.0, modo=modo, **extra)
        ruta = os.path.join(carpeta, archivo)
        with open(ruta, "w", encoding="ascii") as fh:
            fh.write(prog)
        print(prog, end="")
        imprimir_resumen_perfil(res, ruta, destino=sys.stdout)
        print()
        maquina, nb, hallazgos = revisar_texto(prog, None, rango)
        ne = imprimir_revision(ruta, maquina, nb, hallazgos, rango, None, 10.0)
        ok &= ne == 0 and not hallazgos and maquina == "torno"
    print()
    print("=" * 72)
    print("4) Revisar un programa con errores a propósito")
    ruta = os.path.join(carpeta, "programa_con_errores.nc")
    with open(ruta, "w", encoding="ascii") as fh:
        fh.write(PROGRAMA_CON_ERRORES)
    print(PROGRAMA_CON_ERRORES, end="")
    maquina, nb, hallazgos = revisar_texto(PROGRAMA_CON_ERRORES, None, rango)
    imprimir_revision(ruta, maquina, nb, hallazgos, rango, None, 10.0)
    esperados = ["G96 sin límite", "G01 sin avance", "fuera del rango", "cambio de herramienta",
                 "sin el husillo", "falta M30", "sin punto decimal"]
    textos = " | ".join(x.texto for x in hallazgos)
    faltan = [e for e in esperados if e not in textos]
    ok &= not faltan
    print()
    print("Demo " + ("OK: los resultados coinciden con los esperados." if ok else
                     f"CON DIFERENCIAS: revisar {faltan}"))
    return 0 if ok else 1


# ------------------------------------------------------------------ main

def main(argv=None):
    _salida_segura()
    ap = argparse.ArgumentParser(
        prog="cnc.py",
        description="Programación CNC de torno y fresadora (código ISO, estilo Fanuc): datos de "
                    "corte, programa de un perfil de torneado y revisión de archivos .nc.",
        epilog="Ejemplo completo: python cnc.py demo salida. Valores orientativos: mandan el "
               "catálogo de la herramienta, el manual de la máquina y el profesor.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("corte", help="n, Vf, tiempo, caudal de viruta y potencia aproximada",
                       description="n = 1000·Vc/(pi·D); torno Vf = f·n; fresadora Vf = fz·z·n; "
                                   "t = L/Vf; Pc = Vc·ap·f·kc/60000 (torno) o ap·ae·Vf·kc/6e7 "
                                   "(fresadora); kc = kc1·h^-mc.")
    c.add_argument("--maquina", choices=["torno", "fresadora"], default="torno")
    c.add_argument("--vc", type=num, required=True, help="velocidad de corte (m/min)")
    c.add_argument("--d", type=num, required=True,
                   help="diámetro (mm): de la pieza en torno, de la herramienta en fresadora")
    c.add_argument("--f", type=num, help="torno: avance por vuelta (mm/v)")
    c.add_argument("--fz", type=num, help="fresadora: avance por diente (mm/diente)")
    c.add_argument("--z", type=num, help="fresadora: cantidad de dientes (filos)")
    c.add_argument("--ap", type=num, help="profundidad de corte (mm); en torno, radial")
    c.add_argument("--ae", type=num, help="fresadora: ancho de contacto (mm); sin dato, ranurado")
    c.add_argument("--l", type=num, help="largo recorrido a avance por pasada (mm)")
    c.add_argument("--pasadas", type=int, default=1, help="cantidad de pasadas iguales (1)")
    c.add_argument("--material", choices=sorted(MATERIALES), help="kc1 y mc orientativos (ISCAR)")
    c.add_argument("--kc", type=num, help="fuerza específica de corte (N/mm²), del catálogo")
    c.add_argument("--kc1", type=num, help="kc1 (N/mm²) para kc = kc1·h^-mc")
    c.add_argument("--mc", type=num, help="exponente mc")
    c.add_argument("--kr", type=num, default=90.0, help="ángulo de posición del filo (°), 90")
    c.add_argument("--eta", type=num, default=ETA_SUPUESTO, help="rendimiento de la máquina (0,8)")
    c.add_argument("--nmax", type=num, help="rpm máximas de la máquina")
    c.set_defaults(func=cmd_corte)

    p = sub.add_parser("perfil", help="programa de torneado exterior desde puntos diámetro;z",
                       description="Genera un programa Fanuc (torno, sistema A) con encabezado, "
                                   "límite de rpm, desbaste (G71 o pasadas), terminación y cierre. "
                                   "El perfil va de la cara (Z mayor) hacia el plato, con "
                                   "diámetros que no bajan; se supone la cara refrentada.")
    p.add_argument("--puntos", help='puntos "d;z d;z ..." (X en diámetro), p. ej. "16;0 20;-2 20;-15"')
    p.add_argument("--archivo", help="archivo de texto con un punto d;z por renglón")
    p.add_argument("--bruto", type=num, required=True, help="diámetro del material en bruto (mm)")
    p.add_argument("--modo", choices=["g71", "pasadas"], default="g71",
                   help="g71: ciclo G71 + G70; pasadas: G01 explícitos (controles sin G71)")
    p.add_argument("--ap", type=num, default=1.0, help="profundidad radial por pasada (mm), 1")
    p.add_argument("--sx", type=num, default=0.4, help="sobremetal de terminación en X, diámetro (0,4)")
    p.add_argument("--sz", type=num, default=0.1, help="sobremetal de terminación en Z (0,1)")
    p.add_argument("--vc", type=num, default=180.0, help="Vc de desbaste (m/min), 180")
    p.add_argument("--vc-term", type=num, help="Vc de terminación (m/min); igual a --vc si falta")
    p.add_argument("--f", type=num, default=0.25, help="avance de desbaste (mm/v), 0,25")
    p.add_argument("--f-term", type=num, default=0.1, help="avance de terminación (mm/v), 0,1")
    p.add_argument("--nmax", type=num, default=2000, help="límite de rpm para G50 S (2000)")
    p.add_argument("--t", default="T0101", help="herramienta y corrector de desbaste (T0101)")
    p.add_argument("--t-term", help="herramienta de terminación (p. ej. T0202); si falta, la misma")
    p.add_argument("--cambio", default="X100 Z100", help='punto de cambio de herramienta ("X100 Z100")')
    p.add_argument("--retiro", type=num, default=0.5, help="retiro a 45° tras cada pasada, R de G71 (0,5)")
    p.add_argument("--holgura", type=num, default=1.0, help="holgura radial sobre el bruto (1)")
    p.add_argument("--g42", action="store_true", help="compensación de radio de punta en la terminación")
    p.add_argument("--m04", action="store_true", help="giro M04 en lugar de M03")
    p.add_argument("--sin-refrigerante", action="store_true", help="sin M08/M09")
    p.add_argument("--programa", default="O0001", help="número de programa (O0001)")
    p.add_argument("--nombre", default="PERFIL", help="comentario del encabezado")
    p.add_argument("--salida", help="archivo .nc de salida; si falta, se muestra en pantalla")
    p.set_defaults(func=cmd_perfil)

    r = sub.add_parser("revisar", help="chequeos de seguridad y formato de un archivo .nc",
                       description="Detecta: mecanizado sin husillo girando, G01/G02/G03 sin F, "
                                   "G96 sin límite de rpm, cambio de herramienta sin retiro, falta "
                                   "de M30, coordenadas fuera de rango y avisos (punto decimal, "
                                   "G41/G42 en arcos, G71, G43, M98). No reemplaza la simulación.")
    r.add_argument("archivo", help="programa .nc, .tap o .txt")
    r.add_argument("--maquina", choices=["torno", "fresadora"], help="si falta, se detecta")
    r.add_argument("--rango", help='límites de coordenadas, p. ej. "X0:60,Z-80:5" (torno: X en diámetro)')
    r.add_argument("--x-seguro", type=num, help="torno: X mínima (diámetro) para cambiar herramienta")
    r.add_argument("--z-seguro", type=num, default=10.0, help="Z mínima para cambiar herramienta (10)")
    r.set_defaults(func=cmd_revisar)

    d = sub.add_parser("demo", help="ejemplo completo: corte, perfil y revisar")
    d.add_argument("carpeta", nargs="?", default="salida_cnc", help="carpeta de salida (salida_cnc)")
    d.set_defaults(func=lambda a: sys.exit(demo(a.carpeta)))

    a = ap.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
