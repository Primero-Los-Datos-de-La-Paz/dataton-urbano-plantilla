"""crear-equipos y congelar: repositorios de equipo en la organización de GitHub.

Seguridad:
- Por defecto todo es SIMULACIÓN: se muestra el plan con los comandos exactos y no se llama a GitHub.
- Con --ejecutar se muestra el plan completo y se pide escribir "si". Sin esa confirmación no se hace nada.
- Cada acción comprueba antes si ya existe (idempotencia) y se omite si es así.
- Ante un error de permisos, se detiene.
- Todo queda registrado en un CSV.
"""

from __future__ import annotations

import csv
import datetime as dt
import re
import subprocess
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

COLUMNAS_EQUIPOS = ["equipo_id", "nombre", "desafio", "usuarios_github", "contacto"]
ETIQUETA_ENTREGA = "entrega-final"
PATRON_REPO = re.compile(r"^d\d+-eq\d{2,}-[a-z0-9-]+$")

TEXTO_ACUERDO = """Antes de recibir acceso a datos internos, el equipo acepta las reglas de uso del paquete.

- [ ] Usaremos los datos solo para los fines del datatón.
- [ ] No republicaremos ni compartiremos los datos internos fuera del equipo.
- [ ] No intentaremos identificar personas ni cruzaremos datos con ese fin.
- [ ] Si encontramos un dato personal, avisaremos de inmediato por el buzón institucional y no lo copiaremos.
- [ ] Dejaremos el dato original sin editar y documentaremos cada cambio de forma reproducible.
- [ ] No presentaremos estimaciones sin evidencia ni cálculos como cifras oficiales.
- [ ] Todas las personas del equipo leyeron estas reglas.

Marca las casillas y cierra esta incidencia cuando todo el equipo esté de acuerdo.
"""

TEXTO_CHECKLIST = """Lista de control de la entrega (ver el README del repositorio).

- [ ] `entrega/ficha-equipo.yml` completa
- [ ] `entrega/ficha-por-desafio.md` completa
- [ ] `entrega/datos/`: datos de partida o enlace y suma SHA-256 (sin datos personales)
- [ ] `entrega/scripts/` o `entrega/pasos-manuales.md`: procedimiento reproducible
- [ ] `entrega/salida/`: resultado, con `entrega/salida/checksums.sha256`
- [ ] `entrega/diccionario.csv` con una descripción por columna
- [ ] `entrega/procedencia.md`
- [ ] `entrega/antes-despues.md` con la medición antes y después
- [ ] `autoria.yml` con el consentimiento de mención de cada integrante
- [ ] La validación automática (pestaña Actions) está en verde
"""


class ErrorPermisos(Exception):
    """GitHub negó una acción por falta de permisos."""


@dataclass
class Equipo:
    equipo_id: str
    nombre: str
    desafio: str
    usuarios: list[str]
    contacto: str

    @property
    def numero_desafio(self) -> int:
        return int(self.desafio.upper().lstrip("D"))

    @property
    def repo(self) -> str:
        n = int(re.sub(r"\D", "", self.equipo_id) or 0)
        return f"d{self.numero_desafio}-eq{n:02d}-{slug(self.nombre)}"


def slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:40] or "equipo"


