"""reproducir: ejecuta el procedimiento declarado y compara las sumas SHA-256 de lo que produce.

Dos casos:
- Entrega de equipo: ejecuta entrega/scripts/*.py (en orden alfabético) y compara entrega/salida/
  con entrega/salida/checksums.sha256.
- Paquete: ejecuta scripts/*.py y compara data/interim/ con las líneas de data/interim/ de checksums.sha256.

Todo ocurre en una COPIA TEMPORAL: nunca se modifican los archivos originales.
Ejecutar scripts de otras personas es delicado: por eso, sin --ejecutar, solo se muestra el plan.
Los procedimientos que no son scripts de Python (cuadernos, historiales de OpenRefine, modelos de QGIS,
pasos manuales) se listan para revisión humana.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from dataton.validar import leer_checksums, sha256

LIMITE_SEGUNDOS = 600


@dataclass
class Plan:
    modo: str
    raiz: Path
    scripts: list[Path]
    otros_procedimientos: list[Path]
    checksums: Path
    prefijo_salida: str          # carpeta de salida relativa a la base de checksums
    base_checksums: Path


@dataclass
class ResultadoReproduccion:
    plan: Plan
    ejecutado: bool = False
    coinciden: list[str] = field(default_factory=list)
    difieren: list[str] = field(default_factory=list)
    faltan: list[str] = field(default_factory=list)
    errores: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.ejecutado and not (self.difieren or self.faltan or self.errores)


def planificar(raiz: Path) -> Plan:
    if (raiz / "entrega").is_dir():
        scripts_dir = raiz / "entrega" / "scripts"
        ck = raiz / "entrega" / "salida" / "checksums.sha256"
        return Plan("entrega", raiz, sorted(scripts_dir.glob("*.py")) if scripts_dir.is_dir() else [],
                    sorted(p for p in scripts_dir.glob("*") if p.is_file() and p.suffix not in (".py", ".md")) if scripts_dir.is_dir() else [],
                    ck, "", ck.parent)
    scripts_dir = raiz / "scripts"
    return Plan("paquete", raiz, sorted(scripts_dir.glob("*.py")) if scripts_dir.is_dir() else [],
                sorted(p for p in scripts_dir.glob("*") if p.is_file() and p.suffix not in (".py", ".csv", ".yml")) if scripts_dir.is_dir() else [],
                raiz / "checksums.sha256", "data/interim/", raiz)


def reproducir(raiz: Path, ejecutar: bool = False) -> ResultadoReproduccion:
    raiz = raiz.resolve()  # "." no tiene nombre: sin esto, la copia temporal no tendría carpeta propia
    plan = planificar(raiz)
    res = ResultadoReproduccion(plan)
    if not plan.checksums.is_file():
        res.errores.append(f"No existe {plan.checksums.relative_to(raiz)}: no hay sumas declaradas con qué comparar")
        return res
    if not plan.scripts:
        res.errores.append("No hay scripts de Python que ejecutar")
        return res
    declaradas = [(s, r) for s, r in leer_checksums(plan.checksums) if r.startswith(plan.prefijo_salida)]
    if not declaradas:
        res.errores.append("checksums.sha256 no declara ningún archivo de salida")
        return res
    if not ejecutar:
        return res

    with tempfile.TemporaryDirectory(prefix="dataton-reproducir-") as tmp:
        copia = Path(tmp) / raiz.name
        shutil.copytree(raiz, copia, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__"))
        base = copia / plan.base_checksums.relative_to(raiz)
        # Se borran las salidas declaradas para comprobar que los scripts las vuelven a producir.
        for _, rel in declaradas:
            (base / rel).unlink(missing_ok=True)
        cwd = copia / ("entrega" if plan.modo == "entrega" else "")
        for script in plan.scripts:
            destino = copia / script.relative_to(raiz)
            try:
                proc = subprocess.run([sys.executable, str(destino)], cwd=cwd, capture_output=True, text=True,
                                      timeout=LIMITE_SEGUNDOS)
            except subprocess.TimeoutExpired:
                res.errores.append(f"{script.name}: superó el límite de {LIMITE_SEGUNDOS} segundos")
                return res
            if proc.returncode != 0:
                ultima = (proc.stderr.strip().splitlines() or ["(sin mensaje)"])[-1]
                res.errores.append(f"{script.name} terminó con error (código {proc.returncode}): {ultima}")
                return res
        res.ejecutado = True
        for suma, rel in declaradas:
            ruta = base / rel
            if not ruta.is_file():
                res.faltan.append(rel)
            elif sha256(ruta) == suma:
                res.coinciden.append(rel)
            else:
                res.difieren.append(rel)
    return res


def resumen(res: ResultadoReproduccion) -> str:
    p = res.plan
    lineas = [f"Reproducción ({p.modo}) de {p.raiz.name}",
              "  Scripts: " + (", ".join(s.name for s in p.scripts) or "ninguno")]
    if p.otros_procedimientos:
        lineas.append("  Para revisión humana: " + ", ".join(s.name for s in p.otros_procedimientos))
    if not res.ejecutado and not res.errores:
        lineas.append("  Plan listo. No se ejecutó nada: agrega --ejecutar para correr los scripts en una copia temporal.")
    for e in res.errores:
        lineas.append(f"  ERROR: {e}")
    if res.ejecutado:
        lineas.append(f"  Coinciden: {len(res.coinciden)} · Difieren: {len(res.difieren)} · Faltan: {len(res.faltan)}")
        lineas += [f"    difiere: {r}" for r in res.difieren] + [f"    falta: {r}" for r in res.faltan]
        lineas.append("  OK: el procedimiento reproduce las salidas declaradas." if res.ok else "  El procedimiento NO reproduce las salidas declaradas.")
    return "\n".join(lineas)
