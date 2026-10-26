"""recolectar: reúne las entregas y consolida la evidencia automática por equipo.

- Con --org: clona cada repositorio de equipo en la etiqueta entrega-final (o en main, si no la tiene)
  dentro de una carpeta local, y deja los archivos en solo lectura.
- Con --carpeta: evalúa entregas que ya están en una carpeta local (por ejemplo, ZIP de equipos sin
  cuenta de GitHub, descomprimidos por la organización).

Para cada entrega ejecuta validar, verificar-privacidad, scorecard y nivel, y escribe un informe en
evaluacion/informes/. No ejecuta el código de los equipos: para eso está `reproducir`, que se corre aparte.
La evidencia automática no es el puntaje final: lo pone el jurado.
"""

from __future__ import annotations

import csv
import json
import os
import stat
from pathlib import Path
from typing import Callable

from dataton import nivel as m_nivel
from dataton import privacidad, scorecard, validar
from dataton.equipos import ETIQUETA_ENTREGA, GitHub


def solo_lectura(carpeta: Path) -> None:
    for raiz, dirs, archivos in os.walk(carpeta):
        for a in archivos:
            p = Path(raiz) / a
            p.chmod(p.stat().st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def clonar(repos: list[str], org: str, destino: Path, gh: GitHub, salida: Callable[[str], None] = print) -> list[Path]:
    destino.mkdir(parents=True, exist_ok=True)
    clonados = []
    for r in repos:
        carpeta = destino / r
        if carpeta.exists():
            salida(f"  {r}: ya estaba clonado, se usa la copia local")
            clonados.append(carpeta)
            continue
        res = gh.correr(["gh", "repo", "clone", f"{org}/{r}", str(carpeta), "--", "--depth", "1", "--branch", ETIQUETA_ENTREGA])
        if res.returncode != 0:
            res = gh.correr(["gh", "repo", "clone", f"{org}/{r}", str(carpeta), "--", "--depth", "1"])
            salida(f"  {r}: sin etiqueta {ETIQUETA_ENTREGA}; se clonó main")
        if res.returncode != 0:
            salida(f"  {r}: ERROR al clonar")
            continue
        solo_lectura(carpeta)
        clonados.append(carpeta)
    return clonados


def evaluar_entrega(repo: Path, escala: Path) -> dict:
    v = validar.validar(repo)
    hallazgos = privacidad.verificar(repo)
    base = repo / "entrega" if (repo / "entrega").is_dir() else repo
    sc = scorecard.scorecard(base)
    nv = m_nivel.evaluar(base, escala)
    return {
        "entrega": repo.name,
        "aviso": "Evidencia automática para el jurado. No es el puntaje final.",
        "validar": {"ok": v.ok, "errores": v.errores, "advertencias": v.advertencias},
        "privacidad": {"graves": sum(1 for h in hallazgos if h.gravedad == "alta"),
                       "hallazgos": [h.texto() for h in hallazgos]},
        "scorecard": sc,
        "nivel": {"propuesto": nv["nivel_propuesto"], "nombre": nv["nombre_nivel"],
                  "faltantes": [c["id"] for n in nv["niveles"] for c in n["faltantes"]]},
        "reproducibilidad": "No evaluada aquí: ejecuta `python -m dataton reproducir <entrega> --ejecutar` en un entorno aislado.",
    }


def informe_md(inf: dict) -> str:
    v, p, n = inf["validar"], inf["privacidad"], inf["nivel"]
    lineas = [f"# Informe automático: {inf['entrega']}", "", f"> {inf['aviso']}", "",
              "## Estructura (validar)", "", "Resultado: " + ("OK" if v["ok"] else "con errores"), ""]
    lineas += [f"- Error: {e}" for e in v["errores"]] + [f"- Aviso: {a}" for a in v["advertencias"]]
    lineas += ["", "## Privacidad", "", f"Hallazgos de gravedad alta: {p['graves']}", ""]
    lineas += [f"- {h}" for h in p["hallazgos"]] or ["- Sin hallazgos"]
    lineas += ["", "## Nivel propuesto (escala 0–7)", "", f"{n['propuesto']} · {n['nombre']}", ""]
    lineas += [f"- Falta: {f}" for f in n["faltantes"]]
    lineas += ["", "## Mediciones (scorecard)", "", "```text", scorecard.resumen(inf["scorecard"]), "```", "",
               "## Reproducibilidad", "", inf["reproducibilidad"], ""]
    return "\n".join(lineas)


def recolectar(entregas: list[Path], escala: Path, informes: Path, salida: Callable[[str], None] = print) -> list[dict]:
    informes.mkdir(parents=True, exist_ok=True)
    resultados = []
    for repo in entregas:
        inf = evaluar_entrega(repo, escala)
        (informes / f"{repo.name}.json").write_text(json.dumps(inf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (informes / f"{repo.name}.md").write_text(informe_md(inf), encoding="utf-8")
        resultados.append(inf)
        salida(f"  {repo.name}: estructura {'OK' if inf['validar']['ok'] else 'con errores'}, "
               f"privacidad {inf['privacidad']['graves']} grave(s), nivel propuesto {inf['nivel']['propuesto']}")
    with (informes / "resumen.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["entrega", "estructura_ok", "privacidad_graves", "nivel_propuesto"])
        for r in resultados:
            w.writerow([r["entrega"], "si" if r["validar"]["ok"] else "no", r["privacidad"]["graves"], r["nivel"]["propuesto"]])
    return resultados
