"""nivel: propone un nivel de la escala 0-7 con la lista de criterios cumplidos y faltantes.

Es una propuesta basada en evidencia verificable. La decisión la toman el jurado y el responsable del dato.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from dataton.scorecard import scorecard

NO_CONOCIDO = re.compile(r"desconocid|por confirmar|sin verificar|por definir", re.I)


def buscar_escala(desde: Path) -> Path | None:
    for carpeta in [Path.cwd(), *desde.resolve().parents]:
        ruta = carpeta / "evaluacion" / "escala-preparacion-0-7.yml"
        if ruta.is_file():
            return ruta
    return None


def _campo_procedencia(paq: Path, etiqueta: str) -> str | None:
    """Valor de una fila clave-valor de la tabla de procedencia.md: '| Etiqueta… | valor |'."""
    ruta = paq / "procedencia.md"
    if not ruta.is_file():
        return None
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) >= 2 and celdas[0].lower().startswith(etiqueta.lower()):
            return celdas[1]
    return None


def _conocido(valor: str | None) -> bool:
    return bool(valor and valor.strip("* ") and not NO_CONOCIDO.search(valor))


def _todas(tablas_sc: dict, dimension: str, umbral: float, exigir_medible: bool = True) -> tuple[bool, str]:
    if not tablas_sc:
        return False, "no hay tablas que medir"
    malas = []
    for rel, r in tablas_sc.items():
        d = r.get(dimension) or {}
        v = d.get("valor")
        if v is None:
            if exigir_medible:
                malas.append(f"{rel}: no medible")
        elif v < umbral:
            malas.append(f"{rel}: {v * 100:.1f} %")
    return (not malas), "; ".join(malas) or "cumple en todas las tablas"


def evaluar(paq: Path, escala_ruta: Path, reglas_ruta: Path | None = None) -> dict:
    escala = yaml.safe_load(escala_ruta.read_text(encoding="utf-8"))
    u = escala["umbrales"]
    sc = scorecard(paq, reglas_ruta)
    tablas_sc = {k: v for k, v in sc["recursos"].items() if "error" not in v}
    reglas_ruta = reglas_ruta or paq / "reglas-calidad.yml"
    reglas = (yaml.safe_load(reglas_ruta.read_text(encoding="utf-8")) or {}) if reglas_ruta.is_file() else {}
    dp = paq / "datapackage.json"
    n_recursos = len(json.loads(dp.read_text(encoding="utf-8")).get("resources", [])) if dp.is_file() else 0

    def criterio(cid: str) -> tuple[bool, str]:
        if cid == "fuente_localizada":
            fuente = _campo_procedencia(paq, "Fuente")
            return (n_recursos > 0 or _conocido(fuente)), f"{n_recursos} recursos; fuente en procedencia.md: {'sí' if _conocido(fuente) else 'no'}"
        if cid == "diccionario_descrito":
            d = sc["paquete_dimensiones"]["documentacion"]
            v = d.get("valor")
            return (v is not None and v >= u["documentacion"]), ("no medible" if v is None else f"{v * 100:.1f} %")
        if cid == "periodicidad_conocida":
            v = _campo_procedencia(paq, "Periodicidad")
            return _conocido(v), f"declarada: {v!r}" if v is not None else "no declarada"
        if cid == "responsable_conocido":
            v = _campo_procedencia(paq, "Responsable del dato")
            return _conocido(v), "declarado y confirmado" if _conocido(v) else "no declarado o por confirmar"
        if cid == "completitud_minima":
            return _todas(tablas_sc, "completitud", u["completitud"])
        if cid == "validez_minima":
            return _todas(tablas_sc, "validez", u["validez"])
        if cid == "consistencia_minima":
            return _todas(tablas_sc, "consistencia", u["consistencia"])
        if cid == "unicidad_clave":
            sin_clave = [r for r, v in tablas_sc.items() if not isinstance(v["unicidad"].get("clave"), list)]
            if not tablas_sc or sin_clave:
                return False, "sin clave declarada en: " + ", ".join(sin_clave) if sin_clave else "no hay tablas"
            return _todas(tablas_sc, "unicidad", 1.0)
        if cid == "territorio_o_vinculo":
            if reglas.get("vinculos"):
                return True, f"{len(reglas['vinculos'])} vínculo(s) declarado(s)"
            return _todas(tablas_sc, "territorialidad", u["territorialidad"])
        if cid == "formato_abierto_y_licencia":
            v = sc["paquete_dimensiones"]["accesibilidad"]["valor"]
            return v == 1.0, f"accesibilidad {v * 100:.1f} %"
        if cid == "reglas_de_uso":
            return (paq / "reglas-de-uso.md").is_file(), ""
        raise ValueError(f"Criterio desconocido en la escala: {cid}")

    niveles, propuesto, seguir = [], 0, True
    for n in escala["niveles"]:
        cumplidos, faltantes = [], []
        for c in n.get("criterios", []):
            ok, detalle = criterio(c["id"])
            (cumplidos if ok else faltantes).append({"id": c["id"], "descripcion": c["descripcion"], "detalle": detalle})
        humano = bool(n.get("revision_humana"))
        if seguir and n["nivel"] > 0 and not humano and not faltantes:
            propuesto = n["nivel"]
        elif n["nivel"] > 0:
            seguir = False
        niveles.append({"nivel": n["nivel"], "nombre": n["nombre"], "revision_humana": humano,
                        "cumplidos": cumplidos, "faltantes": faltantes})
    nombre = next(n["nombre"] for n in escala["niveles"] if n["nivel"] == propuesto)
    return {
        "paquete": paq.name, "fecha": sc["fecha"], "herramienta": sc["herramienta"],
        "nivel_propuesto": propuesto, "nombre_nivel": nombre,
        "aviso": "Propuesta basada en criterios verificables. La deciden el jurado y el responsable del dato. Los niveles 6 y 7 requieren revisión humana.",
        "niveles": niveles,
    }


def resumen(r: dict) -> str:
    lineas = [f"{r['paquete']}: nivel propuesto {r['nivel_propuesto']} ({r['nombre_nivel']}). {r['aviso']}"]
    for n in r["niveles"][1:]:
        if n["revision_humana"]:
            lineas.append(f"  Nivel {n['nivel']} ({n['nombre']}): requiere revisión humana")
            continue
        for c in n["cumplidos"]:
            lineas.append(f"  Nivel {n['nivel']} [cumple] {c['id']}: {c['detalle']}")
        for c in n["faltantes"]:
            lineas.append(f"  Nivel {n['nivel']} [falta]  {c['id']}: {c['detalle']}")
    return "\n".join(lineas)
