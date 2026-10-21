"""Exportar modelos CadQuery a los formatos de cada programa y sacar vistas 2D.

    import cadquery as cq
    from exportar_cad import exportar, vistas_dxf
    exportar(pieza, "salida/pieza", nombre="Pieza", color=(0.6, 0.62, 0.66), densidad=7.85)
    vistas_dxf(pieza, "salida/pieza_vistas.dxf")

exportar(): .step (SolidWorks y Fusion 360, con nombres y colores), .stl (impresión 3D),
.glb (Blender y visor web, en metros), _vista.png (control) y un resumen con medidas,
volumen, masa, validez del sólido y si la malla está cerrada.
vistas_dxf(): frente, planta y lateral izquierda en método ISO E (planta debajo del frente,
lateral a la derecha), con aristas visibles (capa CONTORNO) y ocultas (capa OCULTAS).
Con msp=... dibuja dentro de una lámina de la skill planos-tecnicos.

Demo:  python exportar_cad.py demo carpeta_salida
Requiere: pip install cadquery trimesh matplotlib ezdxf
"""
from __future__ import annotations

import math
import os
import sys

import cadquery as cq

# vista: (dirección hacia el observador, eje horizontal de la vista en el papel)
VISTAS = {
    "frente": ((0, -1, 0), (1, 0, 0)),
    "planta": ((0, 0, 1), (1, 0, 0)),
    "lateral": ((-1, 0, 0), (0, -1, 0)),  # lateral izquierda: va a la derecha del frente
}


def exportar(obj, base, nombre="pieza", color=None, densidad=None, tolerancia=0.01, png=True):
    """obj: Workplane, Shape o Assembly. densidad en g/cm³ (acero 7.85, aluminio 2.70, PLA 1.24)."""
    os.makedirs(os.path.dirname(os.path.abspath(base)), exist_ok=True)
    forma = _forma(obj)
    ensamble = obj if isinstance(obj, cq.Assembly) else cq.Assembly(
        forma, name=nombre, color=cq.Color(*(color or (0.62, 0.64, 0.68))))
    import trimesh

    _guardar(ensamble, base + ".step")
    _guardar(ensamble, base + ".glb")
    escena = trimesh.load(base + ".glb", force="scene")  # CadQuery lo guarda en mm;
    escena.apply_scale(0.001)                             # glTF (Blender, three.js) usa metros
    escena.export(base + ".glb")
    cq.exporters.export(forma, base + ".stl", tolerance=tolerancia, angularTolerance=0.1)

    malla = trimesh.load(base + ".stl", force="mesh")
    glb = trimesh.load(base + ".glb", force="scene")
    caja = forma.BoundingBox()
    volumen = forma.Volume()  # mm³
    datos = {
        "medidas_mm": (round(caja.xlen, 2), round(caja.ylen, 2), round(caja.zlen, 2)),
        "volumen_cm3": round(volumen / 1000, 2),
        "masa_kg": round(volumen / 1000 * densidad / 1000, 3) if densidad else None,
        "solido_valido": forma.isValid(),
        "malla_cerrada": bool(malla.is_watertight),
        "glb_medidas_m": tuple(round(float(v), 4) for v in glb.extents),
    }
    if png:
        _vista_png(malla, base + "_vista.png", obj.name if isinstance(obj, cq.Assembly) else nombre)
    print(f"{os.path.basename(base)}: STEP + STL + GLB{' + PNG' if png else ''}")
    for clave, valor in datos.items():
        if valor is not None:
            print(f"  {clave}: {valor}")
    return datos


