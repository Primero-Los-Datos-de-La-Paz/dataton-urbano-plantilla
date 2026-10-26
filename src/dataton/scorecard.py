"""scorecard: mide dimensiones de calidad con reglas deterministas y declaradas.

Las reglas de cada paquete están en su archivo reglas-calidad.yml (ver docs/metricas.md).
Si una dimensión no tiene reglas declaradas, no se mide: se informa como "no medible".
Exactitud y oportunidad nunca se miden aquí: quedan para revisión humana.
Las mediciones son evidencia, no un puntaje.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import yaml

from dataton import __version__, tablas

FORMATOS_ABIERTOS = {".csv", ".json", ".geojson", ".gpkg", ".tif", ".tiff", ".txt", ".md", ".yml", ".yaml", ".parquet"}
REVISION_HUMANA = {
    "exactitud": "No se mide de forma automática: requiere comparar con la realidad o con otra fuente de referencia. Lo valora el jurado o el responsable del dato.",
    "oportunidad": "No se mide de forma automática: depende de la fecha del fenómeno y del uso previsto. Lo valora el jurado o el responsable del dato.",
}


def _proporcion(num: int, den: int) -> dict:
    return {"valor": round(num / den, 4) if den else None, "numerador": num, "denominador": den}


def _no_medible(motivo: str) -> dict:
    return {"valor": None, "medible": False, "motivo": motivo}


def _numero(texto: str) -> float | None:
    t = texto.strip()
    if re.fullmatch(r"-?\d+(\.\d+)?", t):
        return float(t)
    return None


# --- coordenadas ---------------------------------------------------------------

_GMS = re.compile(r"(\d{1,3})\s*°\s*(\d{1,2})\s*['’′]\s*([\d.,]+)\s*[\"”″]?\s*([NSEWO])", re.I)


def leer_coordenada(texto: str) -> tuple[float, float] | None:
    """Devuelve (lat, lon) si el texto es una coordenada legible; si no, None. No corrige nada."""
    t = (texto or "").strip()
    m = re.fullmatch(r"(-?\d{1,3}(?:\.\d+)?)\s*,\s*(-?\d{1,3}(?:\.\d+)?)", t)
    if m:
        return float(m.group(1)), float(m.group(2))
    partes = _GMS.findall(t)
    if len(partes) == 2:
        valores = {}
        for g, mi, s, h in partes:
            v = int(g) + int(mi) / 60 + float(s.replace(",", ".")) / 3600
            h = h.upper()
            if h in "SWO":
                v = -v
            valores["lat" if h in "NS" else "lon"] = v
        if len(valores) == 2:
            return valores["lat"], valores["lon"]
    return None


def _decimal(texto: str) -> float | None:
    t = (texto or "").strip().replace(",", ".")
    return float(t) if re.fullmatch(r"-?\d+(\.\d+)?", t) else None


# --- dimensiones por tabla ------------------------------------------------------

def completitud(t: tablas.Tabla, reglas: dict) -> dict:
    campos = reglas.get("campos_minimos") or list(range(len(t.encabezado)))
    indices = [c if isinstance(c, int) else t.indice(c) for c in campos]
    total = len(t.filas) * len(indices)
    llenas = sum(1 for f in t.filas for i in indices if i < len(f) and f[i].strip())
    r = _proporcion(llenas, total)
    r["campos"] = "todas las columnas" if not reglas.get("campos_minimos") else reglas["campos_minimos"]
    return r


def _cumple(valor: str, regla: dict) -> bool:
    v = valor.strip()
    if "tipo" in regla:
        tipo = regla["tipo"]
        if tipo == "entero" and not re.fullmatch(r"-?\d+", v):
            return False
        if tipo == "numero" and _numero(v) is None:
            return False
        if tipo == "fecha":
            try:
                dt.date.fromisoformat(v)
            except ValueError:
                return False
    if "patron" in regla and not re.fullmatch(regla["patron"], v):
        return False
    if "dominio" in regla and v not in [str(x) for x in regla["dominio"]]:
        return False
    if "minimo" in regla:
        n = _numero(v)
        if n is None or n < regla["minimo"]:
            return False
    if "maximo" in regla:
        n = _numero(v)
        if n is None or n > regla["maximo"]:
            return False
    return True


def validez(t: tablas.Tabla, reglas: dict) -> dict:
    lista = reglas.get("validez") or []
    if not lista:
        return _no_medible("No hay reglas de validez declaradas")
    detalle, num, den = [], 0, 0
    for regla in lista:
        valores = [v for v in t.columna(str(regla["columna"])) if v.strip()]
        ok = sum(1 for v in valores if _cumple(v, regla))
        num, den = num + ok, den + len(valores)
        detalle.append({"regla": regla, **_proporcion(ok, len(valores))})
    return {**_proporcion(num, den), "detalle": detalle}


def unicidad(t: tablas.Tabla, reglas: dict) -> dict:
    clave = reglas.get("clave")
    if clave:
        indices = [t.indice(str(c)) for c in clave]
        claves = [tuple(f[i].strip() if i < len(f) else "" for i in indices) for f in t.filas]
        con_valor = [k for k in claves if all(k)]
        cuenta = Counter(con_valor)
        unicas = sum(1 for k in con_valor if cuenta[k] == 1)
        r = _proporcion(unicas, len(con_valor))
        r.update({"clave": clave, "filas_sin_clave": len(claves) - len(con_valor),
                  "claves_duplicadas": sum(1 for v in cuenta.values() if v > 1)})
        return r
    cuenta = Counter(tuple(f) for f in t.filas)
    unicas = sum(1 for f in t.filas if cuenta[tuple(f)] == 1)
    r = _proporcion(unicas, len(t.filas))
    r["clave"] = "sin clave declarada: se cuentan filas idénticas"
    return r


def consistencia(t: tablas.Tabla, reglas: dict) -> dict:
    lista = reglas.get("consistencia") or []
    if not lista:
        return _no_medible("No hay reglas de consistencia declaradas")
    detalle, num, den = [], 0, 0
    for regla in lista:
        ok = evaluables = 0
        if regla["regla"] == "menor_o_igual":
            for a, b in zip(t.columna(str(regla["a"])), t.columna(str(regla["b"]))):
                na, nb = _numero(a), _numero(b)
                if na is None or nb is None:
                    continue
                evaluables += 1
                ok += na <= nb
        elif regla["regla"] == "suma":
            partes = [t.columna(str(p)) for p in regla["partes"]]
            vacio_cero = regla.get("vacio_como_cero", True)
            for i, total in enumerate(t.columna(str(regla["total"]))):
                nt = _numero(total)
                valores = [p[i] for p in partes]
                if nt is None or (not vacio_cero and not all(v.strip() for v in valores)):
                    continue
                nums = [_numero(v) if v.strip() else 0.0 for v in valores]
                if any(n is None for n in nums):
                    continue
                evaluables += 1
                ok += abs(sum(nums) - nt) < 1e-9
        else:
            raise ValueError(f"Regla de consistencia desconocida: {regla['regla']}")
        num, den = num + ok, den + evaluables
        detalle.append({"regla": regla, **_proporcion(ok, evaluables)})
    return {**_proporcion(num, den), "detalle": detalle}


def territorialidad(t: tablas.Tabla, reglas: dict) -> dict:
    terr = reglas.get("territorio")
    if not terr or "recuadro" not in terr:
        return _no_medible("No hay columnas de coordenadas ni recuadro territorial declarados")
    b = terr["recuadro"]
    if "coordenadas" in terr:
        pares = [leer_coordenada(v) for v in t.columna(str(terr["coordenadas"]))]
    else:
        lat, lon = t.columna(str(terr["lat"])), t.columna(str(terr["lon"]))
        pares = [(_decimal(a), _decimal(o)) for a, o in zip(lat, lon)]
        pares = [p if None not in p else None for p in pares]
    legibles = [p for p in pares if p]
    dentro = sum(1 for la, lo in legibles if b["lat_min"] <= la <= b["lat_max"] and b["lon_min"] <= lo <= b["lon_max"])
    r = _proporcion(dentro, len(t.filas))
    r.update({"legibles": len(legibles), "aproximada": True,
              "metodo": "Recuadro (rectángulo), no polígono: es una verificación geográfica aproximada.",
              "fuente_recuadro": terr.get("fuente_recuadro", "no declarada")})
    return r


def documentacion_tabla(t: tablas.Tabla, rel: str, diccionario: list[dict]) -> dict:
    descritas = {d["encabezado_literal"] for d in diccionario if d.get("archivo") == rel and d.get("descripcion", "").strip()}
    columnas = [h for h in t.encabezado]
    return _proporcion(sum(1 for h in columnas if h in descritas), len(columnas))


# --- paquete -------------------------------------------------------------------

def _leer_diccionario(paq: Path) -> list[dict]:
    ruta = paq / "diccionario.csv"
    if not ruta.is_file():
        return []
    with ruta.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def trazabilidad(paq: Path) -> dict:
    proc = paq / "procedencia.md"
    texto = proc.read_text(encoding="utf-8") if proc.is_file() else ""
    componentes = {
        "procedencia.md existe": proc.is_file() and bool(texto.strip()),
        "checksums.sha256 existe": (paq / "checksums.sha256").is_file(),
        "registro de cambios (sección '## …cambios…' en procedencia.md o archivo registro-cambios.md)":
            bool(re.search(r"^##.*cambios", texto, re.I | re.M)) or (paq / "registro-cambios.md").is_file(),
    }
    r = _proporcion(sum(componentes.values()), len(componentes))
    r["componentes"] = componentes
    return r


def accesibilidad(paq: Path, recursos: list[dict]) -> dict:
    locales = [r for r in recursos if not re.match(r"https?://", r.get("path", ""))]
    abiertos = [r for r in locales if Path(r["path"]).suffix.lower() in FORMATOS_ABIERTOS]
    dp = paq / "datapackage.json"
    licencias = []
    if dp.is_file():
        d = json.loads(dp.read_text(encoding="utf-8"))
        licencias = d.get("licenses") or []
    componentes = {
        "recursos en formato abierto": _proporcion(len(abiertos), len(locales)),
        "licencia o reglas de uso declaradas en datapackage.json": bool(licencias),
    }
    partes = [componentes["recursos en formato abierto"]["valor"] or 0.0, 1.0 if licencias else 0.0]
    return {"valor": round(sum(partes) / 2, 4), "componentes": componentes}


def scorecard(paq: Path, reglas_ruta: Path | None = None) -> dict:
    reglas_ruta = reglas_ruta or paq / "reglas-calidad.yml"
    reglas = yaml.safe_load(reglas_ruta.read_text(encoding="utf-8")) if reglas_ruta.is_file() else {}
    reglas_rec = (reglas or {}).get("recursos") or {}
    dp = paq / "datapackage.json"
    recursos = json.loads(dp.read_text(encoding="utf-8")).get("resources", []) if dp.is_file() else []
    diccionario = _leer_diccionario(paq)

    if reglas_rec:
        rutas = list(reglas_rec)
    elif recursos:
        rutas = [r["path"] for r in recursos if not re.match(r"https?://", r.get("path", ""))
                 and Path(r["path"]).suffix in (".csv", ".geojson") and r["path"].startswith("data/")]
    else:  # sin datapackage.json (por ejemplo, una entrega de equipo): tablas de salida/ y data/
        rutas = sorted(p.relative_to(paq).as_posix() for carpeta in ("salida", "data") if (paq / carpeta).is_dir()
                       for p in (paq / carpeta).rglob("*") if p.suffix in (".csv", ".geojson"))

    por_recurso, doc_num, doc_den = {}, 0, 0
    for rel in rutas:
        ruta = paq / rel
        if not ruta.is_file():
            por_recurso[rel] = {"error": "el archivo no existe"}
            continue
        t = tablas.leer(ruta)[0]
        rr = reglas_rec.get(rel) or {}
        doc = documentacion_tabla(t, rel, diccionario)
        doc_num, doc_den = doc_num + doc["numerador"], doc_den + doc["denominador"]
        por_recurso[rel] = {
            "filas": len(t.filas), "columnas": len(t.encabezado),
            "completitud": completitud(t, rr), "validez": validez(t, rr), "unicidad": unicidad(t, rr),
            "consistencia": consistencia(t, rr), "territorialidad": territorialidad(t, rr), "documentacion": doc,
        }

    return {
        "herramienta": f"dataton {__version__}",
        "fecha": dt.date.today().isoformat(),
        "paquete": paq.name,
        "reglas": {"archivo": reglas_ruta.name if reglas_ruta.is_file() else None,
                   "sha256": hashlib.sha256(reglas_ruta.read_bytes()).hexdigest() if reglas_ruta.is_file() else None},
        "aviso": "Estas mediciones son evidencia para el jurado y el responsable del dato; no son un puntaje.",
        "recursos": por_recurso,
        "paquete_dimensiones": {
            "documentacion": _proporcion(doc_num, doc_den) if doc_den else _no_medible("No hay tablas que medir"),
            "trazabilidad": trazabilidad(paq),
            "accesibilidad": accesibilidad(paq, recursos),
        },
        "revision_humana": REVISION_HUMANA,
    }


def resumen(sc: dict) -> str:
    def fmt(d: dict) -> str:
        if d.get("valor") is None:
            return "no medible" if d.get("medible") is False else "sin datos"
        return f"{d['valor'] * 100:.1f} %"
    lineas = [f"Scorecard de {sc['paquete']} ({sc['fecha']}). {sc['aviso']}"]
    for rel, r in sc["recursos"].items():
        if "error" in r:
            lineas.append(f"  {rel}: {r['error']}")
            continue
        lineas.append(f"  {rel} ({r['filas']} filas, {r['columnas']} columnas)")
        for dim in ("completitud", "validez", "unicidad", "consistencia", "territorialidad", "documentacion"):
            lineas.append(f"    {dim:<16} {fmt(r[dim])}")
    for dim, v in sc["paquete_dimensiones"].items():
        lineas.append(f"  [paquete] {dim:<16} {fmt(v)}")
    for dim in sc["revision_humana"]:
        lineas.append(f"  [revisión humana] {dim}")
    return "\n".join(lineas)
