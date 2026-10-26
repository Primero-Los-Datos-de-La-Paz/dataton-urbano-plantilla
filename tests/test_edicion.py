"""Pruebas de edicion.yml, de la generación de textos y de init-edicion.

Usan solo datos ficticios.
"""

import datetime as dt
import shutil
from pathlib import Path

import pytest
import yaml

from dataton import cli, edicion, generar

RAIZ = Path(__file__).resolve().parents[1]
EJEMPLO = Path(__file__).resolve().parent / "datos" / "edicion-ejemplo.yml"


def edicion_ficticia() -> dict:
    ed = edicion.cargar(EJEMPLO)
    ed["edicion"].update({"id": "dataton-ejemplo-2099", "nombre": "Datatón de Ejemplo", "programa": "Programa X",
                          "anio": 2099, "ciudad": "Ciudad Ficticia", "institucion": {"nombre": "Municipio Ficticio"}})
    ed["github"]["organizacion"] = "org-ficticia"
    ed["github"]["repositorios"]["edicion"] = "dataton-ejemplo-2099"
    ed["sede"]["nombre"] = "Sala Ficticia"
    ed["contacto"]["buzon_institucional"] = "buzon@ejemplo.invalid"
    ed["calendario"][0]["fecha_inicio"] = dt.date(2099, 3, 2)
    ed["calendario"][2].update({"fecha_inicio": dt.date(2099, 3, 9), "fecha_fin": dt.date(2099, 3, 12)})
    ed["desafios"][0].update({"slug": "ejemplo", "titulo": "Desafío ficticio", "nivel_esperado": "Documentado",
                              "responsable_dato": {"unidad": "Unidad Ficticia", "codeowner": "@RESPONSABLE-D1"}})
    for c, p in zip(ed["rubrica"]["criterios"], [20, 20, 15, 15, 10, 10, 10]):
        c["peso"] = p
    return ed


def test_ejemplo_vacio_es_valido_con_pendientes():
    errores, pendientes = edicion.validar(edicion.cargar(EJEMPLO))
    assert errores == []
    assert "edicion.nombre" in pendientes


def test_edicion_del_repositorio_no_tiene_errores():
    errores, _ = edicion.validar(edicion.cargar(RAIZ / "edicion" / "edicion.yml"))
    assert errores == []


def test_pesos_que_no_suman_100_son_error():
    ed = edicion_ficticia()
    ed["rubrica"]["criterios"][0]["peso"] = 25
    errores, _ = edicion.validar(ed)
    assert any("suman 105" in e for e in errores)


def test_fecha_fin_anterior_es_error():
    ed = edicion_ficticia()
    ed["calendario"][2]["fecha_fin"] = dt.date(2099, 3, 1)
    errores, _ = edicion.validar(ed)
    assert any("anterior" in e for e in errores)


def test_fecha_larga_en_espanol():
    assert generar.fecha_larga(dt.date(2099, 3, 9)) == "lunes 9 de marzo de 2099"


def test_bloque_md_se_reemplaza_y_es_idempotente():
    ed = edicion_ficticia()
    texto = "Antes\n<!-- dataton:valor edicion.nombre -->viejo<!-- /dataton -->\n<!-- dataton:rubrica -->\n<!-- /dataton -->\n"
    una = generar.procesar_md(texto, ed)
    assert "Datatón de Ejemplo" in una and "viejo" not in una
    assert "**100 %**" in una
    assert generar.procesar_md(una, ed) == una


def test_bloque_desafio_toma_un_campo():
    ed = edicion_ficticia()
    salida = generar.procesar_md("<!-- dataton:desafio D1 nivel_esperado -->x<!-- /dataton -->", ed)
    assert salida == "<!-- dataton:desafio D1 nivel_esperado -->Documentado<!-- /dataton -->"
    with pytest.raises(generar.ErrorBloque):
        generar.procesar_md("<!-- dataton:desafio D9 titulo --><!-- /dataton -->", ed)


def test_bloque_de_linea_en_yaml_conserva_sangria():
    ed = edicion_ficticia()
    texto = "options:\n    # dataton:opciones-desafios\n    # /dataton\n"
    salida = generar.procesar_lineas(texto, ed)
    datos = yaml.safe_load(salida)
    assert datos["options"][0] == "D1 · Desafío ficticio"


def test_bloque_desconocido_falla():
    with pytest.raises(generar.ErrorBloque):
        generar.procesar_md("<!-- dataton:inexistente --><!-- /dataton -->", edicion_ficticia())


def test_init_edicion_crea_una_copia_generada(tmp_path):
    ed = edicion_ficticia()
    ruta_ed = tmp_path / "mi-edicion.yml"
    ruta_ed.write_text(yaml.safe_dump(ed, allow_unicode=True, sort_keys=False), encoding="utf-8")
    destino = tmp_path / "edicion-nueva"

    codigo = cli.main(["init-edicion", "--plantilla", str(RAIZ), "--edicion", str(ruta_ed), "--destino", str(destino)])

    assert codigo == 0
    readme = (destino / "README.md").read_text(encoding="utf-8")
    assert "Datatón de Ejemplo" in readme
    assert "del lunes 9 de marzo de 2099 al jueves 12 de marzo de 2099" in readme
    assert not (destino / ".git").exists()
    assert cli.main(["regenerar", "--raiz", str(destino), "--comprobar"]) == 0


def test_init_edicion_no_sobrescribe(tmp_path):
    destino = tmp_path / "ocupado"
    destino.mkdir()
    (destino / "algo.txt").write_text("x", encoding="utf-8")
    ruta_ed = tmp_path / "e.yml"
    shutil.copyfile(EJEMPLO, ruta_ed)
    assert cli.main(["init-edicion", "--plantilla", str(RAIZ), "--edicion", str(ruta_ed), "--destino", str(destino)]) == 1


def test_repositorio_esta_al_dia_con_edicion_yml():
    assert cli.main(["regenerar", "--raiz", str(RAIZ), "--comprobar"]) == 0