def vistas_dxf(obj, destino=None, escala=1.0, origen=(0.0, 0.0), separacion=20.0, msp=None,
               vistas=("frente", "planta", "lateral"), ocultas=True):
    """Proyecta el modelo (aristas visibles y ocultas) y ubica las vistas en método ISO E.

    escala: factor del dibujo (1 = tamaño real; 0.5 = 1:2). origen: rincón inferior izquierdo
    del conjunto de vistas. Devuelve {'caja': (x0, y0, x1, y1), vista: (x0, y0, x1, y1), ...}.
    """
    import ezdxf

    forma = _forma(obj)
    proyecciones = {v: _proyectar(forma, *VISTAS[v]) for v in vistas}
    cajas = {v: _caja2d(vis + ocu) for v, (vis, ocu) in proyecciones.items()}
    ancho = lambda v: (cajas[v][2] - cajas[v][0]) * escala
    alto = lambda v: (cajas[v][3] - cajas[v][1]) * escala

    pos = {}
    y_frente = origen[1] + (alto("planta") + separacion if "planta" in vistas else 0.0)
    if "frente" in vistas:
        pos["frente"] = (origen[0], y_frente)
    if "planta" in vistas:
        pos["planta"] = (origen[0], origen[1])
    if "lateral" in vistas:
        x_lat = origen[0] + (ancho("frente") + separacion if "frente" in vistas else 0.0)
        pos["lateral"] = (x_lat, y_frente)

    doc = None
    if msp is None:
        doc = ezdxf.new("R2018", setup=True, units=4)
        doc.layers.add("CONTORNO", color=7, lineweight=50)
        doc.layers.add("OCULTAS", color=8, lineweight=25, linetype="DASHED")
        msp = doc.modelspace()

    resultado = {}
    for v, (visibles, escondidas) in proyecciones.items():
        dx = pos[v][0] - cajas[v][0] * escala
        dy = pos[v][1] - cajas[v][1] * escala
        for arista in visibles:
            _arista_dxf(msp, arista, "CONTORNO", escala, dx, dy)
        if ocultas:
            for arista in escondidas:
                _arista_dxf(msp, arista, "OCULTAS", escala, dx, dy)
        resultado[v] = (pos[v][0], pos[v][1], pos[v][0] + ancho(v), pos[v][1] + alto(v))
    xs = [c[0] for c in resultado.values()] + [c[2] for c in resultado.values()]
    ys = [c[1] for c in resultado.values()] + [c[3] for c in resultado.values()]
    resultado["caja"] = (min(xs), min(ys), max(xs), max(ys))

    if doc is not None and destino:
        os.makedirs(os.path.dirname(os.path.abspath(destino)), exist_ok=True)
        doc.saveas(destino)
        print(f"{os.path.basename(destino)}: vistas {', '.join(vistas)} (método ISO E)")
    return resultado


# ---------------------------------------------------------------- internos

def _forma(obj):
    if isinstance(obj, cq.Assembly):
        return obj.toCompound()
    if isinstance(obj, cq.Workplane):
        formas = [v for v in obj.vals() if isinstance(v, cq.Shape)]
        return formas[0] if len(formas) == 1 else cq.Compound.makeCompound(formas)
    return obj


def _guardar(ensamble, ruta):
    guardar = getattr(ensamble, "export", None) or ensamble.save
    guardar(ruta)


def _proyectar(forma, hacia_observador, eje_x):
    from OCP.BRepLib import BRepLib
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    from OCP.HLRAlgo import HLRAlgo_Projector
    from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape

    algo = HLRBRep_Algo()
    algo.Add(forma.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*hacia_observador), gp_Dir(*eje_x))))
    algo.Update()
    algo.Hide()
    hlr = HLRBRep_HLRToShape(algo)

    def aristas(compuestos):
        lista = []
        for c in compuestos:
            if c is None or c.IsNull():
                continue
            for e in cq.Shape.cast(c).Edges():
                BRepLib.BuildCurves3d_s(e.wrapped, 1e-6)
                lista.append(e)
        return lista

    return (aristas([hlr.VCompound(), hlr.OutLineVCompound()]),
            aristas([hlr.HCompound(), hlr.OutLineHCompound()]))


def _caja2d(aristas):
    xs, ys = [], []
    for e in aristas:
        b = e.BoundingBox()
        xs += [b.xmin, b.xmax]
        ys += [b.ymin, b.ymax]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else (0, 0, 0, 0)


