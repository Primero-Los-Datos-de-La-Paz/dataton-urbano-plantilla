"""Lectura de tablas: CSV (con detección de codificación y separador), GeoJSON y xlsx.

Solo usa la biblioteca estándar. Cada lector devuelve una Tabla con el
encabezado y las filas como texto, sin convertir ni limpiar valores.
"""

from __future__ import annotations

import csv
import io
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

FORMATOS_TABLA = {".csv", ".geojson", ".xlsx"}

_M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"


@dataclass
class Tabla:
    nombre: str                      # ruta del archivo (y hoja, en xlsx)
    encabezado: list[str]
    filas: list[list[str]]
    codificacion: str = "utf-8"
    separador: str = ","
    extra: dict = field(default_factory=dict)

    def columna(self, nombre: str) -> list[str]:
        i = self.indice(nombre)
        return [f[i] if i < len(f) else "" for f in self.filas]

    def indice(self, nombre: str) -> int:
        """Busca la columna por nombre exacto, luego sin espacios a los lados, luego por letra (A, B, … AA)."""
        if nombre in self.encabezado:
            return self.encabezado.index(nombre)
        limpios = [h.strip() for h in self.encabezado]
        if nombre.strip() in limpios:
            return limpios.index(nombre.strip())
        if re.fullmatch(r"[A-Z]{1,3}", nombre):
            n = 0
            for ch in nombre:
                n = n * 26 + ord(ch) - 64
            if n - 1 < len(self.encabezado):
                return n - 1
        raise KeyError(f"La columna '{nombre}' no existe en {self.nombre}")


def decodificar(raw: bytes) -> tuple[str, str]:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc), ("utf-8" if enc.startswith("utf-8") else enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("No se reconoce la codificación del archivo")


def detectar_separador(texto: str) -> str:
    primera = texto.split("\n", 1)[0]
    return max([",", ";", "\t", "|"], key=primera.count)


def leer_csv(ruta: Path, nombre: str | None = None) -> Tabla:
    texto, enc = decodificar(ruta.read_bytes())
    sep = detectar_separador(texto)
    filas = list(csv.reader(io.StringIO(texto), delimiter=sep))
    enc_fila = filas[0] if filas else []
    return Tabla(nombre or ruta.as_posix(), enc_fila, filas[1:], enc, sep)


def leer_geojson(ruta: Path, nombre: str | None = None) -> Tabla:
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    feats = datos.get("features", [])
    claves: list[str] = []
    for f in feats:
        for k in (f.get("properties") or {}):
            if k not in claves:
                claves.append(k)
    filas, coords = [], []
    for f in feats:
        p = f.get("properties") or {}
        filas.append(["" if p.get(k) is None else str(p.get(k)) for k in claves])
        g = f.get("geometry") or {}
        coords.append(g.get("coordinates") if g.get("type") == "Point" else None)
    return Tabla(nombre or ruta.as_posix(), claves, filas, extra={"puntos": coords})


def _texto_compartido(si: ET.Element) -> str:
    partes = [t.text or "" for t in si.findall(f"{_M}t")]
    partes += [t.text or "" for r in si.findall(f"{_M}r") for t in r.findall(f"{_M}t")]
    return "".join(partes)


def _columna_xlsx(ref: str) -> int:
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def leer_xlsx(ruta: Path) -> list[Tabla]:
    """Una Tabla por hoja, con los valores tal como están guardados (sin formato de visualización)."""
    z = zipfile.ZipFile(ruta)
    compartidos = []
    if "xl/sharedStrings.xml" in z.namelist():
        compartidos = [_texto_compartido(si) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(f"{_M}si")]
    libro = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target")
            for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels")).iter(f"{_REL}Relationship")}
    tablas = []
    for hoja in libro.find(f"{_M}sheets"):
        destino = rels[hoja.get(f"{_R}id")].lstrip("/")
        destino = destino if destino.startswith("xl/") else "xl/" + destino
        filas: dict[int, dict[int, str]] = {}
        for fila in ET.fromstring(z.read(destino)).iter(f"{_M}row"):
            celdas = {}
            for c in fila.findall(f"{_M}c"):
                tipo, v = c.get("t"), c.find(f"{_M}v")
                if tipo == "s" and v is not None:
                    celdas[_columna_xlsx(c.get("r"))] = compartidos[int(v.text)]
                elif tipo == "inlineStr":
                    celdas[_columna_xlsx(c.get("r"))] = "".join(t.text or "" for t in c.iter(f"{_M}t"))
                elif v is not None:
                    celdas[_columna_xlsx(c.get("r"))] = v.text or ""
            filas[int(fila.get("r"))] = celdas
        n_cols = max((max(c) + 1 for c in filas.values() if c), default=0)
        matriz = [[filas.get(r, {}).get(c, "") for c in range(n_cols)] for r in range(1, max(filas, default=0) + 1)]
        tablas.append(Tabla(f"{ruta.as_posix()}#{hoja.get('name')}", matriz[0] if matriz else [], matriz[1:]))
    return tablas


def metadatos_autor_xlsx(ruta: Path) -> list[str]:
    """Campos de autor no vacíos en docProps/core.xml (sin devolver su contenido)."""
    z = zipfile.ZipFile(ruta)
    if "docProps/core.xml" not in z.namelist():
        return []
    xml = z.read("docProps/core.xml").decode("utf-8", errors="ignore")
    return [campo for campo in ("creator", "lastModifiedBy")
            if re.search(rf"<[^>]*{campo}>[^<]+</", xml)]


def leer(ruta: Path) -> list[Tabla]:
    if ruta.suffix == ".csv":
        return [leer_csv(ruta)]
    if ruta.suffix == ".geojson":
        return [leer_geojson(ruta)]
    if ruta.suffix == ".xlsx":
        return leer_xlsx(ruta)
    return []
