"""Lectura y validación de edicion/edicion.yml.

edicion.yml es la única fuente de nombres, fechas, sede, desafíos, pesos,
responsables, contacto y reglas de visibilidad de una edición. Un valor
vacío (null) significa "por definir": se acepta, pero se informa.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import yaml

RUTA_EDICION = Path("edicion") / "edicion.yml"

CLAVES_OBLIGATORIAS = [
    "version_esquema",
    "edicion",
    "github",
    "sede",
    "calendario",
    "desafios",
    "rubrica",
    "contacto",
    "visibilidad",
]


class ErrorEdicion(Exception):
    """El archivo edicion.yml no se puede usar."""


def cargar(ruta: Path) -> dict:
    """Lee edicion.yml y devuelve su contenido como diccionario."""
    if not ruta.is_file():
        raise ErrorEdicion(f"No existe el archivo {ruta}")
    with ruta.open(encoding="utf-8") as fh:
        datos = yaml.safe_load(fh)
    if not isinstance(datos, dict):
        raise ErrorEdicion(f"{ruta} no contiene un diccionario YAML")
    return datos


def _es_fecha(valor) -> bool:
    return isinstance(valor, dt.date)


def validar(ed: dict) -> tuple[list[str], list[str]]:
    """Devuelve (errores, pendientes).

    errores: impiden generar la edición.
    pendientes: campos vacíos que la edición debe completar.
    """
    errores: list[str] = []
    pendientes: list[str] = []

    for clave in CLAVES_OBLIGATORIAS:
        if clave not in ed:
            errores.append(f"Falta la clave '{clave}'")
    if errores:
        return errores, pendientes

    def pendiente_si_vacio(ruta: str, valor) -> None:
        if valor is None or valor == "":
            pendientes.append(ruta)

    for clave in ("id", "nombre", "programa", "anio", "ciudad", "institucion"):
        pendiente_si_vacio(f"edicion.{clave}", ed["edicion"].get(clave))
    pendiente_si_vacio("github.organizacion", ed["github"].get("organizacion"))
    pendiente_si_vacio("sede.nombre", ed["sede"].get("nombre"))
    pendiente_si_vacio("contacto.buzon_institucional", ed["contacto"].get("buzon_institucional"))

    ids = set()
    for i, act in enumerate(ed["calendario"] or []):
        aid = act.get("id")
        if not aid:
            errores.append(f"calendario[{i}] no tiene 'id'")
            continue
        if aid in ids:
            errores.append(f"calendario: id repetido '{aid}'")
        ids.add(aid)
        for campo in ("fecha_inicio", "fecha_fin"):
            v = act.get(campo)
            if v is not None and not _es_fecha(v):
                errores.append(f"calendario.{aid}.{campo}: '{v}' no es una fecha AAAA-MM-DD")
        if act.get("fecha_inicio") is None and not act.get("mes"):
            pendientes.append(f"calendario.{aid}.fecha_inicio")
        ini, fin = act.get("fecha_inicio"), act.get("fecha_fin")
        if _es_fecha(ini) and _es_fecha(fin) and fin < ini:
            errores.append(f"calendario.{aid}: la fecha de fin es anterior a la de inicio")

    ids = set()
    for i, des in enumerate(ed["desafios"] or []):
        did = des.get("id")
        if not did:
            errores.append(f"desafios[{i}] no tiene 'id'")
            continue
        if did in ids:
            errores.append(f"desafios: id repetido '{did}'")
        ids.add(did)
        for campo in ("slug", "titulo", "nivel_esperado"):
            pendiente_si_vacio(f"desafios.{did}.{campo}", des.get(campo))
        resp = des.get("responsable_dato") or {}
        pendiente_si_vacio(f"desafios.{did}.responsable_dato.unidad", resp.get("unidad"))
        owner = resp.get("codeowner") or ""
        if owner and not owner.startswith("@"):
            errores.append(f"desafios.{did}.responsable_dato.codeowner debe empezar con '@'")

    criterios = (ed["rubrica"] or {}).get("criterios") or []
    pesos = [c.get("peso") for c in criterios]
    if not criterios:
        pendientes.append("rubrica.criterios")
    elif any(p is None for p in pesos):
        pendientes.append("rubrica.criterios[].peso")
    elif sum(pesos) != 100:
        errores.append(f"rubrica: los pesos suman {sum(pesos)}, no 100")

    return errores, pendientes
