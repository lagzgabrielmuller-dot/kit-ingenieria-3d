#!/usr/bin/env python3
"""revisar_documento.py: último control del archivo que se va a entregar (Word, PowerPoint, Excel, PDF o texto).

Busca lo que un profesor ve enseguida y nadie revisa al final:
- marcadores sin completar: "(completar)", "[COMPLETAR]", "A completar", "TODO", "XXX", "lorem ipsum",
  "Haga clic aquí…", "Click to add…", títulos "Untitled"/"Sin título";
- un mismo nombre escrito de dos formas (TUBOMET y TUBMET, Yacyretá y Yaciretá);
- tablas de Word con columnas que tienen celdas vacías (por ejemplo, la columna "Presenta");
- palabras repetidas seguidas ("de de") y palabras que no van en un trabajo (chistes que quedaron, insultos).

  python revisar_documento.py informe.docx [presentacion.pptx planilla.xlsx informe.pdf ...]
  python revisar_documento.py informe.docx --prohibidas mis_palabras.txt
  python revisar_documento.py demo

Solo biblioteca estándar (para PDF usa pdftotext si está instalado, o PyMuPDF). Sale con código 1 si encuentra algo.
"""
from __future__ import annotations

import argparse
import difflib
import io
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

MARCADORES = re.compile(
    r"\(\s*completar[^)]*\)|\[\s*completar[^\]]*\]|\ba completar\b|\bcompletar aqu[ií]\b|\?\?\?+"
    r"|lorem ipsum|haga clic (?:aqu[ií]|para)|click (?:here|to add)|escriba aqu[ií]|texto de ejemplo|insertar (?:aqu[ií]|texto)"
    r"|\bUntitled\b|\bSin t[ií]tulo\b",
    re.I,
)
MARCADORES_MAYUSCULA = re.compile(r"\bTODO\b|\bTBD\b|\bFIXME\b|\bXXX+\b")  # en mayúsculas: "todo" en minúscula es una palabra normal
# Palabras que no deberían quedar en un trabajo (chistes que quedaron, insultos, risas). Se puede sumar una lista propia.
PROHIBIDAS = {
    "hentai", "porno", "xxx", "puto", "puta", "pelotudo", "boludo", "boludez", "mierda", "concha", "verga", "culo",
    "forro", "carajo", "jaja", "jajaja", "jsjs", "xd", "lol", "asdf", "qwerty", "fuck", "shit",
}
REPETIDA = re.compile(r"\b(\w{2,})\s+\1\b", re.I)


def sin_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)).casefold()


# ---------------------------------------------------------------- lectura de archivos

def texto_docx(datos: bytes):
    """(lista de (lugar, texto), lista de tablas como filas de celdas)."""
    with zipfile.ZipFile(io.BytesIO(datos)) as z:
        raiz = ET.fromstring(z.read("word/document.xml"))
    parrafos, tablas = [], []
    for i, p in enumerate(raiz.iter(W + "p"), start=1):
        texto = "".join(t.text or "" for t in p.iter(W + "t")).strip()
        if texto:
            parrafos.append((f"párrafo {i}", texto))
    for tbl in raiz.iter(W + "tbl"):
        filas = []
        for tr in tbl.findall(W + "tr"):
            filas.append(["".join(t.text or "" for t in tc.iter(W + "t")).strip() for tc in tr.findall(W + "tc")])
        tablas.append(filas)
    return parrafos, tablas


