"""Pruebas de crear-equipos, congelar, recolectar, la rúbrica y sumas.

Nunca llaman a GitHub: usan un simulador que registra los comandos.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

from dataton import cli, edicion, equipos, recolectar

RAIZ = Path(__file__).resolve().parents[1]
EJEMPLO = RAIZ / "edicion" / "equipos.ejemplo.csv"
DEMO = Path(__file__).resolve().parent / "datos" / "demo"


class SimuladorGitHub:
    """Responde como gh. `existentes` son prefijos de rutas de API que ya existen."""

    def __init__(self, existentes=(), prohibido=None, sha_fecha="abc123 2099-01-01T10:00:00Z"):
        self.existentes, self.prohibido, self.sha_fecha, self.llamadas = set(existentes), prohibido, sha_fecha, []

    def __call__(self, args):
        self.llamadas.append(args)
        texto = " ".join(args)
        if self.prohibido and self.prohibido in texto:
            return subprocess.CompletedProcess(args, 1, "", "HTTP 403: Must have admin rights")
        lectura = args[:2] == ["gh", "api"] and "-X" not in args
        if lectura and "commits/main" in texto:
            return subprocess.CompletedProcess(args, 0, self.sha_fecha + "\n", "")
        if lectura or args[:3] == ["gh", "issue", "list"]:
            existe = any(e in texto for e in self.existentes)
            return subprocess.CompletedProcess(args, 0 if existe else 1, "", "" if existe else "HTTP 404")
        return subprocess.CompletedProcess(args, 0, "", "")


def test_leer_equipos_del_ejemplo():
    lista, errores = equipos.leer_equipos(EJEMPLO)
    assert errores == []
    assert [e.repo for e in lista] == ["d1-eq01-datos-claros", "d5-eq02-mapa-abierto", "d2-eq03-red-de-servicios"]


def test_leer_equipos_detecta_errores(tmp_path):
    ruta = tmp_path / "e.csv"
    ruta.write_text("equipo_id,nombre,desafio,usuarios_github,contacto\n01,A,X9,,c\n", encoding="utf-8")
    _, errores = equipos.leer_equipos(ruta)
    assert errores


def test_crear_equipos_simulacion_no_llama_a_github():
    sim = SimuladorGitHub()
    salida = []
    codigo = equipos.crear_equipos(EJEMPLO, "org-ficticia", "dataton-equipo-plantilla", "paquetes-internos", {"D5"},
                                   gh=equipos.GitHub(sim), salida=salida.append)
    assert codigo == 0 and sim.llamadas == []
    texto = "\n".join(salida)
    assert "gh repo create org-ficticia/d1-eq01-datos-claros --private --template org-ficticia/dataton-equipo-plantilla" in texto
    assert "participantes-d5/repos/org-ficticia/paquetes-internos" in texto     # solo D5 tiene paquete interno
    assert "participantes-d1/repos/org-ficticia/paquetes-internos" not in texto


def test_crear_equipos_sin_confirmacion_no_hace_nada(tmp_path):
    sim = SimuladorGitHub()
    codigo = equipos.crear_equipos(EJEMPLO, "org", "plantilla", None, set(), ejecutar=True, confirmar=lambda _: "no",
                                   gh=equipos.GitHub(sim), registro=tmp_path / "r.csv", salida=lambda _: None)
    assert codigo == 0 and sim.llamadas == [] and not (tmp_path / "r.csv").exists()


def test_crear_equipos_es_idempotente(tmp_path):
    sim = SimuladorGitHub(existentes={"repos/org/d1-eq01-datos-claros"})
    registro = tmp_path / "r.csv"
    codigo = equipos.crear_equipos(EJEMPLO, "org", "plantilla", None, set(), ejecutar=True, confirmar=lambda _: "si",
                                   gh=equipos.GitHub(sim), registro=registro, salida=lambda _: None)
    assert codigo == 0
    creados = [a for a in sim.llamadas if a[:3] == ["gh", "repo", "create"]]
    assert ["gh", "repo", "create", "org/d1-eq01-datos-claros"] not in [a[:4] for a in creados]
    assert len(creados) == 2
    assert "ya existía (omitido)" in registro.read_text(encoding="utf-8")


def test_crear_equipos_se_detiene_por_permisos(tmp_path):
    sim = SimuladorGitHub(prohibido="orgs/org/teams")
    codigo = equipos.crear_equipos(EJEMPLO, "org", "plantilla", None, set(), ejecutar=True, confirmar=lambda _: "si",
                                   gh=equipos.GitHub(sim), registro=tmp_path / "r.csv", salida=lambda _: None)
    assert codigo == 1


def test_congelar_simulacion_y_ejecucion(tmp_path):
    repos = ["d1-eq01-datos-claros"]
    sim = SimuladorGitHub()
    assert equipos.congelar(repos, "org", "2099-01-02T00:00:00-04:00", gh=equipos.GitHub(sim), salida=lambda _: None) == 0
    assert sim.llamadas == []
    registro = tmp_path / "entregas.csv"
    assert equipos.congelar(repos, "org", "2099-01-02T00:00:00-04:00", ejecutar=True, confirmar=lambda _: "si",
                            gh=equipos.GitHub(sim), registro=registro, salida=lambda _: None) == 0
    assert "abc123" in registro.read_text(encoding="utf-8") and ",si," in registro.read_text(encoding="utf-8")
    assert any("archived=true" in a for a in sim.llamadas)
    assert any("refs/tags/entrega-final" in " ".join(a) for a in sim.llamadas)


def test_congelar_marca_fuera_de_plazo(tmp_path):
    sim = SimuladorGitHub(sha_fecha="def456 2099-02-01T10:00:00Z")
    registro = tmp_path / "entregas.csv"
    equipos.congelar(["d1-eq01-x"], "org", "2099-01-02T00:00:00-04:00", ejecutar=True, confirmar=lambda _: "si",
                     gh=equipos.GitHub(sim), registro=registro, salida=lambda _: None)
    assert ",no," in registro.read_text(encoding="utf-8")


def test_congelar_exige_zona_horaria():
    assert equipos.congelar(["d1-eq01-x"], "org", "2099-01-02T00:00:00", salida=lambda _: None) == 1


def test_cli_rechaza_dry_run_y_ejecutar_juntos():
    assert cli.main(["crear-equipos", "--csv", str(EJEMPLO), "--org", "o", "--plantilla-equipo", "p",
                     "--dry-run", "--ejecutar"]) == 1


def test_cli_simulaciones_del_ejemplo():
    assert cli.main(["crear-equipos", "--csv", str(EJEMPLO), "--org", "org-ficticia", "--plantilla-equipo", "dataton-equipo-plantilla"]) == 0
    assert cli.main(["congelar", "--org", "org-ficticia", "--csv", str(EJEMPLO), "--fecha-limite", "2099-01-02T18:00:00-04:00"]) == 0


def test_recolectar_desde_carpeta(tmp_path):
    carpeta = tmp_path / "entregas"
    shutil.copytree(DEMO / "entrega-demo", carpeta / "d1-eq01-demo")
    informes = tmp_path / "informes"
    res = recolectar.recolectar([carpeta / "d1-eq01-demo"], RAIZ / "evaluacion" / "escala-preparacion-0-7.yml", informes,
                                salida=lambda _: None)
    assert res[0]["validar"]["ok"]
    assert (informes / "d1-eq01-demo.md").is_file() and (informes / "resumen.csv").is_file()
    assert "no es el puntaje final" in (informes / "d1-eq01-demo.md").read_text(encoding="utf-8").lower()


def test_rubrica_coincide_con_edicion():
    ed = edicion.cargar(RAIZ / "edicion" / "edicion.yml")
    assert edicion.validar_rubrica(ed, RAIZ / "edicion" / "rubrica.yml") == []


def test_rubrica_detecta_pesos_repetidos_y_criterios_distintos(tmp_path):
    ed = edicion.cargar(RAIZ / "edicion" / "edicion.yml")
    ruta = tmp_path / "rubrica.yml"
    ruta.write_text("criterios:\n  - {id: otro, peso: 10, escala: {0: a, 1: b, 2: c, 3: d, 4: e}}\n", encoding="utf-8")
    errores = edicion.validar_rubrica(ed, ruta)
    assert any("mismos criterios" in e for e in errores) and any("repite el peso" in e for e in errores)


def test_sumas_escribe_checksums(tmp_path):
    (tmp_path / "a.csv").write_text("x\n", encoding="utf-8")
    assert cli.main(["sumas", str(tmp_path)]) == 0
    assert "a.csv" in (tmp_path / "checksums.sha256").read_text(encoding="utf-8")
