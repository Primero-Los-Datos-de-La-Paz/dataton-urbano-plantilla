"""liberar: publica un derivado de un dato interno SOLO si pasa la compuerta de liberación.

Requisitos (todos):
- liberacion.yml del paquete completo y con aprobado: true (ver docs/compuerta-de-liberacion.md);
- decisión del responsable del dato "aprobada", con fecha y referencia del acta;
- revisiones jurídica y de tecnología registradas, metadatos de autor eliminados, licencia y script;
- archivos_publicables en formato abierto, sin xlsx ni otros formatos propietarios;
- verificar-privacidad sin hallazgos de gravedad alta sobre esos archivos.

Qué hace con --ejecutar: copia solo los archivos publicables (sin historial) a una rama nueva del
repositorio público, hace un commit y muestra los comandos para subir la rama y abrir la solicitud
de incorporación (repositorio tomado del remoto "origin"). Solo los ejecuta si la persona escribe
"si". Nunca fusiona.
Sin --ejecutar (modo por defecto) solo muestra el plan.
"""

from __future__ import annotations

import datetime as dt
import re
import shlex
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from dataton import privacidad
from dataton.validar import sha256

FORMATOS_PUBLICABLES = {".csv", ".json", ".geojson", ".gpkg", ".md", ".txt", ".yml", ".yaml"}

OBLIGATORIOS = [
    "conjunto", "que_se_libera", "clasificacion", "agregacion_minima.nivel",
    "decision_responsable.unidad", "decision_responsable.decision", "decision_responsable.fecha",
    "decision_responsable.referencia_acta", "revision_privacidad.revision_juridica",
    "revision_privacidad.revision_tecnologia", "licencia", "script_derivado",
]


@dataclass
class Evaluacion:
    paquete: Path
    faltantes: list[str] = field(default_factory=list)
    hallazgos: list[str] = field(default_factory=list)
    archivos: list[Path] = field(default_factory=list)

    @property
    def aprobada(self) -> bool:
        return not self.faltantes and not self.hallazgos


def _valor(d: dict, ruta: str):
    for parte in ruta.split("."):
        d = d.get(parte) if isinstance(d, dict) else None
    return d


def evaluar(paq: Path) -> Evaluacion:
    ev = Evaluacion(paq)
    ruta = paq / "liberacion.yml"
    if not ruta.is_file():
        ev.faltantes.append("No existe liberacion.yml")
        return ev
    lib = yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}
    if lib.get("aprobado") is not True:
        ev.faltantes.append("aprobado no es true")
    for campo in OBLIGATORIOS:
        if _valor(lib, campo) in (None, "", []):
            ev.faltantes.append(f"Falta {campo}")
    if "umbral_conteos_pequenos" not in (lib.get("agregacion_minima") or {}):
        ev.faltantes.append("Falta la decisión agregacion_minima.umbral_conteos_pequenos (puede ser null si se decidió no aplicarlo)")
    if _valor(lib, "decision_responsable.decision") not in (None, "aprobada"):
        ev.faltantes.append("La decisión del responsable del dato no es 'aprobada'")
    if _valor(lib, "revision_privacidad.metadatos_autor_eliminados") is not True:
        ev.faltantes.append("revision_privacidad.metadatos_autor_eliminados no es true")
    publicables = lib.get("archivos_publicables") or []
    if not publicables:
        ev.faltantes.append("Falta archivos_publicables (lista de archivos del derivado)")
    for rel in publicables:
        archivo = paq / rel
        if not archivo.is_file():
            ev.faltantes.append(f"No existe el archivo publicable {rel}")
        elif archivo.suffix.lower() not in FORMATOS_PUBLICABLES:
            ev.faltantes.append(f"{rel} no está en un formato abierto publicable")
        else:
            ev.archivos.append(archivo)
            ev.hallazgos += [h.texto() for h in privacidad.verificar(archivo) if h.gravedad == "alta"]
    return ev


def _git(destino: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(destino), *args], check=True, capture_output=True, text=True).stdout.strip()


def liberar(paq: Path, destino: Path, ejecutar: bool = False, entrada=input) -> tuple[Evaluacion, list[str]]:
    """Devuelve la evaluación y los mensajes. Solo escribe en `destino` si la compuerta aprueba y ejecutar es True."""
    ev = evaluar(paq)
    mensajes: list[str] = []
    if not ev.aprobada:
        mensajes.append("NO SE LIBERA. La compuerta de liberación no está aprobada:")
        mensajes += [f"  - {f}" for f in ev.faltantes] + [f"  - privacidad: {h}" for h in ev.hallazgos]
        return ev, mensajes
    rama = f"liberacion/{paq.name}-{dt.date.today().isoformat()}"
    carpeta = Path("paquetes") / paq.name / "liberado"
    repo = _repositorio_remoto(destino) or "<organizacion>/<repositorio-publico>"
    comandos = [["git", "-C", str(destino), "push", "-u", "origin", rama],
                ["gh", "pr", "create", "--repo", repo, "--head", rama, "--base", "main",
                 "--title", f"Liberación: {paq.name}", "--body", "Derivado liberado según liberacion.yml. No fusionar sin revisión."]]
    mensajes.append(f"La compuerta está aprobada. Archivos a publicar en {destino / carpeta}:")
    mensajes += [f"  - {a.relative_to(paq).as_posix()} (sha256 {sha256(a)})" for a in ev.archivos]
    mensajes.append(f"Rama nueva: {rama}. No se fusiona: la revisa una persona.")
    if not ejecutar:
        mensajes.append("Modo de simulación: no se escribió nada. Agrega --ejecutar para preparar la rama.")
        mensajes += ["Comandos que se mostrarán para confirmar:"] + [f"  {shlex.join(c)}" for c in comandos]
        return ev, mensajes
    if not (destino / ".git").is_dir():
        mensajes.append(f"ERROR: {destino} no es un repositorio git.")
        return ev, mensajes
    _git(destino, "checkout", "-b", rama)
    (destino / carpeta).mkdir(parents=True, exist_ok=True)
    for a in ev.archivos:
        shutil.copyfile(a, destino / carpeta / a.name)
    shutil.copyfile(paq / "liberacion.yml", destino / carpeta / "liberacion.yml")
    _git(destino, "add", str(carpeta))
    _git(destino, "commit", "-m", f"Liberación de {paq.name} según liberacion.yml")
    mensajes.append(f"Rama {rama} creada con un commit local (copia limpia, sin historial del repositorio privado).")
    mensajes.append("Para publicarla se ejecutarán estos comandos:")
    mensajes += [f"  {shlex.join(c)}" for c in comandos]
    if entrada("¿Ejecutarlos ahora? Escribe 'si' para confirmar: ").strip().lower() != "si":
        mensajes.append("No se ejecutó nada en GitHub. La rama queda solo en local.")
        return ev, mensajes
    for c in comandos:
        subprocess.run(c, check=True)
    mensajes.append("Rama subida y solicitud de incorporación abierta. No se fusionó.")
    return ev, mensajes


def _repositorio_remoto(destino: Path) -> str | None:
    try:
        url = _git(destino, "remote", "get-url", "origin")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", url)
    return m.group(1) if m else None