def texto_pptx(datos: bytes):
    salida = []
    with zipfile.ZipFile(io.BytesIO(datos)) as z:
        diapos = sorted((n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                        key=lambda n: int(re.findall(r"\d+", n)[-1]))
        for n in diapos:
            raiz = ET.fromstring(z.read(n))
            numero = re.findall(r"\d+", n)[-1]
            for p in raiz.iter(A + "p"):
                texto = "".join(t.text or "" for t in p.iter(A + "t")).strip()
                if texto:
                    salida.append((f"diapositiva {numero}", texto))
    return salida, []


def texto_xlsx(datos: bytes):
    salida = []
    with zipfile.ZipFile(io.BytesIO(datos)) as z:
        if "xl/sharedStrings.xml" in z.namelist():
            raiz = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for i, si in enumerate(raiz.iter(S + "si"), start=1):
                texto = "".join(t.text or "" for t in si.iter(S + "t")).strip()
                if texto:
                    salida.append((f"texto de celda {i}", texto))
    return salida, []


def texto_pdf(ruta: Path):
    if shutil.which("pdftotext"):
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "salida.txt"
            subprocess.run(["pdftotext", "-layout", str(ruta), str(destino)], check=True, capture_output=True)
            paginas = destino.read_text(encoding="utf-8", errors="replace").split("\f")
    else:
        try:
            import fitz  # type: ignore  # PyMuPDF
        except ImportError:
            raise RuntimeError("para leer PDF hace falta pdftotext (poppler) o PyMuPDF (pip install pymupdf)")
        with fitz.open(str(ruta)) as doc:
            paginas = [pagina.get_text() for pagina in doc]
    salida = []
    for n, pagina in enumerate(paginas, start=1):
        for linea in pagina.splitlines():
            if linea.strip():
                salida.append((f"página {n}", linea.strip()))
    return salida, []


def leer(ruta: Path):
    ext = ruta.suffix.lower()
    if ext == ".docx":
        return texto_docx(ruta.read_bytes())
    if ext == ".pptx":
        return texto_pptx(ruta.read_bytes())
    if ext == ".xlsx":
        return texto_xlsx(ruta.read_bytes())
    if ext == ".pdf":
        return texto_pdf(ruta)
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    return [(f"línea {i}", l.strip()) for i, l in enumerate(texto.splitlines(), start=1) if l.strip()], []


# ---------------------------------------------------------------- controles

def nombres_dobles(lineas):
    """Pares de siglas o nombres propios casi iguales que aparecen escritos de las dos formas.

    Cuenta las palabras en MAYÚSCULAS y las que empiezan con mayúscula en medio de una oración
    (nombres propios), para no confundir con palabras comunes al principio de un título.
    """
    cuenta = Counter()
    for _, texto in lineas:
        for m in re.finditer(r"\b[A-ZÁÉÍÓÚÑ]{4,}\b", texto):
            cuenta[m.group(0)] += 1
        for m in re.finditer(r"(?<=[a-záéíóúñü0-9,;:)] )[A-ZÁÉÍÓÚÑ][a-záéíóúñü]{3,}\b", texto):
            cuenta[m.group(0)] += 1
    palabras = sorted(cuenta)
    pares = []
    for i, a in enumerate(palabras):
        for b in palabras[i + 1:]:
            if a.casefold() == b.casefold():
                continue  # solo cambia la mayúscula (título y texto): no es un error
            ca, cb = sin_tildes(a), sin_tildes(b)
            if ca in (cb + "s", cb + "es") or cb in (ca + "s", ca + "es"):
                continue  # singular y plural
            if ca == cb:  # solo cambia una tilde: Yacyretá y Yacyreta
                pares.append((a, cuenta[a], b, cuenta[b]))
                continue
            parecidas = difflib.SequenceMatcher(None, ca, cb).ratio() >= 0.86 and abs(len(ca) - len(cb)) <= 2
            siglas = a.isupper() and b.isupper()
            if parecidas and (siglas or max(cuenta[a], cuenta[b]) >= 2):
                pares.append((a, cuenta[a], b, cuenta[b]))
    return pares


def revisar(nombre: str, lineas, tablas, prohibidas):
    hallazgos = []
    for lugar, texto in lineas:
        for m in list(MARCADORES.finditer(texto)) + list(MARCADORES_MAYUSCULA.finditer(texto)):
            hallazgos.append(("marcador sin completar", lugar, f"«{m.group(0)}» en: {texto[:110]}"))
        palabras = {sin_tildes(w) for w in re.findall(r"\w+", texto)}
        malas = sorted(palabras & prohibidas)
        if malas:
            hallazgos.append(("palabra que no va", lugar, f"«{', '.join(malas)}» en: {texto[:110]}"))
        for m in REPETIDA.finditer(texto):
            if not m.group(1).isdigit():
                hallazgos.append(("palabra repetida", lugar, f"«{m.group(0)}»"))
    for a, na, b, nb in nombres_dobles(lineas):
        hallazgos.append(("nombre escrito de dos formas", "todo el archivo", f"«{a}» ({na} veces) y «{b}» ({nb} veces): elegir una y usar buscar y reemplazar"))
    for t, filas in enumerate(tablas, start=1):
        if len(filas) < 2:
            continue
        encabezado = filas[0]
        for c, titulo in enumerate(encabezado):
            vacias = [f for f, fila in enumerate(filas[1:], start=2) if c < len(fila) and not fila[c]]
            if titulo and vacias:
                hallazgos.append(("tabla incompleta", f"tabla {t}", f"columna «{titulo}» vacía en {len(vacias)} de {len(filas) - 1} filas"))
    return [(nombre,) + h for h in hallazgos]


# ---------------------------------------------------------------- demo

def docx_de_prueba() -> bytes:
    def p(texto):
        return f'<w:p><w:r><w:t xml:space="preserve">{texto}</w:t></w:r></w:p>'

    def fila(celdas):
        return "<w:tr>" + "".join(f"<w:tc>{p(c) if c else '<w:p/>'}</w:tc>" for c in celdas) + "</w:tr>"

    cuerpo = "".join([
        p("Trabajo Práctico N.º 2: Distribución en planta de TUBOMET"),
        p("TUBOMET fabrica spools de tubería. La planta de TUBMET tiene cuatro sectores."),
        p("El equilibrado de línea de TUBMET se resolvió con el método de de Kilbridge."),
        p("Organización del grupo: (A completar por el grupo antes de la entrega)"),
        "<w:tbl>" + fila(["Bloque", "Integrante", "Presenta"]) + fila(["1", "Alumno A", ""]) + fila(["2", "Alumno B", ""]) + "</w:tbl>",
        p("Conclusiones del trabajo. jajaja"),
    ])
    documento = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                 f"<w:body>{cuerpo}</w:body></w:document>")
    tipos = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="xml" ContentType="application/xml"/>'
             '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
    salida = io.BytesIO()
    with zipfile.ZipFile(salida, "w") as z:
        z.writestr("[Content_Types].xml", tipos)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", documento)
    return salida.getvalue()


