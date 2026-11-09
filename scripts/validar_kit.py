#!/usr/bin/env python3
"""validar_kit.py: revisa que el marketplace y todas sus skills estén bien armados.

  python scripts/validar_kit.py            revisa todo y muestra un resumen
  python scripts/validar_kit.py --conteo   además, la tabla de skills por plugin (para el README)

Qué revisa:
- .claude-plugin/marketplace.json: JSON válido, nombres únicos, que cada "source" exista.
- plugins/<p>/.claude-plugin/plugin.json: JSON válido, mismo nombre que en el marketplace,
  y que existan las rutas de su campo "skills" (si lo tiene).
- Cada SKILL.md: frontmatter con name y description; name en minúsculas, números y guiones,
  de hasta 64 caracteres, sin "claude" ni "anthropic"; description de hasta 1024 caracteres
  y sin etiquetas XML; en el plugin propio, además, name igual a la carpeta.
- Skills con el mismo nombre en dos plugins (compiten entre sí).
- Que no haya archivos .zip, .env ni claves con formato conocido (el repo es público).

Los problemas del plugin propio son errores; los de las skills de la comunidad son avisos,
porque se copian sin modificar (se arreglan en su repo de origen). Sale con código 1 si hay errores.
Solo biblioteca estándar (usa PyYAML si está instalado).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
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
    return nombre or ruta.parent.name


def revisar(conteo: bool) -> int:
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

    total = sum(c for _, c in tabla)
    if conteo:
        print("| Plugin | Skills |\n|---|---:|")
        for nombre, c in tabla:
            print(f"| `{nombre}` | {c} |")
        print(f"| **Total** | **{total}** |\n")
    print(f"Kit: {len(tabla)} plugins, {total} skills. {len(informe.errores)} errores, {len(informe.avisos)} avisos.")
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
    return revisar(parser.parse_args(argv).conteo)


if __name__ == "__main__":
    sys.exit(main())
