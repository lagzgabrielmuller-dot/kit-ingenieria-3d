#!/usr/bin/env python3
"""Prueba un simulador hecho con plantilla/simulador.html en Chrome sin ventana (Playwright).

Uso:
    python probar_simulador.py simulador.html [--salida carpeta] [--casos casos.json] [--chrome RUTA]

Revisa, con internet bloqueado:
  - que no haya errores en la consola ni pedidos a internet;
  - que el gráfico dibuje y que mover el primer deslizador cambie el modelo (resultados o curvas) y su campo;
  - que se generen el CSV y el PNG del gráfico;
  - que los controles visibles tengan nombre accesible y que en el celular nada se salga de costado;
  - con --casos, que window.simulador.calcular() dé los valores calculados con Python.
Guarda capturas en la carpeta de salida: escritorio.png, celular.png, celular-pantalla.png,
impresion.png e impresion.pdf. Sale con código 1 si algo falla.

Formato de casos.json (tolerancia relativa; tolerancia_abs opcional para valores cerca de cero):
    [{"nombre": "Caso a mano", "parametros": {"Pn": 5.5}, "esperado": {"n": 1460.63}, "tolerancia": 1e-4}]

Requisitos: pip install playwright  (y Chrome, Edge o `python -m playwright install chromium`).
"""
import argparse
import json
import math
import shutil
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PIXELES_PINTADOS = """() => {
  const c = document.querySelector('#grafico');
  if (!c || !c.width) return 0;
  const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
  let n = 0;
  for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++;
  return n / (c.width * c.height);
}"""

SIN_NOMBRE = """() => [...document.querySelectorAll('input, select, textarea, button')]
  .filter((e) => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden')
  .filter((e) => !(e.labels && e.labels.length) && !e.getAttribute('aria-label')
    && !e.getAttribute('aria-labelledby') && !(e.tagName === 'BUTTON' && e.textContent.trim()))
  .map((e) => e.id || e.outerHTML.slice(0, 70))"""


def lanzar(p, chrome):
    intentos = [dict(executable_path=chrome)] if chrome else []
    intentos += [dict(), dict(channel="chrome"), dict(channel="msedge")]
    for nombre in ("google-chrome", "chromium", "chromium-browser"):
        ruta = shutil.which(nombre)
        if ruta:
            intentos.append(dict(executable_path=ruta))
    ultimo = None
    for opciones in intentos:
        try:
            return p.chromium.launch(headless=True, **opciones)
        except Exception as e:  # probar el siguiente navegador
            ultimo = e
    sys.exit(f"No se pudo abrir Chrome, Edge ni Chromium: {ultimo}")


def preparar(contexto, errores, externos):
    def ruta(r):
        if r.request.url.startswith(("http:", "https:")):
            externos.append(r.request.url)
            r.abort()
        else:
            r.continue_()

    contexto.route("**/*", ruta)
    pagina = contexto.new_page()
    pagina.on("console", lambda m: errores.append("consola: " + m.text) if m.type == "error" else None)
    pagina.on("pageerror", lambda e: errores.append(f"página: {e}"))
    return pagina