def imprimir(hallazgos) -> None:
    if not hallazgos:
        print("Sin observaciones: no aparecieron marcadores, nombres dobles, tablas incompletas ni palabras raras.")
        return
    tipo_actual = None
    for archivo, tipo, lugar, detalle in sorted(hallazgos, key=lambda h: (h[0], h[1])):
        if (archivo, tipo) != tipo_actual:
            tipo_actual = (archivo, tipo)
            print(f"\n[{archivo}] {tipo}")
        print(f"  {lugar}: {detalle}")
    print(f"\n{len(hallazgos)} cosas para revisar antes de entregar.")


def main(argv=None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description="Último control del archivo que se va a entregar.")
    parser.add_argument("archivos", nargs="+", help="archivos .docx, .pptx, .xlsx, .pdf, .md o .txt, o «demo»")
    parser.add_argument("--prohibidas", help="archivo de texto con más palabras a buscar, una por línea")
    args = parser.parse_args(argv)
    prohibidas = set(PROHIBIDAS)
    if args.prohibidas:
        prohibidas |= {sin_tildes(l.strip()) for l in Path(args.prohibidas).read_text(encoding="utf-8").splitlines() if l.strip()}
    if args.archivos == ["demo"]:
        print("Demo: un Word con los errores típicos (nombre de la empresa escrito de dos formas, tabla sin completar, texto que quedó).")
        lineas, tablas = texto_docx(docx_de_prueba())
        imprimir(revisar("demo.docx", lineas, tablas, prohibidas))
        return 0
    hallazgos = []
    for nombre in args.archivos:
        ruta = Path(nombre)
        try:
            lineas, tablas = leer(ruta)
        except (OSError, zipfile.BadZipFile, KeyError, ET.ParseError, RuntimeError, subprocess.CalledProcessError) as error:
            print(f"No pude leer {ruta.name}: {error}", file=sys.stderr)
            hallazgos.append((ruta.name, "no se pudo leer", "-", str(error)))
            continue
        hallazgos += revisar(ruta.name, lineas, tablas, prohibidas)
    imprimir(hallazgos)
    return 1 if hallazgos else 0


if __name__ == "__main__":
    sys.exit(main())
