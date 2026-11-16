#!/usr/bin/env python3
"""validar_kit.py: revisa que el marketplace y todas sus skills estén bien armados.

  python scripts/validar_kit.py                       revisa todo y muestra un resumen
  python scripts/validar_kit.py --conteo              además, la tabla de skills por plugin (para el README)
  python scripts/validar_kit.py --conteo --completo   el control de antes de commitear (lo corre GitHub Actions)

Qué revisa siempre:
- .claude-plugin/marketplace.json: JSON válido, nombres únicos, que cada "source" exista.
- plugins/<p>/.claude-plugin/plugin.json: JSON válido, mismo nombre que en el marketplace,
  y que existan las rutas de su campo "skills" (si lo tiene).
- Cada SKILL.md: frontmatter con name y description; name en minúsculas, números y guiones,
  de hasta 64 caracteres, sin "claude" ni "anthropic"; description de hasta 1024 caracteres
  y sin etiquetas XML; en el plugin propio, además, name igual a la carpeta, description entre
  comillas y sin < ni >, y SKILL.md de hasta 260 líneas (aviso).
- Skills con el mismo nombre en dos plugins (compiten entre sí).
- Que no haya archivos .zip, .env ni claves con formato conocido (el repo es público).

Con --completo, además (en el plugin propio):
- Que el README.md esté al día: el total de skills, la tabla de plugins y la de skills propias.
- Que cada skill nombrada en negrita (**nombre-con-guiones**) exista en el kit.
- Que los links relativos de los .md lleven a un archivo que existe.
- Que no queden __pycache__ ni .pyc.
- Que el demo de cada script lo pase: lo corre con python -I en una carpeta temporal. Los que
  necesitan Blender se saltean; si falta una biblioteca o ffmpeg, queda un aviso en vez de un error.

Los problemas del plugin propio son errores; los de las skills de la comunidad son avisos,
porque se copian sin modificar (se arreglan en su repo de origen). Sale con código 1 si hay errores.
Solo biblioteca estándar (usa PyYAML si está instalado).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PLUGIN_PROPIO = "ingenieria-3d"
NOMBRE_VALIDO = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ETIQUETA_XML = re.compile(r"<[A-Za-z/!][^>]*>")
CLAVES = [
    (re.compile(r"\bsk-(?:ant-|proj-)[A-Za-z0-9_-]{20,}\b"), "clave de Anthropic u OpenAI"),
    (re.compile(r"\b(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{30,}\b"), "token de GitHub"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "clave de Google"),
    (re.compile(r"\b\d{8,10}:AA[A-Za-z0-9_-]{33}\b"), "token de bot de Telegram"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "clave privada"),
]
MAX_LINEAS_SKILL = 260
NEGRITA_SKILL = re.compile(r"\*\*([a-z0-9]+(?:-[a-z0-9]+)+)\*\*")
LINK_MD = re.compile(r"!?\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
BLOQUE_CODIGO = re.compile(r"^(`{3,}|~{3,})[^\n]*\n.*?^\1[^\n]*$", re.M | re.S)
CODIGO_EN_LINEA = re.compile(r"`[^`\n]*`")
TIENE_DEMO = re.compile(r"""add_parser\(\s*["']demo["']|==\s*\[?\s*["']demo["']""")
EXTENSIONES_TEXTO = {".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".txt", ".sh", ".ps1", ".html", ".mmd", ".scad"}

try:  # PyYAML es opcional
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None


def leer_frontmatter(texto: str):
    """(dict, error). Entiende el YAML que usan las skills: escalares, comillas y bloques > y |."""
    texto = texto.lstrip("﻿").replace("\r\n", "\n")
    if not texto.startswith("---\n"):
        return None, "no empieza con --- (falta el frontmatter)"
    fin = texto.find("\n---", 4)
    if fin == -1:
        return None, "el frontmatter no se cierra con ---"
    bloque = texto[4:fin]
    if yaml is not None:
        try:
            datos = yaml.safe_load(bloque) or {}
            return (datos, None) if isinstance(datos, dict) else (None, "el frontmatter no es un diccionario")
        except yaml.YAMLError as error:
            return None, f"YAML inválido: {str(error).splitlines()[0]}"
    datos, clave, lineas_bloque, estilo = {}, None, [], None

    def cerrar_bloque():
        if clave is not None and estilo is not None:
            unidas = "\n".join(lineas_bloque) if estilo == "|" else " ".join(l.strip() for l in lineas_bloque)
            datos[clave] = unidas.strip()

    for linea in bloque.split("\n"):
        if estilo is not None and (linea.startswith((" ", "\t")) or not linea.strip()):
            lineas_bloque.append(linea)
            continue
        if estilo is not None:
            cerrar_bloque()
            estilo, lineas_bloque = None, []
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", linea)
        if not m:
            continue
        clave, valor = m.group(1), m.group(2).strip()
        if valor[:1] in (">", "|"):
            estilo = valor[0]
            continue
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1].replace('\\"', '"') if valor[0] == '"' else valor[1:-1].replace("''", "'")
        datos[clave] = valor
    cerrar_bloque()
    return datos, None


class Informe:
    def __init__(self):
        self.errores, self.avisos = [], []

    def error(self, donde: str, que: str):
        self.errores.append(f"{donde}: {que}")

    def aviso(self, donde: str, que: str):
        self.avisos.append(f"{donde}: {que}")


def revisar_skill(ruta: Path, plugin: str, informe: Informe):
    rel = ruta.relative_to(RAIZ).as_posix()
    anotar = informe.error if plugin == PLUGIN_PROPIO else informe.aviso
    fm, problema = leer_frontmatter(ruta.read_text(encoding="utf-8", errors="replace"))
    if problema:
        anotar(rel, problema)
        return None
    nombre = str(fm.get("name", "")).strip()
    descripcion = str(fm.get("description", "")).strip()
    if not nombre:
        anotar(rel, "falta «name»")
    else:
        if not NOMBRE_VALIDO.match(nombre) or len(nombre) > 64:
            anotar(rel, f"name «{nombre}»: solo minúsculas, números y guiones, hasta 64 caracteres")
        if "claude" in nombre or "anthropic" in nombre:
            anotar(rel, f"name «{nombre}» no puede tener «claude» ni «anthropic»")
        if plugin == PLUGIN_PROPIO and nombre != ruta.parent.name:
            informe.error(rel, f"name «{nombre}» distinto de la carpeta «{ruta.parent.name}»")
    if not descripcion:
        anotar(rel, "falta «description»")
    else:
        if len(descripcion) > 1024:
            anotar(rel, f"description de {len(descripcion)} caracteres (máximo 1024)")
        if ETIQUETA_XML.search(descripcion):
            anotar(rel, "description con etiquetas XML (< >)")
        if plugin == PLUGIN_PROPIO and "usar cuando" not in descripcion.lower():
            informe.aviso(rel, "description sin «Usar cuando…»: ayuda a que Claude sepa cuándo usarla")
        if plugin == PLUGIN_PROPIO and ("<" in descripcion or ">" in descripcion):
            informe.error(rel, "description con < o >: en este kit no van (algunos lectores las rechazan)")
    if plugin == PLUGIN_PROPIO:
        texto = ruta.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        linea = next((l for l in texto.split("\n")[1:40] if l.startswith("description:")), "")
        if linea and linea.split(":", 1)[1].strip()[:1] not in ("\"", "'"):
            informe.error(rel, "description sin comillas: va entre comillas dobles (regla del kit)")
        lineas = texto.count("\n") + 1
        if lineas > MAX_LINEAS_SKILL:
            informe.aviso(rel, f"SKILL.md de {lineas} líneas (máximo ~{MAX_LINEAS_SKILL}): pasar lo largo a references/")
    return nombre or ruta.parent.name


def sin_codigo(texto: str) -> str:
    """Saca los bloques de código y el código en línea, para no tomar código por links o nombres."""
    return CODIGO_EN_LINEA.sub("", BLOQUE_CODIGO.sub("", texto))


def revisar_readme(tabla, propias: set, informe: Informe):
    """El README tiene que decir lo mismo que el kit: total, skills por plugin y skills propias."""
    ruta = RAIZ / "README.md"
    if not ruta.is_file():
        informe.error("README.md", "no existe")
        return
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    total = sum(c for _, c in tabla)
    m = re.search(r"\*\*(\d+)\s+skills\*\*", texto)
    if not m:
        informe.error("README.md", "no se encuentra el total de skills («**N skills**»)")
    elif int(m.group(1)) != total:
        informe.error("README.md", f"dice {m.group(1)} skills y el kit tiene {total}")
    filas = {n: int(c) for n, c in re.findall(r"^\|\s*`([a-z0-9-]+)`\s*\|\s*(\d+)\s*\|", texto, re.M)}
    for nombre, c in tabla:
        if nombre not in filas:
            informe.error("README.md", f"falta el plugin «{nombre}» en la tabla de plugins")
        elif filas[nombre] != c:
            informe.error("README.md", f"la tabla de plugins dice {filas[nombre]} skills para «{nombre}» y tiene {c}")
    seccion = re.search(r"^## Skills propias.*?(?=^## |\Z)", texto, re.M | re.S)
    if not seccion:
        informe.error("README.md", "no se encuentra la sección «## Skills propias»")
        return
    listadas = set(re.findall(r"^\|\s*`([a-z0-9-]+)`\s*\|", seccion.group(0), re.M))
    for n in sorted(propias - listadas):
        informe.error("README.md", f"falta «{n}» en la tabla de skills propias")
    for n in sorted(listadas - propias):
        informe.error("README.md", f"la tabla de skills propias nombra «{n}», que no es una skill propia")


def revisar_referencias(carpeta: Path, validos: set, informe: Informe):
    """Skills nombradas en negrita que no existen y links relativos rotos, en los .md del plugin propio."""
    for md in sorted(carpeta.rglob("*.md")):
        rel = md.relative_to(RAIZ).as_posix()
        texto = sin_codigo(md.read_text(encoding="utf-8", errors="replace"))
        faltan = sorted({n for n in NEGRITA_SKILL.findall(texto) if n not in validos})
        for n in faltan:
            informe.error(rel, f"nombra la skill **{n}**, que no existe en el kit")
        for destino in LINK_MD.findall(texto):
            if re.match(r"^[a-z][a-z0-9+.-]*:", destino, re.I) or destino.startswith(("#", "<")):
                continue
            camino = destino.split("#", 1)[0].replace("%20", " ")
            if camino and not (md.parent / camino).exists():
                informe.error(rel, f"link roto: {destino}")


def archivos_del_repo():
    """Lo que git subiría (seguidos y nuevos no ignorados); sin git, todo menos .git."""
    try:
        r = subprocess.run(["git", "-C", str(RAIZ), "ls-files", "-co", "--exclude-standard", "-z"],
                           capture_output=True, timeout=60)
        if r.returncode == 0:
            return [RAIZ / p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]
    except (OSError, subprocess.TimeoutExpired):
        pass
    return [p for p in RAIZ.rglob("*") if p.is_file() and ".git" not in p.parts]


def revisar_higiene(informe: Informe):
    """Basura que no tiene que llegar al repo público (respeta el .gitignore)."""
    for ruta in archivos_del_repo():
        if not ruta.is_file():
            continue
        rel = ruta.relative_to(RAIZ).as_posix()
        if "__pycache__" in ruta.parts or ruta.suffix in (".pyc", ".pyo"):
            informe.error(rel, "no se suben __pycache__ ni .pyc")
        elif ruta.name in (".DS_Store", "Thumbs.db", "desktop.ini"):
            informe.error(rel, "archivo del sistema operativo: no va al repo")
        elif ruta.stat().st_size > 5_000_000:
            informe.aviso(rel, f"archivo de {ruta.stat().st_size / 1e6:.1f} MB: el repo es público y se clona entero")


def correr_demos(carpeta: Path, informe: Informe) -> int:
    """Corre «demo» en cada script del plugin propio que lo tenga. Devuelve cuántos pasaron."""
    pasaron = 0
    entorno = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    with tempfile.TemporaryDirectory(prefix="demos_kit_") as tmp:
        for script in sorted(carpeta.glob("*/scripts/*.py")):
            rel = script.relative_to(RAIZ).as_posix()
            fuente = script.read_text(encoding="utf-8", errors="replace")
            if not TIENE_DEMO.search(fuente) or re.search(r"^\s*import bpy\b", fuente, re.M):
                continue  # sin demo, o corre adentro de Blender
            if "ffmpeg" in fuente and shutil.which("ffmpeg") is None:
                informe.aviso(rel, "demo sin correr: necesita ffmpeg")
                continue
            try:
                r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(script), "demo"], cwd=tmp,
                                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                                   timeout=300, env=entorno)
            except subprocess.TimeoutExpired:
                informe.error(rel, "el demo tardó más de 300 s")
                continue
            if r.returncode == 0:
                pasaron += 1
                continue
            detalle = " | ".join((r.stderr or r.stdout).strip().splitlines()[-3:])
            falta = re.search(r"No module named '([^']+)'", r.stderr or "")
            if falta:
                informe.aviso(rel, f"demo sin correr: falta la biblioteca {falta.group(1)}")
            else:
                informe.error(rel, f"el demo falló (código {r.returncode}): {detalle}")
    return pasaron