def leer_equipos(ruta: Path) -> tuple[list[Equipo], list[str]]:
    errores: list[str] = []
    with ruta.open(encoding="utf-8", newline="") as fh:
        lector = csv.DictReader(fh)
        faltan = [c for c in COLUMNAS_EQUIPOS if c not in (lector.fieldnames or [])]
        if faltan:
            return [], [f"Faltan las columnas: {', '.join(faltan)}"]
        filas = list(lector)
    equipos, repos = [], set()
    for n, f in enumerate(filas, 2):
        usuarios = [u.strip().lstrip("@") for u in re.split(r"[;,\s]+", f["usuarios_github"] or "") if u.strip()]
        if not re.fullmatch(r"[Dd]\d+", (f["desafio"] or "").strip()):
            errores.append(f"Fila {n}: desafío no válido ({f['desafio']!r}); usa D1, D2…")
            continue
        if not usuarios:
            errores.append(f"Fila {n}: no hay usuarios de GitHub")
        if not re.search(r"\d", f["equipo_id"] or ""):
            errores.append(f"Fila {n}: equipo_id debe tener un número")
            continue
        e = Equipo(f["equipo_id"].strip(), f["nombre"].strip(), f["desafio"].strip().upper(), usuarios, f["contacto"].strip())
        if e.repo in repos:
            errores.append(f"Fila {n}: el repositorio {e.repo} se repite")
        repos.add(e.repo)
        equipos.append(e)
    return equipos, errores


# --- acceso a GitHub ------------------------------------------------------------

Ejecutor = Callable[[list[str]], subprocess.CompletedProcess]


def ejecutor_real(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)


@dataclass
class Accion:
    descripcion: str
    comando: list[str]
    comprobar: list[str] | None = None   # comando de lectura: si termina bien, la acción ya está hecha
    clave: str = ""


@dataclass
class GitHub:
    ejecutor: Ejecutor = ejecutor_real
    llamadas: list[list[str]] = field(default_factory=list)

    def correr(self, args: list[str]) -> subprocess.CompletedProcess:
        self.llamadas.append(args)
        res = self.ejecutor(args)
        texto = f"{res.stdout or ''} {res.stderr or ''}"
        if res.returncode != 0 and re.search(r"HTTP 403|Must have admin|Resource not accessible|permission", texto, re.I):
            raise ErrorPermisos(f"GitHub negó la acción por permisos: {' '.join(args)}")
        return res

    def existe(self, args: list[str]) -> bool:
        return self.correr(args).returncode == 0


def plan_equipo(e: Equipo, org: str, plantilla: str, internos: str | None, con_paquete_interno: set[str]) -> list[Accion]:
    repo, equipo_org, part = f"{org}/{e.repo}", e.repo, f"participantes-d{e.numero_desafio}"
    acciones = [Accion(f"Crear el repositorio privado {repo} desde {org}/{plantilla}",
                       ["gh", "repo", "create", repo, "--private", "--template", f"{org}/{plantilla}"],
                       ["gh", "api", f"repos/{repo}"], f"repo:{e.repo}")]
    for u in e.usuarios:
        acciones.append(Accion(f"Invitar a {u} como miembro de la organización (si no lo es)",
                               ["gh", "api", "-X", "PUT", f"orgs/{org}/memberships/{u}", "-f", "role=member"],
                               ["gh", "api", f"orgs/{org}/members/{u}"], f"miembro:{u}"))
    acciones.append(Accion(f"Crear el equipo de la organización {equipo_org}",
                           ["gh", "api", "-X", "POST", f"orgs/{org}/teams", "-f", f"name={equipo_org}", "-f", "privacy=closed"],
                           ["gh", "api", f"orgs/{org}/teams/{equipo_org}"], f"equipo:{equipo_org}"))
    acciones.append(Accion(f"Dar escritura al equipo {equipo_org} solo en {repo}",
                           ["gh", "api", "-X", "PUT", f"orgs/{org}/teams/{equipo_org}/repos/{repo}", "-f", "permission=push"],
                           None, f"permiso:{equipo_org}"))
    acciones.append(Accion(f"Crear el equipo {part} (si no existe)",
                           ["gh", "api", "-X", "POST", f"orgs/{org}/teams", "-f", f"name={part}", "-f", "privacy=closed"],
                           ["gh", "api", f"orgs/{org}/teams/{part}"], f"equipo:{part}"))
    if internos and e.desafio in con_paquete_interno:
        acciones.append(Accion(f"Dar lectura al equipo {part} en {org}/{internos}",
                               ["gh", "api", "-X", "PUT", f"orgs/{org}/teams/{part}/repos/{org}/{internos}", "-f", "permission=pull"],
                               None, f"permiso:{part}"))
    for u in e.usuarios:
        for equipo in (equipo_org, part):
            acciones.append(Accion(f"Agregar a {u} al equipo {equipo}",
                                   ["gh", "api", "-X", "PUT", f"orgs/{org}/teams/{equipo}/memberships/{u}", "-f", "role=member"],
                                   ["gh", "api", f"orgs/{org}/teams/{equipo}/memberships/{u}"], f"membresia:{equipo}:{u}"))
    for titulo, cuerpo in (("Acuerdo de reglas de uso", TEXTO_ACUERDO), ("Checklist de entrega", TEXTO_CHECKLIST)):
        acciones.append(Accion(f"Crear la incidencia «{titulo}» en {repo}",
                               ["gh", "issue", "create", "--repo", repo, "--title", titulo, "--body", cuerpo],
                               ["gh", "issue", "list", "--repo", repo, "--search", f"in:title \"{titulo}\"", "--json", "number",
                                "--jq", "if length > 0 then . else error(\"no existe\") end"], f"incidencia:{titulo}"))
    return acciones