def _arista_dxf(msp, e, capa, k, dx, dy):
    p = lambda v: (v.x * k + dx, v.y * k + dy)
    attrs = {"layer": capa}
    tipo = e.geomType()
    if tipo == "LINE":
        msp.add_line(p(e.startPoint()), p(e.endPoint()), dxfattribs=attrs)
        return
    if tipo == "CIRCLE":
        c, r = e.arcCenter(), e.radius() * k
        a, b = e.startPoint(), e.endPoint()
        if (a - b).Length < 1e-6:
            msp.add_circle(p(c), r, dxfattribs=attrs)
            return
        angulo = lambda q: math.degrees(math.atan2(q.y - c.y, q.x - c.x)) % 360
        a0, a1, am = angulo(a), angulo(b), angulo(e.positionAt(0.5))
        if (am - a0) % 360 > (a1 - a0) % 360:
            a0, a1 = a1, a0
        msp.add_arc(p(c), r, a0, a1, dxfattribs=attrs)
        return
    n = max(8, int(e.Length() * k))  # ~1 mm de papel por tramo
    msp.add_lwpolyline([p(e.positionAt(i / n)) for i in range(n + 1)], dxfattribs=attrs)


def _vista_png(malla, ruta, titulo=""):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    elev, azim = 24, -58
    hacia_camara = np.array([math.cos(math.radians(elev)) * math.cos(math.radians(azim)),
                             math.cos(math.radians(elev)) * math.sin(math.radians(azim)),
                             math.sin(math.radians(elev))])
    visibles = malla.face_normals @ hacia_camara > 0   # sin caras traseras: evita manchas
    luz = np.array([0.35, -0.55, 0.75])
    luz /= np.linalg.norm(luz)
    i = 0.35 + 0.65 * np.clip(malla.face_normals[visibles] @ luz, 0, 1)
    colores = np.c_[0.30 + 0.45 * i, 0.34 + 0.46 * i, 0.40 + 0.48 * i, np.ones_like(i)].clip(0, 1)
    fig = plt.figure(figsize=(7, 6), dpi=130)
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(malla.vertices[malla.faces[visibles]], facecolors=colores,
                                         edgecolors="none"))
    mn, mx = malla.bounds
    c, r = (mn + mx) / 2, float((mx - mn).max()) / 2 or 1.0
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(titulo)
    fig.savefig(ruta, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- demo

def _demo(carpeta):
    L, A, E, D, R = 120.0, 80.0, 12.0, 9.0, 6.0     # placa (mm)
    DB, HB, DA = 40.0, 30.0, 20.0                    # buje: diámetro, altura, agujero
    placa = (cq.Workplane("XY").box(L, A, E).translate((0, 0, E / 2))
             .edges("|Z").fillet(R)
             .faces(">Z").workplane().rect(L - 24, A - 24, forConstruction=True).vertices().hole(D))
    buje = (cq.Workplane("XY").workplane(offset=E).circle(DB / 2).extrude(HB)
            .faces(">Z").workplane().hole(DA))
    soporte = placa.union(buje)
    exportar(soporte, os.path.join(carpeta, "soporte"), nombre="Soporte", densidad=7.85)
    vistas_dxf(soporte, os.path.join(carpeta, "soporte_vistas.dxf"))

    eje = cq.Workplane("XY").circle(DA / 2 - 0.1).extrude(70).translate((0, 0, E))  # apoya en la placa
    ensamble = cq.Assembly(name="Soporte con eje")
    ensamble.add(soporte, name="Soporte", color=cq.Color(0.55, 0.58, 0.62))
    ensamble.add(eje, name="Eje", color=cq.Color(0.85, 0.55, 0.20))
    exportar(ensamble, os.path.join(carpeta, "ensamble"))


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "demo":
        _demo(sys.argv[2] if len(sys.argv) > 2 else "salida")
    else:
        print(__doc__)
