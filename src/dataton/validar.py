"""validar: comprueba la estructura, los metadatos y las sumas de un paquete o de una entrega de equipo."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from dataton import tablas

ARCHIVOS_PAQUETE = ["README.md", "datapackage.json", "diccionario.csv", "procedencia.md", "reglas-de-uso.md",
                    "checksums.sha256"]
COLUMNAS_DICCIONARIO = ["archivo", "columna", "encabezado_literal", "tipo", "descripcion"]
# Estructura de la entrega de un equipo (repositorio creado desde la plantilla de equipo).
CARPETAS_ENTREGA = ["entrega/datos", "entrega/scripts", "entrega/salida"]
ARCHIVOS_ENTREGA = ["entrega/ficha-equipo.yml", "entrega/ficha-por-desafio.md", "entrega/diccionario.csv",
                    "entrega/procedencia.md", "entrega/antes-despues.md", "entrega/pasos-manuales.md", "autoria.yml"]
EXT_DATOS = {".csv", ".geojson", ".gpkg", ".json", ".xlsx", ".tif", ".zip"}


@dataclass
class Resultado:
    ruta: Path
    tipo: str
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errores


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as fh:
        for bloque in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def leer_checksums(ruta: Path) -> list[tuple[str, str]]:
    pares = []
    for n, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        if not linea.strip() or linea.startswith("#"):
            continue
        m = re.fullmatch(r"([0-9a-f]{64}) [ *](.+)", linea.strip())
        if not m:
            raise ValueError(f"{ruta.name}, línea {n}: formato no válido")
        pares.append((m.group(1), m.group(2)))
    return pares


def comprobar_checksums(base: Path, archivo: Path, res: Resultado) -> set[str]:
    listados = set()
    try:
        pares = leer_checksums(archivo)
    except ValueError as e:
        res.errores.append(str(e))
        return listados
    for suma, rel in pares:
        listados.add(rel)
        ruta = base / rel
        if not ruta.is_file():
            res.advertencias.append(f"Falta {rel}, listado en {archivo.name} (¿descarga pendiente?)")
        elif sha256(ruta) != suma:
            res.errores.append(f"La suma SHA-256 de {rel} no coincide con {archivo.name}")
    return listados


def es_url(texto: str) -> bool:
    return bool(re.match(r"https?://", texto or ""))


def validar_paquete(paq: Path) -> Resultado:
    res = Resultado(paq, "paquete")
    for nombre in ARCHIVOS_PAQUETE:
        if not (paq / nombre).is_file():
            res.errores.append(f"Falta el archivo obligatorio {nombre}")
    if not (paq / "problemas-observados.md").is_file():
        res.advertencias.append("No hay problemas-observados.md")

    dp_ruta = paq / "datapackage.json"
    if dp_ruta.is_file():
        try:
            dp = json.loads(dp_ruta.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            res.errores.append(f"datapackage.json no es JSON válido: {e}")
            dp = None
        if dp is not None:
            if not re.fullmatch(r"[a-z0-9._-]+", str(dp.get("name", ""))):
                res.errores.append("datapackage.json: 'name' falta o no usa solo minúsculas, números, '.', '_' o '-'")
            recursos = dp.get("resources")
            if not isinstance(recursos, list):
                res.errores.append("datapackage.json: falta la lista 'resources'")
                recursos = []
            nombres = [r.get("name") for r in recursos]
            if len(set(nombres)) != len(nombres):
                res.errores.append("datapackage.json: hay recursos con el mismo 'name'")
            if not dp.get("licenses") and not all(r.get("licenses") for r in recursos):
                res.advertencias.append("datapackage.json: no declara licencias")
            for r in recursos:
                ruta_r = r.get("path")
                if not r.get("name") or not ruta_r:
                    res.errores.append(f"Recurso sin 'name' o sin 'path': {r}")
                    continue
                if es_url(ruta_r):
                    res.advertencias.append(f"Recurso remoto no comprobado: {r['name']}")
                    continue
                local = paq / ruta_r
                if not local.is_file():
                    res.errores.append(f"El recurso {r['name']} apunta a {ruta_r}, que no existe")
                    continue
                if "bytes" in r and local.stat().st_size != r["bytes"]:
                    res.errores.append(f"El tamaño de {ruta_r} no coincide con datapackage.json")
                if str(r.get("hash", "")).startswith("sha256:") and sha256(local) != r["hash"][7:]:
                    res.errores.append(f"La suma de {ruta_r} no coincide con datapackage.json")
                campos = [f.get("name") for f in (r.get("schema") or {}).get("fields", [])]
                if campos and local.suffix in (".csv", ".geojson"):
                    tabla = tablas.leer(local)[0]
                    if tabla.encabezado != campos:
                        res.errores.append(f"Las columnas de {ruta_r} no coinciden con su esquema en datapackage.json")

    ck = paq / "checksums.sha256"
    listados = comprobar_checksums(paq, ck, res) if ck.is_file() else set()
    for ruta in sorted((paq / "data").rglob("*")) if (paq / "data").is_dir() else []:
        rel = ruta.relative_to(paq).as_posix()
        if ruta.is_file() and ruta.suffix in EXT_DATOS and rel not in listados:
            res.advertencias.append(f"{rel} no está en checksums.sha256")

    dic = paq / "diccionario.csv"
    if dic.is_file():
        with dic.open(encoding="utf-8", newline="") as fh:
            encabezado = next(csv.reader(fh), [])
        faltan = [c for c in COLUMNAS_DICCIONARIO if c not in encabezado]
        if faltan:
            res.errores.append(f"diccionario.csv: faltan las columnas {', '.join(faltan)}")
    return res


def validar_entrega(repo: Path) -> Resultado:
    res = Resultado(repo, "entrega")
    for c in CARPETAS_ENTREGA:
        if not (repo / c).is_dir():
            res.errores.append(f"Falta la carpeta {c}/")
    for a in ARCHIVOS_ENTREGA:
        if not (repo / a).is_file():
            res.errores.append(f"Falta el archivo {a}")
    ck = repo / "entrega" / "salida" / "checksums.sha256"
    if ck.is_file():
        comprobar_checksums(ck.parent, ck, res)
    else:
        res.advertencias.append("No hay entrega/salida/checksums.sha256: no se podrá comprobar la reproducibilidad")
    return res


def validar(ruta: Path) -> Resultado:
    if (ruta / "entrega").is_dir():
        return validar_entrega(ruta)
    return validar_paquete(ruta)


def paquetes_de(raiz: Path) -> list[Path]:
    """Paquetes de la carpeta paquetes/ (se omiten las carpetas que empiezan con '_')."""
    base = raiz / "paquetes"
    return sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith("_")) if base.is_dir() else []