def _texto_comando(c: list[str]) -> str:
    import shlex
    partes = [x if "\n" not in x else "<texto de la incidencia>" for x in c]
    return shlex.join(partes)


def _registrar(ruta: Path, filas: list[dict]) -> None:
    nuevo = not ruta.exists()
    with ruta.open("a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["fecha", "equipo_id", "repositorio", "accion", "resultado"], lineterminator="\n")
        if nuevo:
            w.writeheader()
        w.writerows(filas)


def crear_equipos(ruta_csv: Path, org: str, plantilla: str, internos: str | None, con_paquete_interno: set[str],
                  ejecutar: bool = False, confirmar: Callable[[str], str] = input, gh: GitHub | None = None,
                  registro: Path | None = None, salida: Callable[[str], None] = print) -> int:
    equipos, errores = leer_equipos(ruta_csv)
    if errores:
        for e in errores:
            salida(f"ERROR: {e}")
        return 1
    planes = {e.repo: (e, plan_equipo(e, org, plantilla, internos, con_paquete_interno)) for e in equipos}
    salida(f"{'SIMULACIÓN' if not ejecutar else 'PLAN'}: {len(equipos)} equipo(s) en la organización {org}")
    for repo, (e, acciones) in planes.items():
        salida(f"\n== {e.equipo_id} · {e.nombre} · {e.desafio} → {repo}")
        for a in acciones:
            salida(f"  - {a.descripcion}\n      {_texto_comando(a.comando)}")
    if not ejecutar:
        salida("\nModo de simulación: no se llamó a GitHub. Agrega --ejecutar para aplicar los cambios.")
        return 0
    if confirmar("\n¿Aplicar estos cambios en GitHub? Escribe 'si' para confirmar: ").strip().lower() != "si":
        salida("No se hizo ningún cambio.")
        return 0
    gh = gh or GitHub()
    registro = registro or ruta_csv.with_name("equipos_creados.csv")
    hoy = dt.datetime.now().isoformat(timespec="seconds")
    try:
        for repo, (e, acciones) in planes.items():
            filas = []
            for a in acciones:
                if a.comprobar and gh.existe(a.comprobar):
                    resultado = "ya existía (omitido)"
                else:
                    res = gh.correr(a.comando)
                    resultado = "hecho" if res.returncode == 0 else f"error: {(res.stderr or '').strip()[:120]}"
                filas.append({"fecha": hoy, "equipo_id": e.equipo_id, "repositorio": repo, "accion": a.descripcion,
                              "resultado": resultado})
                salida(f"  [{resultado}] {a.descripcion}")
            _registrar(registro, filas)
    except ErrorPermisos as err:
        salida(f"DETENIDO: {err}. Revisa los permisos de la cuenta (por ejemplo, el alcance admin:org de gh).")
        return 1
    salida(f"Registro: {registro}")
    return 0


# --- congelar -------------------------------------------------------------------

def congelar(repos: list[str], org: str, fecha_limite: str, ejecutar: bool = False,
             confirmar: Callable[[str], str] = input, gh: GitHub | None = None,
             registro: Path = Path("evaluacion/entregas.csv"), salida: Callable[[str], None] = print) -> int:
    try:
        limite = dt.datetime.fromisoformat(fecha_limite.replace("Z", "+00:00"))
    except ValueError:
        salida(f"ERROR: fecha límite no válida ({fecha_limite!r}); usa ISO 8601, por ejemplo 2099-01-31T18:00:00-04:00")
        return 1
    if limite.tzinfo is None:
        salida("ERROR: la fecha límite debe incluir la zona horaria (por ejemplo, -04:00)")
        return 1
    invalidos = [r for r in repos if not PATRON_REPO.match(r)]
    if invalidos:
        salida(f"ERROR: nombres de repositorio de equipo no válidos: {', '.join(invalidos)}")
        return 1
    salida(f"{'SIMULACIÓN' if not ejecutar else 'PLAN'}: congelar {len(repos)} repositorio(s) de {org}, fecha límite {limite.isoformat()}")
    for r in repos:
        salida(f"\n== {org}/{r}\n"
               f"  - Registrar el SHA de main en {registro}\n      gh api repos/{org}/{r}/commits/main --jq '.sha'\n"
               f"  - Crear la etiqueta {ETIQUETA_ENTREGA} en ese SHA\n"
               f"      gh api -X POST repos/{org}/{r}/git/refs -f ref=refs/tags/{ETIQUETA_ENTREGA} -f sha=<SHA>\n"
               f"  - Archivar el repositorio (solo lectura)\n      gh api -X PATCH repos/{org}/{r} -F archived=true")
    if not ejecutar:
        salida("\nModo de simulación: no se llamó a GitHub. Agrega --ejecutar para aplicar los cambios.")
        return 0
    if confirmar("\n¿Congelar y archivar estos repositorios? Escribe 'si' para confirmar: ").strip().lower() != "si":
        salida("No se hizo ningún cambio.")
        return 0
    gh = gh or GitHub()
    registro.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not registro.exists()
    try:
        with registro.open("a", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["repositorio", "sha", "fecha_commit", "fecha_limite", "dentro_de_plazo",
                                               "fecha_congelado"], lineterminator="\n")
            if nuevo:
                w.writeheader()
            for r in repos:
                res = gh.correr(["gh", "api", f"repos/{org}/{r}/commits/main", "--jq", '.sha + " " + .commit.committer.date'])
                if res.returncode != 0:
                    salida(f"  ERROR: no se pudo leer main de {r}: {(res.stderr or '').strip()[:120]}")
                    continue
                sha, fecha = res.stdout.split()
                fecha_c = dt.datetime.fromisoformat(fecha.replace("Z", "+00:00"))
                w.writerow({"repositorio": r, "sha": sha, "fecha_commit": fecha, "fecha_limite": limite.isoformat(),
                            "dentro_de_plazo": "si" if fecha_c <= limite else "no",
                            "fecha_congelado": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
                if not gh.existe(["gh", "api", f"repos/{org}/{r}/git/ref/tags/{ETIQUETA_ENTREGA}"]):
                    gh.correr(["gh", "api", "-X", "POST", f"repos/{org}/{r}/git/refs", "-f", f"ref=refs/tags/{ETIQUETA_ENTREGA}", "-f", f"sha={sha}"])
                gh.correr(["gh", "api", "-X", "PATCH", f"repos/{org}/{r}", "-F", "archived=true"])
                salida(f"  [congelado] {r} @ {sha[:10]} ({'dentro' if fecha_c <= limite else 'FUERA'} de plazo)")
    except ErrorPermisos as err:
        salida(f"DETENIDO: {err}")
        return 1
    salida(f"Registro: {registro}")
    return 0