def abrir(pagina, url, errores):
    pagina.goto(url)
    try:
        pagina.wait_for_function("window.simulador !== undefined", timeout=10000)
    except Exception:
        print("FALLA  la página no arrancó (window.simulador no existe). Errores:")
        for e in errores or ["ninguno en la consola: revisar que no se haya borrado el arranque"]:
            print("       " + e)
        sys.exit(1)
    pagina.wait_for_timeout(700)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("--salida", default="prueba_simulador")
    ap.add_argument("--casos")
    ap.add_argument("--chrome", help="ruta al ejecutable de Chrome o Edge")
    a = ap.parse_args()

    html = Path(a.html).resolve()
    salida = Path(a.salida).resolve()
    salida.mkdir(parents=True, exist_ok=True)
    url = html.as_uri()
    fallas, errores, externos = [], [], []

    def control(ok, texto_ok, texto_falla):
        print(("OK     " if ok else "FALLA  ") + (texto_ok if ok else texto_falla))
        if not ok:
            fallas.append(texto_falla)

    with sync_playwright() as p:
        nav = lanzar(p, a.chrome)

        # --- Escritorio ---
        ctx = nav.new_context(viewport={"width": 1366, "height": 900}, accept_downloads=True, locale="es-AR")
        pag = preparar(ctx, errores, externos)
        abrir(pag, url, errores)
        pintado = pag.evaluate(PIXELES_PINTADOS)
        control(pintado > 0.01, f"el gráfico dibuja ({pintado:.1%} del lienzo pintado)", "el gráfico está vacío")

        antes, firma_antes = pag.inner_text("#resultados"), pag.evaluate("window.simulador.firma()")
        rango = pag.locator('input[type="range"]').first
        if rango.count():
            id_rango = rango.get_attribute("id") or ""
            campo = pag.locator("#p-" + id_rango[2:]) if id_rango.startswith("r-") else None
            valor_antes = campo.input_value() if campo else ""
            rango.focus()
            for _ in range(5):
                pag.keyboard.press("ArrowRight")
            pag.keyboard.press("PageUp")
            pag.wait_for_timeout(400)
            cambio_res = pag.inner_text("#resultados") != antes
            cambio_modelo = pag.evaluate("window.simulador.firma()") != firma_antes
            control(cambio_res or cambio_modelo,
                    "mover el primer deslizador cambia " + ("los resultados" if cambio_res else "las curvas"),
                    "mover el primer deslizador no cambió ni los resultados ni las curvas")
            if cambio_modelo and not cambio_res:
                print("AVISO  los resultados no dependen del primer deslizador: revisar que sea lo esperado")
            if campo:
                control(campo.input_value() != valor_antes, "el campo numérico sigue al deslizador",
                        "el campo numérico no se actualizó con el deslizador")
            pag.click("#restablecer")
            pag.wait_for_timeout(300)
        else:
            print("AVISO  no hay deslizadores para probar")

        for boton, nombre, firma in (("#exportar-csv", "CSV", None), ("#exportar-png", "PNG", b"\x89PNG")):
            try:
                with pag.expect_download(timeout=6000) as d:
                    pag.click(boton)
                archivo = salida / d.value.suggested_filename
                d.value.save_as(archivo)
                datos = archivo.read_bytes()
                if firma:
                    ok = datos.startswith(firma) and len(datos) > 5000
                    detalle = f"{len(datos) // 1024} kB"
                else:
                    filas = [f for f in datos.decode("utf-8-sig").splitlines() if f.strip()]
                    ok = len(filas) >= 5 and ";" in filas[-1]
                    detalle = f"{len(filas)} filas"
                control(ok, f"se genera el {nombre}: {archivo.name} ({detalle})", f"el {nombre} salió vacío o mal formado")
            except Exception as e:
                control(False, "", f"no se generó el {nombre} ({e.__class__.__name__})")

        faltan = pag.evaluate(SIN_NOMBRE)
        control(not faltan, "todos los controles visibles tienen nombre accesible",
                "controles sin nombre accesible: " + ", ".join(faltan))

        for caso in json.loads(Path(a.casos).read_text(encoding="utf-8")) if a.casos else []:
            obtenido = pag.evaluate("p => window.simulador.calcular(p)", caso.get("parametros", {}))
            tol, tol_abs = caso.get("tolerancia", 1e-4), caso.get("tolerancia_abs", 1e-9)
            for clave, esperado in caso["esperado"].items():
                v = obtenido.get(clave)
                ok = isinstance(v, (int, float)) and math.isfinite(v) and abs(v - esperado) <= max(tol * abs(esperado), tol_abs)
                control(ok, f"{caso.get('nombre', 'caso')}: {clave} = {v:.6g} (Python: {esperado:.6g})" if ok else "",
                        f"{caso.get('nombre', 'caso')}: {clave} da {v} y Python dice {esperado}")

        pag.screenshot(path=str(salida / "escritorio.png"), full_page=True)
        pag.click("#vista-impresion")
        pag.wait_for_timeout(500)
        pag.screenshot(path=str(salida / "impresion.png"), full_page=True)
        pag.pdf(path=str(salida / "impresion.pdf"), format="A4", print_background=True)
        pag.click("#volver")
        ctx.close()

        # --- Celular ---
        ctx = nav.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True,
                              has_touch=True, locale="es-AR")
        pag = preparar(ctx, errores, externos)
        abrir(pag, url, errores)
        # se compara con el ancho de la pantalla (390 px): en el celular innerWidth crece con el contenido
        ancho = pag.evaluate("() => document.documentElement.scrollWidth")
        control(ancho <= 391, "en el celular nada se sale de costado",
                f"en el celular la página mide {ancho} px de ancho para una pantalla de 390 px")
        pag.screenshot(path=str(salida / "celular-pantalla.png"))
        pag.screenshot(path=str(salida / "celular.png"), full_page=True)
        ctx.close()
        nav.close()

    control(not errores, "sin errores en la consola", "errores: " + " | ".join(errores[:5]))
    control(not externos, "no pide nada a internet", "pide recursos de internet: " + ", ".join(sorted(set(externos))[:5]))
    print(f"\nCapturas en {salida}")
    print("Resultado: " + ("todo bien" if not fallas else f"{len(fallas)} falla(s)"))
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
