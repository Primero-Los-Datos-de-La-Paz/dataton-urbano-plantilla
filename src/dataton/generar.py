"""Genera el contenido que depende de edicion/edicion.yml.

Los archivos del repositorio llevan bloques marcados. Solo se reescribe lo que
está entre las marcas; el resto del texto queda igual.

En Markdown:   <!-- dataton:NOMBRE ARGUMENTOS --> ... <!-- /dataton -->
En YAML y CODEOWNERS (líneas completas):
               # dataton:NOMBRE ARGUMENTOS
               ...
               # /dataton

Además, CITATION.cff se genera completo.
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

import yaml

POR_DEFINIR = "_(por definir en `edicion/edicion.yml`)_"
POR_DEFINIR_TEXTO = "(por definir en edicion/edicion.yml)"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

EXTENSIONES = {".md", ".yml", ".yaml"}
NOMBRES_SIN_EXTENSION = {"CODEOWNERS"}
EXCLUIR_CARPETAS = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}

MARCA_MD = re.compile(r"<!-- dataton:([\w-]+)((?: [^>]*?)?) -->(.*?)<!-- /dataton -->", re.S)
MARCA_LINEA = re.compile(r"^(?P<sangria>[ \t]*)# dataton:(?P<nombre>[\w-]+)(?P<args>(?: .*)?)$")
FIN_LINEA = re.compile(r"^[ \t]*# /dataton[ \t]*$")


class ErrorBloque(Exception):
    """Un bloque marcado no se puede generar."""


# --- formato -----------------------------------------------------------------

def fecha_larga(d: dt.date | None, con_dia: bool = True) -> str:
    if d is None:
        return POR_DEFINIR_TEXTO
    texto = f"{d.day} de {MESES[d.month - 1]} de {d.year}"
    return f"{DIAS[d.weekday()]} {texto}" if con_dia else texto


def texto_actividad(act: dict) -> str:
    ini, fin = act.get("fecha_inicio"), act.get("fecha_fin")
    if ini is None and act.get("mes"):
        anio, mes = str(act["mes"]).split("-")
        texto = f"{MESES[int(mes) - 1]} de {anio}"
        return texto[0].upper() + texto[1:]
    if ini is None:
        return POR_DEFINIR_TEXTO
    if fin is None or fin == ini:
        return fecha_larga(ini)
    return f"del {fecha_larga(ini)} al {fecha_larga(fin)}"


def _celda(valor) -> str:
    if valor is None or valor == "":
        return POR_DEFINIR
    return str(valor).replace("|", "/").replace("\n", " ")


def _obtener(ed: dict, ruta: str):
    actual = ed
    for parte in ruta.split("."):
        if isinstance(actual, dict):
            actual = actual.get(parte)
        else:
            raise ErrorBloque(f"La ruta '{ruta}' no existe en edicion.yml")
    return actual


def _actividad(ed: dict, aid: str) -> dict:
    for act in ed.get("calendario") or []:
        if act.get("id") == aid:
            return act
    raise ErrorBloque(f"No existe la actividad '{aid}' en calendario")


# --- bloques Markdown ----------------------------------------------------------

def b_valor(ed: dict, args: list[str]) -> str:
    valor = _obtener(ed, args[0])
    if isinstance(valor, dt.date):
        return fecha_larga(valor)
    return POR_DEFINIR if valor in (None, "") else str(valor)


def b_fecha(ed: dict, args: list[str]) -> str:
    act = _actividad(ed, args[0])
    cual = args[1] if len(args) > 1 else "completa"
    if cual == "inicio":
        return fecha_larga(act.get("fecha_inicio"))
    if cual == "fin":
        return fecha_larga(act.get("fecha_fin") or act.get("fecha_inicio"))
    return texto_actividad(act)


def b_calendario(ed: dict, args: list[str]) -> str:
    filas = ["| Fecha | Actividad |", "|---|---|"]
    for act in ed.get("calendario") or []:
        filas.append(f"| {texto_actividad(act)} | {_celda(act.get('actividad'))} |")
    if len(filas) == 2:
        filas.append(f"| {POR_DEFINIR} | |")
    return "\n".join(filas)


def b_desafios(ed: dict, args: list[str]) -> str:
    filas = ["| Desafío | Título | Alcance en esta edición | Nivel esperado |", "|---|---|---|---|"]
    for d in ed.get("desafios") or []:
        filas.append(f"| {_celda(d.get('id'))} | {_celda(d.get('titulo'))} | "
                     f"{_celda(d.get('alcance'))} | {_celda(d.get('nivel_esperado'))} |")
    return "\n".join(filas)


def b_rubrica(ed: dict, args: list[str]) -> str:
    criterios = (ed.get("rubrica") or {}).get("criterios") or []
    filas = ["| Criterio | Peso |", "|---|---:|"]
    for c in criterios:
        peso = c.get("peso")
        filas.append(f"| {_celda(c.get('nombre'))} | {POR_DEFINIR if peso is None else f'{peso} %'} |")
    pesos = [c.get("peso") for c in criterios]
    if criterios and all(p is not None for p in pesos):
        filas.append(f"| **Total** | **{sum(pesos)} %** |")
    return "\n".join(filas)


def b_responsables(ed: dict, args: list[str]) -> str:
    filas = ["| Desafío | Responsable del dato | Marcador en CODEOWNERS |", "|---|---|---|"]
    for d in ed.get("desafios") or []:
        r = d.get("responsable_dato") or {}
        filas.append(f"| {_celda(d.get('id'))} {_celda(d.get('titulo'))} | {_celda(r.get('unidad'))} | "
                     f"`{r.get('codeowner') or '@RESPONSABLE-' + str(d.get('id'))}` |")
    return "\n".join(filas)


def b_roles(ed: dict, args: list[str]) -> str:
    filas = ["| Rol | Quién |", "|---|---|"]
    for r in (ed.get("edicion") or {}).get("roles") or []:
        filas.append(f"| {_celda(r.get('rol'))} | {_celda(r.get('quien'))} |")
    if len(filas) == 2:
        filas.append(f"| {POR_DEFINIR} | |")
    return "\n".join(filas)


def b_contacto(ed: dict, args: list[str]) -> str:
    c = ed.get("contacto") or {}
    buzon = c.get("buzon_institucional")
    lineas = [f"- Buzón institucional: {buzon if buzon else POR_DEFINIR}"]
    if c.get("incidencias", True):
        lineas.append("- Incidencias de este repositorio (pestaña *Issues*), con el formulario que corresponda.")
    if c.get("nota"):
        lineas.append(f"- {c['nota']}")
    return "\n".join(lineas)


def b_visibilidad(ed: dict, args: list[str]) -> str:
    v = ed.get("visibilidad") or {}
    filas = []
    if v.get("regla_general"):
        filas += [v["regla_general"], ""]
    filas += ["| Repositorio | Visibilidad inicial | Visibilidad prevista | Condición |", "|---|---|---|---|"]
    repos = (ed.get("github") or {}).get("repositorios") or {}
    for r in v.get("repositorios") or []:
        nombre = repos.get(r.get("repositorio"), r.get("repositorio"))
        nombre = f"`{nombre}`" if nombre else POR_DEFINIR
        filas.append(f"| {nombre} | {_celda(r.get('visibilidad_inicial'))} | "
                     f"{_celda(r.get('visibilidad_prevista'))} | {_celda(r.get('condicion'))} |")
    internos = v.get("datos_internos") or []
    if internos:
        filas.append("")
        filas += [f"- {regla}" for regla in internos]
    return "\n".join(filas)


BLOQUES_MD = {
    "valor": b_valor,
    "fecha": b_fecha,
    "calendario": b_calendario,
    "desafios": b_desafios,
    "rubrica": b_rubrica,
    "responsables": b_responsables,
    "roles": b_roles,
    "contacto": b_contacto,
    "visibilidad": b_visibilidad,
}

# Bloques que van en una sola línea de texto (no llevan saltos de línea alrededor).
EN_LINEA = {"valor", "fecha"}


# --- bloques de línea (YAML, CODEOWNERS) ---------------------------------------

def l_opciones_desafios(ed: dict, args: list[str]) -> list[str]:
    opciones = [f"- \"{d.get('id')} · {d.get('titulo') or 'por definir'}\"" for d in ed.get("desafios") or []]
    return opciones + ['- "No sé / varios desafíos"']


def l_codeowners(ed: dict, args: list[str]) -> list[str]:
    lineas = []
    for d in ed.get("desafios") or []:
        owner = (d.get("responsable_dato") or {}).get("codeowner") or f"@RESPONSABLE-{d.get('id')}"
        slug = d.get("slug") or str(d.get("id")).lower()
        lineas.append(f"/paquetes/{d.get('id')}-{slug}/ {owner}")
    return lineas


BLOQUES_LINEA = {
    "opciones-desafios": l_opciones_desafios,
    "codeowners": l_codeowners,
}


# --- procesamiento de archivos ---------------------------------------------------

def procesar_md(texto: str, ed: dict) -> str:
    def reemplazo(m: re.Match) -> str:
        nombre, args = m.group(1), m.group(2).split()
        if nombre not in BLOQUES_MD:
            raise ErrorBloque(f"Bloque desconocido: {nombre}")
        contenido = BLOQUES_MD[nombre](ed, args)
        cuerpo = contenido if nombre in EN_LINEA else f"\n{contenido}\n"
        return f"<!-- dataton:{nombre}{m.group(2)} -->{cuerpo}<!-- /dataton -->"
    return MARCA_MD.sub(reemplazo, texto)


def procesar_lineas(texto: str, ed: dict) -> str:
    salida: list[str] = []
    lineas = texto.split("\n")
    i = 0
    while i < len(lineas):
        m = MARCA_LINEA.match(lineas[i])
        if not m:
            salida.append(lineas[i])
            i += 1
            continue
        nombre = m.group("nombre")
        if nombre not in BLOQUES_LINEA:
            raise ErrorBloque(f"Bloque desconocido: {nombre}")
        j = i + 1
        while j < len(lineas) and not FIN_LINEA.match(lineas[j]):
            j += 1
        if j == len(lineas):
            raise ErrorBloque(f"Bloque '{nombre}' sin cierre '# /dataton'")
        sangria = m.group("sangria")
        salida.append(lineas[i])
        salida += [sangria + l for l in BLOQUES_LINEA[nombre](ed, m.group("args").split())]
        salida.append(lineas[j])
        i = j + 1
    return "\n".join(salida)


def citation(ed: dict) -> str:
    e = ed.get("edicion") or {}
    inst = e.get("institucion") or {}
    repos = (ed.get("github") or {}).get("repositorios") or {}
    org = (ed.get("github") or {}).get("organizacion")
    datos = {
        "cff-version": "1.2.0",
        "message": "Si usas este repositorio, cítalo con estos datos.",
        "title": e.get("nombre") or "Datatón urbano de preparación de datos (plantilla)",
        "type": "software",
        "authors": [{"name": inst.get("nombre") or "Por definir en edicion/edicion.yml"}],
        "version": e.get("version_repositorio") or "0.1.0",
        "keywords": ["datatón", "datos abiertos", "preparación de datos", "ciudad inteligente"],
    }
    if org and repos.get("edicion"):
        datos["repository-code"] = f"https://github.com/{org}/{repos['edicion']}"
    encabezado = "# Archivo generado desde edicion/edicion.yml con `python -m dataton regenerar`. No lo edites a mano.\n"
    return encabezado + yaml.safe_dump(datos, allow_unicode=True, sort_keys=False)


def archivos_con_bloques(raiz: Path):
    for ruta in sorted(raiz.rglob("*")):
        if not ruta.is_file() or any(p in EXCLUIR_CARPETAS for p in ruta.relative_to(raiz).parts):
            continue
        if ruta.suffix in EXTENSIONES or ruta.name in NOMBRES_SIN_EXTENSION:
            yield ruta


def regenerar(raiz: Path, ed: dict, solo_comprobar: bool = False) -> list[Path]:
    """Reescribe los bloques de todos los archivos. Devuelve los que cambiaron
    (o que cambiarían, si solo_comprobar es verdadero)."""
    cambiados = []
    for ruta in archivos_con_bloques(raiz):
        if ruta.relative_to(raiz).as_posix() == "edicion/edicion.yml":
            continue
        original = ruta.read_text(encoding="utf-8")
        nuevo = procesar_md(original, ed) if ruta.suffix == ".md" else procesar_lineas(original, ed)
        if nuevo != original:
            cambiados.append(ruta)
            if not solo_comprobar:
                ruta.write_text(nuevo, encoding="utf-8", newline="\n")
    ruta_cff = raiz / "CITATION.cff"
    nuevo = citation(ed)
    if not ruta_cff.exists() or ruta_cff.read_text(encoding="utf-8") != nuevo:
        cambiados.append(ruta_cff)
        if not solo_comprobar:
            ruta_cff.write_text(nuevo, encoding="utf-8", newline="\n")
    return cambiados