def revisar(conteo: bool, completo: bool = False) -> int:
    informe = Informe()
    ruta_mk = RAIZ / ".claude-plugin" / "marketplace.json"
    try:
        marketplace = json.loads(ruta_mk.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: no se puede leer {ruta_mk.relative_to(RAIZ)}: {error}")
        return 1
    plugins = marketplace.get("plugins", [])
    nombres = [p.get("name") for p in plugins]
    for repetido in sorted({n for n in nombres if nombres.count(n) > 1}):
        informe.error("marketplace.json", f"plugin repetido: {repetido}")

    por_nombre_skill: dict = {}
    tabla = []
    for p in plugins:
        nombre = p.get("name", "?")
        fuente = RAIZ / str(p.get("source", "")).lstrip("./")
        if not fuente.is_dir():
            informe.error("marketplace.json", f"{nombre}: no existe la carpeta {p.get('source')}")
            continue
        ruta_pj = fuente / ".claude-plugin" / "plugin.json"
        try:
            pj = json.loads(ruta_pj.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            informe.error(ruta_pj.relative_to(RAIZ).as_posix(), f"plugin.json ilegible: {error}")
            continue
        if pj.get("name") != nombre:
            informe.error(ruta_pj.relative_to(RAIZ).as_posix(), f"name «{pj.get('name')}» distinto del marketplace «{nombre}»")
        for extra in pj.get("skills", []) if isinstance(pj.get("skills"), list) else []:
            if not (fuente / str(extra).lstrip("./")).exists():
                informe.error(ruta_pj.relative_to(RAIZ).as_posix(), f"la ruta de skills «{extra}» no existe")
        skills = sorted(fuente.rglob("SKILL.md"))
        for s in skills:
            n = revisar_skill(s, nombre, informe)
            if n:
                por_nombre_skill.setdefault(n, []).append(nombre)
        tabla.append((nombre, len(skills)))

    for n, donde in sorted(por_nombre_skill.items()):
        if len(set(donde)) > 1:
            informe.aviso("skills", f"«{n}» está en {len(set(donde))} plugins ({', '.join(sorted(set(donde)))}): compiten si se instalan juntos")

    for ruta in RAIZ.rglob("*"):
        if ".git" in ruta.parts or not ruta.is_file():
            continue
        rel = ruta.relative_to(RAIZ).as_posix()
        if ruta.suffix.lower() == ".zip" or ruta.name == ".env" or ruta.name.endswith(".env"):
            informe.error(rel, "no se suben .zip ni .env a este repo público")
            continue
        if ruta.suffix.lower() not in EXTENSIONES_TEXTO or ruta.stat().st_size > 2_000_000 or ruta.resolve() == Path(__file__).resolve():
            continue
        texto = ruta.read_text(encoding="utf-8", errors="ignore")
        for patron, que in CLAVES:
            if patron.search(texto):
                informe.error(rel, f"parece contener una {que}")

    demos = None
    if completo:
        carpeta_propia = RAIZ / "plugins" / PLUGIN_PROPIO / "skills"
        propias = {s.parent.name for s in carpeta_propia.glob("*/SKILL.md")}
        revisar_readme(tabla, propias, informe)
        revisar_referencias(carpeta_propia, set(por_nombre_skill) | set(nombres), informe)
        revisar_higiene(informe)
        demos = correr_demos(carpeta_propia, informe)

    total = sum(c for _, c in tabla)
    if conteo:
        print("| Plugin | Skills |\n|---|---:|")
        for nombre, c in tabla:
            print(f"| `{nombre}` | {c} |")
        print(f"| **Total** | **{total}** |\n")
    extra = f" Demos que pasaron: {demos}." if demos is not None else ""
    print(f"Kit: {len(tabla)} plugins, {total} skills. {len(informe.errores)} errores, {len(informe.avisos)} avisos.{extra}")
    for e in informe.errores:
        print(f"  ERROR  {e}")
    for a in informe.avisos[:40]:
        print(f"  aviso  {a}")
    if len(informe.avisos) > 40:
        print(f"  … y {len(informe.avisos) - 40} avisos más")
    return 1 if informe.errores else 0


def main(argv=None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description="Revisa el marketplace kit-ingenieria-3d y sus skills.")
    parser.add_argument("--conteo", action="store_true", help="mostrar la tabla de skills por plugin")
    parser.add_argument("--completo", action="store_true",
                        help="además: README al día, referencias entre skills, links, __pycache__ y demos de los scripts")
    args = parser.parse_args(argv)
    return revisar(args.conteo, args.completo)


if __name__ == "__main__":
    sys.exit(main())
